# -*- coding: utf-8 -*-
#
# Copyright 2021-2022 BigML
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

"""Declared exceptions.

"""

class ResourceException(Exception):
    """Base class to any exception that arises from a bad structured resource

    """
    pass


class NoRootDecisionTree(ResourceException):
    """The decision tree structure has no "root" attribute """
    pass
