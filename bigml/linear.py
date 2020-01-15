# -*- coding: utf-8 -*-
#!/usr/bin/env python
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

"""A local Predictive Linear Regression.

This module defines a Linear Regression to make predictions locally or
embedded into your application without needing to send requests to
BigML.io.

This module cannot only save you a few credits, but also enormously
reduce the latency for each prediction and let you use your linear
regressions offline.

Example usage (assuming that you have previously set up the BIGML_USERNAME
and BIGML_API_KEY environment variables and that you own the
linearregression/id below):

from bigml.api import BigML
from bigml.linear import LinearRegression

api = BigML()

linear_regression = LinearRegression(
    'linearregression/5026965515526876630001b2')
linear_regression.predict({"petal length": 3, "petal width": 1,
                           "sepal length": 1})

"""
import logging
import math
import copy
import json

try:
    import numpy as np
    from scipy.stats import t as student_t
    STATS = True
except ImportError:
    STATS = False

from functools import cmp_to_key

from bigml.api import FINISHED
from bigml.api import get_status, get_api_connection
from bigml.util import cast, check_no_training_missings, PRECISION, NUMERIC, \
    flatten
from bigml.basemodel import get_resource_dict, extract_objective
from bigml.model import parse_operating_point, sort_categories
from bigml.modelfields import ModelFields

try:
    from bigml.laminar.numpy_ops import dot
except ImportError:
    from bigml.laminar.math_ops import dot


LOGGER = logging.getLogger('BigML')

EXPANSION_ATTRIBUTES = {"categorical": "categories", "text": "tag_clouds",
                        "items": "items"}

CATEGORICAL = "categorical"
CONFIDENCE = 0.95

DUMMY = "dummy"
CONTRAST = "contrast"
OTHER = "other"

def get_terms_array(terms, unique_terms, field, field_id):
    """ Returns an array that represents the frequency of terms as ordered
    in the reference `terms` parameter.

    """
    input_terms = unique_terms.get(field_id, [])
    terms_array = [0] * len(terms)
    try:
        for term, frequency in input_terms:
            index = terms.index(term)
            terms_array[index] = frequency
    except ValueError:
        pass
    return terms_array


