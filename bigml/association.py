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


RULE_HEADERS = ["Antecedents", "Consequent", "Confidence", "Leverage",
                "P_value", "Antecedents coverage",
                "Consequent coverage", "Lift", "Support"]

ASSOCIATION_METRICS = ["confidence", "support", "leverage", "lhs_cover",
                       "rhs_cover", "p_value", "lift"]
INDENT = " " * 4


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
                self.items = [Item(index, item, fields) for index, item in
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

    def get_items(self, field=None, names=None, filter_function=None):
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
            if all([field_filter(item), names_filter(item),
                    filter_function_set(item)]):
                items.append(item)

        return items

    def get_rules(self, min_leverage=None, min_strength=None,
                  min_support=None, min_p_value=None, item_list=None,
                  filter_function=None):
        """Returns the rules array, previously selected by the leverage,
           strength, support or a user-defined filter function (if set)

           @param float min_leverage   Minum leverage value
           @param float min_strength   Minum strength value
           @param float min_support   Minum support value
           @param float min_p_value   Minum p_value value
           @param List item_list   List of Item objects. Any of them should be
                                   in the rules
           @param function filter_function   Function used as filter
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
            if all([leverage(rule), strength(rule), support(rule),
                    p_value(rule), item_list_set(rule),
                    filter_function_set(rule)]):
                rules.append(rule)

        return rules

    def rules_CSV(self, file_name, **kwargs):
        """Stores the rules in CSV format in the user-given file. The rules
           can be previously selected using the arguments in get_rules

        """
        rules = self.get_rules(**kwargs)
        rules = [self.describe(rule.to_CSV()) for rule in rules]
        if file_name is None:
            raise ValueError("A valid file name is required to store the "
                             "rules.")
        with UnicodeWriter(file_name) as writer:
            writer.writerow(RULE_HEADERS)
            for rule in rules:
                writer.writerow([item if not isinstance(item, basestring)
                                 else item.encode("utf-8")
                                 for item in rule])

    def describe(self, rule_row):
        """Transforms the lhs and rhs index information to a human-readable
           rule text.

        """
        # lhs items  and rhs items substitution by description
        for index in range(2):
            description = []
            for item_index in rule_row[index]:
                item = self.items[item_index]
                # if there's just one field, we don't use the item description
                # to avoid repeating the field name constantly.
                item_description = item.name if len(self.fields.keys()) == 1 \
                    and not item.complement else item.describe()
                description.append(item_description)
            description = " & ".join(description)
            rule_row[index] = description
        return rule_row

    def summarize(self, out=sys.stdout, **kwargs):
        """Prints a summary of the obtained rules

        """
        # groups the rules by its rhs items:
        rules = self.get_rules(**kwargs)
        groups = {}

        for rule in rules:
            consequent = tuple(rule.rhs)
            if not consequent in groups:
                groups[consequent] = {"rules": []}
            groups[consequent]["rules"].append(rule)
        # aggregators
        for consequent, info in groups.items():
            number_of_rules = len(info['rules'])
            groups[consequent]["number_of_rules"] = number_of_rules
            for metric in ASSOCIATION_METRICS:
                groups[consequent]["max_%s" % metric] = float('-Inf')
                groups[consequent]["min_%s" % metric] = float('Inf')
                groups[consequent]["mean_%s" % metric] = 0
            for rule in info["rules"]:
                for metric in ASSOCIATION_METRICS:
                    metric_value = getattr(rule, metric)
                    if metric_value > groups[consequent]["max_%s" % metric]:
                        groups[consequent]["max_%s" % metric] = metric_value
                    if metric_value < groups[consequent]["min_%s" % metric]:
                        groups[consequent]["min_%s" % metric] = metric_value
                    groups[consequent]["mean_%s" % metric] += metric_value
            for metric in ASSOCIATION_METRICS:
                groups[consequent]["mean_%s" % metric] = \
                    groups[consequent]["mean_%s" % metric] / \
                    float(number_of_rules)
        number_of_consequents = len(groups.keys())

        total = {"rules": rules, "number_of_rules": len(rules)}
        for metric in ASSOCIATION_METRICS:
            total["max_%s" % metric] = float('-Inf')
            total["min_%s" % metric] = float('Inf')
            total["mean_%s" % metric] = 0
            for consequent, info in groups.items():
                if groups[consequent]["max_%s" % metric] > \
                        total["max_%s" % metric]:
                    total["max_%s" % metric] = \
                        groups[consequent]["max_%s" % metric]
                if groups[consequent]["min_%s" % metric] < \
                        total["min_%s" % metric]:
                    total["min_%s" % metric] = \
                        groups[consequent]["min_%s" % metric]
                total["mean_%s" % metric] += \
                    groups[consequent]["mean_%s" % metric]
        for metric in ASSOCIATION_METRICS:
            total["mean_%s" % metric] = total["mean_%s" % metric] / \
                float(number_of_consequents)

        print "Total number of rules: %s\n" % total["number_of_rules"]
        for metric in ASSOCIATION_METRICS:
            print "%s%s <= %s <= %s (mean: %s)" % (
                INDENT, total["max_%s" % metric], metric,
                total["min_%s" % metric], total["mean_%s" % metric])
        print "\n\nPer consequent:\n"

        for consequent, info in sorted(groups.items(),
                                       key=lambda x: x[1]["max_confidence"]):
            print "%s%s: %s rules\n" % \
                (INDENT, self.items[consequent[0]].describe(),
                 info["number_of_rules"])
            for metric in ASSOCIATION_METRICS:
                if info["max_%s" % metric] > info["min_%s" % metric]:
                    print "%s%s <= %s <= %s (mean: %s)" % (
                        INDENT * 2, info["max_%s" % metric], metric,
                        info["min_%s" % metric], info["mean_%s" % metric])
                else:
                    print "%s%s = %s (mean: %s)" % (
                        INDENT * 2, metric,
                        info["min_%s" % metric], info["mean_%s" % metric])

            print "\n\n"

    def summarize_items(self, out=sys.stdout, **kwargs):
        """Prints a summary of the obtained rules

        """
        # groups the rules by its rhs items:
        rules = self.get_rules(**kwargs)
        groups = {}

        for rule in rules:
            consequent = set(rule.rhs)
            antecedent = set(rule.lhs)
            items = antecedent.union(consequent)
            for item_index in items:
                if not (item_index,) in groups:
                    groups[(item_index,)] = {"rules": []}
                groups[(item_index,)]["rules"].append(rule)
        """
        # aggregators
        for consequent, info in groups.items():
            number_of_rules = len(info['rules'])
            groups[consequent]["number_of_rules"] = number_of_rules
            for metric in ASSOCIATION_METRICS:
                groups[consequent]["max_%s" % metric] = float('-Inf')
                groups[consequent]["min_%s" % metric] = float('Inf')
                groups[consequent]["mean_%s" % metric] = 0
            for rule in info["rules"]:
                for metric in ASSOCIATION_METRICS:
                    metric_value = getattr(rule, metric)
                    if metric_value > groups[consequent]["max_%s" % metric]:
                        groups[consequent]["max_%s" % metric] = metric_value
                    if metric_value < groups[consequent]["min_%s" % metric]:
                        groups[consequent]["min_%s" % metric] = metric_value
                    groups[consequent]["mean_%s" % metric] += metric_value
            for metric in ASSOCIATION_METRICS:
                groups[consequent]["mean_%s" % metric] = \
                    groups[consequent]["mean_%s" % metric] / \
                    float(number_of_rules)
        number_of_consequents = len(groups.keys())
        """
        total = {"rules": rules, "number_of_rules": len(rules)}
        """
        for metric in ASSOCIATION_METRICS:
            total["max_%s" % metric] = float('-Inf')
            total["min_%s" % metric] = float('Inf')
            total["mean_%s" % metric] = 0
            for consequent, info in groups.items():
                if groups[consequent]["max_%s" % metric] > \
                        total["max_%s" % metric]:
                    total["max_%s" % metric] = \
                        groups[consequent]["max_%s" % metric]
                if groups[consequent]["min_%s" % metric] < \
                        total["min_%s" % metric]:
                    total["min_%s" % metric] = \
                        groups[consequent]["min_%s" % metric]
                total["mean_%s" % metric] += \
                    groups[consequent]["mean_%s" % metric]
        for metric in ASSOCIATION_METRICS:
            total["mean_%s" % metric] = total["mean_%s" % metric] / \
                float(number_of_consequents)
        """
        print "Total number of rules: %s\n" % total["number_of_rules"]

        print "\n\nPer item:\n"

        for (item_index,), info in groups.items():
            print "%s%s: %s rules\n" % \
                (INDENT, self.items[item_index].describe(),
                 len(info["rules"]))
            for rule in info["rules"]:
                rule_row = self.describe(rule.to_CSV())
                print "%s%s -> %s" % (INDENT * 2, rule_row[0], rule_row[1])
            print "\n\n"
