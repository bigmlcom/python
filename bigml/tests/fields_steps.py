# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015-2016 BigML
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

from world import world
from bigml.fields import Fields

#@step(r'I create a Fields object from the source with objective column "(.*)"')
def create_fields(step, objective_column):
     world.fields = Fields(world.source, objective_field=int(objective_column),
                           objective_field_present=True)


#@step(r'the object id is "(.*)"')
def check_objective(step, objective_id):
    found_id = world.fields.field_id(world.fields.objective_field)
    if found_id != objective_id:
        print "found: %s, expected: %s" % (found_id,
                                           objective_id)
    assert found_id == objective_id
