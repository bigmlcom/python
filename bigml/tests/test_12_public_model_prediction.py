# -*- coding: utf-8 -*-
#
# Copyright 2015-2022 BigML
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


""" Creating public model predictions

"""
import sys

from .world import world, setup_module, teardown_module, show_doc, \
    show_method, delete_local
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create
from . import create_model_steps as model_create
from . import create_prediction_steps as prediction_create
from . import compare_predictions_steps as compare_pred

class TestPublicModelPrediction(object):

    def setup_method(self):
        """
            Debug information
        """
        print("\n-------------------\nTests in: %s\n" % __name__)

    def teardown_method(self):
        """
            Debug information
        """
        delete_local()
        print("\nEnd of tests in: %s\n-------------------\n" % __name__)

    def test_scenario1(self):
        """
            Scenario: Successfully creating a prediction using a public model:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a model
                And I wait until the model is ready less than <time_3> secs
                And I make the model public
                And I wait until the model is ready less than <time_3> secs
                And I check the model status using the model's public url
                When I create a prediction for "<data_input>"
                Then the prediction for "<objective>" is "<prediction>"

                Examples:
                | data                | time_1  | time_2 | time_3 | data_input    | objective | prediction  |
                | ../data/iris.csv | 10      | 10     | 10     | {"petal width": 0.5} | 000004    | Iris-setosa |
        """
        show_doc(self.test_scenario1)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "input_data", "objective_id", "prediction"]
        examples = [
            ['data/iris.csv', '10', '10', '10', '{"petal width": 0.5}',
             '000004', 'Iris-setosa']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            dataset_create.i_create_a_dataset(self, shared=example["data"])
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"], shared=example["data"])
            model_create.i_create_a_model(self)
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            model_create.make_the_model_public(self)
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            model_create.model_from_public_url(self)
            prediction_create.i_create_a_prediction(
                self, example["input_data"])
            prediction_create.the_prediction_is(
                self, example["objective_id"], example["prediction"])
