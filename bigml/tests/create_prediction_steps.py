# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument,no-member
#
# Copyright 2015-2022 BigML
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

from .read_resource_steps import wait_until_status_code_is
from .world import world, res_filename, eq_, ok_, approx_


def i_create_a_prediction(step, data=None):
    """Creating prediction"""
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
    """Creating prediction with operating point"""
    if data is None:
        data = "{}"
    ok_(operating_point is not None)
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
    """Creating prediction from ensemble with operating point"""
    if data is None:
        data = "{}"
    ok_(operating_point is not None)
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
    """Create prediction from fusion with operating point"""
    if data is None:
        data = "{}"
    ok_(operating_point is not None)
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
    """Create centroid"""
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
    """Create prediction using proportional strategy for missings"""
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


def check_prediction(got, expected, precision=4):
    """Checking prediction is as expected"""
    if not isinstance(got, str):
        approx_(got, float(expected), precision=precision)
    else:
        eq_(got, expected)


def the_prediction_is(step, objective, prediction, precision=4):
    """Checking the prediction for objective field"""
    check_prediction(world.prediction['prediction'][objective], prediction,
                     precision=precision)


def the_median_prediction_is(step, objective, prediction, precision=4):
    """Checking the prediction using median"""
    check_prediction(world.prediction['prediction_path'][
        'objective_summary']['median'], prediction, precision=precision)


def the_centroid_is_with_distance(step, centroid, distance):
    """Checking expected centroid and distance"""
    check_prediction(world.centroid['centroid_name'], centroid)
    check_prediction(world.centroid['distance'], distance)


def the_centroid_is(step, centroid):
    """Checking centroid"""
    check_prediction(world.centroid['centroid_name'], centroid)


def the_centroid_is_ok(step):
    """Checking centroid is ready"""
    ok_(world.api.ok(world.centroid))


def the_confidence_is(step, confidence):
    """Checking confidence"""
    local_confidence = world.prediction.get('confidence', \
        world.prediction.get('probability'))
    approx_(float(local_confidence), float(confidence), precision=4)


def i_create_an_ensemble_prediction(step, data=None):
    """Creating prediction from ensemble"""
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
    """Creating prediction from ensemble using proportional strategy for
    missings
    """
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
    """Waiting for prediction and storing result"""
    world.prediction = wait_until_status_code_is(
        code1, code2, secs, world.prediction)


def the_prediction_is_finished_in_less_than(step, secs):
    """Checking wait time"""
    wait_until_prediction_status_code_is(step, FINISHED, FAULTY, secs)


def create_local_ensemble_prediction_add_confidence(step, input_data):
    """Creating prediction from local ensemble with confidence"""
    step.bigml["local_prediction"] = step.bigml["local_ensemble"].predict(
        json.loads(input_data), full=True)


def create_local_ensemble_prediction(step, input_data):
    """Creating prediction from local ensemble"""
    step.bigml["local_prediction"] = step.bigml["local_ensemble"].predict(json.loads(input_data))


def create_local_ensemble_prediction_probabilities(step, input_data):
    """Creating prediction from local ensemble with probabilities"""
    step.bigml["local_prediction"] = step.bigml["local_ensemble"].predict( \
        json.loads(input_data), full=True)
    step.bigml["local_probabilities"] = step.bigml[
        "local_ensemble"].predict_probability( \
        json.loads(input_data), compact=True)


def create_local_ensemble_proportional_prediction_with_confidence( \
    step, input_data, params=None):
    """Creating prediction from local ensemble with confidence"""
    if params is None:
        params = {}
    kwargs = {"full": True, "missing_strategy": 1}
    kwargs.update(params)
    step.bigml["local_prediction"] = step.bigml["local_ensemble"].predict( \
        json.loads(input_data), **kwargs)

def create_local_ensemble_prediction_using_median_with_confidence( \
    step, input_data):
    """Creating prediction from local ensemble using median with confidence"""
    step.bigml["local_prediction"] = step.bigml["local_ensemble"].predict( \
        json.loads(input_data), full=True)


def i_create_an_anomaly_score(step, data=None):
    """Creating anomaly score"""
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
    """Creating association set"""
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
    """Checking the expected anomaly score"""
    check_prediction(world.anomaly_score['score'], score)


def the_logistic_prediction_is(step, prediction):
    """Checking the expected logistic regression prediction"""
    check_prediction(world.prediction['output'], prediction)


def the_fusion_prediction_is(step, prediction):
    """Checking the expected fusion prediction """
    the_logistic_prediction_is(step, prediction)


def i_create_a_logistic_prediction(step, data=None):
    """Checking the expected logistic regression prediction"""
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


def i_create_a_deepnet_prediction(step, data=None, image_fields=None):
    """Creating a prediction from a deepnet"""
    if data is None:
        data = "{}"
    if image_fields is None:
        image_fields = []
    deepnet = world.deepnet['resource']
    data = json.loads(data)
    data_image_fields = []
    for field in image_fields:
        if field in data:
            data[field] = res_filename(data[field])
            data_image_fields.append(field)
    resource = world.api.create_prediction(deepnet, data)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.prediction = resource['object']
    for field in data_image_fields:
        world.sources.append(world.prediction["input_data"][field])
    world.predictions.append(resource['resource'])


def i_create_a_deepnet_prediction_with_op(step, data=None,
                                          operating_point=None):
    """Creating a prediction from a deepnet with operating point"""
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


def i_create_a_logistic_prediction_with_op(step, data=None,
                                           operating_point=None):
    """Creating a prediction from a logistic regression with operating point"""
    if data is None:
        data = "{}"
    logistic_regression = world.logistic_regression['resource']
    data = json.loads(data)
    resource = world.api.create_prediction( \
        logistic_regression, data, {"operating_point": operating_point})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.prediction = resource['object']
    world.predictions.append(resource['resource'])


#pylint: disable=locally-disabled,undefined-loop-variable
def the_logistic_probability_is(step, probability):
    """Checking the logistic regression prediction probability"""
    for [prediction, remote_probability] in world.prediction['probabilities']:
        if prediction == world.prediction['output']:
            break
    approx_(float(remote_probability), float(probability), precision=4)


def the_fusion_probability_is(step, probability):
    """Checking the fusion prediction probability"""
    the_logistic_probability_is(step, probability)


def i_create_a_prediction_op_kind(step, data=None, operating_kind=None):
    """Creating a prediction with operating kind"""
    if data is None:
        data = "{}"
    ok_(operating_kind is not None)
    model = world.model['resource']
    data = json.loads(data)
    resource = world.api.create_prediction( \
        model, data, {"operating_kind": operating_kind})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.prediction = resource['object']
    world.predictions.append(resource['resource'])


def i_create_an_ensemble_prediction_op_kind(
    step, data=None, operating_kind=None):
    """Creating a prediction from an ensemble with operating kind"""
    if data is None:
        data = "{}"
    ok_(operating_kind is not None)
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
    """Creating a prediction from a deepnet with operating kind"""
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
    """Creating a prediction from a logistic regression with operating kind"""
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
    """Creating a prediction from a fusion"""
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
    """Creating a prediction from a linear regression"""
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
