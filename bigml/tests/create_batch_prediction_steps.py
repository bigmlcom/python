# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument,no-member
#
# Copyright 2012-2022 BigML
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

from bigml.api import HTTP_CREATED
from bigml.api import FINISHED, FAULTY
from bigml.io import UnicodeReader

from .read_resource_steps import wait_until_status_code_is
from .world import world, res_filename, eq_, ok_


def i_create_a_batch_prediction(step):
    """Step: I create a batch prediction for the dataset with the model"""
    dataset = world.dataset.get('resource')
    model = world.model.get('resource')
    resource = world.api.create_batch_prediction(model, dataset)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.batch_prediction = resource['object']
    world.batch_predictions.append(resource['resource'])


def i_create_a_batch_prediction_ensemble(step, params=None):
    """Step: I create a batch prediction for the dataset with the ensemble and
    <params>"""
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


def wait_until_batch_prediction_status_code_is(step, code1, code2, secs):
    """Step: I wait until the batch prediction status code is either <code1>
    or <code2> less than <secs>"""
    world.batch_prediction = wait_until_status_code_is(
        code1, code2, secs, world.batch_prediction)


def wait_until_batch_centroid_status_code_is(step, code1, code2, secs):
    """Step: I wait until the batch centroid status code is either <code1> or
    <code2> less than <secs>"""
    world.batch_centroid = wait_until_status_code_is(
        code1, code2, secs, world.batch_centroid)


def wait_until_batch_anomaly_score_status_code_is(step, code1, code2, secs):
    """Step: I wait until the batch anomaly score status code is either <code1>
    or <code2> less than <secs>"""
    world.batch_anomlay_score = wait_until_status_code_is(
        code1, code2, secs, world.batch_anomaly_score)


def the_batch_prediction_is_finished_in_less_than(step, secs):
    """Step: I wait until the batch prediction is ready less than <secs>"""
    wait_until_batch_prediction_status_code_is(step, FINISHED, FAULTY, secs)


def the_batch_centroid_is_finished_in_less_than(step, secs):
    """Step: I wait until the batch centroid is ready less than <secs>"""
    wait_until_batch_centroid_status_code_is(step, FINISHED, FAULTY, secs)


def the_batch_anomaly_score_is_finished_in_less_than(step, secs):
    """Step: I wait until the batch anomaly score is ready less than <secs>"""
    wait_until_batch_anomaly_score_status_code_is(step, FINISHED, FAULTY, secs)


def i_download_predictions_file(step, filename):
    """Step: I download the created predictions file to <filename>"""
    file_object = world.api.download_batch_prediction(
        world.batch_prediction, filename=res_filename(filename))
    ok_(file_object is not None)
    world.output = file_object


def i_download_centroid_file(step, filename):
    """Step: I download the created centroid file to <filename>"""
    file_object = world.api.download_batch_centroid(
        world.batch_centroid, filename=res_filename(filename))
    ok_(file_object is not None)
    world.output = file_object


def i_download_anomaly_score_file(step, filename):
    """Step: I download the created anomaly score file to <filename>"""
    file_object = world.api.download_batch_anomaly_score(
        world.batch_anomaly_score, filename=res_filename(filename))
    ok_(file_object is not None)
    world.output = file_object


def check_rows(prediction_rows, test_rows):
    """Checking rows identity"""
    row_num = 0
    for row in prediction_rows:
        check_row = next(test_rows)
        row_num += 1
        eq_(len(check_row), len (row))
        for index, cell in enumerate(row):
            dot = cell.find(".")
            if dot > 0:
                try:
                    decs = min(len(cell), len(check_row[index])) - dot - 1
                    cell = round(float(cell), decs)
                    check_row[index] = round(float(check_row[index]), decs)
                except ValueError:
                    pass
            eq_(check_row[index], cell,
                "Got: %s/ Expected: %s in line %s" % (row, check_row, row_num))


def i_check_predictions(step, check_file):
    """Step: I download the created anomaly score file to <check_file>"""
    with UnicodeReader(world.output) as prediction_rows:
        with UnicodeReader(res_filename(check_file)) as test_rows:
            check_rows(prediction_rows, test_rows)


def i_check_batch_centroid(step, check_file):
    """Step: the batch centroid file is like <check_file>"""
    i_check_predictions(step, check_file)


def i_check_batch_anomaly_score(step, check_file):
    """Step: the batch anomaly score file is like <check_file>"""
    i_check_predictions(step, check_file)


def i_check_batch_centroid_is_ok(step):
    """Step: I check the batch centroid is ok"""
    ok_(world.api.ok(world.batch_centroid))


def i_check_batch_anomaly_score_is_ok(step):
    """Step: I check the batch anomaly score is ok"""
    ok_(world.api.ok(world.batch_anomaly_score))


def i_create_a_batch_prediction_with_cluster(step):
    """Step: I create a batch centroid for the dataset"""
    dataset = world.dataset.get('resource')
    cluster = world.cluster.get('resource')
    resource = world.api.create_batch_centroid(cluster, dataset)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.batch_centroid = resource['object']
    world.batch_centroids.append(resource['resource'])


def i_create_a_batch_prediction_with_anomaly(step):
    """Step: I create a batch anomaly score"""
    dataset = world.dataset.get('resource')
    anomaly = world.anomaly.get('resource')
    resource = world.api.create_batch_anomaly_score(anomaly, dataset)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.batch_anomaly_score = resource['object']
    world.batch_anomaly_scores.append(resource['resource'])


def i_create_a_linear_batch_prediction(step):
    """Step: I create a linear batch prediction"""
    dataset = world.dataset.get('resource')
    linear_regression = world.linear_regression.get('resource')
    resource = world.api.create_batch_prediction(linear_regression, dataset)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.batch_prediction = resource['object']
    world.batch_predictions.append(resource['resource'])


def i_create_a_source_from_batch_prediction(step):
    """Step: I create a source from the batch prediction"""
    batch_prediction = world.batch_prediction.get('resource')
    resource = world.api.source_from_batch_prediction(batch_prediction)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.source = resource['object']
    world.sources.append(resource['resource'])


def i_create_a_batch_prediction_logistic_model(step):
    """Step: I create a batch prediction for the dataset with the logistic
    regression
    """
    dataset = world.dataset.get('resource')
    logistic = world.logistic_regression.get('resource')
    resource = world.api.create_batch_prediction(logistic, dataset)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.batch_prediction = resource['object']
    world.batch_predictions.append(resource['resource'])


def i_create_a_batch_prediction_fusion(step):
    """Step: I create a batch prediction for the dataset with the fusion"""
    dataset = world.dataset.get('resource')
    fusion = world.fusion.get('resource')
    resource = world.api.create_batch_prediction(fusion, dataset)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.batch_prediction = resource['object']
    world.batch_predictions.append(resource['resource'])
