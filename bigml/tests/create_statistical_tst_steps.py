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

from .read_resource_steps import wait_until_status_code_is
from .world import world, eq_


def i_check_tst_name(step, name):
    """Step: the statistical test name is <name>"""
    statistical_test_name = world.statistical_test['name']
    eq_(name, statistical_test_name)


def i_create_a_tst_from_dataset(step):
    """Step: I create an statistical test from a dataset"""
    dataset = world.dataset.get('resource')
    resource = world.api.create_statistical_test(dataset, \
        {'name': 'new statistical test'})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.statistical_test = resource['object']
    world.statistical_tests.append(resource['resource'])


def i_update_tst_name(step, name):
    """Step: I update the statistical test name to <name>"""
    resource = world.api.update_statistical_test( \
        world.statistical_test['resource'], {'name': name})
    world.status = resource['code']
    eq_(world.status, HTTP_ACCEPTED)
    world.location = resource['location']
    world.statistical_test = resource['object']


def wait_until_tst_status_code_is(step, code1, code2, secs):
    """Step: I wait until the statistical test status code is either
    code1 or code2 less than <secs>"""
    world.statistical_test = wait_until_status_code_is(
        code1, code2, secs, world.statistical_test)


def the_tst_is_finished_in_less_than(step, secs):
    """Step: I wait until the statistical test is ready less than <secs>"""
    wait_until_tst_status_code_is(step, FINISHED, FAULTY, secs)
