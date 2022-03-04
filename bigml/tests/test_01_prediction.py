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


""" Testing prediction creation

"""
import sys

from .world import world, setup_module, teardown_module, show_doc, show_method
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create
from . import create_model_steps as model_create
from . import create_cluster_steps as cluster_create
from . import create_anomaly_steps as anomaly_create
from . import create_lda_steps as topic_create
from . import create_prediction_steps as prediction_create


class TestPrediction(object):

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
            Scenario 1: Successfully creating a prediction:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a model
                And I wait until the model is ready less than <model_wait> secs
                When I create a prediction for "<input_data>"
                Then the prediction for "<objective_id>" is "<prediction>"

        """
        show_doc(self.test_scenario1)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "input_data", "objective_id", "prediction"]
        examples = [
            ['data/iris.csv', '30', '30', '30',
             '{"petal width": 0.5}', '000004', 'Iris-setosa'],
            ['data/iris_sp_chars.csv', '30', '30', '30',
             '{"pétal&width\\u0000": 0.5}', '000004', 'Iris-setosa']]
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
            model_create.i_create_a_model(self, shared=example["data"])
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"], shared=example["data"])
            prediction_create.i_create_a_prediction(
                self, example["input_data"])
            prediction_create.the_prediction_is(
                self, example["objective_id"], example["prediction"])

    def test_scenario2(self):
        """
            Scenario 2: Successfully creating a prediction from a source in a remote location

                Given I create a data source using the url "<url>"
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a model
                And I wait until the model is ready less than <model_wait> secs
                When I create a prediction for "<input_data>"
                Then the prediction for "<objective_id>" is "<prediction>"

        """
        show_doc(self.test_scenario2)
        headers = ["url", "wait_source", "wait_dataset", "wait_model",
                   "input_data", "objective_id", "prediction"]
        examples = [
            ['s3://bigml-public/csv/iris.csv', '10', '10', '10',
             '{"petal width": 0.5}', '000004', 'Iris-setosa']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_create_using_url(self, example["url"])
            source_create.the_source_is_finished(self, example["wait_source"])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["wait_dataset"])
            model_create.i_create_a_model(self)
            model_create.the_model_is_finished_in_less_than(
                self, example["wait_model"])
            prediction_create.i_create_a_prediction(
                self, example["input_data"])
            prediction_create.the_prediction_is(
                self, example["objective_id"], example["prediction"])

    def test_scenario3(self):
        """
            Scenario 3: Successfully creating a prediction from inline data source:
                Given I create a data source from inline data slurped from "<data>"
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a model
                And I wait until the model is ready less than <model_wait> secs
                When I create a prediction for "<input_data>"
                Then the prediction for "<objective_id>" is "<prediction>"
        """
        show_doc(self.test_scenario3)
        headers = ["data", "wait_source", "wait_dataset", "wait_model",
                   "input_data", "objective_id", "prediction"]
        examples = [
            ['data/iris.csv', '10', '10', '10', '{"petal width": 0.5}',
             '000004', 'Iris-setosa']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_create_using_dict_data(
                self, example["data"])
            source_create.the_source_is_finished(self, example["wait_source"])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["wait_dataset"])
            model_create.i_create_a_model(self)
            model_create.the_model_is_finished_in_less_than(
                self, example["wait_model"])
            prediction_create.i_create_a_prediction(
                self, example["input_data"])
            prediction_create.the_prediction_is(
                self, example["objective_id"], example["prediction"])

    def test_scenario4(self):
        """
            Scenario 4: Successfully creating a centroid and the associated dataset:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a cluster
                And I wait until the cluster is ready less than <time_3> secs
                When I create a centroid for "<data_input>"
                And I check the centroid is ok
                Then the centroid is "<centroid>"
                And I create a dataset from the cluster and the centroid
                And I wait until the dataset is ready less than <time_2> secs
                And I check that the dataset is created for the cluster and the centroid
        """
        show_doc(self.test_scenario4)
        headers = ["data", "wait_source", "wait_dataset", "wait_cluster",
                   "input_data", "centroid"]
        examples = [
            ['data/diabetes.csv', '10', '20', '20',
             '{"pregnancies": 0, "plasma glucose": 118, "blood pressure": 84,'
             ' "triceps skin thickness": 47, "insulin": 230, "bmi": 45.8,'
             ' "diabetes pedigree": 0.551, "age": 31, "diabetes": "true"}',
             'Cluster 3']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(self, example["wait_source"],
                shared=example["data"])
            dataset_create.i_create_a_dataset(self, shared=example["data"])
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["wait_dataset"], shared=example["data"])
            cluster_create.i_create_a_cluster(self, shared=example["data"])
            cluster_create.the_cluster_is_finished_in_less_than(
                self, example["wait_cluster"], shared=example["data"])
            prediction_create.i_create_a_centroid(self, example["input_data"])
            prediction_create.the_centroid_is(self, example["centroid"])

    def test_scenario5(self):
        """
            Scenario 5: Successfully creating an anomaly score:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create an anomaly detector from a dataset
                And I wait until the anomaly detector is ready less than <time_3> secs
                When I create an anomaly score for "<data_input>"
                Then the anomaly score is "<score>"
        """
        show_doc(self.test_scenario5)
        headers = ["data", "wait_source", "wait_dataset", "wait_anomaly",
                   "input_data", "score"]
        examples = [
            ['data/tiny_kdd.csv', '10', '10', '100',
             '{"src_bytes": 350}', '0.92846'],
            ['data/iris_sp_chars.csv', '10', '10', '100',
             '{"pétal&width\\u0000": 300}', '0.89313']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(
                self, example["wait_source"], shared=example["data"])
            dataset_create.i_create_a_dataset(self, shared=example["data"])
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["wait_dataset"], shared=example["data"])
            anomaly_create.i_create_an_anomaly(self, shared=example["data"])
            anomaly_create.the_anomaly_is_finished_in_less_than(
                self, example["wait_anomaly"], shared=example["data"])
            prediction_create.i_create_an_anomaly_score(
                self, example["input_data"])
            prediction_create.the_anomaly_score_is(self, example["score"])

    def test_scenario6(self):
        """
            Scenario 6: Successfully creating a Topic Model:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I update the source with params "<params>"
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                When I create a Topic Model from a dataset
                Then I wait until the Topic Model is ready less than <time_3> secs
        """
        show_doc(self.test_scenario6)
        headers = ["data", "wait_source", "wait_dataset", "wait_topic",
                   "source_params"]
        examples = [
            ['data/movies.csv', '10', '10', '100',
             '{"fields": {"000007": {"optype": "items", "item_analysis":'
             ' {"separator": "$"}}, "000006": {"optype": "text"}}}']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(self, example["data"])
            source_create.the_source_is_finished(self, example["wait_source"])
            source_create.i_update_source_with(self, example["source_params"])
            source_create.the_source_is_finished(self, example["wait_source"])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["wait_dataset"])
            topic_create.i_create_a_topic_model(self)
            topic_create.the_topic_model_is_finished_in_less_than(
                self, example["wait_topic"])
