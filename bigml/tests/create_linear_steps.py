# -*- coding: utf-8 -*-

#
# Copyright 2019-2021 BigML
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
from datetime import datetime
from .world import world
from nose.tools import eq_, assert_less

from bigml.api import HTTP_CREATED
from bigml.api import HTTP_ACCEPTED
from bigml.api import FINISHED
from bigml.api import FAULTY
from bigml.api import get_status

from .read_resource_steps import wait_until_status_code_is


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
                                                           objective=None,
                                                           params=None):
    if params is not None:
        params = json.loads(params)
    else:
        params = {}
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
    wait_until_status_code_is(code1, code2, secs, world.linear_regression)


#@step(r'I wait until the linear is ready less than (\d+)')
def the_linear_regression_is_finished_in_less_than(step, secs):
    wait_until_linear_regression_status_code_is(step, FINISHED, FAULTY, secs)


#@step(r'I clone linear regression')
def clone_linear_regression(step, linear_regression):
    resource = world.api.clone_linear_regression(
        linear_regression, {'project': world.project_id})
    # update status
    world.status = resource['code']
    world.location = resource['location']
    world.linear_regression = resource['object']
    # save reference
    world.linear_regressions.append(resource['resource'])

def the_cloned_linear_regression_is(step, linear_regression):
    eq_(world.linear_regression["origin"], linear_regression)
