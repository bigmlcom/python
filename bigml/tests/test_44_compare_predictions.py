# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,line-too-long,attribute-defined-outside-init
#pylint: disable=locally-disabled,unused-import
#
# Copyright 2015-2023 BigML
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
from .world import world, setup_module, teardown_module, show_doc, \
    show_method
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create
from . import create_association_steps as association_create
from . import create_cluster_steps as cluster_create
from . import create_anomaly_steps as anomaly_create
from . import create_prediction_steps as prediction_create
from . import compare_predictions_steps as prediction_compare


class TestComparePrediction:
    """Test local and remote predictions"""

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
        Scenario: Successfully comparing remote and local predictions
                  with raw date input for anomaly detectors
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create an anomaly detector
            And I wait until the anomaly detector is ready less
            than <time_3> secs
            And I create a local anomaly detector
            And I enable the pre-modeling pipeline
            When I create an anomaly score for "<input_data>"
            Then the anomaly score is "<score>"
            And I create a local anomaly score for "<input_data>"
            Then the local anomaly score is "<score>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "input_data", "score"]
        examples = [
            ['data/dates2.csv', '20', '30', '60',
             '{"time-1":"1910-05-08T19:10:23.106","cat-0":"cat2","target-2":0.4}',
             0.52477],
            ['data/dates2.csv', '20', '30', '60',
             '{"time-1":"1920-06-30T20:21:20.320","cat-0":"cat1","target-2":0.2}',
             0.50654]]
        show_doc(self.test_scenario1, examples)
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
            anomaly_create.i_create_an_anomaly(self)
            anomaly_create.the_anomaly_is_finished_in_less_than(
                self, example["model_wait"])
            prediction_compare.i_create_a_local_anomaly(self, pre_model=True)
            prediction_create.i_create_an_anomaly_score(
                self, example["input_data"])
            prediction_create.the_anomaly_score_is(
                self, example["score"])
            prediction_compare.i_create_a_local_anomaly_score(
                self, example["input_data"], pre_model=self.bigml["local_pipeline"])
            prediction_compare.the_local_anomaly_score_is(
                self, example["score"])

    def test_scenario1b(self):
        """
        Scenario: Successfully comparing remote and local predictions
                  with raw date input for anomaly detectors
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create an anomaly detector
            And I wait until the anomaly detector is ready less
            than <time_3> secs
            And I create a local anomaly detector
            When I create an anomaly score for "<input_data>"
            Then the anomaly score is "<score>"
            And I create a local anomaly score for "<input_data>"
            Then the local anomaly score is "<score>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "input_data", "score"]
        examples = [
            ['data/dates2.csv', '20', '30', '60',
             '{"time-1":"1932-01-30T19:24:11.440","cat-0":"cat2","target-2":0.1}',
             0.54343],
            ['data/dates2.csv', '20', '30', '60',
             '{"time-1":"1950-11-06T05:34:05.602","cat-0":"cat1" ,"target-2":0.9}',
             0.5202]]
        show_doc(self.test_scenario1b)
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
            prediction_compare.i_create_a_local_anomaly(self, pre_model=True)
            prediction_create.i_create_an_anomaly_score(
                self, example["input_data"])
            prediction_create.the_anomaly_score_is(
                self, example["score"])
            prediction_compare.i_create_a_local_anomaly_score(
                self, example["input_data"], pre_model=self.bigml["local_pipeline"])
            prediction_compare.the_local_anomaly_score_is(
                self, example["score"])


    def test_scenario1b_a(self):
        """
        Scenario: Successfully comparing remote and local predictions
                  with raw date input for anomaly detectors
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create an anomaly detector
            And I wait until the anomaly detector is ready less
            than <time_3> secs
            And I create a local anomaly detector
            When I create an anomaly score for "<input_data>"
            Then the anomaly score is "<score>"
            And I create a local anomaly score for "<input_data>"
            Then the local anomaly score is "<score>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "input_data", "score"]
        examples = [
            ['data/dates2.csv', '20', '30', '60',
             '{"time-1":"1969-7-14 17:36","cat-0":"cat2","target-2":0.9}',
             0.93639]]
        show_doc(self.test_scenario1b_a)
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
            prediction_compare.i_create_a_local_anomaly(self, pre_model=True)
            prediction_create.i_create_an_anomaly_score(
                self, example["input_data"])
            prediction_create.the_anomaly_score_is(
                self, example["score"])
            prediction_compare.i_create_a_local_anomaly_score(
                self, example["input_data"], pre_model=self.bigml["local_pipeline"])
            prediction_compare.the_local_anomaly_score_is(
                self, example["score"])

    def test_scenario1c(self):
        """
        Scenario: Successfully comparing remote and local predictions
                  with raw date input for anomaly detectors
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create an anomaly detector
            And I wait until the anomaly detector is ready less
            than <time_3> secs
            And I create a local anomaly detector
            When I create an anomaly score for "<input_data>"
            Then the anomaly score is "<score>"
            And I create a local anomaly score for "<input_data>"
            Then the local anomaly score is "<score>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "input_data", "score"]
        examples = [
            ['data/dates2.csv', '20', '30', '60',
             '{"time-1":"2001-01-05T23:04:04.693","cat-0":"cat2","target-2":0.01}',
             0.54911],
            ['data/dates2.csv', '20', '30', '60',
             '{"time-1":"2011-04-01T00:16:45.747","cat-0":"cat2","target-2":0.32}',
             0.52477]]
        show_doc(self.test_scenario1c)
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
            prediction_compare.i_create_a_local_anomaly(self, pre_model=True)
            prediction_create.i_create_an_anomaly_score(
                self, example["input_data"])
            prediction_create.the_anomaly_score_is(self, example["score"])
            prediction_compare.i_create_a_local_anomaly_score(
                self, example["input_data"], pre_model=self.bigml["local_pipeline"])
            prediction_compare.the_local_anomaly_score_is(
                self, example["score"])

    def test_scenario1c_a(self):
        """
        Scenario: Successfully comparing remote and local predictions
                  with raw date input for anomaly detectors
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create an anomaly detector
            And I wait until the anomaly detector is ready less
            than <model_wait> secs
            And I create a local anomaly detector
            When I create an anomaly score for "<input_data>"
            Then the anomaly score is "<score>"
            And I create a local anomaly score for "<input_data>"
            Then the local anomaly score is "<score>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "input_data", "score"]
        examples = [
            ['data/dates2.csv', '20', '30', '60',
             '{"time-1":"1969-W29-1T17:36:39Z","cat-0":"cat1","target-2":0.87}',
             0.93678],
            ['data/dates2.csv', '20', '30', '60',
             '{"time-1":"Mon Jul 14 17:36 +0000 1969","cat-0":"cat1","target-2":0}',
             0.93717]]
        show_doc(self.test_scenario1c_a)
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
            prediction_compare.i_create_a_local_anomaly(self, pre_model=True)
            prediction_create.i_create_an_anomaly_score(
                self, example["input_data"])
            prediction_create.the_anomaly_score_is(
                self, example["score"])
            prediction_compare.i_create_a_local_anomaly_score(
                self, example["input_data"], pre_model=self.bigml["local_pipeline"])
            prediction_compare.the_local_anomaly_score_is(
                self, example["score"])

    def test_scenario2(self):
        """
        Scenario: Successfully comparing remote and local predictions
                  with raw date input for cluster
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create a cluster
            And I wait until the cluster is ready less than <model_wait> secs
            And I create a local cluster
            When I create a centroid for "<input_data>"
            Then the centroid is "<centroid>" with distance "<distance>"
            And I create a local centroid for "<input_data>"
            Then the local centroid is "<centroid>" with
            distance "<distance>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "input_data", "centroid", "distance"]
        examples = [
            ['data/dates2.csv', '20', '30', '60',
             '{"time-1":"1910-05-08T19:10:23.106","cat-0":"cat2","target-2":0.4}',
             "Cluster 2", 0.92112],
            ['data/dates2.csv', '20', '30', '60',
             '{"time-1":"1920-06-30T20:21:20.320","cat-0":"cat1","target-2":0.2}',
             "Cluster 3", 0.77389]]
        show_doc(self.test_scenario2)
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
            prediction_compare.i_create_a_local_cluster(self, pre_model=True)
            prediction_create.i_create_a_centroid(
                self, example["input_data"])
            prediction_create.the_centroid_is_with_distance(
                self, example["centroid"], example["distance"])
            prediction_compare.i_create_a_local_centroid(
                self, example["input_data"], pre_model=self.bigml["local_pipeline"])
            prediction_compare.the_local_centroid_is(
                self, example["centroid"], example["distance"])

    def test_scenario2_a(self):
        """
        Scenario: Successfully comparing remote and local predictions
                  with raw date input for cluster
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create a cluster
            And I wait until the cluster is ready less than <model_wait> secs
            And I create a local cluster
            When I create a centroid for "<input_data>"
            Then the centroid is "<centroid>" with distance "<distance>"
            And I create a local centroid for "<input_data>"
            Then the local centroid is "<centroid>" with
            distance "<distance>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "input_data", "centroid", "distance"]
        examples = [
            ['data/dates2.csv', '20', '30', '60',
             '{"time-1":"1932-01-30T19:24:11.440","cat-0":"cat2","target-2":0.1}',
             "Cluster 0", 0.87855],
            ['data/dates2.csv', '20', '30', '60',
             '{"time-1":"1950-11-06T05:34:05.602","cat-0":"cat1" ,"target-2":0.9}',
             "Cluster 6", 0.83506]]
        show_doc(self.test_scenario2_a)
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
                self, example["model_wait"])
            prediction_compare.i_create_a_local_cluster(self, pre_model=True)
            prediction_create.i_create_a_centroid(
                self, example["input_data"])
            prediction_create.the_centroid_is_with_distance(
                self, example["centroid"], example["distance"])
            prediction_compare.i_create_a_local_centroid(
                self, example["input_data"], pre_model=self.bigml["local_pipeline"])
            prediction_compare.the_local_centroid_is(
                self, example["centroid"], example["distance"])

    def test_scenario3(self):
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
            Then the association set is like the contents of
            "<association_set_file>"
            And I create a local association set for "<input_data>"
            Then the local association set is like the contents of
            "<association_set_file>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "input_data", "association_set_file"]
        examples = [['data/dates2.csv', '20', '30', '80', '{"target-2": -1}',
                     'data/associations/association_set2.json']]
        show_doc(self.test_scenario3)
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
            prediction_compare.i_create_a_local_association(
                self, pre_model=True)
            prediction_create.i_create_an_association_set(
                self, example["input_data"])
            prediction_compare.the_association_set_is_like_file(
                self, example["association_set_file"])
            prediction_compare.i_create_a_local_association_set(
                self, example["input_data"], pre_model=self.bigml["local_pipeline"])
            prediction_compare.the_local_association_set_is_like_file(
                self, example["association_set_file"])
