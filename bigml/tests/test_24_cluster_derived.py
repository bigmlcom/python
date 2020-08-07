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


""" Creating datasets and models associated to a cluster

"""
from .world import world, setup_module, teardown_module
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create
from . import create_model_steps as model_create
from . import create_cluster_steps as cluster_create
from . import compare_predictions_steps as prediction_compare

class TestClusterDerived(object):

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
            Scenario: Successfully creating datasets for first centroid of a cluster:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a cluster
                And I wait until the cluster is ready less than <time_3> secs
                When I create a dataset associated to centroid "<centroid_id>"
                And I wait until the dataset is ready less than <time_4> secs
                Then the dataset is associated to the centroid "<centroid_id>" of the cluster

                Examples:
                | data             | time_1  | time_2 | time_3 | centroid_id                             | time_4 |
                | ../data/iris.csv | 10      | 10     | 40     | 000001                                  | 10     |

        """
        print(self.test_scenario1.__doc__)
        examples = [
            ['data/iris.csv', '10', '10', '40', '000001', '10']]
        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            cluster_create.i_create_a_cluster(self)
            cluster_create.the_cluster_is_finished_in_less_than(self, example[3])
            dataset_create.i_create_a_dataset_from_cluster(self, example[4])
            dataset_create.the_dataset_is_finished_in_less_than(self, example[5])
            dataset_create.is_associated_to_centroid_id(self, example[4])

    def test_scenario2(self):
        """
            Scenario: Successfully creating models for first centroid of a cluster:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a cluster with options "<options>"
                And I wait until the cluster is ready less than <time_3> secs
                When I create a model associated to centroid "<centroid_id>"
                And I wait until the model is ready less than <time_4> secs
                Then the model is associated to the centroid "<centroid_id>" of the cluster

                Examples:
                | data             | time_1  | time_2 | time_3 | centroid_id                             | time_4 |
                | ../data/iris.csv | 10      | 10     | 40     | 000001                                  | 10     |

        """
        print(self.test_scenario2.__doc__)
        examples = [
            ['data/iris.csv', '10', '10', '40', '000001', '10', '{"model_clusters": true}']]
        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            cluster_create.i_create_a_cluster_with_options(self, example[6])
            cluster_create.the_cluster_is_finished_in_less_than(self, example[3])
            model_create.i_create_a_model_from_cluster(self, example[4])
            model_create.the_model_is_finished_in_less_than(self, example[5])
            model_create.is_associated_to_centroid_id(self, example[4])

    def test_scenario3(self):
        """
            Scenario: Successfully getting the closest point in a cluster:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a cluster
                And I wait until the cluster is ready less than <time_3> secs
                And I create a local cluster
                Then the data point in the cluster closest to "<reference>" is "<closest>"

                Examples:
                | data | time_1  | time_2 | time_3 | reference | closest |

        """
        print(self.test_scenario3.__doc__)
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
            print("\nTesting with:\n", example)
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            cluster_create.i_create_a_cluster(self)
            cluster_create.the_cluster_is_finished_in_less_than(self, example[3])
            prediction_compare.i_create_a_local_cluster(self)
            cluster_create.closest_in_cluster(self, example[4], example[5])


    def test_scenario4(self):
        """
            Scenario: Successfully getting the closest centroid in a cluster:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a cluster
                And I wait until the cluster is ready less than <time_3> secs
                And I create a local cluster
                Then the centroid in the cluster closest to "<reference>" is "<closest>"

                Examples:
                | data | time_1  | time_2 | time_3 | reference | closest |

        """
        print(self.test_scenario4.__doc__)
        examples = [
            ['data/spam_4w.csv', '10', '10', '40',
             '{"Message": "free"}',
             '000005']]
        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            cluster_create.i_create_a_cluster(self)
            cluster_create.the_cluster_is_finished_in_less_than(self, example[3])
            prediction_compare.i_create_a_local_cluster(self)
            cluster_create.closest_centroid_in_cluster(self, example[4], example[5])
