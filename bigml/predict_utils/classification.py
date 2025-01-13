# -*- coding: utf-8 -*-
#
# Copyright 2020-2025 BigML
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

"""Predict utilities for classifications

"""
from bigml.predict_utils.common import last_prediction_predict, \
    proportional_predict, extract_distribution
from bigml.predicate_utils.utils import pack_predicate
from bigml.prediction import Prediction
from bigml.multivote import ws_confidence


OFFSETS = { \
    "False": {"id": 0,
              "output": 1,
              "count": 2,
              "confidence": 3,
              "distribution": 4,
              "children#": 5,
              "children": 6},
    "True": {"id": 0,
             "output": 1,
             "count": 2,
             "confidence": 3,
             "distribution": 4,
             "wdistribution": 5,
             "weight": 6,
             "children#": 7,
             "children": 8}}


def build_classification_tree(node_dict, node=None, distribution=None,
                              weighted=False, terms=None):
    """Builds a compressed version of the tree structure as an list of
    lists. Starting from the root node, that is represented by a list:
        [weight, #predicates, op-code, field, value, term, missing...]

    And each child is represented by a list whose elements are:
        [children#, id, output, count, confidence, output, distribution,
         distribution_unit,
         wdistribution, wdistribution_unit, children_nodes_list*]
    """
    if terms is None:
        terms = {}
    predicate = node_dict.get('predicate', True)
    outer = node if node else list(pack_predicate(predicate))
    outer.append(node_dict.get("id"))
    outer.append(node_dict.get("output"))
    outer.append(node_dict.get("count"))
    outer.append(node_dict.get("confidence"))
    distribution = distribution if distribution is not None else \
        node_dict.get("objective_summary")
    _, distribution = extract_distribution(distribution)
    outer.append(distribution)
    if weighted:
        _, wdistribution = extract_distribution( \
             node_dict.get("weighted_objective_summary"))
        outer.append(wdistribution)
        outer.append(node_dict.get("weight"))
    children = node_dict.get("children", [])
    outer.append(len(children))
    children_list = []
    for child in children:
        predicate = child.get('predicate')
        field = predicate.get("field")
        if field not in terms:
            terms[field] = []
        term = predicate.get("term")
        if term not in terms[field]:
            terms[field].append(term)
        inner = pack_predicate(predicate)
        build_classification_tree(child, node=inner, weighted=weighted,
                                  terms=terms)
        children_list.append(inner)
    if children_list:
        outer.append(children_list)
    return outer


def classification_proportional_predict(tree, weighted, fields, input_data):
    """Prediction for classification using proportional strategy

    """
    offset = OFFSETS[str(weighted)]
    (final_distribution, _, _, last_node, population,
     _, path) = proportional_predict( \
        tree, offset, fields, input_data, path=None)

    distribution = [list(element) for element in
                    sorted(list(final_distribution.items()),
                           key=lambda x: (-x[1], x[0]))]
    return Prediction( \
        distribution[0][0],
        path,
        ws_confidence(distribution[0][0], final_distribution,
                      ws_n=population),
        distribution,
        population,
        None,
        'categories',
        [] if last_node[OFFSETS[str(weighted)]["children#"]] == 0 else \
        last_node[OFFSETS[str(weighted)]["children"]])


def classification_last_predict(tree, weighted, fields, input_data):
    """Predict for classification and last prediction missing strategy

    """
    return last_prediction_predict(tree, OFFSETS[str(weighted)], fields,
                                   input_data)
