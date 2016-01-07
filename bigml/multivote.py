# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2012-2016 BigML
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

LOGGER = logging.getLogger('BigML')

PLURALITY = 'plurality'
CONFIDENCE = 'confidence weighted'
PROBABILITY = 'probability weighted'
THRESHOLD = 'threshold'
PLURALITY_CODE = 0
CONFIDENCE_CODE = 1
PROBABILITY_CODE = 2
THRESHOLD_CODE = 3

PREDICTION_HEADERS = ['prediction', 'confidence', 'order', 'distribution',
                      'count']
COMBINATION_WEIGHTS = {
    PLURALITY: None,
    CONFIDENCE: 'confidence',
    PROBABILITY: 'probability',
    THRESHOLD: None}
COMBINER_MAP = {
    PLURALITY_CODE: PLURALITY,
    CONFIDENCE_CODE: CONFIDENCE,
    PROBABILITY_CODE: PROBABILITY,
    THRESHOLD_CODE: THRESHOLD}
WEIGHT_KEYS = {
    PLURALITY: None,
    CONFIDENCE: ['confidence'],
    PROBABILITY: ['distribution', 'count'],
    THRESHOLD: None}

DEFAULT_METHOD = 0
BINS_LIMIT = 32


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
    return (ws_p + ws_factor / 2 - ws_z * ws_sqrt) / (1 + ws_factor)


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
            distribution = merge_bins(distribution, BINS_LIMIT)
        return {'distribution': distribution,
                'distribution_unit': distribution_unit}

    @classmethod
    def avg(cls, instance, with_confidence=False,
            add_confidence=False, add_distribution=False,
            add_count=False, add_median=False, add_min=False, add_max=False):
        """Returns the average of a list of numeric values.

           If with_confidence is True, the combined confidence (as the
           average of confidences of the multivote predictions) is also
           returned
        """
        if (instance.predictions and with_confidence and
                not all(['confidence' in prediction
                         for prediction in instance.predictions])):
            raise Exception("Not enough data to use the selected "
                            "prediction method. Try creating your"
                            " model anew.")
        total = len(instance.predictions)
        result = 0.0
        median_result = 0.0
        confidence = 0.0
        instances = 0
        d_min = float('Inf')
        d_max = float('-Inf')
        for prediction in instance.predictions:
            result += prediction['prediction']
            if add_median:
                median_result += prediction['median']
            if with_confidence or add_confidence:
                confidence += prediction['confidence']
            if add_count:
                instances += prediction['count']
            if add_min and d_min > prediction['min']:
                d_min = prediction['min']
            if add_max and d_max < prediction['max']:
                d_max = prediction['max']
        if with_confidence:
            return (result / total, confidence / total) if total > 0 else \
                (float('nan'), 0)
        if (add_confidence or add_distribution or add_count or
                add_median or add_min or add_max):
            output = {'prediction': result / total if total > 0 else \
                float('nan')}
            if add_confidence:
                output.update(
                    {'confidence': confidence / total if total > 0 else 0})
            if add_distribution:
                output.update(cls.grouped_distribution(instance))
            if add_count:
                output.update({'count': instances})
            if add_median:
                output.update(
                    {'median': median_result / total if total > 0 else \
                    float('nan')})
            if add_min:
                output.update(
                    {'min': d_min})
            if add_max:
                output.update(
                    {'max': d_max})
            return output
        return result / total if total > 0 else float('nan')

    @classmethod
    def error_weighted(cls, instance, with_confidence=False,
                       add_confidence=False, add_distribution=False,
                       add_count=False, add_median=False, add_min=False,
                       add_max=False):
        """Returns the prediction combining votes using error to compute weight

           If with_confidences is true, the combined confidence (as the
           error weighted average of the confidences of the multivote
           predictions) is also returned
        """
        if (instance.predictions and with_confidence and
                not all(['confidence' in prediction
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
            if with_confidence:
                return float('nan'), 0
            else:
                return float('nan')
        if with_confidence or add_confidence:
            combined_error = 0.0
        for prediction in instance.predictions:
            result += prediction['prediction'] * prediction['_error_weight']
            if add_median:
                median_result += (prediction['median'] *
                                  prediction['_error_weight'])
            if add_count:
                instances += prediction['count']
            if add_min and d_min > prediction['min']:
                d_min = prediction['min']
            if add_max and d_max < prediction['max']:
                d_max = prediction['max']
            if with_confidence or add_confidence:
                combined_error += (prediction['confidence'] *
                                   prediction['_error_weight'])
            del prediction['_error_weight']
        if with_confidence:
            return (result / normalization_factor,
                    combined_error / normalization_factor)
        if (add_confidence or add_distribution or add_count or
                add_median or add_min or add_max):
            output = {'prediction': result / normalization_factor}
            if add_confidence:
                output.update({'confidence':
                               combined_error / normalization_factor})
            if add_distribution:
                output.update(cls.grouped_distribution(instance))
            if add_count:
                output.update({'count': instances})
            if add_median:
                output.update({'median': median_result / normalization_factor})
            if add_min:
                output.update(
                    {'min': d_min})
            if add_max:
                output.update(
                    {'max': d_max})
            return output
        return result / normalization_factor

    @classmethod
    def normalize_error(cls, instance, top_range):
        """Normalizes error to a [0, top_range] and builds probabilities

        """
        if instance.predictions and not all(['confidence' in prediction
                                             for prediction
                                             in instance.predictions]):
            raise Exception("Not enough data to use the selected "
                            "prediction method. Try creating your"
                            " model anew.")

        error_values = [prediction['confidence']
                        for prediction in instance.predictions]
        max_error = max(error_values)
        min_error = min(error_values)
        error_range = 1.0 * (max_error - min_error)
        normalize_factor = 0
        if error_range > 0:
            # Shifts and scales predictions errors to [0, top_range].
            # Then builds e^-[scaled error] and returns the normalization
            # factor to fit them between [0, 1]
            for prediction in instance.predictions:
                delta = (min_error - prediction['confidence'])
                prediction['_error_weight'] = math.exp(delta / error_range *
                                                       top_range)
                normalize_factor += prediction['_error_weight']
        else:
            for prediction in instance.predictions:
                prediction['_error_weight'] = 1
            normalize_factor = len(instance.predictions)
        return normalize_factor

    def __init__(self, predictions):
        """Init method, builds a MultiVote with a list of predictions

           The constuctor expects a list of well formed predictions like:
                {'prediction': 'Iris-setosa', 'confidence': 0.7}
            Each prediction can also contain an 'order' key that is used
            to break even in votations. The list order is used by default.
        """
        self.predictions = []
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

    def combine(self, method=DEFAULT_METHOD, with_confidence=False,
                add_confidence=False, add_distribution=False,
                add_count=False, add_median=False, add_min=False,
                add_max=False, options=None):
        """Reduces a number of predictions voting for classification and
           averaging predictions for regression.

           method will determine the voting method (plurality, confidence
           weighted, probability weighted or threshold).
           If with_confidence is true, the combined confidence (as a weighted
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
        if self.is_regression():
            for prediction in self.predictions:
                if prediction['confidence'] is None:
                    prediction['confidence'] = 0
            function = NUMERICAL_COMBINATION_METHODS.get(method,
                                                         self.__class__.avg)
            return function(self, with_confidence=with_confidence,
                            add_confidence=add_confidence,
                            add_distribution=add_distribution,
                            add_count=add_count,
                            add_median=add_median,
                            add_min=add_min,
                            add_max=add_max)
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
                with_confidence=with_confidence,
                add_confidence=add_confidence,
                add_distribution=add_distribution,
                add_count=add_count)

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
                predictions.append({'prediction': prediction,
                                    'probability': float(instances) / total,
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

    def combine_categorical(self, weight_label=None, with_confidence=False,
                            add_confidence=False, add_distribution=False,
                            add_count=False):
        """Returns the prediction combining votes by using the given weight:

            weight_label can be set as:
            None:          plurality (1 vote per prediction)
            'confidence':  confidence weighted (confidence as a vote value)
            'probability': probability weighted (probability as a vote value)

            If with_confidence is true, the combined confidence (as a weighted
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
            if add_count:
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
        if with_confidence or add_confidence:
            if 'confidence' in self.predictions[0]:
                prediction, combined_confidence = self.weighted_confidence(
                    prediction, weight_label)
            # if prediction had no confidence, compute it from distribution
            else:
                combined_distribution = self.combine_distribution()
                distribution, count = combined_distribution
                combined_confidence = ws_confidence(prediction, distribution,
                                                    ws_n=count)
        if with_confidence:
            return prediction, combined_confidence
        if add_confidence or add_distribution or add_count:
            output = {'prediction': prediction}
            if add_confidence:
                output.update({'confidence': combined_confidence})
            if add_distribution:
                output.update(self.__class__.grouped_distribution(self))
            if add_count:
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
                 any([not 'confidence' or weight_label not in prediction
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
            final_confidence += weight * prediction['confidence']
            total_weight += weight
        final_confidence = (final_confidence / total_weight
                            if total_weight > 0 else float('nan'))
        return combined_prediction, final_confidence

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
        if (isinstance(prediction_info, dict) and
                'prediction' in prediction_info):
            order = self.next_order()
            prediction_info['order'] = order
            self.predictions.append(prediction_info)
        else:
            LOGGER.warning("Failed to add the prediction.\n"
                           "The minimal key for the prediction is 'prediction'"
                           ":\n{'prediction': 'Iris-virginica'")

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
