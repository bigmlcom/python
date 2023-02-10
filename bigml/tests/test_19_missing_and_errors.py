# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,line-too-long,attribute-defined-outside-init
#pylint: disable=locally-disabled,unused-import
#
# Copyright 2015-2023 BigML
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
from .world import world, setup_module, teardown_module, show_doc, \
    show_method
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create
from . import read_dataset_steps as dataset_read
from . import create_prediction_steps as prediction_create
from . import compare_predictions_steps as prediction_compare
from . import create_model_steps as model_create

class TestMissingsAndErrors:
    """Testing Missings and Errors retrieval"""

    def setup_method(self, method):
        """
            Debug information
        """
        self.bigml = {}
        self.bigml["method"] = method.__name__
        print("\n-------------------\nTests in: %s\n" % __name__)

    def teardown_method(self):
        """
            Debug information
        """
        print("\nEnd of tests in: %s\n-------------------\n" % __name__)
        self.bigml = {}

    def test_scenario1(self):
        """
        Scenario: Successfully obtaining missing values counts:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I update the source with params "<source_conf>"
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            When I ask for the missing values counts in the fields
            Then the missing values counts dict is "<missing_values>"
        """
        show_doc(self.test_scenario1)
        headers = ["data", "source_wait", "source_conf", "dataset_wait",
                   "missing_values"]
        examples = [
            ['data/iris_missing.csv', '30',
             '{"fields": {"000000": {"optype": "numeric"}}}', '30',
             '{"000000": 1}']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            source_create.i_upload_a_file(self, example["data"])
            source_create.the_source_is_finished(self, example["source_wait"])
            source_create.i_update_source_with(self, example["source_conf"])
            source_create.the_source_is_finished(self, example["source_wait"])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["source_wait"])
            dataset_read.i_get_the_missing_values(self)
            dataset_read.i_get_the_properties_values(
                self, example["missing_values"])

    def test_scenario2(self):
        """
        Scenario: Successfully obtaining parsing error counts:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I update the source with params "<source_conf>"
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            When I ask for the error counts in the fields
            Then the error counts dict is "<error_values>"
        """
        print(self.test_scenario2.__doc__)
        headers = ["data", "source_wait", "source_conf",
                   "dataset_wait", "error_values"]
        examples = [
            ['data/iris_missing.csv', '30',
             '{"fields": {"000000": {"optype": "numeric"}}}', 30,
             '{"000000": 1}']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            source_create.i_upload_a_file(self, example["data"])
            source_create.the_source_is_finished(self, example["source_wait"])
            source_create.i_update_source_with(self, example["source_conf"])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"])
            dataset_read.i_get_the_errors_values(self)
            dataset_read.i_get_the_properties_values(
                self, example["error_values"])

    def test_scenario3(self):
        """
        Scenario: Successfully comparing predictions:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create a model
            And I wait until the model is ready less than <model_wait> secs
            And I create a local model
            When I create a prediction for "<input_data>"
            Then the prediction for "<objective_id>" is "<prediction>"
            And I create a local prediction for "<input_data>"
            Then the local prediction is "<prediction>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "source_conf", "input_data", "objective_id", "prediction"]
        examples = [
            ['data/iris_missing.csv', '30', '30', '50',
            '{"fields": {"000000": {"optype": "numeric"}}, '
            '"source_parser": {"missing_tokens": ["foo"]}}',
            '{"sepal length": "foo", "petal length": 3}',
            '000004', 'Iris-versicolor'],
            ['data/iris_missing.csv', '30', '30', '50',
             '{"fields": {"000000": {"optype": "numeric"}}, '
             '"source_parser": {"missing_tokens": ["foo"]}}',
             '{"sepal length": "foo", "petal length": 5, '
             '"petal width": 1.5}', '000004', 'Iris-virginica']]

        show_doc(self.test_scenario3)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            source_create.i_upload_a_file(
                self, example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"])
            source_create.i_update_source_with(
                self, example["source_conf"])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"])
            model_create.i_create_a_model(self)
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            prediction_compare.i_create_a_local_model(self)
            prediction_create.i_create_a_prediction(
                self, example["input_data"])
            prediction_create.the_prediction_is(
                self, example["objective_id"], example["prediction"])
            prediction_compare.i_create_a_local_prediction(
                self, example["input_data"])
            prediction_compare.the_local_prediction_is(
                self, example["prediction"])
