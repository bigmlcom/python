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

import os
from world import world
from nose.tools import eq_

from bigml.api import HTTP_OK

#@step(r'I get the model "(.*)"')
def i_get_the_model(step, model):
    resource = world.api.get_model(model)
    world.status = resource['code']
    eq_(world.status, HTTP_OK)
    world.model = resource['object']


#@step(r'I get the logistic regression model "(.*)"')
def i_get_the_logistic_model(step, model):
    resource = world.api.get_logistic_regression(model)
    world.status = resource['code']
    eq_(world.status, HTTP_OK)
    world.logistic_regression = resource['object']


#@step(r'I get the deepnet model "(.*)"')
def i_get_the_deepnet_model(step, deepnet):
    resource = world.api.get_deepnet(deepnet)
    world.status = resource['code']
    eq_(world.status, HTTP_OK)
    world.deepnet = resource['object']


#@step(r'I get the optiml "(.*)"')
def i_get_the_optiml(step, optiml):
    resource = world.api.get_optiml(optiml)
    world.status = resource['code']
    eq_(world.status, HTTP_OK)
    world.optiml = resource['object']


#@step(r'I get the fusion "(.*)"')
def i_get_the_fusion(step, fusion):
    resource = world.api.get_fusion(fusion)
    world.status = resource['code']
    eq_(world.status, HTTP_OK)
    world.fusion = resource['object']
