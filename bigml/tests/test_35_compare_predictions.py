# -*- coding: utf-8 -*-
#
# Copyright 2017-2022 BigML
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


""" Comparing remote and local predictions

"""
import sys

from .world import world, setup_module, teardown_module, show_doc, show_method
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create
from . import create_model_steps as model_create
from . import create_time_series_steps as time_series_create
from . import create_forecast_steps as forecast_create
from . import compare_forecasts_steps as forecast_compare
from . import create_pca_steps as pca_create
from . import create_projection_steps as projection_create
from . import compare_predictions_steps as compare_predictions


class TestComparePrediction(object):

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


    def test_scenario4(self):
        """
            Scenario: Successfully comparing forecasts from time series with trivial models
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a time series with "<model_conf>"
                And I wait until the time series is ready less than <model_wait> secs
                And I create a local time series
                When I create a forecast for "<input_data>"
                Then the forecast is "<forecast>"
                And I create a local forecast for "<input_data>"
                Then the local forecast is "<forecast>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "input_data", "forecast", "model_conf"]
        examples = [
            ['data/grades.csv', '10', '100', '100',
             '{"000005": {"horizon": 5, "ets_models": {"names": ["naive"]}}}',
             '{"000005": [{"point_forecast": [61.39, 61.39, 61.39, 61.39, '
             '61.39], "model": "naive"}]}',
             '{"objective_fields": ["000001", "000005"], "period": 1}'],
            ['data/grades.csv', '10', '100', '100',
             '{"000005": {"horizon": 5, "ets_models": {"names": ["naive"]}}}',
             '{"000005": [{"point_forecast": [78.89, 61.39, 78.89, 61.39, '
             '78.89], "model": "naive"}]}',
             '{"objective_fields": ["000001", "000005"], "period": 2}'],
            ['data/grades.csv', '10', '100', '100',
             '{"000005": {"horizon": 5, "ets_models": {"names": ["mean"]}}}',
             '{"000005": [{"point_forecast": [68.45974, 68.45974, 68.45974, '
             '68.45974, 68.45974], "model": "mean"}]}',
             '{"objective_fields": ["000001", "000005"], "period": 1}'],
            ['data/grades.csv', '10', '100', '100',
             '{"000005": {"horizon": 5, "ets_models": {"names": ["mean"]}}}',
             '{"000005": [{"point_forecast": [69.79553, 67.15821, 69.79553, '
             '67.15821, 69.79553], "model": "mean"}]}',
             '{"objective_fields": ["000001", "000005"], "period": 2}'],
            ['data/grades.csv', '10', '100', '100',
             '{"000005": {"horizon": 5, "ets_models": {"names": ["drift"]}}}',
             '{"000005": [{"point_forecast": [61.50545, 61.6209, 61.73635, '
             '61.8518, 61.96725], "model": "drift"}]}',
             '{"objective_fields": ["000001", "000005"], "period": 1}'],
            ['data/grades.csv', '10', '100', '100',
             '{"000005": {"horizon": 5, "ets_models": {"names": ["drift"]}}}',
             '{"000005": [{"point_forecast": [61.50545, 61.6209, 61.73635, '
             '61.8518, 61.96725], "model": "drift"}]}',
             '{"objective_fields": ["000001", "000005"], "period": 2}']]
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
                self, example["dataset_wait"], shared=example["data"])
            time_series_create.i_create_a_time_series_with_params(
                self, example["model_conf"])
            time_series_create.the_time_series_is_finished_in_less_than(
                self, example["model_wait"])
            time_series_create.create_local_time_series(self)
            forecast_create.i_create_a_forecast(
                self, example["input_data"])
            forecast_create.the_forecast_is(
                self, example["forecast"])
            forecast_compare.i_create_a_local_forecast(
                self, example["input_data"])
            forecast_compare.the_local_forecast_is(
                self, example["forecast"])


    def test_scenario5(self):
        """
            Scenario: Successfully comparing projections for PCAs:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a PCA with "<params>"
                And I wait until the PCA is ready less than <time_3> secs
                And I create a local PCA
                When I create a projection for "<input_data>"
                Then the projection is "<projection>"
                And I create a local projection for "<input_data>"
                Then the local projection is "<projection>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "input_data", "projection", "model_conf"]
        examples = [
            ['data/iris.csv', '30', '30', '120', '{}',
             '{"PC2": 0, "PC3": 0, "PC1": 0, "PC6": 0, "PC4": 5e-05, '
             '"PC5": 0}', '{}'],
            ['data/iris.csv', '30', '30', '120', '{"petal length": 1}',
             '{"PC2": 0.08708, "PC3": 0.20929, "PC1": 1.56084, '
             '"PC6": -1.34463, "PC4": 0.7295, "PC5": -1.00876}', '{}']]
        show_doc(self.test_scenario5)
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
            pca_create.i_create_a_pca_with_params(
                self, example["model_conf"])
            pca_create.the_pca_is_finished_in_less_than(
                self, example["model_wait"])
            compare_predictions.create_local_pca(self)
            projection_create.i_create_a_projection(
                self, example["input_data"])
            projection_create.the_projection_is(
                self, example["projection"])
            compare_predictions.i_create_a_local_projection(
                self, example["input_data"])
            compare_predictions.the_local_projection_is(
                self, example["projection"])

    def test_scenario5_b(self):
        """
            Scenario: Successfully comparing projections for PCAs:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a PCA with "<model_conf>"
                And I wait until the PCA is ready less than <model_wait> secs
                And I create a local PCA
                When I create a projection for "<input_data>"
                Then the projection is "<projection>"
                And I create a local projection for "<input_data>"
                Then the local projection is "<projection>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "input_data", "projection", "model_conf"]
        examples = [
            ['data/iris.csv', '30', '30', '120',
             '{"species": "Iris-versicolor"}',
             '{"PC2": 1.8602, "PC3": -2.00864, "PC1": -0.61116, '
             '"PC6": -0.66983, "PC4": -2.44618, "PC5": 0.43414}', '{}'],
            ['data/iris.csv', '30', '30', '120',
             '{"petal length": 1, "sepal length": 0, "petal width": 0, '
             '"sepal width": 0, "species": "Iris-versicolor"}',
             '{"PC2": 7.18009, "PC3": 6.51511, "PC1": 2.78155, '
             '"PC6": 0.21372, "PC4": -1.94865, "PC5": 0.57646}', '{}']]
        show_doc(self.test_scenario5)
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
            pca_create.i_create_a_pca_with_params(
                self, example["model_conf"])
            pca_create.the_pca_is_finished_in_less_than(
                self, example["model_wait"])
            compare_predictions.create_local_pca(self)
            projection_create.i_create_a_projection(
                self, example["input_data"])
            projection_create.the_projection_is(self, example["projection"])
            compare_predictions.i_create_a_local_projection(
                self, example["input_data"])
            compare_predictions.the_local_projection_is(
                self, example["projection"])
