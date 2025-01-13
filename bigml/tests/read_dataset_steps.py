# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,no-member
#
# Copyright 2012-2025 BigML
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

from bigml.fields import Fields
from .world import world, eq_, ok_


def i_get_the_missing_values(step):
    """Step: I ask for the missing values counts in the fields"""
    resource = world.dataset
    fields = Fields(resource['fields'])
    step.bigml["result"] = fields.missing_counts()


def i_get_the_errors_values(step):
    """Step: I ask for the error counts in the fields """
    resource = world.dataset
    step.bigml["result"] = world.api.error_counts(resource)


def i_get_the_properties_values(step, properties_dict):
    """Step: the (missing values counts|error counts) dict
    is <properties_dict>
    """
    ok_(properties_dict is not None)
    eq_(step.bigml["result"], json.loads(properties_dict))
