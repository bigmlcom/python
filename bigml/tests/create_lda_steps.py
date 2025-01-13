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

from bigml.api import HTTP_CREATED
from bigml.api import HTTP_ACCEPTED
from bigml.api import FINISHED
from bigml.api import FAULTY
from bigml.api import get_status
from bigml.topicmodel import TopicModel

from .world import world, res_filename, eq_
from .read_resource_steps import wait_until_status_code_is


def i_create_a_topic_model(step):
    """Step: I create a Topic Model"""
    dataset = world.dataset.get('resource')
    resource = world.api.create_topic_model(
        dataset, {'seed': 'BigML', 'topicmodel_seed': 'BigML'})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.topic_model = resource['object']
    world.topic_models.append(resource['resource'])


def i_create_a_topic_model_from_dataset_list(step):
    """Step: I create a topic model from a dataset list"""
    resource = world.api.create_topic_model(step.bigml["dataset_ids"])
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.topic_model = resource['object']
    world.topic_models.append(resource['resource'])


def i_create_a_topic_model_with_options(step, options):
    """Step: I create a topic model with options <options>"""
    dataset = world.dataset.get('resource')
    options = json.loads(options)
    options.update({'seed': 'BigML',
                    'topicmodel_seed': 'BigML'})
    resource = world.api.create_topic_model(
        dataset, options)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.topic_model = resource['object']
    world.topic_models.append(resource['resource'])


def i_update_topic_model_name(step, name):
    """Step: I update the topic model name to <name>"""
    resource = world.api.update_topic_model(world.topic_model['resource'],
                                            {'name': name})
    world.status = resource['code']
    eq_(world.status, HTTP_ACCEPTED)
    world.location = resource['location']
    world.topic_model = resource['object']


def wait_until_topic_model_status_code_is(step, code1, code2, secs):
    """Step: I wait until the topic model status code is either
    <code1> or <code2> less than <secs>
    """
    world.topic_model = wait_until_status_code_is(
        code1, code2, secs, world.topic_model)


def the_topic_model_is_finished_in_less_than(step, secs):
    """Steps: I wait until the topic model is ready less than <secs>"""
    wait_until_topic_model_status_code_is(step, FINISHED, FAULTY, secs)


def make_the_topic_model_shared(step):
    """Step: I make the topic model shared """
    resource = world.api.update_topic_model(world.topic_model['resource'],
                                            {'shared': True})
    world.status = resource['code']
    eq_(world.status, HTTP_ACCEPTED)
    world.location = resource['location']
    world.topic_model = resource['object']


def get_sharing_info(step):
    """Step: I get the topic_model sharing info"""
    world.shared_hash = world.topic_model['shared_hash']
    world.sharing_key = world.topic_model['sharing_key']


def topic_model_from_shared_url(step):
    """Step: I check the topic model status using the topic model\'s
    shared url
    """
    world.topic_model = world.api.get_topic_model("shared/topicmodel/%s" %
                                          world.shared_hash)
    eq_(get_status(world.topic_model)['code'], FINISHED)


def topic_model_from_shared_key(step):
    """Step: I check the topic model status using the topic model\'s
    shared key
    """
    username = os.environ.get("BIGML_USERNAME")
    world.topic_model = world.api.get_topic_model( \
        world.topic_model['resource'],
        shared_username=username, shared_api_key=world.sharing_key)
    eq_(get_status(world.topic_model)['code'], FINISHED)


def i_check_topic_model_name(step, name):
    """Step: the topic model name is <name>"""
    topic_model_name = world.topic_model['name']
    eq_(name, topic_model_name)


def i_create_a_topic_distribution(step, data=None):
    """Step: Create topic distribution """
    if data is None:
        data = "{}"
    topic_model = world.topic_model['resource']
    data = json.loads(data)
    resource = world.api.create_topic_distribution(topic_model, data)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.topic_distribution = resource['object']
    world.topic_distributions.append(resource['resource'])


def i_create_a_local_topic_distribution(step, data=None):
    """Step: I create a local topic distribution"""
    step.bigml["local_topic_distribution"] = \
        step.bigml["local_topic_model"].distribution(json.loads(data))


def i_export_topic_model(step, filename):
    """Step: I export the topic model"""
    world.api.export(world.topic_model.get('resource'),
                     filename=res_filename(filename))


def i_create_local_topic_model_from_file(step, export_file):
    """Step: I create a local topic model from file <export_file>"""
    step.bigml["local_topic_model"] = TopicModel(res_filename(export_file))


def check_topic_model_id_local_id(step):
    """Step: the topic model ID and the local topic model ID match"""
    eq_(step.bigml["local_topic_model"].resource_id,
        world.topic_model["resource"])


def clone_topic_model(step, topic_model):
    """Step: I clone topic model"""
    resource = world.api.clone_topic_model(topic_model,
                                           {'project': world.project_id})
    # update status
    world.status = resource['code']
    world.location = resource['location']
    world.topic_model = resource['object']
    # save reference
    world.topic_models.append(resource['resource'])


def the_cloned_topic_model_is(step, topic_model):
    """Check cloned topic model"""
    eq_(world.topic_model["origin"], topic_model)
