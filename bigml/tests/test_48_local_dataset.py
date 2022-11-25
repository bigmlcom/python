# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,line-too-long,attribute-defined-outside-init
#pylint: disable=locally-disabled,unused-import
#
# Copyright 2022 BigML
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


""" Testing local dataset transformations

"""
from .world import world, setup_module, teardown_module, show_doc, \
    show_method
from . import compare_dataset_steps as dataset_compare


class TestLocalDataset:
    """Testing Local class for datasets"""

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
        Scenario 1: Successfully creating a transformation from a local dataset in a json file:
            Given I create a local dataset from a "<dataset_file>" file
            Then the transformed data for "<input_data>" is "<output_data>"
        """
        show_doc(self.test_scenario1)
        headers = ["dataset_file", "input_data", "output_data"]
        examples = [
            ['bigml/tests/my_dataset/my_flatline_ds.json',
             '{"plasma glucose": 120, "age": 30, "bmi": 46}',
             '{"plasma glucose": 120, "age": 30, "glucose half": 60}']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            dataset_compare.i_create_a_local_dataset_from_file(
                self, example["dataset_file"])
            dataset_compare.the_transformed_data_is(
                self, example["input_data"], example["output_data"])
