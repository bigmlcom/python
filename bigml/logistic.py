# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015-2016 BigML
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
import re
import copy

from bigml.api import FINISHED
from bigml.api import (BigML, get_logistic_regression_id, get_status)
from bigml.util import cast
from bigml.basemodel import retrieve_resource, extract_objective
from bigml.basemodel import ONLY_MODEL
from bigml.model import STORAGE
from bigml.predicate import TM_TOKENS, TM_FULL_TERM, TM_ALL
from bigml.modelfields import ModelFields
from bigml.cluster import parse_terms, parse_items


LOGGER = logging.getLogger('BigML')

EXPANSION_ATTRIBUTES = {"categorical": "categories", "text": "tag_cloud",
                        "items": "items"}


def get_unique_terms(terms, term_forms, tag_cloud):
    """Extracts the unique terms that occur in one of the alternative forms in
       term_forms or in the tag cloud.

    """

    extend_forms = {}
    for term, forms in term_forms.items():
        for form in forms:
            extend_forms[form] = term
        extend_forms[term] = term
    terms_set = {}
    for term in terms:
        if term in tag_cloud:
            if term not in terms_set:
                terms_set[term] = 0
            terms_set[term] += 1
        elif term in extend_forms:
            term = extend_forms[term]
            if term not in terms_set:
                terms_set[term] = 0
            terms_set[term] += 1
    return terms_set.items()


