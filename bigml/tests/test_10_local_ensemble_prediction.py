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


""" Creating local ensemble predictions

"""
from world import world, setup_module, teardown_module
import create_source_steps as source_create
import create_dataset_steps as dataset_create
import create_model_steps as model_create
import create_ensemble_steps as ensemble_create
import create_prediction_steps as prediction_create
import compare_predictions_steps as compare_pred

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
            Scenario: Successfully creating a local prediction from an Ensemble:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create an ensemble of <number_of_models> models and <tlp> tlp
                And I wait until the ensemble is ready less than <time_3> secs
                And I create a local Ensemble
                When I create a local ensemble prediction with confidence for "<data_input>"
                Then the local prediction is "<prediction>"
                And the local prediction's confidence is "<confidence>"

                Examples:
                | data             | time_1  | time_2 | time_3 | number_of_models | tlp   |  data_input    |prediction  | confidence
                | ../data/iris.csv | 10      | 10     | 50     | 5                | 1     | {"petal width": 0.5} | Iris-versicolor | 0.3687
        """
        print self.test_scenario1.__doc__
        examples = [
            ['data/iris.csv', '10', '10', '50', '5', '1', '{"petal width": 0.5}', 'Iris-versicolor', '0.3687']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            ensemble_create.i_create_an_ensemble(self, example[4], example[5])
            ensemble_create.the_ensemble_is_finished_in_less_than(self, example[3])
            ensemble_create.create_local_ensemble(self)
            prediction_create.create_local_ensemble_prediction_with_confidence(self, example[6])
            compare_pred.the_local_prediction_is(self, example[7])
            compare_pred.the_local_prediction_confidence_is(self, example[8])

    def test_scenario2(self):
        """

            Scenario: Successfully obtaining field importance from an Ensemble:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a model with "<parms1>"
                And I wait until the model is ready less than <time_3> secs
                And I create a model with "<parms2>"
                And I wait until the model is ready less than <time_4> secs
                And I create a model with "<parms3>"
                And I wait until the model is ready less than <time_5> secs
                When I create a local Ensemble with the last <number_of_models> models
                Then the field importance text is <field_importance>

                Examples:
                | data             | time_1  | time_2 |parms1 | time_3 |parms2 | time_4 |parms3| time_5 |number_of_models |field_importance
                | ../data/iris.csv | 10      | 10     |{"input_fields": ["000000", "000001","000003", "000004"]} |20      |{"input_fields": ["000000", "000001","000002", "000004"]} | 20     |{"input_fields": ["000000", "000001","000002", "000003", "000004"]} | 20   | 3 |[["000002", 0.5269933333333333], ["000003", 0.38936], ["000000", 0.04662333333333333], ["000001", 0.037026666666666666]]
        """
        print self.test_scenario2.__doc__
        examples = [
            ['data/iris.csv', '10', '10', '{"input_fields": ["000000", "000001","000003", "000004"]}', '20', '{"input_fields": ["000000", "000001","000002", "000004"]}', '20', '{"input_fields": ["000000", "000001","000002", "000003", "000004"]}', '20', '3', '[["000002", 0.5269933333333333], ["000003", 0.38936], ["000000", 0.04662333333333333], ["000001", 0.037026666666666666]]']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_model_with(self, example[3])
            model_create.the_model_is_finished_in_less_than(self, example[4])
            model_create.i_create_a_model_with(self, example[5])
            model_create.the_model_is_finished_in_less_than(self, example[6])
            model_create.i_create_a_model_with(self, example[7])
            model_create.the_model_is_finished_in_less_than(self, example[8])
            ensemble_create.create_local_ensemble_with_list(self, example[9])
            ensemble_create.field_importance_print(self, example[10])

    def test_scenario3(self):
        """

            Scenario: Successfully creating a local prediction from an Ensemble adding confidence:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create an ensemble of <number_of_models> models and <tlp> tlp
                And I wait until the ensemble is ready less than <time_3> secs
                And I create a local Ensemble
                When I create a local ensemble prediction for "<data_input>" in JSON adding confidence
                Then the local prediction is "<prediction>"
                And the local prediction's confidence is "<confidence>"

                Examples:
                | data             | time_1  | time_2 | time_3 | number_of_models | tlp   |  data_input    |prediction  | confidence
                | ../data/iris.csv | 10      | 10     | 50     | 5                | 1     | {"petal width": 0.5} | Iris-versicolor | 0.3687
        """
        print self.test_scenario3.__doc__
        examples = [
            ['data/iris.csv', '10', '10', '50', '5', '1', '{"petal width": 0.5}', 'Iris-versicolor', '0.3687']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            ensemble_create.i_create_an_ensemble(self, example[4], example[5])
            ensemble_create.the_ensemble_is_finished_in_less_than(self, example[3])
            ensemble_create.create_local_ensemble(self)
            prediction_create.create_local_ensemble_prediction_add_confidence(self, example[6])
            compare_pred.the_local_prediction_is(self, example[7])
            compare_pred.the_local_prediction_confidence_is(self, example[8])

    def test_scenario4(self):
        """
            Scenario: Successfully obtaining field importance from an Ensemble created from local models:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a model with "<parms1>"
                And I wait until the model is ready less than <time_3> secs
                And I create a model with "<parms2>"
                And I wait until the model is ready less than <time_4> secs
                And I create a model with "<parms3>"
                And I wait until the model is ready less than <time_5> secs
                When I create a local Ensemble with the last <number_of_models> local models
                Then the field importance text is <field_importance>

                Examples:
                | data             | time_1  | time_2 |parms1 | time_3 |parms2 | time_4 |parms3| time_5 |number_of_models |field_importance
                | ../data/iris.csv | 10      | 10     |{"input_fields": ["000000", "000001","000003", "000004"]} |20      |{"input_fields": ["000000", "000001","000002", "000004"]} | 20     |{"input_fields": ["000000", "000001","000002", "000003", "000004"]} | 20   | 3 |[["000002", 0.5269933333333333], ["000003", 0.38936], ["000000", 0.04662333333333333], ["000001", 0.037026666666666666]]
        """
        print self.test_scenario4.__doc__
        examples = [
            ['data/iris.csv', '10', '10', '{"input_fields": ["000000", "000001","000003", "000004"]}', '20', '{"input_fields": ["000000", "000001","000002", "000004"]}', '20', '{"input_fields": ["000000", "000001","000002", "000003", "000004"]}', '20', '3', '[["000002", 0.5269933333333333], ["000003", 0.38936], ["000000", 0.04662333333333333], ["000001", 0.037026666666666666]]']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_model_with(self, example[3])
            model_create.the_model_is_finished_in_less_than(self, example[4])
            model_create.i_create_a_model_with(self, example[5])
            model_create.the_model_is_finished_in_less_than(self, example[6])
            model_create.i_create_a_model_with(self, example[7])
            model_create.the_model_is_finished_in_less_than(self, example[8])
            ensemble_create.create_local_ensemble_with_list_of_local_models(self, example[9])
            ensemble_create.field_importance_print(self, example[10])

    def test_scenario5(self):
        """
            Scenario: Successfully creating a local prediction from an Ensemble:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create an ensemble of <number_of_models> models and <tlp> tlp
                And I wait until the ensemble is ready less than <time_3> secs
                And I create a local Ensemble
                When I create a local ensemble prediction using median with confidence for "<data_input>"
                Then the local prediction is "<prediction>"

                Examples:
                | data                | time_1  | time_2 | time_3 | number_of_models | tlp   |  data_input    |prediction  |
                | ../data/grades.csv | 10      | 10     | 50     | 2                | 1     | {}             | 67.8816 |
        """
        print self.test_scenario5.__doc__
        examples = [
            ['data/grades.csv', '10', '10', '50', '2', '1', '{}', 67.8816]]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            ensemble_create.i_create_an_ensemble(self, example[4], example[5])
            ensemble_create.the_ensemble_is_finished_in_less_than(self, example[3])
            ensemble_create.create_local_ensemble(self)
            prediction_create.create_local_ensemble_prediction_using_median_with_confidence(self, example[6])
            compare_pred.the_local_prediction_is(self, example[7])
