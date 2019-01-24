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


""" Creating ensembles predictions

"""
from world import world, setup_module, teardown_module
import create_source_steps as source_create
import create_dataset_steps as dataset_create
import create_ensemble_steps as ensemble_create
import create_prediction_steps as prediction_create

class TestEnsemblePrediction(object):

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
            Scenario: Successfully creating a prediction from an ensemble:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create an ensemble of <number_of_models> models and <tlp> tlp
                And I wait until the ensemble is ready less than <time_3> secs
                When I create an ensemble prediction for "<data_input>"
                And I wait until the prediction is ready less than <time_4> secs
                Then the prediction for "<objective>" is "<prediction>"

                Examples:
                | data               | time_1  | time_2 | time_3 | time_4 | number_of_models | tlp   |  data_input    | objective | prediction  |
                | ../data/iris.csv   | 10      | 10     | 50     | 20     | 5                | 1     | {"petal width": 0.5} | 000004    | Iris-versicolor |
                | ../data/iris_sp_chars.csv   | 10      | 10     | 50     | 20     | 5                | 1     | {"pétal&width\u0000": 0.5} | 000004    | Iris-versicolor |
                | ../data/grades.csv | 10      | 10     | 150     | 20     | 10               | 1     | {"Assignment": 81.22, "Tutorial": 91.95, "Midterm": 79.38, "TakeHome": 105.93} | 000005    | 88.205575 |
                | ../data/grades.csv | 10      | 10     | 150     | 20     | 10               | 1     | {"Assignment": 97.33, "Tutorial": 106.74, "Midterm": 76.88, "TakeHome": 108.89} | 000005    | 84.29401 |
        """
        print self.test_scenario1.__doc__
        examples = [
            ['data/iris.csv', '30', '30', '50', '20', '5', '1', '{"petal width": 0.5}', '000004', 'Iris-versicolor'],
            ['data/iris_sp_chars.csv', '30', '30', '50', '20', '5', '1', '{"pétal&width\u0000": 0.5}', '000004', 'Iris-versicolor'],
            ['data/grades.csv', '30', '30', '150', '20', '10', '1', '{"Assignment": 81.22, "Tutorial": 91.95, "Midterm": 79.38, "TakeHome": 105.93}', '000005', '84.556'],
            ['data/grades.csv', '30', '30', '150', '20', '10', '1', '{"Assignment": 97.33, "Tutorial": 106.74, "Midterm": 76.88, "TakeHome": 108.89}', '000005', '73.13558']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            ensemble_create.i_create_an_ensemble(self, example[5], example[6])
            ensemble_create.the_ensemble_is_finished_in_less_than(self, example[3])
            prediction_create.i_create_an_ensemble_prediction(self, example[7])
            prediction_create.the_prediction_is_finished_in_less_than(self, example[4])
            prediction_create.the_prediction_is(self, example[8], example[9])
