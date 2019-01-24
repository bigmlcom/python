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

"""Path structure based on Predicates for the BigML local Model

This module defines an auxiliary Path structure that is used
to store the predicates' info.

"""
from bigml.predicate import Predicate


EXTENDED = 0
BRIEF = 1
NUMERIC = 'numeric'
CATEGORICAL = 'categorical'
TEXT = 'text'
DATETIME = 'datetime'
ITEMS = 'items'

REVERSE_OP = {'<': '>', '>': '<'}


def reverse(operator):
    """Reverses the unequality operators

    """
    return "%s%s" % (REVERSE_OP[operator[0]], operator[1:])


def merge_rules(list_of_predicates, fields, label='name'):
    """Summarizes the predicates referring to the same field

    """
    if list_of_predicates:
        field_id = list_of_predicates[0].field
        field_type = fields[field_id]['optype']
        missing_flag = None
        name = fields[field_id][label]
        last_predicate = list_of_predicates[-1]
        # if the last predicate is "is missing" forget about the rest
        if last_predicate.operator == "=" and last_predicate.value is None:
            return u"%s is missing" % name
        # if the last predicate is "is not missing"
        if last_predicate.operator[0] in ["!", "/"] and \
            last_predicate.value is None:
            if len(list_of_predicates) == 1:
                # if there's only one predicate, then write "is not missing"
                return u"%s is not missing" % name
            list_of_predicates = list_of_predicates[0: -1]
            missing_flag = False
        if last_predicate.missing:
            missing_flag = True

        if field_type == NUMERIC:
            return merge_numeric_rules( \
                list_of_predicates, fields, label=label,
                missing_flag=missing_flag)

        if field_type == TEXT:
            return merge_text_rules( \
                list_of_predicates, fields, label=label)

        if field_type == CATEGORICAL:
            return merge_categorical_rules( \
                list_of_predicates, fields, label=label,
                missing_flag=missing_flag)

        return " and ".join(
            [predicate.to_rule(fields, label=label).strip() for
             predicate in list_of_predicates])


def merge_numeric_rules(list_of_predicates, fields, label='name',
                        missing_flag=None):
    """ Summarizes the numeric predicates for the same field

    """
    minor = (None, float('-inf'))
    major = (None, float('inf'))
    equal = None

    for predicate in list_of_predicates:
        if (predicate.operator.startswith('>') and
                predicate.value > minor[1]):
            minor = (predicate, predicate.value)
        if (predicate.operator.startswith('<') and
                predicate.value < major[1]):
            major = (predicate, predicate.value)
        if predicate.operator[0] in ['!', '=', '/', 'i']:
            equal = predicate
            break
    if equal is not None:
        return equal.to_rule(fields, label=label, missing=missing_flag)
    rule = u''
    field_id = list_of_predicates[0].field
    name = fields[field_id][label]

    if minor[0] is not None and major[0] is not None:
        predicate, value = minor
        rule = u"%s %s " % (value, reverse(predicate.operator))
        rule += name
        predicate, value = major
        rule += u" %s %s " % (predicate.operator, value)
        if missing_flag:
            rule += u" or missing"
    else:
        predicate = minor[0] if minor[0] is not None else major[0]
        rule = predicate.to_rule(fields, label=label, missing=missing_flag)
    return rule


def merge_text_rules(list_of_predicates, fields, label='name'):
    """ Summarizes the text predicates for the same field

    """
    contains = []
    not_contains = []
    for predicate in list_of_predicates:
        if ((predicate.operator == '<' and predicate.value <= 1) or
                (predicate.operator == '<=' and predicate.value == 0)):
            not_contains.append(predicate)
        else:
            contains.append(predicate)
    rules = []
    rules_not = []
    if contains:
        rules.append(contains[0].to_rule(fields, label=label).strip())
        for predicate in contains[1:]:
            if predicate.term not in rules:
                rules.append(predicate.term)
    rule = u" and ".join(rules)
    if not_contains:
        if not rules:
            rules_not.append(
                not_contains[0].to_rule(fields, label=label).strip())
        else:
            rules_not.append(
                " and %s" % \
                not_contains[0].to_rule(fields, label=label).strip())
        for predicate in not_contains[1:]:
            if predicate.term not in rules_not:
                rules_not.append(predicate.term)
    rule += u" or ".join(rules_not)
    return rule


def  merge_categorical_rules(list_of_predicates,
                             fields, label='name', missing_flag=None):
    """ Summarizes the categorical predicates for the same field

    """
    equal = []
    not_equal = []

    for predicate in list_of_predicates:
        if predicate.operator.startswith("!"):
            not_equal.append(predicate)
        else:
            equal.append(predicate)
    rules = []
    rules_not = []
    if equal:
        rules.append(equal[0].to_rule( \
            fields, label=label, missing=False).strip())
        for predicate in equal[1:]:
            if not predicate.value in rules:
                rules.append(predicate.value)
    rule = u" and ".join(rules)
    if not_equal and not rules:
        rules_not.append(not_equal[0].to_rule( \
            fields, label=label, missing=False).strip())
        for predicate in not_equal[1:]:
            if predicate.value not in rules_not:
                rules_not.append(predicate.value)
    if rules_not:
        connector = u" and " if rule else u""
        rule += connector + u" or ".join(rules_not)
    if missing_flag:
        rule += u" or missing"
    return rule


class Path(object):
    """A Path as a list of Predicates

    """
    def __init__(self, predicates=None):
        """ Path instance constructor accepts only lists of Predicate objects

        """
        if not predicates:
            self.predicates = []
        elif isinstance(predicates, list) and \
                isinstance(predicates[0], Predicate):
            self.predicates = predicates
        else:
            raise ValueError("The Path constructor accepts a list of Predicate"
                             " objects. Please check the arguments for the"
                             " constructor.")


    def to_rules(self, fields, label='name', format=EXTENDED):
        """ Builds rules string from a list lf predicates in different formats

        """
        if format == EXTENDED:
            return self.to_extended_rules(fields, label=label)
        elif format == BRIEF:
            return self.to_brief_rules(fields, label=label)
        else:
            raise ValueError("Invalid format. The list of valid formats are 0 "
                             "(extended) or 1 (brief).")


    def to_extended_rules(self, fields, label='name'):
        """ Builds rules string in ordered and extended format

        """
        list_of_rules = []
        for predicate in self.predicates:
            list_of_rules.append(
                predicate.to_rule(fields, label=label).strip())
        return " and ".join(list_of_rules)

    def to_brief_rules(self, fields, label='name'):
        """ Builds rules string in brief format (grouped and unordered)

        """
        groups_of_rules = {}
        list_of_fields = []
        for predicate in self.predicates:
            if predicate.field not in groups_of_rules:
                groups_of_rules[predicate.field] = []
                list_of_fields.append(predicate.field)
            groups_of_rules[predicate.field].append(predicate)

        lines = []
        for field in list_of_fields:
            lines.append(
                merge_rules(groups_of_rules[field],
                            fields, label=label))
        return " and ".join(lines)

    def append(self, predicate):
        """ Adds new predicate to the path

        """
        self.predicates.append(predicate)
