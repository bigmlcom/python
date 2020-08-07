# -*- coding: utf-8 -*-
#
# Copyright 2017-2020 BigML
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

"""Model level output for python

This module defines functions that generate python code to make local
predictions
"""
import sys
import os

from bigml.tree_utils import slugify, INDENT, sort_fields, docstring_comment, \
    TERM_OPTIONS, TM_TOKENS, TM_FULL_TERM, TM_ALL, \
    ITEM_OPTIONS
from bigml.model import Model

from bigml.out_tree.pythontree import PythonTree, PythonBoostedTree


# templates for static Python
BIGML_SCRIPT = os.path.dirname(__file__)
TERM_TEMPLATE = "%s/static/term_analysis.txt" % BIGML_SCRIPT
ITEMS_TEMPLATE = "%s/static/items_analysis.txt" % BIGML_SCRIPT
HADOOP_CSV_TEMPLATE = "%s/static/python_hadoop_csv.txt" % \
    BIGML_SCRIPT
HADOOP_NEXT_TEMPLATE = "%s/static/python_hadoop_next.txt" % \
    BIGML_SCRIPT
HADOOP_REDUCER_TEMPLATE = "%s/static/python_hadoop_reducer.txt" % \
    BIGML_SCRIPT
MAX_ARGS_LENGTH = -1 # in this version, the argument will be the input array

PYTHON_CONV = {
    "double": "locale.atof",
    "float": "locale.atof",
    "integer": "lambda x: int(locale.atof(x))",
    "int8": "lambda x: int(locale.atof(x))",
    "int16": "lambda x: int(locale.atof(x))",
    "int32": "lambda x: int(locale.atof(x))",
    "int64": "lambda x: long(locale.atof(x))",
    "day": "lambda x: int(locale.atof(x))",
    "month": "lambda x: int(locale.atof(x))",
    "year": "lambda x: int(locale.atof(x))",
    "hour": "lambda x: int(locale.atof(x))",
    "minute": "lambda x: int(locale.atof(x))",
    "second": "lambda x: int(locale.atof(x))",
    "millisecond": "lambda x: int(locale.atof(x))",
    "day-of-week": "lambda x: int(locale.atof(x))",
    "day-of-month": "lambda x: int(locale.atof(x))"
}

PYTHON_TYPE = {
    "double": "float",
    "float": "float",
    "integer": "int",
    "int8": "int",
    "int16": "int",
    "int32": "int",
    "int64": "long",
    "day": "int",
    "month": "int",
    "year": "int",
    "hour": "int",
    "minute": "int",
    "second": "int",
    "millisecond": "int",
    "day-of-week": "int",
    "day-of-month": "int"
}


PYTHON_KEYWORDS = [
    "and",
    "assert",
    "break",
    "class",
    "continue",
    "def",
    "del",
    "elif",
    "else",
    "except",
    "exec",
    "finally",
    "for",
    "from",
    "global",
    "if",
    "import",
    "in",
    "is",
    "lambda",
    "not",
    "or",
    "pass",
    "print",
    "raise",
    "return",
    "try",
    "while ",
    "Data",
    "Float",
    "Int",
    "Numeric",
    "Oxphys",
    "array",
    "close",
    "float",
    "int",
    "input",
    "open",
    "range",
    "type",
    "write",
    "zeros",
    "acos",
    "asin",
    "atan",
    "cos",
    "e",
    "exp",
    "fabs",
    "floor",
    "log",
    "log10",
    "pi",
    "sin",
    "sqrt",
    "tan"
]


