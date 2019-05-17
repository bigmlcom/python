# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2012-2019 BigML
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
import requests
import csv
import traceback
from datetime import datetime, timedelta
from world import world, res_filename
from nose.tools import eq_, ok_, assert_less

from bigml.api import HTTP_CREATED
from bigml.api import FINISHED
from bigml.api import FAULTY
from bigml.api import get_status
from bigml.io import UnicodeReader

from read_batch_prediction_steps import (i_get_the_batch_prediction,
    i_get_the_batch_centroid, i_get_the_batch_anomaly_score)


#@step(r'I create a batch prediction for the dataset with the model$')
def i_create_a_batch_prediction(step):
    dataset = world.dataset.get('resource')
    model = world.model.get('resource')
    resource = world.api.create_batch_prediction(model, dataset)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.batch_prediction = resource['object']
    world.batch_predictions.append(resource['resource'])


#@step(r'I create a batch prediction for the dataset with the ensemble and "(.*)"$')
def i_create_a_batch_prediction_ensemble(step, params=None):
    if params is None:
        params = {}
    dataset = world.dataset.get('resource')
    ensemble = world.ensemble.get('resource')
    resource = world.api.create_batch_prediction(ensemble, dataset, params)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.batch_prediction = resource['object']
    world.batch_predictions.append(resource['resource'])


#@step(r'I wait until the batch prediction status code is either (\d) or (-\d) less than (\d+)')
def wait_until_batch_prediction_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    delta = int(secs) * world.delta
    i_get_the_batch_prediction(step, world.batch_prediction['resource'])
    status = get_status(world.batch_prediction)
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
        time.sleep(3)
        assert_less((datetime.utcnow() - start).seconds, delta)
        i_get_the_batch_prediction(step, world.batch_prediction['resource'])
        status = get_status(world.batch_prediction)
    eq_(status['code'], int(code1))


#@step(r'I wait until the batch centroid status code is either (\d) or (-\d) less than (\d+)')
def wait_until_batch_centroid_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    delta = int(secs) * world.delta
    i_get_the_batch_centroid(step, world.batch_centroid['resource'])
    status = get_status(world.batch_centroid)
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
        time.sleep(3)
        assert_less(datetime.utcnow() - start, timedelta(seconds=delta))
        i_get_the_batch_centroid(step, world.batch_centroid['resource'])
        status = get_status(world.batch_centroid)
    eq_(status['code'], int(code1))


#@step(r'I wait until the batch anomaly score status code is either (\d) or (-\d) less than (\d+)')
def wait_until_batch_anomaly_score_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    delta = int(secs) * world.delta
    i_get_the_batch_anomaly_score(step, world.batch_anomaly_score['resource'])
    status = get_status(world.batch_anomaly_score)
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
        time.sleep(3)
        assert_less(datetime.utcnow() - start, timedelta(seconds=delta))
        i_get_the_batch_anomaly_score(step, world.batch_anomaly_score['resource'])
        status = get_status(world.batch_anomaly_score)
    eq_(status['code'], int(code1), msg="%s seconds waited." % delta)


#@step(r'I wait until the batch prediction is ready less than (\d+)')
def the_batch_prediction_is_finished_in_less_than(step, secs):
    wait_until_batch_prediction_status_code_is(step, FINISHED, FAULTY, secs)

#@step(r'I wait until the batch centroid is ready less than (\d+)')
def the_batch_centroid_is_finished_in_less_than(step, secs):
    wait_until_batch_centroid_status_code_is(step, FINISHED, FAULTY, secs)

#@step(r'I wait until the batch anomaly score is ready less than (\d+)')
def the_batch_anomaly_score_is_finished_in_less_than(step, secs):
    wait_until_batch_anomaly_score_status_code_is(step, FINISHED, FAULTY, secs)


#@step(r'I download the created predictions file to "(.*)"')
def i_download_predictions_file(step, filename):
    file_object = world.api.download_batch_prediction(
        world.batch_prediction, filename=res_filename(filename))
    ok_(file_object is not None)
    world.output = file_object

