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

import os
import time
import json
from datetime import datetime
from urllib.parse import urlencode
from nose.tools import eq_, assert_less
from .world import world

from bigml.api import HTTP_CREATED, HTTP_ACCEPTED
from bigml.api import FINISHED
from bigml.api import FAULTY
from bigml.api import UPLOADING
from bigml.api import get_status

from .read_resource_steps import wait_until_status_code_is


def i_create_project(step, name):
    resource = world.api.create_project({"name": name})
    # update status
    world.status = resource['code']
    world.location = resource['location']
    world.project = resource['object']
    # save reference
    world.projects.append(resource['resource'])


def the_project_is_finished(step, secs):
    wait_until_status_code_is(FINISHED, FAULTY, secs, world.project)


def i_update_project_name_with(step, name=""):
    resource = world.api.update_project(world.project.get('resource'),
                                        {"name": name})
    world.status = resource['code']
    eq_(world.status, HTTP_ACCEPTED)
    world.project = resource['object']


def i_check_project_name(step, name=""):
    updated_name = world.project.get("name", "")
    eq_(updated_name, name)
