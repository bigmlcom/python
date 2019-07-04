# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015-2019 BigML
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

import sys
import math
import logging
import csv


from bigml.api import FINISHED
from bigml.api import get_status
from bigml.basemodel import get_resource_dict
from bigml.modelfields import ModelFields
from bigml.associationrule import AssociationRule
from bigml.item import Item
from bigml.io import UnicodeWriter


LOGGER = logging.getLogger('BigML')

RULE_HEADERS = ["Rule ID", "Antecedent", "Consequent", "Antecedent Coverage %",
                "Antecedent Coverage", "Support %", "Support", "Confidence",
                "Leverage", "Lift", "p-value", "Consequent Coverage %",
                "Consequent Coverage"]

ASSOCIATION_METRICS = ["lhs_cover", "support", "confidence",
                       "leverage", "lift", "p_value"]

SCORES = ASSOCIATION_METRICS[:-1]

METRIC_LITERALS = {"confidence": "Confidence", "support": "Support",
                   "leverage": "Leverage", "lhs_cover": "Coverage",
                   "p_value": "p-value", "lift": "Lift"}

INDENT = " " * 4

DEFAULT_K = 100
DEFAULT_SEARCH_STRATEGY = "leverage"


NO_ITEMS = ['numeric', 'categorical']


def get_metric_string(rule, reverse=False):
    """Returns the string that describes the values of metrics for a rule.

    """
    metric_values = []
    for metric in ASSOCIATION_METRICS:
        if reverse and metric == 'lhs_cover':
            metric_key = 'rhs_cover'
        else:
            metric_key = metric
        metric_value = getattr(rule, metric_key)
        if isinstance(metric_value, list):
            metric_values.append("%s=%.2f%% (%s)" % (
                METRIC_LITERALS[metric], ((round(metric_value[0], 4) * 100)), \
                metric_value[1]))
        elif metric == 'confidence':
            metric_values.append("%s=%.2f%%" % (
                METRIC_LITERALS[metric], ((round(metric_value, 4) * 100))))
        else:
            metric_values.append("%s=%s" % (
                METRIC_LITERALS[metric], metric_value))
    return "; ".join(metric_values)


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
        self.max_k = None
        self.max_lhs = None
        self.min_confidence = None
        self.min_leverage = None
        self.min_support = None
        self.min_lift = None
        self.search_strategy = DEFAULT_SEARCH_STRATEGY
        self.rules = []
        self.significance_level = None

        self.resource_id, association = get_resource_dict( \
            association, "association", api=api)

        if 'object' in association and isinstance(association['object'], dict):
            association = association['object']

        if 'associations' in association and \
                isinstance(association['associations'], dict):
            status = get_status(association)
            if 'code' in status and status['code'] == FINISHED:
                self.input_fields = association['input_fields']
                associations = association['associations']
                fields = associations['fields']
                ModelFields.__init__( \
                    self, fields, \
                    missing_tokens=associations.get('missing_tokens'))
                self.complement = associations.get('complement', False)
                self.discretization = associations.get('discretization', {})
                self.field_discretizations = associations.get(
                    'field_discretizations', {})
                self.items = [Item(index, item, fields) for index, item in
                              enumerate(associations.get('items', []))]
                self.max_k = associations.get('max_k', 100)
                self.max_lhs = associations.get('max_lhs', 4)
                self.min_confidence = associations.get('min_confidence', 0)
                self.min_leverage = associations.get('min_leverage', -1)
                self.min_support = associations.get('min_support', 0)
                self.min_lift = associations.get('min_lift', 0)
                self.search_strategy = associations.get('search_strategy', \
                    DEFAULT_SEARCH_STRATEGY)
                self.rules = [AssociationRule(rule) for rule in
                              associations.get('rules', [])]
                self.significance_level = associations.get(
                    'significance_level', 0.05)
            else:
                raise Exception("The association isn't finished yet")
        else:
            raise Exception("Cannot create the Association instance. Could not"
                            " find the 'associations' key in the "
                            "resource:\n\n%s" %
                            association)

    def association_set(self, input_data,
                        k=DEFAULT_K, score_by=None):
        """Returns the Consequents for the rules whose LHS best match
           the provided items. Cosine similarity is used to score the match.

            @param inputs dict map of input data: e.g.
                               {"petal length": 4.4,
                                "sepal length": 5.1,
                                "petal width": 1.3,
                                "sepal width": 2.1,
                                "species": "Iris-versicolor"}
            @param k integer Maximum number of item predictions to return
                             (Default 100)
            @param max_rules integer Maximum number of rules to return per item
            @param score_by Code for the metric used in scoring
                            (default search_strategy)
                leverage
                confidence
                support
                lhs-cover
                lift

        """
        predictions = {}
        if score_by and score_by not in SCORES:
            raise ValueError("The available values of score_by are: %s" %
                             ", ".join(SCORES))
        input_data = self.filter_input_data(input_data)
        # retrieving the items in input_data
        items_indexes = [item.index for item in
                         self.get_items(input_map=input_data)]
        if score_by is None:
            score_by = self.search_strategy

        for rule in self.rules:
            # checking that the field in the rhs is not in the input data
            field_type = self.fields[self.items[rule.rhs[0]].field_id][ \
                'optype']
            # if the rhs corresponds to a non-itemized field and this field
            # is already in input_data, don't add rhs
            if field_type in NO_ITEMS and self.items[rule.rhs[0]].field_id in \
                    input_data:
                continue
            # if an itemized content is in input_data, don't add it to the
            # prediction
            if field_type not in NO_ITEMS and rule.rhs[0] in items_indexes:
                continue
            cosine = sum([1 for index in items_indexes \
                if index in rule.lhs])
            if cosine > 0:
                cosine = cosine / float(math.sqrt(len(items_indexes)) * \
                                        math.sqrt(len(rule.lhs)))

                rhs = tuple(rule.rhs)
                if rhs not in predictions:
                    predictions[rhs] = {"score": 0}
                predictions[rhs]["score"] += cosine * getattr(
                    rule, score_by)
                if not "rules" in predictions[rhs]:
                    predictions[rhs]["rules"] = []
                predictions[rhs]["rules"].append(rule.rule_id)
        # choose the best k predictions
        k = len(predictions.keys()) if k is None else k
        predictions = sorted(predictions.items(),
                             key=lambda x: x[1]["score"], reverse=True)[:k]
        final_predictions = []
        for rhs, prediction in predictions:
            prediction["item"] = self.items[rhs[0]].to_json()
            # adapting to association_set item format
            for key in ["description", "bin_start", "bin_end"]:
                del prediction["item"][key]
            final_predictions.append(prediction)
        return final_predictions

    def get_items(self, field=None,
                  names=None, input_map=None, filter_function=None):
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

        def input_map_filter(item):
            """ Checking if an item is in the input map

            """
            if input_map is None:
                return True
            value = input_map.get(item.field_id)
            return item.matches(value)

        for item in self.items:
            if all([field_filter(item), names_filter(item),
                    input_map_filter(item),
                    filter_function_set(item)]):
                items.append(item)

        return items

    def get_rules(self, min_leverage=None, min_confidence=None,
                  min_support=None, min_p_value=None, item_list=None,
                  filter_function=None):
        """Returns the rules array, previously selected by the leverage,
           confidence, support or a user-defined filter function (if set)

           @param float min_leverage   Minum leverage value
           @param float min_confidence   Minum confidence value
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

        def confidence(rule):
            """Check minimum confidence

            """
            if min_confidence is None:
                return True
            return rule.confidence >= min_confidence

        def support(rule):
            """Check minimum support

            """
            if min_support is None:
                return True
            for rhs_support, _ in rule.support:
                if rhs_support >= min_support:
                    return True
            return False

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
            if all([leverage(rule), confidence(rule), support(rule),
                    p_value(rule), item_list_set(rule),
                    filter_function_set(rule)]):
                rules.append(rule)

        return rules

    def rules_csv(self, file_name, **kwargs):
        """Stores the rules in CSV format in the user-given file. The rules
           can be previously selected using the arguments in get_rules

        """
        rules = self.get_rules(**kwargs)
        rules = [self.describe(rule.to_csv()) for rule in rules]
        if file_name is None:
            raise ValueError("A valid file name is required to store the "
                             "rules.")
        with UnicodeWriter(file_name, quoting=csv.QUOTE_NONNUMERIC) as writer:
            writer.writerow(RULE_HEADERS)
            for rule in rules:
                writer.writerow([item if not isinstance(item, basestring)
                                 else item.encode("utf-8")
                                 for item in rule])

    def describe(self, rule_row):
        """Transforms the lhs and rhs index information to a human-readable
           rule text.

        """
        # lhs items  and rhs items (second and third element in the row)
        # substitution by description
        for index in range(1, 3):
            description = []
            for item_index in rule_row[index]:
                item = self.items[item_index]
                # if there's just one field, we don't use the item description
                # to avoid repeating the field name constantly.
                item_description = item.name if len(self.fields.keys()) == 1 \
                    and not item.complement else item.describe()
                description.append(item_description)
            description_str = " & ".join(description)
            rule_row[index] = description_str
        return rule_row

    def summarize(self, out=sys.stdout, limit=10, **kwargs):
        """Prints a summary of the obtained rules

        """
        # groups the rules by its metrics
        rules = self.get_rules(**kwargs)
        out.write("Total number of rules: %s\n" % len(rules))
        for metric in ASSOCIATION_METRICS:
            out.write("\n\nTop %s by %s:\n\n" % (
                limit, METRIC_LITERALS[metric]))
            top_rules = sorted(rules, key=lambda x: getattr(x, metric),
                               reverse=True)[0: limit * 2]
            out_rules = []
            ref_rules = []
            counter = 0
            for rule in top_rules:
                rule_row = self.describe(rule.to_csv())
                metric_string = get_metric_string(rule)
                operator = "->"
                rule_id_string = "Rule %s: " % rule.rule_id
                for item in top_rules:
                    if rule.rhs == item.lhs and rule.lhs == item.rhs and \
                            metric_string == get_metric_string(
                                    item, reverse=True):
                        rule_id_string = "Rules %s, %s: " % (rule.rule_id,
                                                             item.rule_id)
                        operator = "<->"
                out_rule = "%s %s %s [%s]" % (
                    rule_row[1], operator, rule_row[2],
                    metric_string)
                reverse_rule = "%s %s %s [%s]" % (
                    rule_row[2], operator, rule_row[1],
                    metric_string)
                if operator == "->" or reverse_rule not in ref_rules:
                    ref_rules.append(out_rule)
                    out_rule = "%s%s%s" % (INDENT * 2,
                                           rule_id_string, out_rule)

                    out_rules.append(out_rule)
                    counter += 1
                    if counter > limit:
                        break
            out.write("\n".join(out_rules))
        out.write("\n")
