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


""" Creating Multimodel batch predictions

"""
from world import world, setup_module, teardown_module
import create_source_steps as source_create
import create_dataset_steps as dataset_create
import create_model_steps as model_create
import compare_predictions_steps as compare_pred

class TestMultimodelBatchPrediction(object):

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
            Scenario: Successfully creating a batch prediction from a multi model:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a model with "<params>"
                And I wait until the model is ready less than <time_3> secs
                And I create a model with "<params>"
                And I wait until the model is ready less than <time_3> secs
                And I create a model with "<params>"
                And I wait until the model is ready less than <time_3> secs
                And I retrieve a list of remote models tagged with "<tag>"
                And I create a local multi model
                When I create a batch prediction for "<data_input>" and save it in "<path>"
                And I combine the votes in "<path>"
                Then the plurality combined predictions are "<predictions>"
                And the confidence weighted predictions are "<predictions>"

                Examples:
                | data             | time_1  | time_2 | time_3 | params                         |  tag  |  data_input    | path | predictions  |
                | ../data/iris.csv | 10      | 10     | 10     | {"tags":["mytag"]} | mytag |  [{"petal width": 0.5}, {"petal length": 6, "petal width": 2}, {"petal length": 4, "petal width": 1.5}]  | ./tmp | ["Iris-setosa", "Iris-virginica", "Iris-versicolor"] |

        """
        print self.test_scenario1.__doc__
        examples = [
            ['data/iris.csv', '10', '10', '10', '{"tags":["mytag"]}', 'mytag', '[{"petal width": 0.5}, {"petal length": 6, "petal width": 2}, {"petal length": 4, "petal width": 1.5}]', './tmp', '["Iris-setosa", "Iris-virginica", "Iris-versicolor"]']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_model_with(self, example[4])
            model_create.the_model_is_finished_in_less_than(self, example[3])
            model_create.i_create_a_model_with(self, example[4])
            model_create.the_model_is_finished_in_less_than(self, example[3])
            model_create.i_create_a_model_with(self, example[4])
            model_create.the_model_is_finished_in_less_than(self, example[3])
            compare_pred.i_retrieve_a_list_of_remote_models(self, example[5])
            compare_pred.i_create_a_local_multi_model(self)
            compare_pred.i_create_a_batch_prediction(self, example[6], example[7])
            compare_pred.i_combine_the_votes(self, example[7])
            compare_pred.the_plurality_combined_prediction(self, example[8])
            compare_pred.the_confidence_weighted_prediction(self, example[8])
