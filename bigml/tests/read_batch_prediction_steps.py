# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015-2019 BigML
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

import os
from world import world
from nose.tools import eq_

from bigml.api import HTTP_OK

#@step(r'I get the batch prediction "(.*)"')
def i_get_the_batch_prediction(step, batch_prediction):
    resource = world.api.get_batch_prediction(batch_prediction)
    world.status = resource['code']
    eq_(world.status, HTTP_OK)
    world.batch_prediction = resource['object']

#@step(r'I get the batch centroid "(.*)"')
def i_get_the_batch_centroid(step, batch_centroid):
    resource = world.api.get_batch_centroid(batch_centroid)
    world.status = resource['code']
    eq_(world.status, HTTP_OK)
    world.batch_centroid = resource['object']

#@step(r'I get the batch anomaly score "(.*)"')
def i_get_the_batch_anomaly_score(step, batch_anomaly_score):
    resource = world.api.get_batch_anomaly_score(batch_anomaly_score)
    world.status = resource['code']
    eq_(world.status, HTTP_OK)
    world.batch_anomaly_score = resource['object']