class PythonModel(Model):


    def __init__(self, model, api=None, fields=None, boosting=None):
        """Empty attributes to be overriden

        """
        self.tree_class = PythonTree if not boosting else PythonBoostedTree
        Model.__init__(self, model, api, fields)

    def plug_in(self, out=sys.stdout,
                filter_id=None, subtree=True, hadoop=False):
        """Generates a basic python function that implements the model.

        `out` is file descriptor to write the python code.

        """
        ids_path = self.get_ids_path(filter_id)
        if hadoop:
            return (self.hadoop_python_mapper(out=out,
                                              ids_path=ids_path,
                                              subtree=subtree) or
                     self.hadoop_python_reducer(out=out))
        else:
            return self.python(out, self.docstring(), ids_path=ids_path,
                               subtree=subtree)

    def hadoop_python_mapper(self, out=sys.stdout, ids_path=None,
                             subtree=True):
        """Generates a hadoop mapper header to make predictions in python

        """
        input_fields = [(value, key) for (key, value) in
                        sorted(list(self.inverted_fields.items()),
                               key=lambda x: x[1])]
        parameters = [value for (key, value) in
                      input_fields if key != self.tree.objective_id]
        args = []
        for field in input_fields:
            slug = slugify(self.tree.fields[field[0]]['name'])
            self.tree.fields[field[0]].update(slug=slug)
            if field[0] != self.tree.objective_id:
                args.append("\"" + self.tree.fields[field[0]]['slug'] + "\"")

        with open(HADOOP_CSV_TEMPLATE) as template_hander:
            output = template_handler.read() % ",".join(parameters)

        output += "\n%sself.INPUT_FIELDS = [%s]\n" % \
            ((INDENT * 3), (",\n " + INDENT * 8).join(args))

        input_types = []
        prefixes = []
        suffixes = []
        count = 0
        fields = self.tree.fields
        for key in [field[0] for field in input_fields
                    if field[0] != self.tree.objective_id]:
            input_type = ('None' if not fields[key]['datatype'] in
                          PYTHON_CONV
                          else PYTHON_CONV[fields[key]['datatype']])
            input_types.append(input_type)
            if 'prefix' in fields[key]:
                prefixes.append("%s: %s" % (count,
                                            repr(fields[key]['prefix'])))
            if 'suffix' in fields[key]:
                suffixes.append("%s: %s" % (count,
                                            repr(fields[key]['suffix'])))
            count += 1
        static_content = "%sself.INPUT_TYPES = [" % (INDENT * 3)
        formatter = ",\n%s" % (" " * len(static_content))
        output += "\n%s%s%s" % (static_content,
                                 formatter.join(input_types),
                                 "]\n")
        static_content = "%sself.PREFIXES = {" % (INDENT * 3)
        formatter = ",\n%s" % (" " * len(static_content))
        output += "\n%s%s%s" % (static_content,
                                 formatter.join(prefixes),
                                 "}\n")
        static_content = "%sself.SUFFIXES = {" % (INDENT * 3)
        formatter = ",\n%s" % (" " * len(static_content))
        output += "\n%s%s%s" % (static_content,
                                 formatter.join(suffixes),
                                 "}\n")

        with open(HADOOP_NEXT_TEMPLATE) as template_hander:
            output += template_handler.read()

        out.write(output)
        out.flush()

        self.tree.python(out, self.docstring(),
                         input_map=True,
                         ids_path=ids_path,
                         subtree=subtree)

        output = \
