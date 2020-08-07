# -*- coding: utf-8 -*-
#
# Copyright 2013-2020 BigML
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


from functools import partial, cmp_to_key

from bigml.api import FINISHED, STATUSES
from bigml.api import get_status, get_api_connection
from bigml.util import slugify, markdown_cleanup, prefix_as_comment, utf8, \
    find_locale, cast
from bigml.util import DEFAULT_LOCALE, PRECISION
from bigml.tree import Tree, LAST_PREDICTION, PROPORTIONAL
from bigml.boostedtree import BoostedTree
from bigml.predicate import Predicate
from bigml.basemodel import BaseModel, get_resource_dict, print_importance
from bigml.multivote import ws_confidence
from bigml.io import UnicodeWriter
from bigml.path import Path, BRIEF
from bigml.prediction import Prediction
from functools import reduce


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
                    for numtype, function in PYTHON_CONV.items()])

INDENT = '    '

DEFAULT_IMPURITY = 0.2

OPERATING_POINT_KINDS = ["probability", "confidence"]

DICTIONARY = "dict"

OUT_FORMATS = [DICTIONARY, "list"]


def init_structure(to):
    """Creates the empty structure to store predictions depending on the
    chosen format.

    """
    if to is not None and to not in OUT_FORMATS:
        raise ValueError("The allowed formats are %s." % \
            ", ".join(OUT_FORMATS))
    return {} if to is DICTIONARY else () if to is None \
        else []


def cast_prediction(full_prediction, to=None,
                    confidence=False, probability=False,
                    path=False, distribution=False,
                    count=False, next=False, d_min=False,
                    d_max=False, median=False,
                    unused_fields=False):
    """Creates the output filtering the attributes in a full
    prediction.

        to: defines the output format. The current
            values are: None, `list` and `dict`. If not set, the result
            will be expressed as a tuple. The other two options will
            produce a list and a dictionary respectively. In the case of lists,
            the attributes are stored in the same order used in
            the signature of the function.
        confidence: Boolean. If True, adds the confidence to the output
        probability: Boolean. If True, adds the probability to the output
        path: Boolean. If True adds the prediction path to the output
        distribution: distribution of probabilities for each
                      of the objective field classes
        count: Boolean. If True adds the number of training instances in the
               prediction node to the output
        next: Boolean. If True adds the next predicate field to the output
        d_min: Boolean. If True adds the predicted node distribution
               minimum to the output
        d_max: Boolean. If True adds the predicted node distribution
               maximum to the output
        median: Boolean. If True adds the median of the predicted node
                distribution to the output
        unused_fields: Boolean. If True adds the fields used in the input
                       data that have not been used by the model.

    """
    prediction_properties = [ \
        "prediction", "confidence", "probability", "path", "distribution",
        "count", "next", "d_min", "d_max", "median", "unused_fields"]
    prediction = True
    result = init_structure(to)
    for prop in prediction_properties:
        value = full_prediction.get(prop)
        if eval(prop):
            if to is None:
                # tuple
                result = result + (value,)
            elif to == DICTIONARY:
                result.update({prop: value})
            else:
                # list
                result.append(value)
    return result


def sort_categories(a, b, categories_list):
    """Sorts a list of dictionaries with category keys according to their
    value and order in the categories_list. If not found, alphabetic order is
    used.

    """
    index_a = categories_list.index(a["category"])
    index_b = categories_list.index(b["category"])
    if index_a < 0 and index_b < 0:
        index_a = a['category']
        index_b = b['category']
    if index_b < index_a:
        return 1
    if index_b > index_a:
        return -1
    return 0


def print_distribution(distribution, out=sys.stdout):
    """Prints distribution data

    """
    total = reduce(lambda x, y: x + y,
                   [group[1] for group in distribution])
    for group in distribution:
        out.write(utf8(
            "    %s: %.2f%% (%d instance%s)\n" % (
                group[0],
                round(group[1] * 1.0 / total, 4) * 100,
                group[1],
                "" if group[1] == 1 else "s")))