class LogisticRegression(ModelFields):
    """ A lightweight wrapper around a logistic regression model.

    Uses a BigML remote logistic regression model to build a local version
    that can be used to generate predictions locally.

    """

    def __init__(self, logistic_regression, api=None):

        self.resource_id = None
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
        old_coefficients = False
        if not (isinstance(logistic_regression, dict)
                and 'resource' in logistic_regression and
                logistic_regression['resource'] is not None):
            if api is None:
                api = BigML(storage=STORAGE)
            self.resource_id = get_logistic_regression_id(logistic_regression)
            if self.resource_id is None:
                raise Exception(
                    api.error_message(logistic_regression,
                                      resource_type='logistic_regression',
                                      method='get'))
            query_string = ONLY_MODEL
            logistic_regression = retrieve_resource(
                api, self.resource_id, query_string=query_string)
        else:
            self.resource_id = get_logistic_regression_id(logistic_regression)

        if 'object' in logistic_regression and \
            isinstance(logistic_regression['object'], dict):
            logistic_regression = logistic_regression['object']
        try:
            self.input_fields = logistic_regression.get("input_fields", [])
            self.dataset_field_types = logistic_regression.get(
                "dataset_field_types", {})
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
                        sorted(self.fields.items(),
                               key=lambda x: x[1].get("column_number"))]
                self.coefficients.update(logistic_regression_info.get( \
                    'coefficients', []))
                if (not isinstance(self.coefficients.values()[0][0], list)):
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
                for field_id, field in fields.items():
                    if field['optype'] == 'text':
                        self.term_forms[field_id] = {}
                        self.term_forms[field_id].update(
                            field['summary']['term_forms'])
                        self.tag_clouds[field_id] = []
                        self.tag_clouds[field_id] = [tag for [tag, _] in field[
                            'summary']['tag_cloud']]
                        self.term_analysis[field_id] = {}
                        self.term_analysis[field_id].update(
                            field['term_analysis'])
                    if field['optype'] == 'items':
                        self.items[field_id] = []
                        self.items[field_id] = [item for item, _ in \
                            field['summary']['items']]
                        self.item_analysis[field_id] = {}
                        self.item_analysis[field_id].update(
                            field['item_analysis'])
                    if field['optype'] == 'categorical':
                        self.categories[field_id] = [category for \
                            [category, _] in field['summary']['categories']]
                    if self.missing_numerics and field['optype'] == 'numeric':
                        self.numeric_fields[field_id] = True
                ModelFields.__init__(
                    self, fields,
                    objective_id=objective_id)
                self.field_codings = logistic_regression_info.get( \
                  'field_codings', {});
                self.format_field_codings()
                for field_id in self.field_codings:
                    if field_id not in fields and \
                            field_id in self.inverted_fields:
                        self.field_codings.update( \
                            {self.inverted_fields[field_id]: \
                             self.field_codings[field_id]})
                        del self.field_codings[field_id]
                if old_coefficients:
                  self.map_coefficients()
            else:
                raise Exception("The logistic regression isn't finished yet")
        else:
            raise Exception("Cannot create the LogisticRegression instance."
                            " Could not find the 'logistic_regression' key"
                            " in the resource:\n\n%s" %
                            logistic_regression)

    def predict(self, input_data, by_name=True):
        """Returns the class prediction and the probability distribution

        """
        # Checks and cleans input_data leaving the fields used in the model
        input_data = self.filter_input_data(input_data, by_name=by_name)

        # In case that missing_numerics is False, checks that all numeric
        # fields are present in input data.
        if not self.missing_numerics:
            for field_id, field in self.fields.items():
                if (not field['optype'] in OPTIONAL_FIELDS and
                        not field_id in input_data):
                    raise Exception("Failed to predict. Input"
                                    " data must contain values for all numeric"
                                    " fields to get a logistic regression"
                                    " prediction.")
        # Strips affixes for numeric values and casts to the final field type
        cast(input_data, self.fields)

        if self.balance_fields:
            for field in input_data:
                if self.fields[field]['optype'] == 'numeric':
                    mean = self.fields[field]['summary']['mean']
                    stddev = self.fields[field]['summary'][ \
                        'standard_deviation']
                    input_data[field] = (input_data[field] - mean) / stddev

        # Compute text and categorical field expansion
        unique_terms = self.get_unique_terms(input_data)

        probabilities = {}
        total = 0
        for category in self.coefficients.keys():
            probability = self.category_probability( \
                input_data, unique_terms, category)
            order = self.categories[self.objective_id].index(category)
            probabilities[category] = {"category": category,
                                       "probability": probability,
                                       "order": order}
            total += probabilities[category]["probability"]
        for category in probabilities.keys():
            probabilities[category]["probability"] /= total
        predictions = sorted(probabilities.items(),
                             key=lambda x: (x[1]["probability"],
                                            - x[1]["order"]), reverse=True)
        for prediction, probability in predictions:
          del probability['order']
        prediction, probability = predictions[0]
        return {
            "prediction": prediction,
            "probability": probability["probability"],
            "distribution": [{"category": category,
                              "probability": probability["probability"]}
                             for category, probability in predictions]}

    def category_probability(self, numeric_inputs, unique_terms, category):
        """Computes the probability for a concrete category

        """
        probability = 0
        norm2 = 0
        # the bias term is the last in the coefficients list
        bias = self.coefficients[category][\
            len(self.coefficients[category]) - 1][0]

        # numeric input data
        for field_id in numeric_inputs:
            coefficients = self.get_coefficients(category, field_id)
            probability += coefficients[0] * numeric_inputs[field_id]
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
                                self.field_codings[field_id].keys()[0] == \
                                "dummy"):
                            index = self.categories[field_id].index(term)
                        elif field_id in self.categories:
                            one_hot = False
                            index = self.categories[field_id].index(term)
                            coeff_index = 0
                            for contribution in \
                                    self.field_codings[field_id].values()[0]:
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
        for field_id in self.numeric_fields:
            if field_id in self.input_fields:
                coefficients = self.get_coefficients(category, field_id)
                if field_id not in numeric_inputs:
                    probability += coefficients[1]
                    norm2 += 1
        for field_id in self.tag_clouds:
            if field_id in self.input_fields:
                coefficients = self.get_coefficients(category, field_id)
                if field_id not in unique_terms or not unique_terms[field_id]:
                    norm2 += 1
                    probability += coefficients[ \
                        len(self.tag_clouds[field_id])]
        for field_id in self.items:
            if field_id in self.input_fields:
                coefficients = self.get_coefficients(category, field_id)
                if field_id not in unique_terms or not unique_terms[field_id]:
                    norm2 += 1
                    probability += coefficients[len(self.items[field_id])]
        for field_id in self.categories:
            if field_id in self.input_fields:
                coefficients = self.get_coefficients(category, field_id)
                if field_id != self.objective_id and field_id \
                        not in unique_terms:
                    norm2 += 1
                    if field_id not in self.field_codings or \
                            self.field_codings[field_id].keys()[0] == "dummy":
                        probability += coefficients[ \
                            len(self.categories[field_id])]
                    else:
                        """ codings are given as arrays of coefficients. The
                        last one is for missings and the previous ones are
                        one per category as found in summary
                        """
                        coeff_index = 0
                        for contribution in \
                                self.field_codings[field_id].values()[0]:
                            probability += coefficients[coeff_index] * \
                                contribution[-1]
                            coeff_index += 1

        probability += bias
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
        return probability

    def get_unique_terms(self, input_data):
        """Parses the input data to find the list of unique terms in the
           tag cloud

        """
        unique_terms = {}
        for field_id in self.term_forms:
            if field_id in input_data:
                input_data_field = input_data.get(field_id, '')
                if isinstance(input_data_field, basestring):
                    case_sensitive = self.term_analysis[field_id].get(
                        'case_sensitive', True)
                    token_mode = self.term_analysis[field_id].get(
                        'token_mode', 'all')
                    if token_mode != TM_FULL_TERM:
                        terms = parse_terms(input_data_field,
                                            case_sensitive=case_sensitive)
                    else:
                        terms = []
                    full_term = input_data_field if case_sensitive \
                        else input_data_field.lower()
                    # We add full_term if needed. Note that when there's
                    # only one term in the input_data, full_term and term are
                    # equal. Then full_term will not be added to avoid
                    # duplicated counters for the term.
                    if token_mode == TM_FULL_TERM or \
                            (token_mode == TM_ALL and terms[0] != full_term):
                        terms.append(full_term)
                    unique_terms[field_id] = get_unique_terms(
                        terms, self.term_forms[field_id],
                        self.tag_clouds.get(field_id, []))
                else:
                    unique_terms[field_id] = [(input_data_field, 1)]
                del input_data[field_id]
        # the same for items fields
        for field_id in self.item_analysis:
            if field_id in input_data:
                input_data_field = input_data.get(field_id, '')
                if isinstance(input_data_field, basestring):
                    # parsing the items in input_data
                    separator = self.item_analysis[field_id].get(
                        'separator', ' ')
                    regexp = self.item_analysis[field_id].get(
                        'separator_regexp')
                    if regexp is None:
                        regexp = ur'%s' % re.escape(separator)
                    terms = parse_items(input_data_field, regexp)
                    unique_terms[field_id] = get_unique_terms(
                        terms, {},
                        self.items.get(field_id, []))
                else:
                    unique_terms[field_id] = [(input_data_field, 1)]
                del input_data[field_id]
        for field_id in self.categories:
            if field_id in input_data:
                input_data_field = input_data.get(field_id, '')
                unique_terms[field_id] = [(input_data_field, 1)]
                del input_data[field_id]
        return unique_terms

    def map_coefficients(self):
        """ Maps each field to the corresponding coefficients subarray

        """
        field_ids = [ \
            field_id for field_id in self.input_fields
            if field_id != self.objective_id]
        shift = 0
        for field_id in field_ids:
            optype = self.fields[field_id]['optype']
            if optype in EXPANSION_ATTRIBUTES.keys():
                # text and items fields have one coefficient per
                # text plus a missing terms coefficient plus a bias
                # coefficient
                # categorical fields too, unless they use a non-default
                # field coding.
                if optype != 'categorical' or \
                        not field_id in self.field_codings or \
                        self.field_codings[field_id].keys()[0] ==  "dummy":
                    length = len(self.fields[field_id]['summary'][ \
                        EXPANSION_ATTRIBUTES[optype]])
                    # missing coefficient
                    length += 1
                else:
                    length = len(self.field_codings[field_id].values()[0])
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
            for index, element in enumerate(field_codings):
                field_id = element['field']
                if element["coding"] == "dummy":
                    self.field_codings[field_id] = {\
                        element["coding"]: element['dummy_class']}
                else:
                    self.field_codings[field_id] = {\
                        element["coding"]: element['coefficients']}
