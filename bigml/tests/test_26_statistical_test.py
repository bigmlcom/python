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


""" Creating test

"""
import sys

from .world import world, setup_module, teardown_module, show_doc, show_method
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create
from . import create_statistical_tst_steps as statistical_tst_create

class TestStatisticalTest(object):

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
            Scenario: Successfully creating an statistical test from a dataset:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create an statistical test from a dataset
                And I wait until the statistical test is ready less than <time_3> secs
                And I update the statistical test name to "<test_name>"
                When I wait until the statistical test is ready less than <time_4> secs
                Then the statistical test name is "<test_name>"

                Examples:
                | data                | time_1  | time_2 | time_3 | time_4 | test_name |
                | ../data/iris.csv | 10      | 10     | 20     | 20 | my new statistical test name |
        """
        show_doc(self.test_scenario1)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "test_name"]
        examples = [
            ['data/iris.csv', '10', '10', '20', '20',
             'my new statistical test name']]
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
            statistical_tst_create.i_create_a_tst_from_dataset(self)
            statistical_tst_create.the_tst_is_finished_in_less_than(
                self, example["model_wait"])
            statistical_tst_create.i_update_tst_name(
                self, example["test_name"])
            statistical_tst_create.the_tst_is_finished_in_less_than(
                self, example["model_wait"])
            statistical_tst_create.i_check_tst_name(
                self, example["test_name"])
