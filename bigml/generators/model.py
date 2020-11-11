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
Functions used to generate or write output from the decision tree models

"""
import sys
import os
import math
import keyword


from functools import reduce, partial

from bigml.path import Path, BRIEF
from bigml.basemodel import print_importance
from bigml.io import UnicodeWriter
from bigml.util import markdown_cleanup, prefix_as_comment, utf8, NUMERIC
from bigml.predicate import Predicate
from bigml.model import PYTHON_CONV
from bigml.predict_utils.common import missing_branch, \
    none_value, get_node, get_predicate
from bigml.predicate_utils.utils import predicate_to_rule, \
    to_lisp_rule, INVERSE_OP
from bigml.tree_utils import MAX_ARGS_LENGTH, tableau_string, slugify, \
    sort_fields, TM_TOKENS, TM_ALL, TM_FULL_TERM, TERM_OPTIONS, ITEM_OPTIONS, \
    PYTHON_OPERATOR
from bigml.generators.tree import plug_in_body
from bigml.generators.boosted_tree import boosted_plug_in_body
from bigml.generators.tree import filter_nodes


# templates for static Python
BIGML_SCRIPT = os.path.dirname(__file__)

TERM_TEMPLATE = "%s/static/term_analysis.txt" % BIGML_SCRIPT
ITEMS_TEMPLATE = "%s/static/items_analysis.txt" % BIGML_SCRIPT
HADOOP_CSV_TEMPLATE = "%s/static/python_hadoop_csv.txt" % \
    BIGML_SCRIPT
HADOOP_NEXT_TEMPLATE = "%s/static/python_hadoop_next.txt" % \
    BIGML_SCRIPT
HADOOP_REDUCER_TEMPLATE = "%s/static/python_hadoop_reducer.txt" % \
    BIGML_SCRIPT

DEFAULT_IMPURITY = 0.2

INDENT = '    '

DFT_ATTR = "output"


MISSING_OPERATOR = {
    EQ: "is",
    NE: "is not"
}

T_MISSING_OPERATOR = {
    EQ: "ISNULL(",
    NE: "NOT ISNULL("
}


def print_distribution(distribution, out=sys.stdout):
    """Prints distribution data

    """
    total = reduce(lambda x, y: x + y,
                   [group[1] for group in distribution])
    for group in distribution:
        out.write(utf8(
            "    %s: %.2f%% (%d instance%s)\n" % (
                group[0],
                round(group[1] * 1.0 / total, 4) * 100,
                group[1],
                "" if group[1] == 1 else "s")))


def list_fields(model, out=sys.stdout):
    """Prints descriptions of the fields for this model.

    """
    out.write(utf8('<%-32s : %s>\n' % (
        model.fields[model.objective_id]['name'],
        model.fields[model.objective_id]['optype'])))
    out.flush()

    for field in [(val['name'], val['optype']) for key, val in
                  sort_fields(model.fields)
                  if key != model.objective_id]:
        out.write(utf8('[%-32s : %s]\n' % (field[0], field[1])))
        out.flush()
    return model.fields


def gini_impurity(distribution, count):
    """Returns the gini impurity score associated to the distribution
       in the node

    """
    purity = 0.0
    if distribution is None:
        return None
    for _, instances in distribution:
        purity += math.pow(instances / float(count), 2)
    return 1.0 - purity


def get_leaves(model, path=None, filter_function=None):
    """Returns a list that includes all the leaves of the tree.

    """

    leaves = []

    if path is None:
        path = []

    offsets = model.offsets

    def get_tree_leaves(tree, fields, path, leaves, filter_function=None):

        node = get_node(tree)
        predicate = get_predicate(tree)
        if isinstance(predicate, list):
            [operator, field, value, term, missing] = get_predicate(tree)
            path.append(to_lisp_rule(operator, field, value, term, missing,
                                     fields[field]))

        children_number = node[offsets["children#"]]
        children = [] if children_number == 0 else node[offsets["children"]]

        if children:
            for child in children:
                leaves += get_tree_leaves(child, fields,
                                          path[:], leaves,
                                          filter_function=filter_function)
        else:
            leaf = {
                'id': node[offsets["id"]],
                'confidence': node[offsets["confidence"]],
                'count': node[offsets["count"]],
                'distribution': node[offsets["distribution"]],
                'impurity': gini_impurity(node[offsets["distribution"]],
                                          node[offsets["count"]]),
                'output': node[offsets["output"]],
                'path': path}
            if 'weighted_distribution' in offsets:
                leaf.update( \
                    {"weighted_distribution": node[offsets[ \
                        "weighted_distribution"]],
                     "weight": node[offsets["weight"]]})
            if (not hasattr(filter_function, '__call__')
                    or filter_function(leaf)):
                leaves += [leaf]
        return leaves
    return get_tree_leaves(model.tree, model.fields, path, leaves,
                           filter_function)


def impure_leaves(model, impurity_threshold=DEFAULT_IMPURITY):
    """Returns a list of leaves that are impure

    """
    if model.regression or model.boosting:
        raise AttributeError("This method is available for non-boosting"
                             " categorization models only.")
    def is_impure(node, impurity_threshold=impurity_threshold):
        """Returns True if the gini impurity of the node distribution
           goes above the impurity threshold.

        """
        return node.get('impurity') > impurity_threshold

    is_impure = partial(is_impure, impurity_threshold=impurity_threshold)
    return get_leaves(model, filter_function=is_impure)


def docstring(model):
    """Returns the docstring describing the model.

    """
    objective_name = model.fields[model.objective_id]['name'] if \
        not model.boosting else \
        model.fields[model.boosting["objective_field"]]['name']
    docstring_cmt = ("Predictor for %s from %s\n" % (
        objective_name,
        model.resource_id))
    model.description = (
        str(
            markdown_cleanup(model.description).strip()) or
        'Predictive model by BigML - Machine Learning Made Easy')
    docstring_cmt += "\n" + INDENT * 2 + (
        "%s" % prefix_as_comment(INDENT * 2, model.description))
    return docstring_cmt


def build_ids_map(tree, offsets, ids_map, parent_id=None):
    """Builds a map for the tree from each node id to its parent

    """
    node = get_node(tree)
    node_id = node[offsets["id"]]
    ids_map[node_id] = parent_id
    children_number = node[offsets["children#"]]
    children = [] if children_number == 0 else node[offsets["children"]]
    for child in children:
        build_ids_map(child, offsets, ids_map, node_id)


def fill_ids_map(model):
    """Filling the parent, child map

    """

    if not (hasattr(model, "ids_map") and model.ids_map):
        model.ids_map = {}
        build_ids_map(model.tree, model.offsets, model.ids_map)
    return model


def get_ids_path(model, filter_id):
    """Builds the list of ids that go from a given id to the tree root

    """
    model = fill_ids_map(model)

    ids_path = []
    if filter_id is not None and model.tree[model.offsets["id"]] is not None:
        if filter_id not in model.ids_map:
            raise ValueError("The given id does not exist.")
        ids_path = [filter_id]
        last_id = filter_id
        while model.ids_map[last_id] is not None:
            ids_path.append(model.ids_map[last_id])
            last_id = model.ids_map[last_id]
    return ids_path


def generate_rules(tree, offsets, objective_id, fields,
                   depth=0, ids_path=None, subtree=True):
    """Translates a tree model into a set of IF-THEN rules.

    """
    rules_str = ""

    node = get_node(tree)
    children_number = node[offsets["children#"]]
    children = [] if children_number == 0 else node[offsets["children"]]
    children = filter_nodes(children, offsets, ids=ids_path,
                            subtree=subtree)
    if children:
        for child in children:
            predicate = get_predicate(child)
            if isinstance(predicate, list):
                [operator, field, value, term, missing] = predicate
                child_node = get_node(child)
            rules_str += ("%s IF %s %s\n" %
                          (INDENT * depth,
                           predicate_to_rule(operator, fields[field],
                                             value, term, missing,
                                             label='slug'),
                           "AND" if child_node[offsets["children#"]] > 0
                           else "THEN"))
            rules_str += generate_rules(child, offsets, objective_id, fields,
                                        depth + 1, ids_path=ids_path,
                                        subtree=subtree)
    else:
        rules_str += ("%s %s = %s\n" %
                      (INDENT * depth,
                       (fields[objective_id]['slug']
                        if objective_id else "Prediction"),
                       node[offsets["output"]]))
    return rules_str


def rules(model, out=sys.stdout, filter_id=None, subtree=True):
    """Returns a IF-THEN rule set that implements the model.

    `out` is file descriptor to write the rules.

    """
    if model.boosting:
        raise AttributeError("This method is not available for boosting"
                             " models.")
    ids_path = get_ids_path(model, filter_id)

    def tree_rules(tree, offsets, objective_id, fields,
                   out, ids_path=None, subtree=True):
        """Prints out an IF-THEN rule version of the tree.

        """
        for field in sort_fields(fields):

            slug = slugify(fields[field[0]]['name'])
            fields[field[0]].update(slug=slug)
        out.write(utf8(generate_rules(tree, offsets, objective_id,
                                      fields,
                                      ids_path=ids_path,
                                      subtree=subtree)))
        out.flush()

    return tree_rules(model.tree, model.offsets, model.objective_id,
                      model.fields, out,
                      ids_path=ids_path, subtree=subtree)


def python(model, out=sys.stdout, hadoop=False,
           filter_id=None, subtree=True):
    """Returns a basic python function that implements the model.

    `out` is file descriptor to write the python code.

    """
    if model.boosting:
        raise AttributeError("This method is not available for boosting"
                             " models.")
    ids_path = get_ids_path(model, filter_id)
    if hadoop:
        return (hadoop_python_mapper(model, out=out,
                                     ids_path=ids_path,
                                     subtree=subtree) or
                hadoop_python_reducer(out=out))
    return tree_python(model.tree, model.offsets, model.fields,
                       model.objective_id, model.boosting, out,
                       docstring(model), ids_path=ids_path, subtree=subtree)

def hadoop_python_mapper(model, out=sys.stdout, ids_path=None,
                         subtree=True):
    """Generates a hadoop mapper header to make predictions in python

    """
    input_fields = [(value, key) for (key, value) in
                    sorted(list(model.inverted_fields.items()),
                           key=lambda x: x[1])]
    parameters = [value for (key, value) in
                  input_fields if key != model.objective_id]
    args = []
    for field in input_fields:
        slug = slugify(model.fields[field[0]]['name'])
        model.fields[field[0]].update(slug=slug)
        if field[0] != model.objective_id:
            args.append("\"" + model.fields[field[0]]['slug'] + "\"")

    with open(HADOOP_CSV_TEMPLATE) as template_handler:
        output = template_handler.read() % ",".join(parameters)

    output += "\n%sself.INPUT_FIELDS = [%s]\n" % \
        ((INDENT * 3), (",\n " + INDENT * 8).join(args))

    input_types = []
    prefixes = []
    suffixes = []
    count = 0
    fields = model.fields
    for key in [field[0] for field in input_fields
                if field[0] != model.objective_id]:
        input_type = ('None' if not fields[key]['datatype'] in
                      PYTHON_CONV
                      else PYTHON_CONV[fields[key]['datatype']])
        input_types.append(input_type)
        if 'prefix' in fields[key]:
            prefixes.append("%s: %s" % (count,
                                        repr(fields[key]['prefix'])))
        if 'suffix' in fields[key]:
            suffixes.append("%s: %s" % (count,
                                        repr(fields[key]['suffix'])))
        count += 1
    static_content = "%sself.INPUT_TYPES = [" % (INDENT * 3)
    formatter = ",\n%s" % (" " * len(static_content))
    output += "\n%s%s%s" % (static_content,
                            formatter.join(input_types),
                            "]\n")
    static_content = "%sself.PREFIXES = {" % (INDENT * 3)
    formatter = ",\n%s" % (" " * len(static_content))
    output += "\n%s%s%s" % (static_content,
                            formatter.join(prefixes),
                            "}\n")
    static_content = "%sself.SUFFIXES = {" % (INDENT * 3)
    formatter = ",\n%s" % (" " * len(static_content))
    output += "\n%s%s%s" % (static_content,
                            formatter.join(suffixes),
                            "}\n")

    with open(HADOOP_NEXT_TEMPLATE) as template_handler:
        output += template_handler.read()

    out.write(output)
    out.flush()

    tree_python(model.tree, model.offsets, model.fields, model.objective_id,
                False if not hasattr(model, "boosting") else model.boosting,
                out, docstring(model), ids_path=ids_path, subtree=subtree)

    output = \
"""
csv = CSVInput()
for values in csv:
    if not isinstance(values, bool):
        print u'%%s\\t%%s' %% (repr(values), repr(predict_%s(values)))
