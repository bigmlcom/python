# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015-2016 BigML
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
from world import world, setup_module, teardown_module
import create_source_steps as source_create
import create_dataset_steps as dataset_create
import read_dataset_steps as dataset_read

class TestMissingsAndErrors(object):

    def setup(self):
        """
            Debug information
        """
        print "\n-------------------\nTests in: %s\n" % __name__

    def teardown(self):
        """
            Debug information
        """
        print "\nEnd of tests in: %s\n-------------------\n" % __name__

    def test_scenario1(self):
        """
            Scenario: Successfully obtaining missing values counts:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I update the source with params "<params>"
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                When I ask for the missing values counts in the fields
                Then the missing values counts dict is "<missing_values>"

                Examples:
                | data                     | time_1  | params                                          | time_2 |missing_values       |
                | ../data/iris_missing.csv | 30      | {"fields": {"000000": {"optype": "numeric"}}}   |30      |{"000000": 1}      |
        """
        print self.test_scenario1.__doc__
        examples = [
            ['data/iris_missing.csv', '30', '{"fields": {"000000": {"optype": "numeric"}}}', '30', '{"000000": 1}']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            source_create.i_update_source_with(self, example[2])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self,
                                                                example[3])
            dataset_read.i_get_the_missing_values(self)
            dataset_read.i_get_the_properties_values(
                self, 'missing values count', example[4])

    def test_scenario2(self):
        """
            Scenario: Successfully obtaining parsing error counts:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I update the source with params "<params>"
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                When I ask for the error counts in the fields
                Then the error counts dict is "<error_values>"

                Examples:
                | data                     | time_1  | params                                          | time_2 |error_values       |
                | ../data/iris_missing.csv | 30      | {"fields": {"000000": {"optype": "numeric"}}}   |30      |{"000000": 1}      |
        """
        print self.test_scenario2.__doc__
        examples = [
            ['data/iris_missing.csv', '30', '{"fields": {"000000": {"optype": "numeric"}}}', '30', '{"000000": 1}']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            source_create.i_update_source_with(self, example[2])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self,
                                                                example[3])
            dataset_read.i_get_the_errors_values(self)
            dataset_read.i_get_the_properties_values(
                self, 'error counts', example[4])
