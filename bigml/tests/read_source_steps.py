# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2012-2020 BigML
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

#@step(r'I get the source "(.*)"')
def i_get_the_source(step, resource):
    resource = world.api.get_source(resource)
    world.status = resource['code']
    eq_(world.status, HTTP_OK)
    world.source = resource['object']

#@step(r'the source has DEV (True|False)')
def source_has_dev(step, boolean):
    if boolean == 'False':
        boolean = ''
    boolean = bool(boolean)
    dev = world.source['dev']
    eq_(dev, boolean)
