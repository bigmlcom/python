# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2012-2019 BigML
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
from world import world, res_filename
from nose.tools import eq_, assert_less

from read_cluster_steps import i_get_the_cluster

from bigml.api import HTTP_CREATED
from bigml.api import HTTP_ACCEPTED
from bigml.api import FINISHED
from bigml.api import FAULTY
from bigml.api import get_status
from bigml.cluster import Cluster


#@step(r'I create a cluster$')
def i_create_a_cluster(step):
    dataset = world.dataset.get('resource')
    resource = world.api.create_cluster(
        dataset, {'seed': 'BigML',
                  'cluster_seed': 'BigML',
                  'k': 8})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.cluster = resource['object']
    world.clusters.append(resource['resource'])

#@step(r'I create a cluster from a dataset list$')
def i_create_a_cluster_from_dataset_list(step):
    resource = world.api.create_cluster(world.dataset_ids)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.cluster = resource['object']
    world.clusters.append(resource['resource'])


#@step(r'I create a cluster with options "(.*)"$')
def i_create_a_cluster_with_options(step, options):
    dataset = world.dataset.get('resource')
    options = json.loads(options)
    options.update({'seed': 'BigML',
                    'cluster_seed': 'BigML',
                    'k': 8})
    resource = world.api.create_cluster(
        dataset, options)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.cluster = resource['object']
    world.clusters.append(resource['resource'])

#@step(r'I wait until the cluster status code is either (\d) or (-\d) less than (\d+)')
def wait_until_cluster_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    delta = int(secs) * world.delta
    i_get_the_cluster(step, world.cluster['resource'])
    status = get_status(world.cluster)
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
           time.sleep(3)
           assert_less((datetime.utcnow() - start).seconds, delta)
           i_get_the_cluster(step, world.cluster['resource'])
           status = get_status(world.cluster)
    eq_(status['code'], int(code1))

#@step(r'I wait until the cluster is ready less than (\d+)')
def the_cluster_is_finished_in_less_than(step, secs):
    wait_until_cluster_status_code_is(step, FINISHED, FAULTY, secs)

#@step(r'I make the cluster shared')
def make_the_cluster_shared(step):
    resource = world.api.update_cluster(world.cluster['resource'],
                                      {'shared': True})
    world.status = resource['code']
    eq_(world.status, HTTP_ACCEPTED)
    world.location = resource['location']
    world.cluster = resource['object']

#@step(r'I get the cluster sharing info')
def get_sharing_info(step):
    world.shared_hash = world.cluster['shared_hash']
    world.sharing_key = world.cluster['sharing_key']

#@step(r'I check the cluster status using the model\'s shared url')
def cluster_from_shared_url(step):
    world.cluster = world.api.get_cluster("shared/cluster/%s" % world.shared_hash)
    eq_(get_status(world.cluster)['code'], FINISHED)

#@step(r'I check the cluster status using the model\'s shared key')
def cluster_from_shared_key(step):

    username = os.environ.get("BIGML_USERNAME")
    world.cluster = world.api.get_cluster(world.cluster['resource'],
        shared_username=username, shared_api_key=world.sharing_key)
    eq_(get_status(world.cluster)['code'], FINISHED)

#@step(r'the data point in the cluster closest to "(.*)" is "(.*)"')
def closest_in_cluster(step, reference, closest):
    local_cluster = world.local_cluster
    reference = json.loads(reference)
    closest = json.loads(closest)
    result = local_cluster.closest_in_cluster( \
        reference, number_of_points=1)["closest"][0]
    result = json.loads(json.dumps(result))
    eq_(closest, result)

#@step(r'I export the cluster$')
def i_export_cluster(step, filename):
    world.api.export(world.cluster.get('resource'),
                     filename=res_filename(filename))

#@step(r'I create a local cluster from file "(.*)"')
def i_create_local_cluster_from_file(step, export_file):
    world.local_cluster = Cluster(res_filename(export_file))


#@step(r'the cluster ID and the local cluster ID match')
def check_cluster_id_local_id(step):
    eq_(world.local_cluster.resource_id, world.cluster["resource"])
