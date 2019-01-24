# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2014-2019 BigML
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

"""Predicates structure for the BigML local AnomalyTree

This module defines an auxiliary Predicates structure that is used in the
AnomalyTree to save the node's predicates info.

"""
from bigml.predicate import Predicate

class Predicates(object):
    """A list of predicates to be evaluated in an anomaly tree's node.

    """
    def __init__(self, predicates_list):
        self.predicates = []
        for predicate in predicates_list:
            if predicate is True:
                self.predicates.append(True)
            else:
                self.predicates.append(
                    Predicate(predicate.get('op'),
                              predicate.get('field'),
                              predicate.get('value'),
                              predicate.get('term')))

    def to_rule(self, fields, label='name'):
        """ Builds rule string from a predicates list

        """
        return " and ".join([predicate.to_rule(fields, label=label) for
                             predicate in self.predicates
                             if not isinstance(predicate, bool)])

    def apply(self, input_data, fields):
        """ Applies the operators defined in each of the predicates to
            the provided input data

        """

        return all([predicate.apply(input_data, fields) for
                    predicate in self.predicates
                    if isinstance(predicate, Predicate)])
