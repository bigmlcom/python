# -*- coding: utf-8 -*-
#
# Copyright 2022-2025 BigML
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
Flatline: Class that encapsulates the Flatline expressions interpreter
"""

from javascript import require


class Flatline:
    """A bridge to an underlying nodejs Flatline interpreter.

    This class uses JSPyBridge to launch a Nodejs interpreter that loads
    Flatline's javascript implementation and allows interaction via
    Python constructs.

    Example:

      Flatline.check_lisp('(+ 1 2)')
      Flatline.check_json(["f", 0], dataset=dataset)

    """

    __FLATLINEJS = require('./flatline/flatline-node.js')
    interpreter = __FLATLINEJS.bigml.dixie.flatline

    #pylint: disable=locally-disabled,invalid-name
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
        id_ = 0
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
            id_str = '%06x' % id_
            if prefix:
                length = len(prefix)
                id_str = prefix + id_str[length:]
            column = id_
            if offset:
                column = offset + id_
            result.append({'id': id_str,
                           'optype':optype,
                           'datatype': datatype,
                           'column_number': column})
            id_ = id_ + 1
        return result

    @staticmethod
    def _dataset(dataset, rows):
        """The dataset argument should be a Dataset that contains the
        in_fields information
        """
        try:
            return {"fields": dataset.in_fields}
        except AttributeError:
            if len(rows) > 0:
                return {'fields': Flatline.infer_fields(rows[0])}
            return None

    @staticmethod
    def defined_functions():
        """A list of the names of all defined Flaline functions"""
        return Flatline.interpreter.defined_primitives

    @staticmethod
    def check_lisp(sexp, fields=None):
        """Checks whether the given lisp s-expression is valid.

        Any operations referring to a dataset's fields will use the
        information found in fields structure.

        """
        r = Flatline.interpreter.evaluate_sexp(sexp, fields, True).valueOf()
        return r

    @staticmethod
    def check_json(json_sexp, fields=None):
        """Checks whether the given JSON s-expression is valid.

        Works like `check_lisp` (which see), but taking a JSON
        expression represented as a native Python list instead of a
        Lisp sexp string.

        """
        r = Flatline.interpreter.evaluate_js(json_sexp, fields).valueOf()
        return r

    @staticmethod
    def lisp_to_json(sexp):
        """ Auxliary function transforming Lisp to Python representation."""
        return Flatline.interpreter.sexp_to_js(sexp)

    @staticmethod
    def json_to_lisp(json_sexp):
        """ Auxliary function transforming Python to lisp representation."""
        return Flatline.interpreter.js_to_sexp(json_sexp)

    @staticmethod
    def apply_lisp(sexp, rows, dataset=None):
        """Applies the given Lisp sexp to a set of input rows.

        Input rows are represented as a list of lists of native Python
        values. The dataset info should be provided as a Dataset object.
        If no dataset is provided, the field characteristics
        of the input rows are guessed using `infer_fields`.

        """
        return Flatline.interpreter.eval_and_apply_sexp(
            sexp,
            Flatline._dataset(dataset, rows),
            rows)

    @staticmethod
    def apply_json(json_sexp, rows, dataset=None):
        """Applies the given JSON sexp to a set of input rows.

        As usual, JSON sexps are represented as Python lists,
        e.g. ["+", 1, 2].

        Input rows are represented as a list of lists of native Python
        values. The dataset info should be provided as a Dataset object.
        If no dataset is provided, the field characteristics
        of the input rows are guessed using `infer_fields`.

        """
        return Flatline.interpreter.eval_and_apply_js(
            json_sexp,
            Flatline._dataset(dataset, rows),
            rows)
