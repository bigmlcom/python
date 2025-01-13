# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument,no-member
#
# Copyright 2020-2025 BigML
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

from bigml.api import HTTP_ACCEPTED
from bigml.api import FINISHED
from bigml.api import FAULTY

from .read_resource_steps import wait_until_status_code_is
from .world import world, eq_, ok_


def i_create_external_connector(step):
    """Step: I create an external connector"""
    resource = world.api.create_external_connector(None, \
        {'project': world.project_id})
    # update status
    world.status = resource['code']
    world.location = resource['location']
    world.external_connector = resource['object']
    # save reference
    world.external_connectors.append(resource['resource'])


def wait_until_external_connector_status_code_is(step, code1, code2, secs):
    """Step: I wait until the external connector status code is either
    <code1> or <code2> less than <step>
    """
    world.external_connector = wait_until_status_code_is(
        code1, code2, secs, world.external_connector)


def the_external_connector_is_finished(step, secs):
    """Step: I wait until the external_connector is ready less than <secs> """
    wait_until_external_connector_status_code_is(step, FINISHED, FAULTY, secs)


def i_update_external_connector_with(step, data="{}"):
    """Step: I update the external_connector with params <data>"""
    resource = world.api.update_external_connector( \
        world.external_connector.get('resource'), json.loads(data))
    world.status = resource['code']
    eq_(world.status, HTTP_ACCEPTED)


def external_connector_has_args(step, args="{}"):
    """Step: the external connector exists and has args <args>"""
    args = json.loads(args)
    for key, value in list(args.items()):
        if key in world.external_connector:
            eq_(world.external_connector[key], value,
                "Expected key %s: %s. Found %s" % (key, value, world.external_connector[key]))
        else:
            ok_(False, "No key %s in external connector." % key)
