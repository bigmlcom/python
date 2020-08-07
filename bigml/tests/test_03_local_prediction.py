# -*- coding: utf-8 -*-
#
# Copyright 2015-2020 BigML
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
from .world import world, setup_module, teardown_module
from . import compare_predictions_steps as prediction_compare


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
        print("\nEnd of tests in: %s\n-------------------\n" % __name__)

    def test_scenario1(self):
        """
            Scenario: Successfully creating a prediction from a local model in a json file:
                Given I create a local model from a "<model>" file
                When I create a local prediction for "<data_input>" with confidence
                Then the local prediction is "<prediction>"
                And the local prediction's confidence is "<confidence>"

                Examples:
                | model                | data_input    |  prediction  | confidence
                | ../data/iris_model.json | {"petal length": 0.5} | Iris-setosa | 0.90594

        """
        print(self.test_scenario1.__doc__)
        examples = [
            ['data/iris_model.json', '{"petal length": 0.5}', 'Iris-setosa', '0.90594'],
            ['data/iris_model.json', '{"petal length": "0.5"}', 'Iris-setosa', '0.90594']]
        for example in examples:
            print("\nTesting with:\n", example)
            prediction_compare.i_create_a_local_model_from_file(self, example[0])
            prediction_compare.i_create_a_local_prediction_with_confidence(self, example[1])
            prediction_compare.the_local_prediction_is(self, example[2])
            prediction_compare.the_local_prediction_confidence_is(self, example[3])
