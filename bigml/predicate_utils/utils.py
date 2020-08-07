# -*- coding: utf-8 -*-
#
# Copyright 2020 BigML
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

"""
Common auxiliar functions to be used in the node predicate evaluation
"""
import operator
import re

# Operator Codes
LT = 0
LE = 1
EQ = 2
NE = 3
GE = 4
GT = 5
IN = 6

# Map operator string to its corresponding code
OPERATOR_CODE = {"<": LT,
                 "<=": LE,
                 "=": EQ,
                 "!=": NE,
                 "/=": NE,
                 ">=": GE,
                 ">": GT,
                 "in": IN}

# Map operator code to its corresponding function
OPERATOR = [operator.lt,
            operator.le,
            operator.eq,
            operator.ne,
            operator.ge,
            operator.gt,
            operator.contains]

TM_TOKENS = 'tokens_only'
TM_FULL_TERM = 'full_terms_only'
TM_ALL = 'all'
FULL_TERM_PATTERN = re.compile(r'^.+\b.+$', re.U)

OPERATION_OFFSET = 2
FIELD_OFFSET = 3
VALUE_OFFSET = 4
TERM_OFFSET = 5
MISSING_OFFSET = 6

PREDICATE_INFO_LENGTH = 5

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
    """Counts the number of occurences of the words in forms_list in the text
    """
    flags = get_tokens_flags(case_sensitive)
    expression = r'(\b|_)%s(\b|_)' % '(\\b|_)|(\\b|_)'.join(forms_list)
    pattern = re.compile(expression, flags=flags)
    matches = re.findall(pattern, text)
    return len(matches)


def item_matches(text, item, options):
    """ Counts the number of occurences of the item in the text
    The matching considers the separator or
    the separating regular expression.
    """
    separator = options.get('separator', ' ')
    regexp = options.get('separator_regexp')
    if regexp is None:
        regexp = r"%s" % re.escape(separator)

    return count_items_matches(text, item, regexp)


def count_items_matches(text, item, regexp):
    """ Counts the number of occurences of the item in the text
    """
    expression = r'(^|%s)%s($|%s)' % (regexp, item, regexp)
    pattern = re.compile(expression, flags=re.U)
    matches = re.findall(pattern, text)

    return len(matches)

def apply_predicates(node, input_data, fields):
    num_predicates = node[1]

    for i in range(num_predicates):
        operation = node[OPERATION_OFFSET + (PREDICATE_INFO_LENGTH * i)]
        field = node[FIELD_OFFSET + (PREDICATE_INFO_LENGTH * i)]
        value = node[VALUE_OFFSET + (PREDICATE_INFO_LENGTH * i)]
        term = node[TERM_OFFSET + (PREDICATE_INFO_LENGTH * i)]
        missing = node[MISSING_OFFSET + (PREDICATE_INFO_LENGTH * i)]

        if not apply_predicate(operation, field, value, term, missing,
                               input_data, fields[field]):
            return False

    return True


def apply_predicate(operator, field, value, term, missing, input_data,
                    field_info):
    """Applies the operators defined in the predicate as strings to
    the provided input data
    """
    # for missing operators
    if input_data.get(field) is None:
        # text and item fields will treat missing values by following the
        # doesn't contain branch
        if term is None:
            return missing or (
                operator == EQ and value is None)
    elif operator == NE and value is None:
        return True

    if term is not None:
        if field_info['optype'] == 'text':
            all_forms = field_info['summary'].get('term_forms', {})
            term_forms = all_forms.get(term, [])
            terms = [term]
            terms.extend(term_forms)
            options = field_info['term_analysis']
            input_terms = term_matches(input_data.get(field, ""), terms,
                                       options)
            return OPERATOR[operator](input_terms, value)
        else:
            # new items optype
            options = field_info['item_analysis']
            input_items = item_matches(input_data.get(field, ""), term,
                                       options)
            return OPERATOR[operator](input_items, value)
    if operator == IN:
        return OPERATOR[operator](value, input_data[field])
    return OPERATOR[operator](input_data[field], value)
