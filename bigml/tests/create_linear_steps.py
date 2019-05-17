# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2019 BigML
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
from datetime import datetime, timedelta
from world import world
from nose.tools import eq_, assert_less

from bigml.api import HTTP_CREATED
from bigml.api import HTTP_ACCEPTED
from bigml.api import FINISHED
from bigml.api import FAULTY
from bigml.api import get_status

from read_linear_steps import i_get_the_linear_regression


#@step(r'the linear name is "(.*)"')
def i_check_linear_name(step, name):
    linear_name = world.linear_regression['name']
    eq_(name, linear_name)

#@step(r'I create a Linear Regression from a dataset$')
def i_create_a_linear_regression_from_dataset(step):
    dataset = world.dataset.get('resource')
    resource = world.api.create_linear_regression( \
        dataset, {'name': 'new linear regression'})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.linear_regression = resource['object']
    world.linear_regressions.append(resource['resource'])


#@step(r'I create a Linear Regression from a dataset$')
def i_create_a_linear_regression_with_params(step, params):
    i_create_a_linear_regression_with_objective_and_params(step, None, params)


#@step(r'I create a Linear Regression with objective and params$')
def i_create_a_linear_regression_with_objective_and_params(step,
                                                           objective,
                                                           params):
    params = json.loads(params)
    if objective is not None:
        params.update({"objective_field": objective})
    dataset = world.dataset.get('resource')
    resource = world.api.create_linear_regression(dataset, params)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.linear_regression = resource['object']
    world.linear_regressions.append(resource['resource'])

def i_create_a_linear_regression(step):
    i_create_a_linear_regression_from_dataset(step)


#@step(r'I update the linear regression name to "(.*)"$')
def i_update_linear_regression_name(step, name):
    resource = world.api.update_linear_regression( \
        world.linear_regression['resource'],
        {'name': name})
    world.status = resource['code']
    eq_(world.status, HTTP_ACCEPTED)
    world.location = resource['location']
    world.linear_regression = resource['object']


#@step(r'I wait until the linear regression status code is either (\d) or (-\d) less than (\d+)')
def wait_until_linear_regression_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    delta = int(secs) * world.delta
    linear_regression_id = world.linear_regression['resource']
    i_get_the_linear_regression(step, linear_regression_id)
    status = get_status(world.linear_regression)
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
           time.sleep(3)
           assert_less((datetime.utcnow() - start).seconds, delta)
           i_get_the_linear_regression(step, linear_regression_id)
           status = get_status(world.linear_regression)
    eq_(status['code'], int(code1))


#@step(r'I wait until the linear is ready less than (\d+)')
def the_linear_regression_is_finished_in_less_than(step, secs):
    wait_until_linear_regression_status_code_is(step, FINISHED, FAULTY, secs)
