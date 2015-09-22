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

import json

from world import world
from bigml.api import HTTP_OK
from bigml.fields import Fields

#@step(r'I get the dataset "(.*)"')
def i_get_the_dataset(step, dataset):
    resource = world.api.get_dataset(dataset)
    world.status = resource['code']
    assert world.status == HTTP_OK
    world.dataset = resource['object']


#@step(r'I ask for the missing values counts in the fields')
def i_get_the_missing_values(step):
    resource = world.dataset
    fields = Fields(resource['fields'])
    world.step_result = fields.missing_counts()


#@step(r'I ask for the error counts in the fields')
def i_get_the_errors_values(step):
    resource = world.dataset
    world.step_result = world.api.error_counts(resource)


#@step(r'the (missing values counts|error counts) dict is "(.*)"')
def i_get_the_properties_values(step, text, properties_dict):
    if properties_dict is None:
        assert False
    assert world.step_result == json.loads(properties_dict)
