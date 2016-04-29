# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015 BigML
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

from bigml.api import HTTP_CREATED
from bigml.api import HTTP_ACCEPTED
from bigml.api import FINISHED
from bigml.api import FAULTY
from bigml.api import get_status

from read_script_steps import i_get_the_script


#@step(r'the script code is "(.*)" and the value of "(.*)" is "(.*)"')
def the_script_code_and_attributes(step, source_code, param, param_value):
    res_param_value = world.script[param]
    if res_param_value == param_value:
        assert True
    else:
        assert False, ("The script %s is %s "
                       "and the expected %s is %s" %
                       (param, param_value, param, param_value))


#@step(r'I create a whizzml script from a excerpt of code "(.*)"$')
def i_create_a_script(step, source_code):
    resource = world.api.create_script(source_code)
    world.status = resource['code']
    assert world.status == HTTP_CREATED
    world.location = resource['location']
    world.script = resource['object']
    world.scripts.append(resource['resource'])


#@step(r'I update the script with "(.*)", "(.*)"$')
def i_update_a_script(step, param, param_value):
    resource = world.api.update_script(world.script['resource'],
                                      {param: param_value})
    world.status = resource['code']
    assert world.status == HTTP_ACCEPTED
    world.location = resource['location']
    world.script = resource['object']


#@step(r'I wait until the script status code is either (\d) or (-\d) less than (\d+)')
def wait_until_script_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    script_id = world.script['resource']
    i_get_the_script(step, script_id)
    status = get_status(world.script)
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
           time.sleep(3)
           assert datetime.utcnow() - start < timedelta(seconds=int(secs))
           i_get_the_script(step, script_id)
           status = get_status(world.script)
    assert status['code'] == int(code1)


#@step(r'I wait until the script is ready less than (\d+)')
def the_script_is_finished(step, secs):
    wait_until_script_status_code_is(step, FINISHED, FAULTY, secs)
