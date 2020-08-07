# -*- coding: utf-8 -*-
#
# Copyright 2017-2020 BigML
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
from .world import world, setup_module, teardown_module, show_doc
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create
from . import create_model_steps as model_create
from . import create_ensemble_steps as ensemble_create
from . import create_linear_steps as linear_create
from . import create_prediction_steps as prediction_create
from . import compare_predictions_steps as prediction_compare


class TestComparePrediction(object):

    def setup(self):
        """
            Debug information
        """
        print("\n-------------------\nTests in: %s\n" % __name__)

    def teardown(self):
        """
            Debug information
        """
        print("\nEnd of tests in: %s\n-------------------\n" % __name__)

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
            ['data/iris.csv', '30', '50', '60', '{"petal width": 4}', '000004', 'Iris-virginica', '{}'],
            ['data/iris.csv', '30', '50', '60', '{"sepal length": 4.1, "sepal width": 2.4}', '000004', 'Iris-setosa', '{}'],
            ['data/iris_missing2.csv', '30', '50', '60', '{}', '000004', 'Iris-setosa', '{}'],
            ['data/grades.csv', '30', '50', '60', '{}', '000005', 42.15473, '{}'],
            ['data/spam.csv', '30', '50', '60', '{}', '000000', 'ham', '{}']]
        show_doc(self.test_scenario1, examples)

        for example in examples:
            print("\nTesting with:\n", example)
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
            print("\nTesting with:\n", example)
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
            ['data/iris.csv', '10', '50', '60', '{"petal width": 4}', '000004', 'Iris-versicolor', '{}', {"kind": "probability", "threshold": 1, "positive_class": "Iris-virginica"}]]
        show_doc(self.test_scenario3, examples)

        for example in examples:
            print("\nTesting with:\n", example)
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
            print("\nTesting with:\n", example)
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


    def test_scenario5(self):
        """
            Scenario: Successfully comparing predictions in operating kind for models:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a model
                And I wait until the model is ready less than <time_3> secs
                And I create a local model
                When I create a prediction for "<data_input>" in "<operating_kind>"
                Then the prediction for "<objective>" is "<prediction>"
                And I create a local prediction for "<data_input>" in "<operating_kind>"
                Then the local prediction is "<prediction>"

                Examples:
                | data             | time_1  | time_2 | time_3 | data_input                             | prediction  | operating_point


        """
        examples = [
            ['data/iris.csv', '10', '50', '50', '{"petal length": 2.46, "sepal length": 5}', 'Iris-versicolor',  "probability", "000004"],
            ['data/iris.csv', '10', '50', '50', '{"petal length": 2.46, "sepal length": 5}', 'Iris-versicolor',  "confidence", "000004"],
            ['data/iris.csv', '10', '50', '50', '{"petal length": 2}', 'Iris-setosa',  "probability", "000004"],
            ['data/iris.csv', '10', '50', '50', '{"petal length": 2}', 'Iris-setosa',  "confidence", "000004"]]
        show_doc(self.test_scenario5, examples)

        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_model(self)
            model_create.the_model_is_finished_in_less_than(self, example[3])
            prediction_compare.i_create_a_local_model(self)
            prediction_create.i_create_a_prediction_op_kind(self, example[4], example[6])
            prediction_create.the_prediction_is(self, example[7], example[5])
            prediction_compare.i_create_a_local_prediction_op_kind(self, example[4], example[6])
            prediction_compare.the_local_prediction_is(self, example[5])


    def test_scenario6(self):
        """
            Scenario: Successfully comparing predictions for deepnets with operating kind:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a deepnet with objective "<objective>" and "<params>"
                And I wait until the deepnet is ready less than <time_3> secs
                And I create a local deepnet
                When I create a prediction with operating kind "<operating_kind>" for "<data_input>"
                Then the prediction for "<objective>" is "<prediction>"
                And I create a local prediction with operating point "<operating_kind>" for "<data_input>"
                Then the local prediction is "<prediction>"

                Examples:
                | data             | time_1  | time_2 | time_3 | data_input                             | objective | prediction  | params | operating_point,


        """
        examples = [
            ['data/iris.csv', '10', '50', '60', '{"petal length": 2.46}', '000004', 'Iris-setosa', '{}', "probability"],
            ['data/iris.csv', '10', '50', '60', '{"petal length": 2}', '000004', 'Iris-setosa', '{}', "probability"]]
        show_doc(self.test_scenario6, examples)

        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_deepnet_with_objective_and_params(self, example[5], example[7])
            model_create.the_deepnet_is_finished_in_less_than(self, example[3])
            prediction_compare.i_create_a_local_deepnet(self)
            prediction_create.i_create_a_deepnet_prediction_op_kind(self, example[4], example[8])
            prediction_create.the_prediction_is(self, example[5], example[6])
            prediction_compare.i_create_a_local_deepnet_prediction_op_kind(self, example[4], example[8])
            prediction_compare.the_local_prediction_is(self, example[6])


    def test_scenario7(self):
        """
            Scenario: Successfully comparing predictions in operating points for ensembles:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create an ensemble
                And I wait until the ensemble is ready less than <time_3> secs
                And I create a local ensemble
                When I create a prediction for "<data_input>" in "<operating_kind>"
                Then the prediction for "<objective>" is "<prediction>"
                And I create a local ensemble prediction for "<data_input>" in "<operating_kind>"
                Then the local ensemble prediction is "<prediction>"

                Examples:
                | data             | time_1  | time_2 | time_3 | data_input                             | prediction  | operating_kind


        """
        examples = [
            ['data/iris.csv', '10', '50', '50', '{"petal length": 2.46}', 'Iris-versicolor',  "probability", "000004"],
            ['data/iris.csv', '10', '50', '50', '{"petal length": 2}', 'Iris-setosa',  "probability", "000004"],
            ['data/iris.csv', '10', '50', '50', '{"petal length": 2.46}', 'Iris-versicolor',  "confidence", "000004"],
            ['data/iris.csv', '10', '50', '50', '{"petal length": 2}', 'Iris-setosa',  "confidence", "000004"],
            ['data/iris.csv', '10', '50', '50', '{"petal length": 2.46}', 'Iris-versicolor',  "votes", "000004"],
            ['data/iris.csv', '10', '50', '50', '{"petal length": 1}', 'Iris-setosa',  "votes", "000004"]]
        show_doc(self.test_scenario7, examples)

        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            ensemble_create.i_create_an_ensemble(self)
            ensemble_create.the_ensemble_is_finished_in_less_than(self, example[3])
            ensemble_create.create_local_ensemble(self)
            prediction_create.i_create_an_ensemble_prediction_op_kind(self, example[4], example[6])
            prediction_create.the_prediction_is(self, example[7], example[5])
            prediction_compare.i_create_a_local_ensemble_prediction_op_kind(self, example[4], example[6])
            prediction_compare.the_local_prediction_is(self, example[5])

    def test_scenario8(self):
        """
            Scenario: Successfully comparing predictions for logistic regressions with operating kind:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a logistic regression with objective "<objective>"
                And I wait until the logistic regression is ready less than <time_3> secs
                And I create a local logistic regression
                When I create a prediction with operating kind "<operating_kind>" for "<data_input>"
                Then the prediction for "<objective>" is "<prediction>"
                And I create a local prediction with operating point "<operating_kind>" for "<data_input>"
                Then the local prediction is "<prediction>"

                Examples:
                | data             | time_1  | time_2 | time_3 | data_input                             | objective | prediction  | params | operating_point,


        """
        examples = [
            ['data/iris.csv', '10', '50', '60', '{"petal length": 5}', '000004', 'Iris-versicolor', '{}', "probability"],
            ['data/iris.csv', '10', '50', '60', '{"petal length": 2}', '000004', 'Iris-setosa', '{}', "probability"]]
        show_doc(self.test_scenario8, examples)

        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_logistic_model(self)
            model_create.the_logistic_model_is_finished_in_less_than(self, example[3])
            prediction_compare.i_create_a_local_logistic_model(self)
            prediction_create.i_create_a_logistic_prediction_with_op_kind(self, example[4], example[8])
            prediction_create.the_prediction_is(self, example[5], example[6])
            prediction_compare.i_create_a_local_logistic_prediction_op_kind(self, example[4], example[8])
            prediction_compare.the_local_prediction_is(self, example[6])


    def test_scenario9(self):
        """
            Scenario: Successfully comparing predictions for logistic regressions with operating kind and supervised model:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a logistic regression with objective "<objective>"
                And I wait until the logistic regression is ready less than <time_3> secs
                And I create a local supervised model
                When I create a prediction with operating kind "<operating_kind>" for "<data_input>"
                Then the prediction for "<objective>" is "<prediction>"
                And I create a local prediction with operating point "<operating_kind>" for "<data_input>"
                Then the local prediction is "<prediction>"

                Examples:
                | data             | time_1  | time_2 | time_3 | data_input                             | objective | prediction  | params | operating_point,


        """
        examples = [
            ['data/iris.csv', '10', '50', '60', '{"petal length": 5}', '000004', 'Iris-versicolor', '{}', "probability"],
            ['data/iris.csv', '10', '50', '60', '{"petal length": 2}', '000004', 'Iris-setosa', '{}', "probability"]]
        show_doc(self.test_scenario9, examples)

        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_logistic_model(self)
            model_create.the_logistic_model_is_finished_in_less_than(self, example[3])
            prediction_compare.i_create_a_local_supervised_model(self, model_type="logistic_regression")
            prediction_create.i_create_a_logistic_prediction_with_op_kind(self, example[4], example[8])
            prediction_create.the_prediction_is(self, example[5], example[6])
            prediction_compare.i_create_a_local_logistic_prediction_op_kind(self, example[4], example[8])
            prediction_compare.the_local_prediction_is(self, example[6])

    def test_scenario10(self):
        """
            Scenario: Successfully comparing predictions for linear regression:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a linear regression with objective "<objective>" and "<params>"
                And I wait until the linear regression is ready less than <time_3> secs
                And I create a local linear regression
                When I create a prediction for "<data_input>"
                Then the prediction for "<objective>" is "<prediction>"
                And I create a local prediction for "<data_input>"
                Then the local prediction is "<prediction>"

                Examples:
                | data             | time_1  | time_2 | time_3 | data_input                             | objective | prediction  | params

        """
        examples = [
            ['data/grades.csv', '10', '50', '60', '{"000000": 1, "000001": 1, "000002": 1}', '000005', 29.63024, '{"input_fields": ["000000", "000001", "000002"]}'],
            ['data/iris.csv', '10', '50', '60', '{"000000": 1, "000001": 1, "000004": "Iris-virginica"}', '000003', 1.21187, '{"input_fields": ["000000", "000001", "000004"]}'],
            ['data/movies.csv', '10', '50', '60', '{"000007": "Action"}', '000009', 4.33333, '{"input_fields": ["000007"]}'],
            ['data/movies.csv', '10', '50', '60', '{"000006": "1999"}', '000009', 3.28427, '{"input_fields": ["000006"], "bias": false}']]
        show_doc(self.test_scenario10, examples)

        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            linear_create.i_create_a_linear_regression_with_objective_and_params( \
                self, example[5], example[7])
            linear_create.the_linear_regression_is_finished_in_less_than( \
                self, example[3])
            prediction_compare.i_create_a_local_linear(self)
            prediction_create.i_create_a_linear_prediction(self, example[4])
            prediction_create.the_prediction_is(self, example[5], example[6])
            prediction_compare.i_create_a_local_linear_prediction(self, example[4])
            prediction_compare.the_local_prediction_is(self, example[6])

    def test_scenario11(self):
        """
            Scenario: Successfully comparing remote and local predictions
                      with raw date input for linear regression:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a linear regression
                And I wait until the linear regression is ready
                less than <time_3> secs
                And I create a local linear regression
                When I create a prediction for "<data_input>"
                Then the prediction for "<objective>" is "<prediction>"
                And I create a local prediction for "<data_input>"
                Then the local prediction is "<prediction>"

                Examples:
                |data|time_1|time_2|time_3|data_input|objective|prediction

        """
        examples = [
            ['data/dates2.csv', '20', '20', '25',
             '{"time-1": "1910-05-08T19:10:23.106", "cat-0":"cat2"}',
             '000002',  -0.01284],
            ['data/dates2.csv', '20', '20', '25',
             '{"time-1": "1920-06-30T20:21:20.320", "cat-0":"cat1"}',
             '000002', -0.09459],
            ['data/dates2.csv', '20', '20', '25',
             '{"time-1": "1932-01-30T19:24:11.440",  "cat-0":"cat2"}',
             '000002', -0.02259],
            ['data/dates2.csv', '20', '20', '25',
             '{"time-1": "1950-11-06T05:34:05.252", "cat-0":"cat1"}',
             '000002', -0.06754],
            ['data/dates2.csv', '20', '20', '25',
             '{"time-1": "2001-01-05T23:04:04.693", "cat-0":"cat2"}',
             '000002', 0.05204],
            ['data/dates2.csv', '20', '20', '25',
             '{"time-1": "2011-04-01T00:16:45.747", "cat-0":"cat2"}',
             '000002', 0.05878]]
        show_doc(self.test_scenario11, examples)

        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self,
                                                                example[2])
            linear_create.i_create_a_linear_regression(self)
            linear_create.the_linear_regression_is_finished_in_less_than(self,
                                                                         example[3])
            prediction_compare.i_create_a_local_linear(self)
            prediction_create.i_create_a_linear_prediction(self, example[4])
            prediction_create.the_prediction_is(self, example[5], example[6])
            prediction_compare.i_create_a_local_linear_prediction(self,
                                                                  example[4])
            prediction_compare.the_local_prediction_is(self, example[6])

    def test_scenario12(self):
        """
            Scenario: Successfully comparing remote and local predictions
                      with raw date input for deepnet:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a deepnet
                And I wait until the deepnet is ready
                less than <time_3> secs
                And I create a local deepnet
                When I create a prediction for "<data_input>"
                Then the prediction for "<objective>" is "<prediction>"
                And I create a local prediction for "<data_input>"
                Then the local prediction is "<prediction>"

                Examples:
                |data|time_1|time_2|time_3|data_input|objective|prediction






            ['data/dates2.csv', '20', '45', '60',
             '{"time-1": "1910-05-08T19:10:23.106", "cat-0":"cat2"}',
             '000002', 0.04082],
            ['data/dates2.csv', '20', '45', '60',
             '{"time-1": "2011-04-01T00:16:45.747", "cat-0":"cat2"}',
             '000002', 0.02919],
            ['data/dates2.csv', '20', '45', '60',
             '{"time-1": "1969-W29-1T17:36:39Z", "cat-0":"cat1"}',
             '000002', 0.0199],
            ['data/dates2.csv', '20', '45', '60',
             '{"time-1": "1920-06-45T20:21:20.320", "cat-0":"cat1"}',
             '000002', 0.0199],
            ['data/dates2.csv', '20', '45', '60',
             '{"time-1": "2001-01-05T23:04:04.693", "cat-0":"cat2"}',
             '000002', 0.28517],
            ['data/dates2.csv', '20', '45', '60',
             '{"time-1": "1950-11-06T05:34:05.602", "cat-0":"cat1"}',
             '000002', -0.05673],
            ['data/dates2.csv', '20', '45', '60',
             '{"time-1": "1932-01-30T19:24:11.440",  "cat-0":"cat2"}',
             '000002', 0.16183],
            ['data/dates2.csv', '20', '45', '60',
             '{"time-1": "Mon Jul 14 17:36 +0000 1969", "cat-0":"cat1"}',
             '000002', 0.0199]

        """
        examples = [
            ['data/dates2.csv', '20', '45', '60',
             '{"time-1": "1910-05-08T19:10:23.106", "cat-0":"cat2"}',
             '000002', 0.04082],
            ['data/dates2.csv', '20', '45', '60',
             '{"time-1": "2011-04-01T00:16:45.747", "cat-0":"cat2"}',
             '000002', 0.02919],
            ['data/dates2.csv', '20', '45', '60',
             '{"time-1": "1969-W29-1T17:36:39Z", "cat-0":"cat1"}',
             '000002', 0.0199],
            ['data/dates2.csv', '20', '45', '60',
             '{"time-1": "1920-06-45T20:21:20.320", "cat-0":"cat1"}',
             '000002', 0.0199],
            ['data/dates2.csv', '20', '45', '60',
             '{"time-1": "2001-01-05T23:04:04.693", "cat-0":"cat2"}',
             '000002', 0.28517],
            ['data/dates2.csv', '20', '45', '60',
             '{"time-1": "1950-11-06T05:34:05.602", "cat-0":"cat1"}',
             '000002', -0.05673],
            ['data/dates2.csv', '20', '45', '60',
             '{"time-1": "1932-01-30T19:24:11.440",  "cat-0":"cat2"}',
             '000002', 0.16183],
            ['data/dates2.csv', '20', '45', '60',
             '{"time-1": "Mon Jul 14 17:36 +0000 1969", "cat-0":"cat1"}',
             '000002', 0.0199]
]
        show_doc(self.test_scenario12, examples)

        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_no_suggest_deepnet(self)
            model_create.the_deepnet_is_finished_in_less_than(self, example[3])
            prediction_compare.i_create_a_local_deepnet(self)
            prediction_create.i_create_a_deepnet_prediction(self, example[4])
            prediction_create.the_prediction_is(self, example[5], example[6])
            prediction_compare.i_create_a_local_deepnet_prediction(self,
                                                                   example[4])
            prediction_compare.the_local_prediction_is(self, example[6])
