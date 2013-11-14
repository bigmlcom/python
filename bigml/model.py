# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2013 BigML
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

This module cannot only save you a few credits, but also enormously
reduce the latency for each prediction and let you use your models
offline.

You can also visualize your predictive model in IF-THEN rule format
and even generate a python function that implements the model.

Example usage (assuming that you have previously set up the BIGML_USERNAME
and BIGML_API_KEY environment variables and that you own the model/id below):

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
import locale
import os
import json

from bigml.api import FINISHED
from bigml.api import (get_status, error_message, BigML, get_model_id,
                       check_resource)
from bigml.util import (invert_dictionary, slugify, markdown_cleanup,
                        prefix_as_comment, utf8,
                        find_locale, cast)
from bigml.util import DEFAULT_LOCALE
from bigml.tree import Tree
from bigml.predicate import Predicate


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

PYTHON_FUNC = dict([(numtype, eval(function))
                    for numtype, function in PYTHON_CONV.iteritems()])

INDENT = u'    '

STORAGE = './storage'


def retrieve_model(api, model_id):
    """ Retrieves model info either from a local repo or from the remote server

    """
    if api.storage is not None:
        try:
            with open("%s%s%s" % (api.storage, os.sep,
                                  model_id.replace("/", "_"))) as model_file:
                model = json.loads(model_file.read())
            return model
        except ValueError:
            raise ValueError("The file %s contains no JSON")
        except IOError:
            pass
    model = check_resource(model_id, api.get_model, 'only_model=true')
    return model


def extract_objective(objective_field):
    """Extract the objective field id from the model structure

    """
    if isinstance(objective_field, list):
        return objective_field[0]
    return objective_field


def print_importance(field_importance, fields, out=sys.stdout):
    """Print a field importance structure

    """
    count = 1
    for [field, importance] in field_importance:
        out.write(utf8(u"    %s. %s: %.2f%%\n" % (count,
                       fields[field]['name'],
                       round(importance, 4) * 100)))
        count += 1


