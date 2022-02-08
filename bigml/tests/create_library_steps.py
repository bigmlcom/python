# -*- coding: utf-8 -*-
#
# Copyright 2015-2021 BigML
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


#@step(r'the library code is "(.*)" and the value of "(.*)" is "(.*)"')
def the_library_code_and_attributes(step, source_code, param, param_value):
    res_param_value = world.library[param]
    eq_(res_param_value, param_value,
        ("The library %s is %s and the expected %s is %s" %
         (param, param_value, param, param_value)))


#@step(r'I create a whizzml library from a excerpt of code "(.*)"$')
def i_create_a_library(step, source_code):
    resource = world.api.create_library(source_code,
                                        {"project": world.project_id})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.library = resource['object']
    world.libraries.append(resource['resource'])


#@step(r'I update the library with "(.*)", "(.*)"$')
def i_update_a_library(step, param, param_value):
    resource = world.api.update_library(world.library['resource'],
                                        {param: param_value})
    world.status = resource['code']
    eq_(world.status, HTTP_ACCEPTED)
    world.location = resource['location']
    world.library = resource['object']


#@step(r'I wait until the library status code is either (\d) or (-\d) less than (\d+)')
def wait_until_library_status_code_is(step, code1, code2, secs):
    wait_until_status_code_is(code1, code2, secs, world.library)


#@step(r'I wait until the library is ready less than (\d+)')
def the_library_is_finished(step, secs):
    wait_until_library_status_code_is(step, FINISHED, FAULTY, secs)
