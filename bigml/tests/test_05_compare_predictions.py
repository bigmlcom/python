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


""" Comparing remote and local predictions

"""
from world import world, setup_module, teardown_module
import create_source_steps as source_create
import create_dataset_steps as dataset_create
import create_model_steps as model_create
import create_association_steps as association_create
import create_cluster_steps as cluster_create
import create_anomaly_steps as anomaly_create
import create_prediction_steps as prediction_create
import compare_predictions_steps as prediction_compare
import create_lda_steps as topic_create


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
            Scenario: Successfully comparing predictions:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a model
                And I wait until the model is ready less than <time_3> secs
                And I create a local model
                When I create a prediction for "<data_input>"
                Then the prediction for "<objective>" is "<prediction>"
                And I create a local prediction for "<data_input>"
                Then the local prediction is "<prediction>"

                Examples:
                | data             | time_1  | time_2 | time_3 | data_input                             | objective | prediction  |
                | ../data/iris.csv | 10      | 10     | 10     | {"petal width": 0.5}                   | 000004    | Iris-setosa |
                | ../data/iris.csv | 10      | 10     | 10     | {"petal length": 6, "petal width": 2}  | 000004    | Iris-virginica |
                | ../data/iris.csv | 10      | 10     | 10     | {"petal length": 4, "petal width": 1.5}| 000004    | Iris-versicolor |
                | ../data/iris_sp_chars.csv | 10      | 10     | 10     | {"pétal.length": 4, "pétal&width\u0000": 1.5}| 000004    | Iris-versicolor |

        """
        print self.test_scenario1.__doc__
        examples = [
            ['data/iris.csv', '10', '10', '10', '{"petal width": 0.5}', '000004', 'Iris-setosa'],
            ['data/iris.csv', '10', '10', '10', '{"petal length": 6, "petal width": 2}', '000004', 'Iris-virginica'],
            ['data/iris.csv', '10', '10', '10', '{"petal length": 4, "petal width": 1.5}', '000004', 'Iris-versicolor'],
            ['data/iris_sp_chars.csv', '10', '10', '10', '{"pétal.length": 4, "pétal&width\u0000": 1.5}', '000004', 'Iris-versicolor']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_model(self)
            model_create.the_model_is_finished_in_less_than(self, example[3])
            prediction_compare.i_create_a_local_model(self)
            prediction_create.i_create_a_prediction(self, example[4])
            prediction_create.the_prediction_is(self, example[5], example[6])
            prediction_compare.i_create_a_local_prediction(self, example[4])
            prediction_compare.the_local_prediction_is(self, example[6])

    def test_scenario2(self):
        """
            Scenario: Successfully comparing predictions with text options:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I update the source with params "<options>"
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a model
                And I wait until the model is ready less than <time_3> secs
                And I create a local model
                When I create a prediction for "<data_input>"
                Then the prediction for "<objective>" is "<prediction>"
                And I create a local prediction for "<data_input>"
                Then the local prediction is "<prediction>"

                Examples:
                | data             | time_1  | time_2 | time_3 | options | data_input                             | objective | prediction  |
                | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false, "language": "en"}}}} |{"Message": "Mobile call"}             | 000000    | ham    |
                | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false, "language": "en"}}}} |{"Message": "A normal message"}        | 000000    | ham     |
                | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": false, "use_stopwords": false, "language": "en"}}}} |{"Message": "Mobile calls"}          | 000000    | spam   |
                | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": false, "use_stopwords": false, "language": "en"}}}} |{"Message": "A normal message"}       | 000000    | ham     |
                | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": true, "use_stopwords": true, "language": "en"}}}} |{"Message": "Mobile call"}            | 000000    | spam    |
                | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": true, "use_stopwords": true, "language": "en"}}}} |{"Message": "A normal message"}       | 000000    | ham     |
                | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"token_mode": "full_terms_only", "language": "en"}}}} |{"Message": "FREE for 1st week! No1 Nokia tone 4 ur mob every week just txt NOKIA to 87077 Get txting and tell ur mates. zed POBox 36504 W45WQ norm150p/tone 16+"}       | 000000    | spam     |
                | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"token_mode": "full_terms_only", "language": "en"}}}} |{"Message": "Ok"}       | 000000    | ham     |
                | ../data/movies.csv | 20      | 20     | 30     | {"fields": {"000007": {"optype": "items", "item_analysis": {"separator": "$"}}}} |{"genres": "Adventure$Action", "timestamp": 993906291, "occupation": "K-12 student"}'| 000009| 3.93064
                | ../data/text_missing.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"token_mode": "all", "language": "en"}}, {"000000": {"optype": "text", "term_analysis": {"token_mode": "all", "language": "en"}}}} |{}       | 000003 | paperwork     |


        """
        print self.test_scenario2.__doc__
        examples = [
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false, "language": "en"}}}}', '{"Message": "Mobile call"}', '000000', 'ham'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false, "language": "en"}}}}', '{"Message": "A normal message"}', '000000', 'ham'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": false, "use_stopwords": false, "language": "en"}}}}', '{"Message": "Mobile calls"}', '000000', 'spam'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": false, "use_stopwords": false, "language": "en"}}}}', '{"Message": "A normal message"}', '000000', 'ham'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": true, "use_stopwords": true, "language": "en"}}}}', '{"Message": "Mobile call"}', '000000', 'spam'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": true, "use_stopwords": true, "language": "en"}}}}', '{"Message": "A normal message"}', '000000', 'ham'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"token_mode": "full_terms_only", "language": "en"}}}}', '{"Message": "FREE for 1st week! No1 Nokia tone 4 ur mob every week just txt NOKIA to 87077 Get txting and tell ur mates. zed POBox 36504 W45WQ norm150p/tone 16+"}', '000000', 'spam'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"token_mode": "full_terms_only", "language": "en"}}}}', '{"Message": "Ok"}', '000000', 'ham'],
            ['data/movies.csv', '20', '20', '30', '{"fields": {"000007": {"optype": "items", "item_analysis": {"separator": "$"}}}}', '{"genres": "Adventure$Action", "timestamp": 993906291, "occupation": "K-12 student"}', '000009', '3.93064'],
            ['data/text_missing.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"token_mode": "all", "language": "en"}}, "000000": {"optype": "text", "term_analysis": {"token_mode": "all", "language": "en"}}}}', '{}', "000003", 'swap']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            source_create.i_update_source_with(self, example[4])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_model(self)
            model_create.the_model_is_finished_in_less_than(self, example[3])
            prediction_compare.i_create_a_local_model(self)
            prediction_create.i_create_a_prediction(self, example[5])
            prediction_create.the_prediction_is(self, example[6], example[7])
            prediction_compare.i_create_a_local_prediction(self, example[5])
            prediction_compare.the_local_prediction_is(self, example[7])


    def test_scenario3(self):
        """
            Scenario: Successfully comparing predictions with proportional missing strategy:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a model
                And I wait until the model is ready less than <time_3> secs
                And I create a local model
                When I create a proportional missing strategy prediction for "<data_input>"
                Then the prediction for "<objective>" is "<prediction>"
                And the confidence for the prediction is "<confidence>"
                And I create a proportional missing strategy local prediction for "<data_input>"
                Then the local prediction is "<prediction>"
                And the local prediction's confidence is "<confidence>"

                Examples:
                | data               | time_1  | time_2 | time_3 | data_input           | objective | prediction     | confidence |
                | ../data/iris.csv   | 10      | 10     | 10     | {}                   | 000004    | Iris-setosa    | 0.2629     |
                | ../data/grades.csv | 10      | 10     | 10     | {}                   | 000005    | 68.62224       | 27.5358    |
                | ../data/grades.csv | 10      | 10     | 10     | {"Midterm": 20}      | 000005    | 46.69889      | 37.27594297134128   |
                | ../data/grades.csv | 10      | 10     | 10     | {"Midterm": 20, "Tutorial": 90, "TakeHome": 100}     | 000005    | 28.06      | 24.86634   |

        """
        print self.test_scenario3.__doc__
        examples = [
            ['data/iris.csv', '10', '10', '10', '{}', '000004', 'Iris-setosa', '0.2629'],
            ['data/grades.csv', '10', '10', '10', '{}', '000005', '68.62224', '27.5358'],
            ['data/grades.csv', '10', '10', '10', '{"Midterm": 20}', '000005', '40.46667', '37.27594297134128'],
            ['data/grades.csv', '10', '10', '10', '{"Midterm": 20, "Tutorial": 90, "TakeHome": 100}', '000005', '28.06', '24.86634']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_model(self)
            model_create.the_model_is_finished_in_less_than(self, example[3])
            prediction_compare.i_create_a_local_model(self)
            prediction_create.i_create_a_proportional_prediction(self, example[4])
            prediction_create.the_prediction_is(self, example[5], example[6])
            prediction_compare.i_create_a_proportional_local_prediction(self, example[4])
            prediction_compare.the_local_prediction_is(self, example[6])


    def test_scenario4(self):
        """
            Scenario: Successfully comparing centroids with or without text options:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I update the source with params "<options>"
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a cluster
                And I wait until the cluster is ready less than <time_3> secs
                And I create a local cluster
                When I create a centroid for "<data_input>"
                Then the centroid is "<centroid>" with distance "<distance>"
                And I create a local centroid for "<data_input>"
                Then the local centroid is "<centroid>" with distance "<distance>"

                Examples headers:
                | data             | time_1  | time_2 | time_3 | options | data_input                            | centroid  | distance |

        """
        print self.test_scenario4.__doc__
        examples = [
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false, "language": "en"}}}}', '{"Type": "ham", "Message": "Mobile call"}', 'Cluster 7', '0.36637'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false}}}}', '{"Type": "ham", "Message": "A normal message"}', 'Cluster 0', '0.5'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": false, "use_stopwords": false, "language": "en"}}}}', '{"Type": "ham", "Message": "Mobile calls"}', 'Cluster 0', '0.5'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": false, "use_stopwords": false, "language": "en"}}}}', '{"Type": "ham", "Message": "A normal message"}', 'Cluster 0', '0.5'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": true, "use_stopwords": true, "language": "en"}}}}', '{"Type": "ham", "Message": "Mobile call"}', 'Cluster 0', '0.5'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": true, "use_stopwords": true, "language": "en"}}}}', '{"Type": "ham", "Message": "A normal message"}', 'Cluster 1', '0.36637'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"token_mode": "full_terms_only", "language": "en"}}}}', '{"Type": "ham", "Message": "FREE for 1st week! No1 Nokia tone 4 ur mob every week just txt NOKIA to 87077 Get txting and tell ur mates. zed POBox 36504 W45WQ norm150p/tone 16+"}', 'Cluster 0', '0.5'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"token_mode": "full_terms_only", "language": "en"}}}}', '{"Type": "ham", "Message": "Ok"}', 'Cluster 0', '0.478833312167'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false, "language": "en"}}}}', '{"Type": "", "Message": ""}', 'Cluster 1', '0.5'],
            ['data/diabetes.csv', '20', '20', '30', '{"fields": {}}', '{"pregnancies": 0, "plasma glucose": 118, "blood pressure": 84, "triceps skin thickness": 47, "insulin": 230, "bmi": 45.8, "diabetes pedigree": 0.551, "age": 31, "diabetes": "true"}', 'Cluster 3', '0.5033378686559257'],
            ['data/diabetes.csv', '20', '20', '30', '{"fields": {}}', '{"pregnancies": 0, "plasma glucose": 118, "blood pressure": 84, "triceps skin thickness": 47, "insulin": 230, "bmi": 45.8, "diabetes pedigree": 0.551, "age": 31, "diabetes": true}', 'Cluster 3', '0.5033378686559257'],
            ['data/iris_sp_chars.csv', '20', '20', '30', '{"fields": {}}', '{"pétal.length":1, "pétal&width\u0000": 2, "sépal.length":1, "sépal&width": 2, "spécies": "Iris-setosa"}', 'Cluster 7', '0.8752380218327035'],
            ['data/movies.csv', '20', '20', '30', '{"fields": {"000007": {"optype": "items", "item_analysis": {"separator": "$"}}}}', '{"gender": "Female", "age_range": "18-24", "genres": "Adventure$Action", "timestamp": 993906291, "occupation": "K-12 student", "zipcode": 59583, "rating": 3}', 'Cluster 1', '0.7294650227133437']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            source_create.i_update_source_with(self, example[4])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            cluster_create.i_create_a_cluster(self)
            cluster_create.the_cluster_is_finished_in_less_than(self, example[3])
            prediction_compare.i_create_a_local_cluster(self)
            prediction_create.i_create_a_centroid(self, example[5])
            prediction_create.the_centroid_is_with_distance(self, example[6], example[7])
            prediction_compare.i_create_a_local_centroid(self, example[5])
            prediction_compare.the_local_centroid_is(self, example[6], example[7])

    def test_scenario5(self):
        """
            Scenario: Successfully comparing centroids with configuration options:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a cluster with options "<options>"
                And I wait until the cluster is ready less than <time_3> secs
                And I create a local cluster
                When I create a centroid for "<data_input>"
                Then the centroid is "<centroid>" with distance "<distance>"
                And I create a local centroid for "<data_input>"
                Then the local centroid is "<centroid>" with distance "<distance>"

                Examples:
                | data             | time_1  | time_2 | time_3 | options | data_input                            | centroid  | distance | full_data_input
                | ../data/iris.csv | 20      | 20     | 30     | {"summary_fields": ["sepal width"]} |{"petal length": 1, "petal width": 1, "sepal length": 1, "species": "Iris-setosa"}             | Cluster 2   | 1.1643644909783857   |
        """
        print self.test_scenario5.__doc__
        examples = [
            ['data/iris.csv', '20', '20', '30', '{"summary_fields": ["sepal width"]}', '{"petal length": 1, "petal width": 1, "sepal length": 1, "species": "Iris-setosa"}', 'Cluster 2', '1.16436', '{"petal length": 1, "petal width": 1, "sepal length": 1, "species": "Iris-setosa"}'],
            ['data/iris.csv', '20', '20', '30', '{"default_numeric_value": "zero"}', '{"petal length": 1}', 'Cluster 4', '1.41215', '{"petal length": 1, "petal width": 0, "sepal length": 0, "sepal width": 0, "species": ""}']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            cluster_create.i_create_a_cluster_with_options(self, example[4])
            cluster_create.the_cluster_is_finished_in_less_than(self, example[3])
            prediction_compare.i_create_a_local_cluster(self)
            prediction_create.i_create_a_centroid(self, example[8])
            prediction_create.the_centroid_is_with_distance(self, example[6], example[7])
            prediction_compare.i_create_a_local_centroid(self, example[5])
            prediction_compare.the_local_centroid_is(self, example[6], example[7])

    def test_scenario6(self):
        """
            Scenario: Successfully comparing predictions with proportional missing strategy for missing_splits models:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a model with missing splits
                And I wait until the model is ready less than <time_3> secs
                And I create a local model
                When I create a proportional missing strategy prediction for "<data_input>"
                Then the prediction for "<objective>" is "<prediction>"
                And the confidence for the prediction is "<confidence>"
                And I create a proportional missing strategy local prediction for "<data_input>"
                Then the local prediction is "<prediction>"
                And the local prediction's confidence is "<confidence>"

                Examples:
                | data               | time_1  | time_2 | time_3 | data_input           | objective | prediction     | confidence |
                | ../data/iris_missing2.csv   | 10      | 10     | 10     | {"petal width": 1}             | 000004    | Iris-setosa    | 0.8064     |
                | ../data/iris_missing2.csv   | 10      | 10     | 10     | {"petal width": 1, "petal length": 4}             | 000004    | Iris-versicolor    | 0.7847     |

        """
        print self.test_scenario6.__doc__
        examples = [
            ['data/iris_missing2.csv', '10', '10', '10', '{"petal width": 1}', '000004', 'Iris-setosa', '0.8064'],
            ['data/iris_missing2.csv', '10', '10', '10', '{"petal width": 1, "petal length": 4}', '000004', 'Iris-versicolor', '0.7847']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_model_with_missing_splits(self)
            model_create.the_model_is_finished_in_less_than(self, example[3])
            prediction_compare.i_create_a_local_model(self)
            prediction_create.i_create_a_proportional_prediction(self, example[4])
            prediction_create.the_prediction_is(self, example[5], example[6])
            prediction_create.the_confidence_is(self, example[7])
            prediction_compare.i_create_a_proportional_local_prediction(self, example[4])
            prediction_compare.the_local_prediction_is(self, example[6])
            prediction_compare.the_local_prediction_confidence_is(self, example[7])

    def test_scenario7(self):
        """
            Scenario: Successfully comparing scores from anomaly detectors:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create an anomaly detector
                And I wait until the anomaly detector is ready less than <time_3> secs
                And I create a local anomaly detector
                When I create an anomaly score for "<data_input>"
                Then the anomaly score is "<score>"
                And I create a local anomaly score for "<data_input>"
                Then the local anomaly score is "<score>"

                Examples:
                | data                 | time_1  | time_2 | time_3 | data_input                            | score  |
                | ../data/tiny_kdd.csv | 20      | 20     | 30     |{"000020": 255.0, "000004": 183.0, "000016": 4.0, "000024": 0.04, "000025": 0.01, "000026": 0.0, "000019": 0.25, "000017": 4.0, "000018": 0.25, "00001e": 0.0, "000005": 8654.0, "000009": "0", "000023": 0.01, "00001f": 123.0}            | 0.69802  |

        """
        print self.test_scenario7.__doc__
        examples = [
            ['data/tiny_kdd.csv', '20', '20', '30', '{"000020": 255.0, "000004": 183.0, "000016": 4.0, "000024": 0.04, "000025": 0.01, "000026": 0.0, "000019": 0.25, "000017": 4.0, "000018": 0.25, "00001e": 0.0, "000005": 8654.0, "000009": "0", "000023": 0.01, "00001f": 123.0}', '0.69802']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            anomaly_create.i_create_an_anomaly(self)
            anomaly_create.the_anomaly_is_finished_in_less_than(self, example[3])
            prediction_compare.i_create_a_local_anomaly(self)
            prediction_create.i_create_an_anomaly_score(self, example[4])
            prediction_create.the_anomaly_score_is(self, example[5])
            prediction_compare.i_create_a_local_anomaly_score(self, example[4])
            prediction_compare.the_local_anomaly_score_is(self, example[5])

    def test_scenario8(self):
        """
            Scenario: Successfully comparing logistic regression predictions:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a logistic regression model
                And I wait until the logistic regression model is ready less than <time_3> secs
                And I create a local logistic regression model
                When I create a logistic regression prediction for "<data_input>"
                Then the logistic regression prediction is "<prediction>"
                And I create a local logistic regression prediction for "<data_input>"
                Then the local logistic regression prediction is "<prediction>"

                Examples:
                | data             | time_1  | time_2 | time_3 | data_input                                                                                 | prediction  |
                | ../data/iris.csv | 10      | 10     | 10     | {"petal width": 0.5, "petal length": 0.5, "sepal width": 0.5, "sepal length": 0.5}         | 'Iris-versicolor' |
                | ../data/iris.csv | 10      | 10     | 10     | {"petal width": 2, "petal length": 6, "sepal width": 0.5, "sepal length": 0.5}             | Iris-virginica |
                | ../data/iris.csv | 10      | 10     | 10     | {"petal width": 1.5, "petal length": 4, "sepal width": 0.5, "sepal length": 0.5}           | Iris-versicolor |
                | ../data/iris.csv | 10      | 10     | 10     | {"petal width": 1}                                                                         | Iris-versicolor |
                | ../data/iris_sp_chars.csv | 10      | 10     | 10     | {"pétal.length": 4, "pétal&width\u0000": 1.5, "sépal&width": 0.5, "sépal.length": 0.5}| Iris-virginica |
                | ../data/price.csv | 10      | 10     | 10     | {"Price": 1200}| Product1 |

        """
        print self.test_scenario8.__doc__
        examples = [
            ['data/iris.csv', '10', '10', '50', '{"petal width": 0.5, "petal length": 0.5, "sepal width": 0.5, "sepal length": 0.5}', 'Iris-versicolor'],
            ['data/iris.csv', '10', '10', '50', '{"petal width": 2, "petal length": 6, "sepal width": 0.5, "sepal length": 0.5}', 'Iris-versicolor'],
            ['data/iris.csv', '10', '10', '50', '{"petal width": 1.5, "petal length": 4, "sepal width": 0.5, "sepal length": 0.5}', 'Iris-versicolor'],
            ['data/iris.csv', '10', '10', '50', '{"petal length": 1}', 'Iris-setosa'],
            ['data/iris_sp_chars.csv', '10', '10', '50', '{"pétal.length": 4, "pétal&width\u0000": 1.5, "sépal&width": 0.5, "sépal.length": 0.5}', 'Iris-versicolor'],
            ['data/price.csv', '10', '10', '50', '{"Price": 1200}', 'Product1']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_logistic_model(self)
            model_create.the_logistic_model_is_finished_in_less_than(self, example[3])
            prediction_compare.i_create_a_local_logistic_model(self)
            prediction_create.i_create_a_logistic_prediction(self, example[4])
            prediction_create.the_logistic_prediction_is(self, example[5])
            prediction_compare.i_create_a_local_prediction(self, example[4])
            prediction_compare.the_local_prediction_is(self, example[5])


    def test_scenario9(self):
        """
            Scenario: Successfully comparing predictions with text options:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I update the source with params "<options>"
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a logistic regression model
                And I wait until the logistic regression model is ready less than <time_3> secs
                And I create a local logistic regression model
                When I create a logistic regression prediction for "<data_input>"
                Then the logistic regression prediction is "<prediction>"
                And I create a local logistic regression prediction for "<data_input>"
                Then the local logistic regression prediction is "<prediction>"

                Examples:
                | data             | time_1  | time_2 | time_3 | options | data_input                             | prediction  |
                | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false, "language": "en"}}}} |{"Message": "Mobile call"}             | ham    |
                | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false, "language": "en"}}}} |{"Message": "A normal message"}        | ham     |
                | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": false, "use_stopwords": false, "language": "en"}}}} |{"Message": "Mobile calls"}          | ham   |
                | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": false, "use_stopwords": false, "language": "en"}}}} |{"Message": "A normal message"}       | ham     |
                | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": true, "use_stopwords": true, "language": "en"}}}} |{"Message": "Mobile call"}             | ham    |
                | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": true, "use_stopwords": true, "language": "en"}}}} |{"Message": "A normal message"}       | ham     |
                | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"token_mode": "full_terms_only", "language": "en"}}}} |{"Message": "FREE for 1st week! No1 Nokia tone 4 ur mob every week just txt NOKIA to 87077 Get txting and tell ur mates. zed POBox 36504 W45WQ norm150p/tone 16+"}       | ham     |
                | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"token_mode": "full_terms_only", "language": "en"}}}} |{"Message": "Ok"}       | ham     |


        """
        print self.test_scenario9.__doc__
        examples = [
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false, "language": "en"}}}}', '{"Message": "Mobile call"}', 'ham'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false, "language": "en"}}}}', '{"Message": "A normal message"}', 'ham'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": false, "use_stopwords": false, "language": "en"}}}}', '{"Message": "Mobile calls"}', 'ham'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": false, "use_stopwords": false, "language": "en"}}}}', '{"Message": "A normal message"}', 'ham'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": true, "use_stopwords": true, "language": "en"}}}}', '{"Message": "Mobile call"}', 'ham'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": true, "use_stopwords": true, "language": "en"}}}}', '{"Message": "A normal message"}', 'ham'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"token_mode": "full_terms_only", "language": "en"}}}}', '{"Message": "FREE for 1st week! No1 Nokia tone 4 ur mob every week just txt NOKIA to 87077 Get txting and tell ur mates. zed POBox 36504 W45WQ norm150p/tone 16+"}', 'ham'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"token_mode": "full_terms_only", "language": "en"}}}}', '{"Message": "Ok"}', 'ham']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            source_create.i_update_source_with(self, example[4])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_logistic_model(self)
            model_create.the_logistic_model_is_finished_in_less_than(self, example[3])
            prediction_compare.i_create_a_local_logistic_model(self)
            prediction_create.i_create_a_logistic_prediction(self, example[5])
            prediction_create.the_logistic_prediction_is(self, example[6])
            prediction_compare.i_create_a_local_prediction(self, example[5])
            prediction_compare.the_local_prediction_is(self, example[6])

    def test_scenario10(self):
        """
            Scenario: Successfully comparing predictions with text options:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I update the source with params "<options>"
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a logistic regression model with objective "<objective>"
                And I wait until the logistic regression model is ready less than <time_3> secs
                And I create a local logistic regression model
                When I create a logistic regression prediction for "<data_input>"
                Then the logistic regression prediction is "<prediction>"
                And the logistic regression probability for the prediction is "<probability>"
                And I create a local logistic regression prediction for "<data_input>"
                Then the local logistic regression prediction is "<prediction>"
                And the local logistic regression probability for the prediction is "<probability>"

                Examples:
                | data             | time_1  | time_2 | objective | time_3 | options | data_input                             | prediction  | probability
                | ../data/spam.csv | 20      | 20     | 000002 | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"token_mode": "full_terms_only", "language": "en"}}}} |{"Message": "A normal message"}       | ham     | 0.7645

        """
        print self.test_scenario10.__doc__
        examples = [
            ['data/spam.csv', '20', '20', '80', '{"fields": {"000001": {"optype": "text", "term_analysis": {"token_mode": "full_terms_only", "language": "en"}}}}', '{"Message": "A normal message"}', 'ham', 0.9169, "000000"],
            ['data/spam.csv', '20', '20', '80', '{"fields": {"000001": {"optype": "text", "term_analysis": {"token_mode": "all", "language": "en"}}}}', '{"Message": "mobile"}', 'ham', 0.815, "000000"],
            ['data/movies.csv', '20', '20', '80', '{"fields": {"000007": {"optype": "items", "item_analysis": {"separator": "$"}}}}', '{"gender": "Female", "genres": "Adventure$Action", "timestamp": 993906291, "occupation": "K-12 student", "zipcode": 59583, "rating": 3}', 'Under 18', '0.8393', '000002']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            source_create.i_update_source_with(self, example[4])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_logistic_model_with_objective_and_parms(self, example[8])
            model_create.the_logistic_model_is_finished_in_less_than(self, example[3])
            prediction_compare.i_create_a_local_logistic_model(self)
            prediction_create.i_create_a_logistic_prediction(self, example[5])
            prediction_create.the_logistic_prediction_is(self, example[6])
            prediction_create.the_logistic_probability_is(self, example[7])
            prediction_compare.i_create_a_local_prediction(self, example[5])
            prediction_compare.the_local_prediction_is(self, example[6])
            prediction_compare.the_local_probability_is(self, example[7])

    def test_scenario11(self):
        """
            Scenario: Successfully comparing predictions with text options and proportional missing strategy:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I update the source with params "<options>"
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a model
                And I wait until the model is ready less than <time_3> secs
                And I create a local model
                When I create a proportional missing strategy prediction for "<data_input>"
                Then the prediction for "<objective>" is "<prediction>"
                And I create a proportional missing strategy local prediction for "<data_input>"
                Then the local prediction is "<prediction>"

                Examples:
                | ../data/text_missing.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"token_mode": "all", "language": "en"}}, {"000000": {"optype": "text", "term_analysis": {"token_mode": "all", "language": "en"}}}} |{}       | paperwork     |

        """
        print self.test_scenario11.__doc__
        examples = [
            ['data/text_missing.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"token_mode": "all", "language": "en"}}, "000000": {"optype": "text", "term_analysis": {"token_mode": "all", "language": "en"}}}}', '{}', "000003",'swap'],
            ['data/text_missing.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"token_mode": "all", "language": "en"}}, "000000": {"optype": "text", "term_analysis": {"token_mode": "all", "language": "en"}}}}', '{"category1": "a"}', "000003",'paperwork']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            source_create.i_update_source_with(self, example[4])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_model(self)
            model_create.the_model_is_finished_in_less_than(self, example[3])
            prediction_compare.i_create_a_local_model(self)
            prediction_create.i_create_a_proportional_prediction(self, example[5])
            prediction_create.the_prediction_is(self, example[6], example[7])
            prediction_compare.i_create_a_proportional_local_prediction(self, example[5])
            prediction_compare.the_local_prediction_is(self, example[7])


    def test_scenario12(self):
        """
            Scenario: Successfully comparing predictions with text options:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I update the source with params "<options>"
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a logistic regression model with objective "<objective>" and parms "<parms>"
                And I wait until the logistic regression model is ready less than <time_3> secs
                And I create a local logistic regression model
                When I create a logistic regression prediction for "<data_input>"
                Then the logistic regression prediction is "<prediction>"
                And the logistic regression probability for the prediction is "<probability>"
                And I create a local logistic regression prediction for "<data_input>"
                Then the local logistic regression prediction is "<prediction>"
                And the local logistic regression probability for the prediction is "<probability>"

        """
        print self.test_scenario12.__doc__
        examples = [
            ['data/iris.csv', '20', '20', '30', '{"fields": {"000000": {"optype": "categorical"}}}', '{"species": "Iris-setosa"}', '5.0', 0.0394, "000000", '{"field_codings": [{"field": "species", "coding": "dummy", "dummy_class": "Iris-setosa"}]}'],
            ['data/iris.csv', '20', '20', '30', '{"fields": {"000000": {"optype": "categorical"}}}', '{"species": "Iris-setosa"}', '5.0', 0.0511, "000000", '{"balance_fields": false, "field_codings": [{"field": "species", "coding": "contrast", "coefficients": [[1, 2, -1, -2]]}]}'],
            ['data/iris.csv', '20', '20', '30', '{"fields": {"000000": {"optype": "categorical"}}}', '{"species": "Iris-setosa"}', '5.0', 0.0511, "000000", '{"balance_fields": false, "field_codings": [{"field": "species", "coding": "other", "coefficients": [[1, 2, -1, -2]]}]}'],
            ['data/iris.csv', '20', '20', '30', '{"fields": {"000000": {"optype": "categorical"}}}', '{"species": "Iris-setosa"}', '5.0', 0.0417, "000000", '{"bias": false}']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            source_create.i_update_source_with(self, example[4])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_logistic_model_with_objective_and_parms(self, example[8], example[9])
            model_create.the_logistic_model_is_finished_in_less_than(self, example[3])
            prediction_compare.i_create_a_local_logistic_model(self)
            prediction_create.i_create_a_logistic_prediction(self, example[5])
            prediction_create.the_logistic_prediction_is(self, example[6])
            prediction_create.the_logistic_probability_is(self, example[7])
            prediction_compare.i_create_a_local_prediction(self, example[5])
            prediction_compare.the_local_prediction_is(self, example[6])
            prediction_compare.the_local_probability_is(self, example[7])

    def test_scenario13(self):
        """
            Scenario: Successfully comparing predictions with proportional missing strategy and balanced models:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a balanced model
                And I wait until the model is ready less than <time_3> secs
                And I create a local model
                When I create a proportional missing strategy prediction for "<data_input>"
                Then the prediction for "<objective>" is "<prediction>"
                And the confidence for the prediction is "<confidence>"
                And I create a proportional missing strategy local prediction for "<data_input>"
                Then the local prediction is "<prediction>"
                And the local prediction's confidence is "<confidence>"

                Examples:
                | data               | time_1  | time_2 | time_3 | data_input           | objective | prediction     | confidence |
                | ../data/iris.csv   | 10      | 10     | 10     | {}                   | 000004    | Iris-setosa    | 0.25284     |
                | ../data/iris.csv   | 10      | 10     | 10     | {"petal length":1, "sepal length":1, "petal width": 1, "sepal width": 1}  | 000004    | Iris-setosa    | 0.7575     |

        """
        print self.test_scenario13.__doc__
        examples = [
            ['data/iris_unbalanced.csv', '10', '10', '10', '{}', '000004', 'Iris-setosa', '0.25284'],
            ['data/iris_unbalanced.csv', '10', '10', '10', '{"petal length":1, "sepal length":1, "petal width": 1, "sepal width": 1}', '000004', 'Iris-setosa', '0.7575']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_balanced_model(self)
            model_create.the_model_is_finished_in_less_than(self, example[3])
            prediction_compare.i_create_a_local_model(self)
            prediction_create.i_create_a_proportional_prediction(self, example[4])
            prediction_create.the_prediction_is(self, example[5], example[6])
            prediction_compare.i_create_a_proportional_local_prediction(self, example[4])
            prediction_compare.the_local_prediction_is(self, example[6])
            prediction_create.the_confidence_is(self, example[7])
            prediction_compare.the_local_prediction_confidence_is(self, example[7])

    def test_scenario14(self):
        """
            Scenario: Successfully comparing predictions for logistic regression with balance_fields:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I update the source with params "<options>"
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a logistic regression model with objective "<objective>" and flags
                And I wait until the logistic regression model is ready less than <time_3> secs
                And I create a local logistic regression model
                When I create a logistic regression prediction for "<data_input>"
                Then the logistic regression prediction is "<prediction>"
                And the logistic regression probability for the prediction is "<probability>"
                And I create a local logistic regression prediction for "<data_input>"
                Then the local logistic regression prediction is "<prediction>"
                And the local logistic regression probability for the prediction is "<probability>"

                Examples:
                | data               | time_1  | time_2 | objective | time_3 | options | data_input                             | prediction  | probability
                | ../data/movies.csv | 20      | 20     | 000009    | 30     | {"fields": {'000000': {'name': 'user_id', 'optype': 'numeric'},
                                                                                           '000001': {'name': 'gender', 'optype': 'categorical'},
                                                                                           '000002': {'name': 'age_range', 'optype': 'categorical'},
                                                                                           '000003': {'name': 'occupation', 'optype': 'categorical'},
                                                                                           '000004': {'name': 'zipcode', 'optype': 'numeric'},
                                                                                           '000005': {'name': 'movie_id', 'optype': 'numeric'},
                                                                                           '000006': {'name': 'title', 'optype': 'text'},
                                                                                           '000007': {'name': 'genres', 'optype': 'items',
                                                                                                      'item_analysis': {'separator': "$"}},
                                                                                           '000008': {'name': 'timestamp', 'optype': 'numeric'},
                                                                                           '000009': {'name': 'rating', 'optype': 'categorical'}},
                                                                               "source_parser": {"separator": ";"}}
                |{"timestamp": "999999999"}       | 5     | 0.3231 | '{"balance_fields": true}'

        """
        print self.test_scenario14.__doc__
        examples = [
            ['data/movies.csv', '20', '20', '80', '{"fields": {"000000": {"name": "user_id", "optype": "numeric"},'
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
                                                  '"source_parser": {"separator": ";"}}', '{"timestamp": "999999999"}', '4', 0.3231, "000009", '{"balance_fields": false}'],
            ['data/movies.csv', '20', '20', '80', '{"fields": {"000000": {"name": "user_id", "optype": "numeric"},'
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
                                                  '"source_parser": {"separator": ";"}}', '{"timestamp": "999999999"}', '4', 0.2622, "000009", '{"normalize": true}'],
            ['data/movies.csv', '20', '20', '80', '{"fields": {"000000": {"name": "user_id", "optype": "numeric"},'
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
                                                  '"source_parser": {"separator": ";"}}', '{"timestamp": "999999999"}', '4', 0.2622, "000009", '{"balance_fields": true, "normalize": true}']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            source_create.i_update_source_with(self, example[4])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_logistic_model_with_objective_and_parms(self, example[8], example[9])
            model_create.the_logistic_model_is_finished_in_less_than(self, example[3])
            prediction_compare.i_create_a_local_logistic_model(self)
            prediction_create.i_create_a_logistic_prediction(self, example[5])
            prediction_create.the_logistic_prediction_is(self, example[6])
            prediction_create.the_logistic_probability_is(self, example[7])
            prediction_compare.i_create_a_local_prediction(self, example[5])
            prediction_compare.the_local_prediction_is(self, example[6])
            prediction_compare.the_local_probability_is(self, example[7])


    def test_scenario15(self):
        """
            Scenario: Successfully comparing topic distributions:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I update the source with params "<options>"
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a topic model
                And I wait until the topic model is ready less than <time_3> secs
                And I create a local topic model
                When I create a topic distribution for "<data_input>"
                Then the topic distribution is "<topic_distribution>"
                And I create a local topic distribution for "<data_input>"
                Then the local topic distribution is "<topic_distribution>"

                Examples headers:
                | data             | time_1  | time_2 | time_3 | options | data_input                            | topic distribution  |

        """
        print self.test_scenario15.__doc__
        examples = [
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false, "language": "en"}}}}', '{"Type": "ham", "Message": "Mobile call"}', '[0.01878, 0.00388, 0.00388, 0.00388, 0.20313, 0.47315, 0.00574, 0.05695, 0.00388, 0.19382, 0.00388, 0.02902]'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false, "language": "en"}}}}', '{"Type": "ham", "Message": "Go until jurong point, crazy.. Available only in bugis n great world la e buffet... Cine there got amore wat..."}', '[0.00263, 0.01083, 0.00831, 0.06004, 0.33701, 0.00263, 0.01209, 0.44553, 0.0531, 0.00326, 0.06193, 0.00263]']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            source_create.i_update_source_with(self, example[4])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            topic_create.i_create_a_topic_model(self)
            topic_create.the_topic_model_is_finished_in_less_than(self, example[3])
            prediction_compare.i_create_a_local_topic_model(self)
            topic_create.i_create_a_local_topic_distribution(self, example[5])
            prediction_compare.the_local_topic_distribution_is(self, example[6])
            topic_create.i_create_a_topic_distribution(self, example[5])
            prediction_compare.the_topic_distribution_is(self, example[6])

    def test_scenario16(self):
        """
            Scenario: Successfully comparing association sets:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I update the source with params "<options>"
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a model
                And I wait until the association is ready less than <time_3> secs
                And I create a local association
                When I create an association set for "<data_input>"
                Then the association set is like the contents of "<association_set_file>"
                And I create a local association set for "<data_input>"
                Then the local association set is like the contents of "<association_set_file>"

                Examples:
                | ../data/groceries.csv | 20      | 20     | 30     | {"fields": {"000000": {"optype": "text", "term_analysis": {"token_mode": "all", "language": "en"}}}} | association_set.json       | {"field1": "cat food"}     |

        """
        print self.test_scenario16.__doc__
        examples = [
            ['data/groceries.csv', '20', '20', '30', '{"fields": {"00000": {"optype": "text", "term_analysis": {"token_mode": "all", "language": "en"}}}}', 'data/associations/association_set.json', '{"field1": "cat food"}']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            source_create.i_update_source_with(self, example[4])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            association_create.i_create_an_association_from_dataset(self)
            association_create.the_association_is_finished_in_less_than(self, example[3])
            prediction_compare.i_create_a_local_association(self)
            prediction_create.i_create_an_association_set(self, example[6])
            prediction_compare.the_association_set_is_like_file(self, example[5])
            prediction_compare.i_create_a_local_association_set(self, example[6])
            prediction_compare.the_local_association_set_is_like_file(self, example[5])
