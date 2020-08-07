# -*- coding: utf-8 -*-
#
# Copyright 2015-2020 BigML
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
from .world import world, setup_module, teardown_module, show_doc
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create
from . import create_association_steps as association_create
from . import create_cluster_steps as cluster_create
from . import create_anomaly_steps as anomaly_create
from . import create_prediction_steps as prediction_create
from . import compare_predictions_steps as prediction_compare


class TestComparePrediction(object):

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
            Scenario: Successfully comparing remote and local predictions
                      with raw date input for anomaly detectors
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create an anomaly detector
                And I wait until the anomaly detector is ready less
                than <time_3> secs
                And I create a local anomaly detector
                When I create an anomaly score for "<data_input>"
                Then the anomaly score is "<score>"
                And I create a local anomaly score for "<data_input>"
                Then the local anomaly score is "<score>"

                Examples:
                |data|time_1|time_2|time_3|data_input|score|

        """
        examples = [
            ['data/dates2.csv', '20', '30', '60',
             '{"time-1":"1910-05-08T19:10:23.106","cat-0":"cat2","target-2":0.4}',
             0.52477],
            ['data/dates2.csv', '20', '30', '60',
             '{"time-1":"1920-06-30T20:21:20.320","cat-0":"cat1","target-2":0.2}',
             0.50654]]
        show_doc(self.test_scenario1, examples)
        for example in examples:
            print("\nTesting with:\n", example)
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


    def test_scenario1b(self):
        """
            Scenario: Successfully comparing remote and local predictions
                      with raw date input for anomaly detectors
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create an anomaly detector
                And I wait until the anomaly detector is ready less
                than <time_3> secs
                And I create a local anomaly detector
                When I create an anomaly score for "<data_input>"
                Then the anomaly score is "<score>"
                And I create a local anomaly score for "<data_input>"
                Then the local anomaly score is "<score>"

                Examples:
                |data|time_1|time_2|time_3|data_input|score|

        """
        examples = [
            ['data/dates2.csv', '20', '30', '60',
             '{"time-1":"1932-01-30T19:24:11.440","cat-0":"cat2","target-2":0.1}',
             0.54343],
            ['data/dates2.csv', '20', '30', '60',
             '{"time-1":"1950-11-06T05:34:05.602","cat-0":"cat1" ,"target-2":0.9}',
             0.5202]]
        show_doc(self.test_scenario1b, examples)
        for example in examples:
            print("\nTesting with:\n", example)
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


    def test_scenario1b_a(self):
        """
            Scenario: Successfully comparing remote and local predictions
                      with raw date input for anomaly detectors
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create an anomaly detector
                And I wait until the anomaly detector is ready less
                than <time_3> secs
                And I create a local anomaly detector
                When I create an anomaly score for "<data_input>"
                Then the anomaly score is "<score>"
                And I create a local anomaly score for "<data_input>"
                Then the local anomaly score is "<score>"

                Examples:
                |data|time_1|time_2|time_3|data_input|score|

        """
        examples = [
            ['data/dates2.csv', '20', '30', '60',
             '{"time-1":"1969-7-14 17:36","cat-0":"cat2","target-2":0.9}',
             0.93639]]
        show_doc(self.test_scenario1b_a, examples)
        for example in examples:
            print("\nTesting with:\n", example)
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



    def test_scenario1c(self):
        """
            Scenario: Successfully comparing remote and local predictions
                      with raw date input for anomaly detectors
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create an anomaly detector
                And I wait until the anomaly detector is ready less
                than <time_3> secs
                And I create a local anomaly detector
                When I create an anomaly score for "<data_input>"
                Then the anomaly score is "<score>"
                And I create a local anomaly score for "<data_input>"
                Then the local anomaly score is "<score>"

                Examples:
                |data|time_1|time_2|time_3|data_input|score|

        """
        examples = [
            ['data/dates2.csv', '20', '30', '60',
             '{"time-1":"2001-01-05T23:04:04.693","cat-0":"cat2","target-2":0.01}',
             0.54911],
            ['data/dates2.csv', '20', '30', '60',
             '{"time-1":"2011-04-01T00:16:45.747","cat-0":"cat2","target-2":0.32}',
             0.52477]]
        show_doc(self.test_scenario1c, examples)
        for example in examples:
            print("\nTesting with:\n", example)
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



    def test_scenario1c_a(self):
        """
            Scenario: Successfully comparing remote and local predictions
                      with raw date input for anomaly detectors
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create an anomaly detector
                And I wait until the anomaly detector is ready less
                than <time_3> secs
                And I create a local anomaly detector
                When I create an anomaly score for "<data_input>"
                Then the anomaly score is "<score>"
                And I create a local anomaly score for "<data_input>"
                Then the local anomaly score is "<score>"

                Examples:
                |data|time_1|time_2|time_3|data_input|score|

        """
        examples = [
            ['data/dates2.csv', '20', '30', '60',
             '{"time-1":"1969-W29-1T17:36:39Z","cat-0":"cat1","target-2":0.87}',
             0.93678],
            ['data/dates2.csv', '20', '30', '60',
             '{"time-1":"Mon Jul 14 17:36 +0000 1969","cat-0":"cat1","target-2":0}',
             0.93717]]
        show_doc(self.test_scenario1c_a, examples)
        for example in examples:
            print("\nTesting with:\n", example)
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


    def test_scenario2(self):
        """
            Scenario: Successfully comparing remote and local predictions
                      with raw date input for cluster
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a cluster
                And I wait until the cluster is ready less than <time_3> secs
                And I create a local cluster
                When I create a centroid for "<data_input>"
                Then the centroid is "<centroid>" with distance "<distance>"
                And I create a local centroid for "<data_input>"
                Then the local centroid is "<centroid>" with
                distance "<distance>"

                Examples headers:
                |data|time_1|time_2|time_3|data_input|centroid|distance|

        """
        examples = [
            ['data/dates2.csv', '20', '30', '60',
             '{"time-1":"1910-05-08T19:10:23.106","cat-0":"cat2","target-2":0.4}',
             "Cluster 2", 0.92112],
            ['data/dates2.csv', '20', '30', '60',
             '{"time-1":"1920-06-30T20:21:20.320","cat-0":"cat1","target-2":0.2}',
             "Cluster 3", 0.77389]]
        show_doc(self.test_scenario2, examples)
        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self,
                                                                example[2])
            cluster_create.i_create_a_cluster(self)
            cluster_create.the_cluster_is_finished_in_less_than(self,
                                                                example[3])
            prediction_compare.i_create_a_local_cluster(self)
            prediction_create.i_create_a_centroid(self, example[4])
            prediction_create.the_centroid_is_with_distance(self,
                                                            example[5],
                                                            example[6])
            prediction_compare.i_create_a_local_centroid(self, example[4])
            prediction_compare.the_local_centroid_is(self,
                                                     example[5],
                                                     example[6])


    def test_scenario2_a(self):
        """
            Scenario: Successfully comparing remote and local predictions
                      with raw date input for cluster
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a cluster
                And I wait until the cluster is ready less than <time_3> secs
                And I create a local cluster
                When I create a centroid for "<data_input>"
                Then the centroid is "<centroid>" with distance "<distance>"
                And I create a local centroid for "<data_input>"
                Then the local centroid is "<centroid>" with
                distance "<distance>"

                Examples headers:
                |data|time_1|time_2|time_3|data_input|centroid|distance|

        """
        examples = [
            ['data/dates2.csv', '20', '30', '60',
             '{"time-1":"1932-01-30T19:24:11.440","cat-0":"cat2","target-2":0.1}',
             "Cluster 0", 0.87855],
            ['data/dates2.csv', '20', '30', '60',
             '{"time-1":"1950-11-06T05:34:05.602","cat-0":"cat1" ,"target-2":0.9}',
             "Cluster 6", 0.83506]]
        show_doc(self.test_scenario2_a, examples)
        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self,
                                                                example[2])
            cluster_create.i_create_a_cluster(self)
            cluster_create.the_cluster_is_finished_in_less_than(self,
                                                                example[3])
            prediction_compare.i_create_a_local_cluster(self)
            prediction_create.i_create_a_centroid(self, example[4])
            prediction_create.the_centroid_is_with_distance(self,
                                                            example[5],
                                                            example[6])
            prediction_compare.i_create_a_local_centroid(self, example[4])
            prediction_compare.the_local_centroid_is(self,
                                                     example[5],
                                                     example[6])


    def test_scenario3(self):
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
                Then the association set is like the contents of
                "<association_set_file>"
                And I create a local association set for "<data_input>"
                Then the local association set is like the contents of
                "<association_set_file>"

        """
        examples = [['data/dates2.csv', '20', '30', '80', '{"target-2": -1}',
                     'data/associations/association_set2.json']]
        show_doc(self.test_scenario3, examples)

        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            association_create.i_create_an_association_from_dataset(self)
            association_create.the_association_is_finished_in_less_than(self,
                                                                        example[3])
            prediction_compare.i_create_a_local_association(self)
            prediction_create.i_create_an_association_set(self, example[4])
            prediction_compare.the_association_set_is_like_file(self, example[5])
            prediction_compare.i_create_a_local_association_set(self, example[4])
            prediction_compare.the_local_association_set_is_like_file(self, example[5])
