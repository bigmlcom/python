# -*- coding: utf-8 -*-
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
import sys
import os

from .world import world, setup_module, teardown_module, show_doc, \
    show_method, delete_local
from . import compare_pipeline_steps as pipeline_compare


class TestLocalPipeline(object):

    def setup(self):
        """
            Debug information
        """
        print("\n-------------------\nTests in: %s\n" % __name__)

    def teardown(self):
        """
            Debug information
        """
        delete_local()
        print("\nEnd of tests in: %s\n-------------------\n" % __name__)

    def test_scenario1(self):
        """
            Scenario 1: Successfully creating a local pipeline from a model and anomaly detector:
                Given I expand the zip file "<pipeline_file>" that contain "<models_list>"
                And I create a local pipeline for "<models_list>" named "<name>"
                Then the transformed data for "<input_data>" is "<output_data>"
        """
        show_doc(self.test_scenario1)
        headers = ["pipeline_file", "models_list", "name", "input_data",
                   "output_data"]
        examples = [
            ['bigml/tests/pipeline3.zip',
             '["anomaly/631a6a968f679a2d2d000319",'
             ' "model/631a6a6f8f679a2d31000445"]',
             "pipeline3",
             '{"plasma glucose": 120, "age": 30, "bmi": 46}',
             '{"plasma glucose": 120, "age": 30, "glucose half": 60,'
             ' "age_range": "2nd third", "bmi": 46,'
             ' "score": 0.8545622319429063,'
             ' "prediction": "false", "probability": 0.6586746586746587}']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            pipeline_compare.i_expand_file_with_models_list(
                self, example["pipeline_file"], example["models_list"])
            pipeline_compare.i_create_a_local_pipeline_from_models_list(
                self, example["models_list"], example["name"],
                storage=os.path.dirname(example["pipeline_file"]))
            pipeline_compare.the_pipeline_transformed_data_is(
                self, example["input_data"], example["output_data"])

    def test_scenario2(self):
        """
            Scenario 2: Successfully creating a local pipeline from two BMLPipelines
                Given I expand the zip file "<pipeline_file>" that contain "<models_list>"
                And I create a local pipeline for "<model1>" named "<name1>"
                And I create a local pipeline for "<model2>" named "<name2>"
                And I create a local pipeline "<name3>" for both pipelines
                Then the transformed data for "<input_data>" is "<output_data>"
        """
        show_doc(self.test_scenario1)
        headers = ["pipeline_file", "models_list", "model1", "name1",
                   "model2", "name2", "name", "input_data", "output_data"]
        examples = [
            ['bigml/tests/pipeline3.zip',
             '["anomaly/631a6a968f679a2d2d000319",'
             ' "model/631a6a6f8f679a2d31000445"]',
             '["model/631a6a6f8f679a2d31000445"]',
             "pipeline1",
             '["anomaly/631a6a968f679a2d2d000319"]',
             "pipeline2",
             "pipeline3",
             '{"plasma glucose": 120, "age": 30, "bmi": 46}',
             '{"plasma glucose": 120, "age": 30, "glucose half": 60,'
             ' "age_range": "2nd third", "bmi": 46,'
             ' "score": 0.8545622319429063,'
             ' "prediction": "false", "probability": 0.6586746586746587}']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            pipeline_compare.i_expand_file_with_models_list(
                self, example["pipeline_file"], example["models_list"])
            pipe1 = pipeline_compare.i_create_a_local_pipeline_from_models_list(
                self, example["model1"], example["name1"],
                storage=os.path.dirname(example["pipeline_file"]))
            pipe2 = pipeline_compare.i_create_a_local_pipeline_from_models_list(
                self, example["model2"], example["name2"],
                storage=os.path.dirname(example["pipeline_file"]))
            pipeline_compare.i_create_composed_pipeline(self, [pipe1, pipe2],
                                                        example["name"])
            pipeline_compare.the_pipeline_transformed_data_is(
                self, example["input_data"], example["output_data"])
