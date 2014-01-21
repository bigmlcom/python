# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2013-2014 BigML
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

import operator
import re

from bigml.util import plural

# Map operator str to its corresponding function
OPERATOR = {
    "<": operator.lt,
    "<=": operator.le,
    "=": operator.eq,
    "!=": operator.ne,
    "/=": operator.ne,
    ">=": operator.ge,
    ">": operator.gt
}
TM_TOKENS = 'tokens_only'
TM_FULL_TERM = 'full_terms_only'
TM_ALL = 'all'
FULL_TERM_PATTERN = re.compile(r'^.+\b.+$', re.U)
RELATIONS = {
    '<=': 'no more than %s %s',
    '>=': '%s %s at most',
    '>': 'more than %s %s',
    '<': 'less than %s %s'
}


def term_matches(text, forms_list, options):
    """ Counts the number of occurences of the words in forms_list in the text

        The terms in forms_list can either be tokens or full terms. The
        matching for tokens is contains and for full terms is equals.
    """
    token_mode = options.get('token_mode', TM_TOKENS)
    case_sensitive = options.get('case_sensitive', False)
    first_term = forms_list[0]
    if token_mode == TM_FULL_TERM:
        return full_term_match(text, first_term, case_sensitive)
    # In token_mode='all' we will match full terms using equals and
    # tokens using contains
    if token_mode == TM_ALL and len(forms_list) == 1:
        if re.match(FULL_TERM_PATTERN, first_term):
            return full_term_match(text, first_term, case_sensitive)
    return term_matches_tokens(text, forms_list, case_sensitive)


def full_term_match(text, full_term, case_sensitive):
    """Counts the match for full terms according to the case_sensitive option

    """
    if not case_sensitive:
        text = text.lower()
        full_term = full_term.lower()
    return 1 if text == full_term else 0


def get_tokens_flags(case_sensitive):
    """Returns flags for regular expression matching depending on text analysis
       options

    """
    flags = re.U
    if not case_sensitive:
        flags = (re.I | flags)
    return flags


def term_matches_tokens(text, forms_list, case_sensitive):
    """ Counts the number of occurences of the words in forms_list in the text

    """
    flags = get_tokens_flags(case_sensitive)
    expression = ur'(\b|_)%s(\b|_)' % '(\\b|_)|(\\b|_)'.join(forms_list)
    pattern = re.compile(expression, flags=flags)
    matches = re.findall(pattern, text)
    return len(matches)


class Predicate(object):
    """A predicate to be evaluated in a tree's node.

    """
    def __init__(self, operation, field, value, term=None):
        self.operator = operation
        self.field = field
        self.value = value
        self.term = term

    def is_full_term(self, fields):
        """Returns a boolean showing if a term is considered as a full_term

        """
        if self.term is not None:
            options = fields[self.field]['term_analysis']
            token_mode = options.get('token_mode', TM_TOKENS)
            if token_mode == TM_FULL_TERM:
                return True
            if token_mode == TM_ALL:
                return re.match(FULL_TERM_PATTERN, self.term)
        return False

    def to_rule(self, fields, label='name'):
        """ Builds rule string from a predicate

        """
        name = fields[self.field][label]
        full_term = self.is_full_term(fields)
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
            return u"%s %s %s %s" % (name, relation_literal,
                                     self.term, relation_suffix)
        return u"%s %s %s" % (name,
                              self.operator,
                              self.value)

    def apply(self, input_data, fields):
        """ Applies the operators defined in the predicate as strings to
            the provided input data
        """
        if self.term is not None:
            all_forms = fields[self.field]['summary'].get('term_forms', {})
            term_forms = all_forms.get(self.term, [])
            terms = [self.term]
            terms.extend(term_forms)
            options = fields[self.field]['term_analysis']
            return apply(OPERATOR[self.operator],
                         [term_matches(input_data[self.field], terms, options),
                          self.value])
        return apply(OPERATOR[self.operator],
                     [input_data[self.field],
                      self.value])
