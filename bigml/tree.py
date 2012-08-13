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

"""BigML.io Python bindings.

This is a simple implementation of a Tree-like Predictive Model

from bigml.api import BigML
from bigml.tree import Tree

api = BigML()

model = api.get_model('model/5026965515526876630001b2')

tree = Tree(model['object']['model']['root'], model['object']['model']['fields'], model['object']['objective_fields'])
tree.predict({"000002": 2.46, "000003": 1})
tree.rules()

"""
import logging
LOGGER = logging.getLogger('BigML')

import operator

OPERATOR = {
    "<": operator.lt,
    "<=": operator.le,
    "=": operator.eq,
    "!=": operator.ne,
    ">=": operator.ge,
    ">": operator.gt
}

class Predicate(object):
    def __init__(self, operator, field, value):
        self.operator = operator
        self.field = field
        self.value = value

class Tree(object):

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
                children.append(Tree(child, fields, objective_field))
        self.children = children
        self.count = tree['count']
        self.distribution = tree['distribution']

    def split(self, children):
        field = set([child.predicate.field for child in children])
        if len(field) == 1:
            return field.pop()

    def predict(self, input):
        if self.children and self.split(self.children) in input:
            for child in self.children:
                if apply(OPERATOR[child.predicate.operator], [input[child.predicate.field], child.predicate.value]):
                    print("%s %s %s\n" % (self.fields[child.predicate.field]['name'], child.predicate.operator, child.predicate.value))
                    return child.predict(input)
                    break;
        else:
            return self.output

    def rules(self, depth=0):
        if self.children:
            for child in self.children:
                print("%s IF %s %s %s %s" %
                    ('   ' * depth,
                    self.fields[child.predicate.field]['name'],
                    child.predicate.operator,
                    child.predicate.value,
                    "AND" if child.children else "THEN"))
                child.rules(depth+1)
        else:
            if self.predicate == True:
                print("%s %s = %s" % (
                    '   ' * depth,
                    self.fields[self.objective_field]['name'] if self.objective_field else "Prediction",
                    self.output))
            else:
                print("%s %s = %s" % (
                    '   ' * depth,
                    self.fields[self.objective_field]['name'] if self.objective_field else "Prediction",
                    self.output))



