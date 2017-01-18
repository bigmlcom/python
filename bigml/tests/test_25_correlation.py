# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015-2017 BigML
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
from world import world, setup_module, teardown_module
import create_source_steps as source_create
import create_dataset_steps as dataset_create
import create_correlation_steps as correlation_create

class TestCorrelation(object):

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
            Scenario: Successfully creating a correlation from a dataset:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a correlation from a dataset
                And I wait until the correlation is ready less than <time_3> secs
                And I update the correlation name to "<correlation_name>"
                When I wait until the correlation is ready less than <time_4> secs
                Then the correlation name is "<correlation_name>"

                Examples:
                | data                | time_1  | time_2 | time_3 | time_4 | correlation_name |
                | ../data/iris.csv | 10      | 10     | 20     | 20 | my new correlation name |
        """
        print self.test_scenario1.__doc__
        examples = [
            ['data/iris.csv', '10', '10', '20', '20', 'my new correlation name']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            correlation_create.i_create_a_correlation_from_dataset(self)
            correlation_create.the_correlation_is_finished_in_less_than(self, example[3])
            correlation_create.i_update_correlation_name(self, example[5])
            correlation_create.the_correlation_is_finished_in_less_than(self, example[4])
            correlation_create.i_check_correlation_name(self, example[5])
