# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015-2019 BigML
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


""" Downloading dataset

"""
from world import world, setup_module, teardown_module
import create_source_steps as source_create
import create_dataset_steps as dataset_create
import create_model_steps as model_create


class TestDownload(object):

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

            Scenario: Successfully exporting a dataset:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I download the dataset file to "<local_file>"
                Then file "<local_file>" is like file "<data>"

                Examples:
                | data             | time_1  | time_2 | local_file |
                | ../data/iris.csv | 30      | 30     | ./tmp/exported_iris.csv |
        """
        print self.test_scenario1.__doc__
        examples = [
            ['data/iris.csv', '30', '30', 'tmp/exported_iris.csv']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            dataset_create.i_export_a_dataset(self, example[3])
            dataset_create.files_equal(self, example[3], example[0])

    def test_scenario2(self):
        """
            Scenario: Successfully creating a model and exporting it:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a model
                And I wait until the model is ready less than <time_3> secs
                And I export the <"pmml"> model to file "<expected_file>"
                Then I check the model is stored in "<expected_file>" file in <"pmml">

                Examples:
                | data                   | time_1  | time_2 | time_3 | expected_file         | pmml
                | data/iris.csv          | 10      | 10     | 10     | tmp/model/iris.json   | false
                | data/iris_sp_chars.csv | 10      | 10     | 10     | tmp/model/iris_sp_chars.pmml   | true

        """
        print self.test_scenario2.__doc__
        examples = [
            ['data/iris.csv', '30', '30', '30', 'tmp/model/iris.json', False],
            ['data/iris_sp_chars.csv', '30', '30', '30', 'tmp/model/iris_sp_chars.pmml', True]]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_model(self)
            model_create.the_model_is_finished_in_less_than(self, example[3])
            model_create.i_export_model(self, example[5], example[4])
            model_create.i_check_model_stored(self, example[4], example[5])
