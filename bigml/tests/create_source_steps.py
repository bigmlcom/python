# -*- coding: utf-8 -*-

#
# Copyright 2012, 2015-2022 BigML
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


from datetime import datetime
from .world import world, res_filename
from nose.tools import eq_, assert_less

from bigml.api import HTTP_CREATED, HTTP_ACCEPTED
from bigml.api import FINISHED
from bigml.api import FAULTY
from bigml.api import UPLOADING
from bigml.api import get_status


from .read_resource_steps import wait_until_status_code_is


#@step(r'I create a data source uploading a "(.*)" file$')
def i_upload_a_file(step, file, shared=None):
    if shared is None or world.shared.get("source", {}).get(shared) is None:
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

#@step(r'I create from list of sources ".*"')
def i_create_composite(step, sources):
    resource = world.api.create_source(sources, {'project': world.project_id})
    # update status
    world.status = resource['code']
    world.location = resource['location']
    world.source = resource['object']
    # save reference
    world.composites.append(resource['resource'])

def the_composite_contains(step, sources):
    eq_(world.source["sources"], sources)

#@step(r'I clone source')
def clone_source(step, source):
    resource = world.api.clone_source(source, {'project': world.project_id})
    # update status
    world.status = resource['code']
    world.location = resource['location']
    world.source = resource['object']
    # save reference
    world.sources.append(resource['resource'])

def the_cloned_source_origin_is(step, source):
    eq_(world.source["origin"], source)

def i_create_annotated_source(step, directory, args=None):
    if args is None:
        args = {}
    args.update({'project': world.project_id})
    resource = world.api.create_annotated_source(res_filename(directory),
                                                 args)
    # update status
    world.status = resource['code']
    world.location = resource['location']
    world.source = resource['object']
    # save reference
    world.composites.append(resource['resource'])

#@step(r'I create a data source from inline data slurped from "(.*)"')
def i_create_using_dict_data(step, data):
    # slurp CSV file to local variable
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
    world.source = wait_until_status_code_is(code1, code2, secs, world.source)


#@step(r'I wait until the source status code is either (\d) or (\d) less than (\d+)')
def wait_until_source_status_code_is(step, code1, code2, secs):
    world.source = wait_until_status_code_is(code1, code2, secs, world.source)


#@step(r'I wait until the source is ready less than (\d+)')
def the_source_is_finished(step, secs, shared=None):
    if shared is None or world.shared.get("source", {}).get(shared) is None:
        wait_until_source_status_code_is(step, FINISHED, FAULTY, secs)
        if shared is not None:
            if world.shared.get("source") is None:
                world.shared["source"] = {}
            world.shared["source"][shared] = world.source
    else:
        world.source = world.shared["source"][shared]
        print("Reusing %s" % world.source["resource"])

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
