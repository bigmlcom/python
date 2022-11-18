# -*- coding: utf-8 -*-
#
# Copyright 2019-2022 BigML
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
import sys

from .world import world, setup_module, teardown_module, show_doc, \
    show_method, delete_local
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create
from . import create_linear_steps as linear_create
from . import create_prediction_steps as prediction_create
from . import create_batch_prediction_steps as batch_pred_create

class TestLinearRegression(object):

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
            Scenario: Successfully creating a linear regression from a dataset:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a linear regression from a dataset
                And I wait until the linear regression is ready less than <model_wait> secs
                And I update the linear regression name to "<linear_name>"
                When I wait until the linear regression is ready less than <model_wait> secs
                Then the linear regression name is "<linear_name>"
        """
        show_doc(self.test_scenario1)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "linear_name"]
        examples = [
            ['data/grades.csv', '100', '100', '200', 'my new linear regression name']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"], shared=example["data"])
            linear_create.i_create_a_linear_regression_from_dataset(self)
            linear_create.the_linear_regression_is_finished_in_less_than(
                self, example["model_wait"])
            linear_create.i_update_linear_regression_name(
                self, example["linear_name"])
            linear_create.the_linear_regression_is_finished_in_less_than(
                self, example["model_wait"])
            linear_create.i_check_linear_name(self, example["linear_name"])

        print("\nEnd of tests in: %s\n-------------------\n" % __name__)

    def test_scenario2(self):
        """
            Scenario: Successfully creating a prediction from linear regression:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a pca
                And I wait until the linear regression is ready less than <model_wait> secs
                When I create a prediction for "<input_data>"
                Then the prediction is "<prediction>"
        """
        show_doc(self.test_scenario2)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "input_data", "objective_id", "prediction", "model_conf"]
        examples = [
            ['data/grades.csv', '30', '30', '50',
             '{"000000": 0.5, "000001": 1, "000002": 1, "000003": 1}',
             "000005", '2.27312', '{}'],
            ['data/grades.csv', '30', '30', '50',
             '{"000000": 0.5, "000001": 1, "000002": 1, "000003": 1}',
             "000005", '8.19619', '{"bias": false}'],
            ['data/dates.csv', '30', '30', '30',
             '{"test-num1": 23, "test-num2" : 54, "test-date.day-of-month":2, '
             '"test-date.month":12, "test-date.day-of-week": 2, '
             '"test-date.year": 2012}', "000003", '48.27679',
             '{"bias": false}']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"])
            linear_create.i_create_a_linear_regression_with_objective_and_params(
                self, example["objective_id"], example["model_conf"])
            linear_create.the_linear_regression_is_finished_in_less_than(
                self, example["model_wait"])
            prediction_create.i_create_a_linear_prediction(
                self, example["input_data"])
            prediction_create.the_prediction_is(
                self, example["objective_id"], example["prediction"])

        print("\nEnd of tests in: %s\n-------------------\n" % __name__)


    def test_scenario3(self):
        """
            Scenario: Successfully creating a batch prediction from a linear regression:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a linear regression
                And I wait until the linear regression is ready less than <model_wait> secs
                When I create a batch prediction for the dataset with the linear regression
                And I wait until the batch predictin is ready less than <batch_wait> secs
                And I download the created predictions file to "<local_file>"
                Then the batch prediction file is like "<predictions_file>"
        """
        show_doc(self.test_scenario3)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "batch_wait", "local_file", "predictions_file"]
        examples = [
            ['data/grades.csv', '30', '30', '50', '50',
             'tmp/batch_predictions.csv', 'data/batch_predictions_linear.csv']]
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
            linear_create.i_create_a_linear_regression_from_dataset(self)
            linear_create.the_linear_regression_is_finished_in_less_than(
                self, example["model_wait"])
            batch_pred_create.i_create_a_linear_batch_prediction(self)
            batch_pred_create.the_batch_prediction_is_finished_in_less_than(
                self, example["batch_wait"])
            batch_pred_create.i_download_predictions_file(
                self, example["local_file"])
            batch_pred_create.i_check_predictions(
                self, example["predictions_file"])
