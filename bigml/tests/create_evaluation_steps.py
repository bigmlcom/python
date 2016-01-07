# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2012, 2015-2016 BigML
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
from datetime import datetime, timedelta
from world import world

from bigml.api import HTTP_CREATED
from bigml.api import FINISHED
from bigml.api import FAULTY
from bigml.api import get_status

from read_evaluation_steps import i_get_the_evaluation

#@step(r'I create an evaluation for the model with the dataset$')
def i_create_an_evaluation(step):
    dataset = world.dataset.get('resource')
    model = world.model.get('resource')
    resource = world.api.create_evaluation(model, dataset)
    world.status = resource['code']
    assert world.status == HTTP_CREATED
    world.location = resource['location']
    world.evaluation = resource['object']
    world.evaluations.append(resource['resource'])


#@step(r'I create an evaluation for the ensemble with the dataset$')
def i_create_an_evaluation_ensemble(step):
    dataset = world.dataset.get('resource')
    ensemble = world.ensemble.get('resource')
    resource = world.api.create_evaluation(ensemble, dataset)
    world.status = resource['code']
    assert world.status == HTTP_CREATED
    world.location = resource['location']
    world.evaluation = resource['object']
    world.evaluations.append(resource['resource'])

#@step(r'I wait until the evaluation status code is either (\d) or (-\d) less than (\d+)')
def wait_until_evaluation_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    i_get_the_evaluation(step, world.evaluation['resource'])
    status = get_status(world.evaluation)
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
        time.sleep(3)
        assert datetime.utcnow() - start < timedelta(seconds=int(secs))
        i_get_the_evaluation(step, world.evaluation['resource'])
        status = get_status(world.evaluation)
    assert status['code'] == int(code1)

#@step(r'I wait until the evaluation is ready less than (\d+)')
def the_evaluation_is_finished_in_less_than(step, secs):
    wait_until_evaluation_status_code_is(step, FINISHED, FAULTY, secs)

#@step(r'the measured "(.*)" is (\d+\.*\d*)')
def the_measured_measure_is_value(step, measure, value):
    ev = world.evaluation['result']['model'][measure] + 0.0
    assert  ev == float(value), "The %s is: %s and %s is expected" % (
        measure, ev, float(value))

#@step(r'the measured "(.*)" is greater than (\d+\.*\d*)')
def the_measured_measure_is_greater_value(step, measure, value):
    assert world.evaluation['result']['model'][measure] + 0.0 > float(value)