\n\n
""" % fields[model.objective_id]['slug']
    out.write(utf8(output))
    out.flush()

def hadoop_python_reducer(out=sys.stdout):
    """Generates a hadoop reducer to make predictions in python

    """

    with open(HADOOP_REDUCER_TEMPLATE) as template_handler:
        output = template_handler.read()
    out.write(utf8(output))
    out.flush()

def tree_python(tree, offsets, fields, objective_id, boosting,
                out, docstring_str, input_map=False,
                ids_path=None, subtree=True):
    """Writes a python function that implements the model.

    """
    args = []
    args_tree = []
    parameters = sort_fields(fields)
    if not input_map:
        input_map = len(parameters) > MAX_ARGS_LENGTH
    reserved_keywords = keyword.kwlist if not input_map else None
    prefix = "_" if not input_map else ""
    for field in parameters:
        field_name_to_show = fields[field[0]]['name'].strip()
        if field_name_to_show == "":
            field_name_to_show = field[0]
        slug = slugify(field_name_to_show,
                       reserved_keywords=reserved_keywords, prefix=prefix)
        fields[field[0]].update(slug=slug)
        if not input_map:
            if field[0] != objective_id:
                args.append("%s=None" % (slug))
                args_tree.append("%s=%s" % (slug, slug))
    if input_map:
        args.append("data={}")
        args_tree.append("data=data")

    function_name = fields[objective_id]['slug'] if \
        not boosting else fields[boosting["objective_field"]]['slug']
    if prefix == "_" and function_name[0] == prefix:
        function_name = function_name[1:]
    if function_name == "":
        function_name = "field_" + objective_id
    python_header = "# -*- coding: utf-8 -*-\n"
    predictor_definition = ("def predict_%s" %
                            function_name)
    depth = len(predictor_definition) + 1
    predictor = "%s(%s):\n" % (predictor_definition,
                               (",\n" + " " * depth).join(args))

    predictor_doc = (INDENT + "\"\"\" " + docstring_str +
                     "\n" + INDENT + "\"\"\"\n")
    body_fn = boosted_plug_in_body if boosting else plug_in_body
    body, term_analysis_predicates, item_analysis_predicates = \
        body_fn(tree, offsets, fields, objective_id,
                fields[objective_id]["optype"] == NUMERIC,
                input_map=input_map,
                ids_path=ids_path, subtree=subtree)
    terms_body = ""
    if term_analysis_predicates or item_analysis_predicates:
        terms_body = term_analysis_body(fields,
                                        term_analysis_predicates,
                                        item_analysis_predicates)
    predictor = python_header + predictor + \
        predictor_doc + terms_body + body

    predictor_model = "def predict"
    depth = len(predictor_model) + 1
    predictor += "\n\n%s(%s):\n" % (predictor_model,
                                    (",\n" + " " * depth).join(args))
    predictor += "%sprediction = predict_%s(%s)\n" % ( \
        INDENT, function_name, ", ".join(args_tree))

    if boosting is not None:
        predictor += "%sprediction.update({\"weight\": %s})\n" % \
            (INDENT, boosting.get("weight"))
        if boosting.get("objective_class") is not None:
            predictor += "%sprediction.update({\"class\": \"%s\"})\n" % \
                (INDENT, boosting.get("objective_class"))
    predictor += "%sreturn prediction" % INDENT

    out.write(utf8(predictor))
    out.flush()


def term_analysis_body(fields, term_analysis_predicates,
                       item_analysis_predicates):
    """ Writes auxiliary functions to handle the term and item
    analysis fields

    """
    body = """
    import re
