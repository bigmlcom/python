# -*- coding: utf-8 -*-
#
# Copyright 2015-2021 BigML
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


""" Creating ensembles predictions

"""
import sys

from .world import world, setup_module, teardown_module, show_doc, show_method
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create
from . import create_ensemble_steps as ensemble_create
from . import create_prediction_steps as prediction_create

class TestEnsemblePrediction(object):

    def setup(self):
        """
            Debug information
        """
        print("\n-------------------\nTests in: %s\n" % __name__)

    def teardown(self):
        """
            Debug information
        """
        print("\nEnd of tests in: %s\n-------------------\n" % __name__)

    def test_scenario1(self):
        """
            Scenario: Successfully creating a prediction from an ensemble:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create an ensemble of <number_of_models> models
                And I wait until the ensemble is ready less than <model_wait> secs
                When I create an ensemble prediction for "<input_data>"
                And I wait until the prediction is ready less than <prediction_wait> secs
                Then the prediction for "<objective_id>" is "<prediction>"
        """
        show_doc(self.test_scenario1)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "prediction_wait", "number_of_models", "input_data",
                   "objective_id", "prediction"]
        examples = [
            ['data/iris.csv', '30', '30', '50', '20', '5',
             '{"petal width": 0.5}', '000004', 'Iris-versicolor'],
            ['data/iris_sp_chars.csv', '30', '30', '50', '20', '5',
             '{"pétal&width\\u0000": 0.5}', '000004', 'Iris-versicolor'],
            ['data/grades.csv', '30', '30', '150', '20', '10',
             '{"Assignment": 81.22, "Tutorial": 91.95, "Midterm": 79.38,'
             ' "TakeHome": 105.93}', '000005', '84.556'],
            ['data/grades.csv', '30', '30', '150', '20', '10',
             '{"Assignment": 97.33, "Tutorial": 106.74, "Midterm": 76.88,'
             ' "TakeHome": 108.89}', '000005', '73.13558']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(self, example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            dataset_create.i_create_a_dataset(self, shared=example["data"])
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"], shared=example["data"])
            ensemble_shared = "%s_%s" % (example["data"],
                example["number_of_models"])
            ensemble_create.i_create_an_ensemble(
                self, example["number_of_models"], shared=ensemble_shared)
            ensemble_create.the_ensemble_is_finished_in_less_than(
                self, example["model_wait"], shared=ensemble_shared)
            prediction_create.i_create_an_ensemble_prediction(
                self, example["input_data"])
            prediction_create.the_prediction_is_finished_in_less_than(
                self, example["prediction_wait"])
            prediction_create.the_prediction_is(
                self, example["objective_id"], example["prediction"])
