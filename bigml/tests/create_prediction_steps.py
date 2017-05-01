# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015-2017 BigML
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
import time
from nose.tools import assert_almost_equals, eq_
from datetime import datetime, timedelta
from world import world
from bigml.api import HTTP_CREATED
from bigml.api import FINISHED, FAULTY
from bigml.api import get_status

from read_prediction_steps import i_get_the_prediction

def i_create_a_prediction(step, data=None):
    if data is None:
        data = "{}"
    model = world.model['resource']
    data = json.loads(data)
    resource = world.api.create_prediction(model, data)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.prediction = resource['object']
    world.predictions.append(resource['resource'])


def i_create_a_centroid(step, data=None):
    if data is None:
        data = "{}"
    cluster = world.cluster['resource']
    data = json.loads(data)
    resource = world.api.create_centroid(cluster, data)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.centroid = resource['object']
    world.centroids.append(resource['resource'])


def i_create_a_proportional_prediction(step, data=None):
    if data is None:
        data = "{}"
    model = world.model['resource']
    data = json.loads(data)
    resource = world.api.create_prediction(model, data,
                                           args={'missing_strategy': 1})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.prediction = resource['object']
    world.predictions.append(resource['resource'])


def check_prediction(got, expected):
    if not isinstance(got, basestring):
        assert_almost_equals(got, float(expected), 5)
    else:
        eq_(got, expected)

def the_prediction_is(step, objective, prediction):
    check_prediction(world.prediction['prediction'][objective], prediction)

def the_median_prediction_is(step, objective, prediction):
    check_prediction(world.prediction['prediction_path'][
        'objective_summary']['median'], prediction)

def the_centroid_is_with_distance(step, centroid, distance):
    check_prediction(world.centroid['centroid_name'], centroid)
    check_prediction(world.centroid['distance'], distance)

def the_centroid_is(step, centroid):
    check_prediction(world.centroid['centroid_name'], centroid)

def the_centroid_is_ok(step):
    assert world.api.ok(world.centroid)


def the_confidence_is(step, confidence):
    local_confidence = world.prediction.get('confidence', \
        world.prediction.get('probability'))
    assert_almost_equals(float(local_confidence),
                         float(confidence), 4)

def i_create_an_ensemble_prediction(step, data=None):
    if data is None:
        data = "{}"
    ensemble = world.ensemble['resource']
    data = json.loads(data)
    resource = world.api.create_prediction(ensemble, data)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.prediction = resource['object']
    world.predictions.append(resource['resource'])

def i_create_an_ensemble_proportional_prediction(step, data=None):
    if data is None:
        data = "{}"
    ensemble = world.ensemble['resource']
    data = json.loads(data)
    resource = world.api.create_prediction(ensemble,
                                           data,
                                           {"missing_strategy": 1})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.prediction = resource['object']
    world.predictions.append(resource['resource'])


def wait_until_prediction_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    i_get_the_prediction(step, world.prediction['resource'])
    status = get_status(world.prediction)
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
        time.sleep(3)
        assert datetime.utcnow() - start < timedelta(seconds=int(secs))
        i_get_the_prediction(step, world.prediction['resource'])
        status = get_status(world.prediction)
    eq_(status['code'], int(code1))


def the_prediction_is_finished_in_less_than(step, secs):
    wait_until_prediction_status_code_is(step, FINISHED, FAULTY, secs)


def create_local_ensemble_prediction_add_confidence(step, input_data):
    world.local_prediction = world.local_ensemble.predict(
        json.loads(input_data), add_confidence=True)

def create_local_ensemble_prediction(step, input_data):
    world.local_prediction = world.local_ensemble.predict(json.loads(input_data))

def create_local_ensemble_prediction_with_confidence(step, input_data):
    world.local_prediction = world.local_ensemble.predict( \
        json.loads(input_data), with_confidence=True)

    world.local_probabilities = world.local_ensemble.predict_probability( \
        json.loads(input_data), compact=True)

def create_local_ensemble_proportional_prediction_with_confidence( \
    step, input_data):
    world.local_prediction = world.local_ensemble.predict( \
        json.loads(input_data), with_confidence=True, missing_strategy=1)

def create_local_ensemble_prediction_using_median_with_confidence( \
    step, input_data):
    world.local_prediction = world.local_ensemble.predict( \
        json.loads(input_data), with_confidence=True, median=True)


def i_create_an_anomaly_score(step, data=None):
    if data is None:
        data = "{}"
    anomaly = world.anomaly['resource']
    data = json.loads(data)
    resource = world.api.create_anomaly_score(anomaly, data)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.anomaly_score = resource['object']
    world.anomaly_scores.append(resource['resource'])


def i_create_an_association_set(step, data=None):
    if data is None:
        data = "{}"
    association = world.association['resource']
    data = json.loads(data)
    resource = world.api.create_association_set(association, data)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.association_set = resource['object']
    world.association_sets.append(resource['resource'])

def the_anomaly_score_is(step, score):
    check_prediction(world.anomaly_score['score'], score)


def the_logistic_prediction_is(step, prediction):
    check_prediction(world.prediction['output'], prediction)


def i_create_a_logistic_prediction(step, data=None):
    if data is None:
        data = "{}"
    model = world.logistic_regression['resource']
    data = json.loads(data)
    resource = world.api.create_prediction(model, data)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.prediction = resource['object']
    world.predictions.append(resource['resource'])

def the_logistic_probability_is(step, probability):
    for [prediction, remote_probability] in world.prediction['probabilities']:
        if prediction == world.prediction['output']:
            break
    assert_almost_equals(round(float(remote_probability), 4),
                         round(float(probability), 4))
