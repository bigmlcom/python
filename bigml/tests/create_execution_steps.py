# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument,no-member
#
# Copyright 2015-2022 BigML
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

from bigml.api import HTTP_CREATED, HTTP_ACCEPTED
from bigml.api import FINISHED, FAULTY
from bigml.execution import Execution

from .read_resource_steps import wait_until_status_code_is
from .world import world, eq_


def the_execution_and_attributes(step, param, param_value, result):
    """Step: the script id is correct, the value of <param> is <param_value>
    and the result is <result>
    """
    eq_(world.script['resource'], world.execution['script'])
    eq_(world.execution['execution']['results'][0], result)
    res_param_value = world.execution[param]
    eq_(res_param_value, param_value,
        ("The execution %s is %s and the expected %s is %s" %
         (param, param_value, param, param_value)))


def the_execution_ids_and_attributes(step, number_of_scripts,
                                     param, param_value, result):
    """Step: the script ids are correct, the value of <param> is <param_value>
    and the result is <result>
    """
    scripts = world.scripts[-number_of_scripts:]
    eq_(scripts, world.execution['scripts'])
    eq_(world.execution['execution']['results'], result)
    res_param_value = world.execution[param]
    eq_(res_param_value, param_value,
        ("The execution %s is %s and the expected %s is %s" %
         (param, param_value, param, param_value)))


def i_create_an_execution(step):
    """Step: I create a whizzml execution from an existing script"""
    resource = world.api.create_execution(world.script['resource'],
                                          {"project": world.project_id})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.execution = resource['object']
    world.executions.append(resource['resource'])


def i_create_an_execution_from_list(step, number_of_scripts=2):
    """Step: I create a whizzml execution from the last two scripts"""
    scripts = world.scripts[-number_of_scripts:]
    resource = world.api.create_execution(scripts,
                                          {"project": world.project_id})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.execution = resource['object']
    world.executions.append(resource['resource'])


def i_update_an_execution(step, param, param_value):
    """Step: I update the execution with <param>, <param_value>"""
    resource = world.api.update_execution(world.execution['resource'],
                                          {param: param_value})
    world.status = resource['code']
    eq_(world.status, HTTP_ACCEPTED)
    world.location = resource['location']
    world.execution = resource['object']


def wait_until_execution_status_code_is(step, code1, code2, secs):
    """Step: I wait until the execution status code is either <code1> or
    <code2> less than <secs>"""
    world.execution = wait_until_status_code_is(
        code1, code2, secs, world.execution)


def the_execution_is_finished(step, secs):
    """Steps: I wait until the script is ready less than <secs>"""
    wait_until_execution_status_code_is(step, FINISHED, FAULTY, secs)


def create_local_execution(step):
    """Step: I create a local execution"""
    step.bigml["local_execution"] = Execution(world.execution)


def the_local_execution_result_is(step, result):
    """Step: And the local execution result is <result>"""
    eq_(step.bigml["local_execution"].result, result)
