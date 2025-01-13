# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument,no-member
#
# Copyright 2014-2025 BigML
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

from .world import world, ok_

def i_store_dataset_id(step):
    """Step: I store the dataset id in a list"""
    if step.bigml.get("dataset_ids") is None:
        step.bigml["dataset_ids"] = []
    step.bigml["dataset_ids"].append(world.dataset['resource'])


def i_check_model_datasets_and_datasets_ids(step):
    """Step: I check the model stems from the original dataset list"""
    model = world.model
    ok_('datasets' in model and model['datasets'] == step.bigml["dataset_ids"],
        ("The model contains only %s and the dataset ids are %s" %
         (",".join(model['datasets']), ",".join(step.bigml["dataset_ids"]))))
