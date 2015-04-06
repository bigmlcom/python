# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015 BigML
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
import create_cluster_steps as cluster_create
import create_anomaly_steps as anomaly_create
import create_prediction_steps as prediction_create
import compare_predictions_steps as prediction_compare


class TestComparePrediction(object):
        
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
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"token_mode": "full_terms_only", "language": "en"}}}}', '{"Message": "Ok"}', '000000', 'ham']]
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
            ['data/grades.csv', '10', '10', '10', '{"Midterm": 20}', '000005', '46.69889', '37.27594297134128'],
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

                Examples:
                | data             | time_1  | time_2 | time_3 | options | data_input                            | centroid  | distance |
                | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false, "language": "en"}}}} |{"Type": "ham", "Message": "Mobile call"}             | Cluster 7   | 0.341886116992   |
                | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false}}}} |{"Type": "ham", "Message": "A normal message"}        | Cluster 0   | 0.5     |
                | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": false, "use_stopwords": false, "language": "en"}}}} |{"Type": "ham", "Message": "Mobile calls"}            | Cluster 0     | 0.5    |
                | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": false, "use_stopwords": false, "language": "en"}}}} |{"Type": "ham", "Message": "A normal message"}       | Cluster 0     | 0.5     |
                | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": true, "use_stopwords": true, "language": "en"}}}} |{"Type": "ham", "Message": "Mobile call"}               | Cluster 4      | 0.382148869802   |
                | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": true, "use_stopwords": true, "language": "en"}}}} |{"Type": "ham", "Message": "A normal message"}       | Cluster 4     | 0.382148869802   |
                | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"token_mode": "full_terms_only", "language": "en"}}}} |{"Type": "ham", "Message": "FREE for 1st week! No1 Nokia tone 4 ur mob every week just txt NOKIA to 87077 Get txting and tell ur mates. zed POBox 36504 W45WQ norm150p/tone 16+"}       | Cluster 1      | 0.5     |
                | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"token_mode": "full_terms_only", "language": "en"}}}} |{"Type": "ham", "Message": "Ok"}       | Cluster 1    | 0.478833312167     |
                | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false, "language": "en"}}}} |{"Type": "", "Message": ""}             | Cluster 0   | 0.707106781187   |
                | ../data/diabetes.csv | 20      | 20     | 30     | {"fields": {}} |{"pregnancies": 0, "plasma glucose": 118, "blood pressure": 84, "triceps skin thickness": 47, "insulin": 230, "bmi": 45.8, "diabetes pedigree": 0.551, "age": 31, "diabetes": "true"}       | Cluster 6    | 0.486471379368     |
                | ../data/iris_sp_chars.csv | 20      | 20     | 30     | {"fields": {}} |{"pétal.length":1, "pétal&width\u0000": 2, "sépal.length":1, "sépal&width": 2, "spécies": "Iris-setosa"}       | Cluster 7    | 0.757736964835     |

        """
        print self.test_scenario4.__doc__
        examples = [
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false, "language": "en"}}}}', '{"Type": "ham", "Message": "Mobile call"}', 'Cluster 7', '0.341886116992'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false}}}}', '{"Type": "ham", "Message": "A normal message"}', 'Cluster 0', '0.5'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": false, "use_stopwords": false, "language": "en"}}}}', '{"Type": "ham", "Message": "Mobile calls"}', 'Cluster 0', '0.5'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": false, "use_stopwords": false, "language": "en"}}}}', '{"Type": "ham", "Message": "A normal message"}', 'Cluster 0', '0.5'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": true, "use_stopwords": true, "language": "en"}}}}', '{"Type": "ham", "Message": "Mobile call"}', 'Cluster 4', '0.382148869802'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": true, "use_stopwords": true, "language": "en"}}}}', '{"Type": "ham", "Message": "A normal message"}', 'Cluster 4', '0.382148869802'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"token_mode": "full_terms_only", "language": "en"}}}}', '{"Type": "ham", "Message": "FREE for 1st week! No1 Nokia tone 4 ur mob every week just txt NOKIA to 87077 Get txting and tell ur mates. zed POBox 36504 W45WQ norm150p/tone 16+"}', 'Cluster 1', '0.5'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"token_mode": "full_terms_only", "language": "en"}}}}', '{"Type": "ham", "Message": "Ok"}', 'Cluster 1', '0.478833312167'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false, "language": "en"}}}}', '{"Type": "", "Message": ""}', 'Cluster 0', '0.707106781187'],
            ['data/diabetes.csv', '20', '20', '30', '{"fields": {}}', '{"pregnancies": 0, "plasma glucose": 118, "blood pressure": 84, "triceps skin thickness": 47, "insulin": 230, "bmi": 45.8, "diabetes pedigree": 0.551, "age": 31, "diabetes": "true"}', 'Cluster 6', '0.486471379368'],
            ['data/iris_sp_chars.csv', '20', '20', '30', '{"fields": {}}', '{"pétal.length":1, "pétal&width\u0000": 2, "sépal.length":1, "sépal&width": 2, "spécies": "Iris-setosa"}', 'Cluster 7', '0.757736964835']]
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
            Scenario: Successfully comparing centroids with summary fields:
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
                | data             | time_1  | time_2 | time_3 | options | data_input                            | centroid  | distance |
                | ../data/iris.csv | 20      | 20     | 30     | {"summary_fields": ["sepal width"]} |{"petal length": 1, "petal width": 1, "sepal length": 1, "species": "Iris-setosa"}             | Cluster 6   | 0.713698082167   |
        """
        print self.test_scenario5.__doc__
        examples = [
            ['data/iris.csv', '20', '20', '30', '{"summary_fields": ["sepal width"]}', '{"petal length": 1, "petal width": 1, "sepal length": 1, "species": "Iris-setosa"}', 'Cluster 6', '0.713698082167']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            cluster_create.i_create_a_cluster_with_options(self, example[4])
            cluster_create.the_cluster_is_finished_in_less_than(self, example[3])
            prediction_compare.i_create_a_local_cluster(self)
            prediction_create.i_create_a_centroid(self, example[5])
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
                | ../data/tiny_kdd.csv | 20      | 20     | 30     |{"000020": 255.0, "000004": 183.0, "000016": 4.0, "000024": 0.04, "000025": 0.01, "000026": 0.0, "000019": 0.25, "000017": 4.0, "000018": 0.25, "00001e": 0.0, "000005": 8654.0, "000009": "0", "000023": 0.01, "00001f": 123.0}            | 0.68782  |  

        """
        print self.test_scenario7.__doc__
        examples = [
            ['data/tiny_kdd.csv', '20', '20', '30', '{"000020": 255.0, "000004": 183.0, "000016": 4.0, "000024": 0.04, "000025": 0.01, "000026": 0.0, "000019": 0.25, "000017": 4.0, "000018": 0.25, "00001e": 0.0, "000005": 8654.0, "000009": "0", "000023": 0.01, "00001f": 123.0}', '0.68782']]
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
