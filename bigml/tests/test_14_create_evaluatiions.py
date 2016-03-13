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


""" Creating evaluation

"""
from world import world, setup_module, teardown_module
import create_source_steps as source_create
import create_dataset_steps as dataset_create
import create_model_steps as model_create
import create_ensemble_steps as ensemble_create
import create_evaluation_steps as evaluation_create

class TestEvaluation(object):

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
            Scenario: Successfully creating an evaluation:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a model
                And I wait until the model is ready less than <time_3> secs
                When I create an evaluation for the model with the dataset
                And I wait until the evaluation is ready less than <time_4> secs
                Then the measured "<measure>" is <value>

                Examples:
                | data             | time_1  | time_2 | time_3 | time_4 | measure       | value  |
                | ../data/iris.csv | 30      | 30     | 30     | 30     | average_phi   | 1      |
        """
        print self.test_scenario1.__doc__
        examples = [
            ['data/iris.csv', '50', '50', '50', '50', 'average_phi', '1']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_model(self)
            model_create.the_model_is_finished_in_less_than(self, example[3])
            evaluation_create.i_create_an_evaluation(self)
            evaluation_create.the_evaluation_is_finished_in_less_than(self, example[4])
            evaluation_create.the_measured_measure_is_value(self, example[5], example[6])

    def test_scenario2(self):
        """

            Scenario: Successfully creating an evaluation for an ensemble:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create an ensemble of <number_of_models> models and <tlp> tlp
                And I wait until the ensemble is ready less than <time_3> secs
                When I create an evaluation for the ensemble with the dataset
                And I wait until the evaluation is ready less than <time_4> secs
                Then the measured "<measure>" is <value>

                Examples:
                | data             | time_1  | time_2 | number_of_models | tlp | time_3 | time_4 | measure       | value  |
                | ../data/iris.csv | 30      | 30     | 5                | 1   | 50     | 30     | average_phi   | 0.98029   |
        """
        print self.test_scenario2.__doc__
        examples = [
            ['data/iris.csv', '50', '50', '5', '1', '80', '80', 'average_phi', '0.98029']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            ensemble_create.i_create_an_ensemble(self, example[3], example[4])
            ensemble_create.the_ensemble_is_finished_in_less_than(self, example[5])
            evaluation_create.i_create_an_evaluation_ensemble(self)
            evaluation_create.the_evaluation_is_finished_in_less_than(self, example[6])
            evaluation_create.the_measured_measure_is_value(self, example[7], example[8])
