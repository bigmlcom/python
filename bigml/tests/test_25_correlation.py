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


""" Creating correlation

"""
from .world import world, setup_module, teardown_module, show_doc, \
    show_method
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create
from . import create_correlation_steps as correlation_create

class TestCorrelation:
    """Test Correlation methods"""

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
        Scenario: Successfully creating a correlation from a dataset:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create a correlation from a dataset
            And I wait until the correlation is ready less than <model_wait> secs
            And I update the correlation name to "<correlation_name>"
            When I wait until the correlation is ready less than <model_wait> secs
            Then the correlation name is "<correlation_name>"
        """
        show_doc(self.test_scenario1)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "correlation_name"]
        examples = [
            ['data/iris.csv', '10', '10', '20', 'my new correlation name']]
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
            correlation_create.i_create_a_correlation_from_dataset(self)
            correlation_create.the_correlation_is_finished_in_less_than(
                self, example["model_wait"])
            correlation_create.i_update_correlation_name(
                self, example["correlation_name"])
            correlation_create.the_correlation_is_finished_in_less_than(
                self, example["model_wait"])
            correlation_create.i_check_correlation_name(
                self, example["correlation_name"])
