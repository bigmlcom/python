# -*- coding: utf-8 -*-
#
# Copyright 2018-2022 BigML
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


""" Creating optimls and fusions

"""
import sys

from .world import world, setup_module, teardown_module, show_doc, show_method
from . import create_model_steps as model_create
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create
from . import compare_predictions_steps as compare_pred
from . import create_prediction_steps as prediction_create
from . import create_evaluation_steps as evaluation_create
from . import create_batch_prediction_steps as batch_pred_create


class TestOptimlFusion(object):

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
            Scenario 1: Successfully creating an optiml from a dataset:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create an optiml from a dataset
                And I wait until the optiml is ready less than <model_wait> secs
                And I update the optiml name to "<optiml_name>"
                When I wait until the optiml is ready less than <model_wait> secs
                Then the optiml name is "<optiml_name>"
        """
        show_doc(self.test_scenario1)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "optiml_name"]
        examples = [
            ['data/iris.csv', '10', '10', '300', 'my new optiml name']]
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
            model_create.i_create_an_optiml_with_objective_and_params( \
                self, parms='{"max_training_time": %s, "model_types": '
                            '["model", "logisticregression"]}' % \
                    (int(float(example["model_wait"])/10) - 1))
            model_create.the_optiml_is_finished_in_less_than(
                self, example["model_wait"])
            model_create.i_update_optiml_name(self, example["optiml_name"])
            model_create.the_optiml_is_finished_in_less_than(
                self, example["model_wait"])
            model_create.i_check_optiml_name(self, example["optiml_name"])

    def test_scenario2(self):
        """
            Scenario 2: Successfully creating a fusion:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a model with "<model_conf>"
                And I wait until the model is ready less than <model_wait> secs
                And I create a model with "<params>"
                And I wait until the model is ready less than <model_wait> secs
                And I create a model with "<params>"
                And I wait until the model is ready less than <model_wait> secs
                And I retrieve a list of remote models tagged with "<tag>"
                And I create a fusion from a list of models
                And I wait until the fusion is ready less than <fusion_wait> secs
                And I update the fusion name to "<fusion_name>"
                When I wait until the fusion is ready less than <fusion_wait> secs
                And I create a prediction for "<input_data>"
                Then the fusion name is "<fusion_name>"
                And the prediction for "<objective_id>" is "<prediction>"
                And I create an evaluation for the fusion with the dataset
                And I wait until the evaluation is ready less than <evaluation_wait> secs
                Then the measured "<metric>" is <value>
        """
        show_doc(self.test_scenario2)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "fusion_wait", "evaluation_wait", "fusion_name",
                   "model_conf",  "tag", "input_data", "objective_id",
                   "prediction", "metric", "value"]
        examples = [
            ['data/iris.csv', '10', '10', '50', '50', '50',
             'my new fusion name',
             '{"tags":["my_fusion_2_tag"]}', 'my_fusion_2_tag',
             '{"petal width": 1.75, "petal length": 2.45}', "000004",
             "Iris-setosa", 'average_phi', '1.0']]
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
            model_create.i_create_a_model_with(
                self, example["model_conf"])
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            model_create.i_create_a_model_with(
                self, example["model_conf"])
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            model_create.i_create_a_model_with(
                self, example["model_conf"])
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            compare_pred.i_retrieve_a_list_of_remote_models(
                self, example["tag"])
            model_create.i_create_a_fusion(self)
            model_create.the_fusion_is_finished_in_less_than(
                self, example["model_wait"])
            model_create.i_update_fusion_name(self, example["fusion_name"])
            model_create.the_fusion_is_finished_in_less_than(
                self, example["fusion_wait"])
            model_create.i_check_fusion_name(self, example["fusion_name"])
            prediction_create.i_create_a_fusion_prediction(
                self, example["input_data"])
            prediction_create.the_prediction_is(
                self, example["objective_id"], example["prediction"])
            evaluation_create.i_create_an_evaluation_fusion(self)
            evaluation_create.the_evaluation_is_finished_in_less_than(
                self, example["evaluation_wait"])
            evaluation_create.the_measured_measure_is_value(
                self, example["metric"], example["value"])


    def test_scenario3(self):
        """
            Scenario 3: Successfully creating a fusion:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a model with "<model_conf>"
                And I wait until the model is ready less than <model_wait> secs
                And I create a model with "<model_conf>"
                And I wait until the model is ready less than <model_wait> secs
                And I create a model with "<model_conf>"
                And I wait until the model is ready less than <model_wait> secs
                And I retrieve a list of remote models tagged with "<tag>"
                And I create a fusion from a list of models
                And I wait until the fusion is ready less than <fusion_wait> secs
                When I create a batch prediction for the dataset with the fusion
                And I wait until the batch prediction is ready less than <batch_wait> secs
                And I download the created predictions file to "<local_file>"
                Then the batch prediction file is like "<predictions_file>"
        """
        show_doc(self.test_scenario3)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "fusion_wait", "batch_wait", "model_conf", "tag",
                   "local_file", "predictions_file"]
        examples = [
            ['data/iris.csv', '10', '10', '30', '30', '30',
             '{"tags":["my_fusion_3_tag"]}', 'my_fusion_3_tag',
              'tmp/batch_predictions.csv', 'data/batch_predictions_fs.csv']]
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
            model_create.i_create_a_model_with(
                self, example["model_conf"])
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            model_create.i_create_a_model_with(
                self, example["model_conf"])
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            model_create.i_create_a_model_with(
                self, example["model_conf"])
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            compare_pred.i_retrieve_a_list_of_remote_models(
                self, example["tag"])
            model_create.i_create_a_fusion(self)
            model_create.the_fusion_is_finished_in_less_than(
                self, example["fusion_wait"])
            batch_pred_create.i_create_a_batch_prediction_fusion(self)
            batch_pred_create.the_batch_prediction_is_finished_in_less_than(
                self, example["batch_wait"])
            batch_pred_create.i_download_predictions_file(
                self, example["local_file"])
            batch_pred_create.i_check_predictions(
                self, example["predictions_file"])

    def test_scenario4(self):
        """
            Scenario 4: Successfully creating a fusion:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a model with "<model_conf>"
                And I wait until the model is ready less than <model_wait> secs
                And I create a logistic regression with "<model_conf>"
                And I wait until the logistic regression is ready less than <model_wait> secs
                And I create a logistic regression with "<model_conf>"
                And I wait until the logistic regression is ready less than <model_wait> secs
                And I retrieve a list of remote logistic regression tagged with "<tag>"
                And I create a fusion from a list of models
                And I wait until the fusion is ready less than <fusion_wait> secs
                When I create a prediction for "<input_data>"
                Then the prediction for "<objective_id>" is "<prediction>"
                And the local logistic regression probability for the prediction is "<probability>"
                And I create a local fusion prediction for "<input_data>"
                Then the local fusion prediction is "<prediction>"
                And the local fusion probability for the prediction is "<probability>"
        """
        show_doc(self.test_scenario4)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "fusion_wait", "model_conf", "tag", "input_data",
                   "objective_id", "prediction", "probability"]
        examples = [
            ['data/iris.csv', '10', '10', '30', '30',
             '{"tags":["my_fusion_4_tag"], "missing_numerics": true}',
             'my_fusion_4_tag',
             '{"petal width": 1.75, "petal length": 2.45}', "000004",
             "Iris-setosa", '0.4726']]
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
            model_create.i_create_a_logistic_model_with_objective_and_parms(
                self, example["objective_id"], example["model_conf"])
            model_create.the_logistic_model_is_finished_in_less_than(
                self, example["model_wait"])
            model_create.i_create_a_logistic_model_with_objective_and_parms(
                self, example["objective_id"], example["model_conf"])
            model_create.the_logistic_model_is_finished_in_less_than(
                self, example["model_wait"])
            compare_pred.i_retrieve_a_list_of_remote_logistic_regressions(
                self, example["tag"])
            model_create.i_create_a_fusion(self)
            model_create.the_fusion_is_finished_in_less_than(
                self, example["fusion_wait"])
            compare_pred.i_create_a_local_fusion(self)
            prediction_create.i_create_a_fusion_prediction(
                self, example["input_data"])
            prediction_create.the_prediction_is(
                self, example["objective_id"], example["prediction"])
            prediction_create.the_fusion_probability_is(
                self, example["probability"])
            compare_pred.i_create_a_local_prediction(
                self, example["input_data"])
            compare_pred.the_local_prediction_is(
                self, example["prediction"])
            compare_pred.the_local_probability_is(
                self, example["probability"])

    def test_scenario5(self):
        """
            Scenario 5: Successfully creating a fusion:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a model with "<model_conf>"
                And I wait until the model is ready less than <model_wait> secs
                And I create a logistic regression with "<model_conf>"
                And I wait until the logistic regression is ready less than <model_wait> secs
                And I create a logistic regression with "<model_conf>"
                And I wait until the logistic regression is ready less than <model_wait> secs
                And I retrieve a list of remote logistic regression tagged with "<tag>"
                And I create a fusion from a list of models
                And I wait until the fusion is ready less than <fusion_wait> secs
                When I create a prediction for "<input_data>"
                Then the prediction for "<objective_id>" is "<prediction>"
                And the fusion probability for the prediction is "<probability>"
                And I create a local fusion prediction for "<input_data>"
                Then the local fusion prediction is "<prediction>"
                And the local fusion probability for the prediction is "<probability>"
        """
        show_doc(self.test_scenario5)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "fusion_wait", "model_conf1", "model_conf2", "tag",
                   "input_data", "objective_id", "prediction", "probability"]
        examples = [
            ['data/iris.csv', '10', '10', '30', '30',
             '{"tags":["my_fusion_5_tag"], "missing_numerics": true}',
             '{"tags":["my_fusion_5_tag"], "missing_numerics": false, '
             '"balance_fields": false }',
             'my_fusion_5_tag',
             '{"petal width": 1.75, "petal length": 2.45}',
             "000004",
             "Iris-setosa",
             '0.4726']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(self, example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"], shared=example["data"])
            model_create.i_create_a_logistic_model_with_objective_and_parms(
                self, example["objective_id"], example["model_conf1"])
            model_create.the_logistic_model_is_finished_in_less_than(
                self, example["model_wait"])
            model_create.i_create_a_logistic_model_with_objective_and_parms(
                self, example["objective_id"], example["model_conf2"])
            model_create.the_logistic_model_is_finished_in_less_than(
                self, example["model_wait"])
            compare_pred.i_retrieve_a_list_of_remote_logistic_regressions(
                self, example["tag"])
            model_create.i_create_a_fusion(self)
            model_create.the_fusion_is_finished_in_less_than(
                self, example["fusion_wait"])
            compare_pred.i_create_a_local_fusion(self)
            prediction_create.i_create_a_fusion_prediction(
                self, example["input_data"])
            prediction_create.the_prediction_is(
                self, example["objective_id"], example["prediction"])
            prediction_create.the_fusion_probability_is(
                self, example["probability"])
            compare_pred.i_create_a_local_prediction(
                self, example["input_data"])
            compare_pred.the_local_prediction_is(
                self, example["prediction"])
            compare_pred.the_local_probability_is(
                self, example["probability"])

    def test_scenario6(self):
        """
            Scenario 6: Successfully creating a fusion:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a model with "<model_conf>"
                And I wait until the model is ready less than <model_wait> secs
                And I create a logistic regression with "<model_conf1>"
                And I wait until the logistic regression is ready less than <model_wait> secs
                And I create a logistic regression with "<model_conf2>"
                And I wait until the logistic regression is ready less than <model_wait> secs
                And I retrieve a list of remote logistic regression tagged with "<tag>"
                And I create a fusion from a list of models and weights "<fusion_weights>"
                And I wait until the fusion is ready less than <fusion_wait> secs
                When I create a prediction for "<input_data>"
                Then the prediction for "<objective_id>" is "<prediction>"
                And the fusion probability for the prediction is "<probability>"
                And I create a local fusion prediction for "<input_data>"
                Then the local fusion prediction is "<prediction>"
                And the local fusion probability for the prediction is "<probability>"
        """
        show_doc(self.test_scenario6)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "fusion_wait", "model_conf1", "model_conf2", "tag",
                   "input_data", "objective_id",
                   "prediction", "probability", "fusion_weights"]
        examples = [
            ['data/iris.csv', '10', '10', '30', '30',
             '{"tags":["my_fusion_6_tag"], "missing_numerics": true}',
             '{"tags":["my_fusion_6_tag"], "missing_numerics": false, '
             '"balance_fields": false }',
             'my_fusion_6_tag',
             '{"petal width": 1.75, "petal length": 2.45}',
             "000004",
             "Iris-setosa",
             '0.4726', '[1, 2]']]
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
            model_create.i_create_a_logistic_model_with_objective_and_parms(
                self, example["objective_id"], example["model_conf1"])
            model_create.the_logistic_model_is_finished_in_less_than(
                self, example["model_wait"])
            model_create.i_create_a_logistic_model_with_objective_and_parms(
                self, example["objective_id"], example["model_conf2"])
            model_create.the_logistic_model_is_finished_in_less_than(
                self, example["model_wait"])
            compare_pred.i_retrieve_a_list_of_remote_logistic_regressions(
                self, example["tag"])
            model_create.i_create_a_fusion_with_weights(
                self, example["fusion_weights"])
            model_create.the_fusion_is_finished_in_less_than(
                self, example["fusion_wait"])
            compare_pred.i_create_a_local_fusion(self)
            prediction_create.i_create_a_fusion_prediction(
                self, example["input_data"])
            prediction_create.the_prediction_is(
                self, example["objective_id"], example["prediction"])
            prediction_create.the_fusion_probability_is(
                self, example["probability"])
            compare_pred.i_create_a_local_prediction(
                self, example["input_data"])
            compare_pred.the_local_prediction_is(self, example["prediction"])
            compare_pred.the_local_probability_is(self, example["probability"])
