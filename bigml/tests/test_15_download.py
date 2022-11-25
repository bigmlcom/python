# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,line-too-long,attribute-defined-outside-init
#pylint: disable=locally-disabled,unused-import
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


""" Downloading dataset

"""
from .world import world, setup_module, teardown_module, show_doc, \
    show_method
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create
from . import create_model_steps as model_create


class TestDownload:
    """Testing downloads"""

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
        Scenario: Successfully exporting a dataset:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <time_1> secs
            And I create a dataset
            And I wait until the dataset is ready less than <time_2> secs
            And I download the dataset file to "<local_file>"
            Then file "<local_file>" is like file "<data>"
        """
        show_doc(self.test_scenario1)
        headers = ["data", "source_wait", "dataset_wait", "exported_file"]
        examples = [
            ['data/iris.csv', '30', '30', 'tmp/exported_iris.csv']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            dataset_create.i_create_a_dataset(self, shared=example["data"])
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"], shared=example["data"])
            dataset_create.i_export_a_dataset(self, example["exported_file"])
            dataset_create.files_equal(
                self, example["exported_file"], example["data"])

    def test_scenario2(self):
        """
        Scenario: Successfully creating a model and exporting it:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create a model
            And I wait until the model is ready less than <model_wait> secs
            And I export the <"pmml"> model to file "<exported_file>"
            Then I check the model is stored in "<exported_file>" file in <"pmml">
        """
        show_doc(self.test_scenario2)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "exported_file", "pmml"]
        examples = [
            ['data/iris.csv', '30', '30', '30', 'tmp/model/iris.json', False],
            ['data/iris_sp_chars.csv', '30', '30', '30', 'tmp/model/iris_sp_chars.pmml', True]]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            source_create.i_upload_a_file(self, example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            dataset_create.i_create_a_dataset(self, shared=example["data"])
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"], shared=example["data"])
            model_create.i_create_a_model(self, shared=example["data"])
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"], shared=example["data"])
            model_create.i_export_model(
                self, example["pmml"], example["exported_file"])
            model_create.i_check_model_stored(
                self, example["exported_file"], example["pmml"])
