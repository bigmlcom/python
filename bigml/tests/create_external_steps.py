# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2020 BigML
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
import csv
import sys


from datetime import datetime
from world import world, res_filename, logged_wait
from nose.tools import eq_, assert_less

from bigml.api import HTTP_CREATED, HTTP_ACCEPTED
from bigml.api import FINISHED
from bigml.api import FAULTY
from bigml.api import UPLOADING
from bigml.api import get_status


import read_external_steps as read

#@step(r'I create an external connector$')
def i_create_external_connector(step):
    resource = world.api.create_external_connector(None, \
        {'project': world.project_id})
    # update status
    world.status = resource['code']
    world.location = resource['location']
    world.external_connector = resource['object']
    # save reference
    world.external_connectors.append(resource['resource'])


#@step(r'I wait until the external connector status code is either (\d) or (\d) less than (\d+)')
def wait_until_external_connector_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    delta = int(secs) * world.delta
    read.i_get_the_external_connector(step, world.external_connector['resource'])
    status = get_status(world.external_connector)
    count = 0
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
        count += 1
        logged_wait(start, delta, count, "externalconnector")
        assert_less((datetime.utcnow() - start).seconds, delta)
        read.i_get_the_external_connector(step, world.external_connector['resource'])
        status = get_status(world.external_connector)
    eq_(status['code'], int(code1))

#@step(r'I wait until the external_connector is ready less than (\d+)')
def the_external_connector_is_finished(step, secs):
    wait_until_external_connector_status_code_is(step, FINISHED, FAULTY, secs)

#@step(r'I update the external_connector with params "(.*)"')
def i_update_external_connector_with(step, data="{}"):
    resource = world.api.update_external_connector( \
        world.external_connector.get('resource'), json.loads(data))
    world.status = resource['code']
    eq_(world.status, HTTP_ACCEPTED)

#@step(r'the external connector exists and has args "(.*)"')
def external_connector_has_args(step, args="{}"):
    args = json.loads(args)
    for key, value in args.items():
        if key in world.external_connector:
            eq_(world.external_connector[key], value,
                "Expected key %s: %s. Found %s" % (key, value, world.external_connector[key]))
        else:
            assert False, "No key %s in external connector." % key
