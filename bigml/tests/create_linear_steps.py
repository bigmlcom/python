# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument,no-member
#
# Copyright 2019-2025 BigML
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

from bigml.api import HTTP_CREATED, HTTP_ACCEPTED
from bigml.api import FINISHED, FAULTY

from .read_resource_steps import wait_until_status_code_is
from .world import world, eq_


def i_check_linear_name(step, name):
    """Step: the linear name is <name>"""
    linear_name = world.linear_regression['name']
    eq_(name, linear_name)


def i_create_a_linear_regression_from_dataset(step, shared=None):
    """Step: I create a Linear Regression from a dataset"""
    if shared is None or \
            world.shared.get("linear_regression", {}).get(shared) is None:
        dataset = world.dataset.get('resource')
        resource = world.api.create_linear_regression(
            dataset, {'name': 'new linear regression'})
        world.status = resource['code']
        eq_(world.status, HTTP_CREATED)
        world.location = resource['location']
        world.linear_regression = resource['object']
        world.linear_regressions.append(resource['resource'])


def i_create_a_linear_regression_with_params(step, params):
    """Step: I create a Linear Regression from a dataset"""
    i_create_a_linear_regression_with_objective_and_params(step, None, params)


def i_create_a_linear_regression_with_objective_and_params(
    step, objective=None, params=None):
    """Step: I create a Linear Regression with objective and params """
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


def i_create_a_linear_regression(step, shared=None):
    """Creating linear regression from dataset """
    i_create_a_linear_regression_from_dataset(step, shared=shared)


def i_update_linear_regression_name(step, name):
    """Step: I update the linear regression name to <name>"""
    resource = world.api.update_linear_regression( \
        world.linear_regression['resource'],
        {'name': name})
    world.status = resource['code']
    eq_(world.status, HTTP_ACCEPTED)
    world.location = resource['location']
    world.linear_regression = resource['object']


def wait_until_linear_regression_status_code_is(step, code1, code2, secs):
    """Step: I wait until the linear regression status code is either
    <code1> or <code2> less than <secs>
    """
    world.linear_regression = wait_until_status_code_is(
        code1, code2, secs, world.linear_regression)


def the_linear_regression_is_finished_in_less_than(step, secs, shared=None):
    """#Step: I wait until the linear is ready less than <secs>"""
    if shared is None or \
            world.shared.get("linear_regression", {}).get(shared) is None:
        wait_until_linear_regression_status_code_is(step, FINISHED, FAULTY, secs)
        if shared is not None:
            if "linear_regression" not in world.shared:
                world.shared["linear_regression"] = {}
            world.shared["linear_regression"][shared] = world.linear_regression
    else:
        world.linear_regression = world.shared["linear_regression"][shared]
        print("Reusing %s" % world.linear_regression["resource"])


def clone_linear_regression(step, linear_regression):
    """Step: I clone linear regression"""
    resource = world.api.clone_linear_regression(
        linear_regression, {'project': world.project_id})
    # update status
    world.status = resource['code']
    world.location = resource['location']
    world.linear_regression = resource['object']
    # save reference
    world.linear_regressions.append(resource['resource'])

def the_cloned_linear_regression_is(step, linear_regression):
    """Checking linear regression is a clone"""
    eq_(world.linear_regression["origin"], linear_regression)
