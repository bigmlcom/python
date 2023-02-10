# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument,no-member
#
# Copyright 2016-2023 BigML
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

from bigml.topicmodel import TopicModel

from .world import eq_, approx_


def i_make_a_prediction(step, model, text, expected):
    """Step: predict the topic distribution for the text <expected>"""
    topic_model = TopicModel(model)
    distribution = topic_model.distribution(text)

    msg = ("Computed distribution is %s, but expected distribution is %s" %
           (str(distribution), str(expected)))

    eq_(len(distribution), len(expected), msg=msg)

    for dis, exp in zip(distribution, expected):
        approx_(dis['probability'], exp['probability'], precision=6, msg=msg)
