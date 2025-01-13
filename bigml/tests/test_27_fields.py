# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,line-too-long,attribute-defined-outside-init
#pylint: disable=locally-disabled,unused-import
#
# Copyright 2015-2025 BigML
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


""" Testing Fields object properties

"""
from .world import world, setup_module, teardown_module, show_doc, \
    show_method
from . import fields_steps
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create


class TestFields:
    """Tests Fields class methods """

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
        Scenario: Successfully creating a Fields object:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a Fields object from the source with objective column "<objective_column>"
            Then the object id is "<objective_id>"
        """
        show_doc(self.test_scenario1)
        headers = ["data", "source_wait", "objective_column", "objective_id"]
        examples = [
            ['data/iris.csv', '10', '0', '000000']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            fields_steps.create_fields(self, example["objective_column"])
            fields_steps.check_objective(self, example["objective_id"])

    def test_scenario2(self):
        """
        Scenario: Successfully creating a Fields object and a summary fields file:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create a Fields object from the dataset with objective column "<objective_column>"
            And I export a summary fields file "<summary_file>"
            Then I check that the file "<summary_file>" is like "<expected_file>"
        """
        show_doc(self.test_scenario2)
        headers = ["data", "source_wait", "dataset_wait", "objective_column",
                   "summary_file", "expected_file"]
        examples = [
            ['data/iris.csv', '10', '10', '0', 'fields_summary.csv',
             'data/fields/fields_summary.csv']]
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
            fields_steps.create_fields_from_dataset(
                self, example["objective_column"])
            fields_steps.generate_summary(self, example["summary_file"])
            fields_steps.check_summary_like_expected(
                self, example["summary_file"], example["expected_file"])

    def test_scenario3(self):
        """
        Scenario: Successfully creating a Fields object and a modified fields structure from a file:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <time_1> secs
            And I create a dataset
            And I wait until the dataset is ready less than <time_2> secs
            And I create a Fields object from the dataset with objective column "<objective_column>"
            And I import a summary fields file "<summary_file>" as a fields structure
            And I clone the source to open it
            And I update the source with the file "<summary_file>"
            And I update the dataset with the file "<summary_file>"
            Then I check the new field structure has field "<field_id>" as "<optype>"
            And I check the source has field "<field_id>" as "<optype>"
        """
        show_doc(self.test_scenario3)
        headers = ["data", "source_wait", "dataset_wait", "objective_column",
                   "summary_file", "field_id", "optype"]
        examples = [
            ['data/iris.csv', '10', '10', '0',
             'data/fields/fields_summary_modified.csv', '000000',
             'categorical']]
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
            fields_steps.create_fields_from_dataset(
                self, example["objective_column"])
            source_create.clone_source(self, world.source["resource"])
            source_create.the_source_is_finished(self, example["source_wait"])
            fields_steps.import_summary_file(self, example["summary_file"])
            fields_steps.update_with_summary_file(
                self, world.source, example["summary_file"])
            fields_steps.update_with_summary_file(
                self, world.dataset, example["summary_file"])
            fields_steps.check_field_type(
                self, example["field_id"], example["optype"])
            fields_steps.check_resource_field_type(
                self, world.source, example["field_id"], example["optype"])
