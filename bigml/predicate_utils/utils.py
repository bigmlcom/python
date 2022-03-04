# -*- coding: utf-8 -*-
#
# Copyright 2020-2022 BigML
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

from bigml.util import plural

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

INVERSE_OP = dict(zip(OPERATOR_CODE.values(), OPERATOR_CODE.keys()))

RELATIONS = {
    '<=': 'no more than %s %s',
    '>=': '%s %s at most',
    '>': 'more than %s %s',
    '<': 'less than %s %s'
}

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

    return term_matches_tokens(text, forms_list, case_sensitive)

def is_full_term(term, field):
    """Returns a boolean showing if a term is considered as a full_term
    """
    if term is not None:
        # new optype has to be handled in tokens
        if field['optype'] == 'items':
            return False
        options = field['term_analysis']
        token_mode = options.get('token_mode', TM_TOKENS)
        if token_mode == TM_FULL_TERM:
            return True
        if token_mode == TM_ALL:
            return re.match(FULL_TERM_PATTERN, term)
    return False


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

    expression = r'(\b|_)%s(\b|_)' % '(\\b|_)|(\\b|_)'.join([re.escape(term) \
        for term in forms_list])
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
    expression = r'(^|%s)%s($|%s)' % (regexp, re.escape(item), regexp)
    pattern = re.compile(expression, flags=re.U)
    matches = re.findall(pattern, text)

    return len(matches)

def apply_predicates(node, input_data, fields, normalize_repeats=False):
    shift = 1 if normalize_repeats else 0
    num_predicates = node[1 + shift]

    predicates_ok = 0

    for i in range(num_predicates):
        operation = node[OPERATION_OFFSET + (PREDICATE_INFO_LENGTH * i) + shift]
        field = node[FIELD_OFFSET + (PREDICATE_INFO_LENGTH * i) + shift]
        value = node[VALUE_OFFSET + (PREDICATE_INFO_LENGTH * i) + shift]
        term = node[TERM_OFFSET + (PREDICATE_INFO_LENGTH * i) + shift]
        missing = node[MISSING_OFFSET + (PREDICATE_INFO_LENGTH * i) + shift]

        predicate_ok = apply_predicate(operation, field, value, term, missing,
                                       input_data, fields[field])
        if predicate_ok:
            predicates_ok += 1

    return predicates_ok

def apply_predicate(operation, field, value, term, missing, input_data,
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
                operation == EQ and value is None)
    elif operation == NE and value is None:
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
            return OPERATOR[operation](input_terms, value)
        # new items optype
        options = field_info['item_analysis']
        input_items = item_matches(input_data.get(field, ""), term,
                                   options)
        return OPERATOR[operation](input_items, value)
    if operation == IN:
        return OPERATOR[operation](value, input_data[field])
    return OPERATOR[operation](input_data[field], value)


def pack_predicate(predicate):
    """Compacts the predicate condition

    """
    node = list()
    if predicate and predicate is not True:
        operation = predicate.get('operator')
        value = predicate.get('value')
        missing = False
        if operation.endswith("*"):
            operation = operation[0: -1]
            missing = True
        elif operation == 'in' and None in value:
            missing = True

        node.append(OPERATOR_CODE.get(operation))
        node.append(predicate.get('field'))
        node.append(value)
        node.append(predicate.get('term'))
        node.append(missing)
    else:
        node.append(True)
    return node


def predicate_to_rule(operation, field_info, value, term,
                      missing, label='name'):
    """Predicate condition string

    """
    # externally forcing missing to True or False depending on the path
    if missing is None:
        missing = False
    if label is not None:
        name = field_info[label]
    else:
        name = ""
    operation = INVERSE_OP[operation]
    full_term = is_full_term(term, field_info)
    relation_missing = " or missing" if missing else ""
    if term is not None:
        relation_suffix = ''
        if ((operation == '<' and value <= 1) or
                (operation == '<=' and value == 0)):
            relation_literal = ('is not equal to' if full_term
                                else 'does not contain')
        else:
            relation_literal = 'is equal to' if full_term else 'contains'
            if not full_term:
                if operation != '>' or value != 0:
                    relation_suffix = (RELATIONS[operation] %
                                       (value,
                                        plural('time', value)))
        return "%s %s %s %s%s" % (name, relation_literal,
                                  term, relation_suffix,
                                  relation_missing)
    if value is None:
        return "%s %s" % (name,
                          "is missing" if operation == '='
                          else "is not missing")
    return "%s %s %s%s" % (name,
                           operation,
                           value,
                           relation_missing)


def to_lisp_rule(operation, field, value, term,
                 missing, field_info):
    """Builds rule string in LISP from a predicate

    """
    if term is not None:
        if field_info['optype'] == 'text':
            options = field_info['term_analysis']
            case_insensitive = not options.get('case_sensitive', False)
            case_insensitive = 'true' if case_insensitive else 'false'
            language = options.get('language')
            language = "" if language is None else " %s" % language
            return "(%s (occurrences (f %s) %s %s%s) %s)" % (
                operation, field, term,
                case_insensitive, language, value)
        if field_info['optype'] == 'items':
            return "(%s (if (contains-items? %s %s) 1 0) %s)" % (
                operation, field, term, value)
    if value is None:
        negation = "" if operation == "=" else "not "
        return "(%s missing? %s)" % (negation, field)
    rule = "(%s (f %s) %s)" % (operation,
                               field,
                               value)
    if missing:
        rule = "(or (missing? %s) %s)" % (field, rule)
    return rule
