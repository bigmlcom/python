# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2012-2015 BigML
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

from bigml.api import HTTP_CREATED
from bigml.api import HTTP_ACCEPTED
from bigml.api import FINISHED
from bigml.api import FAULTY
from bigml.api import get_status
from bigml.ensemble import Ensemble
from bigml.model import Model

from read_ensemble_steps import i_get_the_ensemble

NO_MISSING_SPLITS = {'missing_splits': False}

#@step(r'I create an ensemble of (\d+) models and (\d+) tlp$')
def i_create_an_ensemble(step, number_of_models, tlp):
    dataset = world.dataset.get('resource')
    try:
        number_of_models = int(number_of_models)
        tlp = int(tlp)
        args = {'number_of_models': number_of_models,
                'tlp': tlp, 'sample_rate': 0.70, 'seed': 'BigML'}
    except:
        args = {}
    args.update(NO_MISSING_SPLITS)
    resource = world.api.create_ensemble(dataset, args=args)
    world.status = resource['code']
    assert world.status == HTTP_CREATED
    world.location = resource['location']
    world.ensemble = resource['object']
    world.ensemble_id = resource['resource']
    world.ensembles.append(resource['resource'])

#@step(r'I wait until the ensemble status code is either (\d) or (-\d) less than (\d+)')
def wait_until_ensemble_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    i_get_the_ensemble(step, world.ensemble['resource'])
    status = get_status(world.ensemble)
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
        time.sleep(3)
        assert datetime.utcnow() - start < timedelta(seconds=int(secs))
        i_get_the_ensemble(step, world.ensemble['resource'])
        status = get_status(world.ensemble)
    assert status['code'] == int(code1)

#@step(r'I wait until the ensemble is ready less than (\d+)')
def the_ensemble_is_finished_in_less_than(step, secs):
    wait_until_ensemble_status_code_is(step, FINISHED, FAULTY, secs)


#@step(r'I create a local Ensemble$')
def create_local_ensemble(step):
    world.local_ensemble = Ensemble(world.ensemble_id, world.api)
    world.local_model = Model(world.local_ensemble.model_ids[0])

#@step(r'I create a local Ensemble with the last (\d+) models$')
def create_local_ensemble_with_list(step, number_of_models):
    world.local_ensemble = Ensemble(world.models[-int(number_of_models):], world.api)

#@step(r'I create a local Ensemble with the last (\d+) local models$')
def create_local_ensemble_with_list_of_local_models(step, number_of_models):
    local_models = [Model(model) for model in world.models[-int(number_of_models):]]
    world.local_ensemble = Ensemble(local_models, world.api)

#@step(r'the field importance text is (.*?)$')
def field_importance_print(step, field_importance):
    field_importance_data = world.local_ensemble.field_importance_data()[0]
    if field_importance_data == json.loads(field_importance):
        assert True
    else:
        assert False, "Found %s, expected %s" % (field_importance_data, field_importance)
