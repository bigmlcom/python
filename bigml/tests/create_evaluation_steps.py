# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument,no-member
#
# Copyright 2012, 2015-2025 BigML
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

from bigml.api import HTTP_CREATED
from bigml.api import FINISHED, FAULTY
from bigml.evaluation import Evaluation

from .read_resource_steps import wait_until_status_code_is
from .world import world, eq_, ok_, res_filename, approx_

def i_create_an_evaluation(step, shared=None):
    """Step: I create an evaluation for the model with the dataset"""
    dataset = world.dataset.get('resource')
    model = world.model.get('resource')
    resource = world.api.create_evaluation(model, dataset)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.evaluation = resource['object']
    world.evaluations.append(resource['resource'])


def i_create_an_evaluation_ensemble(step, params=None):
    """Step: I create an evaluation for the ensemble with the dataset"""
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


def i_create_an_evaluation_logistic(step):
    """Step: I create an evaluation for the logistic regression with
    the dataset
    """
    dataset = world.dataset.get('resource')
    logistic = world.logistic_regression.get('resource')
    resource = world.api.create_evaluation(logistic, dataset)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.evaluation = resource['object']
    world.evaluations.append(resource['resource'])


def i_create_an_evaluation_deepnet(step):
    """Step: I create an evaluation for the deepnet with the dataset"""
    dataset = world.dataset.get('resource')
    deepnet = world.deepnet.get('resource')
    resource = world.api.create_evaluation(deepnet, dataset)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.evaluation = resource['object']
    world.evaluations.append(resource['resource'])


def i_create_an_evaluation_fusion(step):
    """Step: I create an evaluation for the fusion with the dataset"""
    dataset = world.dataset.get('resource')
    fusion = world.fusion.get('resource')
    resource = world.api.create_evaluation(fusion, dataset)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.evaluation = resource['object']
    world.evaluations.append(resource['resource'])


def wait_until_evaluation_status_code_is(step, code1, code2, secs):
    """Step: I wait until the evaluation status code is either <code1> or
    <code2> less than <secs>"""
    world.evaluation = wait_until_status_code_is(
        code1, code2, secs, world.evaluation)


def the_evaluation_is_finished_in_less_than(step, secs):
    """Step: I wait until the evaluation is ready less than <secs>"""
    wait_until_evaluation_status_code_is(step, FINISHED, FAULTY, secs)


def the_measured_measure_is_value(step, measure, value):
    """Step: the measured <measure> is <value>"""
    ev_ = world.evaluation['result']['model'][measure] + 0.0
    eq_(ev_, float(value), "The %s is: %s and %s is expected" % (
        measure, ev_, float(value)))


def the_measured_measure_is_greater_value(step, measure, value):
    """Step: the measured <measure> is greater than <value>"""
    ok_(float(world.evaluation['result']['model'][measure]) > float(value))

def i_create_a_local_evaluation(step, filename):
    """Step: I create an Evaluation from the JSON file"""
    filename = res_filename(filename)
    with open(filename) as handler:
        evaluation = json.load(handler)
    local_evaluation = Evaluation(evaluation)
    step.bigml["local_evaluation"] = local_evaluation

def the_local_metric_is_value(step, metric, value):
    """Step: The metric in the local evaluation is <value> """
    approx_(getattr(step.bigml["local_evaluation"], metric), value,
            precision=4)
