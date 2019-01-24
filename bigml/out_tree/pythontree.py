# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2017-2019 BigML
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
    slugify, sort_fields, filter_nodes, missing_branch, none_value,
    one_branch, split, MAX_ARGS_LENGTH, INDENT, PYTHON_OPERATOR, TM_TOKENS,
    TM_FULL_TERM, TM_ALL, TERM_OPTIONS, ITEM_OPTIONS, COMPOSED_FIELDS,
    NUMERIC_VALUE_FIELDS)

from bigml.tree import Tree
from bigml.boostedtree import BoostedTree

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
    return u"\"%s\"" % value.replace('"', '\\"')


def map_data(field, input_map=False, missing=False):
    """Returns the subject of the condition in map format when
       more than MAX_ARGS_LENGTH arguments are used.
    """
    if input_map:
        if missing:
            return "data.get('%s')" % field
        else:
            return "data['%s']" % field
    return field


def missing_prefix_code(self, field, input_map, cmv):
    """Part of the condition that checks for missings when missing_splits
    has been used

    """

    negation = u"" if self.predicate.missing else u" not"
    connection = u"or" if self.predicate.missing else u"and"
    if not self.predicate.missing:
        cmv.append(self.fields[field]['slug'])
    return u"%s is%s None %s " % (map_data(self.fields[field]['slug'],
                                           input_map,
                                           True),
                                  negation,
                                  connection)


