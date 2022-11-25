# -*- coding: utf-8 -*-
#
# Copyright 2014-2022 BigML
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


from datetime import datetime

from bigml.api import HTTP_OK, get_status, get_resource_type

from .world import world, logged_wait, eq_, ok_


def wait_until_status_code_is(code1, code2, secs, resource_info):
    """Waits for the resource to be finished and stores the resulting full
    info in the corresponding dictionary. Attention, resource_info is
    modified
    """

    start = datetime.utcnow()
    delta = int(secs) * world.delta
    resource_info = world.get_minimal_resource(
        resource_info['resource']).get("object")
    status = get_status(resource_info)
    count = 0
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
        count += 1
        resource_type = get_resource_type(resource_info["resource"])
        logged_wait(start, delta, count, resource_type, status=status)
        ok_((datetime.utcnow() - start).seconds < delta)
        resource_info = world.get_minimal_resource(
            resource_info['resource']).get("object")
        status = get_status(resource_info)
    if status['code'] == int(code2):
        world.errors.append(resource_info)
    eq_(status['code'], int(code1))
    return i_get_the_resource(resource_info)


def i_get_the_resource(resource_info):
    """Step: I get the resource <resource_info>"""
    resource = world.get_maximal_resource(resource_info["resource"])
    world.status = resource['code']
    eq_(world.status, HTTP_OK)
    return resource['object']