"""
    # static content

    if term_analysis_predicates:
        body += """
    tm_tokens = '%s'
    tm_full_term = '%s'
    tm_all = '%s'

"""  % (TM_TOKENS, TM_FULL_TERM, TM_ALL)
        with open(TERM_TEMPLATE) as template_handler:
            body += template_handler.read()

        term_analysis_options = {predicate[0] for predicate in
                                 term_analysis_predicates}
        term_analysis_predicates = set(term_analysis_predicates)
        body += """
    term_analysis = {"""
        for field_id in term_analysis_options:
            field = fields[field_id]
            body += """
        \"%s\": {""" % field['slug']
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
        for field_id, term in term_analysis_predicates:
            alternatives = []
            field = fields[field_id]
            if field['slug'] not in term_forms:
                term_forms[field['slug']] = {}
            all_forms = field['summary'].get('term_forms', {})
            if all_forms:
                alternatives = all_forms.get(term, [])
                if alternatives:
                    terms = [term]
                    terms.extend(all_forms.get(term, []))
                    term_forms[field['slug']][term] = terms
        for field in term_forms:
            body += """
        \"%s\": {""" % field
            terms = sorted(term_forms[field].keys())
            for term in terms:
                body += """
            \"%s\": %s,""" % (term, term_forms[field][term])
            body += """
        },"""
        body += """
    }

"""
    if item_analysis_predicates:
        with open(ITEMS_TEMPLATE) as template_handler:
            body += template_handler.read()

        item_analysis_options = {predicate[0] for predicate in
                                 item_analysis_predicates}
        item_analysis_predicates = set(item_analysis_predicates)
        body += """
    item_analysis = {"""
        for field_id in item_analysis_options:
            field = fields[field_id]
            body += """
        \"%s\": {""" % field['slug']
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


def tableau(model, out=sys.stdout, hadoop=False,
            filter_id=None, subtree=True, attr=DFT_ATTR):
    """Returns a basic tableau function that implements the model.

    `out` is file descriptor to write the tableau code.

    """
    if model.boosting:
        raise AttributeError("This method is not available for boosting"
                             " models.")
    ids_path = get_ids_path(model, filter_id)
    if hadoop:
        return "Hadoop output not available."
    response = tree_tableau(model.tree, model.offsets, model.fields,
                            model.objective_id,
                            out, ids_path=ids_path,
                            subtree=subtree, attr=attr)
    if response:
        out.write("END\n")
    else:
        out.write("\nThis function cannot be represented "
                  "in Tableau syntax.\n")
    out.flush()
    return None



def tableau_body(tree, offsets, fields, objective_id,
                 body="", conditions=None, cmv=None,
                 ids_path=None, subtree=True, attr=DFT_ATTR):
    """Translate the model into a set of "if" statements in Tableau syntax

    `depth` controls the size of indentation. As soon as a value is missing
    that node is returned without further evaluation.

    """

    if cmv is None:
        cmv = []
    if body:
        alternate = "ELSEIF"
    else:
        if conditions is None:
            conditions = []
        alternate = "IF"

    node = get_node(tree)
    children_number = node[offsets["children#"]]
    children = [] if children_number == 0 else node[offsets["children"]]
    children = filter_nodes(children, offsets, ids=ids_path,
                            subtree=subtree)
    if children:
        [_, field, _, _, _] = get_predicate(children[0])
        has_missing_branch = (missing_branch(children) or
                              none_value(children))
        # the missing is singled out as a special case only when there's
        # no missing branch in the children list
        if (not has_missing_branch and
                fields[field]['name'] not in cmv):
            conditions.append("ISNULL([%s])" % fields[field]['name'])
            body += ("%s %s THEN " %
                     (alternate, " AND ".join(conditions)))
            if fields[objective_id]['optype'] == 'numeric':
                value = node[offsets[attr]]
            else:
                value = tableau_string(node[offsets[attr]])
            body += ("%s\n" % value)
            cmv.append(fields[field]['name'])
            alternate = "ELSEIF"
            del conditions[-1]

        for child in children:
            pre_condition = ""
            post_condition = ""
            [operator, field, ch_value, _, missing] = get_predicate(child)
            if has_missing_branch and ch_value is not None:
                negation = "" if missing else "NOT "
                connection = "OR" if missing else "AND"
                pre_condition = (
                    "(%sISNULL([%s]) %s " % (
                        negation, fields[field]['name'], connection))
                if not missing:
                    cmv.append(fields[field]['name'])
                post_condition = ")"
            optype = fields[field]['optype']
            if ch_value is None:
                value = ""
            elif optype in ['text', 'items']:
                return ""
            elif optype == 'numeric':
                value = ch_value
            else:
                value = repr(ch_value)

            operator = ("" if ch_value is None else
                        PYTHON_OPERATOR[operator])
            if ch_value is None:
                pre_condition = (
                    T_MISSING_OPERATOR[operator])
                post_condition = ")"

            conditions.append("%s[%s]%s%s%s" % (
                pre_condition,
                fields[field]['name'],
                operator,
                value,
                post_condition))
            body = tableau_body(child, offsets, fields, objective_id,
                                body, conditions[:], cmv=cmv[:],
                                ids_path=ids_path, subtree=subtree, attr=attr)
            del conditions[-1]
    else:
        if fields[objective_id]['optype'] == 'numeric':
            value = tree[offsets[attr]]
        else:
            value = tableau_string(node[offsets[attr]])
        body += (
            "%s %s THEN" % (alternate, " AND ".join(conditions)))
        body += " %s\n" % value

    return body

def tree_tableau(tree, offsets, fields, objective_id,
                 out, ids_path=None, subtree=True, attr=DFT_ATTR):
    """Writes a Tableau function that implements the model.

    """
    body = tableau_body(tree, offsets, fields, objective_id,
                        ids_path=ids_path, subtree=subtree, attr=attr)
    if not body:
        return False
    out.write(utf8(body))
    out.flush()
    return True


def group_prediction(model):
    """Groups in categories or bins the predicted data

    dict - contains a dict grouping counts in 'total' and 'details' lists.
            'total' key contains a 3-element list.
                   - common segment of the tree for all instances
                   - data count
                   - predictions count
            'details' key contains a list of elements. Each element is a
                      3-element list:
                   - complete path of the tree from the root to the leaf
                   - leaf predictions count
                   - confidence
    """
    if model.boosting:
        raise AttributeError("This method is not available for boosting"
                             " models.")
    groups = {}
    tree = model.tree
    node = get_node(tree)
    offsets = model.offsets
    distribution = node[offsets["distribution"]]

    for group in distribution:
        groups[group[0]] = {'total': [[], group[1], 0],
                            'details': []}
    path = []

    def add_to_groups(groups, output, path, count, confidence,
                      impurity=None):
        """Adds instances to groups array

        """
        group = output
        if output not in groups:
            groups[group] = {'total': [[], 0, 0],
                             'details': []}
        groups[group]['details'].append([path, count, confidence,
                                         impurity])
        groups[group]['total'][2] += count

    def depth_first_search(tree, path):
        """Search for leafs' values and instances

        """
        node = get_node(tree)
        predicate = get_predicate(tree)
        if isinstance(predicate, list):
            [operation, field, value, term, _] = predicate
            operator = INVERSE_OP[operation]
            path.append(Predicate(operator, field, value, term))
            if term:
                if field not in model.terms:
                    model.terms[field] = []
                if term not in model.terms[field]:
                    model.terms[field].append(term)

        if node[offsets["children#"]] == 0:
            add_to_groups(groups, node[offsets["output"]],
                          path, node[offsets["count"]],
                          node[offsets["confidence"]],
                          gini_impurity(node[offsets["distribution"]],
                                        node[offsets["count"]]))
            return node[offsets["count"]]
        children = node[offsets["children"]][:]
        children.reverse()

        children_sum = 0
        for child in children:
            children_sum += depth_first_search(child, path[:])
        if children_sum < node[offsets["count"]]:
            add_to_groups(groups, node[offsets["output"]], path,
                          node[offsets["count"]] - children_sum,
                          node[offsets["confidence"]],
                          gini_impurity(node[offsets["distribution"]],
                                        node[offsets["count"]]))
        return node[offsets["count"]]

    depth_first_search(tree, path)

    return groups


def get_data_distribution(model):
    """Returns training data distribution

    """
    if model.boosting:
        raise AttributeError("This method is not available for boosting"
                             " models.")
    node = get_node(model.tree)

    distribution = node[model.offsets["distribution"]]

    return sorted(distribution, key=lambda x: x[0])


def get_prediction_distribution(model, groups=None):
    """Returns model predicted distribution

    """
    if model.boosting:
        raise AttributeError("This method is not available for boosting"
                             " models.")
    if groups is None:
        groups = group_prediction(model)

    predictions = [[group, groups[group]['total'][2]] for group in groups]
    # remove groups that are not predicted
    predictions = [prediction for prediction in predictions \
        if prediction[1] > 0]

    return sorted(predictions, key=lambda x: x[0])


def summarize(model, out=sys.stdout, format=BRIEF):
    """Prints summary grouping distribution as class header and details

    """
    if model.boosting:
        raise AttributeError("This method is not available for boosting"
                             " models.")
    tree = model.tree

    def extract_common_path(groups):
        """Extracts the common segment of the prediction path for a group

        """
        for group in groups:
            details = groups[group]['details']
            common_path = []
            if len(details) > 0:
                mcd_len = min([len(x[0]) for x in details])
                for i in range(0, mcd_len):
                    test_common_path = details[0][0][i]
                    for subgroup in details:
                        if subgroup[0][i] != test_common_path:
                            i = mcd_len
                            break
                    if i < mcd_len:
                        common_path.append(test_common_path)
            groups[group]['total'][0] = common_path
            if len(details) > 0:
                groups[group]['details'] = sorted(details,
                                                  key=lambda x: x[1],
                                                  reverse=True)

    def confidence_error(value, impurity=None):
        """Returns confidence for categoric objective fields
           and error for numeric objective fields
        """
        if value is None:
            return ""
        impurity_literal = ""
        if impurity is not None and impurity > 0:
            impurity_literal = "; impurity: %.2f%%" % (round(impurity, 4))
        objective_type = model.fields[model.objective_id]['optype']
        if objective_type == 'numeric':
            return " [Error: %s]" % value
        return " [Confidence: %.2f%%%s]" % (round(value, 4) * 100,
                                            impurity_literal)

    distribution = get_data_distribution(model)

    out.write(utf8("Data distribution:\n"))
    print_distribution(distribution, out=out)
    out.write(utf8("\n\n"))

    groups = group_prediction(model)
    predictions = get_prediction_distribution(model, groups)

    out.write(utf8("Predicted distribution:\n"))
    print_distribution(predictions, out=out)
    out.write(utf8("\n\n"))

    if model.field_importance:
        out.write(utf8("Field importance:\n"))
        print_importance(model, out=out)

    extract_common_path(groups)

    out.write(utf8("\n\nRules summary:"))

    node = get_node(tree)
    count = node[model.offsets["count"]]
    for group in [x[0] for x in predictions]:
        details = groups[group]['details']
        path = Path(groups[group]['total'][0])
        data_per_group = groups[group]['total'][1] * 1.0 / count
        pred_per_group = groups[group]['total'][2] * 1.0 / count
        out.write(utf8("\n\n%s : (data %.2f%% / prediction %.2f%%) %s" %
                       (group,
                        round(data_per_group, 4) * 100,
                        round(pred_per_group, 4) * 100,
                        path.to_rules(model.fields, format=format))))

        if len(details) == 0:
            out.write(utf8("\n    The model will never predict this"
                           " class\n"))
        elif len(details) == 1:
            subgroup = details[0]
            out.write(utf8("%s\n" % confidence_error(
                subgroup[2], impurity=subgroup[3])))
        else:
            out.write(utf8("\n"))
            for subgroup in details:
                pred_per_sgroup = subgroup[1] * 1.0 / \
                    groups[group]['total'][2]
                path = Path(subgroup[0])
                path_chain = path.to_rules(model.fields, format=format) if \
                    path.predicates else "(root node)"
                out.write(utf8("    · %.2f%%: %s%s\n" %
                               (round(pred_per_sgroup, 4) * 100,
                                path_chain,
                                confidence_error(subgroup[2],
                                                 impurity=subgroup[3]))))

    out.flush()


def get_nodes_info(model, headers, leaves_only=False):
    """Generator that yields the nodes information in a row format

    """
    if model.boosting:
        raise AttributeError("This method is not available for boosting"
                             " models.")

    def get_tree_nodes_info(tree, offsets, regression, fields, objective_id,
                            headers=None, leaves_only=False):
        """Yields the information associated to each of the tree nodes

        """
        row = []
        node = get_node(tree)
        if not regression:
            category_dict = dict(node[offsets["distribution"]])
        for header in headers:
            if header == fields[objective_id]['name']:
                row.append(node[offsets["output"]])
                continue
            if header in ['confidence', 'error']:
                row.append(node[offsets["confidence"]])
                continue
            if header == 'impurity':
                row.append(gini_impurity(node[offsets["distribution"]],
                                         node[offsets["count"]]))
                continue
            if regression and header.startswith('bin'):
                for bin_value, bin_instances in node[offsets["distribution"]]:
                    row.append(bin_value)
                    row.append(bin_instances)
                break
            if not regression:
                row.append(category_dict.get(header))
        while len(row) < len(headers):
            row.append(None)
        if not leaves_only or not tree.children:
            yield row

        if node[offsets["children#"]] > 0:
            for child in node[offsets["children"]]:
                for row in get_tree_nodes_info(child, offsets, regression,
                                               fields, objective_id, headers,
                                               leaves_only=leaves_only):
                    yield row

    return get_tree_nodes_info(model.tree,
                               model.offsets,
                               model.regression,
                               model.fields,
                               model.objective_id,
                               headers, leaves_only=leaves_only)


def tree_csv(model, file_name=None, leaves_only=False):
    """Outputs the node structure to a CSV file or array

    """
    if model.boosting:
        raise AttributeError("This method is not available for boosting"
                             " models.")
    headers_names = []
    if model.regression:
        headers_names.append(
            model.fields[model.objective_id]['name'])
        headers_names.append("error")
        max_bins = get_node(model.tree)[model.offsets["max_bins"]]
        for index in range(0, max_bins):
            headers_names.append("bin%s_value" % index)
            headers_names.append("bin%s_instances" % index)
    else:
        headers_names.append(
            model.fields[model.objective_id]['name'])
        headers_names.append("confidence")
        headers_names.append("impurity")
        node = get_node(model.tree)
        for category, _ in node[model.offsets["distribution"]]:
            headers_names.append(category)

    nodes_generator = get_nodes_info(model, headers_names,
                                     leaves_only=leaves_only)
    if file_name is not None:
        with UnicodeWriter(file_name) as writer:
            writer.writerow([utf8(header)
                             for header in headers_names])
            for row in nodes_generator:
                writer.writerow([item if not isinstance(item, str)
                                 else utf8(item)
                                 for item in row])
        return file_name
    rows = []
    rows.append(headers_names)
    for row in nodes_generator:
        rows.append(row)
    return rows
