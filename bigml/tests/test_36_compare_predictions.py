# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2017-2018 BigML
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


""" Comparing remote and local predictions

"""
from world import world, setup_module, teardown_module, show_doc
import create_source_steps as source_create
import create_dataset_steps as dataset_create
import create_model_steps as model_create
import create_ensemble_steps as ensemble_create
import create_prediction_steps as prediction_create
import compare_predictions_steps as prediction_compare


class TestComparePrediction(object):

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
            Scenario: Successfully comparing predictions for deepnets:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a deepnet with objective "<objective>" and "<params>"
                And I wait until the deepnet is ready less than <time_3> secs
                And I create a local deepnet
                When I create a prediction for "<data_input>"
                Then the prediction for "<objective>" is "<prediction>"
                And I create a local prediction for "<data_input>"
                Then the local prediction is "<prediction>"

                Examples:
                | data             | time_1  | time_2 | time_3 | data_input                             | objective | prediction  | params,


        """
        examples = [
            ['data/iris.csv', '10', '50', '30000', '{"petal width": 4}', '000004', 'Iris-virginica', '{}'],
            ['data/iris.csv', '10', '50', '30000', '{"sepal length": 4.1, "sepal width": 2.4}', '000004', 'Iris-setosa', '{}'],
            ['data/iris_missing2.csv', '10', '50', '30000', '{}', '000004', 'Iris-setosa', '{}'],
            ['data/spam.csv', '10', '50', '30000', '{}', '000000', 'ham', '{}']]
        show_doc(self.test_scenario1, examples)

        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_deepnet_with_objective_and_params(self, example[5], example[7])
            model_create.the_deepnet_is_finished_in_less_than(self, example[3])
            prediction_compare.i_create_a_local_deepnet(self)
            prediction_create.i_create_a_deepnet_prediction(self, example[4])
            prediction_create.the_prediction_is(self, example[5], example[6])
            prediction_compare.i_create_a_local_deepnet_prediction(self, example[4])
            prediction_compare.the_local_prediction_is(self, example[6])


    def test_scenario2(self):
        """
            Scenario: Successfully comparing predictions in operating points for models:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a model
                And I wait until the model is ready less than <time_3> secs
                And I create a local model
                When I create a prediction for "<data_input>" in "<operating_point>"
                Then the prediction for "<objective>" is "<prediction>"
                And I create a local prediction for "<data_input>" in "<operating_point>"
                Then the local prediction is "<prediction>"

                Examples:
                | data             | time_1  | time_2 | time_3 | data_input                             | prediction  | operating_point


        """
        examples = [
            ['data/iris.csv', '10', '50', '50', '{"petal width": 4}', 'Iris-setosa',  {"kind": "probability", "threshold": 0.1, "positive_class": "Iris-setosa"}, "000004"],
            ['data/iris.csv', '10', '50', '50', '{"petal width": 4}', 'Iris-versicolor', {"kind": "probability", "threshold": 0.9, "positive_class": "Iris-setosa"}, "000004"],
            ['data/iris.csv', '10', '50', '50', '{"sepal length": 4.1, "sepal width": 2.4}',  'Iris-setosa', {"kind": "confidence", "threshold": 0.1, "positive_class": "Iris-setosa"}, "000004"],
            ['data/iris.csv', '10', '50', '50', '{"sepal length": 4.1, "sepal width": 2.4}', 'Iris-versicolor',  {"kind": "confidence", "threshold": 0.9, "positive_class": "Iris-setosa"}, "000004"]]
        show_doc(self.test_scenario2, examples)

        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_model(self)
            model_create.the_model_is_finished_in_less_than(self, example[3])
            prediction_compare.i_create_a_local_model(self)
            prediction_create.i_create_a_prediction_op(self, example[4], example[6])
            prediction_create.the_prediction_is(self, example[7], example[5])
            prediction_compare.i_create_a_local_prediction_op(self, example[4], example[6])
            prediction_compare.the_local_prediction_is(self, example[5])


    def test_scenario3(self):
        """
            Scenario: Successfully comparing predictions for deepnets with operating point:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a deepnet with objective "<objective>" and "<params>"
                And I wait until the deepnet is ready less than <time_3> secs
                And I create a local deepnet
                When I create a prediction with operating point "<operating_point>" for "<data_input>"
                Then the prediction for "<objective>" is "<prediction>"
                And I create a local prediction with operating point "<operating_point>" for "<data_input>"
                Then the local prediction is "<prediction>"

                Examples:
                | data             | time_1  | time_2 | time_3 | data_input                             | objective | prediction  | params | operating_point,


        """
        examples = [
            ['data/iris.csv', '10', '50', '30000', '{"petal width": 4}', '000004', 'Iris-versicolor', '{}', {"kind": "probability", "threshold": 1, "positive_class": "Iris-virginica"}]]
        show_doc(self.test_scenario3, examples)

        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_deepnet_with_objective_and_params(self, example[5], example[7])
            model_create.the_deepnet_is_finished_in_less_than(self, example[3])
            prediction_compare.i_create_a_local_deepnet(self)
            prediction_create.i_create_a_deepnet_prediction_with_op(self, example[4], example[8])
            prediction_create.the_prediction_is(self, example[5], example[6])
            prediction_compare.i_create_a_local_deepnet_prediction_with_op(self, example[4], example[8])
            prediction_compare.the_local_prediction_is(self, example[6])


    def test_scenario4(self):
        """
            Scenario: Successfully comparing predictions in operating points for ensembles:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create an ensemble
                And I wait until the ensemble is ready less than <time_3> secs
                And I create a local ensemble
                When I create a prediction for "<data_input>" in "<operating_point>"
                Then the prediction for "<objective>" is "<prediction>"
                And I create a local ensemble prediction for "<data_input>" in "<operating_point>"
                Then the local ensemble prediction is "<prediction>"

                Examples:
                | data             | time_1  | time_2 | time_3 | data_input                             | prediction  | operating_point


        """
        examples = [
            ['data/iris.csv', '10', '50', '50', '{"petal width": 4}', 'Iris-setosa',  {"kind": "probability", "threshold": 0.1, "positive_class": "Iris-setosa"}, "000004"],
            ['data/iris.csv', '10', '50', '50', '{"petal width": 4}', 'Iris-virginica', {"kind": "probability", "threshold": 0.9, "positive_class": "Iris-setosa"}, "000004"],
            ['data/iris.csv', '10', '50', '50', '{"sepal length": 4.1, "sepal width": 2.4}',  'Iris-setosa', {"kind": "confidence", "threshold": 0.1, "positive_class": "Iris-setosa"}, "000004"],
            ['data/iris.csv', '10', '50', '50', '{"sepal length": 4.1, "sepal width": 2.4}', 'Iris-versicolor',  {"kind": "confidence", "threshold": 0.9, "positive_class": "Iris-setosa"}, "000004"]]
        show_doc(self.test_scenario4, examples)

        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            ensemble_create.i_create_an_ensemble(self)
            ensemble_create.the_ensemble_is_finished_in_less_than(self, example[3])
            ensemble_create.create_local_ensemble(self)
            prediction_create.i_create_an_ensemble_prediction_op(self, example[4], example[6])
            prediction_create.the_prediction_is(self, example[7], example[5])
            prediction_compare.i_create_a_local_ensemble_prediction_op(self, example[4], example[6])
            prediction_compare.the_local_prediction_is(self, example[5])
