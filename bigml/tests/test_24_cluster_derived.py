# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,line-too-long,attribute-defined-outside-init
#pylint: disable=locally-disabled,unused-import
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


""" Creating datasets and models associated to a cluster

"""
from .world import world, setup_module, teardown_module, show_doc, \
    show_method
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create
from . import create_model_steps as model_create
from . import create_cluster_steps as cluster_create
from . import compare_predictions_steps as prediction_compare

class TestClusterDerived:
    """Testing resources derived from clusters"""

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
        Scenario: Successfully creating datasets for first centroid of a cluster:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create a cluster
            And I wait until the cluster is ready less than <model_wait> secs
            When I create a dataset associated to centroid "<centroid_id>"
            And I wait until the dataset is ready less than <dataset_wait> secs
            Then the dataset is associated to the centroid "<centroid_id>" of the cluster
        """
        show_doc(self.test_scenario1)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "centroid_id"]
        examples = [
            ['data/iris.csv', '10', '10', '40', '000001']]
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
            dataset_create.i_create_a_dataset_from_cluster(
                self, example["centroid_id"])
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"])
            dataset_create.is_associated_to_centroid_id(
                self, example["centroid_id"])

    def test_scenario2(self):
        """
        Scenario: Successfully creating models for first centroid of a cluster:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create a cluster with options "<model_conf>"
            And I wait until the cluster is ready less than <model_wait> secs
            When I create a model associated to centroid "<centroid_id>"
            And I wait until the model is ready less than <dataset_wait> secs
            Then the model is associated to the centroid "<centroid_id>" of the cluster
        """
        show_doc(self.test_scenario2)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "centroid_id", "model_conf"]
        examples = [
            ['data/iris.csv', '10', '10', '40', '000001',
             '{"model_clusters": true}']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            dataset_create.i_create_a_dataset(self, shared=example["data"])
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"])
            cluster_create.i_create_a_cluster_with_options(
                self, example["model_conf"])
            cluster_create.the_cluster_is_finished_in_less_than(
                self, example["model_wait"])
            model_create.i_create_a_model_from_cluster(
                self, example["centroid_id"])
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            model_create.is_associated_to_centroid_id(
                self, example["centroid_id"])

    def test_scenario3(self):
        """
        Scenario: Successfully getting the closest point in a cluster:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create a cluster
            And I wait until the cluster is ready less than <model_wait> secs
            And I create a local cluster
            Then the data point in the cluster closest to "<reference>" is "<closest>"
        """
        show_doc(self.test_scenario3)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "reference", "closest"]
        examples = [
            ['data/iris.csv', '10', '10', '40',
             '{"petal length": 1.4, "petal width": 0.2,'
             ' "sepal width": 3.0, "sepal length": 4.89,'
             ' "species": "Iris-setosa"}',
             '{"distance": 0.001894153207990619, "data":'
             ' {"petal length": "1.4", "petal width": "0.2",'
             ' "sepal width": "3.0", "sepal length": "4.9",'
             ' "species": "Iris-setosa"}}'],
            ['data/spam_4w.csv', '10', '10', '40',
             '{"Message": "mobile"}',
             '{"distance": 0.0, "data":'
             ' {"Message": "mobile", "Type": "spam"}}']]
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
            prediction_compare.i_create_a_local_cluster(self)
            cluster_create.closest_in_cluster(
                self, example["reference"], example["closest"])


    def test_scenario4(self):
        """
        Scenario: Successfully getting the closest centroid in a cluster:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create a cluster
            And I wait until the cluster is ready less than <model_wait> secs
            And I create a local cluster
            Then the centroid in the cluster closest to "<reference>" is "<closest>"
        """
        show_doc(self.test_scenario4)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "reference", "closest"]
        examples = [
            ['data/spam_4w.csv', '10', '10', '40',
             '{"Message": "free"}',
             '000005']]
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
            prediction_compare.i_create_a_local_cluster(self)
            cluster_create.closest_centroid_in_cluster(
                self, example["reference"], example["closest"])
