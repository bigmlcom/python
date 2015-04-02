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


""" Testing prediction creation

"""
from world import world, setup_module, teardown_module
import create_source_steps as source_create
import create_dataset_steps as dataset_create
import create_model_steps as model_create
import create_prediction_steps as prediction_create


class Test_prediction(object):

    def test_scenario1(self):
        """
            Scenario: Successfully creating a prediction:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a model
                And I wait until the model is ready less than <time_3> secs
                When I create a prediction for "<data_input>"
                Then the prediction for "<objective>" is "<prediction>"

                Examples:
                | data                | time_1  | time_2 | time_3 | data_input    | objective | prediction  |
                | ../data/iris.csv | 10      | 10     | 10     | {"petal width": 0.5} | 000004    | Iris-setosa |
                | ../data/iris_sp_chars.csv | 10      | 10     | 10     | {"pétal&width\u0000": 0.5} | 000004    | Iris-setosa |

        """

        examples = [
            ['data/iris.csv', '10', '10', '10', '{"petal width": 0.5}', '000004', 'Iris-setosa'],
            ['data/iris_sp_chars.csv', '10', '10', '10', '{"pétal&width\u0000": 0.5}', '000004', 'Iris-setosa']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_model(self)
            model_create.the_model_is_finished_in_less_than(self, example[3])
            prediction_create.i_create_a_prediction(self, example[4])
            prediction_create.the_prediction_is(self, example[5], example[6])

    def test_scenario2(self):
        """
            Scenario: Successfully creating a prediction from a source in a remote location

                Given I create a data source using the url "<url>"
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a model
                And I wait until the model is ready less than <time_3> secs
                When I create a prediction for "<data_input>"
                Then the prediction for "<objective>" is "<prediction>"

                Examples:
                | url                | time_1  | time_2 | time_3 | data_input    | objective | prediction  |
                | s3://bigml-public/csv/iris.csv | 10      | 10     | 10     | {"petal width": 0.5} | 000004    | Iris-setosa |
        """
        examples = [
            ['s3://bigml-public/csv/iris.csv', '10', '10', '10', '{"petal width": 0.5}', '000004', 'Iris-setosa']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_create_using_url(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_model(self)
            model_create.the_model_is_finished_in_less_than(self, example[3])
            prediction_create.i_create_a_prediction(self, example[4])
            prediction_create.the_prediction_is(self, example[5], example[6])

