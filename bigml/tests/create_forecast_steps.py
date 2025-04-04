# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument,no-member
#
# Copyright 2017-2025 BigML
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

from bigml.api import HTTP_CREATED

from .world import world, eq_


def i_create_a_forecast(step, data=None):
    """Creating forecast """
    if data is None:
        data = "{}"
    time_series = world.time_series['resource']
    data = json.loads(data)
    resource = world.api.create_forecast(time_series, data)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.forecast = resource['object']
    world.forecasts.append(resource['resource'])


def the_forecast_is(step, predictions):
    """Checking forecast"""
    predictions = json.loads(predictions)
    attrs = ["point_forecast", "model"]
    for field_id in predictions:
        forecast = world.forecast['forecast']['result'][field_id]
        prediction = predictions[field_id]
        eq_(len(forecast), len(prediction), "forecast: %s" % forecast)
        for index, item in enumerate(forecast):
            for attr in attrs:
                eq_(item[attr], prediction[index][attr])
