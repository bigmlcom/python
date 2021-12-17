# -*- coding: utf-8 -*-
#
# Copyright 2013-2021 BigML
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
import locale

from functools import cmp_to_key

import bigml.predict_utils.classification as c
import bigml.predict_utils.regression as r
import bigml.predict_utils.boosting as b

from bigml.predict_utils.common import FIELD_OFFSET, extract_distribution
from bigml.exceptions import NoRootDecisionTree

from bigml.api import FINISHED, STATUSES
from bigml.api import get_status, get_api_connection, get_model_id
from bigml.util import find_locale, cast, use_cache, load
from bigml.util import DEFAULT_LOCALE, PRECISION, NUMERIC
from bigml.constants import LAST_PREDICTION, PROPORTIONAL
from bigml.basemodel import BaseModel, get_resource_dict
from bigml.multivote import ws_confidence
from bigml.prediction import Prediction


LOGGER = logging.getLogger('BigML')

OPERATING_POINT_KINDS = ["probability", "confidence"]

DICTIONARY = "dict"

OUT_FORMATS = [DICTIONARY, "list"]


BOOSTING = "boosting"
REGRESSION = "regression"
CLASSIFICATION = "classification"

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
    "day-of-month": "lambda x: int(locale.atof(x))"}

PYTHON_FUNC = {numtype: eval(function)
               for numtype, function in PYTHON_CONV.items()}


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


def parse_operating_point(operating_point, operating_kinds, class_names):
    """Checks the operating point contents and extracts the three defined
    variables

    """
    if "kind" not in operating_point:
        raise ValueError("Failed to find the kind of operating point.")
    if operating_point["kind"] not in operating_kinds:
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
    positive_class = operating_point["positive_class"]
    if positive_class not in class_names:
        raise ValueError("The positive class must be one of the"
                         "objective field classes: %s." %
                         ", ".join(class_names))
    kind = operating_point["kind"]
    threshold = operating_point["threshold"]

    return kind, threshold, positive_class


def to_prediction(model, value_as_string, data_locale=DEFAULT_LOCALE):
    """Given a prediction string, returns its value in the required type

    """
    if not isinstance(value_as_string, str):
        value_as_string = str(value_as_string, "utf-8")

    objective_id = model.objective_id
    if model.fields[objective_id]['optype'] == NUMERIC:
        if data_locale is None:
            data_locale = model.locale
        find_locale(data_locale)
        datatype = model.fields[objective_id]['datatype']
        cast_function = PYTHON_FUNC.get(datatype, None)
        if cast_function is not None:
            return cast_function(value_as_string)
    return value_as_string


def average_confidence(model):
    """Average for the confidence of the predictions resulting from
       running the training data through the model

    """
    if model.boosting:
        raise AttributeError("This method is not available for boosting"
                             " models.")
    total = 0.0
    cumulative_confidence = 0
    groups = model.group_prediction()
    for _, predictions in list(groups.items()):
        for _, count, confidence in predictions['details']:
            cumulative_confidence += count * confidence
            total += count
    return float('nan') if total == 0.0 else cumulative_confidence


def tree_predict(tree, tree_type, weighted, fields,
                 input_data, missing_strategy=LAST_PREDICTION):
    """Makes a prediction based on a number of field values.

    The input fields must be keyed by Id. There are two possible
    strategies to predict when the value for the splitting field
    is missing:
        0 - LAST_PREDICTION: the last issued prediction is returned.
        1 - PROPORTIONAL: as we cannot choose between the two branches
            in the tree that stem from this split, we consider both. The
            algorithm goes on until the final leaves are reached and
            all their predictions are used to decide the final prediction.
    """

    if missing_strategy == PROPORTIONAL:
        if tree_type == REGRESSION:
            return r.regression_proportional_predict(tree, weighted, fields,
                                                     input_data)

        if tree_type == CLASSIFICATION:
            # classification
            return c.classification_proportional_predict(tree, weighted,
                                                         fields,
                                                         input_data)
    # boosting
        return b.boosting_proportional_predict(tree, fields, input_data)

    if tree_type == REGRESSION:
        # last prediction missing strategy
        return r.regression_last_predict(tree, weighted, fields, input_data)
    if tree_type == CLASSIFICATION:
        return c.classification_last_predict(tree, weighted, fields,
                                             input_data)
    # boosting
    return b.boosting_last_predict(tree, fields, input_data)


def laplacian_term(root_dist, weighted):
    """Correction term based on the training dataset distribution

    """

    if weighted:
        category_map = {category[0]: 0.0 for category in root_dist}
    else:
        total = float(sum([category[1] for category in root_dist]))
        category_map = {category[0]: category[1] / total
                        for category in root_dist}
    return category_map


