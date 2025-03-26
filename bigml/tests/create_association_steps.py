# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument,no-member
#
# Copyright 2014-2025 BigML
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
from bigml.association import Association

from .read_resource_steps import wait_until_status_code_is
from .world import world, res_filename, eq_


def i_check_association_name(step, name):
    """Step: the association name is <name>"""
    association_name = world.association['name']
    eq_(name, association_name)


def i_create_an_association_from_dataset(step, shared=None):
    """Step: I create an association from a dataset"""
    if shared is None or world.shared.get("association", {}).get("shared") is None:
        dataset = world.dataset.get('resource')
        resource = world.api.create_association(dataset, {'name': 'new association'})
        world.status = resource['code']
        eq_(world.status, HTTP_CREATED)
        world.location = resource['location']
        world.association = resource['object']
        world.associations.append(resource['resource'])


def i_create_an_association_from_dataset_with_params(step, parms=None):
    """Step: I create an association from a dataset with params <parms>"""
    dataset = world.dataset.get('resource')
    if parms is not None:
        parms = json.loads(parms)
    else:
        parms = {}
    parms.update({'name': 'new association'})
    resource = world.api.create_association(dataset, parms)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.association = resource['object']
    world.associations.append(resource['resource'])


def i_create_an_association_with_strategy_from_dataset(step, strategy):
    """Step: I create an association with search strategy <strategy>
    from a dataset
    """
    dataset = world.dataset.get('resource')
    resource = world.api.create_association(
        dataset, {'name': 'new association', 'search_strategy': strategy})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.association = resource['object']
    world.associations.append(resource['resource'])


def i_update_association_name(step, name):
    """Step: I update the association name to <name>"""
    resource = world.api.update_association(world.association['resource'],
                                            {'name': name})
    world.status = resource['code']
    eq_(world.status, HTTP_ACCEPTED)
    world.location = resource['location']
    world.association = resource['object']


def wait_until_association_status_code_is(step, code1, code2, secs):
    """Step: I wait until the association status code is either <code1> or
    <code2> less than <secs>
    """
    world.association = wait_until_status_code_is(
        code1, code2, secs, world.association)


def the_association_is_finished_in_less_than(step, secs, shared=None):
    """Steps: I wait until the association is ready less than <secs>"""
    if shared is None or world.shared.get("association", {}).get(shared) is None:
        wait_until_association_status_code_is(step, FINISHED, FAULTY, secs)
        if shared is not None:
            if "association" not in world.shared:
                world.shared["association"] = {}
            world.shared["association"][shared] = world.association
    else:
        world.association = world.shared["association"][shared]
        print("Reusing %s" % world.association["resource"])


def i_create_a_local_association(step):
    """Step: I create a local association"""
    step.bigml["local_association"] = Association(world.association)


def i_get_rules_for_item_list(step, item_list):
    """Step: I get the rules for <item_list>"""
    world.association_rules = step.bigml["local_association"].get_rules(
        item_list=item_list)


def the_first_rule_is(step, rule):
    """Step: the first rule is <rule>"""
    found_rules = []
    for a_rule in world.association_rules:
        found_rules.append(a_rule.to_json())
    eq_(rule, found_rules[0])


def i_export_association(step, filename):
    """Step: I export the association"""
    world.api.export(world.association.get('resource'),
                     filename=res_filename(filename))


def i_create_local_association_from_file(step, export_file):
    """Step: I create a local association from file <export_file>"""
    step.bigml["local_association"] = Association(res_filename(export_file))


def check_association_id_local_id(step):
    """Step: the association ID and the local association ID match"""
    eq_(step.bigml["local_association"].resource_id,
        world.association["resource"])


def clone_association(step, association):
    """Step: I clone association"""
    resource = world.api.clone_association(association,
                                           {'project': world.project_id})
    # update status
    world.status = resource['code']
    world.location = resource['location']
    world.association = resource['object']
    # save reference
    world.associations.append(resource['resource'])


def the_cloned_association_is(step, association):
    """The association is a clone"""
    eq_(world.association["origin"], association)
