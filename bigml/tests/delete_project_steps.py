# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2014-2017 BigML
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
from datetime import datetime, timedelta
from world import world
from nose.tools import eq_, assert_less
from bigml.api import HTTP_NO_CONTENT, HTTP_OK, HTTP_NOT_FOUND


def i_delete_the_project(step):
    resource = world.api.delete_project(world.project['resource'])
    world.status = resource['code']
    eq_(world.status, HTTP_NO_CONTENT)


def wait_until_project_deleted(step, secs):
    start = datetime.utcnow()
    project_id = world.project['resource']
    resource = world.api.get_project(project_id)
    while (resource['code'] == HTTP_OK):
        time.sleep(3)
        assert_less(datetime.utcnow() - start, timedelta(seconds=int(secs)))
        resource = world.api.get_project(project_id)
    eq_(resource['code'], HTTP_NOT_FOUND)
    world.projects.remove(project_id)
