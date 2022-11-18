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


""" Creating association

"""
import sys

from .world import world, setup_module, teardown_module, show_doc, \
    show_method, delete_local
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create
from . import create_association_steps as association_create

class TestAssociation(object):

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
            Scenario: Successfully creating associations from a dataset:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create associations from a dataset
                And I wait until the association is ready less than <model_wait> secs
                And I update the association name to "<association_name>"
                When I wait until the association is ready less than <model_wait> secs
                Then the association name is "<association_name>"
        """
        show_doc(self.test_scenario1)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "association_name"]
        examples = [
            ['data/iris.csv', '10', '10', '50', 'my new association name']]
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
            association_create.i_create_an_association_from_dataset(self)
            association_create.the_association_is_finished_in_less_than(
                self, example["model_wait"])
            association_create.i_update_association_name(
                self, example["association_name"])
            association_create.the_association_is_finished_in_less_than(
                self, example["model_wait"])
            association_create.i_check_association_name(
                self, example["association_name"])

    def test_scenario2(self):
        """
            Scenario: Successfully creating local association object:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create an association from a dataset
                And I wait until the association is ready less than <model_wait> secs
                And I create a local association
                When I get the rules for <"item_list">
                Then the first rule is "<JSON_rule>"
        """
        show_doc(self.test_scenario2)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "item_list", "JSON_rule"]
        examples = [
            ['data/tiny_mushrooms.csv', '10', '20', '50', ["Edible"],
             {'p_value': 5.26971e-31, 'confidence': 1,
              'rhs_cover': [0.488, 122], 'leverage': 0.24986,
              'rhs': [19], 'rule_id': '000002', 'lift': 2.04918,
              'lhs': [0, 21, 16, 7], 'lhs_cover': [0.488, 122],
              'support': [0.488, 122]}]]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(self, example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            dataset_create.i_create_a_dataset(self, shared=example["data"])
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"], shared=example["data"])
            association_create.i_create_an_association_from_dataset(self)
            association_create.the_association_is_finished_in_less_than(
                self, example["model_wait"])
            association_create.i_create_a_local_association(self)
            association_create.i_get_rules_for_item_list(
                self, example["item_list"])
            association_create.the_first_rule_is(
                self, example["JSON_rule"])

    def test_scenario3(self):
        """
            Scenario: Successfully creating local association object:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create an association with search strategy "<strategy>" from a dataset
                And I wait until the association is ready less than <model_wait> secs
                And I create a local association
                When I get the rules for <"item_list">
                Then the first rule is "<JSON_rule>"
        """
        show_doc(self.test_scenario2)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "item_list", "JSON_rule", "strategy"]
        examples = [
            ['data/tiny_mushrooms.csv', '10', '20', '50', ["Edible"],
             {'p_value': 2.08358e-17, 'confidence': 0.79279,
              'rhs_cover': [0.704, 176], 'leverage': 0.07885,
              'rhs': [11], 'rule_id': '000007', 'lift': 1.12613,
              'lhs': [0], 'lhs_cover': [0.888, 222],
              'support': [0.704, 176]}, 'lhs_cover']]
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
            association_create.i_create_an_association_with_strategy_from_dataset(
                self, example["strategy"])
            association_create.the_association_is_finished_in_less_than(
                self, example["model_wait"])
            association_create.i_create_a_local_association(self)
            association_create.i_get_rules_for_item_list(
                self, example["item_list"])
            association_create.the_first_rule_is(self, example["JSON_rule"])