class LinearRegression(ModelFields):
    """ A lightweight wrapper around a linear regression model.

    Uses a BigML remote linear regression model to build a local version
    that can be used to generate predictions locally.

    """

    def __init__(self, linear_regression, api=None):

        self.resource_id = None
        self.input_fields = []
        self.term_forms = {}
        self.tag_clouds = {}
        self.term_analysis = {}
        self.items = {}
        self.item_analysis = {}
        self.categories = {}
        self.coefficients = []
        self.data_field_types = {}
        self.field_codings = {}
        self.bias = None
        self.xtx_inverse = []
        self.mean_squared_error = None
        self.number_of_parameters = None
        self.number_of_samples = None
        self.api = get_api_connection(api)
        self.resource_id, linear_regression = get_resource_dict( \
            linear_regression, "linearregression", api=self.api)

        if 'object' in linear_regression and \
            isinstance(linear_regression['object'], dict):
            linear_regression = linear_regression['object']
        try:
            self.input_fields = linear_regression.get("input_fields", [])
            self.dataset_field_types = linear_regression.get(
                "dataset_field_types", {})
            self.weight_field = linear_regression.get("weight_field")
            objective_field = linear_regression['objective_fields'] if \
                linear_regression['objective_fields'] else \
                linear_regression['objective_field']
        except KeyError:
            raise ValueError("Failed to find the linear regression expected "
                             "JSON structure. Check your arguments.")
        if 'linear_regression' in linear_regression and \
            isinstance(linear_regression['linear_regression'], dict):
            status = get_status(linear_regression)
            if 'code' in status and status['code'] == FINISHED:
                linear_regression_info = linear_regression[ \
                    'linear_regression']
                fields = linear_regression_info.get('fields', {})

                if not self.input_fields:
                    self.input_fields = [ \
                        field_id for field_id, _ in
                        sorted(fields.items(),
                               key=lambda x: x[1].get("column_number"))]
                self.coeff_ids = self.input_fields[:]
                self.coefficients = linear_regression_info.get( \
                    'coefficients', [])
                self.bias = linear_regression_info.get('bias', True)
                self.field_codings = linear_regression_info.get( \
                     'field_codings', {})
                self.number_of_parameters = linear_regression_info.get( \
                    "number_of_parameters")
                missing_tokens = linear_regression_info.get("missing_tokens")

                objective_id = extract_objective(objective_field)
                ModelFields.__init__(
                    self, fields,
                    objective_id=objective_id, terms=True, categories=True,
                    numerics=True, missing_tokens=missing_tokens)
                self.field_codings = linear_regression_info.get( \
                  'field_codings', {})
                self.format_field_codings()
                for field_id in self.field_codings:
                    if field_id not in fields and \
                            field_id in self.inverted_fields:
                        self.field_codings.update( \
                            {self.inverted_fields[field_id]: \
                             self.field_codings[field_id]})
                        del self.field_codings[field_id]
                stats = linear_regression_info["stats"]
                if STATS and stats is not None and \
                        stats.get("xtx_inverse") is not None:
                    self.xtx_inverse = stats["xtx_inverse"][:]
                    self.mean_squared_error = stats["mean_squared_error"]
                    self.number_of_samples = stats["number_of_samples"]
                    # to be used in predictions
                    self.t_crit = student_t.interval( \
                        CONFIDENCE,
                        self.number_of_samples - self.number_of_parameters)[1]
                    self.xtx_inverse = list( \
                        np.linalg.inv(np.array(self.xtx_inverse)))

            else:
                raise Exception("The linear regression isn't finished yet")
        else:
            raise Exception("Cannot create the LinearRegression instance."
                            " Could not find the 'linear_regression' key"
                            " in the resource:\n\n%s" %
                            linear_regression)

    def expand_input(self, input_data, unique_terms, compact=False):
        """ Creates an input array with the values in input_data and
        unique_terms and the following rules:
        - fields are ordered as input_fields
        - numeric fields contain the value or 0 if missing
        - categorial fields are one-hot encoded and classes are sorted as
          they appear in the field summary. If missing_count > 0 a last
          missing element is added set to 1 if the field is missing and 0
          otherwise
        - text and items fields are expanded into their elements as found
          in the corresponding summmary information and their values treated
          as numerics.
        """
        input_array = []
        for index, field_id in enumerate(self.coeff_ids):
            field = self.fields[field_id]
            optype = field["optype"]
            missing = False
            new_inputs = []
            if optype == NUMERIC:
                if field_id in input_data:
                    value = input_data.get(field_id, 0)
                else:
                    missing = True
                    value = 0
                new_inputs = [value]
            else:
                terms = getattr(self, EXPANSION_ATTRIBUTES[optype])[field_id]
                length = len(terms)
                if field_id in unique_terms:
                    new_inputs = get_terms_array( \
                        terms, unique_terms, field, field_id)
                else:
                    new_inputs = [0] * length
                    missing = True

            if field["summary"]["missing_count"] > 0 or \
                    (optype == CATEGORICAL and \
                     self.field_codings[field_id].get(DUMMY) is None):
                new_inputs.append(int(missing))

            if optype == CATEGORICAL:
                new_inputs = self.categorical_encoding( \
                    new_inputs, field_id, compact)

            input_array.extend(new_inputs)

        if self.bias or not compact:
            input_array.append(1)

        return input_array

    def categorical_encoding(self, inputs, field_id, compact):
        """Returns the result of combining the encoded categories
        according to the field_codings projections

        The result is the components generated by the categorical field
        """

        new_inputs = inputs[:]

        projections = self.field_codings[field_id].get( \
                CONTRAST, self.field_codings[field_id].get(OTHER))
        if projections is not None:
            new_inputs = flatten(dot(projections, [new_inputs]))

        if compact and self.field_codings[field_id].get(DUMMY) is not None:
            dummy_class = self.field_codings[field_id][DUMMY]
            index = self.categories[field_id].index(dummy_class)
            cat_new_inputs = new_inputs[0: index]
            if len(new_inputs) > (index + 1):
                cat_new_inputs.extend(new_inputs[index + 1 :])
            new_inputs = cat_new_inputs

        return new_inputs

    def predict(self, input_data, full=False):
        """Returns the prediction and the confidence intervals

        input_data: Input data to be predicted
        full: Boolean that controls whether to include the prediction's
              attributes. By default, only the prediction is produced. If set
              to True, the rest of available information is added in a
              dictionary format. The dictionary keys can be:
                  - prediction: the prediction value
                  - unused_fields: list of fields in the input data that
                                   are not being used in the model

        """

        # Checks and cleans input_data leaving the fields used in the model
        unused_fields = []
        new_data = self.filter_input_data( \
            input_data,
            add_unused_fields=full)
        if full:
            new_data, unused_fields = new_data

        # Strips affixes for numeric values and casts to the final field type
        cast(new_data, self.fields)

        # In case that the training data has no missings, input data shouldn't
        check_no_training_missings(new_data, self.model_fields,
                                   self.weight_field,
                                   self.objective_id)

        # Computes text and categorical field expansion
        unique_terms = self.get_unique_terms(new_data)

        # Creates an input vector with the values for all expanded fields.
        input_array = self.expand_input(new_data, unique_terms)
        compact_input_array = self.expand_input(new_data, unique_terms, True)

        prediction = dot([flatten(self.coefficients)], [input_array])[0][0]

        result = {
            "prediction": prediction}
        if self.xtx_inverse:
            result.update({"confidence_bounds": self.confidence_bounds( \
                compact_input_array)})

        if full:
            result.update({"unused_fields": unused_fields})
        else:
            result = result["prediction"]

        return result


    def predict_probability(self, input_data, compact=False):
        """Method to homogeinize predictions in fusions and composites

        """

        prediction = self.predict(input_data, full=not compact)

        if compact:
            output = [prediction]
        else:
            output = prediction

        return output


    def confidence_bounds(self, input_array):
        """Computes the confidence interval for the prediction

        """
        product = dot(dot([input_array], self.xtx_inverse),
                      [input_array])[0][0]
        valid = True
        try:
            confidence_interval = self.t_crit * math.sqrt( \
                self.mean_squared_error * product)
            prediction_interval = self.t_crit * math.sqrt( \
                self.mean_squared_error * (product + 1))
            valid = True
        except ValueError:
            valid = False
            confidence_interval, prediction_interval = (0, 0)

        return {"confidence_interval": confidence_interval,
                "prediction_interval": prediction_interval,
                "valid": valid}


    def format_field_codings(self):
        """ Changes the field codings format to the dict notation

        """
        if isinstance(self.field_codings, list):
            self.field_codings_list = self.field_codings[:]
            field_codings = self.field_codings[:]
            self.field_codings = {}
            for element in field_codings:
                field_id = element['field']
                if element["coding"] == DUMMY:
                    self.field_codings[field_id] = {\
                        element["coding"]: element['dummy_class']}
                else:
                    self.field_codings[field_id] = {\
                        element["coding"]: element['coefficients']}
