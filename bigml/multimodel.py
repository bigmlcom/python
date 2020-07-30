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
import ast


from bigml.model import Model, cast_prediction
from bigml.model import LAST_PREDICTION
from bigml.util import get_predictions_file_name
from bigml.multivote import MultiVote
from bigml.multivote import PLURALITY_CODE, CONFIDENCE_CODE, PROBABILITY_CODE
from bigml.multivotelist import MultiVoteList
from bigml.io import UnicodeWriter, UnicodeReader


LOGGER = logging.getLogger('BigML')


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
        with UnicodeReader(votes_file) as rdr:
            for row in rdr:
                prediction = to_prediction(row[0], data_locale=data_locale)
                if index > (len(votes) - 1):
                    votes.append(MultiVote([]))
                distribution = None
                instances = None
                if len(row) > 2:
                    distribution = ast.literal_eval(row[2])
                    instances = int(row[3])
                    try:
                        confidence = float(row[1])
                    except ValueError:
                        confidence = 0.0
                prediction_row = [prediction, confidence, order,
                                  distribution, instances]
                votes[index].append_row(prediction_row)
                index += 1
    return votes


class MultiModel(object):
    """A multiple local model.

    Uses a number of BigML remote models to build a local version that can be
    used to generate predictions locally.

    """

    def __init__(self, models, api=None, fields=None, class_names=None):
        self.models = []
        self.class_names = class_names

        if isinstance(models, list):
            if all([isinstance(model, Model) for model in models]):
                self.models = models
            else:
                for model in models:
                    self.models.append(Model(model, api=api, fields=fields))
        else:
            self.models.append(Model(models, api=api, fields=fields))

    def list_models(self):
        """Lists all the model/ids that compound the multi model.

        """
        return [model.resource() for model in self.models]

    def predict(self, input_data, method=PLURALITY_CODE, options=None,
                missing_strategy=LAST_PREDICTION, full=False):
        """Makes a prediction based on the prediction made by every model.

           The method parameter is a numeric key to the following combination
           methods in classifications/regressions:
              0 - majority vote (plurality)/ average: PLURALITY_CODE
              1 - confidence weighted majority vote / error weighted:
                  CONFIDENCE_CODE
              2 - probability weighted majority vote / average:
                  PROBABILITY_CODE
              3 - threshold filtered vote / doesn't apply:
                  THRESHOLD_CODE
        """

        votes = self.generate_votes(input_data,
                                    missing_strategy=missing_strategy)

        result = votes.combine(method=method, options=options, full=full)
        if full:
            unused_fields = set(input_data.keys())
            for _, prediction in enumerate(votes.predictions):
                unused_fields = unused_fields.intersection( \
                    set(prediction.get("unused_fields", [])))
            if not isinstance(result, dict):
                result = {"prediction": result}
            result['unused_fields'] = list(unused_fields)

        return result

    def generate_votes(self, input_data,
                       missing_strategy=LAST_PREDICTION):
        """ Generates a MultiVote object that contains the predictions
            made by each of the models.
        """
        votes = MultiVote([])
        for order in range(0, len(self.models)):
            model = self.models[order]
            prediction_info = model.predict( \
                input_data, missing_strategy=missing_strategy, full=True)

            if model.boosting is not None:
                votes.boosting = True
                prediction_info.update( \
                    {"weight": model.boosting.get("weight")})
                if model.boosting.get("objective_class") is not None:
                    prediction_info.update( \
                        {"class": model.boosting.get("objective_class")})

            votes.append(prediction_info)

        return votes

    def _generate_votes(self, input_data, missing_strategy=LAST_PREDICTION,
                        unused_fields=None):
        """ Generates a MultiVote object that contains the predictions
            made by each of the models. Please note that this function
            calls a _predict method which assumes input data has been
            properly checked against the model fields. Only casting
            to the correct type will be applied.
        """
        votes = MultiVote([])
        for order in range(0, len(self.models)):
            model = self.models[order]
            prediction_info = model._predict( \
                input_data,
                missing_strategy=missing_strategy, unused_fields=unused_fields)

            if model.boosting is not None:
                votes.boosting = True
                prediction_info.update( \
                    {"weight": model.boosting.get("weight")})
                if model.boosting.get("objective_class") is not None:
                    prediction_info.update( \
                        {"class": model.boosting.get("objective_class")})

            votes.append(prediction_info)

        return votes

    def generate_votes_distribution(self,
                                    input_data,
                                    missing_strategy=LAST_PREDICTION,
                                    method=PROBABILITY_CODE):
        votes = []
        for model in self.models:
            model.class_names = self.class_names
            if method == PLURALITY_CODE:
                prediction_info = [0.0] * len(self.class_names)
                prediction = model.predict(
                    input_data,
                    missing_strategy=missing_strategy,
                    full=False)
                prediction_info[self.class_names.index(prediction)] = 1.0
            else:
                predict_method = model.predict_confidence \
                    if method == CONFIDENCE_CODE \
                    else model.predict_probability
                prediction_info = predict_method(
                    input_data,
                    compact=True,
                    missing_strategy=missing_strategy)
            votes.append(prediction_info)

        return MultiVoteList(votes)

    def batch_predict(self, input_data_list, output_file_path=None,
                      reuse=False,
                      missing_strategy=LAST_PREDICTION, headers=None,
                      to_file=True, use_median=False):
        """Makes predictions for a list of input data.

           When the to_file argument is set to True, the predictions
           generated for each model are stored in an output
           file. The name of the file will use the following syntax:
                model_[id of the model]__predictions.csv
           For instance, when using model/50c0de043b563519830001c2 to predict,
           the output file name will be
                model_50c0de043b563519830001c2__predictions.csv
            On the contrary, if it is False, the function returns a list
            of MultiVote objects with the model's predictions.
        """
        add_headers = (isinstance(input_data_list[0], list) and
                       headers is not None and
                       len(headers) == len(input_data_list[0]))
        if not add_headers and not isinstance(input_data_list[0], dict):
            raise ValueError("Input data list is not a dictionary or the"
                             " headers and input data information are not"
                             " consistent.")
        order = 0
        if not to_file:
            votes = []

        for model in self.models:
            order += 1
            out = None
            if to_file:
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
                    out = UnicodeWriter(output_file)
                except IOError:
                    raise Exception("Cannot find %s directory." %
                                    output_file_path)

            if out:
                out.open_writer()
            for index, input_data in enumerate(input_data_list):
                if add_headers:
                    input_data = dict(list(zip(headers, input_data)))
                prediction = model.predict(input_data,
                                           missing_strategy=missing_strategy,
                                           full=True)
                if model.tree.regression:
                    # if median is to be used, we just replace the prediction
                    if use_median:
                        prediction["prediction"] = prediction["median"]
                if to_file:
                    prediction = cast_prediction(prediction, to="list",
                                                 confidence=True,
                                                 distribution=True,
                                                 count=True)
                    out.writerow(prediction)
                else:
                    if len(votes) <= index:
                        votes.append(MultiVote([]))
                    votes[index].append(prediction)
            if out:
                out.close_writer()
        if not to_file:
            return votes

    def batch_votes(self, predictions_file_path, data_locale=None):
        """Adds the votes for predictions generated by the models.

           Returns a list of MultiVote objects each of which contains a list
           of predictions.
        """

        votes_files = []
        for model in self.models:
            votes_files.append(
                get_predictions_file_name(
                    model.resource_id,
                    predictions_file_path))
        return read_votes(
            votes_files, self.models[0].to_prediction, data_locale=data_locale)
