# -*- coding: utf-8 -*-
#
# Copyright 2012-2022 BigML
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
Pre-modeling steps: Flatline data transformations

"""

import copy

from javascript import require, globalThis
from bigml.fields import Fields
from bigml.api import get_api_connection


def header_names(fields):
    """Listing the names of the fields as ordered in the original dataset.
    The `fields` parameter is a Fields object
    """
    headers = []
    for column in fields.fields_columns:
        headers.append(fields.fields[
            fields.fields_by_column_number[column]]["name"])
    return headers


class PreModeling:
    """Transformations that were applied in a workflow

    This class uses JSPyBridge to access and execute
    Flatline's javascript implementation and allows interaction via
    Python constructs.

    """
    def __init__(self, transformations, api=None):
        self.steps = []
        self.headers = []
        self.fields = []
        self.count = 0
        self.api = get_api_connection(api)

        for step in transformations:
            new_fields = step.get("args", {}).get("new_fields")
            if new_fields:
                self.add_step(new_fields,
                              self.api.get_dataset(step.get("origin_id")))

    def add_step(self, new_fields, origin_dataset):
        """Adds a new step where the new fields provided are defined """
        self.steps.append({"id": self.count,
                           "new_fields": new_fields})
        fields = Fields(origin_dataset)
        self.fields.append(fields.fields)
        try:
            self.headers[self.count] = header_names(fields)
        except IndexError:
            self.headers.append(header_names(fields))
        self.count += 1

    def input_array(self, input_data):
        """Transform the dict-like input data into a row """
        input_names = input_data.keys()
        row = []
        for name in self.headers[0]:
            row.append(None if not name in input_names else input_data[name])
        return row

    def run_step(self, step, input_arrays):
        """Applies the transformations of a particular step to the input data
        as a list of arrays. Usually, the list will have a sigle element, but
        can have more if windows are used.

        """
        new_input_arrays = []
        new_field_names = []
        new_fields = step.get("new_fields")
        step_id = step.get("id")
        try:
            fields = {"fields": self.fields[step_id]}
        except:
            fields = None
        for new_field in new_fields:
            expr = new_field.get("field")
            new_names = new_field.get("names")
            new_field_names.extend(new_names)
            # evaluating first to raise an alert if the expression is failing
            check = Interpreter.flatline.evaluate_sexp(
                expr, fields, True).valueOf()
            if "error" in check:
                raise ValueError(check["error"])
            new_input = Interpreter.flatline.eval_and_apply_sexp(
                expr, fields, input_arrays)
            for index, _ in enumerate(new_input):
                try:
                    new_input_arrays[index]
                except IndexError:
                    new_input_arrays.append([])
                new_input_arrays[index].extend(new_input[index])
        try:
            self.headers[step_id + 1]
            new_headers = False
        except IndexError:
            new_headers = True

        if new_headers:
            self.headers.append(new_field_names)
        return new_input_arrays

    def run(self, input_data_list):
        """Applies the transformations to the given input data and returns
        the result. Usually, the input_data_list will contain a single
        dictionary, but it can contain a list of them if needed for window
        functions.
        """
        rows = [self.input_array(input_data) for input_data in input_data_list]
        for step in self.steps:
            rows = self.run_step(step, rows)
        return [dict(zip(self.headers[-1], row)) for row in rows]


class Interpreter:
    """A bridge to an underlying nodejs Flatline interpreter.

    This class uses execjs to launch a Nodejs interpreter that loads
    Flatline's javascript implementation and allows interaction via
    Python constructs.

    Example:

      Interpreter.check_lisp('(+ 1 2)')
      Interpreter.check_json(["f", 0], dataset=dataset)

    """

    __FLATLINEJS = require('../flatline/flatline-node.js')
    flatline = __FLATLINEJS.bigml.dixie.flatline

    @staticmethod
    def infer_fields(row, prefix=None, offset=None):
        """Utility function generating a mock list of fields.

        Usually, checks and applications of Flatline expressions run
        in the context of a given dataset's field descriptors, but
        during testing it's useful sometimes to provide a mock set of
        them, based on the types of the values of the test input rows.

        Example:

           In[1]: Interpreter.infer_fields([0, 'a label'])
           Out[2]: [{'column_number': 0,
                      'datatype': 'int64',
                      'id': '000000',
                      'optype': 'numeric'},
                     {'column_number': 1,
                      'datatype': 'string',
                      'id': '000001',
                      'optype': 'categorical'}]

        """
        result = []
        id = 0
        for v in row:
            t = type(v)
            optype = 'categorical'
            datatype = 'string'
            if (t is int or t is float):
                optype = 'numeric'
                if t is float:
                    datatype = 'float64'
                else:
                    datatype = 'int64'
            id_str = '%06x' % id
            if prefix:
                length = len(prefix)
                id_str = prefix + id_str[length:]
            column = id
            if offset:
                column = offset + id
            result.append({'id': id_str,
                           'optype':optype,
                           'datatype': datatype,
                           'column_number': column})
            id = id + 1
        return result

    @staticmethod
    def __dataset(dataset, rows):
        if dataset is None and len(rows) > 0:
            return {'fields': Interpreter.infer_fields(rows[0])}
        return dataset

    @staticmethod
    def defined_functions(self):
        """A list of the names of all defined Flaline functions"""
        return Interpreter.flatline.defined_primitives

    @staticmethod
    def check_lisp(self, sexp, dataset=None):
        """Checks whether the given lisp s-expression is valid.

        Any operations referring to a dataset's fields will use the
        information found in the provided dataset, which should have
        the structure of the 'object' component of a BigML dataset
        resource.

        """
        r = Interpreter.flatline.evaluate_sexp(sexp, dataset)
        r.pop(u'mapper', None)
        return r

    @staticmethod
    def check_json(self, json_sexp, dataset=None):
        """Checks whether the given JSON s-expression is valid.

        Works like `check_lisp` (which see), but taking a JSON
        expression represented as a native Python list instead of a
        Lisp sexp string.

        """
        r = Interpreter.flatline.evaluate_js(json_sexp, dataset)
        r.pop(u'mapper', None)
        return r

    @staticmethod
    def lisp_to_json(self, sexp):
        """ Auxliary function transforming Lisp to Python representation."""
        return Interpreter.flatline.sexp_to_js(sexp)

    @staticmethod
    def json_to_lisp(self, json_sexp):
        """ Auxliary function transforming Python to lisp representation."""
        return Interpreter.flatline.js_to_sexp(json_sexp)

    @staticmethod
    def apply_lisp(self, sexp, rows, dataset=None):
        """Applies the given Lisp sexp to a set of input rows.

        Input rows are represented as a list of lists of native Python
        values. If no dataset is provided, the field characteristics
        of the input rows are guessed using `infer_fields`.

        """
        return Interpreter.flatline.eval_and_apply_sexp(
            sexp,
            Interpreter.__dataset(dataset, rows),
            rows)

    @staticmethod
    def apply_json(self, json_sexp, rows, dataset=None):
        """Applies the given JSON sexp to a set of input rows.

        As usual, JSON sexps are represented as Python lists,
        e.g. ["+", 1, 2].

        Input rows are represented as a list of lists of native Python
        values. If no dataset is provided, the field characteristics
        of the input rows are guessed using `infer_fields`.

        """
        return Interpreter.flatline.eval_and_apply_js(
            json_sexp,
            Interpreter.__dataset(dataset, rows),
            rows)
