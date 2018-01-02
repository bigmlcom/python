# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2017-2018 BigML
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

import time
import json
import os
from nose.tools import eq_, assert_less
from datetime import datetime, timedelta
from world import world

from bigml.api import HTTP_OK
from bigml.api import HTTP_CREATED
from bigml.api import HTTP_ACCEPTED
from bigml.api import FINISHED
from bigml.api import FAULTY
from bigml.api import get_status
from bigml.timeseries import TimeSeries

import read_time_series_steps as read


#@step(r'I create a time series$')
def i_create_a_time_series(step):
    dataset = world.dataset.get('resource')
    resource = world.api.create_time_series(dataset)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.time_series = resource['object']
    world.time_series_set.append(resource['resource'])


#@step(r'I create a time series with params "(.*)"')
def i_create_a_time_series_with_params(step, data="{}"):
    args = json.loads(data)
    resource = world.api.create_time_series(world.dataset.get('resource'),
                                            args=args)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.time_series = resource['object']
    world.time_series_set.append(resource['resource'])


#@step(r'I wait until the time series status code is either (\d) or (-\d) less than (\d+)')
def wait_until_time_series_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    read.i_get_the_time_series(step, world.time_series['resource'])
    status = get_status(world.time_series)
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
           time.sleep(3)
           assert_less(datetime.utcnow() - start, timedelta(seconds=int(secs)))
           read.i_get_the_time_series(step, world.time_series['resource'])
           status = get_status(world.time_series)
    eq_(status['code'], int(code1))

#@step(r'I wait until the time series is ready less than (\d+)')
def the_time_series_is_finished_in_less_than(step, secs):
    wait_until_time_series_status_code_is(step, FINISHED, FAULTY, secs)


#@step(r'I create a local TimeSeries$')
def create_local_time_series(step):
    world.local_time_series = TimeSeries(world.time_series["resource"],
                                         world.api)


#@step(r'I update the time series name to "(.*)"$')
def i_update_time_series_name(step, name):
    resource = world.api.update_time_series(world.time_series['resource'],
                                            {'name': name})
    world.status = resource['code']
    eq_(world.status, HTTP_ACCEPTED)
    world.location = resource['location']
    world.time_series = resource['object']

#@step(r'the time series name is "(.*)"')
def i_check_time_series_name(step, name):
    time_series_name = world.time_series['name']
    eq_(name, time_series_name)
