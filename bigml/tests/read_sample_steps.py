# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015-2020 BigML
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

from .world import world
from nose.tools import eq_
from bigml.api import HTTP_OK

#@step(r'I get the sample "(.*)"')
def i_get_the_sample(step, resource):
    resource = world.api.get_sample(resource)
    world.status = resource['code']
    eq_(world.status, HTTP_OK)
    world.sample = resource['object']