def parse_operating_point(operating_point, operating_kinds, class_names):
    """Checks the operating point contents and extracts the three defined
    variables

    """
    if "kind" not in operating_point:
        raise ValueError("Failed to find the kind of operating point.")
    elif operating_point["kind"] not in operating_kinds:
        raise ValueError("Unexpected operating point kind. Allowed values"
                         " are: %s." % ", ".join(operating_kinds))
    if "threshold" not in operating_point:
        raise ValueError("Failed to find the threshold of the operating"
                         "point.")
    if operating_point["threshold"] > 1 or \
            operating_point["threshold"] < 0:
        raise ValueError("The threshold value should be in the 0 to 1"
                         " range.")
    if "positive_class" not in operating_point:
        raise ValueError("The operating point needs to have a"
                         " positive_class attribute.")
    else:
        positive_class = operating_point["positive_class"]
        if positive_class not in class_names:
            raise ValueError("The positive class must be one of the"
                             "objective field classes: %s." %
                             ", ".join(class_names))
    kind = operating_point["kind"]
    threshold = operating_point["threshold"]

    return kind, threshold, positive_class


class Model(BaseModel):
    """ A lightweight wrapper around a Tree model.

    Uses a BigML remote model to build a local version that can be used
    to generate predictions locally.

    """

    def __init__(self, model, api=None, fields=None):
        """The Model constructor can be given as first argument:
            - a model structure
            - a model id
            - a path to a JSON file containing a model structure

        """
        self.resource_id = None
        self.ids_map = {}
        self.terms = {}
        self.regression = False
        self.boosting = None
        self.class_names = None
        self.api = get_api_connection(api)
        self.resource_id, model = get_resource_dict( \
            model, "model", api=self.api)

        if 'object' in model and isinstance(model['object'], dict):
            model = model['object']

        if 'model' in model and isinstance(model['model'], dict):
            status = get_status(model)
            if 'code' in status and status['code'] == FINISHED:

                self.input_fields = model["input_fields"]
                BaseModel.__init__(self, model, api=api, fields=fields)

                # boosting models are to be handled using the BoostedTree
                # class
                if model.get("boosted_ensemble"):
                    self.boosting = model.get('boosting', False)
                if self.boosting == {}:
                    self.boosting = False

                self.regression = \
                    not self.boosting and \
                    self.fields[self.objective_id]['optype'] == 'numeric' \
                    or (self.boosting and \
                    self.boosting.get("objective_class") is None)
                if not hasattr(self, 'tree_class'):
                    self.tree_class = Tree if not self.boosting else \
                        BoostedTree

                if self.boosting:
                    self.tree = self.tree_class(
                        model['model']['root'],
                        self.fields,
                        objective_field=self.objective_id)
                else:
                    distribution = model['model']['distribution']['training']
                    # will store global information in the tree: regression and
                    # max_bins number
                    tree_info = {'max_bins': 0}
                    self.tree = self.tree_class(
                        model['model']['root'],
                        self.fields,
                        objective_field=self.objective_id,
                        root_distribution=distribution,
                        parent_id=None,
                        ids_map=self.ids_map,
                        tree_info=tree_info)

                    self.tree.regression = tree_info['regression']

                    if self.tree.regression:
                        try:
                            import numpy
                            import scipy
                            self._max_bins = tree_info['max_bins']
                            self.regression_ready = True
                        except ImportError:
                            self.regression_ready = False
                    else:
                        root_dist = self.tree.distribution
                        self.class_names = sorted([category[0]
                                                   for category in root_dist])
                        self.objective_categories = [category for \
                            category, _ in self.fields[self.objective_id][ \
                           "summary"]["categories"]]
                if not self.regression and not self.boosting:
                    self.laplacian_term = self._laplacian_term()
            else:
                raise Exception("Cannot create the Model instance."
                                " Only correctly finished models can be used."
                                " The model status is currently: %s\n" %
                                STATUSES[status['code']])
        else:
            raise Exception("Cannot create the Model instance. Could not"
                            " find the 'model' key in the resource:\n\n%s" %
                            model)

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
        if self.regression or self.boosting:
            raise AttributeError("This method is available for non-boosting"
                                 " categorization models only.")
        def is_impure(node, impurity_threshold=impurity_threshold):
            """Returns True if the gini impurity of the node distribution
               goes above the impurity threshold.

            """
            return node.get('impurity') > impurity_threshold

        is_impure = partial(is_impure, impurity_threshold=impurity_threshold)
        return self.get_leaves(filter_function=is_impure)

    def _to_output(self, output_map, compact, value_key):
        if compact:
            return [round(output_map.get(name, 0.0), PRECISION)
                    for name in self.class_names]
        else:
            output = []
            for name in self.class_names:
                output.append({
                    'category': name,
                    value_key: round(output_map.get(name, 0.0), PRECISION)
                })
            return output

    def predict_confidence(self, input_data, missing_strategy=LAST_PREDICTION,
                           compact=False):
        """For classification models, Predicts a one-vs.-rest confidence value
        for each possible output class, based on input values.  This
        confidence value is a lower confidence bound on the predicted
        probability of the given class.  The input fields must be a
        dictionary keyed by field name for field ID.

        For regressions, the output is a single element list
        containing the prediction.

        :param input_data: Input data to be predicted
        :param missing_strategy: LAST_PREDICTION|PROPORTIONAL missing strategy
                                 for missing fields
        :param compact: If False, prediction is returned as a list of maps, one
                        per class, with the keys "prediction" and "confidence"
                        mapped to the name of the class and its confidence,
                        respectively.  If True, returns a list of confidences
                        ordered by the sorted order of the class names.

        """
        if self.regression:
            prediction = self.predict(input_data,
                                      missing_strategy=missing_strategy,
                                      full=not compact)

            if compact:
                output = [prediction]
            else:
                output = cast_prediction(prediction, to=DICTIONARY,
                                         confidence=True)
            return output

        elif self.boosting:
            raise AttributeError("This method is available for non-boosting"
                                 " models only.")

        root_dist = self.tree.distribution
        category_map = {category[0]: 0.0 for category in root_dist}
        prediction = self.predict(input_data,
                                  missing_strategy=missing_strategy,
                                  full=True)

        distribution = prediction['distribution']
        population = prediction['count']

        for class_info in distribution:
            name = class_info[0]
            category_map[name] = ws_confidence(name, distribution,
                                               ws_n=population)

        return self._to_output(category_map, compact, "confidence")

    def _laplacian_term(self):
        """Correction term based on the training dataset distribution

        """
        root_dist = self.tree.distribution

        if self.tree.weighted:
            category_map = {category[0]: 0.0 for category in root_dist}
        else:
            total = float(sum([category[1] for category in root_dist]))
            category_map = {category[0]: category[1] / total
                            for category in root_dist}
        return category_map

    def _probabilities(self, distribution):
        """Computes the probability of a distribution using a Laplacian
        correction.

        """
        total = 0 if self.tree.weighted else 1

        category_map = {}
        category_map.update(self.laplacian_term)
        for class_info in distribution:
            category_map[class_info[0]] += class_info[1]
            total += class_info[1]

        for k in category_map:
            category_map[k] /= total
        return category_map


    def predict_probability(self, input_data,
                            missing_strategy=LAST_PREDICTION,
                            compact=False):
        """For classification models, Predicts a probability for
        each possible output class, based on input values.  The input
        fields must be a dictionary keyed by field name for field ID.

        For regressions, the output is a single element list
        containing the prediction.

        :param input_data: Input data to be predicted
        :param missing_strategy: LAST_PREDICTION|PROPORTIONAL missing strategy
                                 for missing fields
        :param compact: If False, prediction is returned as a list of maps, one
                        per class, with the keys "prediction" and "probability"
                        mapped to the name of the class and it's probability,
                        respectively.  If True, returns a list of probabilities
                        ordered by the sorted order of the class names.
        """
        if self.regression or self.boosting:
            prediction = self.predict(input_data,
                                      missing_strategy=missing_strategy,
                                      full=not compact)

            if compact:
                output = [prediction]
            else:
                output = prediction
        else:

            prediction = self.predict(input_data,
                                      missing_strategy=missing_strategy,
                                      full=True)
            category_map = self._probabilities(prediction['distribution'])
            output = self._to_output(category_map, compact, "probability")

        return output

    def predict_operating(self, input_data,
                          missing_strategy=LAST_PREDICTION,
                          operating_point=None):
        """Computes the prediction based on a user-given operating point.

        """

        kind, threshold, positive_class = parse_operating_point( \
            operating_point, OPERATING_POINT_KINDS, self.class_names)
        if kind == "probability":
            predictions = self.predict_probability(input_data,
                                                   missing_strategy, False)
        else:
            predictions = self.predict_confidence(input_data,
                                                  missing_strategy, False)

        position = self.class_names.index(positive_class)
        if predictions[position][kind] > threshold:
            prediction = predictions[position]
        else:
            # if the threshold is not met, the alternative class with
            # highest probability or confidence is returned
            predictions.sort( \
                key=cmp_to_key( \
                lambda a, b: self._sort_predictions(a, b, kind)))
            prediction = predictions[0: 2]
            if prediction[0]["category"] == positive_class:
                prediction = prediction[1]
            else:
                prediction = prediction[0]
        prediction["prediction"] = prediction["category"]
        del prediction["category"]
        return prediction

    def _sort_predictions(self, a, b, criteria):
        """Sorts the categories in the predicted node according to the
        given criteria

        """
        if a[criteria] == b[criteria]:
            return sort_categories(a, b, self.objective_categories)
        return 1 if b[criteria] > a[criteria] else -1

    def predict_operating_kind(self, input_data,
                               missing_strategy=LAST_PREDICTION,
                               operating_kind=None):
        """Computes the prediction based on a user-given operating kind.

        """
        kind = operating_kind.lower()
        if kind not in OPERATING_POINT_KINDS:
            raise ValueError("Allowed operating kinds are %s. %s found." %
                             (", ".join(OPERATING_POINT_KINDS), kind))
        if kind == "probability":
            predictions = self.predict_probability(input_data,
                                                   missing_strategy, False)
        else:
            predictions = self.predict_confidence(input_data,
                                                  missing_strategy, False)

        if self.regression:
            prediction = predictions
        else:
            predictions.sort( \
                key=cmp_to_key( \
                lambda a, b: self._sort_predictions(a, b, kind)))
            prediction = predictions[0]
            prediction["prediction"] = prediction["category"]
            del prediction["category"]
        return prediction

    def predict(self, input_data, missing_strategy=LAST_PREDICTION,
                operating_point=None, operating_kind=None, full=False):
        """Makes a prediction based on a number of field values.

        input_data: Input data to be predicted
        missing_strategy: LAST_PREDICTION|PROPORTIONAL missing strategy for
                          missing fields
        operating_point: In classification models, this is the point of the
                         ROC curve where the model will be used at. The
                         operating point can be defined in terms of:
                         - the positive_class, the class that is important to
                           predict accurately
                         - the probability_threshold (or confidence_threshold),
                           the probability (or confidence) that is stablished
                           as minimum for the positive_class to be predicted.
                         The operating_point is then defined as a map with
                         two attributes, e.g.:
                           {"positive_class": "Iris-setosa",
                            "probability_threshold": 0.5}
                         or
                           {"positive_class": "Iris-setosa",
                            "confidence_threshold": 0.5}
        operating_kind: "probability" or "confidence". Sets the
                        property that decides the prediction. Used only if
                        no operating_point is used
        full: Boolean that controls whether to include the prediction's
              attributes. By default, only the prediction is produced. If set
              to True, the rest of available information is added in a
              dictionary format. The dictionary keys can be:
                  - prediction: the prediction value
                  - confidence: prediction's confidence
                  - probability: prediction's probability
                  - path: rules that lead to the prediction
                  - count: number of training instances supporting the
                           prediction
                  - next: field to check in the next split
                  - min: minim value of the training instances in the
                         predicted node
                  - max: maximum value of the training instances in the
                         predicted node
                  - median: median of the values of the training instances
                            in the predicted node
                  - unused_fields: list of fields in the input data that
                                   are not being used in the model
        """

        # Checks and cleans input_data leaving the fields used in the model
        unused_fields = []
        new_data = self.filter_input_data( \
            input_data,
            add_unused_fields=full)
        if full:
            input_data, unused_fields = new_data
        else:
            input_data = new_data
        # Strips affixes for numeric values and casts to the final field type
        cast(input_data, self.fields)

        full_prediction = self._predict( \
            input_data, missing_strategy=missing_strategy,
            operating_point=operating_point, operating_kind=operating_kind,
            unused_fields=unused_fields)
        if full:
            return dict((key, value) for key, value in \
                full_prediction.items() if value is not None)

        return full_prediction['prediction']

    def _predict(self, input_data, missing_strategy=LAST_PREDICTION,
                 operating_point=None, operating_kind=None,
                 unused_fields=None):
        """Makes a prediction based on a number of field values. Please,
        note that this function does not check the types for the input
        provided, so it's unsafe to use it directly without prior checking.

        """
        # When operating_point is used, we need the probabilities
        # (or confidences) of all possible classes to decide, so se use
        # the `predict_probability` or `predict_confidence` methods
        if operating_point:
            if self.regression:
                raise ValueError("The operating_point argument can only be"
                                 " used in classifications.")
            prediction = self.predict_operating( \
                input_data,
                missing_strategy=missing_strategy,
                operating_point=operating_point)
            return prediction

        if operating_kind:
            if self.regression:
                raise ValueError("The operating_kind argument can only be"
                                 " used in classifications.")
            prediction = self.predict_operating_kind( \
                input_data,
                missing_strategy=missing_strategy,
                operating_kind=operating_kind)
            return prediction

        # Checks if this is a regression model, using PROPORTIONAL
        # missing_strategy
        if (not self.boosting and
                self.regression and missing_strategy == PROPORTIONAL and
                not self.regression_ready):
            raise ImportError("Failed to find the numpy and scipy libraries,"
                              " needed to use proportional missing strategy"
                              " for regressions. Please install them before"
                              " using local predictions for the model.")

        prediction = self.tree.predict(input_data,
                                       missing_strategy=missing_strategy)

        if self.boosting and missing_strategy == PROPORTIONAL:
            # output has to be recomputed and comes in a different format
            g_sum, h_sum, population, path = prediction
            prediction = Prediction(
                - g_sum / (h_sum +  self.boosting.get("lambda", 1)),
                path,
                None,
                distribution=None,
                count=population,
                median=None,
                distribution_unit=None)

        result = vars(prediction)
        # changing key name to prediction
        result['prediction'] = result['output']
        del result['output']
        # next
        field = (None if len(prediction.children) == 0 else
                 prediction.children[0].predicate.field)
        if field is not None and field in self.model_fields:
            field = self.model_fields[field]['name']
        result.update({'next': field})
        del result['children']
        if not self.regression and not self.boosting:
            probabilities = self._probabilities(result['distribution'])
            result['probability'] = probabilities[result['prediction']]
        # adding unused fields, if any
        if unused_fields:
            result.update({'unused_fields': unused_fields})

        return result

    def docstring(self):
        """Returns the docstring describing the model.

        """
        objective_name = self.fields[self.tree.objective_id]['name'] if \
            not self.boosting else \
            self.fields[self.boosting["objective_field"]]['name']
        docstring = ("Predictor for %s from %s\n" % (
            objective_name,
            self.resource_id))
        self.description = (
            str(
                markdown_cleanup(self.description).strip()) or
            'Predictive model by BigML - Machine Learning Made Easy')
        docstring += "\n" + INDENT * 2 + (
            "%s" % prefix_as_comment(INDENT * 2, self.description))
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
        if self.boosting:
            raise AttributeError("This method is not available for boosting"
                                 " models.")
        ids_path = self.get_ids_path(filter_id)
        return self.tree.rules(out, ids_path=ids_path, subtree=subtree)

    def python(self, out=sys.stdout, hadoop=False,
               filter_id=None, subtree=True):
        """Returns a basic python function that implements the model.

        `out` is file descriptor to write the python code.

        """
        if self.boosting:
            raise AttributeError("This method is not available for boosting"
                                 " models.")
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
        if self.boosting:
            raise AttributeError("This method is not available for boosting"
                                 " models.")
        ids_path = self.get_ids_path(filter_id)
        if hadoop:
            return "Hadoop output not available."
        else:
            response = self.tree.tableau(out, ids_path=ids_path,
                                         subtree=subtree)
            if response:
                out.write("END\n")
            else:
                out.write("\nThis function cannot be represented "
                          "in Tableau syntax.\n")
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
        if self.boosting:
            raise AttributeError("This method is not available for boosting"
                                 " models.")
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
        if self.boosting:
            raise AttributeError("This method is not available for boosting"
                                 " models.")
        tree = self.tree
        distribution = tree.distribution

        return sorted(distribution, key=lambda x: x[0])

    def get_prediction_distribution(self, groups=None):
        """Returns model predicted distribution

        """
        if self.boosting:
            raise AttributeError("This method is not available for boosting"
                                 " models.")
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
        if self.boosting:
            raise AttributeError("This method is not available for boosting"
                                 " models.")
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
                return " [Error: %s]" % value
            else:
                return " [Confidence: %.2f%%%s]" % ((round(value, 4) * 100),
                                                     impurity_literal)

        distribution = self.get_data_distribution()

        out.write(utf8("Data distribution:\n"))
        print_distribution(distribution, out=out)
        out.write(utf8("\n\n"))

        groups = self.group_prediction()
        predictions = self.get_prediction_distribution(groups)

        out.write(utf8("Predicted distribution:\n"))
        print_distribution(predictions, out=out)
        out.write(utf8("\n\n"))

        if self.field_importance:
            out.write(utf8("Field importance:\n"))
            print_importance(self, out=out)

        extract_common_path(groups)

        out.write(utf8("\n\nRules summary:"))

        for group in [x[0] for x in predictions]:
            details = groups[group]['details']
            path = Path(groups[group]['total'][0])
            data_per_group = groups[group]['total'][1] * 1.0 / tree.count
            pred_per_group = groups[group]['total'][2] * 1.0 / tree.count
            out.write(utf8("\n\n%s : (data %.2f%% / prediction %.2f%%) %s" %
                           (group,
                            round(data_per_group, 4) * 100,
                            round(pred_per_group, 4) * 100,
                            path.to_rules(self.fields, format=format))))

            if len(details) == 0:
                out.write(utf8("\n    The model will never predict this"
                               " class\n"))
            elif len(details) == 1:
                subgroup = details[0]
                out.write(utf8("%s\n" % confidence_error(
                    subgroup[2], impurity=subgroup[3])))
            else:
                out.write(utf8("\n"))
                for j in range(0, len(details)):
                    subgroup = details[j]
                    pred_per_sgroup = subgroup[1] * 1.0 / \
                        groups[group]['total'][2]
                    path = Path(subgroup[0])
                    path_chain = path.to_rules(self.fields, format=format) if \
                        path.predicates else "(root node)"
                    out.write(utf8("    · %.2f%%: %s%s\n" %
                                   (round(pred_per_sgroup, 4) * 100,
                                    path_chain,
                                    confidence_error(subgroup[2],
                                                     impurity=subgroup[3]))))

        out.flush()

    def hadoop_python_mapper(self, out=sys.stdout, ids_path=None,
                             subtree=True):
        """Returns a hadoop mapper header to make predictions in python

        """
        if self.boosting:
            raise AttributeError("This method is not available for boosting"
                                 " models.")
        input_fields = [(value, key) for (key, value) in
                        sorted(list(self.inverted_fields.items()),
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
"""#!/usr/bin/env python
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
            "\n%sself.INPUT_FIELDS = [%s]\n" %
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
        output += \
"""            self.MISSING_TOKENS = ['?']
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
"""
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
"""#!/usr/bin/env python
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
        if not isinstance(value_as_string, str):
            value_as_string = str(value_as_string, "utf-8")

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
        if self.boosting:
            raise AttributeError("This method is not available for boosting"
                                 " models.")
        total = 0.0
        cumulative_confidence = 0
        groups = self.group_prediction()
        for _, predictions in list(groups.items()):
            for _, count, confidence in predictions['details']:
                cumulative_confidence += count * confidence
                total += count
        return float('nan') if total == 0.0 else cumulative_confidence

    def get_nodes_info(self, headers, leaves_only=False):
        """Generator that yields the nodes information in a row format

        """
        if self.boosting:
            raise AttributeError("This method is not available for boosting"
                                 " models.")
        return self.tree.get_nodes_info(headers, leaves_only=leaves_only)

    def tree_csv(self, file_name=None, leaves_only=False):
        """Outputs the node structure to a CSV file or array

        """
        if self.boosting:
            raise AttributeError("This method is not available for boosting"
                                 " models.")
        headers_names = []
        if self.regression:
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
                    writer.writerow([item if not isinstance(item, str)
                                     else item.encode("utf-8")
                                     for item in row])
        else:
            rows = []
            rows.append(headers_names)
            for row in nodes_generator:
                rows.append(row)
            return rows
