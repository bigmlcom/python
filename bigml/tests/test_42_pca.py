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


""" Creating PCA

"""
from .world import world, setup_module, teardown_module, show_doc, \
    show_method
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create
from . import create_pca_steps as pca_create
from . import create_projection_steps as projection_create
from . import create_batch_projection_steps as batch_proj_create

class TestPCA:
    """Testing PCA methods"""

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
        Scenario: Successfully creating a PCA from a dataset:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create a PCA from a dataset
            And I wait until the PCA is ready less than <model_wait> secs
            And I update the PCA name to "<pca_name>"
            When I wait until the PCA is ready less than <model_wait> secs
            Then the PCA name is "<pca_name>"
        """
        show_doc(self.test_scenario1)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
           "pca_name"]
        examples = [
            ['data/iris.csv', '10', '10', '40', 'my new pca name']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"], shared=example["data"])
            pca_create.i_create_a_pca_from_dataset(self)
            pca_create.the_pca_is_finished_in_less_than(
                self, example["model_wait"])
            pca_create.i_update_pca_name(self, example["pca_name"])
            pca_create.the_pca_is_finished_in_less_than(
                self, example["model_wait"])
            pca_create.i_check_pca_name(self, example["pca_name"])

        print("\nEnd of tests in: %s\n-------------------\n" % __name__)

    def test_scenario2(self):
        """
        Scenario: Successfully creating a projection:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create a pca
            And I wait until the pca is ready less than <model_wait> secs
            When I create a projection for "<input_data>"
            Then the projection is "<projection>"
        """
        show_doc(self.test_scenario2)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
           "input_data", "projection"]
        examples = [
            ['data/iris.csv', '30', '30', '50', '{"petal width": 0.5}',
             '{"PC2": 0.1593, "PC3": -0.01286, "PC1": 0.91648, '
             '"PC6": 0.27284, "PC4": 1.29255, "PC5": 0.75196}']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"], shared=example["data"])
            pca_create.i_create_a_pca(self)
            pca_create.the_pca_is_finished_in_less_than(
                self, example["model_wait"])
            projection_create.i_create_a_projection(
                self, example["input_data"])
            projection_create.the_projection_is(
                self, example["projection"])

    def test_scenario3(self):
        """
        Scenario: Successfully creating a batch projection:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create a pca
            And I wait until the pca is ready less than <model_wait> secs
            When I create a batch projection for the dataset with the pca
            And I wait until the batch projection is ready less than <batch_wait> secs
            And I download the created projections file to "<local_file>"
            Then the batch projection file is like "<projections_file>"
        """
        show_doc(self.test_scenario3)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
           "batch_wait", "local_file", "projections_file"]
        examples = [
            ['data/iris.csv', '30', '30', '50', '50',
             'tmp/batch_projections.csv', 'data/batch_projections.csv']]
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
            pca_create.i_create_a_pca(self)
            pca_create.the_pca_is_finished_in_less_than(
                self, example["model_wait"])
            batch_proj_create.i_create_a_batch_projection(self)
            batch_proj_create.the_batch_projection_is_finished_in_less_than(
                self, example["batch_wait"])
            batch_proj_create.i_download_projections_file(
                self, example["local_file"])
            batch_proj_create.i_check_projections(
                self, example["projections_file"])
