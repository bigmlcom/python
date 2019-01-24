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


""" Testing prediction creation

"""
from world import world, setup_module, teardown_module
import create_source_steps as source_create
import create_dataset_steps as dataset_create
import create_model_steps as model_create
import create_cluster_steps as cluster_create
import create_anomaly_steps as anomaly_create
import create_lda_steps as topic_create
import create_prediction_steps as prediction_create


class TestPrediction(object):

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
        print self.test_scenario1.__doc__
        examples = [
            ['data/iris.csv', '30', '30', '30', '{"petal width": 0.5}', '000004', 'Iris-setosa'],
            ['data/iris_sp_chars.csv', '30', '30', '30', '{"pétal&width\u0000": 0.5}', '000004', 'Iris-setosa']]
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
        print self.test_scenario2.__doc__
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

    def test_scenario3(self):
        """
            Scenario: Successfully creating a prediction from a asynchronous uploaded file:
                Given I create a data source uploading a "<data>" file in asynchronous mode
                And I wait until the source has been created less than <time_1> secs
                And I wait until the source is ready less than <time_2> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_3> secs
                And I create a model
                And I wait until the model is ready less than <time_4> secs
                When I create a prediction for "<data_input>"
                Then the prediction for "<objective>" is "<prediction>"

                Examples:
                | data                | time_1  | time_2 | time_3 | time_4 | data_input    | objective | prediction  |
                | ../data/iris.csv | 10      | 10     | 10     | 10     | {"petal width": 0.5} | 000004    | Iris-setosa |
        """
        print self.test_scenario3.__doc__
        examples = [
            ['data/iris.csv', '10', '10', '10', '10', '{"petal width": 0.5}', '000004', 'Iris-setosa']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file_async(self, example[0])
            source_create.the_source_has_been_created_async(self, example[1])
            source_create.the_source_is_finished(self, example[2])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[3])
            model_create.i_create_a_model(self)
            model_create.the_model_is_finished_in_less_than(self, example[4])
            prediction_create.i_create_a_prediction(self, example[5])
            prediction_create.the_prediction_is(self, example[6], example[7])


    def test_scenario4(self):
        """
            Scenario: Successfully creating a prediction from inline data source:
                Given I create a data source from inline data slurped from "<data>"
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
        """
        print self.test_scenario4.__doc__
        examples = [
            ['data/iris.csv', '10', '10', '10', '{"petal width": 0.5}', '000004', 'Iris-setosa']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_create_using_dict_data(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_model(self)
            model_create.the_model_is_finished_in_less_than(self, example[3])
            prediction_create.i_create_a_prediction(self, example[4])
            prediction_create.the_prediction_is(self, example[5], example[6])

    def test_scenario5(self):
        """
            Scenario: Successfully creating a centroid and the associated dataset:
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

                Examples:
                | data                | time_1  | time_2 | time_3 | data_input    | centroid  |
                | ../data/diabetes.csv | 10      | 20     | 20     | {"pregnancies": 0, "plasma glucose": 118, "blood pressure": 84, "triceps skin thickness": 47, "insulin": 230, "bmi": 45.8, "diabetes pedigree": 0.551, "age": 31, "diabetes": "true"} | Cluster 3 |
        """
        print self.test_scenario5.__doc__
        examples = [
            ['data/diabetes.csv', '10', '20', '20', '{"pregnancies": 0, "plasma glucose": 118, "blood pressure": 84, "triceps skin thickness": 47, "insulin": 230, "bmi": 45.8, "diabetes pedigree": 0.551, "age": 31, "diabetes": "true"}', 'Cluster 3']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            cluster_create.i_create_a_cluster(self)
            cluster_create.the_cluster_is_finished_in_less_than(self, example[3])
            prediction_create.i_create_a_centroid(self, example[4])
            prediction_create.the_centroid_is(self, example[5])

    def test_scenario6(self):
        """
            Scenario: Successfully creating an anomaly score:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create an anomaly detector from a dataset
                And I wait until the anomaly detector is ready less than <time_3> secs
                When I create an anomaly score for "<data_input>"
                Then the anomaly score is "<score>"

                Examples:
                | data                 | time_1  | time_2 | time_3 | data_input         | score  |
                | ../data/tiny_kdd.csv | 10      | 10     | 100     | {"src_bytes": 350} | 0.92618 |
                | ../data/iris_sp_chars.csv | 10      | 10     | 100     | {"pétal&width\u0000": 300} | 0.90198 |
        """
        print self.test_scenario6.__doc__
        examples = [
            ['data/tiny_kdd.csv', '10', '10', '100', '{"src_bytes": 350}', '0.92846'],
            ['data/iris_sp_chars.csv', '10', '10', '100', '{"pétal&width\u0000": 300}', '0.89313']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            anomaly_create.i_create_an_anomaly(self)
            anomaly_create.the_anomaly_is_finished_in_less_than(self, example[3])
            prediction_create.i_create_an_anomaly_score(self, example[4])
            prediction_create.the_anomaly_score_is(self, example[5])


    def test_scenario7(self):
        """
            Scenario: Successfully creating a Topic Model:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I update the source with params "<params>"
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                When I create a Topic Model from a dataset
                Then I wait until the Topic Model is ready less than <time_3> secs

                Examples:
                | data                 | time_1  | time_2 | time_3 | params
                | ../data/movies.csv | 10      | 10     | 100     | {"fields": {"genre": {"optype": "items", "item_analysis": {"separator": "$"}}, "title": {"optype": "text"}}}
        """
        print self.test_scenario7.__doc__
        examples = [
            ['data/movies.csv', '10', '10', '100', '{"fields": {"000007": {"optype": "items", "item_analysis": {"separator": "$"}}, "000006": {"optype": "text"}}}']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            source_create.i_update_source_with(self, data=example[4])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            topic_create.i_create_a_topic_model(self)
            topic_create.the_topic_model_is_finished_in_less_than(self, example[3])
