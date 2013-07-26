# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2013 BigML
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


def term_matches(text, forms_list, options):
    """ Counts the number of occurences of the words in forms_list in the text

    """
    count = 0
    # basic pattern that should be changed to the tokenizer behaviour
    flags = 0
    if not options.get('case_sensitive', False):
        flags = re.I
    pattern = re.compile(r'\b%s\b' % '\\b|\\b'.join(forms_list), flags=flags)
    matches = re.findall(pattern, text)
    if matches is not None:
        count = len(matches)
    return count


class Predicate(object):
    """A predicate to be evaluated in a tree's node.

    """
    def __init__(self, operation, field, value, term=None):
        self.operator = operation
        self.field = field
        self.value = value
        self.term = term

    def to_rule(self, fields, label='name'):
        """ Builds rule string from a predicate

        """
        name = fields[self.field][label]
        if self.term is not None:
            relation_suffix = ''
            if ((self.operator == '<' and self.value <= 1) or
                    (self.operator == '<=' and self.value == 0)):
                relation_literal = 'does not contain'
            else:
                relation_literal = 'contains'
                if self.operator == '<=':
                    relation_suffix = (
                        'no more than %s %s' %
                        (self.value, plural('time', self.value)))
                elif self.operator == '>=':
                    relation_suffix = (
                        '%s %s at most' %
                        (self.value, plural('time', self.value)))
                elif self.operator == '>' and self.value != 0:
                    relation_suffix = (
                        'more than %s %s' %
                        (self.value, plural('time', self.value)))
                elif self.operator == '<':
                    relation_suffix = (
                        'less than %s %s' %
                        (self.value, plural('time', self.value)))
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
