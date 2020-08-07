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


""" Creating datasets with missing values and errors counters

"""
from .world import world, setup_module, teardown_module, show_doc
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create
from . import read_dataset_steps as dataset_read
from . import create_prediction_steps as prediction_create
from . import compare_predictions_steps as prediction_compare
from . import create_model_steps as model_create

class TestMissingsAndErrors(object):

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
            Scenario: Successfully obtaining missing values counts:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I update the source with params "<params>"
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                When I ask for the missing values counts in the fields
                Then the missing values counts dict is "<missing_values>"

                Examples:
                | data                     | time_1  | params                                          | time_2 |missing_values       |
                | ../data/iris_missing.csv | 30      | {"fields": {"000000": {"optype": "numeric"}}}   |30      |{"000000": 1}      |
        """
        print(self.test_scenario1.__doc__)
        examples = [
            ['data/iris_missing.csv', '30', '{"fields": {"000000": {"optype": "numeric"}}}', '30', '{"000000": 1}']]
        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            source_create.i_update_source_with(self, example[2])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self,
                                                                example[3])
            dataset_read.i_get_the_missing_values(self)
            dataset_read.i_get_the_properties_values(
                self, 'missing values count', example[4])

    def test_scenario2(self):
        """
            Scenario: Successfully obtaining parsing error counts:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I update the source with params "<params>"
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                When I ask for the error counts in the fields
                Then the error counts dict is "<error_values>"

                Examples:
                | data                     | time_1  | params                                          | time_2 |error_values       |
                | ../data/iris_missing.csv | 30      | {"fields": {"000000": {"optype": "numeric"}}}   |30      |{"000000": 1}      |
        """
        print(self.test_scenario2.__doc__)
        examples = [
            ['data/iris_missing.csv', '30', '{"fields": {"000000": {"optype": "numeric"}}}', '30', '{"000000": 1}']]
        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            source_create.i_update_source_with(self, example[2])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self,
                                                                example[3])
            dataset_read.i_get_the_errors_values(self)
            dataset_read.i_get_the_properties_values(
                self, 'error counts', example[4])

    def test_scenario3(self):
        """
            Scenario: Successfully comparing predictions:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a model
                And I wait until the model is ready less than <time_3> secs
                And I create a local model
                When I create a prediction for "<data_input>"
                Then the prediction for "<objective>" is "<prediction>"
                And I create a local prediction for "<data_input>"
                Then the local prediction is "<prediction>"

                Examples:
                | data             | time_1  | time_2 | time_3 | data_input                             | objective | prediction  |

        """
        examples = [
            ['data/iris_missing.csv', '30', '{"fields": {"000000": {"optype": "numeric"}}, "source_parser": {"missing_tokens": ["foo"]}}', '30', '{"sepal length": "foo", "petal length": 3}', '000004', 'Iris-versicolor'],
            ['data/iris_missing.csv', '30', '{"fields": {"000000": {"optype": "numeric"}}, "source_parser": {"missing_tokens": ["foo"]}}', '30', '{"sepal length": "foo", "petal length": 5, "petal width": 1.5}', '000004', 'Iris-virginica']]

        show_doc(self.test_scenario3, examples)
        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            source_create.i_update_source_with(self, example[2])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[3])
            model_create.i_create_a_model(self)
            model_create.the_model_is_finished_in_less_than(self, example[3])
            prediction_compare.i_create_a_local_model(self)
            prediction_create.i_create_a_prediction(self, example[4])
            prediction_create.the_prediction_is(self, example[5], example[6])
            prediction_compare.i_create_a_local_prediction(self, example[4])
            prediction_compare.the_local_prediction_is(self, example[6])
