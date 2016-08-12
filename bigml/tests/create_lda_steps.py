# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2012-2016 BigML
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
import os
from datetime import datetime, timedelta
from world import world

from read_lda_steps import i_get_the_lda

from bigml.api import HTTP_CREATED
from bigml.api import HTTP_ACCEPTED
from bigml.api import FINISHED
from bigml.api import FAULTY
from bigml.api import get_status

#@step(r'I create an lda')
def i_create_an_lda(step):
    dataset = world.dataset.get('resource')
    resource = world.api.create_lda(
        dataset, {'seed': 'BigML', 'lda_seed': 'BigML'})
    world.status = resource['code']
    assert world.status == HTTP_CREATED
    world.location = resource['location']
    world.lda = resource['object']
    world.ldas.append(resource['resource'])

#@step(r'I create an lda from a dataset list$')
def i_create_an_lda_from_dataset_list(step):
    resource = world.api.create_lda(world.dataset_ids)
    world.status = resource['code']
    assert world.status == HTTP_CREATED
    world.location = resource['location']
    world.lda = resource['object']
    world.ldas.append(resource['resource'])


#@step(r'I create an lda with options "(.*)"$')
def i_create_an_lda_with_options(step, options):
    dataset = world.dataset.get('resource')
    options = json.loads(options)
    options.update({'seed': 'BigML',
                    'lda_seed': 'BigML'})
    resource = world.api.create_cluster(
        dataset, options)
    world.status = resource['code']
    assert world.status == HTTP_CREATED
    world.location = resource['location']
    world.lda = resource['object']
    world.ldas.append(resource['resource'])

#@step(r'I wait until the lda status code is either (\d) or (-\d) less than (\d+)')
def wait_until_lda_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    i_get_the_lda(step, world.lda['resource'])
    status = get_status(world.lda)
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
           time.sleep(3)
           assert datetime.utcnow() - start < timedelta(seconds=int(secs))
           i_get_the_lda(step, world.lda['resource'])
           status = get_status(world.lda)
    assert status['code'] == int(code1)

#@step(r'I wait until the lda is ready less than (\d+)')
def the_lda_is_finished_in_less_than(step, secs):
    wait_until_lda_status_code_is(step, FINISHED, FAULTY, secs)

#@step(r'I make the lda shared')
def make_the_lda_shared(step):
    resource = world.api.update_lda(world.lda['resource'],
                                      {'shared': True})
    world.status = resource['code']
    assert world.status == HTTP_ACCEPTED
    world.location = resource['location']
    world.lda = resource['object']

#@step(r'I get the lda sharing info')
def get_sharing_info(step):
    world.shared_hash = world.lda['shared_hash']
    world.sharing_key = world.lda['sharing_key']

#@step(r'I check the lda status using the lda\'s shared url')
def lda_from_shared_url(step):
    world.lda = world.api.get_lda("shared/lda/%s" % world.shared_hash)
    assert get_status(world.lda)['code'] == FINISHED

#@step(r'I check the lda status using the lda\'s shared key')
def lda_from_shared_key(step):

    username = os.environ.get("BIGML_USERNAME")
    world.lda = world.api.get_lda(world.lda['resource'],
        shared_username=username, shared_api_key=world.sharing_key)
    assert get_status(world.lda)['code'] == FINISHED
