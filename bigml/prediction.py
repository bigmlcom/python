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

"""class for the Tree Prediction object

This module defines an auxiliary Prediction object that is used in the
Tree module to store all the available prediction info.
"""

class Prediction(object):
    """A Prediction object containing the predicted Node info or the
       subtree grouped prediction info for proportional missing strategy

    """
    def __init__(self, output, path, confidence,
                 distribution=None, count=None, distribution_unit=None,
                 median=None, children=None, d_max=None, d_min=None):
        self.output = output
        self.path = path
        self.confidence = confidence
        self.distribution = [] if distribution is None else distribution
        self.count = (sum([instances for _, instances in self.distribution])
                      if count is None else count)
        self.distribution_unit = ('categorical' if distribution_unit is None
                                  else distribution_unit)
        self.median = median
        self.children = [] if children is None else children
        self.min = d_min
        self.max = d_max