#@step(r'I download the created centroid file to "(.*)"')
def i_download_centroid_file(step, filename):
    file_object = world.api.download_batch_centroid(
        world.batch_centroid, filename=res_filename(filename))
    ok_(file_object is not None)
    world.output = file_object

#@step(r'I download the created anomaly score file to "(.*)"')
def i_download_anomaly_score_file(step, filename):
    file_object = world.api.download_batch_anomaly_score(
        world.batch_anomaly_score, filename=res_filename(filename))
    ok_(file_object is not None)
    world.output = file_object

def check_rows(prediction_rows, test_rows):
    row_num = 0
    for row in prediction_rows:
        check_row = next(test_rows)
        row_num += 1
        eq_(len(check_row), len (row))
        for index in range(len(row)):
            dot = row[index].find(".")
            if dot > 0:
                try:
                    decs = min(len(row[index]), len(check_row[index])) - dot - 1
                    row[index] = round(float(row[index]), decs)
                    check_row[index] = round(float(check_row[index]), decs)
                except ValueError:
                    pass
            eq_(check_row[index], row[index],
                "Got: %s/ Expected: %s in line %s" % (row, check_row, row_num))

#@step(r'the batch prediction file is like "(.*)"')
def i_check_predictions(step, check_file):
    with UnicodeReader(world.output) as prediction_rows:
        with UnicodeReader(res_filename(check_file)) as test_rows:
            check_rows(prediction_rows, test_rows)

#@step(r'the batch centroid file is like "(.*)"')
def i_check_batch_centroid(step, check_file):
    i_check_predictions(step, check_file)

#@step(r'the batch anomaly score file is like "(.*)"')
def i_check_batch_anomaly_score(step, check_file):
    i_check_predictions(step, check_file)

#@step(r'I check the batch centroid is ok')
def i_check_batch_centroid_is_ok(step):
    ok_(world.api.ok(world.batch_centroid))

#@step(r'I check the batch anomaly score is ok')
def i_check_batch_anomaly_score_is_ok(step):
    ok_(world.api.ok(world.batch_anomaly_score))


#@step(r'I create a batch centroid for the dataset$')
def i_create_a_batch_prediction_with_cluster(step):
    dataset = world.dataset.get('resource')
    cluster = world.cluster.get('resource')
    resource = world.api.create_batch_centroid(cluster, dataset)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.batch_centroid = resource['object']
    world.batch_centroids.append(resource['resource'])

#@step(r'I create a batch anomaly score$')
def i_create_a_batch_prediction_with_anomaly(step):
    dataset = world.dataset.get('resource')
    anomaly = world.anomaly.get('resource')
    resource = world.api.create_batch_anomaly_score(anomaly, dataset)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.batch_anomaly_score = resource['object']
    world.batch_anomaly_scores.append(resource['resource'])


#@step(r'I create a linear batch prediction$')
def i_create_a_linear_batch_prediction(step):
    dataset = world.dataset.get('resource')
    linear_regression = world.linear_regression.get('resource')
    resource = world.api.create_batch_prediction(linear_regression, dataset)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.batch_prediction = resource['object']
    world.batch_predictions.append(resource['resource'])


#@step(r'I create a source from the batch prediction$')
def i_create_a_source_from_batch_prediction(step):
    batch_prediction = world.batch_prediction.get('resource')
    resource = world.api.source_from_batch_prediction(batch_prediction)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.source = resource['object']
    world.sources.append(resource['resource'])


#@step(r'I create a batch prediction for the dataset with the logistic regression$')
def i_create_a_batch_prediction_logistic_model(step):
    dataset = world.dataset.get('resource')
    logistic = world.logistic_regression.get('resource')
    resource = world.api.create_batch_prediction(logistic, dataset)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.batch_prediction = resource['object']
    world.batch_predictions.append(resource['resource'])


#@step(r'I create a batch prediction for the dataset with the fusion$')
def i_create_a_batch_prediction_fusion(step):
    dataset = world.dataset.get('resource')
    fusion = world.fusion.get('resource')
    resource = world.api.create_batch_prediction(fusion, dataset)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.batch_prediction = resource['object']
    world.batch_predictions.append(resource['resource'])
