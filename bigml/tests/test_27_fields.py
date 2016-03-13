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


""" Testing Fields object properties

"""
from world import world, setup_module, teardown_module
import fields_steps
import create_source_steps as source_create
import create_dataset_steps as dataset_create


class TestFields(object):

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
            Scenario: Successfully creating a Fields object:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a Fields object from the source with objective column "<objective_column>"
                Then the object id is "<objective_id>"

                Examples:
                | data                | time_1  | objective_column | objective_id |
                | ../data/iris.csv | 10      | 0 | 000000 |
        """
        print self.test_scenario1.__doc__
        examples = [
            ['data/iris.csv', '10', '0', '000000']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            fields_steps.create_fields(self, example[2])
            fields_steps.check_objective(self, example[3])

    def test_scenario2(self):
        """
            Scenario: Successfully creating a Fields object and a summary fields file:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a Fields object from the dataset with objective column "<objective_column>"
                And I export a summary fields file "<summary_file>"
                Then I check that the file "<summary_file>" is like "<expected_file>"

                Examples:
                | data                | time_1  | objective_column | summary_file| expected_file | time_2
                | ../data/iris.csv | 10      | 0 | fields_summary.csv | data/fields/fields_summary.csv | 10
        """
        print self.test_scenario2.__doc__
        examples = [
            ['data/iris.csv', '10', '0', 'fields_summary.csv', 'data/fields/fields_summary.csv', '10']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[5])
            fields_steps.create_fields_from_dataset(self, example[2])
            fields_steps.generate_summary(self, example[3])
            fields_steps.check_summary_like_expected(self, example[3], example[4])

    def test_scenario3(self):
        """
            Scenario: Successfully creating a Fields object and a modified fields structure from a file:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a Fields object from the dataset with objective column "<objective_column>"
                And I import a summary fields file "<summary_file>" as a fields structure
                Then I check the new field structure has field "<field_id>" as "<optype>"

                Examples:
                | data                | time_1  | objective_column | summary_file| field_id | optype | time_2
                | ../data/iris.csv | 10      | 0 | fields_summary_modified.csv | 000000 | categorical | 10
        """
        print self.test_scenario3.__doc__
        examples = [
            ['data/iris.csv', '10', '0', 'data/fields/fields_summary_modified.csv', '000000', 'categorical', '10']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[6])
            fields_steps.create_fields_from_dataset(self, example[2])
            fields_steps.import_summary_file(self, example[3])
            fields_steps.check_field_type(self, example[4], example[5])
