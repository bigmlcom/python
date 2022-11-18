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


""" Creating multimodel predictions

"""
import sys

from .world import world, setup_module, teardown_module, show_doc, \
    show_method, delete_local
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create
from . import create_model_steps as model_create
from . import create_ensemble_steps as ensemble_create
from . import create_prediction_steps as prediction_create
from . import compare_predictions_steps as compare_pred

class TestMultimodelPrediction(object):

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
            Scenario: Successfully creating a prediction from a multi model:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a model with "<tags>"
                And I wait until the model is ready less than <model_wait> secs
                And I create a model with "<tags>"
                And I wait until the model is ready less than <model_wait> secs
                And I create a model with "<tags>"
                And I wait until the model is ready less than <model_wait> secs
                And I retrieve a list of remote models tagged with "<tag>"
                And I create a local multi model
                When I create a local prediction for "<input_data>"
                Then the prediction for "<objective_id>" is "<prediction>"
        """
        show_doc(self.test_scenario1)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "tags", "tag", "input_data", "prediction"]
        examples = [
            ['data/iris.csv', '10', '10', '10', '{"tags":["mytag"]}',
             'mytag', '{"petal width": 0.5}', 'Iris-setosa']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(self, example["source_wait"],
                shared=example["data"])
            dataset_create.i_create_a_dataset(self, shared=example["data"])
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"], shared=example["data"])
            model_create.i_create_a_model_with(self, example["tags"])
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            model_create.i_create_a_model_with(self, example["tags"])
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            model_create.i_create_a_model_with(self, example["tags"])
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            compare_pred.i_retrieve_a_list_of_remote_models(
                self, example["tag"])
            compare_pred.i_create_a_local_multi_model(self)
            compare_pred.i_create_a_local_prediction(
                self, example["input_data"])
            compare_pred.the_local_prediction_is(self, example["prediction"])

    def test_scenario2(self):
        """

            Scenario: Successfully creating a local batch prediction from a multi model:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a model with "<tags>"
                And I wait until the model is ready less than <model_wait> secs
                And I create a model with "<tags>"
                And I wait until the model is ready less than <model_wait> secs
                And I create a model with "<tags>"
                And I wait until the model is ready less than <model_wait> secs
                And I retrieve a list of remote models tagged with "<tag>"
                And I create a local multi model
                When I create a batch multimodel prediction for "<input_data>"
                Then the predictions are "<predictions>"
        """
        show_doc(self.test_scenario2)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "tags", "tag", "input_data", "predictions"]
        examples = [
            ['data/iris.csv', '10', '10', '10', '{"tags":["mytag"]}',
             'mytag', '[{"petal width": 0.5}, {"petal length": 6, '
             '"petal width": 2}]', '["Iris-setosa", "Iris-virginica"]']]
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
            model_create.i_create_a_model_with(self, example["tags"])
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            model_create.i_create_a_model_with(self, example["tags"])
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            model_create.i_create_a_model_with(self, example["tags"])
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            compare_pred.i_retrieve_a_list_of_remote_models(
                self, example["tag"])
            compare_pred.i_create_a_local_multi_model(self)
            compare_pred.i_create_a_batch_prediction_from_a_multi_model(
                self, example["input_data"])
            compare_pred.the_batch_mm_predictions_are(
                self, example["predictions"])
