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

"""

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

class Node(object):

    def __init__(self, node):
        self.output = node['output']
        if node['predicate'] == True:
            self.predicate = True
        else:
            self.predicate = Predicate(
                node['predicate']['operator'],
                node['predicate']['field'],
                node['predicate']['value'])
        children = []
        if 'children' in node:
            for child in node['children']:
                children.append(Node(child))
        self.children = children
        self.count = node['count']
        self.distribution = node['distribution']


class Prediction(object):
    def split(self, node):
        field = set([child.predicate.field for child in node.children])
        if len(field) == 1:
            return field.pop()

    def __init__(self, node, input):
        self.node = node
        self.input = input

    def predict(self):
        if self.node.children and self.split(self.node) in self.input:
            for child in self.node.children:
                if apply(OPERATOR[child.predicate.operator], [self.input[child.predicate.field], child.predicate.value]):
                    return Prediction(child, self.input).predict()
                    break;
        else:
            return self.node.output


class Rule(object):

    def __init__(self, _if, _then):
        self._if = _if
        self._then = _then

    def pprint(self):
        print "IF %s THEN %s" % (self._if, self._then)


# from bigml.api import BigML
# api = BigML()
# from bigml.tree import Node
# from bigml.tree import Prediction

# model = api.get_model('model/5026965515526876630001b2')

# t = Node(model['object']['model']['root'])
