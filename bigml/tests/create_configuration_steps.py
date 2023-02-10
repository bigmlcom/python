# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument,no-member
#
# Copyright 2017-2023 BigML
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

from .world import world, eq_
from .read_resource_steps import wait_until_status_code_is


def i_create_configuration(step, configurations):
    """Step: I create a configuration"""
    resource = world.api.create_configuration(
        configurations, {"name": "configuration"})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.configuration = resource['object']
    world.configurations.append(resource['resource'])


def i_update_configuration(step, changes):
    """Step: I update a configuration"""
    resource = world.api.update_configuration(
        world.configuration["resource"], changes)
    world.status = resource['code']
    eq_(world.status, HTTP_ACCEPTED)
    world.location = resource['location']
    world.configuration = resource['object']


def wait_until_configuration_status_code_is(step, code1, code2, secs):
    """Step: I wait until the configuration status code is either <code1> or
    <code2> less than <secs>
    """
    world.configuration = wait_until_status_code_is(
        code1, code2, secs, world.configuration)


def the_configuration_is_finished_in_less_than(step, secs):
    """Step: I wait until the configuration is ready less than <secs>"""
    wait_until_configuration_status_code_is(step, FINISHED, FAULTY, secs)


def i_check_configuration_name(step, name):
    """Step: the configuration name is <name>"""
    eq_(world.configuration["name"], name["name"])


def i_check_configuration_conf(step, confs):
    """Step: the configuration contents are <confs>"""
    eq_(world.configuration["configurations"], confs)
