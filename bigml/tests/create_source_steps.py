# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument,no-member
#
# Copyright 2012, 2015-2025 BigML
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
import csv

from bigml.api import HTTP_ACCEPTED
from bigml.api import FINISHED, FAULTY

from .read_resource_steps import wait_until_status_code_is
from .world import world, res_filename, eq_, ok_


def i_upload_a_file(step, filename, shared=None):
    """Step: I create a data source uploading a <filename> file"""

    if shared is None or world.shared.get("source", {}).get(shared) is None:
        resource = world.api.create_source(res_filename(filename), \
            {'project': world.project_id})
        # update status
        world.status = resource['code']
        world.location = resource['location']
        world.source = resource['object']
        # save reference
        world.sources.append(resource['resource'])


def i_upload_a_file_with_project_conn(step, filename):
    """Step: I create a data source uploading a <filename> file using
    a project
    """
    resource = world.api.create_source(res_filename(filename))
    # update status
    world.status = resource['code']
    world.location = resource['location']
    world.source = resource['object']
    # save reference
    world.sources.append(resource['resource'])


def i_upload_a_file_from_stdin(step, filename):
    """Step: I create a data source from stdin uploading a <filename> file """
    file_name = res_filename(filename)
    with open(file_name, 'rb') as file_handler:
        resource = world.api.create_source(file_handler, \
            {'project': world.project_id})
        # update status
        world.status = resource['code']
        world.location = resource['location']
        world.source = resource['object']
        # save reference
        world.sources.append(resource['resource'])


def i_upload_a_file_with_args(step, filename, args):
    """Step: I create a data source uploading a <filename> file with args
    <args>
    """
    args = json.loads(args)
    args.update({'project': world.project_id})
    resource = world.api.create_source(res_filename(filename), args)
    # update status
    world.status = resource['code']
    world.location = resource['location']
    world.source = resource['object']
    # save reference
    world.sources.append(resource['resource'])


def i_create_using_url(step, url):
    """Step: I create a data source using the url <url> """
    resource = world.api.create_source(url, {'project': world.project_id})
    # update status
    world.status = resource['code']
    world.location = resource['location']
    world.source = resource['object']
    # save reference
    world.sources.append(resource['resource'])


def i_create_using_connector(step, connector):
    """Step: I create a data source using the connection <connector>"""
    resource = world.api.create_source(connector, {'project': world.project_id})
    # update status
    world.status = resource['code']
    world.location = resource['location']
    world.source = resource['object']
    # save reference
    world.sources.append(resource['resource'])


def i_create_composite(step, sources):
    """Step: I create from list of sources <sources>"""
    resource = world.api.create_source(sources, {'project': world.project_id})
    # update status
    world.status = resource['code']
    world.location = resource['location']
    world.source = resource['object']
    # save reference
    world.composites.append(resource['resource'])


def the_composite_contains(step, sources):
    """Checking source in composite"""
    eq_(world.source["sources"], sources)


def clone_source(step, source):
    """Step: I clone source"""
    resource = world.api.clone_source(source, {'project': world.project_id})
    # update status
    world.status = resource['code']
    world.location = resource['location']
    world.source = resource['object']
    # save reference
    world.sources.append(resource['resource'])


def the_cloned_source_origin_is(step, source):
    """Checking cloned source"""
    eq_(world.source["origin"], source)


def i_create_annotated_source(step, directory, args=None):
    """Creating annotated source"""
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


#pylint: disable=locally-disabled,unnecessary-comprehension
def i_create_using_dict_data(step, data):
    """Step: I create a data source from inline data slurped from <data>"""
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


def i_upload_a_file_async(step, filename):
    """Step: I create a data source uploading a <filename> file in
    asynchronous mode
    """
    resource = world.api.create_source(res_filename(filename),
                                       {'project': world.project_id},
                                       async_load=True)
    world.resource = resource


def the_source_has_been_created_async(step, secs):
    """Step: I wait until the source has been created less than <secs> secs"""
    world.source = wait_until_status_code_is(
        FINISHED, FAULTY, secs, world.source)


def wait_until_source_status_code_is(step, code1, code2, secs):
    """Step: I wait until the source status code is either
    <code1> or <code2> less than <secs>
    """
    world.source = wait_until_status_code_is(code1, code2, secs, world.source)


def the_source_is_finished(step, secs, shared=None):
    """Step: I wait until the source is ready less than <secs> """
    if shared is None or world.shared.get("source", {}).get(shared) is None:
        wait_until_source_status_code_is(step, FINISHED, FAULTY, secs)
        if shared is not None:
            if world.shared.get("source") is None:
                world.shared["source"] = {}
            world.shared["source"][shared] = world.source
    else:
        world.source = world.shared["source"][shared]
        print("Reusing %s" % world.source["resource"])


def i_update_source_with(step, data="{}"):
    """Step: I update the source with params <data>"""
    resource = world.api.update_source(world.source.get('resource'), json.loads(data))
    world.status = resource['code']
    eq_(world.status, HTTP_ACCEPTED)
    world.api.ok(resource)


def source_has_args(step, args="{}"):
    """Step: the source exists and has args <args>"""
    args = json.loads(args)
    for key, value in list(args.items()):
        if key in world.source:
            eq_(world.source[key], value,
                "Expected key %s: %s. Found %s" % (key, value, world.source[key]))
        else:
            ok_(False, "No key %s in source." % key)
