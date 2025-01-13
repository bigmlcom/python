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

"""Tree level output for python
This module defines functions that generate python code to make local
predictions
"""

from bigml.tree_utils import INDENT, COMPOSED_FIELDS

from bigml.predict_utils.common import missing_branch, \
    none_value, get_node, get_predicate, mintree_split
from bigml.generators.tree_common import value_to_print, map_data, \
    missing_prefix_code, filter_nodes, split_condition_code


MISSING_OPERATOR = {
    "=": "is",
    "!=": "is not"
}


def missing_check_code(tree, offsets, fields, objective_id,
                       field, depth, input_map, cmv, metric):
    """Builds the code to predict when the field is missing
    """
    code = "%sif (%s is None):\n" % \
           (INDENT * depth,
            map_data(fields[field]['slug'], input_map, True))
    node = get_node(tree)
    value = value_to_print(node[offsets["output"]],
                           fields[objective_id]['optype'])
    code += "%sreturn {\"prediction\": %s," \
        " \"%s\": %s}\n" % \
        (INDENT * (depth + 1), value, metric, node[offsets["confidence"]])
    cmv.append(fields[field]['slug'])
    return code


def plug_in_body(tree, offsets, fields, objective_id, regression,
                 depth=1, cmv=None, input_map=False,
                 ids_path=None, subtree=True):
    """Translate the model into a set of "if" python statements.
    `depth` controls the size of indentation. As soon as a value is missing
    that node is returned without further evaluation.
    """
    # label for the confidence measure and initialization
    metric = "error" if regression else "confidence"
    if cmv is None:
        cmv = []
    body = ""
    term_analysis_fields = []
    item_analysis_fields = []

    node = get_node(tree)
    children = [] if node[offsets["children#"]] == 0 else \
        node[offsets["children"]]
    children = filter_nodes(children, offsets, ids=ids_path,
                            subtree=subtree)
    if children:

        # field used in the split
        field = mintree_split(children)

        has_missing_branch = (missing_branch(children) or
                              none_value(children))
        # the missing is singled out as a special case only when there's
        # no missing branch in the children list
        one_branch = not has_missing_branch or \
            fields[field]['optype'] in COMPOSED_FIELDS
        if (one_branch and
                not fields[field]['slug'] in cmv):
            body += missing_check_code(tree, offsets, fields, objective_id,
                                       field, depth, input_map, cmv, metric)

        for child in children:
            [_, field, value, _, _] = get_predicate(child)
            pre_condition = ""
            # code when missing_splits has been used
            if has_missing_branch and value is not None:
                pre_condition = missing_prefix_code(child, fields, field,
                                                    input_map, cmv)

            # complete split condition code
            body += split_condition_code( \
                child, fields, depth, input_map, pre_condition,
                term_analysis_fields, item_analysis_fields, cmv)

            # value to be determined in next node
            next_level = plug_in_body(child, offsets, fields, objective_id,
                                      regression, depth + 1, cmv=cmv[:],
                                      input_map=input_map, ids_path=ids_path,
                                      subtree=subtree)

            body += next_level[0]
            term_analysis_fields.extend(next_level[1])
            item_analysis_fields.extend(next_level[2])
    else:
        value = value_to_print(node[offsets["output"]],
                               fields[objective_id]['optype'])
        body = "%sreturn {\"prediction\":%s, \"%s\":%s}\n" % ( \
            INDENT * depth, value, metric, node[offsets["confidence"]])

    return body, term_analysis_fields, item_analysis_fields
