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

"""Predict utilities for boosting models

"""
from bigml.predict_utils.common import one_branch, \
    get_node, get_predicate, FIELD_OFFSET
from bigml.predicate_utils.utils import predicate_to_rule, apply_predicate, \
    pack_predicate
from bigml.prediction import Prediction


OFFSETS = { \
    "id": 0,
    "output": 1,
    "count": 2,
    "g_sum": 3,
    "h_sum": 4,
    "children#": 5,
    "children": 6}


def build_boosting_tree(node_dict, node=None, terms=None):
    """Builds a compressed version of the tree structure as an list of
    lists. Starting from the root node, that is represented by a list:
        [#predicates, op-code, field, value, term, missing...]

    And each child is represented by a list whose elements are:
        [id, output, count, g_sum, h_sum,
         #children, children_nodes_list*]
    """
    if terms is None:
        terms = {}
    predicate = node_dict.get('predicate', True)
    outer = node if node else list(pack_predicate(predicate))
    children = node_dict.get("children", [])
    outer.append(node_dict.get("id"))
    outer.append(node_dict.get("output"))
    outer.append(node_dict.get("count"))
    outer.append(node_dict.get("g_sum"))
    outer.append(node_dict.get("h_sum"))
    outer.append(len(children))
    children_list = list()
    for child in children:
        predicate = child.get('predicate')
        field = predicate.get("field")
        if field not in terms:
            terms[field] = []
        term = predicate.get("term")
        if term not in terms[field]:
            terms[field].append(term)
        inner = pack_predicate(predicate)
        build_boosting_tree(child, node=inner, terms=terms)
        children_list.append(inner)
    if children_list:
        outer.append(children_list)

    return outer


def boosting_proportional_predict(tree, fields, input_data, path=None,
                                  missing_found=False):
    """Makes a prediction based on a number of field values considering all
       the predictions of the leaves that fall in a subtree.

       Each time a splitting field has no value assigned, we consider
       both branches of the split to be true, merging their
       predictions. The function returns the merged distribution and the
       last node reached by a unique path.

    """

    if path is None:
        path = []

    node = get_node(tree)
    children_number = node[OFFSETS["children#"]]
    children = [] if children_number == 0 else node[OFFSETS["children"]]
    g_sum = node[OFFSETS["g_sum"]]
    h_sum = node[OFFSETS["h_sum"]]
    count = node[OFFSETS["count"]]

    if not children:
        return (g_sum, h_sum, count, path)
    if one_branch(children, input_data) or \
            fields[children[0][FIELD_OFFSET]]["optype"] in \
            ["text", "items"]:
        for child in children:
            [operator, field, value, term, missing] = get_predicate(child)
            if apply_predicate(operator, field, value, term, missing,
                               input_data, fields[field]):
                new_rule = predicate_to_rule(operator, fields[field], value,
                                             term, missing)
                if new_rule not in path and not missing_found:
                    path.append(new_rule)
                return boosting_proportional_predict( \
                    child, fields,
                    input_data, path, missing_found)
    else:
        # missing value found, the unique path stops
        missing_found = True
        g_sums = 0.0
        h_sums = 0.0
        population = 0
        for child in children:
            g_sum, h_sum, count, _ = \
                boosting_proportional_predict( \
                    child, fields, input_data,
                    path, missing_found)
            g_sums += g_sum
            h_sums += h_sum
            population += count
        return (g_sums, h_sums, population, path)


def boosting_last_predict(tree, fields, input_data, path=None):
    """Predict function for boosting and last prediction strategy

    """

    if path is None:
        path = []
    node = get_node(tree)

    children_number = node[OFFSETS["children#"]]
    children = [] if children_number == 0 else node[OFFSETS["children"]]
    count = node[OFFSETS["count"]]

    if children:
        for child in children:
            [operator, field, value, term, missing] = get_predicate(child)
            if apply_predicate(operator, field, value, term, missing,
                               input_data, fields[field]):
                path.append(predicate_to_rule(operator, fields[field],
                                              value, term, missing))
                return boosting_last_predict( \
                    child, fields, \
                    input_data, path=path)

    return Prediction(
        node[OFFSETS["output"]],
        path,
        None,
        distribution=None,
        count=count,
        median=None,
        distribution_unit=None,
        children=children,
        d_min=None,
        d_max=None)
