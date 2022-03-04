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

"""Tree level output for python
This module defines functions that generate python code to make local
predictions
"""

from bigml.tree_utils import (
    INDENT, PYTHON_OPERATOR, NUMERIC_VALUE_FIELDS)
from bigml.predict_utils.common import \
    get_node, get_predicate, MISSING_OFFSET

MISSING_OPERATOR = {
    "=": "is",
    "!=": "is not"
}


def value_to_print(value, optype):
    """String of code that represents a value according to its type
    """
    # the value is numeric for these fields
    if (optype in NUMERIC_VALUE_FIELDS or value is None):
        return value
    return "\"%s\"" % value.replace('"', '\\"')


def map_data(field, input_map=False, missing=False):
    """Returns the subject of the condition in map format when
       more than MAX_ARGS_LENGTH arguments are used.
    """
    if input_map:
        if missing:
            return "data.get('%s')" % field
        return "data['%s']" % field
    return field


def missing_prefix_code(tree, fields, field, input_map, cmv):
    """Part of the condition that checks for missings when missing_splits
    has been used
    """

    predicate = get_predicate(tree)
    missing = predicate[MISSING_OFFSET]
    negation = "" if missing else " not"
    connection = "or" if missing else "and"
    if not missing:
        cmv.append(fields[field]['slug'])
    return "%s is%s None %s " % (map_data(fields[field]['slug'],
                                          input_map,
                                          True),
                                 negation,
                                 connection)


def split_condition_code(tree, fields, depth, input_map,
                         pre_condition, term_analysis_fields,
                         item_analysis_fields, cmv):
    """Condition code for the split
    """

    predicate = get_predicate(tree)
    [operation, field, value, term, _] = predicate
    optype = fields[field]['optype']
    value = value_to_print(value, optype)

    if optype in ['text', 'items']:
        if optype == 'text':
            term_analysis_fields.append((field, term))
            matching_function = "term_matches"
        else:
            item_analysis_fields.append((field, term))
            matching_function = "item_matches"

        return "%sif (%s%s(%s, \"%s\", %s%s) %s " \
               "%s):\n" % \
              (INDENT * depth, pre_condition, matching_function,
               map_data(fields[field]['slug'],
                        input_map,
                        False),
               fields[field]['slug'],
               'u' if isinstance(term, str) else '',
               value_to_print(term, 'categorical'),
               PYTHON_OPERATOR[operation],
               value)

    operator = (MISSING_OPERATOR[operation] if
                value is None else
                PYTHON_OPERATOR[operation])
    if value is None:
        cmv.append(fields[field]['slug'])
    return "%sif (%s%s %s %s):\n" % \
           (INDENT * depth, pre_condition,
            map_data(fields[field]['slug'], input_map,
                     False),
            operator,
            value)


def filter_nodes(trees_list, offsets, ids=None, subtree=True):
    """Filters the contents of a trees_list. If any of the nodes is in the
       ids list, the rest of nodes are removed. If none is in the ids list
       we include or exclude the nodes depending on the subtree flag.

    """
    if not trees_list:
        return None
    trees = trees_list[:]
    if ids is not None:
        for tree in trees:
            node = get_node(tree)
            node_id = node[offsets["id"]]
            if node_id in ids:
                trees = [tree]
                return trees
    if not subtree:
        trees = []
    return trees
