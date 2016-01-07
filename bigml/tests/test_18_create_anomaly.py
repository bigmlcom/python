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


""" Creating anomaly detector

"""
from world import world, setup_module, teardown_module
import create_source_steps as source_create
import create_dataset_steps as dataset_create
import create_anomaly_steps as anomaly_create
import create_multimodel_steps as mm_create

class TestAnomaly(object):

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

            Scenario: Successfully creating an anomaly detector from a dataset and a dataset list:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                Then I create an anomaly detector from a dataset
                And I wait until the anomaly detector is ready less than <time_4> secs
                And I check the anomaly detector stems from the original dataset
                And I store the dataset id in a list
                And I create a dataset
                And I wait until the dataset is ready less than <time_3> secs
                And I store the dataset id in a list
                Then I create an anomaly detector from a dataset list
                And I wait until the anomaly detector is ready less than <time_4> secs
                And I check the anomaly detector stems from the original dataset list

                Examples:
                | data                 | time_1  | time_2 | time_3 |  time_4 |
                | ../data/tiny_kdd.csv | 40      | 40     | 80     |  100
        """
        print self.test_scenario1.__doc__
        examples = [
            ['data/tiny_kdd.csv', '40', '40', '40', '100']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self,
                                                                example[2])
            anomaly_create.i_create_an_anomaly_from_dataset(self)
            anomaly_create.the_anomaly_is_finished_in_less_than(self,
                                                                example[4])
            anomaly_create.i_check_anomaly_dataset_and_datasets_ids(self)
            mm_create.i_store_dataset_id(self)
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self,
                                                                example[3])
            mm_create.i_store_dataset_id(self)
            anomaly_create.i_create_an_anomaly_from_dataset_list(self)
            anomaly_create.the_anomaly_is_finished_in_less_than(self,
                                                                example[4])
            anomaly_create.i_check_anomaly_datasets_and_datasets_ids(self)

    def test_scenario2(self):
        """

            Scenario: Successfully creating an anomaly detector from a dataset and generating the anomalous dataset:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                Then I create an anomaly detector of <rows> anomalies from a dataset
                And I wait until the anomaly detector is ready less than <time_4> secs
                And I create a dataset with only the anomalies
                And I wait until the dataset is ready less than <time_3> secs
                And I check that the dataset has <rows> rows

                Examples:
                | data                       | time_1  | time_2 | time_3 |time_4|  rows|
                | ../data/iris_anomalous.csv | 40      | 40     | 80     | 40   |  1
        """
        print self.test_scenario2.__doc__
        examples = [
            ['data/iris_anomalous.csv', '40', '40', '80', '40', '1']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self,
                                                                example[2])
            anomaly_create.i_create_an_anomaly_with_top_n_from_dataset(
                self, example[5])
            anomaly_create.the_anomaly_is_finished_in_less_than(self,
                                                                example[3])
            anomaly_create.create_dataset_with_anomalies(self)
            dataset_create.the_dataset_is_finished_in_less_than(self,
                                                                example[4])
            anomaly_create.the_dataset_has_n_rows(self, example[5])
