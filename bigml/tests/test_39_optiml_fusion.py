# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2018 BigML
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


""" Creating optimls and fusions

"""
from world import world, setup_module, teardown_module
import create_model_steps as model_create
import create_source_steps as source_create
import create_dataset_steps as dataset_create
import compare_predictions_steps as compare_pred
import create_prediction_steps as prediction_create
import create_evaluation_steps as evaluation_create


class TestOptimlFusion(object):

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
            Scenario 1: Successfully creating an optiml from a dataset:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create an optiml from a dataset
                And I wait until the optiml is ready less than <time_3> secs
                And I update the optiml name to "<optiml_name>"
                When I wait until the optiml is ready less than <time_4> secs
                Then the optiml name is "<optiml_name>"

                Examples:
                | data                | time_1  | time_2 | time_3 | time_4 | optiml_name |
                | ../data/iris.csv | 10      | 10     | 2000     | 20 | my new optiml name |
        """
        print self.test_scenario1.__doc__
        examples = [
            ['data/iris.csv', '10', '10', '10000', '20', 'my new optiml name']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_an_optiml_with_objective_and_params( \
                self, parms='{"max_training_time": %s, "model_types": '
                            '["model", "logisticregression"]}' % \
                    (int(float(example[3])/1000) - 1))
            model_create.the_optiml_is_finished_in_less_than(self, example[3])
            model_create.i_update_optiml_name(self, example[5])
            model_create.the_optiml_is_finished_in_less_than(self, example[4])
            model_create.i_check_optiml_name(self, example[5])

    def test_scenario2(self):
        """
            Scenario 2: Successfully creating a fusion from a dataset:
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
                And I create a fusion from a dataset
                And I wait until the fusion is ready less than <time_4> secs
                And I update the fusion name to "<fusion_name>"
                When I wait until the fusion is ready less than <time_5> secs
                And I create a prediction for "<data_input>"
                Then the fusion name is "<fusion_name>"
                And the prediction for "<objective>" is "<prediction>"
                And I create an evaluation for the fusion with the dataset
                And I wait until the evaluation is ready less than <time_4> secs
                Then the measured "<measure>" is <value>

                Examples:
                | data                | time_1  | time_2 | time_3 | time_4 | fusion_name | data_input | objective | prediction
                | ../data/iris.csv | 10      | 10     | 20     | 20 | my new fusion name | {"petal length": 1, "petal width": 1} | "000004" | "Iris-setosa"
        """
        print self.test_scenario2.__doc__
        examples = [
            ['data/iris.csv', '10', '10', '20', '20', 'my new fusion name',
             '{"tags":["mytag"]}', 'mytag',
             '{"petal width": 1.75, "petal length": 2.45}', "000004",
             "Iris-setosa", 'average_phi', '1.0']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_model_with(self, example[6])
            model_create.the_model_is_finished_in_less_than(self, example[3])
            model_create.i_create_a_model_with(self, example[6])
            model_create.the_model_is_finished_in_less_than(self, example[3])
            model_create.i_create_a_model_with(self, example[6])
            model_create.the_model_is_finished_in_less_than(self, example[3])
            compare_pred.i_retrieve_a_list_of_remote_models(self, example[7])
            model_create.i_create_a_fusion(self)
            model_create.the_fusion_is_finished_in_less_than(self, example[3])
            model_create.i_update_fusion_name(self, example[5])
            model_create.the_fusion_is_finished_in_less_than(self, example[4])
            model_create.i_check_fusion_name(self, example[5])
            prediction_create.i_create_a_fusion_prediction(self, example[8])
            prediction_create.the_prediction_is(self, example[9], example[10])
            evaluation_create.i_create_an_evaluation_fusion(self)
            evaluation_create.the_evaluation_is_finished_in_less_than(self, example[3])
            evaluation_create.the_measured_measure_is_value(self, example[11], example[12])
