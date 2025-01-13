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


""" Creating local ensemble predictions

"""
from .world import world, setup_module, teardown_module, show_doc, \
    show_method
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create
from . import create_model_steps as model_create
from . import create_ensemble_steps as ensemble_create
from . import create_prediction_steps as prediction_create
from . import compare_predictions_steps as compare_pred


class TestEnsemblePrediction:
    """Testing local ensemble prediction"""

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
        Scenario: Successfully creating a local prediction from an Ensemble:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create an ensemble of <number_of_models> models
            And I wait until the ensemble is ready less than <model_wait> secs
            And I create a local Ensemble
            When I create a local ensemble prediction with probabilities for "<input_data>"
            Then the local prediction is "<prediction>"
            And the local prediction's confidence is "<confidence>"
            And the local probabilities are "<probabilities>"
        """
        show_doc(self.test_scenario1)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "number_of_models", "input_data",
                   "prediction", "confidence", "probabilities"]
        examples = [
            ['data/iris.csv', '10', '10', '50', '5',
             '{"petal width": 0.5}', 'Iris-versicolor', '0.415',
             '["0.3403", "0.4150", "0.2447"]' ]]
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
            ensemble_shared = "%s_%s" % (example["data"],
                example["number_of_models"])
            ensemble_create.i_create_an_ensemble(
                self, example["number_of_models"], shared=ensemble_shared)
            ensemble_create.the_ensemble_is_finished_in_less_than(
                self, example["model_wait"], shared=ensemble_shared)
            ensemble_create.create_local_ensemble(self)
            prediction_create.create_local_ensemble_prediction_probabilities(
                self, example["input_data"])
            compare_pred.the_local_prediction_is(self, example["prediction"])
            compare_pred.the_local_prediction_confidence_is(
                self, example["confidence"])
            compare_pred.the_local_probabilities_are(
                self, example["probabilities"])

    def test_scenario2(self):
        """
        Scenario: Successfully obtaining field importance from an Ensemble:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create a model with "<model_conf1>"
            And I wait until the model is ready less than <model_wait> secs
            And I create a model with "<model_conf2>"
            And I wait until the model is ready less than <model_wait> secs
            And I create a model with "<model_conf3>"
            And I wait until the model is ready less than <model_wait> secs
            When I create a local Ensemble with the last <number_of_models> models
            Then the field importance text is <field_importance>
        """
        show_doc(self.test_scenario2)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "model_conf1", "model_conf2", "model_conf3",
                   "number_of_models", "field_importance"]
        examples = [
            ['data/iris.csv', '10', '10', '20',
             '{"input_fields": ["000000", "000001","000003", "000004"]}',
             '{"input_fields": ["000000", "000001","000002", "000004"]}',
             '{"input_fields": ["000000", "000001","000002", "000003",'
             ' "000004"]}', '3',
             '[["000002", 0.5269933333333333], ["000003", 0.38936],'
             ' ["000000", 0.04662333333333333],'
             '["000001", 0.037026666666666666]]']]
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
            model_create.i_create_a_model_with(self, example["model_conf1"])
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            model_create.i_create_a_model_with(self, example["model_conf2"])
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            model_create.i_create_a_model_with(self, example["model_conf3"])
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            ensemble_create.create_local_ensemble_with_list(
                self, example["number_of_models"])
            ensemble_create.field_importance_print(
                self, example["field_importance"])

    def test_scenario3(self):
        """
        Scenario: Successfully creating a local prediction from an Ensemble adding confidence:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create an ensemble of <number_of_models> models
            And I wait until the ensemble is ready less than <model_wait> secs
            And I create a local Ensemble
            When I create a local ensemble prediction for "<input_data>" in JSON adding confidence
            Then the local prediction is "<prediction>"
            And the local prediction's confidence is "<confidence>"
        """
        show_doc(self.test_scenario3)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "number_of_models", "input_data", "prediction",
                   "confidence"]
        examples = [
            ['data/iris.csv', '10', '10', '50', '5',
             '{"petal width": 0.5}', 'Iris-versicolor', '0.415']]
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
            ensemble_shared = "%s_%s" % (example["data"],
                example["number_of_models"])
            ensemble_create.i_create_an_ensemble(
                self, example["number_of_models"], shared=ensemble_shared)
            ensemble_create.the_ensemble_is_finished_in_less_than(
                self, example["model_wait"], shared=ensemble_shared)
            ensemble_create.create_local_ensemble(self)
            prediction_create.create_local_ensemble_prediction_add_confidence(
                self, example["input_data"])
            compare_pred.the_local_prediction_is(self, example["prediction"])
            compare_pred.the_local_prediction_confidence_is(
                self, example["confidence"])

    def test_scenario4(self):
        """
        Scenario: Successfully obtaining field importance from an Ensemble created from local models:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create a model with "<model_conf1>"
            And I wait until the model is ready less than <model_wait> secs
            And I create a model with "<model_conf2>"
            And I wait until the model is ready less than <model_wait> secs
            And I create a model with "<model_conf3>"
            And I wait until the model is ready less than <model_wait> secs
            When I create a local Ensemble with the last <number_of_models> local models
            Then the field importance text is <field_importance>
        """
        show_doc(self.test_scenario4)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "model_conf1", "model_conf2", "model_conf3",
                   "number_of_models", "field_importance"]
        examples = [
            ['data/iris.csv', '10', '10', '30',
             '{"input_fields": ["000000", "000001","000003", "000004"]}',
             '{"input_fields": ["000000", "000001","000002", "000004"]}',
             '{"input_fields": ["000000", "000001","000002", "000003",'
             ' "000004"]}', '3',
             '[["000002", 0.5269933333333333], ["000003", 0.38936],'
             ' ["000000", 0.04662333333333333], '
             '["000001", 0.037026666666666666]]']]
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
            model_create.i_create_a_model_with(self, example["model_conf1"])
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            model_create.i_create_a_model_with(self, example["model_conf2"])
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            model_create.i_create_a_model_with(self, example["model_conf3"])
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            ensemble_create.create_local_ensemble_with_list_of_local_models(
                self, example["number_of_models"])
            ensemble_create.field_importance_print(
                self, example["field_importance"])

    def test_scenario5(self):
        """
        Scenario: Successfully creating a local prediction from an Ensemble:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create an ensemble of <number_of_models> models
            And I wait until the ensemble is ready less than <model_wait> secs
            And I create a local Ensemble
            When I create a local ensemble prediction using median with confidence for "<input_data>"
            Then the local prediction is "<prediction>"
        """
        show_doc(self.test_scenario5)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "number_of_models", "input_data", "prediction"]
        examples = [
            ['data/grades.csv', '30', '30', '50', '2', '{}', 69.0934]]
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
            ensemble_shared = "%s_%s" % (example["data"],
                example["number_of_models"])
            ensemble_create.i_create_an_ensemble(
                self, example["number_of_models"], shared=ensemble_shared)
            ensemble_create.the_ensemble_is_finished_in_less_than(
                self, example["model_wait"], shared=ensemble_shared)
            ensemble_create.create_local_ensemble(self)
            prediction_create.create_local_ensemble_prediction_using_median_with_confidence(
                self, example["input_data"])
            compare_pred.the_local_prediction_is(self, example["prediction"])
