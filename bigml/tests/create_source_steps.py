# -*- coding: utf-8 -*-

#
# Copyright 2012, 2015-2020 BigML
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
from .world import world, res_filename, logged_wait
from nose.tools import eq_, assert_less

from bigml.api import HTTP_CREATED, HTTP_ACCEPTED
from bigml.api import FINISHED
from bigml.api import FAULTY
from bigml.api import UPLOADING
from bigml.api import get_status


from . import read_source_steps as read

#@step(r'I create a data source uploading a "(.*)" file$')
def i_upload_a_file(step, file):
    resource = world.api.create_source(res_filename(file), \
        {'project': world.project_id})
    # update status
    world.status = resource['code']
    world.location = resource['location']
    world.source = resource['object']
    # save reference
    world.sources.append(resource['resource'])

#@step(r'I create a data source uploading a "(.*)" file using a project$')
def i_upload_a_file_with_project_conn(step, file):
    resource = world.api.create_source(res_filename(file))
    # update status
    world.status = resource['code']
    world.location = resource['location']
    world.source = resource['object']
    # save reference
    world.sources.append(resource['resource'])

#@step(r'I create a data source from stdin uploading a "(.*)" file$')
def i_upload_a_file_from_stdin(step, file):
    file_name = res_filename(file)
    with open(file_name, 'rb') as file_handler:
        resource = world.api.create_source(file_handler, \
            {'project': world.project_id})
        # update status
        world.status = resource['code']
        world.location = resource['location']
        world.source = resource['object']
        # save reference
        world.sources.append(resource['resource'])


#@step(r'I create a data source uploading a "(.*)" file with args "(.*)"$')
def i_upload_a_file_with_args(step, file, args):
    args = json.loads(args)
    args.update({'project': world.project_id})
    resource = world.api.create_source(res_filename(file), args)
    # update status
    world.status = resource['code']
    world.location = resource['location']
    world.source = resource['object']
    # save reference
    world.sources.append(resource['resource'])

#@step(r'I create a data source using the url "(.*)"')
def i_create_using_url(step, url):
    resource = world.api.create_source(url, {'project': world.project_id})
    # update status
    world.status = resource['code']
    world.location = resource['location']
    world.source = resource['object']
    # save reference
    world.sources.append(resource['resource'])

#@step(r'I create a data source using the connection ".*"')
def i_create_using_connector(step, connector):
    resource = world.api.create_source(connector, {'project': world.project_id})
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
    with open(res_filename(data), mode) as fid:
        reader = csv.DictReader(fid)
        dict_data = [row for row in reader]
    # create source
    resource = world.api.create_source(dict_data,
                                       {'project': world.project_id})
    # update status
    world.status = resource['code']
    world.location = resource['location']
    world.source = resource['object']
    # save reference
    world.sources.append(resource['resource'])

#@step(r'I create a data source uploading a "(.*)" file in asynchronous mode$')
def i_upload_a_file_async(step, file):
    resource = world.api.create_source(res_filename(file),
                                       {'project': world.project_id},
                                       async_load=True)
    world.resource = resource

#@step(r'I wait until the source has been created less than (\d+) secs')
def the_source_has_been_created_async(step, secs):
    start = datetime.utcnow()
    read.i_get_the_source(step, world.source['resource'])
    status = get_status(world.resource)
    count = 0
    delta = int(secs) * world.delta
    while status['code'] == UPLOADING:
        count += 1
        logged_wait(start, delta, count, "source")
        read.i_get_the_source(step, world.source['resource'])
        status = get_status(world.source)
    eq_(world.resource['code'], HTTP_CREATED)
    # update status
    world.status = world.resource['code']
    world.location = world.resource['location']
    world.source = world.resource['object']
    # save reference
    world.sources.append(world.resource['resource'])

#@step(r'I wait until the source status code is either (\d) or (\d) less than (\d+)')
def wait_until_source_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    delta = int(secs) * world.delta
    read.i_get_the_source(step, world.source['resource'])
    status = get_status(world.source)
    count = 0
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
        count += 1
        logged_wait(start, delta, count, "source")
        read.i_get_the_source(step, world.source['resource'])
        status = get_status(world.source)
    eq_(status['code'], int(code1))

#@step(r'I wait until the source is ready less than (\d+)')
def the_source_is_finished(step, secs):
    wait_until_source_status_code_is(step, FINISHED, FAULTY, secs)

#@step(r'I update the source with params "(.*)"')
def i_update_source_with(step, data="{}"):
    resource = world.api.update_source(world.source.get('resource'), json.loads(data))
    world.status = resource['code']
    eq_(world.status, HTTP_ACCEPTED)

#@step(r'the source exists and has args "(.*)"')
def source_has_args(step, args="{}"):
    args = json.loads(args)
    for key, value in list(args.items()):
        if key in world.source:
            eq_(world.source[key], value,
                "Expected key %s: %s. Found %s" % (key, value, world.source[key]))
        else:
            assert False, "No key %s in source." % key
