# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument,no-member
#
# Copyright 2022-2023 BigML
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

from bigml.dataset import Dataset

from .world import res_filename, eq_


def i_create_a_local_dataset_from_file(step, dataset_file):
    """Step: I create a local dataset from a <dataset_file> file"""
    step.bigml["local_dataset"] = Dataset(res_filename(dataset_file))


def the_transformed_data_is(step, input_data, output_data):
    """Checking expected transformed data"""
    if input_data is None:
        input_data = "{}"
    if output_data is None:
        output_data = "{}"
    input_data = json.loads(input_data)
    output_data = json.loads(output_data)
    transformed_data = step.bigml["local_dataset"].transform([input_data])
    for key, value in transformed_data[0].items():
        eq_(output_data.get(key), value)
