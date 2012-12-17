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
from bigml.model import Model
from bigml.util import get_predictions_file_name


def avg(data):
    """Returns the average of a list of numeric values.

    """
    total = 0
    result = 0.0
    for prediction, confidences in data.items():
        total += len(confidences)
        result += prediction * len(confidences)
    return result / total if total > 0 else float('nan')


def combine_predictions(predictions, method='plurality'):
    """Reduces a number of predictions voting for classification and averaging
    predictions for regression.

    """
    if all([isinstance(prediction, numbers.Number) for prediction in
           predictions.keys()]):
        return avg(predictions)
    else:
        return COMBINATION_METHODS[method](predictions)


def plurality(predictions):
    """Returns the prediction combining votes by assigning one vote per model

    """
    mode = {}
    order = 0
    for prediction, values in predictions.items():
        if prediction in mode:
            mode[prediction] = {"count": mode[prediction]["count"] +
                                len(values),
                                "order": mode[prediction]["order"]}
        else:
            order = order + 1
            mode[prediction] = {"count": len(values), "order": order}
    return sorted(mode.items(), key=lambda x: (x[1]['count'],
                                               -x[1]['order']),
                  reverse=True)[0][0]

def confidence_weighted(predictions):
    """Returns the prediction combining votes by assigning one vote per model

    """
    mode = {}
    order = 0
    for prediction, values in predictions.items():
        values = [float(value) for value in values]
        if prediction in mode:
            mode[prediction] = {"count": mode[prediction]["count"] + sum(values),
                                "order": mode[prediction]["order"]}
        else:
            order = order + 1
            mode[prediction] = {"count": sum(values), "order": order}
    return sorted(mode.items(), key=lambda x: (x[1]['count'],
                                               -x[1]['order']),
                  reverse=True)[0][0]


COMBINATION_METHODS = {"plurality": plurality,
                       "confidence weighted": confidence_weighted}


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

        predictions = []
        for model in self.models:
            predictions.append(model.predict(input_data, by_name=by_name))

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
                predictions_file = csv.writer(open(output_file, 'w', 0))
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
                                          predictions_file_path), "U"))))
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
                    confidence = row[1]
                except StopIteration:
                    prediction = False
                    break
                prediction = model.to_prediction(prediction, data_locale)
                if not prediction in predictions:
                    predictions[prediction] = []
                predictions[prediction].append(confidence)

        return votes
