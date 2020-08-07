# -*- coding: utf-8 -*-
#
# Copyright 2013-2020 BigML
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

"""Predicate structure for the BigML local Model
This module defines an auxiliary Predicate structure that is used in the Tree
to save the node's predicate info.
"""

import re

from bigml.predicate_utils.utils import TM_TOKENS, TM_FULL_TERM, TM_ALL, \
    FULL_TERM_PATTERN, OPERATOR_CODE
from bigml.predicate_utils.utils import apply_predicate, term_matches, \
    item_matches
from bigml.util import plural

RELATIONS = {
    '<=': 'no more than %s %s',
    '>=': '%s %s at most',
    '>': 'more than %s %s',
    '<': 'less than %s %s'
}

class Predicate(object):
    """A predicate to be evaluated in a tree's node.
    """
    def __init__(self, operation, field, value, term=None):
        self.operator = operation
        self.missing = False

        if self.operator.endswith("*"):
            self.operator = self.operator[0: -1]
            self.missing = True
        elif operation == 'in' and None in value:
            self.missing = True

        self.field = field
        self.value = value
        self.term = term

    def is_full_term(self, fields):
        """Returns a boolean showing if a term is considered as a full_term
        """
        if self.term is not None:
            # new optype has to be handled in tokens
            if fields[self.field]['optype'] == 'items':
                return False
            options = fields[self.field]['term_analysis']
            token_mode = options.get('token_mode', TM_TOKENS)
            if token_mode == TM_FULL_TERM:
                return True
            if token_mode == TM_ALL:
                return re.match(FULL_TERM_PATTERN, self.term)
        return False

    def to_rule(self, fields, label='name', missing=None):
        """Builds rule string from a predicate
        """
        # externally forcing missing to True or False depending on the path
        if missing is None:
            missing = self.missing
        if label is not None:
            name = fields[self.field][label]
        else:
            name = ""
        full_term = self.is_full_term(fields)
        relation_missing = " or missing" if missing else ""
        if self.term is not None:
            relation_suffix = ''
            if ((self.operator == '<' and self.value <= 1) or
                    (self.operator == '<=' and self.value == 0)):
                relation_literal = ('is not equal to' if full_term
                                    else 'does not contain')
            else:
                relation_literal = 'is equal to' if full_term else 'contains'
                if not full_term:
                    if self.operator != '>' or self.value != 0:
                        relation_suffix = (RELATIONS[self.operator] %
                                           (self.value,
                                            plural('time', self.value)))
            return "%s %s %s %s%s" % (name, relation_literal,
                                       self.term, relation_suffix,
                                       relation_missing)
        if self.value is None:
            return "%s %s" % (name,
                               "is missing" if self.operator == '='
                               else "is not missing")
        return "%s %s %s%s" % (name,
                                self.operator,
                                self.value,
                                relation_missing)

    def to_LISP_rule(self, fields):
        """To be deprecated. See to_lisp_rule
        """
        self.to_lisp_rule(fields)

    def to_lisp_rule(self, fields):
        """Builds rule string in LISP from a predicate
        """
        if self.term is not None:
            if fields[self.field]['optype'] == 'text':
                options = fields[self.field]['term_analysis']
                case_insensitive = not options.get('case_sensitive', False)
                case_insensitive = 'true' if case_insensitive else 'false'
                language = options.get('language')
                language = "" if language is None else " %s" % language
                return "(%s (occurrences (f %s) %s %s%s) %s)" % (
                    self.operator, self.field, self.term,
                    case_insensitive, language, self.value)
            elif fields[self.field]['optype'] == 'items':
                return "(%s (if (contains-items? %s %s) 1 0) %s)" % (
                    self.operator, self.field, self.term,
                    self.value)
        if self.value is None:
            negation = "" if self.operator == "=" else "not "
            return "(%s missing? %s)" % (negation, self.field)
        rule = "(%s (f %s) %s)" % (self.operator,
                                    self.field,
                                    self.value)
        if self.missing:
            rule = "(or (missing? %s) %s)" % (self.field, rule)
        return rule

    def apply(self, input_data, fields):
        """Applies the operators defined in the predicate as strings to
        the provided input data
        """

        return apply_predicate(OPERATOR_CODE.get(self.operator), self.field,
                               self.value, self.term, self.missing, input_data,
                               fields[self.field])
