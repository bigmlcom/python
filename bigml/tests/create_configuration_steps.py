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
from datetime import datetime
from .world import world
from nose.tools import eq_

from .read_resource_steps import wait_until_status_code_is

from bigml.api import HTTP_CREATED
from bigml.api import HTTP_ACCEPTED
from bigml.api import FINISHED
from bigml.api import FAULTY
from bigml.api import get_status

#@step(r'I create a configuration$')
def i_create_configuration(step, configurations):
    resource = world.api.create_configuration(
        configurations, {"name": "configuration"})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.configuration = resource['object']
    world.configurations.append(resource['resource'])


#@step(r'I update a configuration$')
def i_update_configuration(step, changes):
    resource = world.api.update_configuration(
        world.configuration["resource"], changes)
    world.status = resource['code']
    eq_(world.status, HTTP_ACCEPTED)
    world.location = resource['location']
    world.configuration = resource['object']


#@step(r'I wait until the configuration status code is either (\d) or (-\d) less than (\d+)')
def wait_until_configuration_status_code_is(step, code1, code2, secs):
    world.configuration = wait_until_status_code_is(
        code1, code2, secs, world.configuration)


#@step(r'I wait until the configuration is ready less than (\d+)')
def the_configuration_is_finished_in_less_than(step, secs):
    wait_until_configuration_status_code_is(step, FINISHED, FAULTY, secs)


#@step(r'the configuration name is "(.*)"$')
def i_check_configuration_name(step, name):
    eq_(world.configuration["name"], name["name"])


#@step(r'the configuration contents are "(.*)"$')
def i_check_configuration_conf(step, confs):
    eq_(world.configuration["configurations"], confs)
