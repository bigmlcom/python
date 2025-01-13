# -*- coding: utf-8 -*-
#
# Copyright 2019-2025 BigML
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

"""Flat Tree structure for the BigML local Model

This module defines an auxiliary Tree structure that is used in the local Model
to make predictions locally or embedded into your application without needing
to send requests to BigML.io.

"""

import os

from bigml.util import NUMERIC
from bigml.predicate_utils.utils import INVERSE_OP
from bigml.predict_utils.common import get_node, get_predicate
from bigml.tree_utils import old_filter_nodes, missing_branch, \
    none_value
from bigml.tree_utils import INDENT, PYTHON_OPERATOR, \
    TM_TOKENS, TM_FULL_TERM, TM_ALL, TERM_OPTIONS, ITEM_OPTIONS, \
    COMPOSED_FIELDS, NUMERIC_VALUE_FIELDS
from bigml.predicate import Predicate


MISSING_OPERATOR = {
    "=": "is",
    "!=": "is not"
}

CONFIDENCE = "confidence"
PROBABILITY = "probability"
CONFIDENCE_METRICS = [CONFIDENCE, PROBABILITY]


# templates for static Python
BIGML_SCRIPT = os.path.dirname(__file__)
TERM_TEMPLATE = "%s/out_model/static/term_analysis.txt" % BIGML_SCRIPT
ITEMS_TEMPLATE = "%s/out_model/static/items_analysis.txt" % BIGML_SCRIPT


def map_nodes(tree, offsets, nodes=None):
    """Map nodes by ID

    """
    if nodes is None:
        nodes = {}

    node = Node(tree, offsets)

    children = []
    for child in node.children:
        nodes = map_nodes(child, offsets, nodes)
        ch_node = Node(child, offsets)
        children.append("n_%s" % ch_node.id)

    node.children = children
    nodes["n_%s" % node.id] = node
    return nodes


def value_to_print(value, optype):
    """String of code that represents a value according to its type

    """
    # the value is numeric for these fields
    if (optype in NUMERIC_VALUE_FIELDS or value is None):
        return value
    return "\"%s\"" % value.replace('"', '\\"')


def map_data(field, missing=False):
    """Returns the subject of the condition in map format when
       more than MAX_ARGS_LENGTH arguments are used.
    """
    if missing:
        return "data.get('%s')" % field
    return "data['%s']" % field


def missing_prefix_code(self, field):
    """Part of the condition that checks for missings when missing_splits
    has been used

    """

    negation = "" if self.predicate.missing else " not"
    connection = "or" if self.predicate.missing else "and"

    return "%s is%s None %s " % (map_data(field, True),
                                 negation,
                                 connection)


def split_condition_code(self, field, depth,
                         pre_condition, term_analysis_fields,
                         item_analysis_fields):
    """Condition code for the split

    """

    optype = self.fields[field]['optype']
    value = value_to_print(self.predicate.value, optype)

    if optype in ['text', 'items']:
        if optype == 'text':
            term_analysis_fields.append((field,
                                         self.predicate.term))
            matching_function = "term_matches"
        else:
            item_analysis_fields.append((field,
                                         self.predicate.term))
            matching_function = "item_matches"

        return "%sif (%s%s(%s, \"%s\", %s%s) %s " \
               "%s):\n" % \
              (INDENT * depth, pre_condition, matching_function,
               map_data(field, False),
               self.predicate.field,
               'u' if isinstance(self.predicate.term, str) else '',
               value_to_print(self.predicate.term, 'categorical'),
               PYTHON_OPERATOR[self.predicate.operator],
               value)

    operator = (MISSING_OPERATOR[self.predicate.operator] if
                self.predicate.value is None else
                PYTHON_OPERATOR[self.predicate.operator])

    return "%sif (%s%s %s %s):\n" % \
           (INDENT * depth, pre_condition,
            map_data(field, False),
            operator,
            value)


