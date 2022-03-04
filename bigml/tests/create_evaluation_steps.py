# -*- coding: utf-8 -*-
#
# Copyright 2012, 2015-2022 BigML
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
from datetime import datetime
from .world import world
from nose.tools import eq_, assert_less, assert_greater

from bigml.api import HTTP_CREATED
from bigml.api import FINISHED
from bigml.api import FAULTY
from bigml.api import get_status

from .read_resource_steps import wait_until_status_code_is

#@step(r'I create an evaluation for the model with the dataset$')
def i_create_an_evaluation(step, shared=None):
    dataset = world.dataset.get('resource')
    model = world.model.get('resource')
    resource = world.api.create_evaluation(model, dataset)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.evaluation = resource['object']
    world.evaluations.append(resource['resource'])


#@step(r'I create an evaluation for the ensemble with the dataset$')
def i_create_an_evaluation_ensemble(step, params=None):
    if params is None:
        params = {}
    dataset = world.dataset.get('resource')
    ensemble = world.ensemble.get('resource')
    resource = world.api.create_evaluation(ensemble, dataset, params)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.evaluation = resource['object']
    world.evaluations.append(resource['resource'])

#@step(r'I create an evaluation for the logistic regression with the dataset$')
def i_create_an_evaluation_logistic(step):
    dataset = world.dataset.get('resource')
    logistic = world.logistic_regression.get('resource')
    resource = world.api.create_evaluation(logistic, dataset)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.evaluation = resource['object']
    world.evaluations.append(resource['resource'])

#@step(r'I create an evaluation for the deepnet with the dataset$')
def i_create_an_evaluation_deepnet(step):
    dataset = world.dataset.get('resource')
    deepnet = world.deepnet.get('resource')
    resource = world.api.create_evaluation(deepnet, dataset)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.evaluation = resource['object']
    world.evaluations.append(resource['resource'])


#@step(r'I create an evaluation for the fusion with the dataset$')
def i_create_an_evaluation_fusion(step):
    dataset = world.dataset.get('resource')
    fusion = world.fusion.get('resource')
    resource = world.api.create_evaluation(fusion, dataset)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.evaluation = resource['object']
    world.evaluations.append(resource['resource'])

#@step(r'I wait until the evaluation status code is either (\d) or (-\d) less than (\d+)')
def wait_until_evaluation_status_code_is(step, code1, code2, secs):
    world.evaluation = wait_until_status_code_is(
        code1, code2, secs, world.evaluation)

#@step(r'I wait until the evaluation is ready less than (\d+)')
def the_evaluation_is_finished_in_less_than(step, secs):
    wait_until_evaluation_status_code_is(step, FINISHED, FAULTY, secs)

#@step(r'the measured "(.*)" is (\d+\.*\d*)')
def the_measured_measure_is_value(step, measure, value):
    ev = world.evaluation['result']['model'][measure] + 0.0
    eq_(ev, float(value), "The %s is: %s and %s is expected" % (
        measure, ev, float(value)))

#@step(r'the measured "(.*)" is greater than (\d+\.*\d*)')
def the_measured_measure_is_greater_value(step, measure, value):
    assert_greater(world.evaluation['result']['model'][measure] + 0.0,
                   float(value))
