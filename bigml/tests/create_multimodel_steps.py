# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2014-2017 BigML
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
from nose.tools import ok_

#@step(r'I store the dataset id in a list')
def i_store_dataset_id(step):
    world.dataset_ids.append(world.dataset['resource'])

#@step(r'I check the model stems from the original dataset list')
def i_check_model_datasets_and_datasets_ids(step):
    model = world.model
    ok_('datasets' in model and model['datasets'] == world.dataset_ids,
        ("The model contains only %s and the dataset ids are %s" %
         (",".join(model['datasets']), ",".join(world.dataset_ids))))
