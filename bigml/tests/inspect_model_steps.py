# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2012, 2015-2016 BigML
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
from bigml.tests.world import res_filename
from world import world


#@step(r'I translate the tree into IF-THEN rules$')
def i_translate_the_tree_into_IF_THEN_rules(step):
    output = io.BytesIO()
    world.local_model.rules(out=output)
    world.output = output.getvalue()

#@step(r'I check data distribution with "(.*)" file$')
def i_check_the_data_distribution(step, file):
    distribution = world.local_model.get_data_distribution()

    distribution_str = ''
    for bin_value, bin_instances in distribution:
        distribution_str += "[%s,%s]\n" % (bin_value, bin_instances)

    world.output = distribution_str.encode('utf-8')

    i_check_if_the_output_is_like_expected_file(step, file)


#@step(r'I check the predictions distribution with "(.*)" file$')
def i_check_the_predictions_distribution(step, file):
    predictions = world.local_model.get_prediction_distribution()


    distribution_str = ''
    for group, instances in predictions:
        distribution_str += "[%s,%s]\n" % (group, instances)

    world.output = distribution_str.encode('utf-8')

    i_check_if_the_output_is_like_expected_file(step, file)


#@step(r'I check the model summary with "(.*)" file$')
def i_check_the_model_summary_with(step, file):
    output = io.BytesIO()
    world.local_model.summarize(out=output)
    world.output = output.getvalue()
    i_check_if_the_output_is_like_expected_file(step, file)


#@step(r'I check the output is like "(.*)" expected file')
def i_check_if_the_output_is_like_expected_file(step, expected_file):
    file = open(res_filename(expected_file), "rb")
    expected_content = file.read()
    file.close()
    if world.output.strip() == expected_content.strip():
        assert True
    else:
        assert False, "Found:\n%s\n\nExpected:\n%s\n\n" % (world.output,
                                                           expected_content)
