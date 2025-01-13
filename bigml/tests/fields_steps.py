# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument,no-member
#
# Copyright 2015-2025 BigML
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

from bigml.fields import Fields, get_resource_type
from bigml.io import UnicodeReader

from .world import world, res_filename, eq_, ok_


def create_fields(step, objective_column):
    """Step: I create a Fields object from the source with objective column
    <objective_column>
    """
    world.fields = Fields(world.source, objective_field=int(objective_column),
                          objective_field_present=True)


def create_fields_from_dataset(step, objective_column):
    """Step: I create a Fields object from the dataset with objective column
    objective_column
    """
    world.fields = Fields(world.dataset, objective_field=int(objective_column),
                          objective_field_present=True)


def check_objective(step, objective_id):
    """Step: the object id is <objective_id> """
    found_id = world.fields.field_id(world.fields.objective_field)
    eq_(found_id, objective_id)


def import_summary_file(step, summary_file):
    """#Step: I import a summary fields file <summary_field> as a fields
    structure
    """
    world.fields_struct = world.fields.new_fields_structure( \
        csv_attributes_file=res_filename(summary_file))


def check_field_type(step, field_id, field_type):
    """Step: I check the new field structure has field <field_id> as
    <field_type>
    """
    ok_(field_id in list(world.fields_struct['fields'].keys()))
    eq_(world.fields_struct['fields'][field_id]["optype"], field_type)


def generate_summary(step, summary_file):
    """Step: I export a summary fields file <summary_file> """
    world.fields.summary_csv(res_filename(summary_file))


def check_summary_like_expected(step, summary_file, expected_file):
    """Step: I check that the fields summary file is like <expected_file>"""
    summary_contents = []
    expected_contents = []
    with UnicodeReader(res_filename(summary_file)) as summary_handler:
        for line in summary_handler:
            summary_contents.append(line)
    with UnicodeReader(res_filename(expected_file)) as expected_handler:
        for line in expected_handler:
            expected_contents.append(line)
    eq_(summary_contents, expected_contents)


def update_with_summary_file(step, resource, summary_file):
    """Step: I update the <resource> with the file <summary_file>"""
    if get_resource_type(resource) == "source":
        # We need to download the source again, as it could have been closed
        resource = world.api.get_source(resource)
        if resource.get("object", {}).get("closed", False):
            resource = world.api.clone_source(resource)
            world.api.ok(resource)
    fields = Fields(resource)
    changes = fields.filter_fields_update( \
        fields.new_fields_structure(res_filename(summary_file)))
    resource_type = get_resource_type(resource)
    resource = world.api.updaters[resource_type](resource, changes)
    world.api.ok(resource)
    setattr(world, resource_type, resource)


def check_resource_field_type(step, resource, field_id, optype):
    """Step: I check the source has field <field_id> as <optype> """
    eq_(resource["object"]["fields"][field_id]["optype"], optype)
