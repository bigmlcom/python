# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2014-2015 BigML
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

from read_anomaly_steps import i_get_the_anomaly

from bigml.api import HTTP_CREATED
from bigml.api import HTTP_ACCEPTED
from bigml.api import FINISHED
from bigml.api import FAULTY
from bigml.api import get_status
from bigml.anomaly import Anomaly

#@step(r'I check the anomaly detector stems from the original dataset list')
def i_check_anomaly_datasets_and_datasets_ids(step):
    anomaly = world.anomaly
    if 'datasets' in anomaly and anomaly['datasets'] == world.dataset_ids:
        assert True
    else:
        assert False, ("The anomaly detector contains only %s "
                       "and the dataset ids are %s" %
                       (",".join(anomaly['datasets']),
                        ",".join(world.dataset_ids)))


#@step(r'I check the anomaly detector stems from the original dataset')
def i_check_anomaly_dataset_and_datasets_ids(step):
    anomaly = world.anomaly
    if 'dataset' in anomaly and anomaly['dataset'] == world.dataset['resource']:
        assert True
    else:
        assert False, ("The anomaly detector contains only %s "
                       "and the dataset id is %s" %
                       (anomaly['dataset'],
                        world.dataset['resource']))


#@step(r'I create an anomaly detector$')
def i_create_an_anomaly(step):
    i_create_an_anomaly_from_dataset(step)


#@step(r'I create an anomaly detector from a dataset$')
def i_create_an_anomaly_from_dataset(step):
    dataset = world.dataset.get('resource')
    resource = world.api.create_anomaly(dataset, {'seed': 'BigML'})
    world.status = resource['code']
    assert world.status == HTTP_CREATED
    world.location = resource['location']
    world.anomaly = resource['object']
    world.anomalies.append(resource['resource'])

#@step(r'I create an anomaly detector with (\d+) anomalies from a dataset$')
def i_create_an_anomaly_with_top_n_from_dataset(step, top_n):
    dataset = world.dataset.get('resource')
    resource = world.api.create_anomaly(
        dataset, {'seed': 'BigML', 'top_n': int(top_n)})
    world.status = resource['code']
    assert world.status == HTTP_CREATED, "Expected: %s, found: %s" % (
        HTTP_CREATED, world.status)
    world.location = resource['location']
    world.anomaly = resource['object']
    world.anomalies.append(resource['resource'])

#@step(r'I create an anomaly detector from a dataset list$')
def i_create_an_anomaly_from_dataset_list(step):
    resource = world.api.create_anomaly(world.dataset_ids, {'seed': 'BigML'})
    world.status = resource['code']
    assert world.status == HTTP_CREATED
    world.location = resource['location']
    world.anomaly = resource['object']
    world.anomalies.append(resource['resource'])

#@step(r'I wait until the anomaly detector status code is either (\d) or (-\d) less than (\d+)')
def wait_until_anomaly_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    i_get_the_anomaly(step, world.anomaly['resource'])
    status = get_status(world.anomaly)
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
           time.sleep(3)
           assert datetime.utcnow() - start < timedelta(seconds=int(secs))
           i_get_the_anomaly(step, world.anomaly['resource'])
           status = get_status(world.anomaly)
    assert status['code'] == int(code1)

#@step(r'I wait until the anomaly detector is ready less than (\d+)')
def the_anomaly_is_finished_in_less_than(step, secs):
    wait_until_anomaly_status_code_is(step, FINISHED, FAULTY, secs)

#@step(r'I create a dataset with only the anomalies')
def create_dataset_with_anomalies(step):
    local_anomalies = Anomaly(world.anomaly['resource'])
    world.dataset = world.api.create_dataset(
        world.dataset['resource'],
        {"lisp_filter": local_anomalies.anomalies_filter()})
    world.datasets.append(world.dataset['resource'])

#@step(r'I check that the dataset has (\d+) rows')
def the_dataset_has_n_rows(step, rows):
    assert world.dataset['rows'] == int(rows), "Expected: %s, found: %s" % (
        rows, world.dataset['rows'])
