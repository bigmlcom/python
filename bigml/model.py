# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2013-2016 BigML
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

model = Model('model/5026965515526876630001b2')
model.predict({"petal length": 3, "petal width": 1})

You can also see model in a IF-THEN rule format with:

model.rules()

Or auto-generate a python function code for the model with:

model.python()

"""
import logging
import sys
import locale
import json

from functools import partial

from bigml.api import FINISHED
from bigml.api import (BigML, get_model_id, get_status)
from bigml.util import (slugify, markdown_cleanup,
                        prefix_as_comment, utf8,
                        find_locale, cast)
from bigml.util import DEFAULT_LOCALE
from bigml.tree import Tree, LAST_PREDICTION, PROPORTIONAL
from bigml.predicate import Predicate
from bigml.basemodel import BaseModel, retrieve_resource, print_importance
from bigml.basemodel import ONLY_MODEL
from bigml.multivote import ws_confidence
from bigml.io import UnicodeWriter
from bigml.path import Path, BRIEF


LOGGER = logging.getLogger('BigML')

# we use the atof conversion for integers to include integers written as
# 10.0
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

DEFAULT_IMPURITY = 0.2


def print_distribution(distribution, out=sys.stdout):
    """Prints distribution data

    """
    total = reduce(lambda x, y: x + y,
                   [group[1] for group in distribution])
    for group in distribution:
        out.write(utf8(
            u"    %s: %.2f%% (%d instance%s)\n" % (
                group[0],
                round(group[1] * 1.0 / total, 4) * 100,
                group[1],
                u"" if group[1] == 1 else u"s")))


class Model(BaseModel):
    """ A lightweight wrapper around a Tree model.

    Uses a BigML remote model to build a local version that can be used
    to generate predictions locally.

    """

    def __init__(self, model, api=None):
        """The Model constructor can be given as first argument:
            - a model structure
            - a model id
            - a path to a JSON file containing a model structure

        """
        self.resource_id = None
        self.ids_map = {}
        self.terms = {}
        # the string can be a path to a JSON file
        if isinstance(model, basestring):
            try:
                with open(model) as model_file:
                    model = json.load(model_file)
                    self.resource_id = get_model_id(model)
                    if self.resource_id is None:
                        raise ValueError("The JSON file does not seem"
                                         " to contain a valid BigML model"
                                         " representation.")
            except IOError:
                # if it is not a path, it can be a model id
                self.resource_id = get_model_id(model)
                if self.resource_id is None:
                    if model.find('model/') > -1:
                        raise Exception(
                            api.error_message(model,
                                              resource_type='model',
                                              method='get'))
                    else:
                        raise IOError("Failed to open the expected JSON file"
                                      " at %s" % model)
            except ValueError:
                raise ValueError("Failed to interpret %s."
                                 " JSON file expected.")

        if not (isinstance(model, dict) and 'resource' in model and
                model['resource'] is not None):
            if api is None:
                api = BigML(storage=STORAGE)
            query_string = ONLY_MODEL
            model = retrieve_resource(api, self.resource_id,
                                      query_string=query_string)
        else:
            self.resource_id = get_model_id(model)
        BaseModel.__init__(self, model, api=api)
        if 'object' in model and isinstance(model['object'], dict):
            model = model['object']

        if 'model' in model and isinstance(model['model'], dict):
            status = get_status(model)
            if 'code' in status and status['code'] == FINISHED:
                distribution = model['model']['distribution']['training']
                # will store global information in the tree: regression and
                # max_bins number
                tree_info = {'max_bins': 0}
                self.tree = Tree(
                    model['model']['root'],
                    self.fields,
                    objective_field=self.objective_id,
                    root_distribution=distribution,
                    parent_id=None,
                    ids_map=self.ids_map,
                    tree_info=tree_info)
                self.tree.regression = tree_info['regression']
                if self.tree.regression:
                    self._max_bins = tree_info['max_bins']
            else:
                raise Exception("The model isn't finished yet")
        else:
            raise Exception("Cannot create the Model instance. Could not"
                            " find the 'model' key in the resource:\n\n%s" %
                            model)
        if self.tree.regression:
            try:
                import numpy
                import scipy
                self.regression_ready = True
            except ImportError:
                self.regression_ready = False

    def list_fields(self, out=sys.stdout):
        """Prints descriptions of the fields for this model.

        """
        self.tree.list_fields(out)

    def get_leaves(self, filter_function=None):
        """Returns a list that includes all the leaves of the model.

           filter_function should be a function that returns a boolean
           when applied to each leaf node.
        """
        return self.tree.get_leaves(filter_function=filter_function)

    def impure_leaves(self, impurity_threshold=DEFAULT_IMPURITY):
        """Returns a list of leaves that are impure

        """
        if self.tree.regression:
            raise AttributeError("This method is available for "
                                 " categorization models only.")
        def is_impure(node, impurity_threshold=impurity_threshold):
            """Returns True if the gini impurity of the node distribution
               goes above the impurity threshold.

            """
            return node.get('impurity') > impurity_threshold

        is_impure = partial(is_impure, impurity_threshold=impurity_threshold)
        return self.get_leaves(filter_function=is_impure)

    def predict(self, input_data, by_name=True,
                print_path=False, out=sys.stdout, with_confidence=False,
                missing_strategy=LAST_PREDICTION,
                add_confidence=False,
                add_path=False,
                add_distribution=False,
                add_count=False,
                add_median=False,
                add_next=False,
                add_min=False,
                add_max=False,
                multiple=None):
        """Makes a prediction based on a number of field values.

        By default the input fields must be keyed by field name but you can use
        `by_name` to input them directly keyed by id.

        input_data: Input data to be predicted
        by_name: Boolean, True if input_data is keyed by names
        print_path: Boolean, if True the rules that lead to the prediction
                    are printed
        out: output handler
        with_confidence: Boolean, if True, all the information in the node
                         (prediction, confidence, distribution and count)
                         is returned in a list format
        missing_strategy: LAST_PREDICTION|PROPORTIONAL missing strategy for
                          missing fields
        add_confidence: Boolean, if True adds confidence to the dict output
        add_path: Boolean, if True adds path to the dict output
        add_distribution: Boolean, if True adds distribution info to the
                          dict output
        add_count: Boolean, if True adds the number of instances in the
                       node to the dict output
        add_median: Boolean, if True adds the median of the values in
                    the distribution
        add_next: Boolean, if True adds the field that determines next
                  split in the tree
        add_min: Boolean, if True adds the minimum value in the prediction's
                 distribution (for regressions only)
        add_max: Boolean, if True adds the maximum value in the prediction's
                 distribution (for regressions only)
        multiple: For categorical fields, it will return the categories
                  in the distribution of the predicted node as a
                  list of dicts:
                    [{'prediction': 'Iris-setosa',
                      'confidence': 0.9154
                      'probability': 0.97
                      'count': 97},
                     {'prediction': 'Iris-virginica',
                      'confidence': 0.0103
                      'probability': 0.03,
                      'count': 3}]
                  The value of this argument can either be an integer
                  (maximum number of categories to be returned), or the
                  literal 'all', that will cause the entire distribution
                  in the node to be returned.

        """
        # Checks if this is a regression model, using PROPORTIONAL
        # missing_strategy
        if (self.tree.regression and missing_strategy == PROPORTIONAL and
                not self.regression_ready):
            raise ImportError("Failed to find the numpy and scipy libraries,"
                              " needed to use proportional missing strategy"
                              " for regressions. Please install them before"
                              " using local predictions for the model.")
        # Checks and cleans input_data leaving the fields used in the model
        input_data = self.filter_input_data(input_data, by_name=by_name)

        # Strips affixes for numeric values and casts to the final field type
        cast(input_data, self.fields)

        prediction = self.tree.predict(input_data,
                                       missing_strategy=missing_strategy)

        # Prediction path
        if print_path:
            out.write(utf8(u' AND '.join(prediction.path) + u' => %s \n' %
                           prediction.output))
            out.flush()
        output = prediction.output
        if with_confidence:
            output = [prediction.output,
                      prediction.confidence,
                      prediction.distribution,
                      prediction.count,
                      prediction.median]
        if multiple is not None and not self.tree.regression:
            output = []
            total_instances = float(prediction.count)
            distribution = enumerate(prediction.distribution)
            for index, [category, instances] in distribution:
                if ((isinstance(multiple, basestring) and multiple == 'all') or
                        (isinstance(multiple, int) and index < multiple)):
                    prediction_dict = {
                        'prediction': category,
                        'confidence': ws_confidence(category,
                                                    prediction.distribution),
                        'probability': instances / total_instances,
                        'count': instances}
                    output.append(prediction_dict)
        else:
            if (add_confidence or add_path or add_distribution or add_count or
                    add_median or add_next or add_min or add_max):
                output = {'prediction': prediction.output}
                if add_confidence:
                    output.update({'confidence': prediction.confidence})
                if add_path:
                    output.update({'path': prediction.path})
                if add_distribution:
                    output.update(
                        {'distribution': prediction.distribution,
                         'distribution_unit': prediction.distribution_unit})
                if add_count:
                    output.update({'count': prediction.count})
                if self.tree.regression and add_median:
                    output.update({'median': prediction.median})
                if add_next:
                    field = (None if len(prediction.children) == 0 else
                             prediction.children[0].predicate.field)
                    if field is not None and field in self.fields:
                        field = self.fields[field]['name']
                    output.update({'next': field})
                if self.tree.regression and add_min:
                    output.update({'min': prediction.min})
                if self.tree.regression and add_max:
                    output.update({'max': prediction.max})

        return output

    def docstring(self):
        """Returns the docstring describing the model.

        """
        docstring = (u"Predictor for %s from %s\n" % (
            self.fields[self.tree.objective_id]['name'],
            self.resource_id))
        self.description = (
            unicode(
                markdown_cleanup(self.description).strip()) or
            u'Predictive model by BigML - Machine Learning Made Easy')
        docstring += u"\n" + INDENT * 2 + (
            u"%s" % prefix_as_comment(INDENT * 2, self.description))
        return docstring

    def get_ids_path(self, filter_id):
        """Builds the list of ids that go from a given id to the tree root

        """
        ids_path = None
        if filter_id is not None and self.tree.id is not None:
            if filter_id not in self.ids_map:
                raise ValueError("The given id does not exist.")
            else:
                ids_path = [filter_id]
                last_id = filter_id
                while self.ids_map[last_id].parent_id is not None:
                    ids_path.append(self.ids_map[last_id].parent_id)
                    last_id = self.ids_map[last_id].parent_id
        return ids_path

    def rules(self, out=sys.stdout, filter_id=None, subtree=True):
        """Returns a IF-THEN rule set that implements the model.

        `out` is file descriptor to write the rules.

        """
        ids_path = self.get_ids_path(filter_id)
        return self.tree.rules(out, ids_path=ids_path, subtree=subtree)

    def python(self, out=sys.stdout, hadoop=False,
               filter_id=None, subtree=True):
        """Returns a basic python function that implements the model.

        `out` is file descriptor to write the python code.

        """
        ids_path = self.get_ids_path(filter_id)
        if hadoop:
            return (self.hadoop_python_mapper(out=out,
                                              ids_path=ids_path,
                                              subtree=subtree) or
                    self.hadoop_python_reducer(out=out))
        else:
            return self.tree.python(out, self.docstring(), ids_path=ids_path,
                                    subtree=subtree)

    def tableau(self, out=sys.stdout, hadoop=False,
                filter_id=None, subtree=True):
        """Returns a basic tableau function that implements the model.

        `out` is file descriptor to write the tableau code.

        """
        ids_path = self.get_ids_path(filter_id)
        if hadoop:
            return "Hadoop output not available."
        else:
            response = self.tree.tableau(out, ids_path=ids_path,
                                         subtree=subtree)
            if response:
                out.write(u"END\n")
            else:
                out.write(u"\nThis function cannot be represented "
                          u"in Tableau syntax.\n")
            out.flush()
            return None

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

        def add_to_groups(groups, output, path, count, confidence,
                          impurity=None):
            """Adds instances to groups array

            """
            group = output
            if output not in groups:
                groups[group] = {'total': [[], 0, 0],
                                 'details': []}
            groups[group]['details'].append([path, count, confidence,
                                             impurity])
            groups[group]['total'][2] += count

        def depth_first_search(tree, path):
            """Search for leafs' values and instances

            """
            if isinstance(tree.predicate, Predicate):
                path.append(tree.predicate)
                if tree.predicate.term:
                    term = tree.predicate.term
                    if tree.predicate.field not in self.terms:
                        self.terms[tree.predicate.field] = []
                    if term not in self.terms[tree.predicate.field]:
                        self.terms[tree.predicate.field].append(term)

            if len(tree.children) == 0:
                add_to_groups(groups, tree.output,
                              path, tree.count, tree.confidence, tree.impurity)
                return tree.count
            else:
                children = tree.children[:]
                children.reverse()

                children_sum = 0
                for child in children:
                    children_sum += depth_first_search(child, path[:])
                if children_sum < tree.count:
                    add_to_groups(groups, tree.output, path,
                                  tree.count - children_sum, tree.confidence,
                                  tree.impurity)
                return tree.count

        depth_first_search(tree, path)

        return groups

    def get_data_distribution(self):
        """Returns training data distribution

        """
        tree = self.tree
        distribution = tree.distribution

        return sorted(distribution, key=lambda x: x[0])

    def get_prediction_distribution(self, groups=None):
        """Returns model predicted distribution

        """
        if groups is None:
            groups = self.group_prediction()

        predictions = [[group, groups[group]['total'][2]] for group in groups]
        # remove groups that are not predicted
        predictions = [prediction for prediction in predictions \
            if prediction[1] > 0]

        return sorted(predictions, key=lambda x: x[0])

    def summarize(self, out=sys.stdout, format=BRIEF):
        """Prints summary grouping distribution as class header and details

        """
        tree = self.tree

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

        def confidence_error(value, impurity=None):
            """Returns confidence for categoric objective fields
               and error for numeric objective fields
            """
            if value is None:
                return ""
            impurity_literal = ""
            if impurity is not None and impurity > 0:
                impurity_literal = "; impurity: %.2f%%" % (round(impurity, 4))
            objective_type = self.fields[tree.objective_id]['optype']
            if objective_type == 'numeric':
                return u" [Error: %s]" % value
            else:
                return u" [Confidence: %.2f%%%s]" % ((round(value, 4) * 100),
                                                     impurity_literal)

        distribution = self.get_data_distribution()

        out.write(utf8(u"Data distribution:\n"))
        print_distribution(distribution, out=out)
        out.write(utf8(u"\n\n"))

        groups = self.group_prediction()
        predictions = self.get_prediction_distribution(groups)

        out.write(utf8(u"Predicted distribution:\n"))
        print_distribution(predictions, out=out)
        out.write(utf8(u"\n\n"))

        if self.field_importance:
            out.write(utf8(u"Field importance:\n"))
            print_importance(self, out=out)

        extract_common_path(groups)

        out.write(utf8(u"\n\nRules summary:"))

        for group in [x[0] for x in predictions]:
            details = groups[group]['details']
            path = Path(groups[group]['total'][0])
            data_per_group = groups[group]['total'][1] * 1.0 / tree.count
            pred_per_group = groups[group]['total'][2] * 1.0 / tree.count
            out.write(utf8(u"\n\n%s : (data %.2f%% / prediction %.2f%%) %s" %
                           (group,
                            round(data_per_group, 4) * 100,
                            round(pred_per_group, 4) * 100,
                            path.to_rules(self.fields, format=format))))

            if len(details) == 0:
                out.write(utf8(u"\n    The model will never predict this"
                               u" class\n"))
            elif len(details) == 1:
                subgroup = details[0]
                out.write(utf8(u"%s\n" % confidence_error(
                    subgroup[2], impurity=subgroup[3])))
            else:
                out.write(utf8(u"\n"))
                for j in range(0, len(details)):
                    subgroup = details[j]
                    pred_per_sgroup = subgroup[1] * 1.0 / \
                        groups[group]['total'][2]
                    path = Path(subgroup[0])
                    path_chain = path.to_rules(self.fields, format=format) if \
                        path.predicates else "(root node)"
                    out.write(utf8(u"    · %.2f%%: %s%s\n" %
                                   (round(pred_per_sgroup, 4) * 100,
                                    path_chain,
                                    confidence_error(subgroup[2],
                                                     impurity=subgroup[3]))))

        out.flush()

    def hadoop_python_mapper(self, out=sys.stdout, ids_path=None,
                             subtree=True):
        """Returns a hadoop mapper header to make predictions in python

        """
        input_fields = [(value, key) for (key, value) in
                        sorted(self.inverted_fields.items(),
                               key=lambda x: x[1])]
        parameters = [value for (key, value) in
                      input_fields if key != self.tree.objective_id]
        args = []
        for field in input_fields:
            slug = slugify(self.fields[field[0]]['name'])
            self.fields[field[0]].update(slug=slug)
            if field[0] != self.tree.objective_id:
                args.append("\"" + self.fields[field[0]]['slug'] + "\"")
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

        output += (
            u"\n%sself.INPUT_FIELDS = [%s]\n" %
            ((INDENT * 3), (",\n " + INDENT * 8).join(args)))

        input_types = []
        prefixes = []
        suffixes = []
        count = 0
        fields = self.fields
        for key in [key[0] for key in input_fields
                    if key != self.tree.objective_id]:
            input_type = ('None' if fields[key]['datatype'] not in
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
                         input_map=True,
                         ids_path=ids_path,
                         subtree=subtree)
        output = \
u"""
csv = CSVInput()
for values in csv:
    if not isinstance(values, bool):
        print u'%%s\\t%%s' %% (repr(values), repr(predict_%s(values)))
