# -*- coding: utf-8 -*-
#
# Copyright 2015-2021 BigML
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
import sys

from .world import world, setup_module, teardown_module, show_doc, show_method
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create
from . import create_model_steps as model_create
from . import create_association_steps as association_create
from . import create_cluster_steps as cluster_create
from . import create_anomaly_steps as anomaly_create
from . import create_prediction_steps as prediction_create
from . import compare_predictions_steps as prediction_compare
from . import create_lda_steps as topic_create


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

    def test_scenario10(self):
        """
           Scenario: Successfully comparing predictions with proportional missing strategy and balanced models:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a balanced model
                And I wait until the model is ready less than <model_wait> secs
                And I create a local model
                When I create a proportional missing strategy prediction for "<input_data>"
                Then the prediction for "<objective_id>" is "<prediction>"
                And the confidence for the prediction is "<confidence>"
                And I create a proportional missing strategy local prediction for "<input_data>"
                Then the local prediction is "<prediction>"
                And the local prediction's confidence is "<confidence>"
                And I create local probabilities for "<input_data>"
                Then the local probabilities are "<probabilities>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "input_data", "objective_id", "prediction",
                   "confidence", "probabilities"]
        examples = [
            ['data/iris_unbalanced.csv', '10', '10', '10', '{}', '000004',
             'Iris-setosa', '0.25284', '[0.33333, 0.33333, 0.33333]'],
            ['data/iris_unbalanced.csv', '10', '10', '10',
             '{"petal length":1, "sepal length":1, "petal width": 1, '
             '"sepal width": 1}', '000004', 'Iris-setosa', '0.7575',
             '[1.0, 0.0, 0.0]']]
        show_doc(self.test_scenario10)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(self, example["data"],
                shared=example["data"])
            source_create.the_source_is_finished(self, example["source_wait"],
                shared=example["data"])
            dataset_create.i_create_a_dataset(self, shared=example["data"])
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"], shared=example["data"])
            model_create.i_create_a_balanced_model(self)
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            prediction_compare.i_create_a_local_model(self)
            prediction_create.i_create_a_proportional_prediction(
                self, example["input_data"])
            prediction_create.the_prediction_is(
                self, example["objective_id"], example["prediction"])
            prediction_compare.i_create_a_proportional_local_prediction(
                self, example["input_data"])
            prediction_compare.the_local_prediction_is(
                self, example["prediction"])
            prediction_create.the_confidence_is(
                self, example["confidence"])
            prediction_compare.the_local_prediction_confidence_is(
                self, example["confidence"])
            prediction_compare.i_create_local_probabilities(
                self, example["input_data"])
            prediction_compare.the_local_probabilities_are(
                self, example["probabilities"])

    def test_scenario11(self):
        """
            Scenario: Successfully comparing predictions for logistic regression with balance_fields:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I update the source with params "<source_conf>"
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a logistic regression model with objective "<objective_id>" and flags
                And I wait until the logistic regression model is ready less than <model_wait> secs
                And I create a local logistic regression model
                When I create a logistic regression prediction for "<input_data>"
                Then the logistic regression prediction is "<prediction>"
                And the logistic regression probability for the prediction is "<probability>"
                And I create a local logistic regression prediction for "<input_data>"
                Then the local logistic regression prediction is "<prediction>"
                And the local logistic regression probability for the prediction is "<probability>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "source_conf", "input_data", "prediction", "probability",
                   "objective_id", "model_conf"]
        examples = [
            ['data/movies.csv', '20', '20', '180',
             '{"fields": {"000000": {"name": "user_id", "optype": "numeric"},'
             ' "000001": {"name": "gender", "optype": "categorical"},'
             ' "000002": {"name": "age_range", "optype": "categorical"},'
             ' "000003": {"name": "occupation", "optype": "categorical"},'
             ' "000004": {"name": "zipcode", "optype": "numeric"},'
             ' "000005": {"name": "movie_id", "optype": "numeric"},'
             ' "000006": {"name": "title", "optype": "text"},'
             ' "000007": {"name": "genres", "optype": "items",'
             '"item_analysis": {"separator": "$"}},'
             '"000008": {"name": "timestamp", "optype": "numeric"},'
             '"000009": {"name": "rating", "optype": "categorical"}},'
             '"source_parser": {"separator": ";"}}',
             '{"timestamp": "999999999"}', '4', 0.4079, "000009",
             '{"balance_fields": false}'],
            ['data/movies.csv', '20', '20', '180',
             '{"fields": {"000000": {"name": "user_id", "optype": "numeric"},'
             ' "000001": {"name": "gender", "optype": "categorical"},'
             ' "000002": {"name": "age_range", "optype": "categorical"},'
             ' "000003": {"name": "occupation", "optype": "categorical"},'
             ' "000004": {"name": "zipcode", "optype": "numeric"},'
             ' "000005": {"name": "movie_id", "optype": "numeric"},'
             ' "000006": {"name": "title", "optype": "text"},'
             ' "000007": {"name": "genres", "optype": "items",'
             '"item_analysis": {"separator": "$"}},'
             '"000008": {"name": "timestamp", "optype": "numeric"},'
             '"000009": {"name": "rating", "optype": "categorical"}},'
             '"source_parser": {"separator": ";"}}',
             '{"timestamp": "999999999"}', '4', 0.2547, "000009",
             '{"normalize": true}'],
            ['data/movies.csv', '20', '20', '180',
             '{"fields": {"000000": {"name": "user_id", "optype": "numeric"},'
             ' "000001": {"name": "gender", "optype": "categorical"},'
             ' "000002": {"name": "age_range", "optype": "categorical"},'
             ' "000003": {"name": "occupation", "optype": "categorical"},'
             ' "000004": {"name": "zipcode", "optype": "numeric"},'
             ' "000005": {"name": "movie_id", "optype": "numeric"},'
             ' "000006": {"name": "title", "optype": "text"},'
             ' "000007": {"name": "genres", "optype": "items",'
             '"item_analysis": {"separator": "$"}},'
             '"000008": {"name": "timestamp", "optype": "numeric"},'
             '"000009": {"name": "rating", "optype": "categorical"}},'
             '"source_parser": {"separator": ";"}}',
             '{"timestamp": "999999999"}', '4', 0.2547, "000009",
             '{"balance_fields": true, "normalize": true}']]
        show_doc(self.test_scenario11)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(self, example["data"])
            source_create.the_source_is_finished(self, example["source_wait"])
            source_create.i_update_source_with(self, example["source_conf"])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"])
            model_create.i_create_a_logistic_model_with_objective_and_parms(
                self, example["objective_id"], example["model_conf"])
            model_create.the_logistic_model_is_finished_in_less_than(
                self, example["model_wait"])
            prediction_compare.i_create_a_local_logistic_model(self)
            prediction_create.i_create_a_logistic_prediction(
                self, example["input_data"])
            prediction_create.the_logistic_prediction_is(
                self, example["prediction"])
            prediction_create.the_logistic_probability_is(
                self, example["probability"])
            prediction_compare.i_create_a_local_prediction(
                self, example["input_data"])
            prediction_compare.the_local_prediction_is(
                self, example["prediction"])
            prediction_compare.the_local_probability_is(
                self, example["probability"])

    def test_scenario12(self):
        """
            Scenario: Successfully comparing logistic regression predictions with constant fields:

                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I update the dataset with "<dataset_conf>"
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a logistic regression model
                And I wait until the logistic regression model is ready less than <model_wait> secs
                And I create a local logistic regression model
                When I create a logistic regression prediction for "<input_data>"
                Then the logistic regression prediction is "<prediction>"
                And I create a local logistic regression prediction for "<input_data>"
                Then the local logistic regression prediction is "<prediction>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "input_data", "prediction", "dataset_conf"]
        examples = [
            ['data/constant_field.csv', '10', '20', '50',
             '{"a": 1, "b": 1, "c": 1}', 'a',
             '{"fields": {"000000": {"preferred": true}}}']]
        show_doc(self.test_scenario12)

        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"])
            dataset_create.i_update_dataset_with(self, example["dataset_conf"])
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"])
            model_create.i_create_a_logistic_model(self)
            model_create.the_logistic_model_is_finished_in_less_than(
                self, example["model_wait"])
            prediction_compare.i_create_a_local_logistic_model(self)
            prediction_create.i_create_a_logistic_prediction(
                self, example["input_data"])
            prediction_create.the_logistic_prediction_is(
                self, example["prediction"])
            prediction_compare.i_create_a_local_prediction(
                self, example["input_data"])
            prediction_compare.the_local_prediction_is(
                self, example["prediction"])

    def test_scenario13(self):
        """
            Scenario: Successfully comparing predictions:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a model
                And I wait until the model is ready less than <model_wait> secs
                And I create a local model
                When I create a prediction for "<input_data>"
                Then the prediction for "<objective>" is "<prediction>"
                And I create a local prediction for "<input_data>"
                Then the local prediction is "<prediction>"
                And I export the model with tags "<model_tags>"
                And I create a local model from file "<model_file>"
                And I create a local prediction for "<input_data>"
                Then the local prediction is "<prediction>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "input_data", "objective_id", "prediction",
                   "model_file", "model_tags"]
        examples = [
            ['data/iris.csv', '10', '10', '10', '{"petal width": 0.5}',
             '000004', 'Iris-setosa', "tmp/my_model.json", "my_test"],
            ['data/iris.csv', '10', '10', '10',
             '{"petal length": 6, "petal width": 2}', '000004',
             'Iris-virginica', "tmp/my_model.json", "my_test"],
            ['data/iris.csv', '10', '10', '10',
             '{"petal length": 4, "petal width": 1.5}', '000004',
             'Iris-versicolor', "tmp/my_model.json", "my_test"],
            ['data/iris_sp_chars.csv', '10', '10', '10',
             '{"pétal.length": 4, "pétal&width\\u0000": 1.5}', '000004',
             'Iris-versicolor', "tmp/my_model_2.json", "my_test"]]
        show_doc(self.test_scenario13)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            dataset_create.i_create_a_dataset(
                self, shared=example["data"])
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"], shared=example["data"])
            args = '{"tags": ["%s"]}' % example["model_tags"]
            model_create.i_create_a_model_with(self, data=args)
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            model_create.i_export_model(
                self, False, example["model_file"]) # no pmml
            prediction_compare.i_create_a_local_model_from_file(
                self, example["model_file"])
            prediction_create.i_create_a_prediction(
                self, example["input_data"])
            prediction_create.the_prediction_is(
                self, example["objective_id"], example["prediction"])
            prediction_compare.i_create_a_local_prediction(
                self, example["input_data"])
            prediction_compare.the_local_prediction_is(
                self, example["prediction"])
            model_create.i_export_tags_model(
                self, example["model_file"], example["model_tags"])
            prediction_compare.i_create_a_local_model_from_file(
                self, example["model_file"])
            prediction_compare.i_create_a_local_prediction(
                self, example["input_data"])
            prediction_compare.the_local_prediction_is(
                self, example["prediction"])

    def test_scenario14(self):
        """
            Scenario: Successfully comparing predictions with supervised model:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a model
                And I wait until the model is ready less than <model_wait> secs
                And I create a local supervised model
                When I create a prediction for "<input_data>"
                Then the prediction for "<objective>" is "<prediction>"
                And I create a local prediction for "<input_data>"
                Then the local prediction is "<prediction>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "input_data", "objective_id", "prediction"]
        examples = [
            ['data/iris.csv', '10', '10', '10', '{"petal width": 0.5}',
             '000004', 'Iris-setosa'],
            ['data/iris.csv', '10', '10', '10',
             '{"petal length": 6, "petal width": 2}', '000004',
             'Iris-virginica'],
            ['data/iris.csv', '10', '10', '10',
             '{"petal length": 4, "petal width": 1.5}', '000004',
             'Iris-versicolor'],
            ['data/iris_sp_chars.csv', '10', '10', '10',
             '{"pétal.length": 4, "pétal&width\\u0000": 1.5}',
             '000004', 'Iris-versicolor']]
        show_doc(self.test_scenario14)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            dataset_create.i_create_a_dataset(self, shared=example["data"])
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"], shared=example["data"])
            model_create.i_create_a_model(self, shared=example["data"])
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"], shared=example["data"])
            prediction_compare.i_create_a_local_supervised_model(self)
            prediction_create.i_create_a_prediction(
                self, example["input_data"])
            prediction_create.the_prediction_is(
                self, example["objective_id"], example["prediction"])
            prediction_compare.i_create_a_local_prediction(
                self, example["input_data"])
            prediction_compare.the_local_prediction_is(
                self, example["prediction"])

    def test_scenario15(self):
        """
            Scenario: Successfully comparing predictions with text options:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a logistic regression model with objective "<objective_id>" and params "<model_conf>"
                And I wait until the logistic regression model is ready less than <model_wait> secs
                And I create a local logistic regression model
                When I create a logistic regression prediction for "<input_data>"
                Then the logistic regression prediction is "<prediction>"
                And the logistic regression probability for the prediction is "<probability>"
                And I create a local logistic regression prediction for "<input_data>"
                Then the local logistic regression prediction is "<prediction>"
                And the local logistic regression probability for the prediction is "<probability>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "model_conf", "input_data", "prediction", "probability",
                   "objective_id"]
        examples = [
            ['data/iris.csv', '20', '20', '180',
             '{"weight_field": "000000", "missing_numerics": false}',
             '{"petal width": 1.5, "petal length": 2, "sepal width":1}',
             'Iris-versicolor', '0.9547', '000004']]
        show_doc(self.test_scenario15)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(self, example["source_wait"],
                shared=example["data"])
            dataset_create.i_create_a_dataset(self, shared=example["data"])
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"], shared=example["data"])
            model_create.i_create_a_logistic_model_with_objective_and_parms(
                self, example["objective_id"], example["model_conf"])
            model_create.the_logistic_model_is_finished_in_less_than(
                self, example["model_wait"])
            prediction_compare.i_create_a_local_logistic_model(self)
            prediction_create.i_create_a_logistic_prediction(
                self, example["input_data"])
            prediction_create.the_logistic_prediction_is(
                self, example["prediction"])
            prediction_create.the_logistic_probability_is(
                self, example["probability"])
            prediction_compare.i_create_a_local_prediction(
                self, example["input_data"])
            prediction_compare.the_local_prediction_is(
                self, example["prediction"])
            prediction_compare.the_local_probability_is(
                self, example["probability"])

    def test_scenario16(self):
        """
           Scenario: Successfully comparing remote and local predictions
                     with raw date input:
               Given I create a data source uploading a "<data>" file
               And I wait until the source is ready less than <source_wait> secs
               And I create a dataset
               And I wait until the dataset is ready less than <dataset_wait> secs
               And I create a model
               And I wait until the model is ready less than <model_wait> secs
               And I create a local model
               When I create a prediction for "<input_data>"
               Then the prediction for "<objective>" is "<prediction>"
               And I create a local prediction for "<input_data>"
               Then the local prediction is "<prediction>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "input_data", "objective_id", "prediction"]
        examples = [
            ['data/dates2.csv', '20', '20', '25',
             '{"time-1": "1910-05-08T19:10:23.106", "cat-0":"cat2"}',
             '000002', -1.01482],
            ['data/dates2.csv', '20', '20', '25',
             '{"time-1": "1920-06-30T20:21:20.320", "cat-0":"cat1"}',
             '000002', 0.78406],
            ['data/dates2.csv', '20', '20', '25',
             '{"time-1": "1932-01-30T19:24:11.440",  "cat-0":"cat2"}',
             '000002', -0.98757],
            ['data/dates2.csv', '20', '20', '25',
             '{"time-1": "1950-11-06T05:34:05.252", "cat-0":"cat1"}',
             '000002', 0.27538],
            ['data/dates2.csv', '20', '20', '25',
             '{"time-1": "1969-7-14 17:36", "cat-0":"cat2"}',
             '000002', -0.06256],
            ['data/dates2.csv', '20', '20', '25',
             '{"time-1": "2001-01-05T23:04:04.693", "cat-0":"cat2"}',
             '000002', 0.9832],
            ['data/dates2.csv', '20', '20', '25',
             '{"time-1": "2011-04-01T00:16:45.747", "cat-0":"cat2"}',
             '000002', -0.5977],
            ['data/dates2.csv', '20', '20', '25',
             '{"time-1": "1969-W29-1T17:36:39Z", "cat-0":"cat1"}',
             '000002',  -0.06256],
            ['data/dates2.csv', '20', '20', '25',
             '{"time-1": "Mon Jul 14 17:36 +0000 1969", "cat-0":"cat1"}',
             '000002', -0.06256]]
        show_doc(self.test_scenario16)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(self, example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            dataset_create.i_create_a_dataset(self, shared=example["data"])
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"], shared=example["data"])
            model_create.i_create_a_model(self, shared=example["data"])
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"], shared=example["data"])
            prediction_compare.i_create_a_local_model(self)
            prediction_create.i_create_a_prediction(
                self, example["input_data"])
            prediction_create.the_prediction_is(
                self, example["objective_id"], example["prediction"])
            prediction_compare.i_create_a_local_prediction(
                self, example["input_data"])
            prediction_compare.the_local_prediction_is(
                self, example["prediction"])

    def test_scenario17(self):
        """
           Scenario: Successfully comparing remote and local predictions
                     with raw date input:
               Given I create a data source uploading a "<data>" file
               And I wait until the source is ready less than <source_wait> secs
               And I create a dataset
               And I wait until the dataset is ready less than <dataset_wait> secs
               And I create a logistic regression model
               And I wait until the logistic regression is ready less
               than <model_wait> secs
               And I create a local logistic regression model
               When I create a prediction for "<input_data>"
               Then the prediction is "<prediction>"
               And the logistic regression probability for the prediction
               is "<probability>"
               And I create a local prediction for "<input_data>"
               Then the local prediction is "<prediction>"
               And the local logistic regression probability for the
               prediction is "<probability>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "input_data", "prediction", "probability"]
        examples = [
            ['data/dates2.csv', '20', '20', '45',
             '{"time-1": "1910-05-08T19:10:23.106", "target-1":0.722}',
             'cat0', 0.75024],
            ['data/dates2.csv', '20', '20', '45',
             '{"time-1": "1920-06-30T20:21:20.320", "target-1":0.12}',
             'cat0', 0.75821],
            ['data/dates2.csv', '20', '20', '45',
             '{"time-1": "1932-01-30T19:24:11.440",  "target-1":0.32}',
             'cat0', 0.71498],
            ['data/dates2.csv', '20', '20', '45',
             '{"time-1": "1950-11-06T05:34:05.252", "target-1":0.124}',
             'cat0', 0.775],
            ['data/dates2.csv', '20', '20', '45',
             '{"time-1": "1969-7-14 17:36", "target-1":0.784}',
             'cat0', 0.73663],
            ['data/dates2.csv', '20', '20', '45',
             '{"time-1": "2001-01-05T23:04:04.693", "target-1":0.451}',
             'cat0', 0.6822],
            ['data/dates2.csv', '20', '20', '45',
             '{"time-1": "2011-04-01T00:16:45.747", "target-1":0.42}',
             'cat0', 0.71107],
            ['data/dates2.csv', '20', '20', '45',
             '{"time-1": "1969-W29-1T17:36:39Z", "target-1":0.67}',
             'cat0', 0.73663],
            ['data/dates2.csv', '20', '20', '45',
             '{"time-1": "Mon Jul 14 17:36 +0000 1969", "target-1":0.005}',
             'cat0', 0.73663]]
        show_doc(self.test_scenario17)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            dataset_create.i_create_a_dataset(self, shared=example["data"])
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"], shared=example["data"])
            model_create.i_create_a_logistic_model(
                self, shared=example["data"])
            model_create.the_logistic_model_is_finished_in_less_than(
                self, example["model_wait"], shared=example["data"])
            prediction_compare.i_create_a_local_logistic_model(self)
            prediction_create.i_create_a_logistic_prediction(
                self, example["input_data"])
            prediction_create.the_logistic_prediction_is(
                self, example["prediction"])
            prediction_create.the_logistic_probability_is(
                self, example["probability"])
            prediction_compare.i_create_a_local_prediction(
                self, example["input_data"])
            prediction_compare.the_local_prediction_is(
                self, example["prediction"])
            prediction_compare.the_local_probability_is(
                self, example["probability"])

    def test_scenario18(self):
        """
            Scenario: Successfully comparing predictions with proportional missing strategy for missing_splits models:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a weighted model with missing splits
                And I wait until the model is ready less than <model_wait> secs
                And I create a local model
                When I create a proportional missing strategy prediction for "<input_data>"
                Then the prediction for "<objective_id>" is "<prediction>"
                And the confidence for the prediction is "<confidence>"
                And I create a proportional missing strategy local prediction for "<input_data>"
                Then the local prediction is "<prediction>"
                And the local prediction's confidence is "<confidence>"
                And the highest local prediction's confidence is "<confidence>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "input_data", "objective_id", "prediction", "confidence"]
        examples = [
            ['data/missings_cat.csv', '10', '10', '10', '{"x2": 4}',
             '000002', 'positive', '0.25241']
]
        show_doc(self.test_scenario18)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            dataset_create.i_create_a_dataset(self, shared=example["data"])
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"], shared=example["data"])
            model_create.i_create_a_weighted_model_with_missing_splits(self)
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            prediction_compare.i_create_a_local_model(self)
            prediction_create.i_create_a_proportional_prediction(
                self, example["input_data"])
            prediction_create.the_prediction_is(
                self, example["objective_id"], example["prediction"])
            prediction_create.the_confidence_is(
                self, example["confidence"])
            prediction_compare.i_create_a_proportional_local_prediction(
                self, example["input_data"])
            prediction_compare.the_local_prediction_is(
                self, example["prediction"])
            prediction_compare.the_local_prediction_confidence_is(
                self, example["confidence"])
            prediction_compare.the_highest_local_prediction_confidence_is(
                self, example["input_data"], example["confidence"])
