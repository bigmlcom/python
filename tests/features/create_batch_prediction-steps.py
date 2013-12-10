# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2012 BigML
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
from datetime import datetime, timedelta
from lettuce import step, world

from bigml.api import HTTP_CREATED
from bigml.api import FINISHED
from bigml.api import FAULTY
from bigml.api import get_status


@step(r'I create a batch prediction for the dataset with the model$')
def i_create_a_batch_prediction(step):
    dataset = world.dataset.get('resource')
    model = world.model.get('resource')
    resource = world.api.create_batch_prediction(model, dataset)
    world.status = resource['code']
    assert world.status == HTTP_CREATED
    world.location = resource['location']
    world.batch_prediction = resource['object']
    world.batch_predictions.append(resource['resource'])


@step(r'I create a batch prediction for the dataset with the ensemble$')
def i_create_a_batch_prediction_ensemble(step):
    dataset = world.dataset.get('resource')
    ensemble = world.ensemble.get('resource')
    resource = world.api.create_batch_prediction(ensemble, dataset)
    world.status = resource['code']
    assert world.status == HTTP_CREATED
    world.location = resource['location']
    world.batch_prediction = resource['object']
    world.batch_predictions.append(resource['resource'])


@step(r'I wait until the batch prediction status code is either (\d) or (-\d) less than (\d+)')
def wait_until_batch_prediction_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    step.given('I get the batch prediction "{id}"'.format(id=world.batch_prediction['resource']))
    status = get_status(world.batch_prediction)
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
        time.sleep(3)
        assert datetime.utcnow() - start < timedelta(seconds=int(secs))
        step.given('I get the batch prediction "{id}"'.format(id=world.batch_prediction['resource']))
        status = get_status(world.batch_prediction)
    assert status['code'] == int(code1)


@step(r'I wait until the batch prediction is ready less than (\d+)')
def the_batch_prediction_is_finished_in_less_than(step, secs):
    wait_until_batch_prediction_status_code_is(step, FINISHED, FAULTY, secs)


@step(r'I download the created predictions file to "(.*)"')
def i_download_predictions_file(step, filename):
    file_object = world.api.download_batch_prediction(
        world.batch_prediction, filename=filename)
    assert file_object is not None
    world.output = file_object
    

@step(r'the batch prediction file is like "(.*)"')
def i_check_predictions(step, check_file):
    predictions_file = world.output
    try:
        predictions_file = csv.reader(open(predictions_file, "U"), lineterminator="\n")
        check_file = csv.reader(open(check_file, "U"), lineterminator="\n")
        for row in predictions_file:
            check_row = check_file.next()
            if len(check_row) != len(row):
                assert False
            for index in range(len(row)):
                dot = row[index].find(".")
                if dot > 0:
                    try:
                        decimal_places = min(len(row[index]), len(check_row[index])) - dot - 1
                        row[index] = round(float(row[index]), decimal_places)
                        check_row[index] = round(float(check_row[index]), decimal_places)    
                    except ValueError:
                        pass
                if check_row[index] != row[index]:
                    print row, check_row
                    assert False
        assert True
    except Exception, exc:
        assert False, str(exc)
