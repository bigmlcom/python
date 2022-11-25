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


""" Creating public dataset

"""
from .world import world, setup_module, teardown_module, show_doc, \
    show_method
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create

class TestPublicDataset:
    """Testing published datasets """

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
        Scenario: Successfully creating and reading a public dataset:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I make the dataset public
            And I wait until the dataset is ready less than <dataset_wait> secs
            When I get the dataset status using the dataset's public url
            Then the dataset's status is FINISHED
        """
        show_doc(self.test_scenario1)
        headers = ["data", "source_wait", "dataset_wait"]
        examples = [
            ['data/iris.csv', '10', '10']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            source_create.i_upload_a_file_from_stdin(
                self, example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"])
            dataset_create.make_the_dataset_public(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"])
            dataset_create.build_local_dataset_from_public_url(self)
            dataset_create.dataset_status_finished(self)