\n\n
""" % fields[self.tree.objective_id]['slug']
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

        objective_id = self.tree.objective_id
        if self.fields[objective_id]['optype'] == 'numeric':
            if data_locale is None:
                data_locale = self.locale
            find_locale(data_locale)
            datatype = self.fields[objective_id]['datatype']
            cast_function = PYTHON_FUNC.get(datatype, None)
            if cast_function is not None:
                return cast_function(value_as_string)
        return value_as_string

    def average_confidence(self):
        """Average for the confidence of the predictions resulting from
           running the training data through the model

        """
        total = 0.0
        cumulative_confidence = 0
        groups = self.group_prediction()
        for _, predictions in groups.items():
            for _, count, confidence in predictions['details']:
                cumulative_confidence += count * confidence
                total += count
        return float('nan') if total == 0.0 else cumulative_confidence

    def get_nodes_info(self, headers, leaves_only=False):
        """Generator that yields the nodes information in a row format

        """
        return self.tree.get_nodes_info(headers, leaves_only=leaves_only)

    def tree_CSV(self, file_name=None, leaves_only=False):
        """To be deprecated. See tree_csv

        """
        self.tree_csv(file_name=file_name, leaves_only=leaves_only)

    def tree_csv(self, file_name=None, leaves_only=False):
        """Outputs the node structure to a CSV file or array

        """
        headers_names = []
        if self.tree.regression:
            headers_names.append(
                self.fields[self.tree.objective_id]['name'])
            headers_names.append("error")
            for index in range(0, self._max_bins):
                headers_names.append("bin%s_value" % index)
                headers_names.append("bin%s_instances" % index)
        else:
            headers_names.append(
                self.fields[self.tree.objective_id]['name'])
            headers_names.append("confidence")
            headers_names.append("impurity")
            for category, _ in self.tree.distribution:
                headers_names.append(category)

        nodes_generator = self.get_nodes_info(headers_names,
                                              leaves_only=leaves_only)
        if file_name is not None:
            with UnicodeWriter(file_name) as writer:
                writer.writerow([header.encode("utf-8")
                                 for header in headers_names])
                for row in nodes_generator:
                    writer.writerow([item if not isinstance(item, basestring)
                                     else item.encode("utf-8")
                                     for item in row])
        else:
            rows = []
            rows.append(headers_names)
            for row in nodes_generator:
                rows.append(row)
            return rows
