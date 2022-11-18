# -*- coding: utf-8 -*-
#
# Copyright 2015-2022 BigML
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

from .world import world, setup_module, teardown_module, show_doc, \
    show_method, delete_local
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create
from . import create_model_steps as model_create
from . import create_ensemble_steps as ensemble_create
from . import create_linear_steps as linear_create
from . import create_association_steps as association_create
from . import create_cluster_steps as cluster_create
from . import create_anomaly_steps as anomaly_create
from . import create_prediction_steps as prediction_create
from . import compare_predictions_steps as prediction_compare
from . import create_lda_steps as topic_create



class TestComparePrediction(object):

    def setup_method(self):
        """
            Debug information
        """
        print("\n-------------------\nTests in: %s\n" % __name__)

    def teardown_method(self):
        """
            Debug information
        """
        delete_local()
        print("\nEnd of tests in: %s\n-------------------\n" % __name__)

    def test_scenario1(self):
        """
            Scenario: Successfully comparing centroids with or without text options:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I update the source with params "<source_conf>"
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a cluster
                And I wait until the cluster is ready less than <model_wait> secs
                And I create a local cluster
                When I create a centroid for "<input_data>"
                Then the centroid is "<centroid>" with distance "<distance>"
                And I create a local centroid for "<input_data>"
                Then the local centroid is "<centroid>" with distance "<distance>"

        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "source_conf", "input_data", "centroid", "distance"]
        examples = [
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false, "language": "en"}}}}', '{"Type": "ham", "Message": "Mobile call"}', 'Cluster 0', '0.25'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false}}}}', '{"Type": "ham", "Message": "A normal message"}', 'Cluster 0', '0.5'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": false, "use_stopwords": false, "language": "en"}}}}', '{"Type": "ham", "Message": "Mobile calls"}', 'Cluster 0', '0.5'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": false, "use_stopwords": false, "language": "en"}}}}', '{"Type": "ham", "Message": "A normal message"}', 'Cluster 0', '0.5'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": true, "use_stopwords": true, "language": "en"}}}}', '{"Type": "ham", "Message": "Mobile call"}', 'Cluster 1', '0.34189'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": true, "use_stopwords": true, "language": "en"}}}}', '{"Type": "ham", "Message": "A normal message"}', 'Cluster 0', '0.5'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"token_mode": "full_terms_only", "language": "en"}}}}', '{"Type": "ham", "Message": "FREE for 1st week! No1 Nokia tone 4 ur mob every week just txt NOKIA to 87077 Get txting and tell ur mates. zed POBox 36504 W45WQ norm150p/tone 16+"}', 'Cluster 0', '0.5'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"token_mode": "full_terms_only", "language": "en"}}}}', '{"Type": "ham", "Message": "Ok"}', 'Cluster 0', '0.478833312167'],
            ['data/spam.csv', '20', '20', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false, "language": "en"}}}}', '{"Type": "", "Message": ""}', 'Cluster 6', '0.5'],
            ['data/diabetes.csv', '20', '20', '30', '{"fields": {}}', '{"pregnancies": 0, "plasma glucose": 118, "blood pressure": 84, "triceps skin thickness": 47, "insulin": 230, "bmi": 45.8, "diabetes pedigree": 0.551, "age": 31, "diabetes": "true"}', 'Cluster 3', '0.5033378686559257'],
            ['data/diabetes.csv', '20', '20', '30', '{"fields": {}}', '{"pregnancies": 0, "plasma glucose": 118, "blood pressure": 84, "triceps skin thickness": 47, "insulin": 230, "bmi": 45.8, "diabetes pedigree": 0.551, "age": 31, "diabetes": true}', 'Cluster 3', '0.5033378686559257'],
            ['data/iris_sp_chars.csv', '20', '20', '30', '{"fields": {}}', '{"pétal.length":1, "pétal&width\\u0000": 2, "sépal.length":1, "sépal&width": 2, "spécies": "Iris-setosa"}', 'Cluster 7', '0.8752380218327035'],
            ['data/movies.csv', '20', '20', '30', '{"fields": {"000007": {"optype": "items", "item_analysis": {"separator": "$"}}}}', '{"gender": "Female", "age_range": "18-24", "genres": "Adventure$Action", "timestamp": 993906291, "occupation": "K-12 student", "zipcode": 59583, "rating": 3}', 'Cluster 3', '0.62852']]
        show_doc(self.test_scenario1)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(self, example["data"])
            source_create.the_source_is_finished(self, example["source_wait"])
            source_create.i_update_source_with(self, example["source_conf"])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"])
            cluster_create.i_create_a_cluster(self)
            cluster_create.the_cluster_is_finished_in_less_than(
                self, example["model_wait"])
            prediction_compare.i_create_a_local_cluster(self)
            prediction_create.i_create_a_centroid(
                self, example["input_data"])
            prediction_create.the_centroid_is_with_distance(
                self, example["centroid"], example["distance"])
            prediction_compare.i_create_a_local_centroid(
                self, example["input_data"])
            prediction_compare.the_local_centroid_is(
                self, example["centroid"], example["distance"])

    def test_scenario2(self):
        """
            Scenario: Successfully comparing centroids with configuration options:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a cluster with options "<options>"
                And I wait until the cluster is ready less than <model_wait> secs
                And I create a local cluster
                When I create a centroid for "<input_data>"
                Then the centroid is "<centroid>" with distance "<distance>"
                And I create a local centroid for "<input_data_l>"
                Then the local centroid is "<centroid>" with distance "<distance>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "model_conf", "input_data_l", "centroid", "distance",
                   "input_data"]
        examples = [
            ['data/iris.csv', '30', '30', '30',
             '{"summary_fields": ["sepal width"]}',
             '{"petal length": 1, "petal width": 1, "sepal length": 1, '
             '"species": "Iris-setosa"}', 'Cluster 2', '1.16436',
             '{"petal length": 1, "petal width": 1, "sepal length": 1, '
             '"species": "Iris-setosa"}'],
            ['data/iris.csv', '20', '20', '30',
             '{"default_numeric_value": "zero"}',
             '{"petal length": 1}', 'Cluster 4', '1.41215',
             '{"petal length": 1, "petal width": 0, "sepal length": 0, '
             '"sepal width": 0, "species": ""}']]
        show_doc(self.test_scenario2)
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
            cluster_create.i_create_a_cluster_with_options(
                self, example["model_conf"])
            cluster_create.the_cluster_is_finished_in_less_than(
                self, example["model_wait"])
            prediction_compare.i_create_a_local_cluster(self)
            prediction_create.i_create_a_centroid(
                self, example["input_data"])
            prediction_create.the_centroid_is_with_distance(
                self, example["centroid"], example["distance"])
            prediction_compare.i_create_a_local_centroid(
                self, example["input_data_l"])
            prediction_compare.the_local_centroid_is(
                self, example["centroid"], example["distance"])


    def test_scenario3(self):
        """
            Scenario: Successfully comparing scores from anomaly detectors:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create an anomaly detector with params "<model_conf>"
                And I wait until the anomaly detector is ready less than <model_wait> secs
                And I create a local anomaly detector
                When I create an anomaly score for "<input_data>"
                Then the anomaly score is "<score>"
                And I create a local anomaly score for "<input_data>"
                Then the local anomaly score is "<score>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "input_data", "score", "model_conf"]
        examples = [
            ['data/tiny_kdd.csv', '30', '30', '80',
             '{"000020": 255.0, "000004": 183.0, "000016": 4.0, '
             '"000024": 0.04, "000025": 0.01, "000026": 0.0, "000019": 0.25, '
             '"000017": 4.0, "000018": 0.25, "00001e": 0.0, "000005": 8654.0, '
             '"000009": "0", "000023": 0.01, "00001f": 123.0}', '0.69802',
             '{}'],
            ['data/repeat_iris.csv', '30', '30', '80',
             '{"sepal width":3.5, "petal width": 0.2, "sepal length": 5.1, '
             '"petal length": 1.4, "species": "Iris-setosa"}', '0.50',
             '{"normalize_repeats": false}'],
            ['data/repeat_iris.csv', '30', '30', '80',
             '{"sepal width":3.5, "petal width": 0.2, "sepal length": 5.1, '
             '"petal length": 1.4, "species": "Iris-setosa"}', '0.36692',
             '{"normalize_repeats": true}'],
            ['data/repeat_iris.csv', '30', '30', '80',
             '{"sepal width":3.2, "petal width": 1.5, "sepal length": 6.4, '
             '"petal length": 4.5, "species": "Iris-versicolor"}', '0.76131',
             '{"normalize_repeats": true}']]
        show_doc(self.test_scenario3)
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
            anomaly_create.i_create_an_anomaly_with_params(
                self, example["model_conf"])
            anomaly_create.the_anomaly_is_finished_in_less_than(
                self, example["model_wait"])
            prediction_compare.i_create_a_local_anomaly(self)
            prediction_create.i_create_an_anomaly_score(
                self, example["input_data"])
            prediction_create.the_anomaly_score_is(self, example["score"])
            prediction_compare.i_create_a_local_anomaly_score(
                self, example["input_data"])
            prediction_compare.the_local_anomaly_score_is(
                self, example["score"])

    def test_scenario4(self):
        """
            Scenario: Successfully comparing topic distributions:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I update the source with params "<source_conf>"
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a topic model
                And I wait until the topic model is ready less than <model_wait> secs
                And I create a local topic model
                When I create a topic distribution for "<input_data>"
                Then the topic distribution is "<topic_distribution>"
                And I create a local topic distribution for "<input_data>"
                Then the local topic distribution is "<topic_distribution>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "source_conf", "input_data", "topic_distribution"]
        examples = [
            ['data/spam.csv', '30', '30', '80',
             '{"fields": {"000001": {"optype": "text", "term_analysis": '
             '{"case_sensitive": true, "stem_words": true, '
             '"use_stopwords": false, "language": "en"}}}}',
             '{"Type": "ham", "Message": "Mobile call"}',
             '[0.51133, 0.00388, 0.00574, 0.00388, 0.00388, 0.00388, '
             '0.00388, 0.00388, 0.00388, 0.00388, 0.00388, 0.44801]'],
            ['data/spam.csv', '30', '30', '30',
             '{"fields": {"000001": {"optype": "text", "term_analysis": '
             '{"case_sensitive": true, "stem_words": true, '
             '"use_stopwords": false, "language": "en"}}}}',
             '{"Type": "ham", "Message": "Go until jurong point, crazy.. '
             'Available only in bugis n great world la e buffet... Cine '
             'there got amore wat..."}',
             '[0.39188, 0.00643, 0.00264, 0.00643, 0.08112, 0.00264, '
             '0.37352, 0.0115, 0.00707, 0.00327, 0.00264, 0.11086]']]
        show_doc(self.test_scenario4)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(self, example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"])
            source_create.i_update_source_with(self, example["source_conf"])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"])
            topic_create.i_create_a_topic_model(self)
            topic_create.the_topic_model_is_finished_in_less_than(
                self, example["model_wait"])
            prediction_compare.i_create_a_local_topic_model(self)
            topic_create.i_create_a_topic_distribution(
                self, example["input_data"])
            prediction_compare.the_topic_distribution_is(
                self, example["topic_distribution"])
            topic_create.i_create_a_local_topic_distribution(
                self, example["input_data"])
            prediction_compare.the_local_topic_distribution_is(
                self, example["topic_distribution"])

    def test_scenario5(self):
        """
            Scenario: Successfully comparing association sets:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I update the source with params "<source_conf>"
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a model
                And I wait until the association is ready less than <model_wait> secs
                And I create a local association
                When I create an association set for "<input_data>"
                Then the association set is like the contents of "<association_set_file>"
                And I create a local association set for "<input_data>"
                Then the local association set is like the contents of "<association_set_file>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "source_conf", "association_set_file", "input_data"]
        examples = [
            ['data/groceries.csv', '20', '20', '50', '{"fields": {"00000": {"optype": "text", "term_analysis": {"token_mode": "all", "language": "en"}}}}', 'data/associations/association_set.json', '{"field1": "cat food"}']]
        show_doc(self.test_scenario5)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(self, example["data"])
            source_create.the_source_is_finished(self, example["source_wait"])
            source_create.i_update_source_with(self, example["source_conf"])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"])
            association_create.i_create_an_association_from_dataset(self)
            association_create.the_association_is_finished_in_less_than(
                self, example["model_wait"])
            prediction_compare.i_create_a_local_association(self)
            prediction_create.i_create_an_association_set(
                self, example["input_data"])
            prediction_compare.the_association_set_is_like_file(
                self, example["association_set_file"])
            prediction_compare.i_create_a_local_association_set(
                self, example["input_data"])
            prediction_compare.the_local_association_set_is_like_file(
                self, example["association_set_file"])


    def test_scenario6(self):
        """
            Scenario: Successfully comparing predictions for ensembles:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create an ensemble with "<model_conf>"
                And I wait until the ensemble is ready less than <model_wait> secs
                And I create a local ensemble
                When I create a prediction for "<input_data>"
                Then the prediction for "<objective_id>" is "<prediction>"
                And I create a local prediction for "<input_data>"
                Then the local prediction is "<prediction>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "input_data", "objective_id", "prediction", "model_conf"]
        examples = [
            ['data/iris_unbalanced.csv', '30', '30', '120',
             '{"petal width": 4}', '000004', 'Iris-virginica',
             '{"boosting": {"iterations": 5}, "number_of_models": 5}'],
            ['data/grades.csv', '30', '30', '120', '{"Midterm": 20}',
             '000005', 61.61036,
             '{"boosting": {"iterations": 5}, "number_of_models": 5}']]
        show_doc(self.test_scenario6)
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
            ensemble_create.i_create_an_ensemble_with_params(
                self, example["model_conf"])
            ensemble_create.the_ensemble_is_finished_in_less_than(
                self, example["model_wait"])
            ensemble_create.create_local_ensemble(self)
            prediction_create.i_create_an_ensemble_prediction(
                self, example["input_data"])
            prediction_create.the_prediction_is(
                self, example["objective_id"], example["prediction"])
            prediction_compare.i_create_a_local_ensemble_prediction(
                self, example["input_data"])
            prediction_compare.the_local_prediction_is(
                self, example["prediction"])

    def test_scenario7(self):
        """
            Scenario: Successfully comparing predictions for ensembles with proportional missing strategy:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create an esemble with "<params>"
                And I wait until the ensemble is ready less than <model_wait> secs
                And I create a local ensemble
                When I create a proportional missing strategy prediction for "<input_data>" with <"operating">
                Then the prediction for "<objective_id>" is "<prediction>"
                And the confidence for the prediction is "<confidence>"
                And I create a proportional missing strategy local prediction for "<data_input>" with <"operating">
                Then the local prediction is "<prediction>"
                And the local prediction's confidence is "<confidence>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "input_data", "objective_id", "prediction", "confidence",
                   "model_conf", "operating"]
        examples = [
            ['data/iris.csv', '30', '30', '80', '{}', '000004', 'Iris-virginica', '0.33784', '{"boosting": {"iterations": 5}}', {}],
            ['data/iris.csv', '30', '30', '80', '{}', '000004', 'Iris-versicolor', '0.27261', '{"number_of_models": 5"}', {"operating_kind": "confidence"}],
            ['data/grades.csv', '30', '30', '50', '{}', '000005', '70.505792', '30.7161', '{"number_of_models": 5}', {}]]

        show_doc(self.test_scenario7)
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
            ensemble_create.i_create_an_ensemble_with_params(
                self, example["model_conf"])
            ensemble_create.the_ensemble_is_finished_in_less_than(
                self, example["model_wait"])
            ensemble_create.create_local_ensemble(self)
            prediction_create.i_create_an_ensemble_proportional_prediction(
                self, example["input_data"])
            prediction_create.the_prediction_is(
                self, example["objective_id"], example["prediction"])
            prediction_create.the_confidence_is(self, example["confidence"])
            prediction_create.create_local_ensemble_proportional_prediction_with_confidence(
                self, example["input_data"], example["operating"])
            prediction_compare.the_local_ensemble_prediction_is(
                self, example["prediction"])
            prediction_compare.the_local_prediction_confidence_is(
                self, example["confidence"])

    def test_scenario7b(self):
        """
            Scenario: Successfully comparing predictions for ensembles with proportional missing strategy:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create an esemble with "<model_conf>"
                And I wait until the ensemble is ready less than <model_wait> secs
                And I create a local ensemble
                When I create a proportional missing strategy prediction for "<input_data>" with <"operating">
                Then the prediction for "<objective_id>" is "<prediction>"
                And the confidence for the prediction is "<confidence>"
                And I create a proportional missing strategy local prediction for "<input_data>" with <"operating">
                Then the local prediction is "<prediction>"
                And the local prediction's confidence is "<confidence>"

        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "input_data", "objective_id", "prediction", "confidence",
                   "model_conf", "operating"]
        examples = [
            ['data/grades.csv', '30', '30', '80',
             '{"Midterm": 20}', '000005', '54.82214', '25.89672',
             '{"number_of_models": 5}', {"operating_kind": "confidence"}],
            ['data/grades.csv', '30', '30', '80', '{"Midterm": 20}',
             '000005', '45.4573', '29.58403', '{"number_of_models": 5}', {}],
            ['data/grades.csv', '30', '30', '80',
             '{"Midterm": 20, "Tutorial": 90, "TakeHome": 100}', '000005',
             '42.814', '31.51804', '{"number_of_models": 5}', {}]]
        show_doc(self.test_scenario7b)
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
            ensemble_create.i_create_an_ensemble_with_params(
                self, example["model_conf"])
            ensemble_create.the_ensemble_is_finished_in_less_than(
                self, example["model_wait"])
            ensemble_create.create_local_ensemble(self)
            prediction_create.i_create_an_ensemble_proportional_prediction(
                self, example["input_data"], example["operating"])
            prediction_create.the_prediction_is(
                self, example["objective_id"], example["prediction"])
            prediction_create.the_confidence_is(self, example["confidence"])
            prediction_create.create_local_ensemble_proportional_prediction_with_confidence(
                self, example["input_data"], example["operating"])
            prediction_compare.the_local_ensemble_prediction_is(
                self, example["prediction"])
            prediction_compare.the_local_prediction_confidence_is(
                self, example["confidence"])

    def test_scenario8(self):
        """
            Scenario: Successfully comparing predictions for ensembles:
                Given I create a local ensemble predictor from "<directory>"
                And I create a local prediction for "<input_data>"
                Then the local prediction is "<prediction>"


        """
        headers = ["directory", "input_data", "prediction"]
        examples = [
            ['bigml/tests/my_ensemble', '{"petal width": 4}', 68.1258030739]]
        show_doc(self.test_scenario8)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            ensemble_create.create_local_ensemble_predictor(
                self, example["directory"])
            prediction_compare.i_create_a_local_ensemble_prediction(
                self, example["input_data"])
            prediction_compare.the_local_ensemble_prediction_is(
                self, example["prediction"])

    def test_scenario9(self):
        """
            Scenario: Successfully comparing predictions for ensembles with proportional missing strategy in a supervised model:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create an esemble with "<model_conf>"
                And I wait until the ensemble is ready less than <model_wait> secs
                And I create a local ensemble
                When I create a proportional missing strategy prediction for "<input_data>" with <"operating">
                Then the prediction for "<objective_id>" is "<prediction>"
                And the confidence for the prediction is "<confidence>"
                And I create a proportional missing strategy local prediction for "<input_data>" with <"operating">
                Then the local prediction is "<prediction>"
                And the local prediction's confidence is "<confidence>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "input_data", "objective_id", "prediction", "confidence",
                   "model_conf", "operating"]
        examples = [
            ['data/iris.csv', '10', '10', '80', '{}', '000004', 'Iris-virginica', '0.33784', '{"boosting": {"iterations": 5}}', {}],
            ['data/iris.csv', '10', '10', '80', '{}', '000004', 'Iris-versicolor', '0.27261', '{"number_of_models": 5"}', {"operating_kind": "confidence"}]]
        show_doc(self.test_scenario9)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"], shared=example["data"])
            ensemble_create.i_create_an_ensemble_with_params(
                self, example["model_conf"])
            ensemble_create.the_ensemble_is_finished_in_less_than(
                self, example["model_wait"])
            ensemble_create.create_local_supervised_ensemble(self)
            prediction_create.i_create_an_ensemble_proportional_prediction(
                self, example["input_data"], example["operating"])
            prediction_create.the_prediction_is(
                self, example["objective_id"], example["prediction"])
            prediction_create.the_confidence_is(self, example["confidence"])
            prediction_create.create_local_ensemble_proportional_prediction_with_confidence(
                self, example["input_data"], example["operating"])
            prediction_compare.the_local_ensemble_prediction_is(
                self, example["prediction"])
            prediction_compare.the_local_prediction_confidence_is(
                self, example["confidence"])

    def test_scenario10(self):
        """
            Scenario: Successfully comparing predictions for fusions:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a model with "<tag>"
                And I wait until the model is ready less than <model_wait> secs
                And I create a model with "<tag>"
                And I wait until the model is ready less than <model_wait> secs
                And I create a model with "<tag>"
                And I wait until the model is ready less than <model_wait> secs
                And I retrieve a list of remote models tagged with "<tag>"
                And I create a fusion from a list of models
                And I wait until the fusion is ready less than <model_wait> secs
                And I create a local fusion
                When I create a prediction for "<input_data>"
                Then the prediction for "<objective>" is "<prediction>"
                And I create a local prediction for "<input_data>"
                Then the local prediction is "<prediction>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait", "tag",
                   "input_data", "objective_id", "prediction"]
        examples = [
            ['data/iris_unbalanced.csv', '30', '30', '120',
             'my_fusion_tag', '{"petal width": 4}', '000004',
             'Iris-virginica'],
            ['data/grades.csv', '30', '30', '120',
             'my_fusion_tag_reg', '{"Midterm": 20}', '000005', 43.65286]]
        show_doc(self.test_scenario10)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            tag = example["tag"]
            tag_args = '{"tags":["%s"]}' % tag
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"], shared=example["data"])
            model_create.i_create_a_model_with(self, tag_args)
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            model_create.i_create_a_model_with(self, tag_args)
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            model_create.i_create_a_model_with(self, tag_args)
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            prediction_compare.i_retrieve_a_list_of_remote_models(
                self, tag)
            model_create.i_create_a_fusion(self)
            model_create.the_fusion_is_finished_in_less_than(
                self, example["model_wait"])
            prediction_compare.i_create_a_local_fusion(self)
            prediction_create.i_create_a_fusion_prediction(
                self, example["input_data"])
            prediction_create.the_prediction_is(
                self, example["objective_id"], example["prediction"])
            prediction_compare.i_create_a_local_prediction(
                self, example["input_data"])
            prediction_compare.the_local_prediction_is(
                self, example["prediction"])

    def test_scenario11(self):
        """
            Scenario: Successfully comparing predictions in operating points for fusions:
            Scenario: Successfully comparing predictions for fusions:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a model with "<tag>"
                And I wait until the model is ready less than <model_wait> secs
                And I create a model with "<tag>"
                And I wait until the model is ready less than <model_wait> secs
                And I create a model with "<tag>"
                And I wait until the model is ready less than <model_wait> secs
                And I retrieve a list of remote models tagged with "<tag>"
                And I create a fusion from a list of models
                And I wait until the fusion is ready less than <model_wait> secs
                And I create a local fusion
                When I create a prediction for "<data_input>" in "<operating_point>"
                Then the prediction for "<objective>" is "<prediction>"
                And I create a local fusion prediction for "<data_input>" in "<operating_point>"
                Then the local ensemble prediction is "<prediction>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait", "tag",
                   "input_data", "objective_id", "prediction",
                   "operating_point"]
        examples = [
            ['data/iris_unbalanced.csv', '30', '30', '120',
             'my_fusion_tag_11', '{"petal width": 4}', '000004',
             'Iris-virginica',
              {"kind": "probability", "threshold": 0.1,
               "positive_class": "Iris-setosa"}],
           ['data/iris_unbalanced.csv', '30', '30', '120',
            'my_fusion_tag_11_b', '{"petal width": 4}',
            '000004', 'Iris-virginica',
            {"kind": "probability", "threshold": 0.9,
             "positive_class": "Iris-setosa"}]]
        show_doc(self.test_scenario11)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            tag = example["tag"]
            tag_args = '{"tags":["%s"]}' % tag
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            dataset_create.i_create_a_dataset(self, shared=example["data"])
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"], shared=example["data"])
            model_create.i_create_a_model_with(self, tag_args)
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            model_create.i_create_a_model_with(self, tag_args)
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            model_create.i_create_a_model_with(self, tag_args)
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            prediction_compare.i_retrieve_a_list_of_remote_models(self, tag)
            model_create.i_create_a_fusion(self)
            model_create.the_fusion_is_finished_in_less_than(
                self, example["model_wait"])
            prediction_compare.i_create_a_local_fusion(self)
            prediction_create.i_create_a_fusion_prediction_op(
                self, example["input_data"], example["operating_point"])
            prediction_create.the_prediction_is(
                self, example["objective_id"], example["prediction"])
            prediction_compare.i_create_a_local_prediction_op(
                self, example["input_data"], example["operating_point"])
            prediction_compare.the_local_prediction_is(
                self, example["prediction"])

    def test_scenario12(self):
        """
            Scenario: Successfully comparing predictions for fusions:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a model with "<model_conf>"
                And I wait until the model is ready less than <model_wait> secs
                And I create a model with "<model_conf>"
                And I wait until the model is ready less than <model_wait> secs
                And I create a model with "<model_conf>"
                And I wait until the model is ready less than <model_wait> secs
                And I retrieve a list of remote models tagged with "<tag>"
                And I create a fusion from a list of models
                And I wait until the fusion is ready less than <model_wait> secs
                And I create a local fusion
                When I create a prediction for "<input_data>"
                Then the prediction for "<objective>" is "<prediction>"
                And I create a local prediction for "<input_data>"
                Then the local prediction is "<prediction>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "model_conf", "tag", "input_data", "objective_id",
                   "prediction"]
        tag = "my_fusion_tag_12"
        tag_reg = "my_fusion_tag_12_reg"
        examples = [
            ['data/iris_unbalanced.csv', '30', '30', '120',
             '{"tags":["%s"], "sample_rate": 0.8, "seed": "bigml"}' % tag, tag,
             '{"petal width": 4}', '000004', 'Iris-virginica'],
            ['data/grades.csv', '30', '30', '120',
             '{"tags":["%s"], "sample_rate": 0.8, "seed": "bigml"}' % tag_reg,
             tag_reg, '{"Midterm": 20}', '000005', 44.37625]]
        show_doc(self.test_scenario12)
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
            model_create.i_create_a_model_with(
                self, example["model_conf"])
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            model_create.i_create_a_model_with(
                self, example["model_conf"])
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            model_create.i_create_a_model_with(
                self, example["model_conf"])
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            prediction_compare.i_retrieve_a_list_of_remote_models(
                self, example["tag"])
            model_create.i_create_a_fusion_with_weights(self)
            model_create.the_fusion_is_finished_in_less_than(
                self, example["model_wait"])
            prediction_compare.i_create_a_local_fusion(self)
            prediction_create.i_create_a_fusion_prediction(
                self, example["input_data"])
            prediction_create.the_prediction_is(
                self, example["objective_id"], example["prediction"])
            prediction_compare.i_create_a_local_prediction(
                self, example["input_data"])
            prediction_compare.the_local_prediction_is(
                self, example["prediction"])

    def test_scenario13(self):
        """
            Scenario: Successfully comparing predictions for fusions:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <"dataset_wait"> secs
                And I create a model with "<model_conf>"
                And I wait until the model is ready less than <model_wait> secs
                And I create a model with "<model_conf>"
                And I wait until the model is ready less than <model_wait> secs
                And I create a model with "<model_conf>"
                And I wait until the model is ready less than <model_wait> secs
                And I retrieve a list of remote models tagged with "<tag>"
                And I create a fusion from a list of models
                And I wait until the fusion is ready less than <model_wait> secs
                And I create a local fusion
                When I create a prediction for "<input_data>"
                Then the prediction for "<objective>" is "<prediction>"
                And I create a local prediction for "<input_data>"
                Then the local prediction is "<prediction>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "tag", "input_data", "objective_id", "prediction"]
        examples = [
            ['data/grades.csv', '30', '30', '120', 'my_fusion_tag_lreg',
             '{"000000": 10, "000001": 10, "000002": 10, "000003": 10, '
             '"000004": 10}', '000005', 21.01712]]
        show_doc(self.test_scenario13)

        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            tag = example["tag"]
            tag_args = '{"tags":["%s"]}' % tag
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            dataset_create.i_create_a_dataset(self, shared=example["data"])
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"], shared=example["data"])
            linear_create.i_create_a_linear_regression_with_params(
                self, tag_args)
            linear_create.the_linear_regression_is_finished_in_less_than(
                self, example["model_wait"])
            prediction_compare.i_retrieve_a_list_of_remote_linear_regressions(
                self, tag)
            model_create.i_create_a_fusion(self)
            model_create.the_fusion_is_finished_in_less_than(
                self, example["model_wait"])
            prediction_compare.i_create_a_local_fusion(self)
            prediction_create.i_create_a_fusion_prediction(
                self, example["input_data"])
            prediction_create.the_prediction_is(
                self, example["objective_id"], example["prediction"])
            prediction_compare.i_create_a_local_prediction(
                self, example["input_data"])
            prediction_compare.the_local_prediction_is(
                self, example["prediction"])

    def test_scenario14(self):
        """
            Scenario: Successfully comparing predictions for ensembles:
                Given I load the full ensemble information from "<directory>"
                And I create a local ensemble from the ensemble +  models list
                And I create a local prediction for "<input_data>"
                Then the local prediction is "<prediction>"


        """
        headers = ["directory", "input_data", "prediction"]
        examples = [
            ['bigml/tests/mlflow_ensemble', '{"plasma glucose": 240}', 'true']]
        show_doc(self.test_scenario14)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            model_list = ensemble_create.load_full_ensemble(
                self, example["directory"])
            ensemble_create.create_local_ensemble_from_list(
                self, model_list)
            prediction_compare.i_create_a_local_ensemble_prediction(
                self, example["input_data"])
            prediction_compare.the_local_ensemble_prediction_is(
                self, example["prediction"])
