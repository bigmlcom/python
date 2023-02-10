# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument,no-member
#
# Copyright 2015-2023 BigML
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

def i_check_correlation_name(step, name):
    """Step: the correlation name is <name>"""
    correlation_name = world.correlation['name']
    eq_(name, correlation_name)

def i_create_a_correlation_from_dataset(step):
    """Step: I create a correlation from a dataset"""
    dataset = world.dataset.get('resource')
    resource = world.api.create_correlation(dataset, {'name': 'new correlation'})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.correlation = resource['object']
    world.correlations.append(resource['resource'])


def i_update_correlation_name(step, name):
    """Step: I update the correlation name to <name>"""
    resource = world.api.update_correlation(world.correlation['resource'],
                                            {'name': name})
    world.status = resource['code']
    eq_(world.status, HTTP_ACCEPTED)
    world.location = resource['location']
    world.correlation = resource['object']


def wait_until_correlation_status_code_is(step, code1, code2, secs):
    """Step: I wait until the correlation status code is either <code1>
    or <code2> less than <secs>
    """
    world.correlation = wait_until_status_code_is(
        code1, code2, secs, world.correlation)


def the_correlation_is_finished_in_less_than(step, secs):
    """Step: I wait until the correlation is ready less than <secs>"""
    wait_until_correlation_status_code_is(step, FINISHED, FAULTY, secs)
