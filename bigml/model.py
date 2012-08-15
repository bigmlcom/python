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

"""BigML.io Local Predictive Model.

This is a simple implementation of a local Predictive Model

from bigml.api import BigML
from bigml.model import Model

api = BigML()

model = Model(api.get_model('model/5026965515526876630001b2'))
model.predict({"sepal length": 2.46, "sepal width": 1})
model.rules()
model.python()

"""
import logging
LOGGER = logging.getLogger('BigML')

import operator
import unidecode
import re

from api import invert_dictionary

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

def slugify(str):
    str = unidecode.unidecode(str).lower()
    return re.sub(r'\W+', '_', str)

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
                children.append(Tree(child, self.fields, objective_field))
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
                if apply(OPERATOR[child.predicate.operator],
                        [input[child.predicate.field],
                        child.predicate.value]):
                    print("%s %s %s\n" % (
                        self.fields[child.predicate.field]['name'],
                        child.predicate.operator,
                        child.predicate.value))
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
            print("%s %s = %s" % (
                '   ' * depth,
                self.fields[self.objective_field]['name'] if self.objective_field else "Prediction",
                self.output))

    def python_body(self, depth=1):
        if self.children:
            for child in self.children:
                print("%sif (%s %s %s)%s" %
                    ('    ' * depth,
                    self.fields[child.predicate.field]['slug'],
                    child.predicate.operator,
                    child.predicate.value,
                    ":" if child.children else ":"))
                child.python_body(depth+1)
        else:
            if self.fields[self.

            objective_field]['optype'] == 'numeric':
                print("%s return %s" % ('    ' * depth, self.output))
            else:
                print("%s return '%s'" % ('    ' * depth, self.output))

    def python(self):
        args = []
        for key in self.fields.iterkeys():
            slug = slugify(self.fields[key]['name'])
            self.fields[key].update(slug=slug)
            if key != self.objective_field:
                args.append(slug)
        print("def predict_%s(%s):" % (self.fields[self.objective_field]['slug'], ", ".join(args)))
        self.python_body()


class Model(object):

    def __init__(self, model):
        fields = model['object']['model']['fields']
        self.inverted_fields = invert_dictionary(fields)
        self.tree = Tree(
            model['object']['model']['root'],
            fields,
            model['object']['objective_fields'])

    def predict(self, input):
        try:
            input_data = dict(
                [[self.inverted_fields[key], value]
                    for key, value in input.items()])
        except KeyError, field:
            LOGGER.error("Wrong field name %s" % field)
            return
        return self.tree.predict(input_data)

    def rules(self):
        return self.tree.rules()

    def python(self):
        return self.tree.python()

