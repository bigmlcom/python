# -*- coding: utf-8 -*-
#
# Copyright 2012, 2015-2022 BigML
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

import io
import os
import json

import bigml.generators.model as g


from bigml.tests.world import res_filename
from .world import world
from nose.tools import eq_
from bigml.predict_utils.common import extract_distribution
from bigml.util import utf8


#@step(r'I translate the tree into IF-THEN rules$')
def i_translate_the_tree_into_IF_THEN_rules(step):
    output = io.StringIO()
    g.rules(world.local_model, out=output)
    world.output = output.getvalue()

#@step(r'I check data distribution with "(.*)" file$')
def i_check_the_data_distribution(step, file):
    distribution = g.get_data_distribution(world.local_model)

    distribution_str = ''
    for bin_value, bin_instances in distribution:
        distribution_str += "[%s,%s]\n" % (bin_value, bin_instances)
    world.output = utf8(distribution_str)
    i_check_if_the_output_is_like_expected_file(step, file)


#@step(r'I check the predictions distribution with "(.*)" file$')
def i_check_the_predictions_distribution(step, file):
    predictions = g.get_prediction_distribution(world.local_model)

    distribution_str = ''
    for group, instances in predictions:
        distribution_str += "[%s,%s]\n" % (group, instances)

    world.output = utf8(distribution_str)

    i_check_if_the_output_is_like_expected_file(step, file)


#@step(r'I check the model summary with "(.*)" file$')
def i_check_the_model_summary_with(step, file):
    output = io.StringIO()
    g.summarize( world.local_model, out=output)
    world.output = output.getvalue()
    i_check_if_the_output_is_like_expected_file(step, file)


#@step(r'I check the output is like "(.*)" expected file')
def i_check_if_the_output_is_like_expected_file(step, expected_file):
    file = open(res_filename(expected_file), "r")
    expected_content = file.read()
    file.close()
    eq_(world.output.strip(), expected_content.strip())

#@step(r'I check the distribution print with "(.*)" file$')
def i_check_print_distribution(step, filename):
    output = io.StringIO()
    _, distribution = extract_distribution(world.local_model.root_distribution)
    g.print_distribution(distribution, output)
    world.output = output.getvalue()
    if world.debug:
        backup = "%s.bck" % filename
        with open(backup, "w") as bck_file:
            bck_file.write(world.output)
    i_check_if_the_output_is_like_expected_file(step, filename)

#@step(r'I check the list fields print with "(.*)" file$')
def i_list_fields(step, filename):
    output = io.StringIO()
    g.list_fields(world.local_model, output)
    world.output = output.getvalue()
    if world.debug:
        backup = "%s.bck" % filename
        with open(backup, "w") as bck_file:
            bck_file.write(world.output)
    i_check_if_the_output_is_like_expected_file(step, filename)

#@step(r'I check the tree csv print with "(.*)" file$')
def i_create_tree_csv(step, filename):
    rows = g.tree_csv(world.local_model)
    world.output = json.dumps(rows)
    if world.debug:
        backup = "%s.bck" % filename
        with open(backup, "w") as bck_file:
            bck_file.write(world.output)
    i_check_if_the_output_is_like_expected_file(step, filename)

def update_content(filename, content):
    with open(res_filename(filename), "w") as file_handler:
        file_handler.write(content)
