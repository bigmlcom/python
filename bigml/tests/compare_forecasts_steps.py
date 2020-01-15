# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2017-2020 BigML
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


import json
import os

from nose.tools import eq_, assert_almost_equal
from world import world, res_filename


#@step(r'I create a local forecast for "(.*)"')
def i_create_a_local_forecast(step, input_data):
    input_data = json.loads(input_data)
    world.local_forecast = world.local_time_series.forecast(input_data)


#@step(r'the local forecast is "(.*)"')
def the_local_forecast_is(step, local_forecasts):
    local_forecasts = json.loads(local_forecasts)
    attrs = ["point_forecast", "model"]
    for field_id in local_forecasts:
        forecast = world.local_forecast[field_id]
        local_forecast = local_forecasts[field_id]
        eq_(len(forecast), len(local_forecast), "forecast: %s" % forecast)
        for index in range(len(forecast)):
            for attr in attrs:
                if isinstance(forecast[index][attr], list):
                    for pos, item in enumerate(forecast[index][attr]):
                        assert_almost_equal(local_forecast[index][attr][pos],
                                            item, places=5)
                else:
                    eq_(forecast[index][attr], local_forecast[index][attr])
