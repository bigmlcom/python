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

import time
import json
import os
from datetime import datetime, timedelta
from world import world
from nose.tools import eq_, assert_less

from bigml.api import HTTP_CREATED
from bigml.api import HTTP_ACCEPTED
from bigml.api import FINISHED
from bigml.api import FAULTY
from bigml.api import get_status

from read_execution_steps import i_get_the_execution


#@step(r'the script id is correct, the value of "(.*)" is "(.*)" and the result is "(.*)"')
def the_execution_and_attributes(step, param, param_value, result):
    eq_(world.script['resource'], world.execution['script'])
    print world.execution['execution']['results']
    eq_(world.execution['execution']['results'][0], result)
    res_param_value = world.execution[param]
    eq_(res_param_value, param_value,
        ("The execution %s is %s and the expected %s is %s" %
         (param, param_value, param, param_value)))

#@step(r'the script ids are correct, the value of "(.*)" is "(.*)" and the result is "(.*)"')
def the_execution_ids_and_attributes(step, number_of_scripts,
                                     param, param_value, result):
    scripts = world.scripts[-number_of_scripts:]
    eq_(scripts, world.execution['scripts'])
    print world.execution['execution']['results']
    eq_(world.execution['execution']['results'], result)
    res_param_value = world.execution[param]
    eq_(res_param_value, param_value,
        ("The execution %s is %s and the expected %s is %s" %
         (param, param_value, param, param_value)))

#@step(r'I create a whizzml execution from an existing script"$')
def i_create_an_execution(step):
    resource = world.api.create_execution(world.script['resource'])
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.execution = resource['object']
    world.executions.append(resource['resource'])


#@step(r'I create a whizzml execution from the last two scripts$')
def i_create_an_execution_from_list(step, number_of_scripts=2):
    scripts = world.scripts[-number_of_scripts:]
    resource = world.api.create_execution(scripts)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.execution = resource['object']
    world.executions.append(resource['resource'])


#@step(r'I update the execution with "(.*)", "(.*)"$')
def i_update_an_execution(step, param, param_value):
    resource = world.api.update_execution(world.execution['resource'],
                                          {param: param_value})
    world.status = resource['code']
    eq_(world.status, HTTP_ACCEPTED)
    world.location = resource['location']
    world.execution = resource['object']


#@step(r'I wait until the execution status code is either (\d) or (-\d) less than (\d+)')
def wait_until_execution_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    delta = int(secs) * world.delta
    execution_id = world.execution['resource']
    i_get_the_execution(step, execution_id)
    status = get_status(world.execution)
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
           time.sleep(3)
           assert_less((datetime.utcnow() - start).seconds, delta)
           i_get_the_execution(step, execution_id)
           status = get_status(world.execution)
    eq_(status['code'], int(code1))


#@step(r'I wait until the script is ready less than (\d+)')
def the_execution_is_finished(step, secs):
    wait_until_execution_status_code_is(step, FINISHED, FAULTY, secs)
