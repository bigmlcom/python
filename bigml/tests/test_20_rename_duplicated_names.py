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


""" Renaming duplicated names in fields

"""
from world import world, setup_module, teardown_module
import create_source_steps as source_create
import create_dataset_steps as dataset_create
import create_model_steps as model_create
import compare_predictions_steps as compare_preds

class TestDuplicatedFields(object):

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
            Scenario: Successfully changing duplicated field names:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset with "<options>"
                And I wait until the dataset is ready less than <time_2> secs
                And I create a model
                And I wait until the model is ready less than <time_3> secs
                And I create a local model
                Then "<field_id>" field's name is changed to "<new_name>"

        Examples:
                | data             | time_1  | time_2 | time_3 | options | field_id | new_name
                | ../data/iris.csv | 20      | 20     | 30     | {"fields": {"000001": {"name": "species"}}} | 000001 | species1
                | ../data/iris.csv | 20      | 20     | 30     | {"fields": {"000001": {"name": "petal width"}}} | 000001 | petal width1
        """
        print self.test_scenario1.__doc__
        examples = [
            ['data/iris.csv', '20', '20', '30', '{"fields": {"000001": {"name": "species"}}}', '000001', 'species1'],
            ['data/iris.csv', '20', '20', '30', '{"fields": {"000001": {"name": "petal width"}}}', '000003', 'petal width3']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset_with(self, example[4])
            dataset_create.the_dataset_is_finished_in_less_than(self,
                                                                example[3])
            model_create.i_create_a_model(self)
            model_create.the_model_is_finished_in_less_than(self, example[3])
            compare_preds.i_create_a_local_model(self)
            model_create.field_name_to_new_name(self, example[5],  example[6])
