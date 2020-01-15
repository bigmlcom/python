# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2018-2020 BigML
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
from world import world, setup_module, teardown_module
import create_source_steps as source_create
import create_dataset_steps as dataset_create

class TestMultiDataset(object):

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
            Scenario: Successfully creating a sampled multi-dataset:
                Given I create a data source with "<params>" uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a multi-dataset with sample rates <rates>
                And I wait until the multi-dataset is ready less than <time_3> secs
                When I compare the datasets' instances
                Then the proportion of instances between datasets is <rate>

                Examples:
                | data                | time_1  | time_2 | time_3 | rate |rates
                | ../data/iris.csv | 10      | 10     | 10     | 0.5 |[0.2, 0.3]
        """
        print self.test_scenario1.__doc__
        examples = [
            ['data/iris.csv', '10', '10', '10', '0.5', '[0.2, 0.3]']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file_with_args(self, example[0], '{}')
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self,
                                                                example[2])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self,
                                                                example[2])
            dataset_create.i_create_a_multidataset(self, example[5])
            dataset_create.the_dataset_is_finished_in_less_than(self,
                                                                example[3])
            dataset_create.i_compare_datasets_instances(self)
            dataset_create.proportion_datasets_instances(self, example[4])


    def test_scenario2(self):
        """
            Scenario: Successfully creating a single dataset multi-dataset:
                Given I create a data source with "<params>" uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a multi-dataset with sample rates <rates>
                And I wait until the multi-dataset is ready less than <time_3> secs
                When I compare the datasets' instances
                Then the proportion of instances between datasets is <rate>

                Examples:
                | data                | time_1  | time_2 | time_3 | rate |rates
                | ../data/iris.csv | 10      | 10     | 10     | 0.2 |[0.2]
        """
        print self.test_scenario2.__doc__
        examples = [
            ['data/iris.csv', '10', '10', '10', '0.2', '[0.2]']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file_with_args(self, example[0], '{}')
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self,
                                                                example[2])
            dataset_create.i_create_a_multidataset(self, example[5])
            dataset_create.the_dataset_is_finished_in_less_than(self,
                                                                example[3])
            dataset_create.i_compare_datasets_instances(self)
            dataset_create.proportion_datasets_instances(self, example[4])

    def test_scenario3(self):
        """
            Scenario: Successfully creating a sampled multi-dataset with sample:
                Given I create a data source with "<params>" uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a multi-dataset with same dataset and the first sample rate <rates>
                And I wait until the multi-dataset is ready less than <time_3> secs
                When I compare the datasets' instances
                Then the proportion of instances between datasets is <rate>

                Examples:
                | data                | time_1  | time_2 | time_3 | rate |rates
                | ../data/iris.csv | 10      | 10     | 10     | 1.3 |[1, 0.3]
        """
        print self.test_scenario1.__doc__
        examples = [
            ['data/iris.csv', '10', '10', '10', '1.3', '[1, 0.3]']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file_with_args(self, example[0], '{}')
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self,
                                                                example[2])
            dataset_create.i_create_a_multidataset_mixed_format(self, example[5])
            dataset_create.the_dataset_is_finished_in_less_than(self,
                                                                example[3])
            dataset_create.i_compare_datasets_instances(self)
            dataset_create.proportion_datasets_instances(self, example[4])
