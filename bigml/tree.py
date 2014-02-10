# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2013-2014 BigML
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


def tableau_string(text):
    """Transforms to a string representation in Tableau

    """
    value = repr(text)
    if isinstance(text, unicode):
        return value[1:]


class Tree(object):
    """A tree-like predictive model.

    """
    def __init__(self, tree, fields, objective_field=None,
                 root_distribution=None):

        self.fields = fields
        self.objective_field = objective_field
        self.output = tree['output']

        if tree['predicate'] is True:
            self.predicate = True
        else:
            self.predicate = Predicate(
                tree['predicate']['operator'],
                tree['predicate']['field'],
                tree['predicate']['value'],
                tree['predicate'].get('term', None))

        children = []
        if 'children' in tree:
            for child in tree['children']:
                children.append(Tree(child, self.fields, objective_field))

        self.children = children
        self.count = tree['count']
        self.confidence = tree.get('confidence', None)
        if 'distribution' in tree:
            self.distribution = tree['distribution']
        elif ('objective_summary' in tree):
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

    def list_fields(self, out):
        """Lists a description of the model's fields.

        """
        out.write(utf8(u'<%-32s : %s>\n' % (
            self.fields[self.objective_field]['name'],
            self.fields[self.objective_field]['optype'])))
        out.flush()

        for field in [(val['name'], val['optype']) for key, val in
                      sort_fields(self.fields)
                      if key != self.objective_field]:
            out.write(utf8(u'[%-32s : %s]\n' % (field[0], field[1])))
            out.flush()
        return self.fields

    def get_leaves(self):
        """Returns a list that includes all the leaves of the tree.

        """
        leaves = []

        if self.children:
            for child in self.children:
                leaves += child.get_leaves()
        else:
            leaves += [{
                'confidence': self.confidence,
                'count': self.count,
                'distribution': self.distribution,
                'output': self.output
            }]
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
            final_distribution = self.predict_proportional(input_data,
                                                           path=path)
            is_regression = all([not isinstance(category, basestring) for
                                 category in final_distribution])

            if is_regression:
                # sort elements by their mean
                distribution = [list(element) for element in
                                sorted(final_distribution.items(),
                                       key=lambda x: x[0])]
                distribution = merge_bins(distribution, BINS_LIMIT)
                predictions = []
                total_instances = []
                for prediction, instances in distribution:
                    predictions.append(prediction)
                    total_instances.append(instances)
                prediction = sum(predictions) / sum(total_instances)
                confidence = None
                return (prediction, path, confidence,
                        distribution, total_instances)
            else:
                distribution = [list(element) for element in
                                sorted(final_distribution.items(),
                                       key=lambda x: -x[1])]
                return (distribution[0][0], path,
                        ws_confidence(distribution[0][0], final_distribution),
                        distribution, get_instances(distribution))

        else:
            if self.children and split(self.children) in input_data:
                for child in self.children:
                    if child.predicate.apply(input_data, self.fields):
                        path.append(child.predicate.to_rule(self.fields))
                        return child.predict(input_data, path)
            return (self.output, path, self.confidence,
                    self.distribution, get_instances(self.distribution))

    def predict_proportional(self, input_data, path=None):
        """Makes a prediction based on a number of field values averaging
           the predictions of the leaves that fall in a subtree.

           Each time a splitting field has no value assigned, we consider
           both branches of the split to be true, merging their
           predictions.

        """

        if path is None:
            path = []

        final_distribution = {}
        if not self.children:
            return merge_distributions({}, dict((x[0], x[1])
                                                for x in self.distribution))
        if split(self.children) in input_data:
            for child in self.children:
                if child.predicate.apply(input_data, self.fields):
                    new_rule = child.predicate.to_rule(self.fields)
                    if not new_rule in path:
                        path.append(new_rule)
                    return child.predict_proportional(input_data, path)
        else:
            for child in self.children:
                final_distribution = merge_distributions(
                    final_distribution,
                    child.predict_proportional(input_data, path))
            return final_distribution

    def generate_rules(self, depth=0):
        """Translates a tree model into a set of IF-THEN rules.

        """
        rules = u""
        if self.children:
            for child in self.children:
                rules += (u"%s IF %s %s\n" %
                         (INDENT * depth,
                          child.predicate.to_rule(self.fields, 'slug'),
                          "AND" if child.children else "THEN"))
                rules += child.generate_rules(depth + 1)
        else:
            rules += (u"%s %s = %s\n" %
                     (INDENT * depth,
                      (self.fields[self.objective_field]['slug']
                       if self.objective_field else "Prediction"),
                      self.output))
        return rules

    def rules(self, out):
        """Prints out an IF-THEN rule version of the tree.

        """
        for field in [(key, val) for key, val in sort_fields(self.fields)]:

            slug = slugify(self.fields[field[0]]['name'])
            self.fields[field[0]].update(slug=slug)
        out.write(utf8(self.generate_rules()))
        out.flush()

    def python_body(self, depth=1, cmv=None, input_map=False):
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
                    return "not '%s' in data or data['%s']" % (field, field)
                else:
                    return "data['%s']" % field
            return field
        if cmv is None:
            cmv = []
        body = u""
        term_analysis_fields = []
        if self.children:
            field = split(self.children)
            if not self.fields[field]['slug'] in cmv:
                body += (u"%sif (%s is None):\n" %
                        (INDENT * depth,
                         map_data(self.fields[field]['slug'], True)))
                if self.fields[self.objective_field]['optype'] == 'numeric':
                    value = self.output
                else:
                    value = repr(self.output)
                body += (u"%sreturn %s\n" %
                        (INDENT * (depth + 1),
                         value))
                cmv.append(self.fields[field]['slug'])

            for child in self.children:
                optype = self.fields[child.predicate.field]['optype']
                if (optype == 'numeric' or optype == 'text'):
                    value = child.predicate.value
                else:
                    value = repr(child.predicate.value)
                if optype == 'text':
                    body += (
                        u"%sif (term_matches(%s, \"%s\", %s\"%s\") %s %s):\n" %
                        (INDENT * depth,
                         map_data(self.fields[child.predicate.field]['slug'],
                         False),
                         self.fields[child.predicate.field]['slug'],
                         ('u' if isinstance(child.predicate.term, unicode)
                          else ''),
                         child.predicate.term.replace("\"", "\\\""),
                         PYTHON_OPERATOR[child.predicate.operator],
                         value))
                    term_analysis_fields.append((child.predicate.field,
                                                 child.predicate.term))
                else:
                    body += (
                        u"%sif (%s %s %s):\n" %
                        (INDENT * depth,
                         map_data(self.fields[child.predicate.field]['slug'],
                         False),
                         PYTHON_OPERATOR[child.predicate.operator],
                         value))
                next_level = child.python_body(depth + 1, cmv=cmv[:],
                                               input_map=input_map)
                body += next_level[0]
                term_analysis_fields.extend(next_level[1])
        else:
            if self.fields[self.objective_field]['optype'] == 'numeric':
                value = self.output
            else:
                value = repr(self.output)
            body = u"%sreturn %s\n" % (INDENT * depth, value)

        return body, term_analysis_fields

    def python(self, out, docstring, input_map=False):
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
                if field[0] != self.objective_field:
                    args.append("%s=None" % (slug))
        if input_map:
            args.append("data={}")
        predictor_definition = (u"def predict_%s" %
                                self.fields[self.objective_field]['slug'])
        depth = len(predictor_definition) + 1
        predictor = u"%s(%s):\n" % (predictor_definition,
                                   (",\n" + " " * depth).join(args))
        predictor_doc = (INDENT + u"\"\"\" " + docstring +
                         u"\n" + INDENT + u"\"\"\"\n")
        body, term_analysis_predicates = self.python_body(input_map=input_map)
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

    def tableau_body(self, body=u"", conditions=None, cmv=None):
        """Translate the model into a set of "if" statements in Tableau syntax

        `depth` controls the size of indentation. As soon as a value is missing
        that node is returned without further evaluation.

        """

        if cmv is None:
            cmv = []
        if conditions is None:
            conditions = []
            alternate = u"IF"
        else:
            alternate = u"ELSEIF"

        if self.children:
            field = split(self.children)
            if not self.fields[field]['name'] in cmv:
                conditions.append("ISNULL([%s])" % self.fields[field]['name'])
                body += (u"%s %s THEN " %
                         (alternate, " AND ".join(conditions)))
                if self.fields[self.objective_field]['optype'] == 'numeric':
                    value = self.output
                else:
                    value = tableau_string(self.output) 
                body += (u"%s\n" % value)
                cmv.append(self.fields[field]['name'])
                alternate = u"ELSEIF"
                del conditions[-1]

            for child in self.children:
                optype = self.fields[child.predicate.field]['optype']
                if optype == 'text':
                    return u""
                if (optype == 'numeric'):
                    value = child.predicate.value
                else:
                    value = repr(child.predicate.value)
                conditions.append("[%s]%s%s" % (
                    self.fields[child.predicate.field]['name'],
                    PYTHON_OPERATOR[child.predicate.operator],
                    value))
                body = child.tableau_body(body, conditions[:], cmv=cmv[:])
                del conditions[-1]
        else:
            if self.fields[self.objective_field]['optype'] == 'numeric':
                value = self.output
            else:
                value = tableau_string(self.output) 
            body += (
                u"%s %s THEN" % (alternate, " AND ".join(conditions)))
            body += u" %s\n" % value

        return body

    def tableau(self, out):
        """Writes a Tableau function that implements the model.

        """
        body = self.tableau_body()
        if not body:
            return False
        out.write(utf8(body))
        out.flush()
        return True