class Model(object):
    """ A lightweight wrapper around a Tree model.

    Uses a BigML remote model to build a local version that can be used
    to generate predictions locally.

    """

    def __init__(self, model, api=None):

        if (isinstance(model, dict) and 'resource' in model and
                model['resource'] is not None):
            self.resource_id = model['resource']
        else:
            if api is None:
                api = BigML(storage=STORAGE)
            self.resource_id = get_model_id(model)
            if self.resource_id is None:
                raise Exception(error_message(model,
                                              resource_type='model',
                                              method='get'))
            model = retrieve_model(api, self.resource_id)

        if ('object' in model and isinstance(model['object'], dict)):
            model = model['object']

        if ('model' in model and isinstance(model['model'], dict)):
            status = get_status(model)
            if ('code' in status and status['code'] == FINISHED):
                if 'model_fields' in model['model']:
                    fields = model['model']['model_fields']
                    # pagination or exclusion might cause a field not to
                    # be in available fields dict
                    if not all(key in model['model']['fields']
                               for key in fields.keys()):
                        raise Exception("Some fields are missing"
                                        " to generate a local model."
                                        " Please, provide a model with"
                                        " the complete list of fields.")
                    for field in fields:
                        field_info = model['model']['fields'][field]
                        fields[field]['summary'] = field_info['summary']
                        fields[field]['name'] = field_info['name']
                else:
                    fields = model['model']['fields']
                objective_field = model['objective_fields']
                self.objective_field = extract_objective(objective_field)
                self.uniquify_varnames(fields)
                self.inverted_fields = invert_dictionary(fields)
                self.all_inverted_fields = invert_dictionary(model['model']
                                                             ['fields'])
                self.tree = Tree(
                    model['model']['root'],
                    fields,
                    self.objective_field)
                self.description = model['description']
                self.field_importance = model['model'].get('importance',
                                                           None)
                if self.field_importance:
                    self.field_importance = [element for element
                                             in self.field_importance
                                             if element[0] in fields]
                self.locale = model.get('locale', DEFAULT_LOCALE)

            else:
                raise Exception("The model isn't finished yet")
        else:
            raise Exception("Cannot create the Model instance. Could not"
                            " find the 'model' key in the resource:\n\n%s" %
                            model)

    def uniquify_varnames(self, fields):
        """Tests if the fields names are unique. If they aren't, a
           transformation is applied to ensure unicity.

        """
        unique_names = set([fields[key]['name'] for key in fields])
        if len(unique_names) < len(fields):
            self.transform_repeated_names(fields)

    def transform_repeated_names(self, fields):
        """If a field name is repeated, it will be transformed adding its
           column number. If that combination is also a field name, the
           field id will be added.

        """
        # The objective field treated first to avoid changing it.
        unique_names = [fields[self.objective_field]['name']]

        field_ids = [field_id for field_id in fields
                     if field_id != self.objective_field]
        for field_id in field_ids:
            new_name = fields[field_id]['name']
            if new_name in unique_names:
                new_name = "{0}{1}".format(fields[field_id]['name'],
                                           fields[field_id]['column_number'])
                if new_name in unique_names:
                    new_name = "{0}_{1}".format(new_name, field_id)
                fields[field_id]['name'] = new_name
            unique_names.append(new_name)

            

    def resource(self):
        """Returns the model resource ID

        """
        return self.resource_id

    def fields(self, out=sys.stdout):
        """Describes and return the fields for this model.

        """
        self.tree.list_fields(out)

    def get_leaves(self):
        """Returns a list that includes all the leaves of the model.

        """
        return self.tree.get_leaves()

    def filter_input_data(self, input_data, by_name=True):
        """Filters the keys given in input_data checking against model fields

        """

        if isinstance(input_data, dict):
            empty_fields = [(key, value) for (key, value) in input_data.items()
                            if value is None]
            for (key, value) in empty_fields:
                del input_data[key]

            if by_name:
                # Checks input_data keys against field names and filters the
                # ones used in the model
                wrong_keys = [key for key in input_data.keys() if not key
                              in self.all_inverted_fields]

                if wrong_keys:
                    LOGGER.info("Wrong field names in input data: %s" %
                                 ", ".join(wrong_keys))
                input_data = dict(
                    [[self.inverted_fields[key], value]
                        for key, value in input_data.items()
                        if key in self.inverted_fields])
            else:
                input_data = dict(
                    [[key, value]
                        for key, value in input_data.items()
                        if key in self.tree.fields])
            return input_data
        else:
            LOGGER.error("Failed to read input data in the expected"
                         " {field:value} format.")
            return {}

    def predict(self, input_data, by_name=True,
                print_path=False, out=sys.stdout, with_confidence=False):
        """Makes a prediction based on a number of field values.

        By default the input fields must be keyed by field name but you can use
        `by_name` to input them directly keyed by id.

        """
        # Checks and cleans input_data leaving the fields used in the model
        input_data = self.filter_input_data(input_data, by_name=by_name)

        # Strips affixes for numeric values and casts to the final field type
        cast(input_data, self.tree.fields)

        prediction_info = self.tree.predict(input_data)
        prediction, path, confidence, distribution, instances = prediction_info

        # Prediction path
        if print_path:
            out.write(utf8(u' AND '.join(path) + u' => %s \n' % prediction))
            out.flush()
        if with_confidence:
            return [prediction, confidence, distribution, instances]
        return prediction

    def docstring(self):
        """Returns the docstring describing the model.

        """
        docstring = (u"Predictor for %s from %s\n" % (
            self.tree.fields[self.tree.objective_field]['name'],
            self.resource_id))
        self.description = (unicode(markdown_cleanup(
            self.description).strip())
            or u'Predictive model by BigML - Machine Learning Made Easy')
        docstring += u"\n" + INDENT * 2 + (u"%s" %
                     prefix_as_comment(INDENT * 2, self.description))
        return docstring

    def rules(self, out=sys.stdout):
        """Returns a IF-THEN rule set that implements the model.

        `out` is file descriptor to write the rules.

        """

        return self.tree.rules(out)

    def python(self, out=sys.stdout, hadoop=False):
        """Returns a basic python function that implements the model.

        `out` is file descriptor to write the python code.

        """
        if hadoop:
            return (self.hadoop_python_mapper(out=out) or
                    self.hadoop_python_reducer(out=out))
        else:
            return self.tree.python(out, self.docstring())

    def group_prediction(self):
        """Groups in categories or bins the predicted data

        dict - contains a dict grouping counts in 'total' and 'details' lists.
                'total' key contains a 3-element list.
                       - common segment of the tree for all instances
                       - data count
                       - predictions count
                'details' key contains a list of elements. Each element is a
                          3-element list:
                       - complete path of the tree from the root to the leaf
                       - leaf predictions count
                       - confidence
        """
        groups = {}
        tree = self.tree
        distribution = tree.distribution

        for group in distribution:
            groups[group[0]] = {'total': [[], group[1], 0],
                                'details': []}
        path = []

        def add_to_groups(groups, output, path, count, confidence):
            """Adds instances to groups array

            """
            group = output
            if not output in groups:
                groups[group] = {'total': [[], 0, 0],
                                 'details': []}
            groups[group]['details'].append([path, count, confidence])
            groups[group]['total'][2] += count

        def depth_first_search(tree, path):
            """Search for leafs' values and instances

            """
            if isinstance(tree.predicate, Predicate):
                path.append(tree.predicate)

            if len(tree.children) == 0:
                add_to_groups(groups, tree.output,
                              path, tree.count, tree.confidence)
                return tree.count
            else:
                children = tree.children[:]
                children.reverse()

                children_sum = 0
                for child in children:
                    children_sum += depth_first_search(child, path[:])
                if children_sum < tree.count:
                    add_to_groups(groups, tree.output, path,
                                  tree.count - children_sum, tree.confidence)
                return tree.count

        depth_first_search(tree, path)

        return groups

    def get_data_distribution(self):
        """Returns training data distribution

        """
        tree = self.tree
        distribution = tree.distribution

        return sorted(distribution,  key=lambda x: x[0])

    def get_prediction_distribution(self, groups=None):
        """Returns model predicted distribution

        """
        if groups is None:
            groups = self.group_prediction()

        predictions = [[group, groups[group]['total'][2]] for group in groups]
        # remove groups that are not predicted
        predictions = filter(lambda x: x[1] > 0, predictions)

        return sorted(predictions,  key=lambda x: x[0])

    def summarize(self, out=sys.stdout):
        """Prints summary grouping distribution as class header and details

        """
        tree = self.tree

        def print_distribution(distribution, out=sys.stdout):
            """Prints distribution data

            """
            total = reduce(lambda x, y: x + y,
                           [group[1] for group in distribution])
            for group in distribution:
                out.write(utf8(u"    %s: %.2f%% (%d instance%s)\n" % (group[0],
                               round(group[1] * 1.0 / total, 4) * 100,
                               group[1],
                               "" if group[1] == 1 else "s")))

        def print_field_importance(out=sys.stdout):
            """Prints field importance

            """
            print_importance(self.field_importance, self.tree.fields, out=out)

        def extract_common_path(groups):
            """Extracts the common segment of the prediction path for a group

            """
            for group in groups:
                details = groups[group]['details']
                common_path = []
                if len(details) > 0:
                    mcd_len = min([len(x[0]) for x in details])
                    for i in range(0, mcd_len):
                        test_common_path = details[0][0][i]
                        for subgroup in details:
                            if subgroup[0][i] != test_common_path:
                                i = mcd_len
                                break
                        if i < mcd_len:
                            common_path.append(test_common_path)
                groups[group]['total'][0] = common_path
                if len(details) > 0:
                    groups[group]['details'] = sorted(details,
                                                      key=lambda x: x[1],
                                                      reverse=True)

        def confidence_error(value):
            """Returns confidence for categoric objective fields
               and error for numeric objective fields
            """
            if value is None:
                return ""
            objective_type = tree.fields[tree.objective_field]['optype']
            if objective_type == 'numeric':
                return u" [Error: %s]" % value
            else:
                return u" [Confidence: %.2f%%]" % (round(value, 4) * 100)

        distribution = self.get_data_distribution()

        out.write(u"Data distribution:\n")
        print_distribution(distribution, out=out)
        out.write(u"\n\n")

        groups = self.group_prediction()
        predictions = self.get_prediction_distribution(groups)

        out.write(u"Predicted distribution:\n")
        print_distribution(predictions, out=out)
        out.write(u"\n\n")

        if self.field_importance:
            out.write(u"Field importance:\n")
            print_field_importance(out=out)

        extract_common_path(groups)

        for group in [x[0] for x in predictions]:
            details = groups[group]['details']
            path = [prediction.to_rule(tree.fields) for
                    prediction in groups[group]['total'][0]]
            data_per_group = groups[group]['total'][1] * 1.0 / tree.count
            pred_per_group = groups[group]['total'][2] * 1.0 / tree.count
            out.write(utf8(u"\n\n%s : (data %.2f%% / prediction %.2f%%) %s\n" %
                           (group,
                            round(data_per_group, 4) * 100,
                            round(pred_per_group, 4) * 100,
                            " and ".join(path))))

            if len(details) == 0:
                out.write(u"    The model will never predict this class\n")
            for j in range(0, len(details)):
                subgroup = details[j]
                pred_per_sgroup = subgroup[1] * 1.0 / groups[group]['total'][2]
                path = [prediction.to_rule(tree.fields) for
                        prediction in subgroup[0]]
                path_chain = " and ".join(path) if len(path) else "(root node)"
                out.write(utf8(u"    · %.2f%%: %s%s\n" %
                               (round(pred_per_sgroup, 4) * 100,
                                path_chain,
                                confidence_error(subgroup[2]))))
        out.flush()

    def hadoop_python_mapper(self, out=sys.stdout):
        """Returns a hadoop mapper header to make predictions in python

        """
        input_fields = [(value, key) for (key, value) in
                        sorted(self.inverted_fields.items(),
                               key=lambda x: x[1])]
        parameters = [value for (key, value) in
                      input_fields if key != self.tree.objective_field]
        args = []
        for field in input_fields:
            slug = slugify(self.tree.fields[field[0]]['name'])
            self.tree.fields[field[0]].update(slug=slug)
            if field[0] != self.tree.objective_field:
                args.append("\"" + self.tree.fields[field[0]]['slug'] + "\"")
        output = \
