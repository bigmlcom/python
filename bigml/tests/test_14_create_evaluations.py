# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,line-too-long,attribute-defined-outside-init
#pylint: disable=locally-disabled,unused-import
#
# Copyright 2015-2023 BigML
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


""" Creating evaluation

"""
from .world import world, setup_module, teardown_module, show_doc, \
    show_method
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create
from . import create_model_steps as model_create
from . import create_ensemble_steps as ensemble_create
from . import create_evaluation_steps as evaluation_create

class TestEvaluation:
    """Testing Evaluation methods"""

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
        Scenario1: Successfully creating an evaluation:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create a model
            And I wait until the model is ready less than <model_wait> secs
            When I create an evaluation for the model with the dataset
            And I wait until the evaluation is ready less than <evaluation_time> secs
            Then the measured "<metric>" is <value>
        """
        show_doc(self.test_scenario1)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "evaluation_wait", "metric", "value"]
        examples = [
            ['data/iris.csv', '50', '50', '50', '50', 'average_phi', '1']]
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
            model_create.i_create_a_model(self, shared=example["data"])
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"], shared=example["data"])
            evaluation_create.i_create_an_evaluation(self)
            evaluation_create.the_evaluation_is_finished_in_less_than(
                self, example["evaluation_wait"])
            evaluation_create.the_measured_measure_is_value(
                self, example["metric"], example["value"])

    def test_scenario2(self):
        """
        Scenario2: Successfully creating an evaluation for an ensemble:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create an ensemble of <number_of_models> models
            And I wait until the ensemble is ready less than <model_wait> secs
            When I create an evaluation for the ensemble with the dataset and "evaluation_conf"
            And I wait until the evaluation is ready less than <evaluation_wait> secs
            Then the measured "<metric>" is <value>
        """
        show_doc(self.test_scenario2)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "evaluation_wait", "number_of_models",
                   "metric", "value", "evaluation_conf"]
        examples = [
            ['data/iris.csv', '50', '50', '80', '80', '5', 'average_phi',
             '0.98029', {"combiner": 0}],
            ['data/iris.csv', '50', '50', '80', '80', '5', 'average_phi',
             '0.95061', {"combiner": 1}],
            ['data/iris.csv', '50', '50', '80', '80', '5', 'average_phi',
             '0.98029', {"combiner": 2}],
            ['data/iris.csv', '50', '50', '80', '80', '5', 'average_phi',
             '0.98029', {"operating_kind": "votes"}],
            ['data/iris.csv', '50', '50', '80', '80', '5', 'average_phi',
             '0.97064', {"operating_kind": "probability"}],
            ['data/iris.csv', '50', '50', '80', '80', '5', 'average_phi',
             '0.95061', {"operating_kind": "confidence"}]]
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
            evaluation_create.i_create_an_evaluation_ensemble(
                self, example["evaluation_conf"])
            evaluation_create.the_evaluation_is_finished_in_less_than(
                self, example["evaluation_wait"])
            evaluation_create.the_measured_measure_is_value(
                self, example["metric"], example["value"])

    def test_scenario3(self):
        """
        Scenario3: Successfully creating an evaluation for a logistic regression:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create a logistic regression
            And I wait until the logistic regression is ready less than <model_wait> secs
            When I create an evaluation for the logistic regression with the dataset
            And I wait until the evaluation is ready less than <evaluation_wait> secs
            Then the measured "<metric>" is <value>
        """
        show_doc(self.test_scenario3)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "evaluation_wait", "metric", "value"]
        examples = [
            ['data/iris.csv', '50', '50', '800', '80', 'average_phi',
             '0.89054']]
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
            model_create.i_create_a_logistic_model(
                self, shared=example["data"])
            model_create.the_logistic_model_is_finished_in_less_than(
                self, example["model_wait"], shared=example["data"])
            evaluation_create.i_create_an_evaluation_logistic(
                self)
            evaluation_create.the_evaluation_is_finished_in_less_than(
                self, example["evaluation_wait"])
            evaluation_create.the_measured_measure_is_value(
                self, example["metric"], example["value"])

    def test_scenario4(self):
        """
        Scenario4: Successfully creating an evaluation for a deepnet:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <time_1> secs
            And I create a dataset
            And I wait until the dataset is ready less than <time_2> secs
            And I create a deepnet
            And I wait until the deepnet is ready less than <time_3> secs
            When I create an evaluation for the deepnet with the dataset
            And I wait until the evaluation is ready less than <time_4> secs
            Then the measured "<measure>" is <value>
        """
        show_doc(self.test_scenario4)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "evaluation_wait", "metric", "value"]
        examples = [
            ['data/iris.csv', '50', '50', '800', '80', 'average_phi',
             '0.97007']]
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
            model_create.i_create_a_deepnet(self, shared=example["data"])
            model_create.the_deepnet_is_finished_in_less_than(
                self, example["model_wait"], shared=example["data"])
            evaluation_create.i_create_an_evaluation_deepnet(
                self)
            evaluation_create.the_evaluation_is_finished_in_less_than(
                self, example["evaluation_wait"])
            evaluation_create.the_measured_measure_is_value(
                self, example["metric"], example["value"])

    def test_scenario5(self):
        """
        Scenario5: Successfully instantiating Evaluation:
            Given a stored evaluation "<data>" file
            When I create an Evaluation for the JSON
            Then the measured "<metric>" is <value>
        """
        show_doc(self.test_scenario5)
        headers = ["data", "metric", "value"]
        examples = [
            ['data/classification_evaluation.json', 'phi',
             0.64837],
            ['data/classification_evaluation.json', 'accuracy',
             0.91791],
            ['data/classification_evaluation.json', 'precision',
             0.86639],
            ['data/regression_evaluation.json', 'r_squared',
             0.9288]]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            evaluation_create.i_create_a_local_evaluation(
                self, example["data"])
            evaluation_create.the_local_metric_is_value(
                self, example["metric"], example["value"])
