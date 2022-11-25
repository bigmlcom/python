# -*- coding: utf-8 -*-
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


import json

from .world import eq_, approx_


def i_create_a_local_forecast(step, input_data):
    """Step: I create a local forecast for <input_data>"""
    input_data = json.loads(input_data)
    step.bigml["local_forecast"] = step.bigml[ \
        "local_time_series"].forecast(input_data)


def the_local_forecast_is(step, local_forecasts):
    """Step: the local forecast is <local_forecasts>"""
    local_forecasts = json.loads(local_forecasts)
    attrs = ["point_forecast", "model"]
    for field_id in local_forecasts:
        forecast = step.bigml["local_forecast"][field_id]
        local_forecast = local_forecasts[field_id]
        eq_(len(forecast), len(local_forecast), msg="forecast: %s" % forecast)
        for index, forecast_item in enumerate(forecast):
            for attr in attrs:
                if isinstance(forecast_item[attr], list):
                    for pos, item in enumerate(forecast_item[attr]):
                        approx_(local_forecast[index][attr][pos],
                                item, precision=5)
                else:
                    eq_(forecast_item[attr], local_forecast[index][attr])
