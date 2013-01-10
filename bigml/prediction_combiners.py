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
import logging
LOGGER = logging.getLogger('BigML')

import numbers
import math

PLURALITY = 'plurality'
CONFIDENCE = 'confidence weighted'
PROBABILITY = 'probability weighted'
PREDICTION_HEADERS = ['prediction', 'confidence', 'order', 'distribution',
                      'count']


def combine_predictions(predictions, method=PLURALITY):
    """Reduces a number of predictions voting for classification and averaging
    predictions for regression.

    """

    if all([isinstance(prediction['prediction'], numbers.Number)
           for prediction in predictions]):
        return NUMERICAL_COMBINATION_METHODS.get(method, avg)(predictions)
    else: 
        if method == PROBABILITY:
            predictions = probability_weight(predictions)
        return combine_categorical(predictions,
                                   COMBINATION_WEIGHTS.get(method, None))


def avg(predictions):
    """Returns the average of a list of numeric values.

    """
    total = len(predictions)
    result = 0.0
    for prediction in predictions:
        result += prediction['prediction']
    return result / total if total > 0 else float('nan')


def error_weighted(predictions):
    """Returns the prediction combining votes using error to compute weight

    """
    top_range = 10
    result = 0.0
    # we only need the error part of each prediction that originally saves
    # error
    normalization_factor = normalize_error(predictions, top_range)
    for prediction in predictions:
        result += prediction['prediction'] * prediction['error_weight']
    return (result / normalization_factor if normalization_factor > 0
            else float('nan'))


def normalize_error(predictions, top_range):
    """Normalizes error to a [0, top_range] and builds probabilities

    """
    error_values = [prediction['confidence'] for prediction in predictions]
    max_error = max(error_values)
    min_error = min(error_values)
    error_range = 1.0 * (max_error - min_error)
    normalize_factor = 0
    if error_range > 0:
        # Shifts and scales predictions errors to [0, top_range].
        # Then builds e^-[scaled error] and returns the normalization factor
        # to fit them between [0, 1]
        for prediction in predictions:
            prediction['error_weight'] = math.exp((min_error -
                                                   prediction['confidence']) /
                                                   error_range * top_range)
            normalize_factor += prediction['error_weight']
    return normalize_factor


def combine_categorical(predictions, weight_label=None):
    """Returns the prediction combining votes by using the related function

        len for plurality (1 vote per prediction)
        sum for confidence weighted (confidence as a vote value)
        sum for probability weighted (probability as a vote value)
    """
    mode = {}
    if weight_label is None:
        weight = 1
    for prediction in predictions:
        if not weight_label is None:
            if not weight_label in prediction:
                raise Exception("Not enough data to use the selected "
                                "prediction method. Try creating your"
                                " model anew.")
            else:
                weight = prediction[weight_label]
        category = prediction['prediction']
        if category in mode:
            mode[category] = {"count": mode[category]["count"] +
                               weight,
                               "order": mode[category]["order"]}
        else:
            mode[category] = {"count": weight,
                              "order": prediction['order']}
    return sorted(mode.items(), key=lambda x: (x[1]['count'],
                                               -x[1]['order']),
                  reverse=True)[0][0]



def probability_weight(predictions):
    """Reorganizes predictions depending on training data probability

    """
    new_predictions = []
    for prediction in predictions:
        if not 'distribution' in prediction or not 'count' in prediction:
            raise Exception("Probability weighting is not available "
                            "because distribution information is missing.")
        total = prediction['count']
        order = prediction['order']
        for prediction, instances in prediction['distribution']:
            add_prediction(new_predictions, {'prediction': prediction,
                           'probability': float(instances) / total,
                           'order': order})
    return new_predictions


COMBINATION_WEIGHTS = {PLURALITY: None,
                       CONFIDENCE: 'confidence',
                       PROBABILITY: 'probability'}

NUMERICAL_COMBINATION_METHODS = {PLURALITY: avg,
                                 CONFIDENCE: error_weighted,
                                 PROBABILITY: avg}


def add_prediction(predictions, prediction_info):
    """Adds a new prediction into a list of predictions
       
       prediction_info should contain the following keys
       - prediction: whose value is the predicted category or value
       - order: whose value is the order of the model that generated the
                prediction

       for instance:
           {'prediction': 'Iris-virginica', 'order': 1}

       it may also contain the keys:
       - confidence: whose value is the confidence/error of the prediction
       - distribution: a list of [category/value, instances] pairs describing
                       the distribution at the prediction node
       - count: the total number of instances of the training set in the node
    """
    if (isinstance(prediction_info, dict) and 'prediction' in prediction_info
        and 'order' in prediction_info):
        predictions.append(prediction_info)
    else:
        LOGGER.error("WARNING: failed to add the prediction.\n"
                     "The minimal keys for the prediction are:\n"
                     "{'prediction': 'Iris-virginica', 'order': 1}")


def add_prediction_row(predictions, prediction_row,
                       prediction_headers=PREDICTION_HEADERS):
    """Adds a new prediction into a list of predictions

       prediction_headers should contain the labels for the prediction_row
       values in the same order.

       prediction_headers should contain at least the following strings
       - 'prediction': whose associated value in prediction_row
                       is the predicted category or value
       - 'order': whose associated value in prediction_row
                  is the order of the model that generated the prediction

       for instance:
           prediction_row = ['Iris-virginica', 1]
           prediction_headers = ['prediction', 'order']

       it may also contain the following headers and values:
       - 'confidence': whose associated value in prediction_row
                       is the confidence/error of the prediction
       - 'distribution': a list of [category/value, instances] pairs describing
                         the distribution at the prediction node
       - 'count': the total number of instances of the training set in the node

    """

    if (isinstance(prediction_row, list) and
        isinstance(prediction_headers, list) and
        len(prediction_row) == len(prediction_headers) and
        'prediction' in prediction_headers and 'order' in prediction_headers):
        prediction_info = {}
        for i in range(0, len(prediction_row)):
            prediction_info.update({prediction_headers[i]: prediction_row[i]})
        predictions.append(prediction_info)
    else:
        LOGGER.error("WARNING: failed to add the prediction.\n"
                     "The minimal labels rows and labels for the prediction"
                     " are 'prediction' and 'order'")
