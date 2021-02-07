# -*- coding: utf-8 -*-
#
# Copyright 2020-2021 BigML
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

"""Common predict utilities

"""
from bigml.predicate_utils.utils import apply_predicate, predicate_to_rule
from bigml.prediction import Prediction

from bigml.multivote import merge_distributions

OPERATION_OFFSET = 0
FIELD_OFFSET = 1
VALUE_OFFSET = 2
TERM_OFFSET = 3
MISSING_OFFSET = 4

PREDICATE_INFO_LENGTH = 5

DISTRIBUTION_GROUPS = ['bins', 'counts', 'categories']


def mintree_split(children):
    """Returns the field ID for the split

    """
    return children[0][FIELD_OFFSET]


def one_branch(children, input_data):
    """Check if there's only one branch to be followed

    """
    no_missing = mintree_split(children) in input_data
    return (no_missing or missing_branch(children)
            or none_value(children))


def missing_branch(children):
    """Checks if the missing values are assigned to a special branch

    """
    return any([child[MISSING_OFFSET] for child in children])


def none_value(children):
    """Checks if the predicate has a None value

    """
    return any([child[VALUE_OFFSET] is None for child in children])


def extract_distribution(summary):
    """Extracts the distribution info from the objective_summary structure
       in any of its grouping units: bins, counts or categories

    """
    for group in DISTRIBUTION_GROUPS:
        if group in summary:
            return group, summary.get(group)


def last_prediction_predict(tree, offsets, fields, input_data, path=None):
    """ Predictions for last prediction missing strategy

    """

    if path is None:
        path = []

    node = get_node(tree)

    children_number = node[offsets["children#"]]
    children = [] if children_number == 0 else node[offsets["children"]]

    for child in children:
        [operator, field, value, term, missing] = get_predicate(child)
        if apply_predicate(operator, field, value, term, missing,
                           input_data, fields[field]):
            new_rule = predicate_to_rule(operator, fields[field], value,
                                         term, missing)
            path.append(new_rule)
            return last_prediction_predict(child,
                                           offsets, fields,
                                           input_data, path=path)

    if "wdistribution" in offsets:
        output_distribution = node[offsets["wdistribution"]]
        output_unit = 'categories' if "distribution_unit" not in offsets else \
            node[offsets["wdistribution_unit"]]
    else:
        output_distribution = node[offsets["distribution"]]
        output_unit = 'categories' if "distribution_unit" not in offsets else \
            node[offsets["distribution_unit"]]

    return Prediction( \
        node[offsets["output"]],
        path,
        node[offsets["confidence"]],
        distribution=output_distribution,
        count=node[offsets["count"]],
        median=None if offsets.get("median") is None else \
            node[offsets["median"]],
        distribution_unit=output_unit,
        children=[] if node[offsets["children#"]] == 0 else \
            node[offsets["children"]],
        d_min=None if offsets.get("min") is None else \
            node[offsets["min"]],
        d_max=None if offsets.get("max") is None else \
            node[offsets["max"]])


def proportional_predict(tree, offsets, fields, input_data, path=None,
                         missing_found=False, median=False, parent=None):
    """Makes a prediction based on a number of field values averaging
       the predictions of the leaves that fall in a subtree.

       Each time a splitting field has no value assigned, we consider
       both branches of the split to be true, merging their
       predictions. The function returns the merged distribution and the
       last node reached by a unique path.

    """

    if path is None:
        path = []

    node = get_node(tree)

    final_distribution = {}
    children_number = node[offsets["children#"]]
    if "wdistribution" in offsets:
        distribution = node[offsets["wdistribution"]]
    else:
        distribution = node[offsets["distribution"]]
    children = [] if children_number == 0 else node[offsets["children"]]
    t_min = None if offsets.get("min") is None else node[offsets["min"]]
    t_max = None if offsets.get("max") is None else node[offsets["max"]]
    count = node[offsets["count"]]

    if children_number == 0:
        return (merge_distributions({}, dict((x[0], x[1])
                                             for x in distribution)),
                t_min, t_max, node, count, parent, path)
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
                return proportional_predict( \
                    child, offsets, fields,
                    input_data, path,
                    missing_found, median, parent=node)
    else:
        # missing value found, the unique path stops
        missing_found = True
        minimums = []
        maximums = []
        population = 0
        for child in children:
            (subtree_distribution, subtree_min,
             subtree_max, _, subtree_pop, _, path) = \
                proportional_predict( \
                    child, offsets, fields,
                    input_data, path, missing_found, median, parent=node)
            if subtree_min is not None:
                minimums.append(subtree_min)
            if subtree_max is not None:
                maximums.append(subtree_max)
            population += subtree_pop
            final_distribution = merge_distributions(
                final_distribution, subtree_distribution)
        return (final_distribution,
                min(minimums) if minimums else None,
                max(maximums) if maximums else None, node, population,
                parent, path)


def get_node(tree):
    """Extracts the properties of the node

    """
    if isinstance(tree[0], bool) and tree[0]: # predicate is True
        return tree[1:]
    return tree[PREDICATE_INFO_LENGTH:]


def get_predicate(tree):
    """Extracts the predicate for the node

    """
    if isinstance(tree[0], bool) and tree[0]:
        return True
    return tree[0: PREDICATE_INFO_LENGTH]
