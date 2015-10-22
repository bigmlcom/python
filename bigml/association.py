# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015 BigML
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

"""A local Association Rules object.

This module defines an Association Rule object as extracted from a given
dataset. It shows the items discovered in the dataset and the association
rules between these items.

Example usage (assuming that you have previously set up the BIGML_USERNAME
and BIGML_API_KEY environment variables and that you own the association/id
below):

from bigml.api import BigML
from bigml.association import Association

api = BigML()

association = Association('association/5026966515526876630001b2')
association.rules()

"""
import logging
LOGGER = logging.getLogger('BigML')

import sys
import math
import re

from bigml.api import FINISHED
from bigml.api import (BigML, get_association_id, get_status)
from bigml.util import cast, utf8
from bigml.basemodel import retrieve_resource
from bigml.basemodel import ONLY_MODEL
from bigml.model import print_distribution
from bigml.model import STORAGE
from bigml.modelfields import ModelFields
from bigml.associationrule import AssociationRule
from bigml.item import Item
from bigml.io import UnicodeWriter


RULE_HEADERS = ["leverage", "lhs_cover", "lhs_desc", "p_value", "rhs_cover",
                "rhs_desc", "strength", "support"]


class Association(ModelFields):
    """ A lightweight wrapper around an Association rules object.

    Uses a BigML remote association resource to build a local version
    that can be used to extract associations information.

    """

    def __init__(self, association, api=None):

        self.resource_id = None
        self.complement = None
        self.discretization = {}
        self.field_discretizations = {}
        self.items = []
        self.k = None
        self.max_lhs = None
        self.min_coverage = None
        self.min_leverage = None
        self.min_strength = None
        self.min_support = None
        self.rules = []
        self.significance_level = None

        if not (isinstance(association, dict) and 'resource' in association and
                association['resource'] is not None):
            if api is None:
                api = BigML(storage=STORAGE)
            self.resource_id = get_association_id(association)
            if self.resource_id is None:
                raise Exception(api.error_message(association,
                                                  resource_type='association',
                                                  method='get'))
            query_string = ONLY_MODEL
            association = retrieve_resource(api, self.resource_id,
                                            query_string=query_string)
        else:
            self.resource_id = get_association_id(association)
        if 'object' in association and isinstance(association['object'], dict):
            association = association['object']

        if 'associations' in association and \
                isinstance(association['associations'], dict):
            status = get_status(association)
            if 'code' in status and status['code'] == FINISHED:
                associations = association['associations']
                fields = associations['fields']
                ModelFields.__init__(self, fields)
                self.complement = associations.get('complement', False)
                self.discretization = associations.get('discretization', {})
                self.field_discretizations = associations.get(
                    'field_discretizations', {})
                self.items = [Item(index, item) for index, item in
                              enumerate(associations['items'])]
                self.k = associations.get('k', 100)
                self.max_lhs = associations.get('max_lhs', 4)
                self.min_coverage = associations.get('min_coverage', 0)
                self.min_leverage = associations.get('min_leverage', -1)
                self.min_strength = associations.get('min_strength', 0)
                self.min_support = associations.get('min_support', 0)
                self.rules = [AssociationRule(rule) for rule in
                              associations['rules']]
                self.significance_level = associations.get(
                    'significance_level', 0.05)
            else:
                raise Exception("The association isn't finished yet")
        else:
            raise Exception("Cannot create the Association instance. Could not"
                            " find the 'associations' key in the "
                            "resource:\n\n%s" %
                            association)

    def get_items(self, field=None, names=None, filter_function=None,
                  out_format=None):
        """Returns the items array, previously selected by the field
           corresponding to the given field name or a user-defined function
           (if set)

        """
        items = []
        if field:
            if field in self.fields:
                field_id = field
            elif field in self.inverted_fields:
                field_id = self.inverted_fields[field]
            else:
                raise ValueError("Failed to find a field name or ID"
                                 " corresponding to %s." % field)

        def filter_function_set(item):
            """Checking filter function if set

            """
            if filter_function is None:
                return True
            return filter_function(item)

        def field_filter(item):
            """Checking if an item is associated to a fieldInfo

            """
            if field is None:
                return True
            return item.field_id == field_id

        def names_filter(item):
            """Checking if an item by name

            """
            if names is None:
                return True
            return item.name in names

        for item in self.items:
            new_item = item.out_format(
                language=out_format, fields=self.fields) \
                if out_format else item
            if all([field_filter(item), names_filter(item),
                    filter_function_set(item)]):
                items.append(new_item)

        return items

    def get_rules(self, min_leverage=None, min_strength=None,
                  min_support=None, min_p_value=None, item_list=None,
                  filter_function=None, out_format="JSON"):
        """Returns the rules array, previously selected by the leverage,
           strength, support or a user-defined filter function (if set)

           @param float min_leverage   Minum leverage value
           @param float min_strength   Minum strength value
           @param float min_support   Minum support value
           @param float min_p_value   Minum p_value value
           @param List item_list   List of Item objects. Any of them should be
                                   in the rules
           @param function filter_function   Function used as filter
           @param string out_format   Output format for the rules: JSON or CSV
        """
        def leverage(rule):
            """Check minimum leverage

            """
            if min_leverage is None:
                return True
            return rule.leverage >= min_leverage

        def strength(rule):
            """Check minimum strength

            """
            if min_strength is None:
                return True
            return rule.strength >= min_strength

        def support(rule):
            """Check minimum support

            """
            if min_support is None:
                return True
            return rule.support >= min_support

        def p_value(rule):
            """Check minimum p_value

            """
            if min_p_value is None:
                return True
            return rule.p_value >= min_p_value

        def filter_function_set(rule):
            """Checking filter function if set

            """
            if filter_function is None:
                return True
            return filter_function(rule)

        def item_list_set(rule):
            """Checking if any of the items list is in a rule

            """
            if item_list is None:
                return True
            if isinstance(item_list[0], Item):
                items = [item.index for item in item_list]
            elif isinstance(item_list[0], basestring):
                items = [item.index for item
                         in self.get_items(names=item_list)]

            for item_index in rule.lhs:
                if item_index in items:
                    return True
            for item_index in rule.rhs:
                if item_index in items:
                    return True
            return False

        rules = []
        for rule in self.rules:
            new_rule = rule.out_format(language=out_format) if out_format \
                else rule
            if all([leverage(rule), strength(rule), support(rule),
                    p_value(rule), item_list_set(rule),
                    filter_function_set(rule)]):
                rules.append(new_rule)

        return rules

    def rules_CSV(self, file_name, **kwargs):
        """Stores the rules in CSV format in the user-given file. The rules
           can be previously selected using the arguments in get_rules

        """
        kwargs.update({"out_format": "CSV"})
        rules = self.get_rules(**kwargs)
        if file_name is None:
            raise ValueError("A valid file name is required to store the "
                             "rules.")
        with UnicodeWriter(file_name) as writer:
            writer.writerow(RULE_HEADERS)
            for rule in rules:
                writer.writerow([item if not isinstance(item, basestring)
                                 else item.encode("utf-8")
                                 for item in rule])
