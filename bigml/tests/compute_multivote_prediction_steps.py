# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument,no-member
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

import json

from bigml.multivote import MultiVote

from .world import world, res_filename, eq_, ok_

DIGITS = 5


def i_create_a_multivote(step, predictions_file):
    """Step: I create a MultiVote for the set of predictions in file
    <predictions_file>
    """
    predictions_path = res_filename(predictions_file)
    try:
        with open(predictions_file, 'r') as predictions_path:
            world.multivote = MultiVote(json.load(predictions_path))
    except IOError:
        ok_(False, "Failed to read %s" % predictions_path)


def compute_prediction(step, method):
    """Step: I compute the prediction with confidence using method
    <method>
    """
    try:
        prediction = world.multivote.combine(int(method), full=True)
        world.combined_prediction = prediction["prediction"]
        world.combined_confidence = prediction["confidence"]
    except ValueError:
        ok_(False, "Incorrect method")


def compute_prediction_no_confidence(step, method):
    """Step: I compute the prediction without confidence using method <method>
    """
    try:
        world.combined_prediction_nc = world.multivote.combine(int(method))
    except ValueError:
        ok_(False, "Incorrect method")


def check_combined_prediction(step, prediction):
    """Step: the combined prediction is <prediction>"""
    if world.multivote.is_regression():
        try:
            eq_(round(world.combined_prediction, DIGITS),
                round(float(prediction), DIGITS))
        except ValueError as exc:
            ok_(False, str(exc))
    else:
        eq_(world.combined_prediction, prediction)


def check_combined_prediction_no_confidence(step, prediction):
    """Step: the combined prediction without confidence is <prediction>"""
    if world.multivote.is_regression():
        try:
            eq_(round(world.combined_prediction_nc, DIGITS),
                round(float(prediction), DIGITS))
        except ValueError as exc:
            ok_(False, str(exc))
    else:
        eq_(world.combined_prediction, prediction)


def check_combined_confidence(step, confidence):
    """Step: the confidence for the combined prediction is <confidence>"""
    try:
        eq_(round(world.combined_confidence, DIGITS),
            round(float(confidence), DIGITS))
    except ValueError as exc:
        ok_(False, str(exc))
