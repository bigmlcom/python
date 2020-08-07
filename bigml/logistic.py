# -*- coding: utf-8 -*-
#
# Copyright 2015-2020 BigML
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

"""A local Predictive Logistic Regression.

This module defines a Logistic Regression to make predictions locally or
embedded into your application without needing to send requests to
BigML.io.

This module cannot only save you a few credits, but also enormously
reduce the latency for each prediction and let you use your logistic
regressions offline.

Example usage (assuming that you have previously set up the BIGML_USERNAME
and BIGML_API_KEY environment variables and that you own the
logisticregression/id below):

from bigml.api import BigML
from bigml.logistic import LogisticRegression

api = BigML()

logistic_regression = LogisticRegression(
    'logisticregression/5026965515526876630001b2')
logistic_regression.predict({"petal length": 3, "petal width": 1,
                             "sepal length": 1, "sepal width": 0.5})

"""
import logging
import math
import copy
import json

from functools import cmp_to_key

from bigml.api import FINISHED
from bigml.api import get_status, get_api_connection
from bigml.util import cast, check_no_missing_numerics, PRECISION, NUMERIC
from bigml.basemodel import get_resource_dict, extract_objective
from bigml.model import parse_operating_point, sort_categories
from bigml.modelfields import ModelFields

LOGGER = logging.getLogger('BigML')

EXPANSION_ATTRIBUTES = {"categorical": "categories", "text": "tag_cloud",
                        "items": "items"}


def balance_input(input_data, fields):
    """Balancing the values in the input_data using the corresponding
    field scales

    """

    for field in input_data:
        if fields[field]['optype'] == NUMERIC:
            mean = fields[field]['summary'].get('mean', 0)
            stddev = fields[field]['summary'].get( \
                'standard_deviation', 0)
            if mean is None:
                mean = 0
            if stddev is None:
                stddev = 0
            # if stddev is not positive, we only substract the mean
            input_data[field] = input_data[field] - mean if \
                stddev <= 0 else (input_data[field] - mean) / stddev


