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

import time
import json
import os
from nose.tools import eq_, assert_less
from datetime import datetime
from .world import world, res_filename

from bigml.api import HTTP_OK
from bigml.api import HTTP_CREATED
from bigml.api import HTTP_ACCEPTED
from bigml.api import FINISHED
from bigml.api import FAULTY
from bigml.api import get_status
from bigml.timeseries import TimeSeries

from .read_resource_steps import wait_until_status_code_is


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



#@step(r'I wait until the time series is ready less than (\d+)')
def the_time_series_is_finished_in_less_than(step, secs):
    world.time_series = wait_until_status_code_is(
        FINISHED, FAULTY, secs, world.time_series)


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


#@step(r'I export the time series$')
def i_export_time_series(step, filename):
    world.api.export(world.time_series.get('resource'),
                     filename=res_filename(filename))


#@step(r'I create a local time series from file "(.*)"')
def i_create_local_time_series_from_file(step, export_file):
    world.local_time_series = TimeSeries(res_filename(export_file))


#@step(r'the time series ID and the local time series ID match')
def check_time_series_id_local_id(step):
    eq_(world.local_time_series.resource_id, world.time_series["resource"])

#@step(r'I clone time series')
def clone_time_series(step, time_series):
    resource = world.api.clone_time_series(time_series,
                                           {'project': world.project_id})
    # update status
    world.status = resource['code']
    world.location = resource['location']
    world.time_series = resource['object']
    # save reference
    world.time_series_set.append(resource['resource'])

def the_cloned_time_series_is(step, time_series):
    eq_(world.time_series["origin"], time_series)