u"""#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import csv
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


class CSVInput(object):
    \"\"\"Reads and parses csv input from stdin

       Expects a data section (without headers) with the following fields:
       %s

       Data is processed to fall into the corresponding input type by applying
       INPUT_TYPES, and per field PREFIXES and SUFFIXES are removed. You can
       also provide strings to be considered as no content markers in
       MISSING_TOKENS.
    \"\"\"
    def __init__(self, input=sys.stdin):
        \"\"\" Opens stdin and defines parsing constants

        \"\"\"
        try:
            self.reader = csv.reader(input, delimiter=',', quotechar='\"')
""" % ",".join(parameters)

        output += (u"\n%sself.INPUT_FIELDS = [%s]\n" %
                  ((INDENT * 3), (",\n " + INDENT * 8).join(args)))

        input_types = []
        prefixes = []
        suffixes = []
        count = 0
        fields = self.tree.fields
        for key in [key[0] for key in input_fields
                    if key != self.tree.objective_field]:
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
        output += u"\n%s%s%s" % (static_content,
                                 formatter.join(input_types),
                                 "]\n")
        static_content = "%sself.PREFIXES = {" % (INDENT * 3)
        formatter = ",\n%s" % (" " * len(static_content))
        output += u"\n%s%s%s" % (static_content,
                                 formatter.join(prefixes),
                                 "}\n")
        static_content = "%sself.SUFFIXES = {" % (INDENT * 3)
        formatter = ",\n%s" % (" " * len(static_content))
        output += u"\n%s%s%s" % (static_content,
                                 formatter.join(suffixes),
                                 "}\n")
        output += \
