# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,line-too-long,attribute-defined-outside-init
#pylint: disable=locally-disabled,unused-import
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


""" Creating time series forecasts

"""
from .world import world, setup_module, teardown_module, show_doc, \
    show_method
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create
from . import create_time_series_steps as time_series_create
from . import create_forecast_steps as forecast_create


class TestTimeSeries:
    """Testing Time Series methods"""

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
        Scenario: Successfully creating forecasts from a dataset:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create time-series from a dataset
            And I wait until the time series is ready less than <model_wait> secs
            And I update the time series name to "<time_series_name>"
            When I wait until the time series is ready less than <model_wait> secs
            Then the time series name is "<time_series_name>"
            And I create a forecast for "<input_data>"
            Then the forecasts are "<forecast_points>"
        """
        show_doc(self.test_scenario1)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "time_series_name", "input_data", "forecast_points"]
        examples = [
            ['data/grades.csv', '30', '30', '50', 'my new time series name',
             '{"000005": {"horizon": 5}}',
             '{"000005": [{"point_forecast": [73.96192, 74.04106, 74.12029, '
             '74.1996, 74.27899], "model": "M,M,N"}]}']]
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
            time_series_create.i_create_a_time_series(self)
            time_series_create.the_time_series_is_finished_in_less_than(
                self, example["model_wait"])
            time_series_create.i_update_time_series_name(
                self, example["time_series_name"])
            time_series_create.the_time_series_is_finished_in_less_than(
                self, example["model_wait"])
            time_series_create.i_check_time_series_name(
                self, example["time_series_name"])
            forecast_create.i_create_a_forecast(
                self, example["input_data"])
            forecast_create.the_forecast_is(self, example["forecast_points"])
