# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,line-too-long,attribute-defined-outside-init
#pylint: disable=locally-disabled,unused-import
#
# Copyright 2018-2025 BigML
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


""" Creating tests for building local models from files

"""
from .world import world, setup_module, teardown_module, show_doc, \
    show_method
from . import create_model_steps as model_create
from . import create_linear_steps as linear_create
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create
from . import create_ensemble_steps as ensemble_create
from . import create_anomaly_steps as anomaly_create
from . import create_time_series_steps as timeseries_create
from . import create_association_steps as association_create
from . import create_cluster_steps as cluster_create
from . import create_lda_steps as topic_create
from . import compare_predictions_steps as prediction_compare


class TestLocalFromFile:
    """Testing locally generated code"""

    def setup_method(self, method):
        """
            Debug information
        """
        self.bigml = {}
        self.bigml["method"] = method.__name__
        print("\n-------------------\nTests in: %s\n" % __name__)

    def teardown_method(self):
        """
            Debug information
        """
        print("\nEnd of tests in: %s\n-------------------\n" % __name__)
        self.bigml = {}

    def test_scenario1(self):
        """
        Scenario 1: Successfully creating a local model from an exported file:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create a model with params "<model_conf>"
            And I wait until the model is ready less than <model_wait> secs
            And I export the "<pmml>" model to "<exported_file>"
            When I create a local model from the file "<exported_file>"
            Then the model ID and the local model ID match
            And the prediction for "<input_data>" is "<prediction>"
            And the number of leaves is "<leaves#>"
        """
        show_doc(self.test_scenario1)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "pmml", "exported_file", "input_data", "prediction",
                   "model_conf", 'leaves#']
        examples = [
            ['data/iris.csv', '10', '10', '10', False,
             './tmp/model.json', {}, "Iris-setosa", '{}', 9],
            ['data/iris.csv', '10', '10', '10', False,
             './tmp/model_dft.json', {}, "Iris-versicolor",
             '{"default_numeric_value": "mean"}', 9]]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            dataset_create.i_create_a_dataset(self, shared=example["data"])
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"], shared=example["data"])
            model_create.i_create_a_model_with(self, example["model_conf"])
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            model_create.i_export_model(
                self, example["pmml"], example["exported_file"])
            model_create.i_create_local_model_from_file(
                self, example["exported_file"])
            model_create.check_model_id_local_id(self)
            model_create.local_model_prediction_is(
                self, example["input_data"], example["prediction"])
            model_create.check_leaves_number(self, example["leaves#"])

    def test_scenario2(self):
        """
        Scenario 2: Successfully creating a local ensemble from an exported file:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create an ensemble with "<params>"
            And I wait until the ensemble is ready less than <model_wait> secs
            And I export the ensemble to "<exported_file>"
            When I create a local ensemble from the file "<exported_file>"
            Then the ensemble ID and the local ensemble ID match
            And the prediction for "<input_data>" is "<prediction>"
        """
        show_doc(self.test_scenario2)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "exported_file", "input_data", "prediction",
                   "model_conf"]
        examples = [
            ['data/iris.csv', '10', '10', '50', './tmp/ensemble.json',
             {}, {'probability': 0.35714, 'prediction': 'Iris-versicolor'},
             '{}'],
            ['data/iris.csv', '10', '10', '50', './tmp/ensemble_dft.json',
             {}, {'probability': 0.98209, 'prediction': 'Iris-versicolor'},
             '{"default_numeric_value": "mean"}']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
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
            ensemble_create.i_export_ensemble(self, example["exported_file"])
            ensemble_create.i_create_local_ensemble_from_file(
                self, example["exported_file"])
            ensemble_create.check_ensemble_id_local_id(self)
            model_create.local_ensemble_prediction_is(
                self, example["input_data"], example["prediction"])

    def test_scenario3(self):
        """
        Scenario 3: Successfully creating a local logistic regression from an exported file:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <time_1> secs
            And I create a dataset
            And I wait until the dataset is ready less than <time_2> secs
            And I create a logistic regression with "<params>"
            And I wait until the logistic regression is ready less than <time_3> secs
            And I export the logistic regression to "<exported_file>"
            When I create a local logistic regression from the file "<exported_file>"
            Then the logistic regression ID and the local logistic regression ID match
            And the prediction for "<input_data>" is "<prediction>"
        """
        show_doc(self.test_scenario3)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "exported_file", "input_data", "prediction",
                   "model_conf"]
        examples = [
            ['data/iris.csv', '10', '10', '50', './tmp/logistic.json', {},
             'Iris-versicolor', '{}'],
            ['data/iris.csv', '10', '10', '50', './tmp/logistic_dft.json', {},
             'Iris-virginica', '{"default_numeric_value": "maximum"}']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            dataset_create.i_create_a_dataset(self, shared=example["data"])
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"], shared=example["data"])
            model_create.i_create_a_logistic_model_with_objective_and_parms(
                self, parms=example["model_conf"])
            model_create.the_logistic_model_is_finished_in_less_than(
                self, example["model_wait"])
            model_create.i_export_logistic_regression(
                self, example["exported_file"])
            model_create.i_create_local_logistic_regression_from_file(
                self, example["exported_file"])
            model_create.check_logistic_regression_id_local_id(self)
            model_create.local_logistic_prediction_is(
                self, example["input_data"], example["prediction"])

    def test_scenario4(self):
        """
        Scenario 4: Successfully creating a local deepnet from an exported file:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create a deepnet with "<params>"
            And I wait until the deepnet is ready less than <model_wait> secs
            And I export the deepnet to "<exported_file>"
            When I create a local deepnet from the file "<exported_file>"
            Then the deepnet ID and the local deepnet ID match
            And the prediction for "<input_data>" is "<prediction>"
        """
        show_doc(self.test_scenario4)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "exported_file", "input_data", "prediction",
                   "model_conf"]
        examples = [
            ['data/iris.csv', '10', '10', '500', './tmp/deepnet.json', {},
             'Iris-versicolor', '{}'],
            ['data/iris.csv', '10', '10', '500', './tmp/deepnet_dft.json', {},
             'Iris-versicolor', '{"default_numeric_value": "maximum"}']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            dataset_create.i_create_a_dataset(self, shared=example["data"])
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"], shared=example["data"])
            model_create.i_create_a_deepnet_with_objective_and_params(
                self, parms=example["model_conf"])
            model_create.the_deepnet_is_finished_in_less_than(
                self, example["model_wait"])
            model_create.i_export_deepnet(self, example["exported_file"])
            model_create.i_create_local_deepnet_from_file(
                self, example["exported_file"])
            model_create.check_deepnet_id_local_id(self)
            model_create.local_deepnet_prediction_is(
                self, example["input_data"], example["prediction"])

    def test_scenario5(self):
        """
        Scenario 5: Successfully creating a local cluster from an exported file:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create a cluster with "<model_conf>"
            And I wait until the cluster is ready less than <model_wait> secs
            And I export the cluster to "<exported_file>"
            When I create a local cluster from the file "<exported_file>"
            Then the cluster ID and the local cluster ID match
            And the prediction for "<input_data>" is "<prediction>"
        """
        show_doc(self.test_scenario5)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "exported_file", "input_data", "prediction",
                   "model_conf"]
        examples = [
            ['data/iris.csv', '10', '10', '500', './tmp/cluster.json',
             {"petal length": 2, "petal width": 2, "sepal length": 2,
              "sepal width": 2, "species": "Iris-setosa"},
             {'centroid_id': '000007', 'centroid_name': 'Cluster 7',
              'distance': 0.7340597799442431}, '{}'],
            ['data/iris.csv', '10', '10', '500', './tmp/cluster_dft.json', {},
             {'centroid_id': '000005', 'centroid_name': 'Cluster 5',
              'distance': 0.502695797586787},
             '{"default_numeric_value": "maximum"}']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
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
            cluster_create.i_export_cluster(self, example["exported_file"])
            cluster_create.i_create_local_cluster_from_file(
                self, example["exported_file"])
            cluster_create.check_cluster_id_local_id(self)
            model_create.local_cluster_prediction_is(
                self, example["input_data"], example["prediction"])

    def test_scenario6(self):
        """
        Scenario 6: Successfully creating a local anomaly from an exported file:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create an anomaly with "<params>"
            And I wait until the anomaly is ready less than <model_wait> secs
            And I export the anomaly to "<exported_file>"
            When I create a local anomaly from the file "<exported_file>"
            Then the anomaly ID and the local anomaly ID match
            And the prediction for "<input_data>" is "<prediction>"
        """
        show_doc(self.test_scenario6)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "exported_file", "input_data", "prediction",
                   "model_conf"]
        examples = [
            ['data/iris.csv', '10', '10', '500', './tmp/anomaly.json',
             {"petal length": 2, "petal width": 2, "sepal length": 2,
              "sepal width": 2, "species": "Iris-setosa"},
              0.64387, '{}'],
            ['data/iris.csv', '10', '10', '500',
             './tmp/anomaly_dft.json', {}, 0.77699,
             '{"default_numeric_value": "maximum"}']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
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
            anomaly_create.i_export_anomaly(self, example["exported_file"])
            anomaly_create.i_create_local_anomaly_from_file(
                self, example["exported_file"])
            anomaly_create.check_anomaly_id_local_id(self)
            model_create.local_anomaly_prediction_is(
                self, example["input_data"], example["prediction"])

    def test_scenario7(self):
        """
        Scenario 7: Successfully creating a local association from an exported file:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create an association with "<model_conf>"
            And I wait until the association is ready less than <model_wait> secs
            And I export the association to "<exported_file>"
            When I create a local association from the file "<exported_file>"
            Then the association ID and the local association ID match
            And the prediction for "<input_data>" is "<prediction>"
        """
        show_doc(self.test_scenario7)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "exported_file", "input_data", "prediction", "model_conf"]
        examples = [
            ['data/iris.csv', '10', '10', '500', './tmp/association.json', {},
             [], '{}'],
            ['data/iris.csv', '10', '10', '500', './tmp/association_dft.json',
             {}, [{'score': 0.12, 'rules': ['00000d'], 'item': {
             'complement': False, 'count': 50, 'field_id': '000004',
             'name': 'Iris-versicolor'}}],
             '{"default_numeric_value": "mean"}']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            dataset_create.i_create_a_dataset(self, shared=example["data"])
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"], shared=example["data"])
            association_create.i_create_an_association_from_dataset_with_params(
                self, example["model_conf"])
            association_create.the_association_is_finished_in_less_than(
                self, example["model_wait"])
            association_create.i_export_association(
                self, example["exported_file"])
            association_create.i_create_local_association_from_file(
                self, example["exported_file"])
            association_create.check_association_id_local_id(self)
            model_create.local_association_prediction_is(
                self, example["input_data"], example["prediction"])

    def test_scenario8(self):
        """
        Scenario 8: Successfully creating a local topic model from an exported file:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create a topic model
            And I wait until the topic model is ready less than <model_wait> secs
            And I export the topic model to "<exported_file>"
            When I create a local topic model from the file "<exported_file>"
            Then the topic model ID and the local topic model ID match
        """
        show_doc(self.test_scenario8)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "exported_file", "source_conf"]
        examples = [
            ['data/spam.csv', '10', '10', '500', './tmp/topic_model.json', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false, "language": "en"}}}}']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            source_create.i_upload_a_file(
                self, example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"])
            source_create.i_update_source_with(self, example["source_conf"])
            source_create.the_source_is_finished(self, example["source_wait"])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"])
            topic_create.i_create_a_topic_model(self)
            topic_create.the_topic_model_is_finished_in_less_than(
                self, example["model_wait"])
            topic_create.i_export_topic_model(
                self, example["exported_file"])
            topic_create.i_create_local_topic_model_from_file(
                self, example["exported_file"])
            topic_create.check_topic_model_id_local_id(self)

    def test_scenario9(self):
        """
        Scenario 9: Successfully creating a local time series from an exported file:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create a time series with "<model_conf>"
            And I wait until the time series is ready less than <model_wait> secs
            And I export the time series to "<exported_file>"
            When I create a local time series from the file "<exported_file>"
            Then the time series ID and the local time series ID match
        """
        show_doc(self.test_scenario9)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "exported_file"]
        examples = [
            ['data/iris.csv', '10', '10', '500', './tmp/time_series.json']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            source_create.i_upload_a_file(self, example["data"])
            source_create.the_source_is_finished(self, example["source_wait"])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"])
            timeseries_create.i_create_a_time_series(self)
            timeseries_create.the_time_series_is_finished_in_less_than(
                self, example["model_wait"])
            timeseries_create.i_export_time_series(
                self, example["exported_file"])
            timeseries_create.i_create_local_time_series_from_file(
                self, example["exported_file"])
            timeseries_create.check_time_series_id_local_id(self)

    def test_scenario10(self):
        """
        Scenario 10: Successfully creating a local fusion from an exported file:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create a model with "<params>"
            And I wait until the model is ready less than <model_wait> secs
            And I create a model with "<model_conf>"
            And I wait until the model is ready less than <model_wait> secs
            And I create a model with "<model_conf>"
            And I wait until the model is ready less than <model_wait> secs
            And I retrieve a list of remote models tagged with "<tag>"
            And I create a fusion from a list of models
            And I wait until the fusion is ready less than <fusion_wait> secs
            And I export the fusion to "<exported_file>"
            When I create a local fusion from the file "<exported_file>"
            Then the fusion ID and the local fusion ID match
        """
        show_doc(self.test_scenario10)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "exported_file", "tag"]
        examples = [
            ['data/iris.csv', '10', '10', '50', './tmp/fusion.json',
             'my_fusion_tag']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
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
            model_create.i_export_fusion(self, example["exported_file"])
            model_create.i_create_local_fusion_from_file(
                self, example["exported_file"])
            model_create.check_fusion_id_local_id(self)

    def test_scenario11(self):
        """
        Scenario 11: Successfully creating a local linear regression from an exported file:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create a linear regression with "<model_conf>"
            And I wait until the linear regression is ready less than <model_wait> secs
            And I export the linear regression to "<exported_file>"
            When I create a local linear regression from the file "<exported_file>"
            Then the linear regression ID and the local linear regression ID match
            And the prediction for "<input_data>" is "<prediction>"
        """
        show_doc(self.test_scenario11)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "exported_file", "input_data", "prediction", "model_conf"]
        examples = [
            ['data/grades.csv', '20', '20', '50', './tmp/linear.json',
             {"Prefix": 5, "Assignment": 57.14, "Tutorial": 34.09,
              "Midterm": 64, "TakeHome": 40, "Final": 50}, 54.69551,
              '{}'],
            ['data/grades.csv', '20', '20', '50', './tmp/linear_dft.json', {},
             100.33246, '{"default_numeric_value": "maximum"}']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"])
            linear_create.i_create_a_linear_regression_with_objective_and_params(
                self, params=example["model_conf"])
            linear_create.the_linear_regression_is_finished_in_less_than(
                self, example["model_wait"])
            model_create.i_export_linear_regression(
                self, example["exported_file"])
            model_create.i_create_local_linear_regression_from_file(
                self, example["exported_file"])
            model_create.check_linear_regression_id_local_id(self)
            model_create.local_linear_prediction_is(
                self, example["input_data"], example["prediction"])
