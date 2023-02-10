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


def i_check_sample_name(step, name):
    """Step: the sample name is <name>"""
    sample_name = world.sample['name']
    eq_(name, sample_name)


def i_create_a_sample_from_dataset(step):
    """Step: I create a sample from a dataset"""
    dataset = world.dataset.get('resource')
    resource = world.api.create_sample(dataset, {'name': 'new sample'})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.sample = resource['object']
    world.samples.append(resource['resource'])


def i_update_sample_name(step, name):
    """Step: I update the sample name to <name>"""
    resource = world.api.update_sample(world.sample['resource'],
                                       {'name': name})
    world.status = resource['code']
    eq_(world.status, HTTP_ACCEPTED)
    world.location = resource['location']
    world.sample = resource['object']


def the_sample_is_finished_in_less_than(step, secs):
    """Step: I wait until the sample is ready less than <secs>"""
    world.sample = wait_until_status_code_is(
        FINISHED, FAULTY, secs, world.sample)
