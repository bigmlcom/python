# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,line-too-long,attribute-defined-outside-init
#pylint: disable=locally-disabled,unused-import
#
# Copyright 2020 BigML
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


""" Creating clones for models

"""
from .world import world, setup_module, teardown_module, show_doc, \
    show_method
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create
from . import create_model_steps as model_create
from . import create_ensemble_steps as ensemble_create
from . import create_linear_steps as linear_create
from . import create_cluster_steps as cluster_create
from . import create_lda_steps as topic_create
from . import create_anomaly_steps as anomaly_create
from . import create_association_steps as association_create
from . import create_time_series_steps as time_create
from . import create_pca_steps as pca_create


class TestCloning:
    """Testing cloned resources creation"""

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
        Scenario: Successfully creating a clone from a model:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create a model
            And I wait until the model is ready less than <model_wait> secs
            Then the origin model is the previous model
        """
        show_doc(self.test_scenario1)
        headers = ["data", "source_wait", "dataset_wait", "model_wait"]
        examples = [
            ['data/iris.csv', '10', '10', '10']]
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
            model_create.i_create_a_model(self, shared=example["data"])
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"], shared=example["data"])
            model = world.model["resource"]
            model_create.clone_model(self, model)
            model_create.the_cloned_model_is(self, model)

    def test_scenario2(self):
        """
        Scenario: Successfully creating a clone from a ensemble:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create an ensemble
            And I wait until the ensemble is ready less than <model_wait> secs
            Then the origin ensemble is the previous ensemble
        """
        show_doc(self.test_scenario2)
        headers = ["data", "source_wait", "dataset_wait", "model_wait"]
        examples = [
            ['data/iris.csv', '10', '10', '30']]
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
            ensemble_create.i_create_an_ensemble(self, shared=example["data"])
            ensemble_create.the_ensemble_is_finished_in_less_than(
                self, example["model_wait"], shared=example["data"])
            ensemble = world.ensemble["resource"]
            ensemble_create.clone_ensemble(self, ensemble)
            ensemble_create.the_cloned_ensemble_is(self, ensemble)

    def test_scenario3(self):
        """
        Scenario: Successfully creating a clone from a deepnet:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create a quick deepnet
            And I wait until the deepnet is ready less than <model_wait> secs
            Then the origin deepnet is the previous deepnet
        """
        show_doc(self.test_scenario3)
        headers = ["data", "source_wait", "dataset_wait", "model_wait"]
        examples = [
            ['data/iris.csv', '10', '10', '100']]
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
            model_create.i_create_a_quick_deepnet(self)
            model_create.the_deepnet_is_finished_in_less_than(
                self, example["model_wait"])
            deepnet = world.deepnet["resource"]
            model_create.clone_deepnet(self, deepnet)
            model_create.the_cloned_deepnet_is(self, deepnet)

    def test_scenario4(self):
        """
        Scenario: Successfully creating a clone from a logistic regression:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create a logistic regression
            And I wait until the logistic regression is ready less than <model_wait> secs
            Then the origin logistic regression is the previous logistic regression
        """
        show_doc(self.test_scenario4)
        headers = ["data", "source_wait", "dataset_wait", "model_wait"]
        examples = [
            ['data/iris.csv', '10', '10', '30']]
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
            model_create.i_create_a_logistic_model(self, shared=example["data"])
            model_create.the_logistic_model_is_finished_in_less_than(
                self, example["model_wait"], shared=example["data"])
            logistic_regression = world.logistic_regression["resource"]
            model_create.clone_logistic_regression(self, logistic_regression)
            model_create.the_cloned_logistic_regression_is(
                self, logistic_regression)

    def test_scenario5(self):
        """
        Scenario: Successfully creating a clone from a linear regression:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create a linear regression
            And I wait until the linear regression is ready less than <model_wait> secs
            Then the origin linear regression is the previous linear regression
        """
        show_doc(self.test_scenario5)
        headers = ["data", "source_wait", "dataset_wait", "model_wait"]
        examples = [
            ['data/iris.csv', '10', '10', '30']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            source_create.i_upload_a_file(self, example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            dataset_create.i_create_a_dataset(self, shared=example["data"])
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"], shared=example["data"])
            linear_create.i_create_a_linear_regression_from_dataset(
                self, shared=example["data"])
            linear_create.the_linear_regression_is_finished_in_less_than(
                self, example["model_wait"], shared=example["data"])
            linear_regression = world.linear_regression["resource"]
            linear_create.clone_linear_regression(self, linear_regression)
            linear_create.the_cloned_linear_regression_is(
                self, linear_regression)

    def test_scenario6(self):
        """
        Scenario: Successfully creating a clone from a cluster:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create a cluster
            And I wait until the cluster is ready less than <model_wait> secs
            Then the origin cluster is the previous cluster
        """
        show_doc(self.test_scenario6)
        headers = ["data", "source_wait", "dataset_wait", "model_wait"]
        examples = [
            ['data/iris.csv', '10', '10', '30']]
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
            cluster_create.i_create_a_cluster(self, shared=example["data"])
            cluster_create.the_cluster_is_finished_in_less_than(
                self, example["model_wait"], shared=example["data"])
            cluster = world.cluster["resource"]
            cluster_create.clone_cluster(self, cluster)
            cluster_create.the_cloned_cluster_is(
                self, cluster)

    def test_scenario7(self):
        """
        Scenario: Successfully creating a clone from a topic model:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create a topic model
            And I wait until the topic model is ready less than <model_wait> secs
            Then the origin topic model is the previous topic model
        """
        show_doc(self.test_scenario7)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "source_conf"]
        examples = [
            ['data/spam.csv', '10', '10', '100', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false, "language": "en"}}}}']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            source_create.i_upload_a_file(
                self, example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"])
            source_create.i_update_source_with(
                self, example["source_conf"])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"])
            topic_create.i_create_a_topic_model(self)
            topic_create.the_topic_model_is_finished_in_less_than(
                self, example["model_wait"])
            topic_model = world.topic_model["resource"]
            topic_create.clone_topic_model(self, topic_model)
            topic_create.the_cloned_topic_model_is(
                self, topic_model)


    def test_scenario8(self):
        """
        Scenario: Successfully creating a clone from an anomaly detector:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create an anomaly detector
            And I wait until the anomaly detector is ready less than <model_wait> secs
            Then the origin anomaly detector is the previous anomaly detector
        """
        show_doc(self.test_scenario8)
        headers = ["data", "source_wait", "dataset_wait", "model_wait"]
        examples = [
            ['data/iris.csv', '10', '10', '100']]
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
            anomaly_create.i_create_an_anomaly(self, shared=example["data"])
            anomaly_create.the_anomaly_is_finished_in_less_than(
                self, example["model_wait"], shared=example["data"])
            anomaly = world.anomaly["resource"]
            anomaly_create.clone_anomaly(self, anomaly)
            anomaly_create.the_cloned_anomaly_is(
                self, anomaly)

    def test_scenario9(self):
        """
        Scenario: Successfully creating a clone from an association:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create an association
            And I wait until the association is ready less than <model_wait> secs
            Then the origin association is the previous association
        """
        show_doc(self.test_scenario9)
        headers = ["data", "source_wait", "dataset_wait", "model_wait"]
        examples = [
            ['data/iris.csv', '10', '10', '100']]
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
            association_create.i_create_an_association_from_dataset(
                self, shared=example["data"])
            association_create.the_association_is_finished_in_less_than(
                self, example["model_wait"], shared=example["data"])
            association = world.association["resource"]
            association_create.clone_association(self, association)
            association_create.the_cloned_association_is(
                self, association)

    def test_scenario10(self):
        """
        Scenario: Successfully creating a clone from a time series:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create a time series
            And I wait until the time series is ready less than <model_wait> secs
            Then the origin time series is the previous time series
        """
        show_doc(self.test_scenario10)
        headers = ["data", "source_wait", "dataset_wait", "model_wait"]
        examples = [
            ['data/iris.csv', '10', '10', '100']]
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
            time_create.i_create_a_time_series(self)
            time_create.the_time_series_is_finished_in_less_than(
                self, example["model_wait"])
            time_series = world.time_series["resource"]
            time_create.clone_time_series(self, time_series)
            time_create.the_cloned_time_series_is(
                self, time_series)

    def test_scenario11(self):
        """
        Scenario: Successfully creating a clone from a pca:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create a pca
            And I wait until the pca is ready less than <model_wait> secs
            Then the origin pca is the previous pca
        """
        show_doc(self.test_scenario11)
        headers = ["data", "source_wait", "dataset_wait", "model_wait"]
        examples = [
            ['data/iris.csv', '10', '10', '100']]
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
            pca_create.i_create_a_pca(self, shared=example["data"])
            pca_create.the_pca_is_finished_in_less_than(
                self, example["model_wait"], shared=example["data"])
            pca = world.pca["resource"]
            pca_create.clone_pca(self, pca)
            pca_create.the_cloned_pca_is(self, pca)
