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

import time
import json
import os
from datetime import datetime
from nose.tools import eq_, ok_, assert_less
from .world import world, res_filename

from .read_resource_steps import wait_until_status_code_is

from bigml.api import HTTP_CREATED
from bigml.api import HTTP_ACCEPTED
from bigml.api import FINISHED
from bigml.api import FAULTY
from bigml.api import get_status
from bigml.anomaly import Anomaly


#@step(r'I check the anomaly detector stems from the original dataset list')
def i_check_anomaly_datasets_and_datasets_ids(step):
    anomaly = world.anomaly
    ok_('datasets' in anomaly and anomaly['datasets'] == world.dataset_ids,
        ("The anomaly detector contains only %s and the dataset ids are %s" %
         (",".join(anomaly['datasets']), ",".join(world.dataset_ids))))

#@step(r'I check the anomaly detector stems from the original dataset')
def i_check_anomaly_dataset_and_datasets_ids(step):
    anomaly = world.anomaly
    ok_('dataset' in anomaly and anomaly['dataset'] == world.dataset['resource'],
        ("The anomaly detector contains only %s and the dataset id is %s" %
         (anomaly['dataset'], world.dataset['resource'])))


#@step(r'I create an anomaly detector$')
def i_create_an_anomaly(step, shared=None):
    i_create_an_anomaly_from_dataset(step, shared=shared)


#@step(r'I clone anomaly')
def clone_anomaly(step, anomaly):
    resource = world.api.clone_anomaly(anomaly,
                                       {'project': world.project_id})
    # update status
    world.status = resource['code']
    world.location = resource['location']
    world.anomaly = resource['object']
    # save reference
    world.anomalies.append(resource['resource'])


def the_cloned_anomaly_is(step, anomaly):
    eq_(world.anomaly["origin"], anomaly)


#@step(r'I create an anomaly detector from a dataset$')
def i_create_an_anomaly_from_dataset(step, shared=None):
    if shared is None or world.shared.get("anomaly", {}).get(shared) is None:
        dataset = world.dataset.get('resource')
        resource = world.api.create_anomaly(dataset, {'seed': 'BigML'})
        world.status = resource['code']
        eq_(world.status, HTTP_CREATED)
        world.location = resource['location']
        world.anomaly = resource['object']
        world.anomalies.append(resource['resource'])


#@step(r'I create an anomaly detector with (\d+) anomalies from a dataset$')
def i_create_an_anomaly_with_top_n_from_dataset(step, top_n):
    dataset = world.dataset.get('resource')
    resource = world.api.create_anomaly(
        dataset, {'seed': 'BigML', 'top_n': int(top_n)})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED,
        "Expected: %s, found: %s" % (HTTP_CREATED, world.status))
    world.location = resource['location']
    world.anomaly = resource['object']
    world.anomalies.append(resource['resource'])


#@step(r'I create an anomaly detector with (\d+) from a dataset$')
def i_create_an_anomaly_with_params(step, parms=None):
    dataset = world.dataset.get('resource')
    if parms is not None:
        parms = json.loads(parms)
    else:
        parms = {}
    parms.update({"seed": 'BigML'})
    resource = world.api.create_anomaly(
        dataset, parms)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED,
        "Expected: %s, found: %s" % (HTTP_CREATED, world.status))
    world.location = resource['location']
    world.anomaly = resource['object']
    world.anomalies.append(resource['resource'])


#@step(r'I create an anomaly detector from a dataset list$')
def i_create_an_anomaly_from_dataset_list(step):
    resource = world.api.create_anomaly(world.dataset_ids, {'seed': 'BigML'})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.anomaly = resource['object']
    world.anomalies.append(resource['resource'])


#@step(r'I wait until the anomaly detector status code is either (\d) or (-\d) less than (\d+)')
def wait_until_anomaly_status_code_is(step, code1, code2, secs):
    world.anomaly = wait_until_status_code_is(
        code1, code2, secs, world.anomaly)


#@step(r'I wait until the anomaly detector is ready less than (\d+)')
def the_anomaly_is_finished_in_less_than(step, secs, shared=None):
    if shared is None or world.shared.get("anomaly", {}).get(shared) is None:
        wait_until_anomaly_status_code_is(step, FINISHED, FAULTY, secs)
        if shared is not None:
            if "anomaly" not in world.shared:
                world.shared["anomaly"] = {}
            world.shared["anomaly"][shared] = world.anomaly
    else:
        world.anomaly = world.shared["anomaly"][shared]
        print("Reusing %s" % world.anomaly["resource"])


#@step(r'I create a dataset with only the anomalies')
def create_dataset_with_anomalies(step):
    local_anomalies = Anomaly(world.anomaly['resource'])
    world.dataset = world.api.create_dataset(
        world.dataset['resource'],
        {"lisp_filter": local_anomalies.anomalies_filter()})
    world.datasets.append(world.dataset['resource'])


#@step(r'I check that the dataset has (\d+) rows')
def the_dataset_has_n_rows(step, rows):
    eq_(world.dataset['rows'], int(rows))


#@step(r'I export the anomaly$')
def i_export_anomaly(step, filename):
    world.api.export(world.anomaly.get('resource'),
                     filename=res_filename(filename))


#@step(r'I create a local anomaly from file "(.*)"')
def i_create_local_anomaly_from_file(step, export_file):
    world.local_anomaly = Anomaly(res_filename(export_file))


#@step(r'the anomaly ID and the local anomaly ID match')
def check_anomaly_id_local_id(step):
    eq_(world.local_anomaly.resource_id, world.anomaly["resource"])