"""
csv = CSVInput()
for values in csv:
    if not isinstance(values, bool):
        print u'%%s\\t%%s' %% (repr(values), repr(predict_%s(values)))
\n\n
""" % fields[self.tree.objective_id]['slug']
        out.write(output)
        out.flush()

    def hadoop_python_reducer(self, out=sys.stdout):
        """Generates a hadoop reducer to make predictions in python

        """

        with open(HADOOP_REDUCER_TEMPLATE) as template_hander:
            output = template_handler.read()
        out.write(output)
        out.flush()

    def term_analysis_body(self, term_analysis_predicates,
                           item_analysis_predicates):
        """ Writes auxiliary functions to handle the term and item
        analysis fields

        """
        body = ""
        # static content
        body += """
    import re
"""
        if term_analysis_predicates:
            body += """
    tm_tokens = '%s'
    tm_full_term = '%s'
    tm_all = '%s'

""" % (TM_TOKENS, TM_FULL_TERM, TM_ALL)

            with open(TERM_TEMPLATE) as template_handler:
                body += template_handler.read()

            term_analysis_options = set([x[0] for x in term_analysis_predicates])
            term_analysis_predicates = set(term_analysis_predicates)
            body += """
    term_analysis = {"""
            for field_id in term_analysis_options:
                field = self.fields[field_id]
                body += """
        \"%s\": {""" % field['slug']
                options = sorted(field['term_analysis'].keys())
                for option in options:
                    if option in TERM_OPTIONS:
                        body += """
            \"%s\": %s,""" % (option, repr(field['term_analysis'][option]))
                body += """
        },"""
            body += """
    }"""
            body += """
    term_forms = {"""
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
            for field in term_forms:
                body += """
        \"%s\": {""" % field
                terms = sorted(term_forms[field].keys())
                for term in terms:
                    body += """
            u\"%s\": %s,""" % (term, term_forms[field][term])
                body += """
        },"""
            body += """
    }

"""
        if item_analysis_predicates:
            with open(ITEMS_TEMPLATE) as template_handler:
                body += template_handler.read()

            item_analysis_options = set([x[0] for x in item_analysis_predicates])
            item_analysis_predicates = set(item_analysis_predicates)
            body += """
    item_analysis = {"""
            for field_id in item_analysis_options:
                field = self.fields[field_id]
                body += """
        \"%s\": {""" % field['slug']
                for option in field['item_analysis']:
                    if option in ITEM_OPTIONS:
                        body += """
            \"%s\": %s,""" % (option, repr(field['item_analysis'][option]))
                body += """
        },"""
            body += """
    }

"""
        return body

    def python(self, out, docstring, ids_path=None, subtree=True):
        """Generates a python function that implements the model.

        """

        args = []
        args_tree = []
        parameters = sort_fields(self.fields)
        input_map = len(parameters) > MAX_ARGS_LENGTH and MAX_ARGS_LENGTH > 0
        reserved_keywords = PYTHON_KEYWORDS if not input_map else None
        prefix = "_" if not input_map else ""
        for field in [(key, val) for key, val in parameters]:
            field_name_to_show = self.fields[field[0]]['name'].strip()
            if field_name_to_show == "":
                field_name_to_show = field[0]
            slug = slugify(field_name_to_show,
                           reserved_keywords=reserved_keywords, prefix=prefix)
            self.fields[field[0]].update(slug=slug)
            if not input_map:
                if field[0] != self.objective_id:
                    args.append("%s=None" % (slug))
                    args_tree.append("%s=%s" % (slug, slug))
        if input_map:
            args.append("data={}")
            args_tree.append("data=data")

        function_name = self.fields[self.objective_id]['slug'] if \
            not self.boosting else \
            self.fields[self.boosting["objective_field"]]['slug']
        if prefix == "_" and function_name[0] == prefix:
            function_name = function_name[1:]
        if function_name == "":
            function_name = "field_" + self.objective_id
        python_header = "#!/usr/bin/env python\n# -*- coding: utf-8 -*-\n"
        predictor_definition = ("def predict_%s" %
                                function_name)
        depth = len(predictor_definition) + 1
        predictor = "%s(%s):\n" % (predictor_definition,
                                   (",\n" + " " * depth).join(args))
        predictor_doc = (INDENT + "\"\"\" " + docstring +
                         "\n" + INDENT + "\"\"\"\n")
        body, term_analysis_predicates, item_analysis_predicates = \
            self.tree.plug_in_body(input_map=input_map,
                                   ids_path=ids_path,
                                   subtree=subtree)
        terms_body = ""
        if term_analysis_predicates or item_analysis_predicates:
            terms_body = self.term_analysis_body(term_analysis_predicates,
                                                 item_analysis_predicates)
        predictor = python_header + predictor + \
            predictor_doc + terms_body + body

        predictor_model = "def predict"
        depth = len(predictor_model) + 1
        predictor += "\n\n%s(%s):\n" % (predictor_model,
                                         (",\n" + " " * depth).join(args))
        predictor += "%sprediction = predict_%s(%s)\n" % ( \
            INDENT, function_name, ", ".join(args_tree))

        if self.boosting is not None:
            predictor += "%sprediction.update({\"weight\": %s})\n" % \
                (INDENT, self.boosting.get("weight"))
            if self.boosting.get("objective_class") is not None:
                predictor += "%sprediction.update({\"class\": \"%s\"})\n" % \
                    (INDENT, self.boosting.get("objective_class"))
        predictor += "%sreturn prediction" % INDENT

        out.write(predictor)
        out.flush()
