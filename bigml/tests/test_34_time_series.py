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


""" Creating time series forecasts

"""
from world import world, setup_module, teardown_module
import create_source_steps as source_create
import create_dataset_steps as dataset_create
import create_time_series_steps as time_series_create
import create_forecast_steps as forecast_create


class TestTimeSeries(object):

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
            Scenario: Successfully creating forecasts from a dataset:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create time-series from a dataset
                And I wait until the time series is ready less than <time_3> secs
                And I update the time series name to "<time_series_name>"
                When I wait until the time series is ready less than <time_4> secs
                Then the time series name is "<time_series_name>"
                And I create a forecast for "<input_data>"
                Then the forecasts are "<forecast_points>"

                Examples:
                | data                | time_1  | time_2 | time_3 | time_4 | time_series_name |input_data | forecast_points
                | ../data/grades.csv | 10      | 10     | 20     | 50 | my new time_series name |
                {"000005": {"horizon": 5}], {}}
        """
        print self.test_scenario1.__doc__
        examples = [
            ['data/grades.csv', '10', '10', '20', '50', 'my new time series name',
             '{"000005": {"horizon": 5}}', '{"000005": [{"point_forecast": [68.50243, 68.50243, 68.50243, 68.50243, 68.50243], "model": "A,N,N"}]}']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            time_series_create.i_create_a_time_series(self)
            time_series_create.the_time_series_is_finished_in_less_than(self, example[3])
            time_series_create.i_update_time_series_name(self, example[5])
            time_series_create.the_time_series_is_finished_in_less_than(self, example[4])
            time_series_create.i_check_time_series_name(self, example[5])
            forecast_create.i_create_a_forecast(self, example[6])
            forecast_create.the_forecast_is(self, example[7])