u"""            self.MISSING_TOKENS = ['?']
        except Exception, exc:
            sys.stderr.write(\"Cannot read csv\"
                             \" input. %s\\n\" % str(exc))

    def __iter__(self):
        \"\"\" Iterator method

        \"\"\"
        return self

    def next(self):
        \"\"\" Returns processed data in a list structure

        \"\"\"
        def normalize(value):
            \"\"\"Transforms to unicode and cleans missing tokens
            \"\"\"
            value = unicode(value.decode('utf-8'))
            return \"\" if value in self.MISSING_TOKENS else value

        def cast(function_value):
            \"\"\"Type related transformations
            \"\"\"
            function, value = function_value
            if not len(value):
                return None
            if function is None:
                return value
            else:
                return function(value)

        try:
            values = self.reader.next()
        except StopIteration:
            raise StopIteration()
        if len(values) < len(self.INPUT_FIELDS):
            sys.stderr.write(\"Found %s fields when %s were expected.\\n\" %
                             (len(values), len(self.INPUT_FIELDS)))
            raise StopIteration()
        else:
            values = values[0:len(self.INPUT_FIELDS)]
        try:
            values = map(normalize, values)
            for key in self.PREFIXES:
                prefix_len = len(self.PREFIXES[key])
                if values[key][0:prefix_len] == self.PREFIXES[key]:
                    values[key] = values[key][prefix_len:]
            for key in self.SUFFIXES:
                suffix_len = len(self.SUFFIXES[key])
                if values[key][-suffix_len:] == self.SUFFIXES[key]:
                    values[key] = values[key][0:-suffix_len]
            function_tuples = zip(self.INPUT_TYPES, values)
            values = map(cast, function_tuples)
            data = {}
            for i in range(len(values)):
                data.update({self.INPUT_FIELDS[i]: values[i]})
            return data
        except Exception, exc:
            sys.stderr.write(\"Error in data transformations. %s\\n\" %
                             str(exc))
            return False
\n\n
"""
        out.write(utf8(output))
        out.flush()

        self.tree.python(out, self.docstring(),
                         input_map=True)
        output = \
