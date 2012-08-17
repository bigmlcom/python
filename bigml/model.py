# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2012 BigML
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

"""A local Predictive Model.

This module defines a Model to make predictions locally or
embedded into your application without needing to send requests to
BigML.io.

This module cannot only save you a few credits but also enormously
reduce the latency for each prediction.

You can also visualize your predictive model in IF-THEN rule format
and even generate a python function that implements the model.

Example usage (assuming that you have previously set up the BIGML_USERNAME and
BIGML_API_KEY environment variables and that you own the model/id below):

from bigml.api import BigML
from bigml.model import Model

api = BigML()

model = Model(api.get_model('model/5026965515526876630001b2'))
model.predict({"petal length": 3, "petal width": 1})


You can also see model in a IF-THEN rule format with:

model.rules()

Or auto-generate a python function code for the model with:

model.python()

"""
import logging
LOGGER = logging.getLogger('BigML')

import sys
import operator
import re

from api import invert_dictionary, slugify

# Map operator str to its corresponding function
OPERATOR = {
    "<": operator.lt,
    "<=": operator.le,
    "=": operator.eq,
    "!=": operator.ne,
    ">=": operator.ge,
    ">": operator.gt
}

class Predicate(object):
    """A predicate to be evaluated in a tree node"""

    def __init__(self, operator, field, value):
        self.operator = operator
        self.field = field
        self.value = value

class Tree(object):
    """A tree-like predictive model"""
    def __init__(self, tree, fields, objective_field=None):

        self.fields = fields
        if objective_field and isinstance(objective_field, list):
            self.objective_field = objective_field[0]
        else:
            self.objective_field = objective_field

        self.output = tree['output']
        if tree['predicate'] == True:
            self.predicate = True
        else:
            self.predicate = Predicate(
                tree['predicate']['operator'],
                tree['predicate']['field'],
                tree['predicate']['value'])
        children = []
        if 'children' in tree:
            for child in tree['children']:
                children.append(Tree(child, self.fields, objective_field))
        self.children = children
        self.count = tree['count']
        self.distribution = tree['distribution']

    def split(self, children):
        """Return the field that is used by the node to make a decision.

        """
        field = set([child.predicate.field for child in children])
        if len(field) == 1:
            return field.pop()

    def predict(self, input, path=[]):
        """Make a prediction based on a number of field values.

        The input fields must be keyed by Id.

        """
        if self.children and self.split(self.children) in input:
            for child in self.children:
                if apply(OPERATOR[child.predicate.operator],
                        [input[child.predicate.field],
                        child.predicate.value]):
                    path.append("%s %s %s" % (
                        self.fields[child.predicate.field]['name'],
                        child.predicate.operator,
                        child.predicate.value))
                    return child.predict(input, path)
                    break;
        else:
            return self.output, path

    def generate_rules(self, depth=0):
        """Translate a tree model into a set of IF-THEN rules.

        """
        rules = ""
        if self.children:
            for child in self.children:
                rules += "%s IF %s %s %s %s\n" % ('   ' * depth,
                    self.fields[child.predicate.field]['name'],
                    child.predicate.operator,
                    child.predicate.value,
                    "AND" if child.children else "THEN")
                rules += child.generate_rules(depth+1)
        else:
            rules += "%s %s = %s\n" % ('   ' * depth,
                self.fields[self.objective_field]['name'] if self.objective_field else "Prediction",
                self.output)
        return rules

    def rules(self, out):
        """Print out an IF-THEN rule version of the tree.

        """
        out.write(self.generate_rules())
        out.flush()

    def python_body(self, depth=1):
        """Translate the model into a set of "if" python statements.

        """
        body = ""
        if self.children:
            for child in self.children:
                body += "%sif (%s %s %s)%s\n" % ('    ' * depth,
                    self.fields[child.predicate.field]['slug'],
                    child.predicate.operator,
                    child.predicate.value,
                    ":" if child.children else ":")
                body += child.python_body(depth+1)
        else:
            if self.fields[self.

            objective_field]['optype'] == 'numeric':
                body = "%s return %s\n" % ('    ' * depth, self.output)
            else:
                body = "%s return '%s'\n" % ('    ' * depth, self.output)
        return body

    def python(self, out):
        """Writes a python function that implements the model.
        """
        args = []
        for key in self.fields.iterkeys():
            slug = slugify(self.fields[key]['name'])
            self.fields[key].update(slug=slug)
            if key != self.objective_field:
                args.append("%s=None" % slug)
        predictor = "def predict_%s(%s):\n" % (self.fields[self.objective_field]['slug'], ", ".join(args))
        predictor += self.python_body()
        out.write(predictor)
        out.flush()


class Model(object):
    """ A lightwheight wrapper around a Tree model.

    Uses a BigML remote model to build a local version that can be used
    to generate prediction locally.

    """

    def __init__(self, model):
        fields = model['object']['model']['fields']
        self.inverted_fields = invert_dictionary(fields)
        self.tree = Tree(
            model['object']['model']['root'],
            fields,
            model['object']['objective_fields'])

    def predict(self, input, out=sys.stdout):
        """Makes a prediction based on a number of field values.

        The input fields must be keyed by field name.

        """
        try:
            input_data = dict(
                [[self.inverted_fields[key], value]
                    for key, value in input.items()])
        except KeyError, field:
            LOGGER.error("Wrong field name %s" % field)
            return
        prediction, path = self.tree.predict(input_data)
        out.write(' AND '.join(path) + ' => %s \n' % prediction)
        out.flush()
        return prediction

    def rules(self, out=sys.stdout):
        return self.tree.rules(out)

    def python(self, out=sys.stdout):
        return self.tree.python(out)
