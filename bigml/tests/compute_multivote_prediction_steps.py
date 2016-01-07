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
import os
from datetime import datetime, timedelta
from world import world, res_filename

from bigml.api import HTTP_CREATED
from bigml.api import HTTP_ACCEPTED
from bigml.api import FINISHED
from bigml.api import FAULTY
from bigml.api import get_status
from bigml.multivote import MultiVote

#@step(r'I create a MultiVote for the set of predictions in file (.*)$')
def i_create_a_multivote(step, predictions_file):
    predictions_file = res_filename(predictions_file)
    try:
        with open(predictions_file, 'r') as predictions_file:
            world.multivote = MultiVote(json.load(predictions_file))
    except IOError:
        assert False, "Failed to read %s" % predictions_file

#@step(r'I compute the prediction with confidence using method "(.*)"$')
def compute_prediction(step, method):
    try:
        world.combined_prediction, world.combined_confidence = (
            world.multivote.combine(int(method), with_confidence=True))
    except ValueError:
        assert False, "Incorrect method"

#@step(r'I compute the prediction without confidence using method "(.*)"$')
def compute_prediction_no_confidence(step, method):
    try:
        world.combined_prediction_nc = world.multivote.combine(int(method))
    except ValueError:
        assert False, "Incorrect method"

#@step(r'the combined prediction is "(.*)"$')
def check_combined_prediction(step, prediction):

    if world.multivote.is_regression():
        try:
            assert round(world.combined_prediction, 6) == round(float(prediction), 6)
        except ValueError, exc:
            assert False, str(exc)
    else:
        assert world.combined_prediction == prediction

#@step(r'the combined prediction without confidence is "(.*)"$')
def check_combined_prediction_no_confidence(step, prediction):

    if world.multivote.is_regression():
        try:
            assert round(world.combined_prediction_nc, 6) == round(
                float(prediction), 6)
        except ValueError, exc:
            assert False, str(exc)
    else:
        assert world.combined_prediction == prediction

#@step(r'the confidence for the combined prediction is (.*)$')
def check_combined_confidence(step, confidence):
    try:
        assert round(world.combined_confidence, 6) == round(float(confidence), 6)
    except ValueError, exc:
        assert False, str(exc)
