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


import csv
import ast
from bigml.model import Model
from bigml.util import get_predictions_file_name
from bigml.multivote import MultiVote
from bigml.multivote import PLURALITY_CODE


def read_votes(votes_files, to_prediction, data_locale=None):
    """Reads the votes found in the votes' files.

       Returns a list of MultiVote objects containing the list of predictions.
       votes_files parameter should contain the path to the files where votes
       are stored
       In to_prediction parameter we expect the method of a local model object
       that casts the string prediction values read from the file to their
       real type. For instance
           >>> local_model = Model(model)
           >>> prediction = local_model.to_prediction("1")
           >>> isinstance(prediction, int)
           True
           >>> read_votes(["my_predictions_file"], local_model.to_prediction)
       data_locale should contain the string identification for the locale
       used in numeric formatting.
    """
    votes = []
    for order in range(0, len(votes_files)):
        votes_file = votes_files[order]
        index = 0
        for row in csv.reader(open(votes_file, "U"), lineterminator="\n"):
            prediction = to_prediction(row[0], data_locale=data_locale)
            if index > (len(votes) - 1):
                votes.append(MultiVote([]))
            distribution = None
            instances = None
            if len(row) > 2:
                distribution = ast.literal_eval(row[2])
                instances = int(row[3])
            prediction_row = [prediction, float(row[1]), order,
                              distribution, instances]
            votes[index].append_row(prediction_row)
            index += 1
    return votes


class MultiModel(object):
    """A multiple local model.

    Uses a number of BigML remote models to build a local version that can be
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

    def predict(self, input_data, by_name=True, method=PLURALITY_CODE,
                with_confidence=False):
        """Makes a prediction based on the prediction made by every model.

           The method parameter is a numeric key to the following combination
           methods in classifications/regressions:
              0 - majority vote (plurality)/ average: PLURALITY_CODE
              1 - confidence weighted majority vote / error weighted:
                  CONFIDENCE_CODE
              2 - probability weighted majority vote / average:
                  PROBABILITY_CODE
        """

        votes = self.generate_votes(input_data, by_name=by_name)
        return votes.combine(method=method, with_confidence=with_confidence)

    def generate_votes(self, input_data, by_name=True):
        """ Generates a MultiVote object that contains the predictions
            made by each of the models.
        """
        votes = MultiVote([])
        for order in range(0, len(self.models)):
            model = self.models[order]
            prediction_info = model.predict(input_data, by_name=by_name,
                                            with_confidence=True)
            prediction, confidence, distribution, instances = prediction_info
            prediction_row = [prediction, confidence, order,
                              distribution, instances]
            votes.append_row(prediction_row)
        return votes

    def batch_predict(self, input_data_list, output_file_path,
                      by_name=True, reuse=False):
        """Makes predictions for a list of input data.

           The predictions generated for each model are stored in an output
           file. The name of the file will use the following syntax:
                model_[id of the model]__predictions.csv
           For instance, when using model/50c0de043b563519830001c2 to predict,
           the output file name will be
                model_50c0de043b563519830001c2__predictions.csv
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

           Returns a list of MultiVote objects each of which contains a list
           of predictions.
        """

        votes_files = []
        for model in self.models:
            votes_files.append(get_predictions_file_name(model.resource_id,
                               predictions_file_path))
        return read_votes(votes_files, self.models[0].to_prediction,
                          data_locale=data_locale)
