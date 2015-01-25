# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2013-2015 BigML
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

"""Tree structure for the BigML local Model

This module defines an auxiliary Tree structure that is used in the local Model
to make predictions locally or embedded into your application without needing
to send requests to BigML.io.

"""
import keyword
import numbers
import math

try:
    from scipy import stats
except ImportError:
    pass

from bigml.predicate import Predicate
from bigml.predicate import TM_TOKENS, TM_FULL_TERM, TM_ALL
from bigml.util import sort_fields, slugify, split, utf8
from bigml.multivote import ws_confidence


# Map operator str to its corresponding python operator
PYTHON_OPERATOR = {
    "<": "<",
    "<=": "<=",
    "=": "==",
    "!=": "!=",
    "/=": "!=",
    ">=": ">=",
    ">": ">"
}

MISSING_OPERATOR = {
    "=": "is",
    "!=": "is not"
}

T_MISSING_OPERATOR = {
    "=": "ISNULL(",
    "!=": "NOT ISNULL("
}


MAX_ARGS_LENGTH = 10

INDENT = u'    '

TERM_OPTIONS = ["case_sensitive", "token_mode"]

LAST_PREDICTION = 0
PROPORTIONAL = 1
BINS_LIMIT = 32


def get_instances(distribution):
    """Returns the total number of instances in a distribution

    """
    return sum(x[1] for x in distribution) if distribution else 0


def merge_distributions(distribution, new_distribution):
    """Adds up a new distribution structure to a map formatted distribution

    """
    for value, instances in new_distribution.items():
        if not value in distribution:
            distribution[value] = 0
        distribution[value] += instances
    return distribution


def merge_bins(distribution, limit):
    """Merges the bins of a regression distribution to the given limit number

    """
    length = len(distribution)
    if limit < 1 or length <= limit or length < 2:
        return distribution
    index_to_merge = 2
    shortest = float('inf')
    for index in range(1, length):
        distance = distribution[index][0] - distribution[index - 1][0]
        if distance < shortest:
            shortest = distance
            index_to_merge = index
    new_distribution = distribution[: index_to_merge - 1]
    left = distribution[index_to_merge - 1]
    right = distribution[index_to_merge]
    new_bin = [(left[0] * left[1] + right[0] * right[1]) /
               (left[1] + right[1]), left[1] + right[1]]
    new_distribution.append(new_bin)
    if index_to_merge < (length - 1):
        new_distribution.extend(distribution[(index_to_merge + 1):])
    return merge_bins(new_distribution, limit)


def mean(distribution):
    """Computes the mean of a distribution in the [[point, instances]] syntax

    """
    addition = 0.0
    count = 0.0
    for point, instances in distribution:
        addition += point * instances
        count += instances
    if count > 0:
        return addition / count
    return float('nan')


def unbiased_sample_variance(distribution, distribution_mean=None):
    """Computes the standard deviation of a distribution in the
       [[point, instances]] syntax

    """
    addition = 0.0
    count = 0.0
    if (distribution_mean is None or not
            isinstance(distribution_mean, numbers.Number)):
        distribution_mean = mean(distribution)
    for point, instances in distribution:
        addition += ((point - distribution_mean) ** 2) * instances
        count += instances
    if count > 1:
        return addition / (count - 1)
    return float('nan')


def regression_error(distribution_variance, population, r_z=1.96):
    """Computes the variance error

    """
    if population > 0:
        chi_distribution = stats.chi2(population)
        ppf = chi_distribution.ppf(1 - math.erf(r_z / math.sqrt(2)))
        if ppf != 0:
            error = distribution_variance * (population - 1) / ppf
            error = error * ((math.sqrt(population) + r_z) ** 2)
            return math.sqrt(error / population)
    return float('nan')


def tableau_string(text):
    """Transforms to a string representation in Tableau

    """
    value = repr(text)
    if isinstance(text, unicode):
        return value[1:]
    return value


def filter_nodes(nodes_list, ids=None, subtree=True):
    """Filters the contents of a nodes_list. If any of the nodes is in the
       ids list, the rest of nodes are removed. If none is in the ids list
       we include or exclude the nodes depending on the subtree flag.

    """
    if not nodes_list:
        return None
    nodes = nodes_list[:]
    if ids is not None:
        for node in nodes:
            if node.id in ids:
                nodes = [node]
                return nodes
    if not subtree:
        nodes = []
    return nodes


