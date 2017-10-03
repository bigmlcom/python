# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015-2017 BigML
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
        show_doc(self.test_scenario1, examples)
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

    def test_scenario2(self):
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
        """
        examples = [
            ['data/iris.csv', '20', '20', '30', '{"summary_fields": ["sepal width"]}', '{"petal length": 1, "petal width": 1, "sepal length": 1, "species": "Iris-setosa"}', 'Cluster 2', '1.16436', '{"petal length": 1, "petal width": 1, "sepal length": 1, "species": "Iris-setosa"}'],
            ['data/iris.csv', '20', '20', '30', '{"default_numeric_value": "zero"}', '{"petal length": 1}', 'Cluster 4', '1.41215', '{"petal length": 1, "petal width": 0, "sepal length": 0, "sepal width": 0, "species": ""}']]
        show_doc(self.test_scenario2, examples)
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


    def test_scenario3(self):
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

        """
        examples = [
            ['data/tiny_kdd.csv', '20', '20', '30', '{"000020": 255.0, "000004": 183.0, "000016": 4.0, "000024": 0.04, "000025": 0.01, "000026": 0.0, "000019": 0.25, "000017": 4.0, "000018": 0.25, "00001e": 0.0, "000005": 8654.0, "000009": "0", "000023": 0.01, "00001f": 123.0}', '0.69802']]
        show_doc(self.test_scenario3, examples)
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


    def test_scenario4(self):
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
        examples = [
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false, "language": "en"}}}}', '{"Type": "ham", "Message": "Mobile call"}', '[0.01878, 0.00388, 0.00388, 0.00388, 0.20313, 0.47315, 0.00574, 0.05695, 0.00388, 0.19382, 0.00388, 0.02902]'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false, "language": "en"}}}}', '{"Type": "ham", "Message": "Go until jurong point, crazy.. Available only in bugis n great world la e buffet... Cine there got amore wat..."}', '[0.00263, 0.01083, 0.00831, 0.06004, 0.33701, 0.00263, 0.01209, 0.44553, 0.0531, 0.00326, 0.06193, 0.00263]']]
        show_doc(self.test_scenario4, examples)
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


    def test_scenario5(self):
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

        """
        examples = [
            ['data/groceries.csv', '20', '20', '30', '{"fields": {"00000": {"optype": "text", "term_analysis": {"token_mode": "all", "language": "en"}}}}', 'data/associations/association_set.json', '{"field1": "cat food"}']]
        show_doc(self.test_scenario5, examples)

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


    def test_scenario6(self):
        """
            Scenario: Successfully comparing predictions for ensembles:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create an ensemble with "<params>"
                And I wait until the ensemble is ready less than <time_3> secs
                And I create a local ensemble
                When I create a prediction for "<data_input>"
                Then the prediction for "<objective>" is "<prediction>"
                And I create a local prediction for "<data_input>"
                Then the local prediction is "<prediction>"

                Examples:
                | data             | time_1  | time_2 | time_3 | data_input                             | objective | prediction  | params

            ['data/iris.csv', '10', '10', '120', '{"petal width": 0.5}', '000004', 'Iris-versicolor', '{"number_of_models": 5}'],
            ['data/iris.csv', '10', '10', '120', '{"petal length": 6, "petal width": 2}', '000004', 'Iris-virginica', '{"number_of_models": 5}'],
            ['data/iris.csv', '10', '10', '120', '{"petal length": 4, "petal width": 1.5}', '000004', 'Iris-versicolor', '{"number_of_models": 5}'],
            ['data/grades.csv', '10', '10', '120', '{"Midterm": 20}', '000005', 46.261364, '{"number_of_models": 5}'],
            ['data/iris.csv', '10', '10', '120', '{"petal width": 0.5}', '000004', 'Iris-setosa', '{"boosting": {"iterations": 5}, "number_of_models": 5}'],
            ['data/iris.csv', '10', '10', '120', '{"petal length": 6, "petal width": 2}', '000004', 'Iris-virginica', '{"boosting": {"iterations": 5}, "number_of_models": 5}'],
            ['data/iris.csv', '10', '10', '120', '{"petal length": 4, "petal width": 1.5}', '000004', 'Iris-versicolor', '{"boosting": {"iterations": 5}, "number_of_models": 5}'],


        """
        examples = [
            ['data/iris_unbalanced.csv', '10', '10', '120', '{"petal width": 4}', '000004', 'Iris-virginica', '{"boosting": {"iterations": 5}, "number_of_models": 5}'],
            ['data/grades.csv', '10', '10', '120', '{"Midterm": 20}', '000005', 61.61036, '{"boosting": {"iterations": 5}, "number_of_models": 5}']]
        show_doc(self.test_scenario6, examples)

        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            ensemble_create.i_create_an_ensemble_with_params(self, example[7])
            ensemble_create.the_ensemble_is_finished_in_less_than(self, example[3])
            ensemble_create.create_local_ensemble(self)
            prediction_create.i_create_an_ensemble_prediction(self, example[4])
            prediction_create.the_prediction_is(self, example[5], example[6])
            prediction_compare.i_create_a_local_ensemble_prediction(self, example[4])
            prediction_compare.the_local_prediction_is(self, example[6])


    def test_scenario7(self):
        """
            Scenario: Successfully comparing predictions for ensembles with proportional missing strategy:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create an esemble with "<params>"
                And I wait until the ensemble is ready less than <time_3> secs
                And I create a local ensemble
                When I create a proportional missing strategy prediction for "<data_input>"
                Then the prediction for "<objective>" is "<prediction>"
                And the confidence for the prediction is "<confidence>"
                And I create a proportional missing strategy local prediction for "<data_input>"
                Then the local prediction is "<prediction>"
                And the local prediction's confidence is "<confidence>"

                Examples:
                | data               | time_1  | time_2 | time_3 | data_input           | objective | prediction     | confidence | params

        """
        examples = [
            ['data/iris.csv', '10', '10', '50', '{}', '000004', 'Iris-virginica', '0.33784', '{"boosting": {"iterations": 5}}'],
            ['data/iris.csv', '10', '10', '50', '{}', '000004', 'Iris-versicolor', '0.3174', '{"number_of_models": 5}'],
            ['data/grades.csv', '10', '10', '50', '{}', '000005', '70.505792', '30.7161', '{"number_of_models": 5}'],
            ['data/grades.csv', '10', '10', '50', '{"Midterm": 20}', '000005', '45.4573', '29.58403', '{"number_of_models": 5}'],
            ['data/grades.csv', '10', '10', '50', '{"Midterm": 20, "Tutorial": 90, "TakeHome": 100}', '000005', '42.814', '31.51804', '{"number_of_models": 5}']]
        show_doc(self.test_scenario7, examples)

        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            ensemble_create.i_create_an_ensemble_with_params(self, example[8])
            ensemble_create.the_ensemble_is_finished_in_less_than(self, example[3])
            ensemble_create.create_local_ensemble(self)
            prediction_create.i_create_an_ensemble_proportional_prediction(self, example[4])
            prediction_create.the_prediction_is(self, example[5], example[6])
            prediction_create.the_confidence_is(self, example[7])
            prediction_create.create_local_ensemble_proportional_prediction_with_confidence(self, example[4])
            prediction_compare.the_local_ensemble_prediction_is(self, example[6])
            prediction_compare.the_local_prediction_confidence_is(self, example[7])

    def test_scenario8(self):
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
            ['data/iris_missing2.csv', '10', '50', '30000', '{}', '000004', 'Iris-setosa', '{}'],
            ['data/spam.csv', '10', '50', '30000', '{}', '000000', 'ham', '{}']]
        show_doc(self.test_scenario8, examples)

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
