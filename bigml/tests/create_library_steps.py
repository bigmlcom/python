# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument,no-member
#
# Copyright 2015-2025 BigML
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

from .read_resource_steps import wait_until_status_code_is
from .world import world, eq_


def the_library_code_and_attributes(step, source_code, param, param_value):
    """Step: the library code is <source_code> and the value of <param>
    is <param_value>
    """
    res_param_value = world.library[param]
    eq_(res_param_value, param_value,
        ("The library %s is %s and the expected %s is %s" %
         (param, param_value, param, param_value)))


def i_create_a_library(step, source_code):
    """Step: I create a whizzml library from a excerpt of code <source_code>"""
    resource = world.api.create_library(source_code,
                                        {"project": world.project_id})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.library = resource['object']
    world.libraries.append(resource['resource'])


def i_update_a_library(step, param, param_value):
    """Step: I update the library with <param>, <param_value>"""
    resource = world.api.update_library(world.library['resource'],
                                        {param: param_value})
    world.status = resource['code']
    eq_(world.status, HTTP_ACCEPTED)
    world.location = resource['location']
    world.library = resource['object']


def wait_until_library_status_code_is(step, code1, code2, secs):
    """Step: I wait until the library status code is either <code1> or
    <code2> less than <secs>
    """
    world.library = wait_until_status_code_is(
        code1, code2, secs, world.library)


def the_library_is_finished(step, secs):
    """Step: I wait until the library is ready less than <secs>"""
    wait_until_library_status_code_is(step, FINISHED, FAULTY, secs)
