# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2012 BigML
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
from datetime import datetime, timedelta
from urllib import urlencode
from lettuce import step, world

from bigml.api import HTTP_CREATED
from bigml.api import FINISHED
from bigml.api import FAULTY

@step(r'I create a data source uploading a "(.*)" file$')
def i_upload_a_file(step, file):
    resource = world.api.create_source(file)
    # update status
    world.status = resource['code']
    world.location = resource['location']
    world.source = resource['object']
    # save reference
    world.sources.append(resource['resource'])

@step(r'I create a data source using the url "(.*)"')
def i_create_using_url(step, url):
    resource = world.api.create_source_from_url(url)
    # update status
    world.status = resource['code']
    world.location = resource['location']
    world.source = resource['object']
    # save reference
    world.sources.append(resource['resource'])

@step(r'the source has been created')
def the_source_has_been_created(step):
    assert world.status == HTTP_CREATED

@step(r'I wait until the source status code is either (\d) or (\d) less than (\d+)')
def wait_until_source_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    step.given('I get the source "{id}"'.format(id=world.source['resource']))
    while (world.source['status']['code'] != int(code1) and
           world.source['status']['code'] != int(code2)):
           time.sleep(3)
           assert datetime.utcnow() - start < timedelta(seconds=int(secs))
           step.given('I get the source "{id}"'.format(id=world.source['resource']))
    assert world.source['status']['code'] == int(code1)

@step(r'I wait until the source is ready less than (\d+)')
def the_source_is_finished(step, secs):
    wait_until_source_status_code_is(step, FINISHED, FAULTY, secs)