class LogisticRegression(ModelFields):
    """ A lightweight wrapper around a logistic regression model.

    Uses a BigML remote logistic regression model to build a local version
    that can be used to generate predictions locally.

    """

    def __init__(self, logistic_regression, api=None):

        self.resource_id = None
        self.class_names = None
        self.input_fields = []
        self.term_forms = {}
        self.tag_clouds = {}
        self.term_analysis = {}
        self.items = {}
        self.item_analysis = {}
        self.categories = {}
        self.coefficients = {}
        self.data_field_types = {}
        self.field_codings = {}
        self.numeric_fields = {}
        self.bias = None
        self.missing_numerics = None
        self.c = None
        self.eps = None
        self.lr_normalize = None
        self.balance_fields = None
        self.regularization = None
        self.api = get_api_connection(api)

        old_coefficients = False

        self.resource_id, logistic_regression = get_resource_dict( \
            logistic_regression, "logisticregression", api=self.api)

        if 'object' in logistic_regression and \
            isinstance(logistic_regression['object'], dict):
            logistic_regression = logistic_regression['object']
        try:
            self.input_fields = logistic_regression.get("input_fields", [])
            self.dataset_field_types = logistic_regression.get(
                "dataset_field_types", {})
            self.weight_field = logistic_regression.get("weight_field")
            objective_field = logistic_regression['objective_fields'] if \
                logistic_regression['objective_fields'] else \
                logistic_regression['objective_field']
        except KeyError:
            raise ValueError("Failed to find the logistic regression expected "
                             "JSON structure. Check your arguments.")
        if 'logistic_regression' in logistic_regression and \
            isinstance(logistic_regression['logistic_regression'], dict):
            status = get_status(logistic_regression)
            if 'code' in status and status['code'] == FINISHED:
                logistic_regression_info = logistic_regression[ \
                    'logistic_regression']
                fields = logistic_regression_info.get('fields', {})

                if not self.input_fields:
                    self.input_fields = [ \
                        field_id for field_id, _ in
                        sorted(list(fields.items()),
                               key=lambda x: x[1].get("column_number"))]
                self.coefficients.update(logistic_regression_info.get( \
                    'coefficients', []))
                if not isinstance(list(self.coefficients.values())[0][0], list):
                    old_coefficients = True
                self.bias = logistic_regression_info.get('bias', True)
                self.c = logistic_regression_info.get('c')
                self.eps = logistic_regression_info.get('eps')
                self.lr_normalize = logistic_regression_info.get('normalize')
                self.balance_fields = logistic_regression_info.get( \
                    'balance_fields')
                self.regularization = logistic_regression_info.get( \
                    'regularization')
                self.field_codings = logistic_regression_info.get( \
                     'field_codings', {})
                # old models have no such attribute, so we set it to False in
                # this case
                self.missing_numerics = logistic_regression_info.get( \
                    'missing_numerics', False)
                objective_id = extract_objective(objective_field)
                missing_tokens = logistic_regression_info.get("missing_tokens")
                ModelFields.__init__(
                    self, fields,
                    objective_id=objective_id, terms=True, categories=True,
                    numerics=True, missing_tokens=missing_tokens)
                self.field_codings = logistic_regression_info.get( \
                  'field_codings', {})
                self.format_field_codings()
                for field_id in self.field_codings:
                    if field_id not in self.fields and \
                            field_id in self.inverted_fields:
                        self.field_codings.update( \
                            {self.inverted_fields[field_id]: \
                             self.field_codings[field_id]})
                        del self.field_codings[field_id]
                if old_coefficients:
                    self.map_coefficients()
                categories = self.fields[self.objective_id].get( \
                    "summary", {}).get('categories')
                if len(list(self.coefficients.keys())) > len(categories):
                    self.class_names = [""]
                else:
                    self.class_names = []
                self.class_names.extend(sorted([category[0]
                                                for category in categories]))
                # order matters
                self.objective_categories = [category[0]
                                             for category in categories]
            else:
                raise Exception("The logistic regression isn't finished yet")
        else:
            raise Exception("Cannot create the LogisticRegression instance."
                            " Could not find the 'logistic_regression' key"
                            " in the resource:\n\n%s" %
                            logistic_regression)

    def _sort_predictions(self, a, b, criteria):
        """Sorts the categories in the predicted node according to the
        given criteria

        """
        if a[criteria] == b[criteria]:
            return sort_categories(a, b, self.objective_categories)
        return 1 if b[criteria] > a[criteria] else - 1

    def predict_probability(self, input_data, compact=False):
        """Predicts a probability for each possible output class,
        based on input values.  The input fields must be a dictionary
        keyed by field name or field ID.

        :param input_data: Input data to be predicted
        :param compact: If False, prediction is returned as a list of maps, one
                        per class, with the keys "prediction" and "probability"
                        mapped to the name of the class and it's probability,
                        respectively.  If True, returns a list of probabilities
                        ordered by the sorted order of the class names.
        """
        distribution = self.predict(input_data, full=True)['distribution']
        distribution.sort(key=lambda x: x['category'])

        if compact:
            return [category['probability'] for category in distribution]
        else:
            return distribution

    def predict_operating(self, input_data,
                          operating_point=None):
        """Computes the prediction based on a user-given operating point.

        """

        kind, threshold, positive_class = parse_operating_point( \
            operating_point, ["probability"], self.class_names)
        predictions = self.predict_probability(input_data, False)
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

    def predict_operating_kind(self, input_data,
                               operating_kind=None):
        """Computes the prediction based on a user-given operating kind.

        """
        kind = operating_kind.lower()
        if kind == "probability":
            predictions = self.predict_probability(input_data,
                                                   False)
        else:
            raise ValueError("Only probability is allowed as operating kind"
                             " for logistic regressions.")
        predictions.sort( \
            key=cmp_to_key( \
            lambda a, b: self._sort_predictions(a, b, kind)))
        prediction = predictions[0]
        prediction["prediction"] = prediction["category"]
        del prediction["category"]
        return prediction

    def predict(self, input_data,
                operating_point=None, operating_kind=None,
                full=False):
        """Returns the class prediction and the probability distribution

        input_data: Input data to be predicted
        operating_point: In classification models, this is the point of the
                         ROC curve where the model will be used at. The
                         operating point can be defined in terms of:
                         - the positive_class, the class that is important to
                           predict accurately
                         - the probability_threshold,
                           the probability that is stablished
                           as minimum for the positive_class to be predicted.
                         The operating_point is then defined as a map with
                         two attributes, e.g.:
                           {"positive_class": "Iris-setosa",
                            "probability_threshold": 0.5}
        operating_kind: "probability". Sets the
                        property that decides the prediction. Used only if
                        no operating_point is used
        full: Boolean that controls whether to include the prediction's
              attributes. By default, only the prediction is produced. If set
              to True, the rest of available information is added in a
              dictionary format. The dictionary keys can be:
                  - prediction: the prediction value
                  - probability: prediction's probability
                  - distribution: distribution of probabilities for each
                                  of the objective field classes
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

        # When operating_point is used, we need the probabilities
        # of all possible classes to decide, so se use
        # the `predict_probability` method
        if operating_point:
            return self.predict_operating( \
                input_data, operating_point=operating_point)
        if operating_kind:
            return self.predict_operating_kind( \
                input_data, operating_kind=operating_kind)

        # In case that missing_numerics is False, checks that all numeric
        # fields are present in input data.
        if not self.missing_numerics:
            check_no_missing_numerics(input_data, self.model_fields,
                                      self.weight_field)

        if self.balance_fields:
            balance_input(input_data, self.fields)

        # Computes text and categorical field expansion
        unique_terms = self.get_unique_terms(input_data)

        probabilities = {}
        total = 0
        # Computes the contributions for each category
        for category in self.coefficients:
            probability = self.category_probability( \
                input_data, unique_terms, category)
            try:
                order = self.categories[self.objective_id].index(category)
            except ValueError:
                if category == '':
                    order = len(self.categories[self.objective_id])
            probabilities[category] = {"category": category,
                                       "probability": probability,
                                       "order": order}
            total += probabilities[category]["probability"]
        # Normalizes the contributions to get a probability
        for category in probabilities:
            probabilities[category]["probability"] /= total
            probabilities[category]["probability"] = round( \
                probabilities[category]["probability"], PRECISION)

        # Chooses the most probable category as prediction
        predictions = sorted(list(probabilities.items()),
                             key=lambda x: (x[1]["probability"],
                                            - x[1]["order"]), reverse=True)
        for prediction, probability in predictions:
            del probability['order']
        prediction, probability = predictions[0]

        result = {
            "prediction": prediction,
            "probability": probability["probability"],
            "distribution": [{"category": category,
                              "probability": probability["probability"]}
                             for category, probability in predictions]}

        if full:
            result.update({'unused_fields': unused_fields})
        else:
            result = result["prediction"]

        return result

    def category_probability(self, numeric_inputs, unique_terms, category):
        """Computes the probability for a concrete category

        """
        probability = 0
        norm2 = 0

        # numeric input data
        for field_id in numeric_inputs:
            coefficients = self.get_coefficients(category, field_id)
            probability += coefficients[0] * numeric_inputs[field_id]
            if self.lr_normalize:
                norm2 += math.pow(numeric_inputs[field_id], 2)

        # text, items and categories
        for field_id in unique_terms:
            if field_id in self.input_fields:
                coefficients = self.get_coefficients(category, field_id)
                for term, occurrences in unique_terms[field_id]:
                    try:
                        one_hot = True
                        if field_id in self.tag_clouds:
                            index = self.tag_clouds[field_id].index(term)
                        elif field_id in self.items:
                            index = self.items[field_id].index(term)
                        elif field_id in self.categories and ( \
                                not field_id in self.field_codings or \
                                list(self.field_codings[field_id].keys())[0] == \
                                "dummy"):
                            index = self.categories[field_id].index(term)
                        elif field_id in self.categories:
                            one_hot = False
                            index = self.categories[field_id].index(term)
                            coeff_index = 0
                            for contribution in \
                                    list(self.field_codings[field_id].values())[0]:
                                probability += \
                                    coefficients[coeff_index] * \
                                    contribution[index] * occurrences
                                coeff_index += 1
                        if one_hot:
                            probability += coefficients[index] * \
                                occurrences
                        norm2 += math.pow(occurrences, 2)
                    except ValueError:
                        pass

        # missings
        for field_id in self.input_fields:
            contribution = False
            coefficients = self.get_coefficients(category, field_id)
            if field_id in self.numeric_fields and \
                    field_id not in numeric_inputs:
                probability += coefficients[1]
                contribution = True
            elif field_id in self.tag_clouds and (field_id not in \
                    unique_terms \
                    or not unique_terms[field_id]):
                probability += coefficients[ \
                    len(self.tag_clouds[field_id])]
                contribution = True
            elif field_id in self.items and (field_id not in \
                    unique_terms \
                    or not unique_terms[field_id]):
                probability += coefficients[len(self.items[field_id])]
                contribution = True
            elif field_id in self.categories and \
                    field_id != self.objective_id and \
                    field_id not in unique_terms:
                if field_id not in self.field_codings or \
                        list(self.field_codings[field_id].keys())[0] == "dummy":
                    probability += coefficients[ \
                        len(self.categories[field_id])]
                else:
                    """ codings are given as arrays of coefficients. The
                    last one is for missings and the previous ones are
                    one per category as found in summary
                    """
                    coeff_index = 0
                    for contribution in \
                            list(self.field_codings[field_id].values())[0]:
                        probability += coefficients[coeff_index] * \
                            contribution[-1]
                        coeff_index += 1
                contribution = True
            if contribution and self.lr_normalize:
                norm2 += 1

        # the bias term is the last in the coefficients list
        probability += self.coefficients[category][\
            len(self.coefficients[category]) - 1][0]

        if self.bias:
            norm2 += 1
        if self.lr_normalize:
            try:
                probability /= math.sqrt(norm2)
            except ZeroDivisionError:
                # this should never happen
                probability = float('NaN')

        try:
            probability = 1 / (1 + math.exp(-probability))
        except OverflowError:
            probability = 0 if probability < 0 else 1
        # truncate probability to 5 digits, as in the backend
        probability = round(probability, 5)
        return probability

    def map_coefficients(self):
        """ Maps each field to the corresponding coefficients subarray

        """
        field_ids = [ \
            field_id for field_id in self.input_fields
            if field_id != self.objective_id]
        shift = 0
        for field_id in field_ids:
            optype = self.fields[field_id]['optype']
            if optype in list(EXPANSION_ATTRIBUTES.keys()):
                # text and items fields have one coefficient per
                # text plus a missing terms coefficient plus a bias
                # coefficient
                # categorical fields too, unless they use a non-default
                # field coding.
                if optype != 'categorical' or \
                        not field_id in self.field_codings or \
                        list(self.field_codings[field_id].keys())[0] == "dummy":
                    length = len(self.fields[field_id]['summary'][ \
                        EXPANSION_ATTRIBUTES[optype]])
                    # missing coefficient
                    length += 1
                else:
                    length = len(list(self.field_codings[field_id].values())[0])
            else:
                # numeric fields have one coefficient and an additional one
                # if self.missing_numerics is True
                length = 2 if self.missing_numerics else 1
            self.fields[field_id]['coefficients_shift'] = shift
            self.fields[field_id]['coefficients_length'] = length
            shift += length
        self.group_coefficients()

    def get_coefficients(self, category, field_id):
        """ Returns the set of coefficients for the given category and fieldIds

        """
        coeff_index = self.input_fields.index(field_id)
        return self.coefficients[category][coeff_index]

    def group_coefficients(self):
        """ Groups the coefficients of the flat array in old formats to the
        grouped array, as used in the current notation

        """
        coefficients = copy.deepcopy(self.coefficients)
        self.flat_coefficients = coefficients
        for category in coefficients:
            self.coefficients[category] = []
            for field_id in self.input_fields:
                shift = self.fields[field_id]['coefficients_shift']
                length = self.fields[field_id]['coefficients_length']
                coefficients_group = \
                    coefficients[category][shift : length + shift]
                self.coefficients[category].append(coefficients_group)
            self.coefficients[category].append( \
                [coefficients[category][len(coefficients[category]) - 1]])

    def format_field_codings(self):
        """ Changes the field codings format to the dict notation

        """
        if isinstance(self.field_codings, list):
            self.field_codings_list = self.field_codings[:]
            field_codings = self.field_codings[:]
            self.field_codings = {}
            for element in field_codings:
                field_id = element['field']
                if element["coding"] == "dummy":
                    self.field_codings[field_id] = {\
                        element["coding"]: element['dummy_class']}
                else:
                    self.field_codings[field_id] = {\
                        element["coding"]: element['coefficients']}
