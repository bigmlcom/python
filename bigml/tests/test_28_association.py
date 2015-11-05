# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015 BigML
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


""" Creating association

"""
from world import world, setup_module, teardown_module
import create_source_steps as source_create
import create_dataset_steps as dataset_create
import create_association_steps as association_create

class TestAssociation(object):

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
            Scenario: Successfully creating associations from a dataset:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create associations from a dataset
                And I wait until the association is ready less than <time_3> secs
                And I update the association name to "<association_name>"
                When I wait until the association is ready less than <time_4> secs
                Then the association name is "<association_name>"

                Examples:
                | data                | time_1  | time_2 | time_3 | time_4 | association_name |
                | ../data/iris.csv | 10      | 10     | 20     | 20 | my new association name |
        """
        print self.test_scenario1.__doc__
        examples = [
            ['data/iris.csv', '10', '10', '20', '20', 'my new association name']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            association_create.i_create_an_association_from_dataset(self)
            association_create.the_association_is_finished_in_less_than(self, example[3])
            association_create.i_update_association_name(self, example[5])
            association_create.the_association_is_finished_in_less_than(self, example[4])
            association_create.i_check_association_name(self, example[5])

    def test_scenario2(self):
        """
            Scenario: Successfully creating local association object:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create an association from a dataset
                And I wait until the association is ready less than <time_3> secs
                And I create a local association
                When I get the rules for <"item_list">
                Then the first rule is "<JSON_rule>"

                Examples:
                | data             | time_1  | time_2 | time_3 | item_list                              | JSON_rule  |
                | ../data/tiny_mushrooms.csv | 10      | 20     | 20     | ["Edible"]                   | {'p_value': 1.99981e-26, 'confidence': 1, 'rhs_cover': 122, 'leverage': 0.24986, 'rhs': [19], 'lift': 2.04918, 'lhs': [0, 21, 12, 7], 'lhs_cover': 122, 'support': 122} |


        """
        print self.test_scenario2.__doc__
        examples = [
            ['data/tiny_mushrooms.csv', '10', '20', '20', ["Edible"], {'p_value': 1.99981e-26, 'confidence': 1, 'rhs_cover': 122, 'leverage': 0.24986, 'rhs': [19], 'lift': 2.04918, 'lhs': [0, 21, 12, 7], 'lhs_cover': 122, 'support': 122}]]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            association_create.i_create_an_association_from_dataset(self)
            association_create.the_association_is_finished_in_less_than(self, example[3])
            association_create.i_create_a_local_association(self)
            association_create.i_get_rules_for_item_list(self, example[4])
            association_create.the_first_rule_is(self, example[5])
