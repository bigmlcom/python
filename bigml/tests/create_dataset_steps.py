# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument,no-member
#
# Copyright 2012-2022 BigML
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

from bigml.api import HTTP_CREATED, HTTP_OK, HTTP_ACCEPTED
from bigml.api import FINISHED, FAULTY
from bigml.api import get_status

from .read_resource_steps import wait_until_status_code_is
from .world import world, res_filename, eq_


def i_create_a_dataset(step, shared=None):
    """Step: I create a dataset"""
    if shared is None or world.shared.get("dataset", {}).get(shared) is None:
        resource = world.api.create_dataset(world.source['resource'])
        world.status = resource['code']
        eq_(world.status, HTTP_CREATED)
        world.location = resource['location']
        world.dataset = resource['object']
        world.datasets.append(resource['resource'])


def i_export_a_dataset(step, local_file):
    """Step: I download the dataset file to <local_file>"""
    world.api.download_dataset(world.dataset['resource'],
                               filename=res_filename(local_file))


def files_equal(step, local_file, data):
    """Step: file <local_file> is like file <data>"""
    with open(res_filename(local_file)) as handler:
        contents_local_file = handler.read()
    with open(res_filename(data)) as handler:
        contents_data = handler.read()
    eq_(contents_local_file, contents_data)


def i_create_a_dataset_with(step, data="{}"):
    """Step: I create a dataset with <data>"""
    resource = world.api.create_dataset(world.source['resource'],
                                        json.loads(data))
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.dataset = resource['object']
    world.datasets.append(resource['resource'])


def wait_until_dataset_status_code_is(step, code1, code2, secs):
    """Step: I wait until the dataset status code is either <code1> or
    <code2> less than <secs>
    """
    world.dataset = wait_until_status_code_is(
        code1, code2, secs, world.dataset)


def the_dataset_is_finished_in_less_than(step, secs, shared=None):
    """Step: I wait until the dataset is ready less than <secs>"""
    if shared is None or world.shared.get("dataset", {}).get(shared) is None:
        wait_until_dataset_status_code_is(step, FINISHED, FAULTY, secs)
        if shared is not None:
            if "dataset" not in world.shared:
                world.shared["dataset"] = {}
            world.shared["dataset"][shared]= world.dataset
    else:
        world.dataset = world.shared["dataset"][shared]
        print("Reusing %s" % world.dataset["resource"])


def make_the_dataset_public(step):
    """Step: I make the dataset public"""
    resource = world.api.update_dataset(world.dataset['resource'],
                                        {'private': False})
    world.status = resource['code']
    eq_(world.status, HTTP_ACCEPTED)
    world.location = resource['location']
    world.dataset = resource['object']


def build_local_dataset_from_public_url(step):
    """Step: I get the dataset status using the dataset's public url"""
    world.dataset = world.api.get_dataset("public/%s" %
                                          world.dataset['resource'])

def dataset_status_finished(step):
    """Step: the dataset's status is FINISHED"""
    eq_(get_status(world.dataset)['code'], FINISHED)


def i_create_a_split_dataset(step, rate):
    """Step: I create a dataset extracting a <rate> sample"""
    world.origin_dataset = world.dataset
    resource = world.api.create_dataset(world.dataset['resource'],
                                        {'sample_rate': float(rate)})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.dataset = resource['object']
    world.datasets.append(resource['resource'])


def i_create_a_multidataset(step, ranges):
    """Step: I create a multidataset with ranges <ranges>"""
    ranges = json.loads(ranges)
    datasets = world.datasets[-len(ranges):]
    world.origin_dataset = world.dataset
    resource = world.api.create_dataset( \
        datasets,
        {'sample_rates': dict(list(zip(datasets, ranges)))})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.dataset = resource['object']
    world.datasets.append(resource['resource'])


def i_create_a_multidataset_mixed_format(step, ranges):
    """Step: I create a multi-dataset with same datasets and the first sample
    rate <ranges>
    """
    ranges = json.loads(ranges)
    dataset = world.dataset['resource']
    origins = []
    for value in ranges:
        if value == 1:
            origins.append(dataset)
        else:
            origins.append({"id": dataset,
                            "sample_rate": value})
    world.origin_dataset = world.dataset
    resource = world.api.create_dataset( \
        origins)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.dataset = resource['object']
    world.datasets.append(resource['resource'])


def i_compare_datasets_instances(step):
    """Step: I compare the datasets' instances"""
    world.datasets_instances = (world.dataset['rows'],
                                world.origin_dataset['rows'])


def proportion_datasets_instances(step, rate):
    """Step: the proportion of instances between datasets is <rate>"""
    eq_(int(world.datasets_instances[1] * float(rate)),
        world.datasets_instances[0])


def i_create_a_dataset_from_cluster(step, centroid_id):
    """Step: I create a dataset associated to centroid <centroid_id>"""
    resource = world.api.create_dataset(
        world.cluster['resource'],
        args={'centroid': centroid_id})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.dataset = resource['object']
    world.datasets.append(resource['resource'])


def i_create_a_dataset_from_cluster_centroid(step):
    """Step: I create a dataset from the cluster and the centroid"""
    i_create_a_dataset_from_cluster(step, world.centroid['centroid_id'])


def is_associated_to_centroid_id(step, centroid_id):
    """Step: the dataset is associated to the centroid <centroid_id>
    of the cluster
    """
    cluster = world.api.get_cluster(world.cluster['resource'])
    world.status = cluster['code']
    eq_(world.status, HTTP_OK)
    eq_("dataset/%s" % (cluster['object']['cluster_datasets'][centroid_id]),
        world.dataset['resource'])


def i_check_dataset_from_cluster_centroid(step):
    """Step: I check that the dataset is created for the cluster and the
    centroid
    """
    is_associated_to_centroid_id(step, world.centroid['centroid_id'])


def i_update_dataset_with(step, data="{}"):
    """Step: I update the dataset with params <data>"""
    resource = world.api.update_dataset(world.dataset.get('resource'),
                                        json.loads(data))
    world.status = resource['code']
    eq_(world.status, HTTP_ACCEPTED)


def clone_dataset(step, dataset):
    """Step: I clone dataset"""
    resource = world.api.clone_dataset(dataset, {'project': world.project_id})
    # update status
    world.status = resource['code']
    world.location = resource['location']
    world.dataset = resource['object']
    # save reference
    world.datasets.append(resource['resource'])


def the_cloned_dataset_is(step, dataset):
    """Checking the dataset is a clone"""
    eq_(world.dataset["origin"], dataset)