def split_condition_code(self, field, depth, input_map,
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

        return u"%sif (%s%s(%s, \"%s\", %s%s) %s " \
               u"%s):\n" % \
              (INDENT * depth, pre_condition, matching_function,
               map_data(self.fields[field]['slug'],
                        input_map,
                        False),
               self.fields[self.predicate.field]['slug'],
               'u' if isinstance(self.predicate.term, unicode) else '',
               value_to_print(self.predicate.term, 'categorical'),
               PYTHON_OPERATOR[self.predicate.operator],
               value)

    operator = (MISSING_OPERATOR[self.predicate.operator] if
                self.predicate.value is None else
                PYTHON_OPERATOR[self.predicate.operator])
    if self.predicate.value is None:
        cmv.append(self.fields[field]['slug'])
    return u"%sif (%s%s %s %s):\n" % \
           (INDENT * depth, pre_condition,
            map_data(self.fields[field]['slug'], input_map,
                     False),
            operator,
            value)



class PythonTree(Tree):

    def missing_check_code(self, field, depth, input_map, cmv, metric):
        """Builds the code to predict when the field is missing

        """
        code = u"%sif (%s is None):\n" % \
               (INDENT * depth,
                map_data(self.fields[field]['slug'], input_map, True))
        value = value_to_print(self.output,
                               self.fields[self.objective_id]['optype'])
        code += u"%sreturn {\"prediction\": %s," \
            u" \"%s\": %s}\n" % \
            (INDENT * (depth + 1), value, metric, self.confidence)
        cmv.append(self.fields[field]['slug'])
        return code


    def missing_prefix_code(self, field, input_map, cmv):
        """Part of the condition that checks for missings when missing_splits
        has been used

        """
        return missing_prefix_code(self, field, input_map, cmv)

    def split_condition_code(self, field, depth, input_map,
                             pre_condition, term_analysis_fields,
                             item_analysis_fields):
        """Condition code for the split

        """

        return split_condition_code(self, field, depth, input_map,
                                    pre_condition, term_analysis_fields,
                                    item_analysis_fields)

    def plug_in_body(self, depth=1, cmv=None, input_map=False,
                     ids_path=None, subtree=True):
        """Translate the model into a set of "if" python statements.

        `depth` controls the size of indentation. As soon as a value is missing
        that node is returned without further evaluation.

        """
        # label for the confidence measure and initialization
        metric = "error" if self.regression else "confidence"
        if cmv is None:
            cmv = []
        body = u""
        term_analysis_fields = []
        item_analysis_fields = []

        children = filter_nodes(self.children, ids=ids_path,
                                subtree=subtree)
        if children:

            # field used in the split
            field = split(children)

            has_missing_branch = (missing_branch(children) or
                                  none_value(children))
            # the missing is singled out as a special case only when there's
            # no missing branch in the children list
            one_branch = not has_missing_branch or \
                self.fields[field]['optype'] in COMPOSED_FIELDS
            if (one_branch and
                not self.fields[field]['slug'] in cmv):
                body += self.missing_check_code(field, depth, input_map, cmv,
                                                metric)

            for child in children:
                field = child.predicate.field
                pre_condition = u""
                # code when missing_splits has been used
                if has_missing_branch and child.predicate.value is not None:
                    pre_condition = self.missing_prefix_code(child, field,
                                                             input_map, cmv)

                # complete split condition code
                body += child.split_condition_code( \
                    field, depth, input_map, pre_condition,
                    term_analysis_fields, item_analysis_fields)

                # value to be determined in next node
                next_level = child.plug_in_body(depth + 1,
                                                cmv=cmv[:],
                                                input_map=input_map,
                                                ids_path=ids_path,
                                                subtree=subtree)

                body += next_level[0]
                term_analysis_fields.extend(next_level[1])
                item_analysis_fields.extend(next_level[2])
        else:
            value = value_to_print(self.output,
                                   self.fields[self.objective_id]['optype'])
            body = u"%sreturn {\"prediction\":%s, \"%s\":%s}\n" % ( \
                INDENT * depth, value, metric, self.confidence)

        return body, term_analysis_fields, item_analysis_fields


class PythonBoostedTree(BoostedTree):

    def missing_check_code(self, field, depth, input_map, cmv):
        """Builds the code to predict when the field is missing

        """
        code = u"%sif (%s is None):\n" % \
               (INDENT * depth,
                map_data(self.fields[field]['slug'], input_map, True))
        value = value_to_print(self.output, "numeric")
        code += u"%sreturn {\"prediction\":%s" % (INDENT * (depth + 1),
                                                  value)
        if hasattr(self, "probability"):
            code += u", \"probability\": %s" % self.probability
        code += u"}\n"
        cmv.append(self.fields[field]['slug'])
        return code

    def missing_prefix_code(self, field, input_map, cmv):
        """Part of the condition that checks for missings when missing_splits
        has been used

        """
        return missing_prefix_code(self, field, input_map, cmv)

    def split_condition_code(self, field, depth, input_map,
                             pre_condition, term_analysis_fields,
                             item_analysis_fields):
        """Condition code for the split

        """
        return split_condition_code(self, field, depth, input_map,
                                    pre_condition, term_analysis_fields,
                                    item_analysis_fields)

    def plug_in_body(self, depth=1, cmv=None, input_map=False,
                     ids_path=None, subtree=True):
        """Translate the model into a set of "if" python statements.

        `depth` controls the size of indentation. As soon as a value is missing
        that node is returned without further evaluation.

        """
        if cmv is None:
            cmv = []
        body = u""
        term_analysis_fields = []
        item_analysis_fields = []

        children = filter_nodes(self.children, ids=ids_path,
                                subtree=subtree)
        if children:

            # field used in the split
            field = split(children)

            has_missing_branch = (missing_branch(children) or
                                  none_value(children))
            # the missing is singled out as a special case only when there's
            # no missing branch in the children list
            one_branch = not has_missing_branch or \
                self.fields[field]['optype'] in COMPOSED_FIELDS
            if (one_branch and
                not self.fields[field]['slug'] in cmv):
                body += self.missing_check_code(field, depth, input_map, cmv)

            for child in children:
                field = child.predicate.field
                pre_condition = u""
                # code when missing_splits has been used
                if has_missing_branch and child.predicate.value is not None:
                    pre_condition = self.missing_prefix_code(child, field,
                                                             input_map, cmv)

                # complete split condition code
                body += child.split_condition_code( \
                    field, depth, input_map, pre_condition,
                    term_analysis_fields, item_analysis_fields)

                # value to be determined in next node
                next_level = child.plug_in_body(depth + 1,
                                                cmv=cmv[:],
                                                input_map=input_map,
                                                ids_path=ids_path,
                                                subtree=subtree)

                body += next_level[0]
                term_analysis_fields.extend(next_level[1])
                item_analysis_fields.extend(next_level[2])
        else:
            value = value_to_print(self.output, "numeric")
            body = u"%sreturn {\"prediction\":%s" % (INDENT * depth, value)
            if hasattr(self, "probability"):
                body += u", \"probability\": %s" % self.probability
            body += u"}\n"

        return body, term_analysis_fields, item_analysis_fields
