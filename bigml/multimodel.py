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

"""A Multiple Local Predictive Model.

This module defines a Multiple Model to make predictions locally using multiple
local models.

This module cannot only save you a few credits, but also enormously
reduce the latency for each prediction and let you use your models
offline.

from bigml.api import BigML
from bigml.multimodel import MultiModel

api = BigML()

model = MultiModel([api.get_model(model['resource']) for model in
                    api.list_models(query_string="tags__in=my_tag")
                    ['objects']])

model.predict({"petal length": 3, "petal width": 1})

"""
import logging
LOGGER = logging.getLogger('BigML')

import numbers
import csv
import math
from bigml.model import Model
from bigml.util import get_predictions_file_name


def combine_predictions(predictions, method='plurality'):
    """Reduces a number of predictions voting for classification and averaging
    predictions for regression.

    """
    if all([isinstance(prediction, numbers.Number) for prediction in
           predictions.keys()]):
        return NUMERICAL_COMBINATION_METHODS[method](predictions)
    else:
        return combine_categorical(predictions, COMBINATION_METHODS[method])


def avg(predictions):
    """Returns the average of a list of numeric values.

    """
    total = 0
    result = 0.0
    for prediction, confidences in predictions.items():
        total += len(confidences)
        result += prediction * len(confidences)
    return result / total if total > 0 else float('nan')


def error_weighted(predictions):
    """Returns the prediction combining votes using error to compute weight

    """
    TOP_RANGE = 10
    result = 0.0
    normalization_factor = normalize_error(predictions, TOP_RANGE)
    for prediction, confidences in predictions.items():
        result += prediction * sum(confidences)
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


def combine_categorical(predictions, function):
    """Returns the prediction combining votes by using the related function

        len for plurality (1 vote per prediction)
        sum for confidence_weighted (confidence as a vote value)
    """
    mode = {}
    order = 0
    for prediction, values in predictions.items():
        if prediction in mode:
            mode[prediction] = {"count": mode[prediction]["count"] +
                                function(values),
                                "order": mode[prediction]["order"]}
        else:
            order = order + 1
            mode[prediction] = {"count": function(values), "order": order}
    return sorted(mode.items(), key=lambda x: (x[1]['count'],
                                               -x[1]['order']),
                  reverse=True)[0][0]


COMBINATION_METHODS = {"plurality": len,
                       "confidence weighted": sum}
NUMERICAL_COMBINATION_METHODS = {"plurality": avg,
                                 "confidence weighted": error_weighted}


class MultiModel(object):
    """A multiple local model.

    Uses a numbers of BigML remote models to build a local version that can be
    used to generate predictions locally.

    """

    def __init__(self, models):
        self.models = []
        if isinstance(models, list):
            for model in models:
                self.models.append(Model(model))
        else:
            self.models.append(Model(models))

    def list_models(self):
        """Lists all the model/ids that compound the multi model.

        """
        return [model['resource'] for model in self.models]

    def predict(self, input_data, by_name=True):
        """Makes a prediction based on the prediction made by every model.

        """

        predictions = {}
        for model in self.models:
            prediction, confidence = model.predict(input_data, by_name=by_name,
                                                   with_confidence=True)
            if not prediction in predictions:
                predictions[prediction] = []
            predictions[prediction].append(confidence)

        return combine_predictions(predictions)

    def batch_predict(self, input_data_list, output_file_path,
                      by_name=True, reuse=False):
        """Makes predictions for a list of input data.

           The predictions generated for each model are stored in an output
           file. The name of the file will use the following syntax:
                model_[id of the model]_predictions.csv
           For instance, when using model/50c0de043b563519830001c2 to predict,
           the output file name will be
                model_50c0de043b563519830001c2_predictions.csv
        """
        for model in self.models:
            output_file = get_predictions_file_name(model.resource_id,
                                                    output_file_path)
            if reuse:
                try:
                    predictions_file = open(output_file)
                    predictions_file.close()
                    continue
                except IOError:
                    pass
            try:
                predictions_file = csv.writer(open(output_file, 'w', 0),
                                              lineterminator="\n")
            except IOError:
                raise Exception("Cannot find %s directory." % output_file_path)
            for input_data in input_data_list:
                prediction = model.predict(input_data,
                                           by_name=by_name,
                                           with_confidence=True)
                if isinstance(prediction[0], basestring):
                    prediction[0] = prediction[0].encode("utf-8")
                predictions_file.writerow(prediction)

    def batch_votes(self, predictions_file_path, data_locale=None):
        """Adds the votes for predictions generated by the models.

           Returns a list of predictions groups. A prediction group is a dict
           whose key is the prediction and its value is a list of the
           confidences with which the prediction has been issued
        """

        predictions_files = []
        for model in self.models:
            predictions_files.append((model, csv.reader(open(
                get_predictions_file_name(model.resource_id,
                                          predictions_file_path), "U"),
                lineterminator="\n")))
        votes = []
        predictions = {}
        prediction = True
        while prediction:
            if predictions:
                votes.append(predictions)
                predictions = {}
            for (model, handler) in predictions_files:
                try:
                    row = handler.next()
                    prediction = row[0]
                    confidence = float(row[1])
                except StopIteration:
                    prediction = False
                    break
                prediction = model.to_prediction(prediction, data_locale)
                if not prediction in predictions:
                    predictions[prediction] = []
                predictions[prediction].append(confidence)

        return votes
