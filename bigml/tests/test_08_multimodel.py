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


""" Creating model on lists of datasets

"""
import sys

from .world import world, setup_module, teardown_module, show_doc, show_method
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create
from . import create_model_steps as model_create
from . import create_multimodel_steps as multimodel_create
from . import compare_predictions_steps as compare_pred

class TestMultimodel(object):

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
            Scenario: Successfully creating a model from a dataset list:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I store the dataset id in a list
                And I create a dataset
                And I wait until the dataset is ready less than <time_3> secs
                And I store the dataset id in a list
                Then I create a model from a dataset list
                And I wait until the model is ready less than <time_4> secs
                And I check the model stems from the original dataset list
        """
        show_doc(self.test_scenario1)
        headers = ["data", "source_wait", "dataset_wait", "model_wait"]
        examples = [
            ['data/iris.csv', '10', '10', '10']]
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
            multimodel_create.i_store_dataset_id(self)
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"])
            multimodel_create.i_store_dataset_id(self)
            model_create.i_create_a_model_from_dataset_list(self)
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            multimodel_create.i_check_model_datasets_and_datasets_ids(self)

    def test_scenario2(self):
        """
            Scenario: Successfully creating a model from a dataset list and predicting with it using median:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a model
                And I wait until the model is ready less than <time_3> secs
                And I create a local multi model
                When I create a local multimodel batch prediction using median for <input_data>
                Then the local prediction is <prediction>
        """
        show_doc(self.test_scenario2)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "input_data", "prediction"]
        examples = [
            ['data/grades.csv', '30', '30', '30',
             '{"Tutorial": 99.47, "Midterm": 53.12, "TakeHome": 87.96}',
             63.33]]
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
            model_create.i_create_a_model(self, shared=example["data"])
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"], shared=example["data"])
            world.list_of_models = [world.model]
            compare_pred.i_create_a_local_multi_model(self)
            compare_pred.i_create_a_local_mm_median_batch_prediction(
                self, example["input_data"])
            compare_pred.the_local_prediction_is(self, example["prediction"])
