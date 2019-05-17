# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2018-2019 BigML
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
import time
from nose.tools import assert_almost_equals, eq_, assert_is_not_none
from datetime import datetime, timedelta
from world import world
from bigml.api import HTTP_CREATED
from bigml.api import FINISHED, FAULTY
from bigml.api import get_status

from read_projection_steps import i_get_the_projection

def i_create_a_projection(step, data=None):
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
    if projection is None:
        projection = "{}"
    projection = json.loads(projection)
    eq_(len(projection.keys()),
        len(world.projection['projection']['result'].keys()))
    for name, value in projection.items():
        eq_(world.projection['projection']['result'][name], projection[name],
            "remote: %s, %s - expected: %s" % ( \
                name, world.projection['projection']['result'][name],
                projection[name]))


def wait_until_projection_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    delta = int(secs) * world.delta
    i_get_the_projection(step, world.projection['resource'])
    status = get_status(world.projection)
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
        time.sleep(3)
        assert_less((datetime.utcnow() - start).seconds, delta)
        i_get_the_projection(step, world.projection['resource'])
        status = get_status(world.projection)
    eq_(status['code'], int(code1))


def the_projection_is_finished_in_less_than(step, secs):
    wait_until_projection_status_code_is(step, FINISHED, FAULTY, secs)
