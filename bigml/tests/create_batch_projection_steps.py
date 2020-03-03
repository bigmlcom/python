# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2018-2020 BigML
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
import requests
import csv
import traceback
from datetime import datetime
from world import world, res_filename, logged_wait
from nose.tools import eq_, ok_, assert_less

from bigml.api import HTTP_CREATED
from bigml.api import FINISHED
from bigml.api import FAULTY
from bigml.api import get_status
from bigml.io import UnicodeReader

from read_batch_projection_steps import i_get_the_batch_projection


#@step(r'I create a batch projection for the dataset with the PCA$')
def i_create_a_batch_projection(step):
    dataset = world.dataset.get('resource')
    pca = world.pca.get('resource')
    resource = world.api.create_batch_projection(pca, dataset)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.batch_projection = resource['object']
    world.batch_projections.append(resource['resource'])


#@step(r'I wait until the batch projection status code is either (\d) or (-\d) less than (\d+)')
def wait_until_batch_projection_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    delta = int(secs) * world.delta
    i_get_the_batch_projection(step, world.batch_projection['resource'])
    status = get_status(world.batch_projection)
    count = 0
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
        count += 1
        logged_wait(start, delta, count, "batchprojection")
        assert_less((datetime.utcnow() - start).seconds, delta)
        i_get_the_batch_projection(step, world.batch_projection['resource'])
        status = get_status(world.batch_projection)
    eq_(status['code'], int(code1))


#@step(r'I wait until the batch projection is ready less than (\d+)')
def the_batch_projection_is_finished_in_less_than(step, secs):
    wait_until_batch_projection_status_code_is(step, FINISHED, FAULTY, secs)

#@step(r'I download the created projections file to "(.*)"')
def i_download_projections_file(step, filename):
    file_object = world.api.download_batch_projection(
        world.batch_projection, filename=res_filename(filename))
    ok_(file_object is not None)
    world.output = file_object

#@step(r'the batch projection file is like "(.*)"')
def i_check_projections(step, check_file):
    with UnicodeReader(world.output) as projection_rows:
        with UnicodeReader(res_filename(check_file)) as test_rows:
            check_csv_rows(projection_rows, test_rows)

def check_csv_rows(projections, expected):
    for projection in projections:
        eq_(projection, expected.next())
