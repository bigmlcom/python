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
import json

from .world import world, setup_module, teardown_module, show_doc, \
    show_method, delete_local
from . import compare_pipeline_steps as pipeline_compare
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create
from . import create_anomaly_steps as anomaly_create
from . import create_model_steps as model_create
from . import create_ensemble_steps as ensemble_create
from . import create_linear_steps as linear_create
from . import create_prediction_steps as prediction_create
from . import compare_predictions_steps as prediction_compare


class TestLocalPipeline(object):

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
             ' "score": 0.85456,'
             ' "prediction": "false", "probability": 0.6586746586746587}']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            pipeline_compare.i_expand_file_with_models_list(
                self, example["pipeline_file"], example["models_list"])
            pipeline_compare.i_create_a_local_pipeline_from_models_list(
                self, example["models_list"], example["name"],
                storage=os.path.splitext(example["pipeline_file"])[0])
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
        show_doc(self.test_scenario2)
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
             ' "score": 0.85456,'
             ' "prediction": "false", "probability": 0.6586746586746587}']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            pipeline_compare.i_expand_file_with_models_list(
                self, example["pipeline_file"], example["models_list"])
            pipe1 = pipeline_compare.i_create_a_local_pipeline_from_models_list(
                self, example["model1"], example["name1"],
                storage=os.path.splitext(example["pipeline_file"])[0])
            pipe2 = pipeline_compare.i_create_a_local_pipeline_from_models_list(
                self, example["model2"], example["name2"],
                storage=os.path.splitext(example["pipeline_file"])[0])
            pipeline_compare.i_create_composed_pipeline(self, [pipe1, pipe2],
                                                        example["name"])
            pipeline_compare.the_pipeline_transformed_data_is(
                self, example["input_data"], example["output_data"])

    def test_scenario3(self):
        """
            Scenario: Successfully comparing remote and local predictions
                      with raw date input for linear regression:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a linear regression
                And I wait until the linear regression is ready
                less than <model_wait> secs
                And I create a local pipeline for the linear regression named "<name>"
                When I create a prediction for "<input_data>"
                Then the prediction for "<objective_id>" is "<prediction>"
                And the prediction in the transformed data for "<input_data>" is "<prediction>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "input_data", "objective_id", "prediction", "name"]
        examples = [
            ['data/dates2.csv', '20', '20', '25',
             '{"time-1": "1910-05-08T19:10:23.106", "cat-0":"cat2"}',
             '000002',  -0.01284, "pipeline1"],
            ['data/dates2.csv', '20', '20', '25',
             '{"time-1": "1920-06-30T20:21:20.320", "cat-0":"cat1"}',
             '000002', -0.09459, "pipeline2"],
            ['data/dates2.csv', '20', '20', '25',
             '{"time-1": "1932-01-30T19:24:11.440",  "cat-0":"cat2"}',
             '000002', -0.02259, "pipeline3"],
            ['data/dates2.csv', '20', '20', '25',
             '{"time-1": "1950-11-06T05:34:05.252", "cat-0":"cat1"}',
             '000002', -0.06754, "pipeline4"],
            ['data/dates2.csv', '20', '20', '25',
             '{"time-1": "2001-01-05T23:04:04.693", "cat-0":"cat2"}',
             '000002', 0.05204, "pipeline5"],
            ['data/dates2.csv', '20', '20', '25',
             '{"time-1": "2011-04-01T00:16:45.747", "cat-0":"cat2"}',
             '000002', 0.05878, "pipeline6"]]
        show_doc(self.test_scenario3)

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
            linear_create.i_create_a_linear_regression(
                self, shared=example["data"])
            linear_create.the_linear_regression_is_finished_in_less_than(
                self, example["model_wait"], shared=example["data"])
            pipe1 = pipeline_compare.i_create_a_local_pipeline_from_models_list(
                self, [world.linear_regression["resource"]], example["name"])
            prediction_create.i_create_a_linear_prediction(
                self, example["input_data"])
            prediction_create.the_prediction_is(
                self, example["objective_id"], example["prediction"])
            pipeline_compare.the_pipeline_result_key_is(
                self, example["input_data"], "prediction",
                example["prediction"])

    def test_scenario4(self):
        """
            Scenario: Successfully comparing remote and local predictions
                      with raw date input for deepnet:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a deepnet
                And I wait until the deepnet is ready less than <model_wait> secs
                And I create a local pipeline for the deepnet named "<name>"
                When I create a prediction for "<input_data>"
                Then the prediction for "<objective_id>" is "<prediction>"
                And the prediction in the transformed data for "<input_data>" is "<prediction>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "input_data", "objective_id", "prediction", "name"]
        examples = [
            ['data/dates2.csv', '20', '45', '160',
             '{"time-1": "1910-05-08T19:10:23.106", "cat-0":"cat2"}',
             '000002', -0.02616, "pipeline1"],
            ['data/dates2.csv', '20', '45', '160',
             '{"time-1": "2011-04-01T00:16:45.747", "cat-0":"cat2"}',
             '000002', 0.13352, "pipeline2"],
            ['data/dates2.csv', '20', '45', '160',
             '{"time-1": "1969-W29-1T17:36:39Z", "cat-0":"cat1"}',
             '000002', 0.10071, "pipeline3"],
            ['data/dates2.csv', '20', '45', '160',
             '{"time-1": "1920-06-45T20:21:20.320", "cat-0":"cat1"}',
             '000002', 0.10071, "pipeline4"],
            ['data/dates2.csv', '20', '45', '160',
             '{"time-1": "2001-01-05T23:04:04.693", "cat-0":"cat2"}',
             '000002', 0.15235, "pipeline5"],
            ['data/dates2.csv', '20', '45', '160',
             '{"time-1": "1950-11-06T05:34:05.602", "cat-0":"cat1"}',
             '000002', -0.07686, "pipeline6"],
            ['data/dates2.csv', '20', '45', '160',
             '{"time-1": "1932-01-30T19:24:11.440",  "cat-0":"cat2"}',
             '000002', 0.0017, "pipeline7"],
            ['data/dates2.csv', '20', '45', '160',
             '{"time-1": "Mon Jul 14 17:36 +0000 1969", "cat-0":"cat1"}',
             '000002', 0.10071, "pipeline8"]]
        show_doc(self.test_scenario4)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            dataset_create.i_create_a_dataset(self, shared=example["data"])
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"])
            deepnet_shared = "%s_no_sug" % example["data"]
            model_create.i_create_a_no_suggest_deepnet(
                self, shared=deepnet_shared)
            model_create.the_deepnet_is_finished_in_less_than(
                self, example["model_wait"], shared=deepnet_shared)
            pipe1 = pipeline_compare.i_create_a_local_pipeline_from_models_list(
                self, [world.deepnet["resource"]], example["name"])
            prediction_create.i_create_a_deepnet_prediction(
                self, example["input_data"])
            prediction_create.the_prediction_is(
                self, example["objective_id"], example["prediction"],
                precision=4)
            pipeline_compare.the_pipeline_result_key_is(
                self, example["input_data"], "prediction",
                example["prediction"], precision=4)

    def test_scenario5(self):
        """
            Scenario: Successfully comparing remote and local predictions
                      with raw input for deepnets with images:
                Given I create an annotated images data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a deepnet with parms <model_conf>
                And I wait until the deepnet is ready
                less than <time_3> secs
                And I create a local pipeline for the deepnet named "<name>"
                When I create a prediction for "<input_data>"
                Then the prediction for "<objective>" is "<prediction>"
                When I create a prediction for "<input_data>"
                Then the prediction for "<objective_id>" is "<prediction>"
                And the prediction in the transformed data for "<input_data>" is "<prediction>"
                And the probability in the transformed data for "<input_data>" is "<probability>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "input_data", "objective_id", "model_conf", "image_fields",
                   "name"]
        examples = [
            ['data/images/metadata.json', '500', '500', '600',
             '{"image_id": "data/fruits1e.jpg", "label":"f1"}',
             '100003', {"objective_field": "100003",
                        "number_of_hidden_layers": 1,
                        "suggest_structure": False,
                        "missing_numerics": True,
                        "max_training_time": 100,
                        "hidden_layers": [{
                            "activation_function": "tanh",
                            "number_of_nodes": 10}]},
             ['image_id'], "pipeline1"]]
        show_doc(self.test_scenario5)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_create_annotated_source(
                self,
                example["data"],
                args={"image_analysis": {"enabled": False,
                                         "extracted_features": []}})
            source_create.the_source_is_finished(
                self, example["source_wait"])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"])
            model_create.i_create_a_deepnet_with_objective_and_params(
                self, example["objective_id"],
                json.dumps(example["model_conf"]))
            model_create.the_deepnet_is_finished_in_less_than(
                self, example["model_wait"])
            pipe1 = pipeline_compare.i_create_a_local_pipeline_from_models_list(
                self, [world.deepnet["resource"]], example["name"])
            prediction_create.i_create_a_deepnet_prediction(
                self, example["input_data"], example["image_fields"])
            prediction = world.prediction["output"]
            probability = world.prediction["probability"]
            pipe1 = pipeline_compare.i_create_a_local_pipeline_from_models_list(
                self, [world.deepnet["resource"]], example["name"])
            pipeline_compare.the_pipeline_result_key_is(
                self, example["input_data"], "prediction", prediction,
                precision=4)
            pipeline_compare.the_pipeline_result_key_is(
                self, example["input_data"], "probability", probability,
                precision=2)

    def test_scenario6(self):
        """
            Scenario: Successfully comparing remote and local anomaly scores
                      with raw input for dataset with images:
                Given I create an annotated images data source uploading a "<data>" file and <extracted_features>

                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create an anomaly detector
                And I wait until the anomaly is ready
                less than <anomaly_wait> secs
                And I create a local pipeline for the anomaly detector named "<name>"
                When I create an anomaly score for "<input_data>"
                Then the anomaly score is "<score>"
                And the anomaly score in the transformed data for "<input_data>" is "<score>"
        """
        headers = ["data", "extracted_features", "source_wait", "dataset_wait",
                   "anomaly_wait", "input_data", "score", "name"]
        examples = [
            ['data/images/fruits_hist.zip',
             ["dimensions", "average_pixels", "level_histogram",
              "histogram_of_gradients", ["wavelet_subbands", 5],
              ["pretrained_cnn", "mobilenetv2"]],
              '500', '500', '600',
             '{"image_id": "data/fruits1e.jpg"}', 0.39902, "pipeline1"]]
        show_doc(self.test_scenario6)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file_with_args(
                self,
                example["data"],
                args=json.dumps({"image_analysis": {
                    "enabled": True,
                    "extracted_features": example["extracted_features"]}}))
            source_create.the_source_is_finished(
                self, example["source_wait"])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"])
            anomaly_create.i_create_an_anomaly(self)
            anomaly_create.the_anomaly_is_finished_in_less_than(
                self, example["anomaly_wait"])
            pipe1 = pipeline_compare.i_create_a_local_pipeline_from_models_list(
                self, [world.anomaly["resource"]], example["name"])
            prediction_create.i_create_an_anomaly_score(
                self, example["input_data"])
            score = world.anomaly_score["score"]
            prediction_create.the_anomaly_score_is(
                self, world.anomaly_score["score"])
            pipeline_compare.the_pipeline_result_key_is(
                self, example["input_data"], "score", score)