class Model(BaseModel):
    """ A lightweight wrapper around a Tree model.

    Uses a BigML remote model to build a local version that can be used
    to generate predictions locally.

    """

    def __init__(self, model, api=None, fields=None, cache_get=None):
        """The Model constructor can be given as first argument:
            - a model structure
            - a model id
            - a path to a JSON file containing a model structure

        """

        if use_cache(cache_get):
            # using a cache to store the model attributes
            self.__dict__ = load(get_model_id(model), cache_get)
            return

        self.resource_id = None
        self.ids_map = {}
        self.terms = {}
        self.regression = False
        self.boosting = None
        self.class_names = None
        self.default_numeric_value = None
        api = get_api_connection(api)
        # retrieving model information from
        self.resource_id, model = get_resource_dict( \
            model, "model", api=api, no_check_fields=fields is not None)

        if 'object' in model and isinstance(model['object'], dict):
            model = model['object']

        if 'model' in model and isinstance(model['model'], dict):
            status = get_status(model)
            if 'code' in status and status['code'] == FINISHED:
                # fill boosting info before creating modelfields
                if model.get("boosted_ensemble"):
                    self.boosting = model.get('boosting', False)
                if self.boosting == {}:
                    self.boosting = False

                self.default_numeric_value = model.get('default_numeric_value')
                self.input_fields = model["input_fields"]
                BaseModel.__init__(self, model, api=api, fields=fields)

                try:
                    root = model['model']['root']
                except KeyError:
                    raise NoRootDecisionTree("Model %s has no `root` element"
                        " and cannot be used"
                        % self.resource_id)
                self.weighted = "weighted_objective_summary" in root

                terms = {}

                if self.boosting:
                    # build boosted tree
                    self.tree = b.build_boosting_tree( \
                        model['model']['root'], terms=terms)
                elif self.regression:
                    self.root_distribution = model['model'][ \
                        'distribution']['training']
                    # build regression tree
                    self.tree = r.build_regression_tree(root, \
                        distribution=self.root_distribution, \
                        weighted=self.weighted, terms=terms)
                else:
                    # build classification tree
                    self.root_distribution = model['model'][\
                        'distribution']['training']
                    self.laplacian_term = laplacian_term( \
                        extract_distribution(self.root_distribution)[1],
                        self.weighted)
                    self.tree = c.build_classification_tree( \
                        model['model']['root'], \
                        distribution=self.root_distribution, \
                        weighted=self.weighted, terms=terms)
                    self.class_names = sorted( \
                        [category[0] for category in \
                        self.root_distribution["categories"]])
                    self.objective_categories = [category for \
                        category, _ in self.fields[self.objective_id][ \
                       "summary"]["categories"]]

                if not hasattr(self, "tag_clouds"):
                    self.tag_clouds = {}
                if not hasattr(self, "items"):
                    self.items = {}

                if terms:
                    # only the terms used in the model are kept
                    for field_id in terms:
                        if self.tag_clouds.get(field_id):
                            self.tag_clouds[field_id] = terms[field_id]
                        elif self.items.get(field_id):
                            self.items[field_id] = terms[field_id]

                if self.boosting:
                    self.tree_type = BOOSTING
                    self.offsets = b.OFFSETS
                elif self.regression:
                    self.tree_type = REGRESSION
                    self.offsets = r.OFFSETS[str(self.weighted)]
                else:
                    self.tree_type = CLASSIFICATION
                    self.offsets = c.OFFSETS[str(self.weighted)]

            else:
                raise Exception("Cannot create the Model instance."
                                " Only correctly finished models can be"
                                " used. The model status is currently:"
                                " %s\n" % STATUSES[status['code']])
        else:
            raise Exception("Cannot create the Model instance. Could not"
                            " find the 'model' key in the resource:"
                            "\n\n%s" % model)

    def _to_output(self, output_map, compact, value_key):
        if compact:
            return [round(output_map.get(name, 0.0), PRECISION)
                    for name in self.class_names]
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

        if self.boosting:
            raise AttributeError("This method is available for non-boosting"
                                 " models only.")

        root_dist = self.root_distribution
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

    def _probabilities(self, distribution):
        """Computes the probability of a distribution using a Laplacian
        correction.

        """
        total = 0 if self.weighted else 1

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
        norm_input_data = self.filter_input_data( \
            input_data,
            add_unused_fields=full)
        if full:
            norm_input_data, unused_fields = norm_input_data

        # Strips affixes for numeric values and casts to the final field type
        cast(norm_input_data, self.fields)

        full_prediction = self._predict( \
            norm_input_data, missing_strategy=missing_strategy,
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

        prediction = tree_predict( \
            self.tree, self.tree_type, self.weighted, self.fields,
            input_data, missing_strategy=missing_strategy)

        if self.boosting and missing_strategy == PROPORTIONAL:
            # output has to be recomputed and comes in a different format
            g_sum, h_sum, population, path = prediction
            prediction = Prediction( \
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
                 prediction.children[0][FIELD_OFFSET])
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
