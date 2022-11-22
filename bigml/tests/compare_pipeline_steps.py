# -*- coding: utf-8 -*-
#
# Copyright 2022 BigML
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
import os
import zipfile

from .world import world, res_filename, eq_, ok_


from bigml.pipeline.pipeline import BMLPipeline, Pipeline
from bigml.api import BigML

def i_expand_file_with_models_list(step, pipeline_file, models_list):
    inner_files = []
    models_list = json.loads(models_list)
    for resource_id in models_list:
        inner_files.append(resource_id.replace("/", "_"))

    pipeline_file = res_filename(pipeline_file)
    with zipfile.ZipFile(pipeline_file, 'r') as zip_ref:
        filenames = [os.path.basename(filename) for
                     filename in zip_ref.namelist()]
        ok_(all(filename in filenames for filename in inner_files))
        zip_ref.extractall(os.path.dirname(pipeline_file))


#@step(r'I create a local pipeline for "(.*)" named "(.*)"$')
def i_create_a_local_pipeline_from_models_list(
    step, models_list, name, storage=None):
    if not isinstance(models_list, list):
        models_list = json.loads(models_list)
    kwargs = {}
    if storage is not None:
        kwargs = {'api': BigML(storage=res_filename(storage))}
    world.local_pipeline = BMLPipeline(name,
                                       models_list,
                                       **kwargs)
    return world.local_pipeline


def the_pipeline_transformed_data_is(step, input_data, output_data):
    if input_data is None:
        input_data = "{}"
    if output_data is None:
        output_data = "{}"
    input_data = json.loads(input_data)
    output_data = json.loads(output_data)
    transformed_data = world.local_pipeline.transform([input_data])
    for key, value in transformed_data[0].items():
        eq_(output_data.get(key), value)


def the_pipeline_result_key_is(step, input_data, key, value, precision=None):
    if input_data is None:
        input_data = "{}"
    input_data = json.loads(input_data)
    transformed_data = world.local_pipeline.transform([input_data])
    pipe_value = transformed_data[0].get(key)
    if precision is not None and not isinstance(value, str):
        pipe_value = round(pipe_value, precision)
        value = round(value, precision)
    eq_(str(value), str(pipe_value))


def i_create_composed_pipeline(
    step, pipelines_list, name):
    world.local_pipeline = Pipeline(name, pipelines_list)
