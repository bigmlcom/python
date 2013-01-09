# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2012 BigML
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
"""Auxiliar functions for predictions combination.

"""
import numbers

PLURALITY = 'plurality'
CONFIDENCE = 'confidence weighted'
PROBABILITY = 'probability weighted'


def combine_predictions(predictions, method=PLURALITY):
    """Reduces a number of predictions voting for classification and averaging
    predictions for regression.

    Predictions is a dict whose key is the prediction and its associated values
    are a list of tuples of the form (confidence, order, distribution, total
    number of instances). For instance, given three different models where the
    first one predicts 'Iris-virginica' with confidence 0.26289, the second
    one 'Iris-virginica' with confidence 0.22343 and the third one
    'Iris-setosa' with confidence 0.1783 the predictions to be combined would
    be:

    {'Iris-virginica': [(0.26289, 0, [['Iris-versicolor', 50],
                                      ['Iris-setosa', 50],
                                      ['Iris-virginica', 50]], 150),
                        (0.22343, 1, [['Iris-versicolor', 50],
                                      ['Iris-setosa', 40],
                                      ['Iris-virginica', 60]], 150)],
     'Iris-setosa':[(0.1783, 2, [['Iris-versicolor', 50],
                                 ['Iris-setosa', 55],
                                 ['Iris-virginica', 45]], 150)]}

    """

    if all([isinstance(prediction, numbers.Number) for prediction in
           predictions.keys()]):
        return NUMERICAL_COMBINATION_METHODS.get(method, avg)(predictions)
    else:
        probability_weighted = (method == PROBABILITY)
        if probability_weighted:
            # Changes predictions dict using its distribution values.
            # Initially the prediction structure is
            # prediction: (confidence, order, distribution, instances)
            # The new predictions dict has the same structure, but
            # changing confidence values to probability values:
            # prediction: (probability, order)
            predictions = probability_weight(predictions)
        return combine_categorical(predictions,
                                   *COMBINATION_METHODS.get(method, (len,)))


def avg(predictions):
    """Returns the average of a list of numeric values.

    """
    total = 0
    result = 0.0
    for prediction, weights in predictions.items():
        total += len(weights)
        result += prediction * len(weights)
    return result / total if total > 0 else float('nan')


def error_weighted(predictions):
    """Returns the prediction combining votes using error to compute weight

    """
    top_range = 10
    result = 0.0
    # we only need the error part of each prediction that originally saves
    # error
    for prediction, values in predictions.items():
        predictions[prediction] = [x[0] for x in values]
    normalization_factor = normalize_error(predictions, top_range)
    for prediction, values in predictions.items():
        result += prediction * sum(values)
    return (result / normalization_factor if normalization_factor > 0
            else float('nan'))


def normalize_error(predictions, top_range):
    """Normalizes error to a [0, top_range] and builds probabilities

    """
    error_values = reduce(lambda x, y: x + y,
                          [errors for errors in predictions.values()])
    max_error = max(error_values)
    min_error = min(error_values)
    error_range = max_error - min_error
    if error_range > 0:
        # Shifts and scales predictions errors to [0, top_range].
        # Then builds e^-[scaled error] and returns the normalization factor
        # to fit them between [0, 1]
        for prediction, errors in predictions.items():
            predictions[prediction] = [math.exp((min_error - x) / error_range
                                                * top_range) for x in errors]
    return sum(reduce(lambda x, y: x + y, [errors
                      for errors in predictions.values()]))


def combine_categorical(predictions, function, weight_extractor=None):
    """Returns the prediction combining votes by using the related function

        len for plurality (1 vote per prediction)
        sum for confidence weighted (confidence as a vote value)
        sum for probability weighted (probability as a vote value)
    """
    mode = {}
    for prediction, values in predictions.items():
        weights_factors = values
        # the structure of each value is (confidence, order, distribution,
        # instances) or
        # (probability, order)
        if not weight_extractor is None:
            weights_factors = weight_extractor(values)
        if not weights_factors:
            raise Exception("Not enough data to use the selected prediction"
                            " method. Try creating your model anew.")
        if prediction in mode:
            mode[prediction] = {"count": mode[prediction]["count"] +
                                function(weights_factors),
                                "order": mode[prediction]["order"]}
        else:
            mode[prediction] = {"count": function(weights_factors),
                                "order": values[0][1]}
    return sorted(mode.items(), key=lambda x: (x[1]['count'],
                                               -x[1]['order']),
                  reverse=True)[0][0]


def extract_confidence(values):
    """Extracts confidence from predictions associated values

    """
    return [x[0] for x in values if not x[0] is None]


def probability_weight(predictions):
    """Reorganizes predictions depending on training data probability

    Transforms the predictions original structure (see combine_predictions)
    to a similar one where confidence is replaced by probability as
    extracted from distribution and instances data. For instance, for the
    previous example data:

    {'Iris-virginica': [(0.26289, 0, [['Iris-versicolor', 50],
                                      ['Iris-setosa', 50],
                                      ['Iris-virginica', 50]], 150),
                        (0.22343, 1, [['Iris-versicolor', 50],
                                      ['Iris-setosa', 40],
                                      ['Iris-virginica', 60]], 150)],
     'Iris-setosa':[(0.1783, 2, [['Iris-versicolor', 50],
                                 ['Iris-setosa', 55],
                                 ['Iris-virginica', 45]], 150)]}
    it produces:

    {'Iris-virginica': [(0.3333333333333333, 0),
                        (0.4, 1),
                        (0.3, 2)],
     'Iris-setosa': [(0.3333333333333333, 0),
                     (0.26666666666666666, 1),
                     (0.36666666666666664, 2)],
     'Iris-versicolor': [(0.3333333333333333, 0),
                         (0.3333333333333333, 1),
                         (0.3333333333333333, 2)]}

    where the dict's key is the prediction, and the value is a list of tuples
    containing the probability and the number of the model that issued the
    prediction

    """
    new_predictions = {}
    for prediction, values in predictions.items():
        for node_info in values:
            order = node_info[1]
            distribution = node_info[2]
            total = node_info[3]
            if distribution is None:
                raise Exception("Probability weighting is not available "
                                "because distribution information is missing.")

            for prediction, instances in distribution:
                insert_prediction(new_predictions, prediction,
                                  float(instances) / total, order)
    return new_predictions


COMBINATION_METHODS = {PLURALITY: (len,),
                       CONFIDENCE: (sum, extract_confidence),
                       PROBABILITY: (sum, extract_confidence)}

NUMERICAL_COMBINATION_METHODS = {PLURALITY: avg,
                                 CONFIDENCE: error_weighted,
                                 PROBABILITY: avg}


def insert_prediction(predictions, prediction, confidence, order,
                   distribution=None, instances=None):
    """Inserts a new prediction into a dictionary of predictions or
       appends it to a list of existing ones

    """
    if not prediction in predictions:
        predictions[prediction] = []
    prediction_info = (confidence, order)
    if not distribution is None and not instances is None:
        prediction_info = prediction_info + (distribution, instances)
    predictions[prediction].append(prediction_info)