def missing_branch(children):
    """Checks if the missing values are assigned to a special branch

    """
    return any([child.predicate.missing for child in children])


def none_value(children):
    """Checks if the predicate has a None value

    """
    return any([child.predicate.value is None for child in children])


def one_branch(children, input_data):
    """Check if there's only one branch to be followed

    """
    missing = split(children) in input_data
    return (missing or missing_branch(children)
            or none_value(children))


class Tree(object):
    """A tree-like predictive model.

    """
    def __init__(self, tree, fields, objective_field=None,
                 root_distribution=None, parent_id=None, ids_map=None,
                 subtree=True):

        self.fields = fields
        self.objective_id = objective_field
        self.output = tree['output']

        if tree['predicate'] is True:
            self.predicate = True
        else:
            self.predicate = Predicate(
                tree['predicate']['operator'],
                tree['predicate']['field'],
                tree['predicate']['value'],
                tree['predicate'].get('term', None))
        if 'id' in tree:
            self.id = tree['id']
            self.parent_id = parent_id
            if isinstance(ids_map, dict):
                ids_map[self.id] = self
        else:
            self.id = None

        children = []
        if 'children' in tree:
            for child in tree['children']:
                children.append(Tree(child,
                                     self.fields,
                                     objective_field=objective_field,
                                     parent_id=self.id,
                                     ids_map=ids_map,
                                     subtree=subtree))

        self.children = children
        self.regression = self.is_regression()
        self.count = tree['count']
        self.confidence = tree.get('confidence', None)
        self.distribution = None
        if 'distribution' in tree:
            self.distribution = tree['distribution']
        elif 'objective_summary' in tree:
            summary = tree['objective_summary']
            if 'bins' in summary:
                self.distribution = summary['bins']
            elif 'counts' in summary:
                self.distribution = summary['counts']
            elif 'categories' in summary:
                self.distribution = summary['categories']
        else:
            summary = root_distribution
            if 'bins' in summary:
                self.distribution = summary['bins']
            elif 'counts' in summary:
                self.distribution = summary['counts']
            elif 'categories' in summary:
                self.distribution = summary['categories']
        self.impurity = None
        if not self.regression and self.distribution is not None:
            self.impurity = self.gini_impurity()

    def gini_impurity(self):
        """Returns the gini impurity score associated to the distribution
           in the node

        """
        purity = 0.0
        if self.distribution is None:
            return None
        for category, instances in self.distribution:
           purity += math.pow(instances / float(self.count), 2)
        return (1.0 - purity) / 2

    def list_fields(self, out):
        """Lists a description of the model's fields.

        """
        out.write(utf8(u'<%-32s : %s>\n' % (
            self.fields[self.objective_id]['name'],
            self.fields[self.objective_id]['optype'])))
        out.flush()

        for field in [(val['name'], val['optype']) for key, val in
                      sort_fields(self.fields)
                      if key != self.objective_id]:
            out.write(utf8(u'[%-32s : %s]\n' % (field[0], field[1])))
            out.flush()
        return self.fields

    def is_regression(self):
        """Checks if the subtree structure can be a regression

        """
        def is_classification(node):
            """Checks if the node's value is a category

            """
            return isinstance(node.output, basestring)

        classification = is_classification(self)
        if classification:
            return False
        if not self.children:
            return True
        else:
            return not any([is_classification(child)
                            for child in self.children])

    def get_leaves(self, path=None, filter_function=None):
        """Returns a list that includes all the leaves of the tree.

        """
        leaves = []
        if path is None:
            path = []
        if not isinstance(self.predicate, bool):
            path.append(self.predicate.to_LISP_rule(self.fields))

        if self.children:
            for child in self.children:
                leaves += child.get_leaves(path=path[:],
                                           filter_function=filter_function)
        else:
            leaf = {
                    'id': self.id,
                    'confidence': self.confidence,
                    'count': self.count,
                    'distribution': self.distribution,
                    'impurity': self.impurity,
                    'output': self.output,
                    'path': path}
            if (not hasattr(filter_function, '__call__')
                    or filter_function(leaf)):
                leaves += [leaf]
        return leaves

    def predict(self, input_data, path=None, missing_strategy=LAST_PREDICTION):
        """Makes a prediction based on a number of field values.

        The input fields must be keyed by Id. There are two possible
        strategies to predict when the value for the splitting field
        is missing:
            0 - LAST_PREDICTION: the last issued prediction is returned.
            1 - PROPORTIONAL: as we cannot choose between the two branches
                in the tree that stem from this split, we consider both. The
                algorithm goes on until the final leaves are reached and
                all their predictions are used to decide the final prediction.
        """

        if path is None:
            path = []
        if missing_strategy == PROPORTIONAL:
            (final_distribution,
             last_node) = self.predict_proportional(input_data, path=path)

            if self.regression:
                # singular case:
                # when the prediction is the one given in a 1-instance node
                if len(final_distribution.items()) == 1:
                    prediction, instances = final_distribution.items()[0]
                    if instances == 1:
                        return (last_node.output, path, last_node.confidence,
                                last_node.distribution, instances)               
                # when there's more instances, sort elements by their mean
                distribution = [list(element) for element in
                                sorted(final_distribution.items(),
                                       key=lambda x: x[0])]
                distribution = merge_bins(distribution, BINS_LIMIT)
                prediction = mean(distribution)
                total_instances = sum([instances
                                       for _, instances in distribution])
                confidence = regression_error(
                    unbiased_sample_variance(distribution, prediction),
                    total_instances)
                return (prediction, path, confidence,
                        distribution, total_instances)
            else:
                distribution = [list(element) for element in
                                sorted(final_distribution.items(),
                                       key=lambda x: (-x[1], x[0]))]
                return (distribution[0][0], path,
                        ws_confidence(distribution[0][0], final_distribution),
                        distribution, get_instances(distribution))

        else:
            if self.children:
                for child in self.children:
                    if child.predicate.apply(input_data, self.fields):
                        path.append(child.predicate.to_rule(self.fields))
                        return child.predict(input_data, path)
            return (self.output, path, self.confidence,
                    self.distribution, get_instances(self.distribution))

    def predict_proportional(self, input_data, path=None, missing_found=False):
        """Makes a prediction based on a number of field values averaging
           the predictions of the leaves that fall in a subtree.

           Each time a splitting field has no value assigned, we consider
           both branches of the split to be true, merging their
           predictions. The function returns the merged distribution and the
           last node reached by a unique path.

        """

        if path is None:
            path = []

        final_distribution = {}
        if not self.children:
            return (merge_distributions({}, dict((x[0], x[1])
                                                 for x in self.distribution)),
                    self)
        if one_branch(self.children, input_data):
            for child in self.children:
                if child.predicate.apply(input_data, self.fields):
                    new_rule = child.predicate.to_rule(self.fields)
                    if not new_rule in path and not missing_found:
                        path.append(new_rule)
                    return child.predict_proportional(input_data, path,
                                                      missing_found)
        else:
            # missing value found, the unique path stops
            missing_found = True
            for child in self.children:
                final_distribution = merge_distributions(
                    final_distribution,
                    child.predict_proportional(input_data, path,
                                               missing_found)[0])
            return final_distribution, self

    def generate_rules(self, depth=0, ids_path=None, subtree=True):
        """Translates a tree model into a set of IF-THEN rules.

        """
        rules = u""
        children = filter_nodes(self.children, ids=ids_path,
                                subtree=subtree)
        if children:
            for child in children:
                rules += (u"%s IF %s %s\n" %
                          (INDENT * depth,
                           child.predicate.to_rule(self.fields, 'slug'),
                           "AND" if child.children else "THEN"))
                rules += child.generate_rules(depth + 1, ids_path=ids_path,
                                              subtree=subtree)
        else:
            rules += (u"%s %s = %s\n" %
                      (INDENT * depth,
                       (self.fields[self.objective_id]['slug']
                        if self.objective_id else "Prediction"),
                       self.output))
        return rules

    def rules(self, out, ids_path=None, subtree=True):
        """Prints out an IF-THEN rule version of the tree.

        """
        for field in [(key, val) for key, val in sort_fields(self.fields)]:

            slug = slugify(self.fields[field[0]]['name'])
            self.fields[field[0]].update(slug=slug)
        out.write(utf8(self.generate_rules(ids_path=ids_path,
                                           subtree=subtree)))
        out.flush()

    def python_body(self, depth=1, cmv=None, input_map=False,
                    ids_path=None, subtree=True):
        """Translate the model into a set of "if" python statements.

        `depth` controls the size of indentation. As soon as a value is missing
        that node is returned without further evaluation.

        """

        def map_data(field, missing=False):
            """Returns the subject of the condition in map format when
               more than MAX_ARGS_LENGTH arguments are used.
            """
            if input_map:
                if missing:
                    return "data.get('%s')" % field
                else:
                    return "data['%s']" % field
            return field
        if cmv is None:
            cmv = []
        body = u""
        term_analysis_fields = []
        children = filter_nodes(self.children, ids=ids_path,
                                subtree=subtree)
        if children:
            field = split(children)
            has_missing_branch = (missing_branch(children) or
                                  none_value(children))
            # the missing is singled out as a special case only when there's
            # no missing branch in the children list
            if (not has_missing_branch and
                not self.fields[field]['slug'] in cmv):
                body += (u"%sif (%s is None):\n" %
                         (INDENT * depth,
                          map_data(self.fields[field]['slug'], True)))
                if self.fields[self.objective_id]['optype'] == 'numeric':
                    value = self.output
                else:
                    value = repr(self.output)
                body += (u"%sreturn %s\n" %
                         (INDENT * (depth + 1),
                          value))
                cmv.append(self.fields[field]['slug'])

            for child in children:
                field = child.predicate.field
                pre_condition = u""
                if has_missing_branch and child.predicate.value is not None:
                    negation = u"" if child.predicate.missing else u" not"
                    connection = u"or" if child.predicate.missing else u"and"
                    pre_condition = (u"%s is%s None %s " % (
                                     map_data(self.fields[field]['slug'],
                                              True),
                                     negation,
                                     connection))
                    if not child.predicate.missing:
                        cmv.append(self.fields[field]['slug'])
                optype = self.fields[field]['optype']
                if (optype == 'numeric' or optype == 'text' or
                    child.predicate.value is None):
                    value = child.predicate.value
                else:
                    value = repr(child.predicate.value)
                if optype == 'text':
                    body += (
                        u"%sif (%sterm_matches(%s, \"%s\", %s\"%s\") %s %s):"
                        u"\n" %
                        (INDENT * depth, pre_condition,
                         map_data(self.fields[field]['slug'],
                                  False),
                         self.fields[field]['slug'],
                         ('u' if isinstance(child.predicate.term, unicode)
                          else ''),
                         child.predicate.term.replace("\"", "\\\""),
                         PYTHON_OPERATOR[child.predicate.operator],
                         value))
                    term_analysis_fields.append((field,
                                                 child.predicate.term))
                else:
                    operator = (MISSING_OPERATOR[child.predicate.operator] if
                                child.predicate.value is None else
                                PYTHON_OPERATOR[child.predicate.operator])
                    if child.predicate.value is None:
                        cmv.append(self.fields[field]['slug'])
                    body += (
                        u"%sif (%s%s %s %s):\n" %
                        (INDENT * depth, pre_condition,
                         map_data(self.fields[field]['slug'],
                                  False),
                         operator,
                         value))
                next_level = child.python_body(depth + 1, cmv=cmv[:],
                                               input_map=input_map,
                                               ids_path=ids_path,
                                               subtree=subtree)
                body += next_level[0]
                term_analysis_fields.extend(next_level[1])
        else:
            if self.fields[self.objective_id]['optype'] == 'numeric':
                value = self.output
            else:
                value = repr(self.output)
            body = u"%sreturn %s\n" % (INDENT * depth, value)

        return body, term_analysis_fields

    def python(self, out, docstring, input_map=False,
               ids_path=None, subtree=True):
        """Writes a python function that implements the model.

        """
        args = []
        parameters = sort_fields(self.fields)
        if not input_map:
            input_map = len(parameters) > MAX_ARGS_LENGTH
        reserved_keywords = keyword.kwlist if not input_map else None
        prefix = "_" if not input_map else ""
        for field in [(key, val) for key, val in parameters]:
            slug = slugify(self.fields[field[0]]['name'],
                           reserved_keywords=reserved_keywords, prefix=prefix)
            self.fields[field[0]].update(slug=slug)
            if not input_map:
                if field[0] != self.objective_id:
                    args.append("%s=None" % (slug))
        if input_map:
            args.append("data={}")
        predictor_definition = (u"def predict_%s" %
                                self.fields[self.objective_id]['slug'])
        depth = len(predictor_definition) + 1
        predictor = u"%s(%s):\n" % (
            predictor_definition,
            (",\n" + " " * depth).join(args))
        predictor_doc = (INDENT + u"\"\"\" " + docstring +
                         u"\n" + INDENT + u"\"\"\"\n")
        body, term_analysis_predicates = self.python_body(input_map=input_map,
                                                          ids_path=ids_path,
                                                          subtree=subtree)
        terms_body = ""
        if term_analysis_predicates:
            terms_body = self.term_analysis_body(term_analysis_predicates)
        predictor += predictor_doc + terms_body + body
        out.write(utf8(predictor))
        out.flush()

    def term_analysis_body(self, term_analysis_predicates):
        """ Writes auxiliary functions to handle the term analysis fields

        """
        body = u""
        # static content
        body += """
    import re

    tm_tokens = '%s'
    tm_full_term = '%s'
    tm_all = '%s'


    def term_matches(text, field_name, term):
        \"\"\" Counts the number of occurences of term and its variants in text

        \"\"\"
        forms_list = term_forms[field_name].get(term, [term])
        options = term_analysis[field_name]
        token_mode = options.get('token_mode', tm_tokens)
        case_sensitive = options.get('case_sensitive', False)
        first_term = forms_list[0]
        if token_mode == tm_full_term:
            return full_term_match(text, first_term, case_sensitive)
        else:
            # In token_mode='all' we will match full terms using equals and
            # tokens using contains
            if token_mode == tm_all and len(forms_list) == 1:
                pattern = re.compile(r'^.+\\b.+$', re.U)
                if re.match(pattern, first_term):
                    return full_term_match(text, first_term, case_sensitive)
            return term_matches_tokens(text, forms_list, case_sensitive)


    def full_term_match(text, full_term, case_sensitive):
        \"\"\"Counts the match for full terms according to the case_sensitive
              option

        \"\"\"
        if not case_sensitive:
            text = text.lower()
            full_term = full_term.lower()
        return 1 if text == full_term else 0

    def get_tokens_flags(case_sensitive):
        \"\"\"Returns flags for regular expression matching depending on text
              analysis options

        \"\"\"
        flags = re.U
        if not case_sensitive:
            flags = (re.I | flags)
        return flags


    def term_matches_tokens(text, forms_list, case_sensitive):
        \"\"\" Counts the number of occurences of the words in forms_list in
               the text

        \"\"\"
        flags = get_tokens_flags(case_sensitive)
        expression = ur'(\\b|_)%%s(\\b|_)' %% '(\\\\b|_)|(\\\\b|_)'.join(forms_list)
        pattern = re.compile(expression, flags=flags)
        matches = re.findall(pattern, text)
        return len(matches)
""" % (TM_TOKENS, TM_FULL_TERM, TM_ALL)

        term_analysis_options = set(map(lambda x: x[0],
                                        term_analysis_predicates))
        term_analysis_predicates = set(term_analysis_predicates)
        body += """
    term_analysis = {"""
        for field_id in term_analysis_options:
            field = self.fields[field_id]
            body += """
        \"%s\": {""" % field['slug']
            for option in field['term_analysis']:
                if option in TERM_OPTIONS:
                    body += """
                \"%s\": %s,""" % (option, repr(field['term_analysis'][option]))
            body += """
        },"""
        body += """
    }"""
        if term_analysis_predicates:
            term_forms = {}
            fields = self.fields
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
            body += """
    term_forms = {"""
            for field in term_forms:
                body += """
        \"%s\": {""" % field
                for term in term_forms[field]:
                    body += """
            u\"%s\": %s,""" % (term, term_forms[field][term])
                body += """
        },
                """
            body += """
    }
"""

        return body

    def tableau_body(self, body=u"", conditions=None, cmv=None,
                     ids_path=None, subtree=True):
        """Translate the model into a set of "if" statements in Tableau syntax

        `depth` controls the size of indentation. As soon as a value is missing
        that node is returned without further evaluation.

        """

        if cmv is None:
            cmv = []
        if body:
            alternate = u"ELSEIF"
        else:
            if conditions is None:
                conditions = []
            alternate = u"IF"

        children = filter_nodes(self.children, ids=ids_path,
                                subtree=subtree)
        if children:
            field = split(children)
            has_missing_branch = (missing_branch(children) or
                                  none_value(children))
            # the missing is singled out as a special case only when there's
            # no missing branch in the children list
            if (not has_missing_branch and
                    not self.fields[field]['name'] in cmv):
                conditions.append("ISNULL([%s])" % self.fields[field]['name'])
                body += (u"%s %s THEN " %
                         (alternate, " AND ".join(conditions)))
                if self.fields[self.objective_id]['optype'] == 'numeric':
                    value = self.output
                else:
                    value = tableau_string(self.output)
                body += (u"%s\n" % value)
                cmv.append(self.fields[field]['name'])
                alternate = u"ELSEIF"
                del conditions[-1]

            for child in children:
                pre_condition = u""
                post_condition = u""
                if has_missing_branch and child.predicate.value is not None:
                    negation = u"" if child.predicate.missing else u"NOT "
                    connection = u"OR" if child.predicate.missing else u"AND"
                    pre_condition = (u"(%sISNULL([%s]) %s " % (
                                     negation, self.fields[field]['name'],
                                     connection))
                    if not child.predicate.missing:
                        cmv.append(self.fields[field]['name'])
                    post_condition = u")"
                optype = self.fields[child.predicate.field]['optype']
                if child.predicate.value is None:
                    value = ""
                elif optype == 'text':
                    return u""
                elif optype == 'numeric':
                    value = child.predicate.value
                else:
                    value = repr(child.predicate.value)

                operator = ("" if child.predicate.value is None else
                            PYTHON_OPERATOR[child.predicate.operator])
                if child.predicate.value is None:
                    pre_condition = (
                        T_MISSING_OPERATOR[child.predicate.operator])
                    post_condition = ")"

                conditions.append("%s[%s]%s%s%s" % (
                    pre_condition,
                    self.fields[child.predicate.field]['name'],
                    operator,
                    value,
                    post_condition))
                body = child.tableau_body(body, conditions[:], cmv=cmv[:],
                                          ids_path=ids_path, subtree=subtree)
                del conditions[-1]
        else:
            if self.fields[self.objective_id]['optype'] == 'numeric':
                value = self.output
            else:
                value = tableau_string(self.output)
            body += (
                u"%s %s THEN" % (alternate, " AND ".join(conditions)))
            body += u" %s\n" % value

        return body

    def tableau(self, out, ids_path=None, subtree=True):
        """Writes a Tableau function that implements the model.

        """
        body = self.tableau_body(ids_path=ids_path, subtree=subtree)
        if not body:
            return False
        out.write(utf8(body))
        out.flush()
        return True

    def get_nodes_info(self, headers=None, leaves_only=False):
        """Yields the information associated to each of the tree nodes

        """
        row = []
        if not self.regression:
            category_dict = dict(self.distribution)
        for header in headers:
            if header == self.fields[self.objective_id]['name']:
                row.append(self.output)
                continue
            if header in ['confidence', 'error']:
                row.append(self.confidence)
                continue
            if header == 'impurity':
                row.append(self.impurity)
                continue
            if self.regression and header.startswith('bin'):
                for bin_value, bin_instances in self.distribution:
                    row.append(bin_value)
                    row.append(bin_instances)
                break
            if not self.regression:
                row.append(category_dict.get(header))
        while len(row) < len(headers):
            row.append(None)
        if not leaves_only or not self.children:
            yield row

        if self.children:
            for child in self.children:
                for row in child.get_nodes_info(headers,
                                                leaves_only=leaves_only):
                    yield row
