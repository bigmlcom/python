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
from datetime import datetime, timedelta
from world import world
from nose.tools import eq_, assert_less

from bigml.api import HTTP_CREATED
from bigml.api import HTTP_ACCEPTED
from bigml.api import FINISHED
from bigml.api import FAULTY
from bigml.api import get_status
from bigml.ensemble import Ensemble
from bigml.model import Model

from read_ensemble_steps import i_get_the_ensemble

NO_MISSING_SPLITS = {'missing_splits': False}
ENSEMBLE_SAMPLE = {'ensemble_sample': {"rate": 0.70, "seed": 'BigML'}}

#@step(r'I create an ensemble of (\d+) models and (\d+) tlp$')
def i_create_an_ensemble(step, number_of_models='10', tlp='1'):
    dataset = world.dataset.get('resource')
    try:
        number_of_models = int(number_of_models)
        tlp = int(tlp)
        args = {'number_of_models': number_of_models,
                'tlp': tlp}
    except:
        args = {}
    args.update(NO_MISSING_SPLITS)
    args.update(ENSEMBLE_SAMPLE)
    resource = world.api.create_ensemble(dataset, args=args)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.ensemble = resource['object']
    world.ensemble_id = resource['resource']
    world.ensembles.append(resource['resource'])

#@step(r'I wait until the ensemble status code is either (\d) or (-\d)
# less than (\d+)')
def wait_until_ensemble_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    i_get_the_ensemble(step, world.ensemble['resource'])
    status = get_status(world.ensemble)
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
        time.sleep(3)
        assert_less(datetime.utcnow() - start, timedelta(seconds=int(secs)))
        i_get_the_ensemble(step, world.ensemble['resource'])
        status = get_status(world.ensemble)
    eq_(status['code'], int(code1))

#@step(r'I wait until the ensemble is ready less than (\d+)')
def the_ensemble_is_finished_in_less_than(step, secs):
    wait_until_ensemble_status_code_is(step, FINISHED, FAULTY, secs)


#@step(r'I create a local Ensemble$')
def create_local_ensemble(step):
    world.local_ensemble = Ensemble(world.ensemble_id, world.api)
    world.local_model = Model(world.local_ensemble.model_ids[0], world.api)

#@step(r'I create a local Ensemble with the last (\d+) models$')
def create_local_ensemble_with_list(step, number_of_models):
    world.local_ensemble = Ensemble(world.models[-int(number_of_models):],
                                    world.api)

#@step(r'I create a local Ensemble with the last (\d+) local models$')
def create_local_ensemble_with_list_of_local_models(step, number_of_models):
    local_models = [Model(model) for model in
                    world.models[-int(number_of_models):]]
    world.local_ensemble = Ensemble(local_models, world.api)

#@step(r'the field importance text is (.*?)$')
def field_importance_print(step, field_importance):
    field_importance_data = world.local_ensemble.field_importance_data()[0]
    eq_(field_importance_data, json.loads(field_importance))

#@step(r'I create an ensemble with "(.*)"$')
def i_create_an_ensemble_with_params(step, params):
    dataset = world.dataset.get('resource')
    try:
        args = json.loads(params)
    except:
        args = {}
    args.update(ENSEMBLE_SAMPLE)
    resource = world.api.create_ensemble(dataset, args=args)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.ensemble = resource['object']
    world.ensemble_id = resource['resource']
    world.ensembles.append(resource['resource'])

#@step(r'I make the ensemble shared')
def make_the_ensemble_shared(step):
    resource = world.api.update_ensemble(world.ensemble['resource'],
                                         {'shared': True})
    world.status = resource['code']
    eq_(world.status, HTTP_ACCEPTED)
    world.location = resource['location']
    world.ensemble = resource['object']

#@step(r'I get the ensemble sharing info')
def get_sharing_info(step):
    world.shared_hash = world.ensemble['shared_hash']
    world.sharing_key = world.ensemble['sharing_key']

#@step(r'I check the ensemble status using the ensemble\'s shared url')
def ensemble_from_shared_url(step):
    world.ensemble = world.api.get_ensemble("shared/ensemble/%s" % world.shared_hash)
    eq_(get_status(world.ensemble)['code'], FINISHED)

#@step(r'I check the ensemble status using the ensemble\'s shared key')
def ensemble_from_shared_key(step):
    username = os.environ.get("BIGML_USERNAME")
    world.ensemble = world.api.get_ensemble(world.ensemble['resource'],
        shared_username=username, shared_api_key=world.sharing_key)
    eq_(get_status(world.ensemble)['code'], FINISHED)
