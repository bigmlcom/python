# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2017 BigML
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

"""Tree structure for the BigML local boosted Model

This module defines an auxiliary Tree structure that is used in the local
boosted Ensemble to predict locally or embedded into your application
without needing to send requests to BigML.io.

"""
from bigml.predicate import Predicate
from bigml.prediction import Prediction
from bigml.util import sort_fields, utf8, split
from bigml.tree import LAST_PREDICTION, PROPORTIONAL
from bigml.tree import one_branch


class BoostedTree(object):
    """A boosted tree-like predictive model.

    """
    def __init__(self, tree, fields, objective_field=None):

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

        self.id = tree.get('id')
        children = []
        if 'children' in tree:
            for child in tree['children']:
                children.append(BoostedTree(child,
                                            self.fields,
                                            objective_field=objective_field))
        self.children = children
        self.count = tree['count']
        self.g_sum = tree.get('g_sum')
        self.h_sum = tree.get('h_sum')

    def list_fields(self, out):
        """Lists a description of the model's fields.

        """

        for field in [(val['name'], val['optype']) for _, val in
                      sort_fields(self.fields)]:
            out.write(utf8(u'[%-32s : %s]\n' % (field[0], field[1])))
            out.flush()
        return self.fields

    def predict(self, input_data, path=None, missing_strategy=LAST_PREDICTION):
        """Makes a prediction based on a number of field values.

        The input fields must be keyed by Id. There are two possible
        strategies to predict when the value for the splitting field
        is missing:
            0 - LAST_PREDICTION: the last issued prediction is returned.
            1 - PROPORTIONAL: we consider all possible outcomes and create
                              an average prediction.
        """

        if path is None:
            path = []
        if missing_strategy == PROPORTIONAL:
            return self.predict_proportional(input_data, path=path)
        else:
            if self.children:
                for child in self.children:
                    if child.predicate.apply(input_data, self.fields):
                        path.append(child.predicate.to_rule(self.fields))
                        return child.predict(input_data, path=path)

            return Prediction(
                self.output,
                path,
                None,
                distribution=None,
                count=self.count,
                median=None,
                distribution_unit=None,
                children=self.children,
                d_min=None,
                d_max=None)

    def predict_proportional(self, input_data, path=None,
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

        if not self.children:
            return (self.g_sum, self.h_sum, self.count, path)
        if one_branch(self.children, input_data) or \
                self.fields[split(self.children)]["optype"] in \
                ["text", "items"]:
            for child in self.children:
                if child.predicate.apply(input_data, self.fields):
                    new_rule = child.predicate.to_rule(self.fields)
                    if new_rule not in path and not missing_found:
                        path.append(new_rule)
                    return child.predict_proportional(input_data, path,
                                                      missing_found)
        else:
            # missing value found, the unique path stops
            missing_found = True
            g_sums = 0.0
            h_sums = 0.0
            population = 0
            for child in self.children:
                g_sum, h_sum, count, _ = \
                    child.predict_proportional(input_data, path,
                                               missing_found)
                g_sums += g_sum
                h_sums += h_sum
                population += count
            return (g_sums, h_sums, population, path)


    def get_leaves(self, path=None, filter_function=None):
        """Returns a list that includes all the leaves of the tree.

        """
        leaves = []
        if path is None:
            path = []
        if not isinstance(self.predicate, bool):
            path.append(self.predicate.to_lisp_rule(self.fields))

        if self.children:
            for child in self.children:
                leaves += child.get_leaves(path=path[:],
                                           filter_function=filter_function)
        else:
            leaf = {
                'id': self.id,
                'count': self.count,
                'g_sum': self.g_sum,
                'h_sum': self.h_sum,
                'output': self.output,
                'path': path}
            if (not hasattr(filter_function, '__call__')
                    or filter_function(leaf)):
                leaves += [leaf]
        return leaves