#pylint: disable=locally-disabled,invalid-name
class Node():
    """Structure to store the node information

    """
    counter = 0

    def __init__(self, tree, offsets):
        predicate = get_predicate(tree)
        if isinstance(predicate, bool):
            self.predicate = predicate
        else:
            [operator, field, value, term, _] = predicate
            self.predicate = Predicate(INVERSE_OP[operator],
                                       field, value, term)
        node = get_node(tree)
        for attr in offsets:
            if attr not in ["children#", "children"]:
                setattr(self, attr, node[offsets[attr]])
        children = [] if node[offsets["children#"]] == 0 else \
            node[offsets["children"]]
        self.children = children
        self.id = Node.counter
        Node.counter += 1


class FlatTree():
    """A tree-like predictive model.

    """
    def __init__(self, tree, offsets, fields, objective_id,
                 boosting=None):

        self.fields = fields
        self.objective_id = objective_id
        self.regression = fields[objective_id]["optype"] == NUMERIC
        self.nodes = map_nodes(tree, offsets)
        self.boosting = boosting

    def missing_check_code(self, field, node, depth, metric):
        """Builds the code to predict when the field is missing

        """
        code = "%sif (%s is None):\n" % \
               (INDENT * depth,
                map_data(field, True))
        value = value_to_print(node.output,
                               self.fields[self.objective_id]['optype'])
        code += "%sreturn {\"prediction\": %s," \
            " \"%s\": %s}\n" % \
            (INDENT * (depth + 1), value, metric, getattr(node, metric))
        return code


    def missing_prefix_code(self, field):
        """Part of the condition that checks for missings when missing_splits
        has been used

        """
        return missing_prefix_code(self, field)

    def split_condition_code(self, field, depth,
                             pre_condition, term_analysis_fields,
                             item_analysis_fields):
        """Condition code for the split

        """

        return split_condition_code(self, field, depth,
                                    pre_condition, term_analysis_fields,
                                    item_analysis_fields)

    def term_analysis_body(self, term_analysis_predicates,
                           item_analysis_predicates):
        """ Writes auxiliary functions to handle the term and item
        analysis fields

        """
        body = ""
        # static content
        body += """
    import re
"""
        if term_analysis_predicates:
            body += """
    tm_tokens = '%s'
    tm_full_term = '%s'
    tm_all = '%s'

""" % (TM_TOKENS, TM_FULL_TERM, TM_ALL)

            with open(TERM_TEMPLATE) as template_handler:
                body += template_handler.read()

            term_analysis_options = {x[0] for x in term_analysis_predicates}
            term_analysis_predicates = set(term_analysis_predicates)
            body += """
    term_analysis = {"""
            for field_id in term_analysis_options:
                field = self.fields[field_id]
                body += """
        \"%s\": {""" % field_id
                options = sorted(field['term_analysis'].keys())
                for option in options:
                    if option in TERM_OPTIONS:
                        body += """
            \"%s\": %s,""" % (option, repr(field['term_analysis'][option]))
                body += """
        },"""
            body += """
    }"""
            body += """
    term_forms = {"""
            term_forms = {}
            fields = self.fields
            for field_id, term in term_analysis_predicates:
                alternatives = []
                field = fields[field_id]
                if field_id not in term_forms:
                    term_forms[field_id] = {}
                all_forms = field['summary'].get('term_forms', {})
                if all_forms:
                    alternatives = all_forms.get(term, [])
                    if alternatives:
                        terms = [term]
                        terms.extend(all_forms.get(term, []))
                        term_forms[field_id][term] = terms
            for field, term_form in term_forms.items():
                body += """
        \"%s\": {""" % field
                terms = sorted(term_form.keys())
                for term in terms:
                    body += """
            u\"%s\": %s,""" % (term, term_form[term])
                body += """
        },"""
            body += """
    }

"""
        if item_analysis_predicates:
            with open(ITEMS_TEMPLATE) as template_handler:
                body += template_handler.read()

            item_analysis_options = {[x[0] for x in item_analysis_predicates]}
            item_analysis_predicates = set(item_analysis_predicates)
            body += """
    item_analysis = {"""
            for field_id in item_analysis_options:
                field = self.fields[field_id]
                body += """
        \"%s\": {""" % field_id
                for option in field['item_analysis']:
                    if option in ITEM_OPTIONS:
                        body += """
            \"%s\": %s,""" % (option, repr(field['item_analysis'][option]))
                body += """
        },"""
            body += """
    }

"""
        return body

    def python(self, out, docstring, ids_path=None, subtree=True,
               metric=CONFIDENCE):
        """Generates a python function that implements the model.

        """

        python_header = "#!/usr/bin/env python\n# -*- coding: utf-8 -*-\n"

        predictor = "def predict_%s(data=None):\n" % self.objective_id
        predictor_doc = (INDENT + "\"\"\" " + docstring +
                         "\n" + INDENT + "\"\"\"\n")
        body, term_analysis_predicates, item_analysis_predicates = \
            self.plug_in_body(ids_path=ids_path, subtree=subtree, \
            metric=metric)
        terms_body = ""
        if term_analysis_predicates or item_analysis_predicates:
            terms_body = self.term_analysis_body(term_analysis_predicates,
                                                 item_analysis_predicates)
        predictor = python_header + predictor + \
            predictor_doc + terms_body + \
            "\n\n".join(body) + "\n%sreturn n_0(data)\n" % INDENT

        predictor_model = "def predict"
        predictor += "\n\n%s(data=None):\n%sif data is None:\n%sdata = {}\n" \
            % (predictor_model, INDENT, INDENT * 2)
        predictor += "%sprediction = predict_%s(data)\n" % ( \
            INDENT, self.objective_id)

        if self.boosting is not None:
            predictor += "%sprediction.update({\"weight\": %s})\n" % \
                (INDENT, self.boosting.get("weight"))
            if self.boosting.get("objective_class") is not None:
                predictor += "%sprediction.update({\"class\": \"%s\"})\n" % \
                    (INDENT, self.boosting.get("objective_class"))
        predictor += "%sreturn prediction" % INDENT
        out.write(predictor)
        out.flush()


    def plug_in_body(self, ids_path=None, subtree=True, prefix=None,
                     metric=CONFIDENCE):
        """Translate the model into a set of functions, one per node, that
        contain only if statements and function calls

        `depth` controls the size of indentation. As soon as a value is missing
        that node is returned without further evaluation.

        """
        # label for the confidence measure and initialization
        metric = metric if metric in CONFIDENCE_METRICS else "confidence"

        if prefix is None:
            prefix = ""
        term_analysis_fields = []
        item_analysis_fields = []
        functions = []

        nodes = old_filter_nodes(list(self.nodes.values()), ids=ids_path,
                                 subtree=subtree)
        if nodes:

            for node in nodes:
                depth = 1
                body = "%sdef %sn_%s(data):\n" % (INDENT * depth, prefix,
                                                  node.id)
                depth += 1

                children = [self.nodes[key] for key in node.children]
                if children:

                    # field used in the split
                    field = children[0].predicate.field

                    has_missing_branch = (missing_branch(children) or
                                          none_value(children))
                    # the missing is singled out as a special case only when
                    # there's no missing branch in the children list
                    has_one_branch = not has_missing_branch or \
                        self.fields[field]['optype'] in COMPOSED_FIELDS
                    if has_one_branch:
                        body += self.missing_check_code( \
                            field, node, depth, metric)

                    condition = True

                    for child in children:

                        if condition: # only first child has if condition
                            field = child.predicate.field
                            pre_condition = ""
                            # code when missing_splits has been used
                            if has_missing_branch and child.predicate.value \
                                    is not None:
                                pre_condition = child.missing_prefix_code( \
                                    field)

                            # complete split condition code
                            body += child.split_condition_code( \
                                field, depth, pre_condition,
                                term_analysis_fields, item_analysis_fields)

                        # body += next_level[0]
                        depth += 1
                        body += "%sreturn %sn_%s(data)\n" % \
                            (INDENT * depth, prefix, child.id)
                        depth -= 2
                        condition = False
                else:
                    value = value_to_print( \
                        node.output,
                        self.fields[self.objective_id]['optype'])
                    body += "%sreturn {\"prediction\":%s, \"%s\":%s}\n" % ( \
                        INDENT * depth, value, metric, getattr(node, metric))
                    depth -= 1

                functions.append(body)

        return functions, term_analysis_fields, item_analysis_fields
