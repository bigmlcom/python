# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument,no-member
#
# Copyright 2018-2023 BigML
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

from bigml.api import HTTP_CREATED, HTTP_ACCEPTED
from bigml.api import FINISHED, FAULTY

from .read_resource_steps import wait_until_status_code_is
from .world import world, eq_


def i_check_pca_name(step, name):
    """Step: the pca name is <name>"""
    pca_name = world.pca['name']
    eq_(name, pca_name)


def i_create_a_pca_from_dataset(step, shared=None):
    """Step: I create a PCA from a dataset"""
    if shared is None or world.shared.get("pca", {}).get(shared) is None:
        dataset = world.dataset.get('resource')
        resource = world.api.create_pca(dataset, {'name': 'new PCA'})
        world.status = resource['code']
        eq_(world.status, HTTP_CREATED)
        world.location = resource['location']
        world.pca = resource['object']
        world.pcas.append(resource['resource'])


def i_create_a_pca_with_params(step, params):
    """Step: I create a PCA from a dataset"""
    params = json.loads(params)
    dataset = world.dataset.get('resource')
    resource = world.api.create_pca(dataset, params)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.pca = resource['object']
    world.pcas.append(resource['resource'])


def i_create_a_pca(step, shared=None):
    """Creating a PCA"""
    i_create_a_pca_from_dataset(step, shared=shared)


def i_update_pca_name(step, name):
    """Step: I update the PCA name to <name>"""
    resource = world.api.update_pca(world.pca['resource'],
                                    {'name': name})
    world.status = resource['code']
    eq_(world.status, HTTP_ACCEPTED)
    world.location = resource['location']
    world.pca = resource['object']


def wait_until_pca_status_code_is(step, code1, code2, secs):
    """Step: I wait until the PCA status code is either <code1> or
    <code2> less than <secs>
    """
    world.pca = wait_until_status_code_is(code1, code2, secs, world.pca)


def the_pca_is_finished_in_less_than(step, secs, shared=None):
    """Step: I wait until the PCA is ready less than <secs>"""
    if shared is None or world.shared.get("pca", {}).get(shared) is None:
        wait_until_pca_status_code_is(step, FINISHED, FAULTY, secs)
        if shared is not None:
            if "pca" not in world.shared:
                world.shared["pca"] = {}
            world.shared["pca"][shared] = world.pca
    else:
        world.pca = world.shared["pca"][shared]
        print("Reusing %s" % world.pca["resource"])


def clone_pca(step, pca):
    """Step: I clone pca"""
    resource = world.api.clone_pca(pca,
                                   {'project': world.project_id})
    # update status
    world.status = resource['code']
    world.location = resource['location']
    world.pca = resource['object']
    # save reference
    world.pcas.append(resource['resource'])


def the_cloned_pca_is(step, pca):
    """Checking that pca is a clone """
    eq_(world.pca["origin"], pca)
