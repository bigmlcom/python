# -*- coding: utf-8 -*-

#
# Copyright 2015-2020 BigML
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
from nose.tools import assert_almost_equals, eq_, assert_is_not_none, \
    assert_less
from datetime import datetime
from .world import world, logged_wait
from bigml.api import HTTP_CREATED
from bigml.api import FINISHED, FAULTY
from bigml.api import get_status

from .read_prediction_steps import i_get_the_prediction

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


def i_create_a_prediction_op(step, data=None, operating_point=None):
    if data is None:
        data = "{}"
    assert_is_not_none(operating_point)
    model = world.model['resource']
    data = json.loads(data)
    resource = world.api.create_prediction( \
        model, data, {"operating_point": operating_point})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.prediction = resource['object']
    world.predictions.append(resource['resource'])


def i_create_an_ensemble_prediction_op(step, data=None, operating_point=None):
    if data is None:
        data = "{}"
    assert_is_not_none(operating_point)
    ensemble = world.ensemble['resource']
    data = json.loads(data)
    resource = world.api.create_prediction( \
        ensemble, data, {"operating_point": operating_point})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.prediction = resource['object']
    world.predictions.append(resource['resource'])


def i_create_a_fusion_prediction_op(step, data=None, operating_point=None):
    if data is None:
        data = "{}"
    assert_is_not_none(operating_point)
    fusion = world.fusion['resource']
    data = json.loads(data)
    resource = world.api.create_prediction( \
        fusion, data, {"operating_point": operating_point})
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
    if not isinstance(got, str):
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

def i_create_an_ensemble_proportional_prediction(step, data=None, params=None):
    if data is None:
        data = "{}"
    if params is None:
        params = {}
    ensemble = world.ensemble['resource']
    data = json.loads(data)
    args = {"missing_strategy": 1}
    args.update(params)
    resource = world.api.create_prediction(ensemble, data, args)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.prediction = resource['object']
    world.predictions.append(resource['resource'])


def wait_until_prediction_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    delta = int(secs) * world.delta
    i_get_the_prediction(step, world.prediction['resource'])
    status = get_status(world.prediction)
    count = 0
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
        count += 1
        logged_wait(start, delta, count, "prediction")
        assert_less((datetime.utcnow() - start).seconds, delta)
        i_get_the_prediction(step, world.prediction['resource'])
        status = get_status(world.prediction)
    eq_(status['code'], int(code1))


def the_prediction_is_finished_in_less_than(step, secs):
    wait_until_prediction_status_code_is(step, FINISHED, FAULTY, secs)


def create_local_ensemble_prediction_add_confidence(step, input_data):
    world.local_prediction = world.local_ensemble.predict(
        json.loads(input_data), full=True)

def create_local_ensemble_prediction(step, input_data):
    world.local_prediction = world.local_ensemble.predict(json.loads(input_data))

def create_local_ensemble_prediction_with_confidence(step, input_data):
    world.local_prediction = world.local_ensemble.predict( \
        json.loads(input_data), full=True)
    world.local_probabilities = world.local_ensemble.predict_probability( \
        json.loads(input_data), compact=True)

def create_local_ensemble_proportional_prediction_with_confidence( \
    step, input_data, params=None):
    if params is None:
        params = {}
    kwargs = {"full": True, "missing_strategy": 1}
    kwargs.update(params)
    world.local_prediction = world.local_ensemble.predict( \
        json.loads(input_data), **kwargs)

def create_local_ensemble_prediction_using_median_with_confidence( \
    step, input_data):
    world.local_prediction = world.local_ensemble.predict( \
        json.loads(input_data), full=True)


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


def the_fusion_prediction_is(step, prediction):
    the_logistic_prediction_is(step, prediction)


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

def i_create_a_deepnet_prediction(step, data=None):
    if data is None:
        data = "{}"
    deepnet = world.deepnet['resource']
    data = json.loads(data)
    resource = world.api.create_prediction(deepnet, data)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.prediction = resource['object']
    world.predictions.append(resource['resource'])

def i_create_a_deepnet_prediction_with_op(step, data=None,
                                          operating_point=None):
    if data is None:
        data = "{}"
    deepnet = world.deepnet['resource']
    data = json.loads(data)
    resource = world.api.create_prediction( \
        deepnet, data, {"operating_point": operating_point})
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


def the_fusion_probability_is(step, probability):
    the_logistic_probability_is(step, probability)


def i_create_a_prediction_op_kind(step, data=None, operating_kind=None):
    if data is None:
        data = "{}"
    assert_is_not_none(operating_kind)
    model = world.model['resource']
    data = json.loads(data)
    resource = world.api.create_prediction( \
        model, data, {"operating_kind": operating_kind})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.prediction = resource['object']
    world.predictions.append(resource['resource'])


def i_create_an_ensemble_prediction_op_kind(step, data=None, operating_kind=None):
    if data is None:
        data = "{}"
    assert_is_not_none(operating_kind)
    ensemble = world.ensemble['resource']
    data = json.loads(data)
    resource = world.api.create_prediction( \
        ensemble, data, {"operating_kind": operating_kind})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.prediction = resource['object']
    world.predictions.append(resource['resource'])

def i_create_a_deepnet_prediction_op_kind(step, data=None,
                                          operating_kind=None):
    if data is None:
        data = "{}"
    deepnet = world.deepnet['resource']
    data = json.loads(data)
    resource = world.api.create_prediction( \
        deepnet, data, {"operating_kind": operating_kind})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.prediction = resource['object']
    world.predictions.append(resource['resource'])

def i_create_a_logistic_prediction_with_op_kind(step, data=None,
                                                operating_kind=None):
    if data is None:
        data = "{}"
    logistic_regression = world.logistic_regression['resource']
    data = json.loads(data)
    resource = world.api.create_prediction( \
        logistic_regression, data, {"operating_kind": operating_kind})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.prediction = resource['object']
    world.predictions.append(resource['resource'])

def i_create_a_fusion_prediction(step, data=None):
    if data is None:
        data = "{}"
    fusion = world.fusion['resource']
    data = json.loads(data)
    resource = world.api.create_prediction(fusion, data)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.prediction = resource['object']
    world.predictions.append(resource['resource'])

def i_create_a_linear_prediction(step, data=None):
    if data is None:
        data = "{}"
    linear_regression = world.linear_regression['resource']
    data = json.loads(data)
    resource = world.api.create_prediction(linear_regression, data)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.prediction = resource['object']
    world.predictions.append(resource['resource'])
