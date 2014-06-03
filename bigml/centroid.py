# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2014 BigML
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

"""Centroid structure for the BigML local Cluster

This module defines an auxiliary Centroid predicate structure that is used
in the cluster.

"""

import operator
import re
import math

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


def cosine_distance2(terms, centroid_terms, scale):
    """Returns the distance defined by cosine similarity

    """
    # Centroid values for the field can be an empty list.
    # Then the distance for an empty input is 1
    # (before applying the scale factor).
    if not terms and not centroid_terms:
        return 0
    if not terms or not centroid_terms:
        return scale ** 2
    input_count = 0
    for term in centroid_terms:
        if term in terms:
            input_count += 1
    cosine_similarity = input_count / math.sqrt(
        len(terms) * len(centroid_terms))
    similarity_distance = scale * (1 - cosine_similarity)
    return similarity_distance ** 2


class Centroid(object):
    """A Centroid.

    """
    def __init__(self, centroid_info):
        self.center = centroid_info.get('center', {})
        self.count = centroid_info.get('count', 0)
        self.centroid_id = centroid_info.get('id', None)
        self.name = centroid_info.get('name', None)

    def distance(self, input_data, term_sets, scales, stop_distance=None):
        """Distance from the given input data to the centroid

        """
        distance = 0.0;
        for field_id, value in self.center.items():
            if isinstance(value, list):
                # text field
                distance += cosine_distance2(term_sets[field_id], value,
                                             scales[field_id])
            elif isinstance(value, basestring):
                if not field_id in input_data or input_data[field_id] != value:
                    distance += 1 * scales[field_id] ** 2
            else:
                int(value)
                distance += ((input_data[field_id] - value) *
                             scales[field_id]) ** 2
            if stop_distance is not None and distance >= stop_distance:
                return None
        return distance
                
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
