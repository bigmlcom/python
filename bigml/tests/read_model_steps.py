# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2012-2015 BigML
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

from bigml.api import HTTP_OK

#@step(r'I get the model "(.*)"')
def i_get_the_model(step, model):
    resource = world.api.get_model(model)
    world.status = resource['code']
    assert world.status == HTTP_OK
    world.model = resource['object']


#@step(r'I get the logistic regression model "(.*)"')
def i_get_the_logistic_model(step, model):
    resource = world.api.get_logistic_regression(model)
    world.status = resource['code']
    assert world.status == HTTP_OK
    world.logistic_regression = resource['object']
