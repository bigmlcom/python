# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2012, 2015 BigML
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
import csv
from datetime import datetime, timedelta
from urllib import urlencode
from world import world

from bigml.api import HTTP_CREATED, HTTP_ACCEPTED
from bigml.api import FINISHED
from bigml.api import FAULTY
from bigml.api import UPLOADING
from bigml.api import get_status

import read_source_steps as read

#@step(r'I create a data source uploading a "(.*)" file$')
def i_upload_a_file(step, file):
    resource = world.api.create_source(file)
    # update status
    world.status = resource['code']
    world.location = resource['location']
    world.source = resource['object']
    # save reference
    world.sources.append(resource['resource'])

#@step(r'I create a data source using the url "(.*)"')
def i_create_using_url(step, url):
    resource = world.api.create_source(url)
    # update status
    world.status = resource['code']
    world.location = resource['location']
    world.source = resource['object']
    # save reference
    world.sources.append(resource['resource'])

#@step(r'I create a data source from inline data slurped from "(.*)"')
def i_create_using_dict_data(step, data):
    # slurp CSV file to local variable
    mode = 'rb'
    if sys.version > '3':
        mode = 'rt'
    with open(data, mode) as fid:
        reader = csv.DictReader(fid)
        dict_data = [row for row in reader]
    # create source
    resource = world.api.create_source(dict_data)
    # update status
    world.status = resource['code']
    world.location = resource['location']
    world.source = resource['object']
    # save reference
    world.sources.append(resource['resource'])

#@step(r'I create a data source uploading a "(.*)" file in asynchronous mode$')
def i_upload_a_file_async(step, file):
    resource = world.api.create_source(file, async=True)
    world.resource = resource

#@step(r'I wait until the source has been created less than (\d+) secs')
def the_source_has_been_created_async(step, secs):
    start = datetime.utcnow()
    status = get_status(world.resource)
    while status['code'] == UPLOADING:
        time.sleep(3)
        assert datetime.utcnow() - start < timedelta(seconds=int(secs))
        status = get_status(world.resource)
    assert world.resource['code'] == HTTP_CREATED
    # update status
    world.status = world.resource['code']
    world.location = world.resource['location']
    world.source = world.resource['object']
    # save reference
    world.sources.append(world.resource['resource'])

#@step(r'I wait until the source status code is either (\d) or (\d) less than (\d+)')
def wait_until_source_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    read.i_get_the_source(step, world.source['resource'])
    status = get_status(world.source)
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
        time.sleep(3)
        assert datetime.utcnow() - start < timedelta(seconds=int(secs))
        read.i_get_the_source(step, world.source['resource'])
        status = get_status(world.source)
    assert status['code'] == int(code1)

#@step(r'I wait until the source is ready less than (\d+)')
def the_source_is_finished(step, secs):
    wait_until_source_status_code_is(step, FINISHED, FAULTY, secs)

#@step(r'I update the source with params "(.*)"')
def i_update_source_with(step, data="{}"):
    resource = world.api.update_source(world.source.get('resource'), json.loads(data))
    world.status = resource['code']
    assert world.status == HTTP_ACCEPTED
