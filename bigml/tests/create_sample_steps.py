# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015-2020 BigML
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
from datetime import datetime
from world import world, logged_wait
from nose.tools import eq_, assert_less

from bigml.api import HTTP_CREATED
from bigml.api import HTTP_ACCEPTED
from bigml.api import FINISHED
from bigml.api import FAULTY
from bigml.api import get_status

from read_sample_steps import i_get_the_sample


#@step(r'the sample name is "(.*)"')
def i_check_sample_name(step, name):
    sample_name = world.sample['name']
    eq_(name, sample_name)

#@step(r'I create a sample from a dataset$')
def i_create_a_sample_from_dataset(step):
    dataset = world.dataset.get('resource')
    resource = world.api.create_sample(dataset, {'name': 'new sample'})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.sample = resource['object']
    world.samples.append(resource['resource'])


#@step(r'I update the sample name to "(.*)"$')
def i_update_sample_name(step, name):
    resource = world.api.update_sample(world.sample['resource'],
                                       {'name': name})
    world.status = resource['code']
    eq_(world.status, HTTP_ACCEPTED)
    world.location = resource['location']
    world.sample = resource['object']


#@step(r'I wait until the sample status code is either (\d) or (-\d) less than (\d+)')
def wait_until_sample_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    delta = int(secs) * world.delta
    sample_id = world.sample['resource']
    i_get_the_sample(step, sample_id)
    status = get_status(world.sample)
    count = 0
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
        count += 1
        logged_wait(start, delta, count, "sample")
        assert_less((datetime.utcnow() - start).seconds, delta)
        i_get_the_sample(step, sample_id)
        status = get_status(world.sample)
    eq_(status['code'], int(code1))


#@step(r'I wait until the sample is ready less than (\d+)')
def the_sample_is_finished_in_less_than(step, secs):
    wait_until_sample_status_code_is(step, FINISHED, FAULTY, secs)
