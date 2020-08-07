# -*- coding: utf-8 -*-
#
# Copyright 2019-2020 BigML
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


""" Creating Linear Regression

"""
from .world import world, setup_module, teardown_module
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create
from . import create_linear_steps as linear_create
from . import create_prediction_steps as prediction_create
from . import create_batch_prediction_steps as batch_pred_create

class TestLinearRegression(object):

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
            Scenario: Successfully creating a linear regression from a dataset:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a linear regression from a dataset
                And I wait until the linear regression is ready less than <time_3> secs
                And I update the linear regression name to "<linear_name>"
                When I wait until the linear regression is ready less than <time_4> secs
                Then the linear regression name is "<linear_name>"

                Examples:
                | data                | time_1  | time_2 | time_3 | time_4 | linear_name |
                | ../data/iris.csv | 10      | 10     | 20     | 20 | my new linear regression name |
        """
        print(self.test_scenario1.__doc__)
        examples = [
            ['data/grades.csv', '100', '100', '200', '200', 'my new linear regression name']]
        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            linear_create.i_create_a_linear_regression_from_dataset(self)
            linear_create.the_linear_regression_is_finished_in_less_than(self, example[3])
            linear_create.i_update_linear_regression_name(self, example[5])
            linear_create.the_linear_regression_is_finished_in_less_than(self, example[4])
            linear_create.i_check_linear_name(self, example[5])

        print("\nEnd of tests in: %s\n-------------------\n" % __name__)

    def test_scenario2(self):
        """
            Scenario: Successfully creating a prediction from linear regression:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a pca
                And I wait until the linear regression is ready less than <time_3> secs
                When I create a prediction for "<data_input>"
                Then the prediction is "<prediction>"

                Examples:
                | data                | time_1  | time_2 | time_3 | data_input    |objective | prediction  |

        """
        print(self.test_scenario2.__doc__)
        examples = [
            ['data/grades.csv', '30', '30', '30', '{"000000": 0.5, "000001": 1, "000002": 1, "000003": 1}', "000005", '2.27312', '{}'],
            ['data/grades.csv', '30', '30', '30', '{"000000": 0.5, "000001": 1, "000002": 1, "000003": 1}', "000005", '8.19619', '{"bias": false}'],
            ['data/dates.csv', '30', '30', '30', '{"test-num1": 23, "test-num2" : 54, "test-date.day-of-month":2, "test-date.month":12, "test-date.day-of-week": 2, "test-date.year": 2012}', "000003", '48.27679', '{"bias": false}']]
        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            linear_create.i_create_a_linear_regression_with_objective_and_params(self, example[5], example[7])
            linear_create.the_linear_regression_is_finished_in_less_than(self, example[3])
            prediction_create.i_create_a_linear_prediction(self, example[4])
            prediction_create.the_prediction_is(self, example[5], example[6])

        print("\nEnd of tests in: %s\n-------------------\n" % __name__)


    def test_scenario3(self):
        """
            Scenario: Successfully creating a batch prediction from a linear regression:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a linear regression
                And I wait until the linear regression is ready less than <time_3> secs
                When I create a batch prediction for the dataset with the linear regression
                And I wait until the batch predictin is ready less than <time_4> secs
                And I download the created predictions file to "<local_file>"
                Then the batch prediction file is like "<predictions_file>"

                Examples:
                | data             | time_1  | time_2 | time_3 | time_4 | local_file | predictions_file       |


        """
        print(self.test_scenario3.__doc__)
        examples = [
            ['data/grades.csv', '30', '30', '50', '50', 'tmp/batch_predictions.csv', 'data/batch_predictions_linear.csv']]
        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            linear_create.i_create_a_linear_regression_from_dataset(self)
            linear_create.the_linear_regression_is_finished_in_less_than(self, example[3])
            batch_pred_create.i_create_a_linear_batch_prediction(self)
            batch_pred_create.the_batch_prediction_is_finished_in_less_than(self, example[4])
            batch_pred_create.i_download_predictions_file(self, example[5])
            batch_pred_create.i_check_predictions(self, example[6])
