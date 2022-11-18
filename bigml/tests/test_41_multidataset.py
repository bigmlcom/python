# -*- coding: utf-8 -*-
#
# Copyright 2018-2022 BigML
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


""" Creating a sampled multidataset

"""
import sys

from .world import world, setup_module, teardown_module, show_doc, \
    show_method, delete_local
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create

class TestMultiDataset(object):

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
            Scenario: Successfully creating a sampled multi-dataset:
                Given I create a data source with "<params>" uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a multi-dataset with sample rates <rates>
                And I wait until the multi-dataset is ready less than <dataset_wait> secs
                When I compare the datasets' instances
                Then the proportion of instances between datasets is <rate>
        """
        show_doc(self.test_scenario1)
        headers = ["data", "source_wait", "dataset_wait", "rate",
                   "rates"]
        examples = [
            ['data/iris.csv', '50', '50', '0.5', '[0.2, 0.3]']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file_with_args(
                self, example["data"], '{}')
            source_create.the_source_is_finished(
                self, example["source_wait"])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"])
            dataset_create.i_create_a_multidataset(
                self, example["rates"])
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"])
            dataset_create.i_compare_datasets_instances(self)
            dataset_create.proportion_datasets_instances(
            self, example["rate"])


    def test_scenario2(self):
        """
            Scenario: Successfully creating a single dataset multi-dataset:
                Given I create a data source with "<params>" uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a multi-dataset with sample rates <rates>
                And I wait until the multi-dataset is ready less than <dataset_wait> secs
                When I compare the datasets' instances
                Then the proportion of instances between datasets is <rate>
        """
        show_doc(self.test_scenario2)
        headers = ["data", "source_wait", "dataset_wait", "rate",
                   "rates"]
        examples = [
            ['data/iris.csv', '50', '50', '0.2', '[0.2]']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file_with_args(
                self, example["data"], '{}')
            source_create.the_source_is_finished(
                self, example["source_wait"])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"])
            dataset_create.i_create_a_multidataset(
                self, example["rates"])
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"])
            dataset_create.i_compare_datasets_instances(self)
            dataset_create.proportion_datasets_instances(
                self, example["rate"])

    def test_scenario3(self):
        """
            Scenario: Successfully creating a sampled multi-dataset with sample:
                Given I create a data source with "<params>" uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a multi-dataset with same dataset and the first sample rate <rates>
                And I wait until the multi-dataset is ready less than <dataset_wait> secs
                When I compare the datasets' instances
                Then the proportion of instances between datasets is <rate>
        """
        show_doc(self.test_scenario3)
        headers = ["data", "source_wait", "dataset_wait", "rate",
                   "rates"]
        examples = [
            ['data/iris.csv', '50', '50', '1.3', '[1, 0.3]']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file_with_args(
                self, example["data"], '{}')
            source_create.the_source_is_finished(
                self, example["source_wait"])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"])
            dataset_create.i_create_a_multidataset_mixed_format(
                self, example["rates"])
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"])
            dataset_create.i_compare_datasets_instances(self)
            dataset_create.proportion_datasets_instances(
                self, example["rate"])
