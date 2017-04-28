# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2012-2017 BigML
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
from nose.tools import eq_, assert_less
from datetime import datetime, timedelta
from world import world

from bigml.api import HTTP_OK
from bigml.api import HTTP_CREATED
from bigml.api import HTTP_ACCEPTED
from bigml.api import FINISHED
from bigml.api import FAULTY
from bigml.api import get_status

import read_model_steps as read

NO_MISSING_SPLITS = {'missing_splits': False}

#@step(r'I create a model$')
def i_create_a_model(step):
    dataset = world.dataset.get('resource')
    resource = world.api.create_model(dataset, args=NO_MISSING_SPLITS)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.model = resource['object']
    world.models.append(resource['resource'])

#@step(r'I create a balanced model$')
def i_create_a_balanced_model(step):
    dataset = world.dataset.get('resource')
    args = {}
    args.update(NO_MISSING_SPLITS)
    args.update({"balance_objective": True})
    resource = world.api.create_model(dataset, args=args)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.model = resource['object']
    world.models.append(resource['resource'])

#@step(r'I create a model from a dataset list$')
def i_create_a_model_from_dataset_list(step):
    resource = world.api.create_model(world.dataset_ids,
                                      args=NO_MISSING_SPLITS)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.model = resource['object']
    world.models.append(resource['resource'])

#@step(r'I wait until the model status code is either (\d) or (-\d) less than (\d+)')
def wait_until_model_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    read.i_get_the_model(step, world.model['resource'])
    status = get_status(world.model)
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
           time.sleep(3)
           assert_less(datetime.utcnow() - start, timedelta(seconds=int(secs)))
           read.i_get_the_model(step, world.model['resource'])
           status = get_status(world.model)
    eq_(status['code'], int(code1))

#@step(r'I wait until the model is ready less than (\d+)')
def the_model_is_finished_in_less_than(step, secs):
    wait_until_model_status_code_is(step, FINISHED, FAULTY, secs)

#@step(r'I create a model with "(.*)"')
def i_create_a_model_with(step, data="{}"):
    args = json.loads(data)
    if not 'missing_splits' in args:
        args.update(NO_MISSING_SPLITS)
    resource = world.api.create_model(world.dataset.get('resource'),
                                      args=args)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.model = resource['object']
    world.models.append(resource['resource'])

#@step(r'I create a model with missing splits')
def i_create_a_model_with_missing_splits(step):
    i_create_a_model_with(step, data='{"missing_splits": true}')

#@step(r'I make the model public')
def make_the_model_public(step):
    resource = world.api.update_model(world.model['resource'],
                                      {'private': False, 'white_box': True})
    world.status = resource['code']
    if world.status != HTTP_ACCEPTED:
        print "unexpected status: %s" % world.status
    eq_(world.status, HTTP_ACCEPTED)
    world.location = resource['location']
    world.model = resource['object']

#@step(r'I check the model status using the model\'s public url')
def model_from_public_url(step):
    world.model = world.api.get_model("public/%s" % world.model['resource'])
    eq_(get_status(world.model)['code'], FINISHED)

#@step(r'I make the model shared')
def make_the_model_shared(step):
    resource = world.api.update_model(world.model['resource'],
                                      {'shared': True})
    world.status = resource['code']
    eq_(world.status, HTTP_ACCEPTED)
    world.location = resource['location']
    world.model = resource['object']

#@step(r'I get the model sharing info')
def get_sharing_info(step):
    world.shared_hash = world.model['shared_hash']
    world.sharing_key = world.model['sharing_key']

#@step(r'I check the model status using the model\'s shared url')
def model_from_shared_url(step):
    world.model = world.api.get_model("shared/model/%s" % world.shared_hash)
    eq_(get_status(world.model)['code'], FINISHED)

#@step(r'I check the model status using the model\'s shared key')
def model_from_shared_key(step):
    username = os.environ.get("BIGML_USERNAME")
    world.model = world.api.get_model(world.model['resource'],
        shared_username=username, shared_api_key=world.sharing_key)
    eq_(get_status(world.model)['code'], FINISHED)

#@step(r'"(.*)" field\'s name is changed to "(.*)"')
def field_name_to_new_name(step, field_id, new_name):
    eq_(world.local_model.tree.fields[field_id]['name'], new_name)

#@step(r'I create a model associated to centroid "(.*)"')
def i_create_a_model_from_cluster(step, centroid_id):
    resource = world.api.create_model(
        world.cluster['resource'],
        args={'centroid': centroid_id})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.model = resource['object']
    world.models.append(resource['resource'])

#@step(r'the model is associated to the centroid "(.*)" of the cluster')
def is_associated_to_centroid_id(step, centroid_id):
    cluster = world.api.get_cluster(world.cluster['resource'])
    world.status = cluster['code']
    eq_(world.status, HTTP_OK)
    eq_("model/%s" % (cluster['object']['cluster_models'][centroid_id]),
        world.model['resource'])

#@step(r'I create a logistic regression model$')
def i_create_a_logistic_model(step):
    dataset = world.dataset.get('resource')
    resource = world.api.create_logistic_regression(dataset)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.logistic_regression = resource['object']
    world.logistic_regressions.append(resource['resource'])


#@step(r'I create a logistic regression model with objective "(.*?)" and parms "(.*)"$')
def i_create_a_logistic_model_with_objective_and_parms(step, objective, parms=None):
    dataset = world.dataset.get('resource')
    if parms is None:
        parms = {}
    else:
        parms = json.loads(parms)
    parms.update({"objective_field": objective})
    resource = world.api.create_logistic_regression( \
        dataset, parms)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.logistic_regression = resource['object']
    world.logistic_regressions.append(resource['resource'])

#@step(r'I wait until the logistic regression model status code is either (\d) or (-\d) less than (\d+)')
def wait_until_logistic_model_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    read.i_get_the_logistic_model(step, world.logistic_regression['resource'])
    status = get_status(world.logistic_regression)
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
           time.sleep(3)
           assert_less(datetime.utcnow() - start, timedelta(seconds=int(secs)))
           read.i_get_the_logistic_model(step, world.logistic_regression['resource'])
           status = get_status(world.logistic_regression)
    eq_(status['code'], int(code1))

#@step(r'I wait until the logistic regression model is ready less than (\d+)')
def the_logistic_model_is_finished_in_less_than(step, secs):
    wait_until_logistic_model_status_code_is(step, FINISHED, FAULTY, secs)
