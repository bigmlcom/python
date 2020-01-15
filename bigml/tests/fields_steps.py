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

from world import world, res_filename
from bigml.fields import Fields
from bigml.io import UnicodeReader

from nose.tools import eq_

#@step(r'I create a Fields object from the source with objective column "(.*)"')
def create_fields(step, objective_column):
     world.fields = Fields(world.source, objective_field=int(objective_column),
                           objective_field_present=True)



#@step(r'I create a Fields object from the dataset with objective column "(.*)"')
def create_fields_from_dataset(step, objective_column):
     world.fields = Fields(world.dataset, objective_field=int(objective_column),
                           objective_field_present=True)



#@step(r'the object id is "(.*)"')
def check_objective(step, objective_id):
    found_id = world.fields.field_id(world.fields.objective_field)
    eq_(found_id, objective_id)


#@step(r'I import a summary fields file "(.*)" as a fields structure')
def import_summary_file(step, summary_file):
    world.fields_struct = world.fields.new_fields_structure( \
        csv_attributes_file=res_filename(summary_file))


#@step(r'I check the new field structure has field "(.*)" as "(.*)"')
def check_field_type(step, field_id, field_type):
    assert field_id in world.fields_struct['fields'].keys()
    eq_(world.fields_struct['fields'][field_id]["optype"], field_type)


#@step(r'I export a summary fields file "(.*)"')
def generate_summary(step, summary_file):
    world.fields.summary_csv(res_filename(summary_file))


#@step(r'I check that the fields summary file is like "(.*)"')
def check_summary_like_expected(step, summary_file, expected_file):
    summary_contents = []
    expected_contents = []
    with UnicodeReader(res_filename(summary_file)) as summary_handler:
        for line in summary_handler:
            summary_contents.append(line)
    with UnicodeReader(res_filename(expected_file)) as expected_handler:
        for line in expected_handler:
            expected_contents.append(line)
    eq_(summary_contents, expected_contents)
