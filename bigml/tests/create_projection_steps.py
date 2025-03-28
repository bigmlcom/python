# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument
#
# Copyright 2018-2025 BigML
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
from bigml.api import HTTP_CREATED
from bigml.api import FINISHED, FAULTY

from .world import world, eq_
from .read_resource_steps import wait_until_status_code_is


#pylint: disable=locally-disabled,no-member
def i_create_a_projection(step, data=None):
    """Creating Projection"""
    if data is None:
        data = "{}"
    pca = world.pca['resource']
    data = json.loads(data)
    resource = world.api.create_projection(pca, data)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.projection = resource['object']
    world.projections.append(resource['resource'])


def the_projection_is(step, projection):
    """Checking projection"""
    if projection is None:
        projection = "{}"
    projection = json.loads(projection)
    eq_(len(list(projection.keys())),
        len(list(world.projection['projection']['result'].keys())))
    for name, value in list(projection.items()):
        eq_(world.projection['projection']['result'][name], value,
            "remote: %s, %s - expected: %s" % ( \
                name, world.projection['projection']['result'][name],
                value))


def wait_until_projection_status_code_is(step, code1, code2, secs):
    """Checking status code"""
    world.projection = wait_until_status_code_is(
        code1, code2, secs, world.projection)


def the_projection_is_finished_in_less_than(step, secs):
    """Wait for completion"""
    wait_until_projection_status_code_is(step, FINISHED, FAULTY, secs)
