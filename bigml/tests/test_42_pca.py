# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2018-2020 BigML
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


""" Creating PCA

"""
from world import world, setup_module, teardown_module
import create_source_steps as source_create
import create_dataset_steps as dataset_create
import create_pca_steps as pca_create
import create_projection_steps as projection_create
import create_batch_projection_steps as batch_proj_create

class TestPCA(object):

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
            Scenario: Successfully creating a PCA from a dataset:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a PCA from a dataset
                And I wait until the PCA is ready less than <time_3> secs
                And I update the PCA name to "<pca_name>"
                When I wait until the PCA is ready less than <time_4> secs
                Then the PCA name is "<pca_name>"

                Examples:
                | data                | time_1  | time_2 | time_3 | time_4 | pca_name |
                | ../data/iris.csv | 10      | 10     | 20     | 20 | my new pca name |
        """
        print self.test_scenario1.__doc__
        examples = [
            ['data/iris.csv', '10', '10', '20', '20', 'my new pca name']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            pca_create.i_create_a_pca_from_dataset(self)
            pca_create.the_pca_is_finished_in_less_than(self, example[3])
            pca_create.i_update_pca_name(self, example[5])
            pca_create.the_pca_is_finished_in_less_than(self, example[4])
            pca_create.i_check_pca_name(self, example[5])

        print "\nEnd of tests in: %s\n-------------------\n" % __name__

    def test_scenario2(self):
        """
            Scenario: Successfully creating a projection:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a pca
                And I wait until the pca is ready less than <time_3> secs
                When I create a projection for "<data_input>"
                Then the projection is "<projection>"

                Examples:
                | data                | time_1  | time_2 | time_3 | data_input    | projection  |
                | ../data/iris.csv | 10      | 10     | 10     | {"petal width": 0.5} | '{"PC-0": 0.46547, "PC-1": 0.13724, "PC-2": -0.01666, "PC-3": 3.28995, "PC-4": 4.60383, "PC-5": 2.22108}' |
        """
        print self.test_scenario2.__doc__
        examples = [
            ['data/iris.csv', '30', '30', '30', '{"petal width": 0.5}', '{"PC2": 0.1593, "PC3": -0.01286, "PC1": 0.91648, "PC6": 0.27284, "PC4": 1.29255, "PC5": 0.75196}']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            pca_create.i_create_a_pca(self)
            pca_create.the_pca_is_finished_in_less_than(self, example[3])
            projection_create.i_create_a_projection(self, example[4])
            projection_create.the_projection_is(self, example[5])

        print "\nEnd of tests in: %s\n-------------------\n" % __name__


    def test_scenario3(self):
        """
            Scenario: Successfully creating a batch projection:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a pca
                And I wait until the pca is ready less than <time_3> secs
                When I create a batch projection for the dataset with the pca
                And I wait until the batch projection is ready less than <time_4> secs
                And I download the created projections file to "<local_file>"
                Then the batch projection file is like "<projections_file>"

                Examples:
                | data             | time_1  | time_2 | time_3 | time_4 | local_file | predictions_file       |
                | ../data/iris.csv | 30      | 30     | 50     | 50     | ./tmp/batch_projections.csv |./data/batch_projections.csv |

        """
        print self.test_scenario3.__doc__
        examples = [
            ['data/iris.csv', '30', '30', '50', '50', 'tmp/batch_projections.csv', 'data/batch_projections.csv']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            pca_create.i_create_a_pca(self)
            pca_create.the_pca_is_finished_in_less_than(self, example[3])
            batch_proj_create.i_create_a_batch_projection(self)
            batch_proj_create.the_batch_projection_is_finished_in_less_than(self, example[4])
            batch_proj_create.i_download_projections_file(self, example[5])
            batch_proj_create.i_check_projections(self, example[6])
