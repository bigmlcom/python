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

    def __init__(self, output, predicate, children, count, distribution):

        self.output = output
        if predicate == True:
            self.predicate = True
        else:
            self.predicate = Predicate(predicate['operator'], predicate['field'], predicate['value'])
        self.children = children
        self.count = count
        self.distribution = distribution

class Tree(object):

    def __init__(self, node):
        children = []
        if 'children' in node:
            for child in node['children']:
                children.append(Tree(child))
        self.node =  Node(node['output'], node['predicate'], children, node['count'], node['distribution'])


