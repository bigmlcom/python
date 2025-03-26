# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument,no-member
#
# Copyright 2012-2025 BigML
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
import os

from bigml.api import HTTP_CREATED, HTTP_ACCEPTED
from bigml.api import FINISHED, FAULTY
from bigml.api import get_status
from bigml.cluster import Cluster

from .read_resource_steps import wait_until_status_code_is
from .world import world, res_filename, eq_


def i_create_a_cluster(step, shared=None):
    """Step: I create a cluster"""
    if shared is None or world.shared.get("cluster", {}).get(shared) is None:
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


def i_create_a_cluster_from_dataset_list(step):
    """Step: I create a cluster from a dataset list"""
    resource = world.api.create_cluster(step.bigml["dataset_ids"])
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.cluster = resource['object']
    world.clusters.append(resource['resource'])


def i_create_a_cluster_with_options(step, options):
    """Step: I create a cluster with options <options>"""
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


def wait_until_cluster_status_code_is(step, code1, code2, secs):
    """Step: I wait until the cluster status code is either <code1> or
    <code2> less than <secs>"""
    world.cluster = wait_until_status_code_is(
        code1, code2, secs, world.cluster)


def the_cluster_is_finished_in_less_than(step, secs, shared=None):
    """Step: I wait until the cluster is ready less than <secs>"""
    if shared is None or world.shared.get("cluster", {}).get(shared) is None:
        wait_until_cluster_status_code_is(step, FINISHED, FAULTY, secs)
        if shared is not None:
            if "cluster" not in world.shared:
                world.shared["cluster"] = {}
            world.shared["cluster"][shared] = world.cluster
    else:
        world.cluster = world.shared["cluster"][shared]
        print("Reusing %s" % world.cluster["resource"])


def make_the_cluster_shared(step):
    """Step: I make the cluster shared"""
    resource = world.api.update_cluster(world.cluster['resource'],
                                      {'shared': True})
    world.status = resource['code']
    eq_(world.status, HTTP_ACCEPTED)
    world.location = resource['location']
    world.cluster = resource['object']


def get_sharing_info(step):
    """Step: I get the cluster sharing info"""
    world.shared_hash = world.cluster['shared_hash']
    world.sharing_key = world.cluster['sharing_key']


def cluster_from_shared_url(step):
    """Step: I check the cluster status using the model's shared url"""
    world.cluster = world.api.get_cluster("shared/cluster/%s" % world.shared_hash)
    eq_(get_status(world.cluster)['code'], FINISHED)


def cluster_from_shared_key(step):
    """Step: I check the cluster status using the model's shared key"""
    username = os.environ.get("BIGML_USERNAME")
    world.cluster = world.api.get_cluster(world.cluster['resource'],
        shared_username=username, shared_api_key=world.sharing_key)
    eq_(get_status(world.cluster)['code'], FINISHED)


def closest_in_cluster(step, reference, closest):
    """Step: the data point in the cluster closest to <reference> is <closest>"""
    local_cluster = step.bigml["local_cluster"]
    reference = json.loads(reference)
    closest = json.loads(closest)
    result = local_cluster.closest_in_cluster( \
        reference, number_of_points=1)["closest"][0]
    result = json.loads(json.dumps(result))
    eq_(closest, result)


def closest_centroid_in_cluster(step, reference, closest_id):
    """Step: the centroid in the cluster closest to <reference> is
    <closest_id>
    """
    local_cluster = step.bigml["local_cluster"]
    reference = json.loads(reference)
    result = local_cluster.sorted_centroids( \
        reference)
    result = result["centroids"][0]["centroid_id"]
    eq_(closest_id, result)

def i_export_cluster(step, filename):
    """Step: I export the cluster"""
    world.api.export(world.cluster.get('resource'),
                     filename=res_filename(filename))


def i_create_local_cluster_from_file(step, export_file):
    """Step: I create a local cluster from file <export_file>"""
    step.bigml["local_cluster"] = Cluster(res_filename(export_file))


def check_cluster_id_local_id(step):
    """Step: the cluster ID and the local cluster ID match"""
    eq_(step.bigml["local_cluster"].resource_id, world.cluster["resource"])


def clone_cluster(step, cluster):
    """Step: I clone cluster"""
    resource = world.api.clone_cluster(cluster,
                                       {'project': world.project_id})
    # update status
    world.status = resource['code']
    world.location = resource['location']
    world.cluster = resource['object']
    # save reference
    world.clusters.append(resource['resource'])


def the_cloned_cluster_is(step, cluster):
    """Checking the cluster is a clone"""
    eq_(world.cluster["origin"], cluster)
