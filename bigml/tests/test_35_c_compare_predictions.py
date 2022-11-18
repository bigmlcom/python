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

from .world import world, setup_module, teardown_module, show_doc, \
    show_method, delete_local
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


    def test_scenario3(self):
        """
            Scenario: Successfully comparing forecasts from time series with "M" seasonality
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
            ['data/grades.csv', '30', '30', '120', '{"000005": {"horizon": 5, "ets_models": {"names": ["M,N,M"], "criterion": "aic", "limit": 3}}}', '{"000005": [{"point_forecast":  [68.99775, 72.76777, 66.5556, 70.90818, 70.92998], "model": "M,N,M"}]}', '{"objective_fields": ["000001", "000005"], "period": 12}'],
            ['data/grades.csv', '30', '30', '120', '{"000005": {"horizon": 5, "ets_models": {"names": ["M,A,M"], "criterion": "aic", "limit": 3}}}', '{"000005": [{"point_forecast": [70.65993, 78.20652, 69.64806, 75.43716, 78.13556], "model": "M,A,M"}]}', '{"objective_fields": ["000001", "000005"], "period": 12}']]
        show_doc(self.test_scenario3)

        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(self, example["data"], shared=example["data"])
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
            forecast_create.i_create_a_forecast(self, example["input_data"])
            forecast_create.the_forecast_is(self, example["forecast"])
            forecast_compare.i_create_a_local_forecast(
                self, example["input_data"])
            forecast_compare.the_local_forecast_is(
                self, example["forecast"])

    def test_scenario3b(self):
        """
            Scenario: Successfully comparing forecasts from time series with "M" seasonality
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
            ['data/grades.csv', '30', '30', '120',
             '{"000005": {"horizon": 5, "ets_models": {"names": ["M,M,M"], '
             '"criterion": "aic", "limit": 3}}}',
             '{"000005": [{"point_forecast": [71.75055, 80.67195, 70.81368, '
             '79.84999, 78.27634], "model": "M,M,M"}]}',
             '{"objective_fields": ["000001", "000005"], "period": 12}']]
        show_doc(self.test_scenario3)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(self, example["data"])
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
            forecast_create.i_create_a_forecast(self, example["input_data"])
            forecast_create.the_forecast_is(self, example["forecast"])
            forecast_compare.i_create_a_local_forecast(
                self, example["input_data"])
            forecast_compare.the_local_forecast_is(self, example["forecast"])