u"""
csv = CSVInput()
for values in csv:
    if not isinstance(values, bool):
        print u'%%s\\t%%s' %% (repr(values), repr(predict_%s(values)))
\n\n
""" % fields[self.tree.objective_field]['slug']
        out.write(utf8(output))
        out.flush()

    def hadoop_python_reducer(self, out=sys.stdout):
        """Returns a hadoop reducer to make predictions in python

        """

        output = \
u"""#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

count = 0
previous = None

def print_result(values, prediction, count):
    \"\"\"Prints input data and predicted value as an ordered list.

    \"\"\"
    result = \"[%s, %s]\" % (values, prediction)
    print u\"%s\\t%s\" % (result, count)

for line in sys.stdin:
    values, prediction = line.strip().split('\\t')
    if previous is None:
        previous = (values, prediction)
    if values != previous[0]:
        print_result(previous[0], previous[1], count)
        previous = (values, prediction)
        count = 0
    count += 1
if count > 0:
    print_result(previous[0], previous[1], count)
"""
        out.write(utf8(output))
        out.flush()

    def to_prediction(self, value_as_string, data_locale=DEFAULT_LOCALE):
        """Given a prediction string, returns its value in the required type

        """
        if not isinstance(value_as_string, unicode):
            value_as_string = unicode(value_as_string, "utf-8")

        objective_field = self.tree.objective_field
        if self.tree.fields[objective_field]['optype'] == 'numeric':
            if data_locale is None:
                data_locale = self.locale
            find_locale(data_locale)
            datatype = self.tree.fields[objective_field]['datatype']
            cast_function = PYTHON_FUNC.get(datatype, None)
            if cast_function is not None:
                return cast_function(value_as_string)
        return value_as_string
