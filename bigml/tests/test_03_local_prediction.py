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


""" Testing local prediction

"""
import sys

from .world import world, setup_module, teardown_module, show_doc, \
    show_method, delete_local
from . import compare_predictions_steps as prediction_compare
from . import create_ensemble_steps as ensemble_create
from . import create_prediction_steps as prediction_create


class TestLocalPrediction(object):

    def setup(self):
        """
            Debug information
        """
        print("\n-------------------\nTests in: %s\n" % __name__)

    def teardown(self):
        """
            Debug information
        """
        delete_local()
        print("\nEnd of tests in: %s\n-------------------\n" % __name__)

    def test_scenario1(self):
        """
            Scenario 1: Successfully creating a prediction from a local model in a json file:
                Given I create a local model from a "<model>" file
                When I create a local prediction for "<data_input>" with confidence
                Then the local prediction is "<prediction>"
                And the local prediction's confidence is "<confidence>"
        """
        show_doc(self.test_scenario1)
        headers = ["file_path", "input_data", "prediction", "confidence"]
        examples = [
            ['data/iris_model.json', '{"petal length": 0.5}', 'Iris-setosa',
             '0.90594'],
            ['data/iris_model.json', '{"petal length": "0.5"}', 'Iris-setosa',
             '0.90594']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            prediction_compare.i_create_a_local_model_from_file(
                self, example["file_path"])
            prediction_compare.i_create_a_local_prediction_with_confidence(
                self, example["input_data"])
            prediction_compare.the_local_prediction_is(
                self, example["prediction"])
            prediction_compare.the_local_prediction_confidence_is(
                self, example["confidence"])

    def test_scenario2(self):
        """
            Scenario 2: Successfully creating a prediction from a local model in a json file:
                Given I create a local model using SupervisedModel from a "<model>" file
                When I create a local prediction for "<data_input>" with confidence
                Then the local prediction is "<prediction>"
                And the local prediction's confidence is "<confidence>"
        """
        show_doc(self.test_scenario2)
        headers = ["file_path", "input_data", "prediction", "confidence"]
        examples = [
            ['data/iris_model.json', '{"petal length": 0.5}', 'Iris-setosa',
             '0.90594'],
            ['data/iris_model.json', '{"petal length": "0.5"}', 'Iris-setosa',
             '0.90594']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            prediction_compare.i_create_a_local_supervised_model_from_file(
                self, example["file_path"])
            prediction_compare.i_create_a_local_prediction_with_confidence(
                self, example["input_data"])
            prediction_compare.the_local_prediction_is(
                self, example["prediction"])
            prediction_compare.the_local_prediction_confidence_is(
                self, example["confidence"])


    def test_scenario3(self):
        """
            Scenario 3: Successfully creating a local prediction from an Ensemble created from file storage:
                Given I create a local Ensemble from path "<path>"
                When I create a local ensemble prediction with confidence for "<data_input>"
                Then the local prediction is "<prediction>"
                And the local prediction's confidence is "<confidence>"
                And the local probabilities are "<probabilities>"
        """
        show_doc(self.test_scenario3)
        headers = ["file_path", "input_data", "prediction", "confidence",
                   "probabilities"]
        examples = [
            ['bigml/tests/my_no_root_ensemble/ensemble.json',
             '{"petal width": 0.5}', 'Iris-setosa', '0.3533',
             '["0.3533", "0.31", "0.33666"]' ]]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            ensemble_create.create_local_ensemble(
                self, path=example["file_path"])
            prediction_create.create_local_ensemble_prediction_with_confidence(
                self, example["input_data"])
            prediction_compare.the_local_prediction_is(
                self, example["prediction"])
            prediction_compare.the_local_prediction_confidence_is(
                self, example["confidence"])
            prediction_compare.the_local_probabilities_are(
                self, example["probabilities"])

    def test_scenario4(self):
        """
            Scenario 4: Successfully creating a local prediction from an Ensemble created from file storage:
                Given I create a local SupervisedModel from path "<path>"
                When I create a local ensemble prediction with confidence for "<data_input>"
                Then the local prediction is "<prediction>"
                And the local prediction's confidence is "<confidence>"
                And the local probabilities are "<probabilities>"
        """
        show_doc(self.test_scenario4)
        headers = ["file_path", "input_data", "prediction", "confidence",
                   "probabilities"]
        examples = [
            ['bigml/tests/my_no_root_ensemble/ensemble.json',
             '{"petal width": 0.5}', 'Iris-setosa', '0.3533',
             '["0.3533", "0.31", "0.33666"]' ]]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            prediction_compare.i_create_a_local_supervised_model_from_file(
                self, example["file_path"])
            prediction_compare.i_create_a_local_prediction_with_confidence(
                self, example["input_data"])
            prediction_compare.the_local_prediction_is(
                self, example["prediction"])
            prediction_compare.the_local_prediction_confidence_is(
                self, example["confidence"])
            prediction_compare.the_local_probabilities_are(
                self, example["probabilities"])

    def test_scenario5(self):
        """
            Scenario 5: Successfully creating a prediction from a local images deepnet in a json file:
                Given I create a local deepnet from a "<deepnet>" file
                When I create a local prediction for "<data_input>"
                Then the local prediction is "<prediction>"
        """
        show_doc(self.test_scenario5)
        headers = ["file_path", "input_data", "operation_settings",
                   "prediction"]
        examples = [
            ['data/imgs_deepnet.zip', "data/images/cats/pexels-pixabay-33358.jpg",
             {"region_score_threshold": 0.7},
             '{"prediction": [{"box": [0.68164, 0.30469, 0.79688, 0.36979], "label": "eye", "score": 0.79633}, {"box": [0.38086, 0.27865, 0.50391, 0.36068], "label": "eye", "score": 0.74563}]}']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            prediction_compare.i_create_a_local_deepnet_from_zip_file(
                self, example["file_path"],
                operation_settings=example["operation_settings"])
            prediction_compare.i_create_a_local_regions_prediction(
                self, example["input_data"])
            prediction_compare.the_local_regions_prediction_is(
                self, example["prediction"])
