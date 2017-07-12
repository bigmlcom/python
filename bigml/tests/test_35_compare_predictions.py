# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2017 BigML
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
from world import world, setup_module, teardown_module, show_doc
import create_source_steps as source_create
import create_dataset_steps as dataset_create
import create_model_steps as model_create
import create_time_series_steps as time_series_create
import create_forecast_steps as forecast_create
import compare_forecasts_steps as forecast_compare


class TestComparePrediction(object):

    def setup(self):
        """
            Debug information
        """
        print "\n-------------------\nTests in: %s\n" % __name__

    def teardown(self):
        """
            Debug information
        """
        print "\nEnd of tests in: %s\n-------------------\n" % __name__


    def test_scenario1(self):
        """
            Scenario: Successfully comparing forecasts from time series:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a time series with "<params>"
                And I wait until the time series is ready less than <time_3> secs
                And I create a local time series
                When I create a forecast for "<input_data>"
                Then the forecast is "<forecasts>"
                And I create a local forecast for "<data_input>"
                Then the local forecast is "<forecasts>"

                Examples:
                | data             | time_1  | time_2 | time_3 | input_data  | forecasts | params



        """
        examples = [
            ['data/grades.csv', '10', '10', '120', '{"000005": {"horizon": 5}}', '{"000005": [{"point_forecast": [68.50243, 68.50243, 68.50243, 68.50243, 68.50243], "model": "A,N,N"}]}', '{"objective_fields": ["000001", "000005"]}'],
            ['data/grades.csv', '10', '10', '120', '{"000005": {"horizon": 5, "ets_models": {"names": ["M,N,N"], "criterion": "aic", "limit": 3}}}', '{"000005": [{"point_forecast":  [68.4726, 68.4726, 68.4726, 68.4726, 68.4726], "model": "M,N,N"}]}', '{"objective_fields": ["000001", "000005"]}'],
            ['data/grades.csv', '10', '10', '120', '{"000005": {"horizon": 5, "ets_models": {"names": ["A,A,N"], "criterion": "aic", "limit": 3}}}', '{"000005": [{"point_forecast": [78.30154, 79.43494, 80.56834, 81.70174, 82.83514], "model": "A,A,N"}]}', '{"objective_fields": ["000001", "000005"]}'],
            ['data/grades.csv', '10', '10', '120', '{"000005": {"horizon": 5, "ets_models": {"names": ["A,Ad,N"], "criterion": "aic", "limit": 3}}}', '{"000005": [{"point_forecast":  [73.24041, 73.30553, 73.36935, 73.43189, 73.49318], "model": "A,Ad,N"}]}', '{"objective_fields": ["000001", "000005"]}'],
            ['data/grades.csv', '10', '10', '120', '{"000005": {"horizon": 5}, "000001": {"horizon": 3, "ets_models": {"criterion": "aic", "limit": 2}}}', '{"000005": [{"point_forecast": [68.50243, 68.50243, 68.50243, 68.50243, 68.50243], "model": "A,N,N"}], "000001": [{"point_forecast": [84.71215, 84.71215, 84.71215], "model": "M,N,N"}, {"point_forecast": [84.71842, 84.71842, 84.71842], "model": "A,N,N"}]}', '{"objective_fields": ["000001", "000005"]}']]
        show_doc(self.test_scenario1, examples)

        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            time_series_create.i_create_a_time_series_with_params(self, example[6])
            time_series_create.the_time_series_is_finished_in_less_than(self, example[3])
            time_series_create.create_local_time_series(self)
            forecast_create.i_create_a_forecast(self, example[4])
            forecast_create.the_forecast_is(self, example[5])
            forecast_compare.i_create_a_local_forecast(self, example[4])
            forecast_compare.the_local_forecast_is(self, example[5])


    def test_scenario2(self):
        """
            Scenario: Successfully comparing forecasts from time series with "A" seasonality
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a time series with "<params>"
                And I wait until the time series is ready less than <time_3> secs
                And I create a local time series
                When I create a forecast for "<input_data>"
                Then the forecast is "<forecasts>"
                And I create a local forecast for "<data_input>"
                Then the local forecast is "<forecasts>"

                Examples:
                | data             | time_1  | time_2 | time_3 | input_data  | forecasts | params

        """
        examples = [

            ['data/grades.csv', '10', '10', '120', '{"000005": {"horizon": 5}}', '{"000005": [{"point_forecast": [68.50243, 68.50243, 68.50243, 68.50243, 68.50243], "model": "A,N,N"}]}', '{"objective_fields": ["000001", "000005"], "period": 12}'],
            ['data/grades.csv', '10', '10', '120', '{"000005": {"horizon": 5, "ets_models": {"names": ["M,N,A"], "criterion": "aic", "limit": 3}}}', '{"000005": [{"point_forecast":  [67.33993, 65.56501, 67.35921, 67.45622, 72.67582], "model": "M,N,A"}]}', '{"objective_fields": ["000001", "000005"], "period": 12}'],
            ['data/grades.csv', '10', '10', '120', '{"000005": {"horizon": 5, "ets_models": {"names": ["A,A,A"], "criterion": "aic", "limit": 3}}}', '{"000005": [{"point_forecast": [75.75439, 70.5471, 74.44553, 74.23406, 79.61495], "model": "A,A,A"}]}', '{"objective_fields": ["000001", "000005"], "period": 12}'],
            ['data/grades.csv', '10', '10', '120', '{"000005": {"horizon": 5, "ets_models": {"names": ["A,Ad,A"], "criterion": "aic", "limit": 3}}}', '{"000005": [{"point_forecast":[71.86203, 69.63101, 74.03271, 72.20512, 77.51355], "model": "A,Ad,A"}]}', '{"objective_fields": ["000001", "000005"], "period": 12}']]
        show_doc(self.test_scenario2, examples)

        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            time_series_create.i_create_a_time_series_with_params(self, example[6])
            time_series_create.the_time_series_is_finished_in_less_than(self, example[3])
            time_series_create.create_local_time_series(self)
            forecast_create.i_create_a_forecast(self, example[4])
            forecast_create.the_forecast_is(self, example[5])
            forecast_compare.i_create_a_local_forecast(self, example[4])
            forecast_compare.the_local_forecast_is(self, example[5])


    def test_scenario3(self):
        """
            Scenario: Successfully comparing forecasts from time series with "M" seasonality
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a time series with "<params>"
                And I wait until the time series is ready less than <time_3> secs
                And I create a local time series
                When I create a forecast for "<input_data>"
                Then the forecast is "<forecasts>"
                And I create a local forecast for "<data_input>"
                Then the local forecast is "<forecasts>"

                Examples:
                | data             | time_1  | time_2 | time_3 | input_data  | forecasts | params

        """
        examples = [
            ['data/grades.csv', '10', '10', '120', '{"000005": {"horizon": 5, "ets_models": {"names": ["M,N,M"], "criterion": "aic", "limit": 3}}}', '{"000005": [{"point_forecast":  [68.89268, 66.75495, 68.9379, 66.05173, 74.70658], "model": "M,N,M"}]}', '{"objective_fields": ["000001", "000005"], "period": 12}'],
            ['data/grades.csv', '10', '10', '120', '{"000005": {"horizon": 5, "ets_models": {"names": ["M,A,M"], "criterion": "aic", "limit": 3}}}', '{"000005": [{"point_forecast": [74.05616, 72.22785, 76.35103, 72.45758, 81.60411], "model": "M,A,M"}]}', '{"objective_fields": ["000001", "000005"], "period": 12}'],
            ['data/grades.csv', '10', '10', '120', '{"000005": {"horizon": 5, "ets_models": {"names": ["M,Ad,M"], "criterion": "aic", "limit": 3}}}', '{"000005": [{"point_forecast": [71.33721, 70.93937, 73.78299, 70.56123, 79.1128], "model": "M,Ad,M"}]}', '{"objective_fields": ["000001", "000005"], "period": 12}'],
            ['data/grades.csv', '10', '10', '120', '{"000005": {"horizon": 5, "ets_models": {"names": ["M,M,M"], "criterion": "aic", "limit": 3}}}', '{"000005": [{"point_forecast": [73.78021, 71.82572, 75.11851, 72.59416, 81.2843], "model": "M,M,M"}]}', '{"objective_fields": ["000001", "000005"], "period": 12}'],
            ['data/grades.csv', '10', '10', '120', '{"000005": {"horizon": 5, "ets_models": {"names": ["M,Md,M"], "criterion": "aic", "limit": 3}}}', '{"000005": [{"point_forecast": [71.72127, 71.12783, 73.98116, 70.72066, 79.6831], "model": "M,Md,M"}]}', '{"objective_fields": ["000001", "000005"], "period": 12}']]
        show_doc(self.test_scenario3, examples)

        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            time_series_create.i_create_a_time_series_with_params(self, example[6])
            time_series_create.the_time_series_is_finished_in_less_than(self, example[3])
            time_series_create.create_local_time_series(self)
            forecast_create.i_create_a_forecast(self, example[4])
            forecast_create.the_forecast_is(self, example[5])
            forecast_compare.i_create_a_local_forecast(self, example[4])
            forecast_compare.the_local_forecast_is(self, example[5])


    def test_scenario4(self):
        """
            Scenario: Successfully comparing forecasts from time series with trivial models
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a time series with "<params>"
                And I wait until the time series is ready less than <time_3> secs
                And I create a local time series
                When I create a forecast for "<input_data>"
                Then the forecast is "<forecasts>"
                And I create a local forecast for "<data_input>"
                Then the local forecast is "<forecasts>"

                Examples:
                | data             | time_1  | time_2 | time_3 | input_data  | forecasts | params

        """
        examples = [
            ['data/grades.csv', '10', '10', '120', '{"000005": {"horizon": 5, "ets_models": {"names": ["naive"]}}}', '{"000005": [{"point_forecast": [61.39, 61.39, 61.39, 61.39, 61.39], "model": "naive"}]}', '{"objective_fields": ["000001", "000005"], "period": 1}'],
            ['data/grades.csv', '10', '10', '120', '{"000005": {"horizon": 5, "ets_models": {"names": ["naive"]}}}', '{"000005": [{"point_forecast": [78.89, 61.39, 78.89, 61.39, 78.89], "model": "naive"}]}', '{"objective_fields": ["000001", "000005"], "period": 2}'],
            ['data/grades.csv', '10', '10', '120', '{"000005": {"horizon": 5, "ets_models": {"names": ["mean"]}}}', '{"000005": [{"point_forecast": [68.48369, 68.48369, 68.48369, 68.48369, 68.48369], "model": "mean"}]}', '{"objective_fields": ["000001", "000005"], "period": 1}'],
            ['data/grades.csv', '10', '10', '120', '{"000005": {"horizon": 5, "ets_models": {"names": ["mean"]}}}', '{"000005": [{"point_forecast": [65.16813, 71.79925, 65.16813, 71.79925, 65.16813], "model": "mean"}]}', '{"objective_fields": ["000001", "000005"], "period": 2}'],
            ['data/grades.csv', '10', '10', '120', '{"000005": {"horizon": 5, "ets_models": {"names": ["drift"]}}}', '{"000005": [{"point_forecast": [61.50113, 61.61226, 61.72339, 61.83452, 61.94565], "model": "drift"}]}', '{"objective_fields": ["000001", "000005"], "period": 1}'],
            ['data/grades.csv', '10', '10', '120', '{"000005": {"horizon": 5, "ets_models": {"names": ["drift"]}}}', '{"000005": [{"point_forecast": [61.50113, 61.61226, 61.72339, 61.83452, 61.94565], "model": "drift"}]}', '{"objective_fields": ["000001", "000005"], "period": 2}']]
        show_doc(self.test_scenario4, examples)

        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            time_series_create.i_create_a_time_series_with_params(self, example[6])
            time_series_create.the_time_series_is_finished_in_less_than(self, example[3])
            time_series_create.create_local_time_series(self)
            forecast_create.i_create_a_forecast(self, example[4])
            forecast_create.the_forecast_is(self, example[5])
            forecast_compare.i_create_a_local_forecast(self, example[4])
            forecast_compare.the_local_forecast_is(self, example[5])
