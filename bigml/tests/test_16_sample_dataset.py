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


""" Creating sample dataset

"""
import sys

from .world import world, setup_module, teardown_module, show_doc, \
    show_method, delete_local
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create
from . import create_sample_steps as sample_create

class TestSampleDataset(object):

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
            Scenario: Successfully creating a sample from a dataset:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a sample from a dataset
                And I wait until the sample is ready less than <sample_wait> secs
                And I update the sample name to "<sample_name>"
                When I wait until the sample is ready less than <sample_wait> secs
                Then the sample name is "<sample_name>"
        """
        show_doc(self.test_scenario1)
        headers = ["data", "source_wait", "dataset_wait", "sample_wait",
                   "sample_name"]
        examples = [
            ['data/iris.csv', '10', '10', '10', 'my new sample name']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(self, example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            dataset_create.i_create_a_dataset(self, shared=example["data"])
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"], shared=example["data"])
            sample_create.i_create_a_sample_from_dataset(self)
            sample_create.the_sample_is_finished_in_less_than(
                self, example["sample_wait"])
            sample_create.i_update_sample_name(self, example["sample_name"])
            sample_create.the_sample_is_finished_in_less_than(
                self, example["sample_wait"])
            sample_create.i_check_sample_name(self, example["sample_name"])

    def test_scenario2(self):
        """

            Scenario: Successfully cloning dataset:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I clone the last dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                Then the new dataset is as the origin dataset
        """
        show_doc(self.test_scenario2)
        headers = ["data", "source_wait", "dataset_wait"]
        examples = [
            ['data/iris.csv', '30', '30']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(self, example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            source = world.source["resource"]
            source_create.clone_source(self, source)
            source_create.the_source_is_finished(self, example["source_wait"])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"])
            dataset = world.dataset["resource"]
            dataset_create.clone_dataset(self, dataset)
            dataset_create.the_cloned_dataset_is(self, dataset)
