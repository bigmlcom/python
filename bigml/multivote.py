# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2012-2020 BigML
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""Auxiliar class for predictions combination.

"""
import logging
import numbers
import math


from bigml.util import PRECISION


LOGGER = logging.getLogger('BigML')

PLURALITY = 'plurality'
CONFIDENCE = 'confidence weighted'
PROBABILITY = 'probability weighted'
THRESHOLD = 'threshold'
BOOSTING = 'boosting'
PLURALITY_CODE = 0
CONFIDENCE_CODE = 1
PROBABILITY_CODE = 2
THRESHOLD_CODE = 3
# negative combiner codes are meant for internal use only
BOOSTING_CODE = -1
# note that -2 and -3 codes are also used in BigMLer
# COMBINATION = -2
# AGGREGATION = -3

PREDICTION_HEADERS = ['prediction', 'confidence', 'order', 'distribution',
                      'count']
COMBINATION_WEIGHTS = {
    PLURALITY: None,
    CONFIDENCE: 'confidence',
    PROBABILITY: 'probability',
    THRESHOLD: None,
    BOOSTING: 'weight'}
COMBINER_MAP = {
    PLURALITY_CODE: PLURALITY,
    CONFIDENCE_CODE: CONFIDENCE,
    PROBABILITY_CODE: PROBABILITY,
    THRESHOLD_CODE: THRESHOLD,
    BOOSTING_CODE: BOOSTING}
WEIGHT_KEYS = {
    PLURALITY: None,
    CONFIDENCE: ['confidence'],
    PROBABILITY: ['distribution', 'count'],
    THRESHOLD: None,
    BOOSTING: ['weight']}
BOOSTING_CLASS = 'class'
CONFIDENCE_W = COMBINATION_WEIGHTS[CONFIDENCE]

DEFAULT_METHOD = 0
BINS_LIMIT = 32

def weighted_sum(predictions, weight=None):
    """Returns a weighted sum of the predictions

    """
    return sum([prediction["prediction"] * prediction[weight] for
                prediction in predictions])


def softmax(predictions):
    """Returns the softmax values from a distribution given as a dictionary
    like:
        {"category": {"probability": probability, "order": order}}

    """
    total = 0.0
    normalized = {}
    for category, cat_info in predictions.items():
        normalized[category] = { \
            "probability": math.exp(cat_info["probability"]),
            "order": cat_info["order"]}
        total += normalized[category]["probability"]
    return float('nan') if total == 0 else \
        {category: {"probability": cat_info["probability"] / total,
                    "order": cat_info["order"]}
         for category, cat_info in normalized.items()}


def ws_confidence(prediction, distribution, ws_z=1.96, ws_n=None):
    """Wilson score interval computation of the distribution for the prediction

       expected arguments:
            prediction: the value of the prediction for which confidence is
                        computed
            distribution: a distribution-like structure of predictions and
                          the associated weights. (e.g.
                          [['Iris-setosa', 10], ['Iris-versicolor', 5]])
            ws_z: percentile of the standard normal distribution
            ws_n: total number of instances in the distribution. If absent,
                  the number is computed as the sum of weights in the
                  provided distribution

    """
    if isinstance(distribution, list):
        distribution = dict(distribution)
    ws_p = distribution[prediction]
    if ws_p < 0:
        raise ValueError("The distribution weight must be a positive value")
    ws_norm = float(sum(distribution.values()))
    if ws_norm != 1.0:
        ws_p = ws_p / ws_norm
    if ws_n is None:
        ws_n = ws_norm
    else:
        ws_n = float(ws_n)
    if ws_n < 1:
        raise ValueError("The total of instances in the distribution must be"
                         " a positive integer")
    ws_z = float(ws_z)
    ws_z2 = ws_z * ws_z
    ws_factor = ws_z2 / ws_n
    ws_sqrt = math.sqrt((ws_p * (1 - ws_p) + ws_factor / 4) / ws_n)
    return round((ws_p + ws_factor / 2 - ws_z * ws_sqrt) / (1 + ws_factor),
                 PRECISION)


def merge_distributions(distribution, new_distribution):
    """Adds up a new distribution structure to a map formatted distribution

    """
    for value, instances in new_distribution.items():
        if value not in distribution:
            distribution[value] = 0
        distribution[value] += instances
    return distribution


def merge_bins(distribution, limit):
    """Merges the bins of a regression distribution to the given limit number

    """
    length = len(distribution)
    if limit < 1 or length <= limit or length < 2:
        return distribution
    index_to_merge = 2
    shortest = float('inf')
    for index in range(1, length):
        distance = distribution[index][0] - distribution[index - 1][0]
        if distance < shortest:
            shortest = distance
            index_to_merge = index
    new_distribution = distribution[: index_to_merge - 1]
    left = distribution[index_to_merge - 1]
    right = distribution[index_to_merge]
    new_bin = [(left[0] * left[1] + right[0] * right[1]) /
               (left[1] + right[1]), left[1] + right[1]]
    new_distribution.append(new_bin)
    if index_to_merge < (length - 1):
        new_distribution.extend(distribution[(index_to_merge + 1):])
    return merge_bins(new_distribution, limit)


class MultiVote(object):
    """A multiple vote prediction

    Uses a number of predictions to generate a combined prediction.

    """
    @classmethod
    def grouped_distribution(cls, instance):
        """Returns a distribution formed by grouping the distributions of
           each predicted node.

        """
        joined_distribution = {}
        distribution_unit = 'counts'
        for prediction in instance.predictions:
            joined_distribution = merge_distributions(
                joined_distribution,
                dict((x[0], x[1]) for x in prediction['distribution']))
            # when there's more instances, sort elements by their mean
            distribution = [list(element) for element in
                            sorted(joined_distribution.items(),
                                   key=lambda x: x[0])]
            if distribution_unit == 'counts':
                distribution_unit = ('bins' if len(distribution) > BINS_LIMIT
                                     else 'counts')
            if distribution_unit != 'categories':
                distribution = merge_bins(distribution, BINS_LIMIT)
        return {'distribution': distribution,
                'distribution_unit': distribution_unit}

    @classmethod
    def avg(cls, instance, full=False):
        """Returns the average of a list of numeric values.

           If full is True, the combined confidence (as the
           average of confidences of the multivote predictions) is also
           returned
        """
        if (instance.predictions and full and
                not all([CONFIDENCE_W in prediction
                         for prediction in instance.predictions])):
            raise Exception("Not enough data to use the selected "
                            "prediction method. Try creating your"
                            " model anew.")
        total = len(instance.predictions)
        result = 0.0
        median_result = 0.0
        confidence = 0.0
        instances = 0
        missing_confidence = 0
        d_min = float('Inf')
        d_max = float('-Inf')
        for prediction in instance.predictions:
            result += prediction['prediction']
            if full:
                if 'median' in prediction:
                    median_result += prediction['median']
                # some buggy models don't produce a valid confidence value
                if prediction[CONFIDENCE_W] is not None and \
                   prediction[CONFIDENCE_W] > 0:
                    confidence += prediction[CONFIDENCE_W]
                else:
                    missing_confidence += 1
                instances += prediction['count']
                if 'min' in prediction and prediction['min'] < d_min:
                    d_min = prediction['min']
                if 'max' in prediction and prediction['max'] > d_max:
                    d_max = prediction['max']
        if full:
            output = {'prediction': result / total if total > 0 else \
                float('nan')}
            # some strange models have no confidence
            output.update(
                {'confidence': round( \
                    confidence / (total - missing_confidence), PRECISION) \
                 if total > 0 else 0})
            output.update(cls.grouped_distribution(instance))
            output.update({'count': instances})
            if median_result > 0:
                output.update({
                    'median': median_result / total if \
                    total > 0 else float('nan')})
            if d_min < float('Inf'):
                output.update({'min': d_min})
            if d_max > float('-Inf'):
                output.update({'max': d_max})
            return output
        return result / total if total > 0 else float('nan')

    @classmethod
    def error_weighted(cls, instance, full=False):
        """Returns the prediction combining votes using error to compute weight

           If full is true, the combined confidence (as the
           error weighted average of the confidences of the multivote
           predictions) is also returned
        """
        if (instance.predictions and full and
                not all([CONFIDENCE_W in prediction
                         for prediction in instance.predictions])):
            raise Exception("Not enough data to use the selected "
                            "prediction method. Try creating your"
                            " model anew.")
        top_range = 10
        result = 0.0
        median_result = 0.0
        instances = 0
        d_min = float('Inf')
        d_max = float('-Inf')
        normalization_factor = cls.normalize_error(instance, top_range)
        if normalization_factor == 0:
            if full:
                return {"prediction": float('nan')}
            else:
                return float('nan')
        if full:
            combined_error = 0.0
        for prediction in instance.predictions:
            result += prediction['prediction'] * prediction['_error_weight']
            if full:
                if 'median' in prediction:
                    median_result += (prediction['median'] *
                                      prediction['_error_weight'])
                instances += prediction['count']
                if 'min' in prediction and prediction['min'] < d_min:
                    d_min = prediction['min']
                if 'max' in prediction and prediction['max'] > d_max:
                    d_max = prediction['max']
                # some buggy models don't produce a valid confidence value
                if prediction[CONFIDENCE_W] is not None:
                    combined_error += (prediction[CONFIDENCE_W] *
                                       prediction['_error_weight'])
            del prediction['_error_weight']
        if full:
            output = {'prediction': result / normalization_factor}
            output.update({'confidence':
                           round(combined_error / normalization_factor,
                                 PRECISION)})
            output.update(cls.grouped_distribution(instance))
            output.update({'count': instances})
            if median_result > 0:
                output.update({'median': median_result / normalization_factor})
            if d_min < float('Inf'):
                output.update({'min': d_min})
            if d_max > float('-Inf'):
                output.update({'max': d_max})
            return output
        return result / normalization_factor

    @classmethod
    def normalize_error(cls, instance, top_range):
        """Normalizes error to a [0, top_range] and builds probabilities

        """
        if instance.predictions and not all([CONFIDENCE_W in prediction
                                             for prediction
                                             in instance.predictions]):
            raise Exception("Not enough data to use the selected "
                            "prediction method. Try creating your"
                            " model anew.")

        error_values = []
        for prediction in instance.predictions:
            if prediction[CONFIDENCE_W] is not None:
                error_values.append(prediction[CONFIDENCE_W])
        max_error = max(error_values)
        min_error = min(error_values)
        error_range = 1.0 * (max_error - min_error)
        normalize_factor = 0
        if error_range > 0:
            # Shifts and scales predictions errors to [0, top_range].
            # Then builds e^-[scaled error] and returns the normalization
            # factor to fit them between [0, 1]
            for prediction in instance.predictions:
                delta = (min_error - prediction[CONFIDENCE_W])
                prediction['_error_weight'] = math.exp(delta / error_range *
                                                       top_range)
                normalize_factor += prediction['_error_weight']
        else:
            for prediction in instance.predictions:
                prediction['_error_weight'] = 1
            normalize_factor = len(error_values)
        return normalize_factor

    def __init__(self, predictions, boosting_offsets=None):
        """Init method, builds a MultiVote with a list of predictions
        The constuctor expects a list of well formed predictions like:
            {'prediction': 'Iris-setosa', 'confidence': 0.7}
        Each prediction can also contain an 'order' key that is used
        to break even in votations. The list order is used by default.
        The boosting_offsets can contain the offset used in boosting models, so
        whenever is not None votes will be considered from boosting models.
        """
        self.predictions = []
        self.boosting = boosting_offsets is not None
        self.boosting_offsets = boosting_offsets

        if isinstance(predictions, list):
            self.predictions.extend(predictions)
        else:
            self.predictions.append(predictions)

        if not all(['order' in prediction for prediction in predictions]):

            for i in range(len(self.predictions)):
                self.predictions[i]['order'] = i

    def is_regression(self):
        """Returns True if all the predictions are numbers

        """
        if self.boosting:
            return any(prediction.get('class') is None for
                       prediction in self.predictions)
        return all([isinstance(prediction['prediction'], numbers.Number)
                    for prediction in self.predictions])

    def next_order(self):
        """Return the next order to be assigned to a prediction

           Predictions in MultiVote are ordered in arrival sequence when
           added using the constructor or the append and extend methods.
           This order is used to break even cases in combination
           methods for classifications.
        """
        if self.predictions:
            return self.predictions[-1]['order'] + 1
        return 0

    def combine(self, method=DEFAULT_METHOD, options=None, full=False):
        """Reduces a number of predictions voting for classification and
           averaging predictions for regression.

           method will determine the voting method (plurality, confidence
           weighted, probability weighted or threshold).
           If full is true, the combined confidence (as a weighted
           average of the confidences of votes for the combined prediction)
           will also be given.
        """
        # there must be at least one prediction to be combined
        if not self.predictions:
            raise Exception("No predictions to be combined.")

        method = COMBINER_MAP.get(method, COMBINER_MAP[DEFAULT_METHOD])
        keys = WEIGHT_KEYS.get(method, None)
        # and all predictions should have the weight-related keys
        if keys is not None:
            for key in keys:
                if not all([key in prediction for prediction
                            in self.predictions]):
                    raise Exception("Not enough data to use the selected "
                                    "prediction method. Try creating your"
                                    " model anew.")
        if self.boosting:
            for prediction in self.predictions:
                if prediction[COMBINATION_WEIGHTS[BOOSTING]] is None:
                    prediction[COMBINATION_WEIGHTS[BOOSTING]] = 0
            if self.is_regression():
                # sum all gradients weighted by their "weight" plus the
                # boosting offset
                return weighted_sum(self.predictions, weight="weight") + \
                    self.boosting_offsets
            else:
                return self.classification_boosting_combiner( \
                    options, full=full)
        elif self.is_regression():
            for prediction in self.predictions:
                if prediction[CONFIDENCE_W] is None:
                    prediction[CONFIDENCE_W] = 0
            function = NUMERICAL_COMBINATION_METHODS.get(method,
                                                         self.__class__.avg)
            return function(self, full=full)
        else:
            if method == THRESHOLD:
                if options is None:
                    options = {}
                predictions = self.single_out_category(options)
            elif method == PROBABILITY:
                predictions = MultiVote([])
                predictions.predictions = self.probability_weight()
            else:
                predictions = self
            return predictions.combine_categorical(
                COMBINATION_WEIGHTS.get(method, None),
                full=full)

    def probability_weight(self):
        """Reorganizes predictions depending on training data probability

        """
        predictions = []
        for prediction in self.predictions:
            if 'distribution' not in prediction or 'count' not in prediction:
                raise Exception("Probability weighting is not available "
                                "because distribution information is missing.")
            total = prediction['count']
            if total < 1 or not isinstance(total, int):
                raise Exception("Probability weighting is not available "
                                "because distribution seems to have %s "
                                "as number of instances in a node" % total)
            order = prediction['order']
            for prediction, instances in prediction['distribution']:
                predictions.append({ \
                    'prediction': prediction,
                    'probability': round(float(instances) / total, PRECISION),
                    'count': instances,
                    'order': order})
        return predictions

    def combine_distribution(self, weight_label='probability'):
        """Builds a distribution based on the predictions of the MultiVote

           Given the array of predictions, we build a set of predictions with
           them and associate the sum of weights (the weight being the
           contents of the weight_label field of each prediction)
        """
        if not all([weight_label in prediction
                    for prediction in self.predictions]):
            raise Exception("Not enough data to use the selected "
                            "prediction method. Try creating your"
                            " model anew.")
        distribution = {}
        total = 0
        for prediction in self.predictions:
            if prediction['prediction'] not in distribution:
                distribution[prediction['prediction']] = 0.0
            distribution[prediction['prediction']] += prediction[weight_label]
            total += prediction['count']
        if total > 0:
            distribution = [[key, value] for key, value in
                            distribution.items()]
        else:
            distribution = []
        return distribution, total

    def combine_categorical(self, weight_label=None, full=False):
        """Returns the prediction combining votes by using the given weight:

            weight_label can be set as:
            None:          plurality (1 vote per prediction)
            'confidence':  confidence weighted (confidence as a vote value)
            'probability': probability weighted (probability as a vote value)

            If full is true, the combined confidence (as a weighted
            average of the confidences of the votes for the combined
            prediction) will also be given.
        """
        mode = {}
        instances = 0
        if weight_label is None:
            weight = 1
        for prediction in self.predictions:
            if weight_label is not None:
                if weight_label not in COMBINATION_WEIGHTS.values():
                    raise Exception("Wrong weight_label value.")
                if weight_label not in prediction:
                    raise Exception("Not enough data to use the selected "
                                    "prediction method. Try creating your"
                                    " model anew.")
                else:
                    weight = prediction[weight_label]
            category = prediction['prediction']
            if full:
                instances += prediction['count']
            if category in mode:
                mode[category] = {"count": mode[category]["count"] + weight,
                                  "order": mode[category]["order"]}
            else:
                mode[category] = {"count": weight,
                                  "order": prediction['order']}
        prediction = sorted(mode.items(), key=lambda x: (x[1]['count'],
                                                         -x[1]['order'],
                                                         x[0]),
                            reverse=True)[0][0]
        if full:
            output = {'prediction': prediction}
            if 'confidence' in self.predictions[0]:
                prediction, combined_confidence = self.weighted_confidence(
                    prediction, weight_label)
            # if prediction had no confidence, compute it from distribution
            else:
                if 'probability' in self.predictions[0]:
                    combined_distribution = self.combine_distribution()
                    distribution, count = combined_distribution
                    combined_confidence = ws_confidence(prediction,
                                                        distribution,
                                                        ws_n=count)
            output.update({'confidence':
                           round(combined_confidence, PRECISION)})
            if 'probability' in self.predictions[0]:
                for prediction in self.predictions:
                    if prediction['prediction'] == output['prediction']:
                        output['probability'] = prediction['probability']
            if 'distribution' in self.predictions[0]:
                output.update(self.__class__.grouped_distribution(self))
            output.update({'count': instances})
            return output
        return prediction

    def weighted_confidence(self, combined_prediction, weight_label):
        """Compute the combined weighted confidence from a list of predictions

        """
        predictions = [prediction for prediction in self.predictions \
            if prediction['prediction'] == combined_prediction]
        if (weight_label is not None and
                (not isinstance(weight_label, basestring) or
                 any([not CONFIDENCE_W or weight_label not in prediction
                      for prediction in predictions]))):
            raise ValueError("Not enough data to use the selected "
                             "prediction method. Lacks %s information." %
                             weight_label)
        final_confidence = 0.0
        total_weight = 0.0
        weight = 1
        for prediction in predictions:
            if weight_label is not None:
                weight = prediction[weight_label]
            final_confidence += weight * prediction[CONFIDENCE_W]
            total_weight += weight
        final_confidence = (final_confidence / total_weight
                            if total_weight > 0 else float('nan'))
        return combined_prediction, final_confidence

    def classification_boosting_combiner(self, options, full=False):
        """Combines the predictions for a boosted classification ensemble
        Applies the regression boosting combiner, but per class. Tie breaks
        use the order of the categories in the ensemble summary to decide.

        """
        grouped_predictions = {}
        for prediction in self.predictions:
            if prediction.get(BOOSTING_CLASS) is not None:
                objective_class = prediction.get(BOOSTING_CLASS)
                if grouped_predictions.get(objective_class) is None:
                    grouped_predictions[objective_class] = []
                grouped_predictions[objective_class].append(prediction)
        categories = options.get("categories", [])
        predictions = {key: { \
            "probability": weighted_sum(value, weight="weight") + \
                self.boosting_offsets.get(key, 0),
            "order": categories.index(key)} for
                       key, value in grouped_predictions.items()}
        predictions = softmax(predictions)
        predictions = sorted( \
            predictions.items(), key=lambda(x): \
            (- x[1]["probability"], x[1]["order"]))
        prediction, prediction_info = predictions[0]
        confidence = round(prediction_info["probability"], PRECISION)
        if full:
            return {"prediction": prediction,
                    "probability": confidence, \
                "probabilities": [ \
                    {"category": prediction,
                     "probability": round(prediction_info["probability"],
                                          PRECISION)}
                    for prediction, prediction_info in predictions]}
        else:
            return prediction

    def append(self, prediction_info):
        """Adds a new prediction into a list of predictions

           prediction_info should contain at least:
           - prediction: whose value is the predicted category or value

           for instance:
               {'prediction': 'Iris-virginica'}

           it may also contain the keys:
           - confidence: whose value is the confidence/error of the prediction
           - distribution: a list of [category/value, instances] pairs
                           describing the distribution at the prediction node
           - count: the total number of instances of the training set in the
                    node
        """
        if isinstance(prediction_info, dict):
            if 'prediction' in prediction_info:
                order = self.next_order()
                prediction_info['order'] = order
                self.predictions.append(prediction_info)
            else:
                LOGGER.warning("Failed to add the prediction.\n"
                               "The minimal key for the prediction is "
                               "'prediction': "
                               "\n{'prediction': 'Iris-virginica'")
        """
        elif isinstance(prediction_info, list):
            if self.probabilities:
                self.predictions.append(prediction_info)
        """

    def single_out_category(self, options):
        """Singles out the votes for a chosen category and returns a prediction
           for this category iff the number of votes reaches at least the given
           threshold.

        """
        if options is None or any(option not in options for option in
                                  ["threshold", "category"]):
            raise Exception("No category and threshold information was"
                            " found. Add threshold and category info."
                            " E.g. {\"threshold\": 6, \"category\":"
                            " \"Iris-virginica\"}.")
        length = len(self.predictions)
        if options["threshold"] > length:
            raise Exception("You cannot set a threshold value larger than "
                            "%s. The ensemble has not enough models to use"
                            " this threshold value." % length)
        if options["threshold"] < 1:
            raise Exception("The threshold must be a positive value")
        category_predictions = []
        rest_of_predictions = []
        for prediction in self.predictions:
            if prediction['prediction'] == options["category"]:
                category_predictions.append(prediction)
            else:
                rest_of_predictions.append(prediction)
        if len(category_predictions) >= options["threshold"]:
            return MultiVote(category_predictions)
        return MultiVote(rest_of_predictions)

    def append_row(self, prediction_row,
                   prediction_headers=PREDICTION_HEADERS):
        """Adds a new prediction into a list of predictions

           prediction_headers should contain the labels for the prediction_row
           values in the same order.

           prediction_headers should contain at least the following string
           - 'prediction': whose associated value in prediction_row
                           is the predicted category or value

           for instance:
               prediction_row = ['Iris-virginica']
               prediction_headers = ['prediction']

           it may also contain the following headers and values:
           - 'confidence': whose associated value in prediction_row
                           is the confidence/error of the prediction
           - 'distribution': a list of [category/value, instances] pairs
                             describing the distribution at the prediction node
           - 'count': the total number of instances of the training set in the
                      node
        """

        if (isinstance(prediction_row, list) and
                isinstance(prediction_headers, list) and
                len(prediction_row) == len(prediction_headers) and
                'prediction' in prediction_headers):
            order = self.next_order()
            try:
                index = prediction_headers.index('order')
                prediction_row[index] = order
            except ValueError:
                prediction_headers.append('order')
                prediction_row.append(order)
            prediction_info = {}
            for i in range(0, len(prediction_row)):
                prediction_info.update({prediction_headers[i]:
                                        prediction_row[i]})
            self.predictions.append(prediction_info)
        else:
            LOGGER.error("WARNING: failed to add the prediction.\n"
                         "The row must have label 'prediction' at least.")

    def extend(self, predictions_info):
        """Given a list of predictions, extends the list with another list of
           predictions and adds the order information. For instance,
           predictions_info could be:

                [{'prediction': 'Iris-virginica', 'confidence': 0.3},
                 {'prediction': 'Iris-versicolor', 'confidence': 0.8}]
           where the expected prediction keys are: prediction (compulsory),
           confidence, distribution and count.
        """
        if isinstance(predictions_info, list):
            order = self.next_order()
            for i in range(0, len(predictions_info)):
                prediction = predictions_info[i]
                if isinstance(prediction, dict):
                    prediction['order'] = order + i
                    self.append(prediction)
                else:
                    LOGGER.error("WARNING: failed to add the prediction.\n"
                                 "Only dict like predictions are expected.")
        else:
            LOGGER.error("WARNING: failed to add the predictions.\n"
                         "Only a list of dict-like predictions are expected.")

    def extend_rows(self, predictions_rows,
                    prediction_headers=PREDICTION_HEADERS):
        """Given a list of predictions, extends the list with a list of
           predictions and adds the order information. For instance,
           predictions_info could be:

                [['Iris-virginica', 0.3],
                 ['Iris-versicolor', 0.8]]
           and their respective labels are extracted from predition_headers,
           that for this example would be:
                ['prediction', 'confidence']

           The expected prediction elements are: prediction (compulsory),
           confidence, distribution and count.
        """
        order = self.next_order()
        try:
            index = prediction_headers.index('order')
        except ValueError:
            index = len(prediction_headers)
            prediction_headers.append('order')
        if isinstance(predictions_rows, list):
            for i in range(0, len(predictions_rows)):
                prediction = predictions_rows[i]
                if isinstance(prediction, list):
                    if index == len(prediction):
                        prediction.append(order + i)
                    else:
                        prediction[index] = order + i
                    self.append_row(prediction, prediction_headers)
                else:
                    LOGGER.error("WARNING: failed to add the prediction.\n"
                                 "Only row-like predictions are expected.")
        else:
            LOGGER.error("WARNING: failed to add the predictions.\n"
                         "Only a list of row-like predictions are expected.")

NUMERICAL_COMBINATION_METHODS = {
    PLURALITY: MultiVote.avg,
    CONFIDENCE: MultiVote.error_weighted,
    PROBABILITY: MultiVote.avg}
