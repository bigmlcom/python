# -*- coding: utf-8 -*-
#
# Copyright 2018-2020 BigML
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

"""A local Partial Component Analysis.

This module defines a PCA to make projections locally or
embedded into your application without needing to send requests to
BigML.io.

This module cannot only save you a few credits, but also enormously
reduce the latency for each prediction and let you use your PCAs offline.

Example usage (assuming that you have previously set up the BIGML_USERNAME
and BIGML_API_KEY environment variables and that you own the
logisticregression/id below):

from bigml.api import BigML
from bigml.pca import PCA

api = BigML()

pca = PCA(
    'pca/5026965515526876630001b2')
pca.projection({"petal length": 3, "petal width": 1,
                "sepal length": 1, "sepal width": 0.5})

"""
import logging
import math


from bigml.api import FINISHED
from bigml.api import get_status, get_api_connection
from bigml.util import cast, NUMERIC
from bigml.basemodel import get_resource_dict
from bigml.modelfields import ModelFields

try:
    from bigml.laminar.numpy_ops import dot
except ImportError:
    from bigml.laminar.math_ops import dot

LOGGER = logging.getLogger('BigML')

EXPANSION_ATTRIBUTES = {"categorical": "categories", "text": "tag_clouds",
                        "items": "items"}

CATEGORICAL = "categorical"


def get_terms_array(terms, unique_terms, field, field_id):
    """ Returns an array that represents the frequency of terms as ordered
    in the reference `terms` parameter.

    """
    input_terms = unique_terms.get(field_id, [])
    terms_array = [0] * len(terms)
    if field['optype'] == CATEGORICAL and \
            field["summary"].get("missing_count", 0) > 0:
        terms_array.append(int(field_id not in unique_terms))
    try:
        for term, frequency in input_terms:
            index = terms.index(term)
            terms_array[index] = frequency
    except ValueError:
        pass
    return terms_array


class PCA(ModelFields):
    """ A lightweight wrapper around a PCA.

    Uses a BigML remote PCA to build a local version
    that can be used to generate projections locally.

    """

    def __init__(self, pca, api=None):

        self.resource_id = None
        self.input_fields = []
        self.term_forms = {}
        self.tag_clouds = {}
        self.dataset_field_types = {}
        self.term_analysis = {}
        self.categories = {}
        self.categories_probabilities = {}
        self.items = {}
        self.fields = {}
        self.item_analysis = {}
        self.standardize = None
        self.famd_j = 1
        self.api = get_api_connection(api)

        self.resource_id, pca = get_resource_dict( \
            pca, "pca", api=self.api)

        if 'object' in pca and \
            isinstance(pca['object'], dict):
            pca = pca['object']
        try:
            self.input_fields = pca.get("input_fields", [])
            self.dataset_field_types = pca.get("dataset_field_types", {})
            self.famd_j = 1 if (self.dataset_field_types['categorical'] != \
                self.dataset_field_types['total']) else \
                self.dataset_field_types['categorical']

        except KeyError:
            raise ValueError("Failed to find the pca expected "
                             "JSON structure. Check your arguments.")
        if 'pca' in pca and \
            isinstance(pca['pca'], dict):
            status = get_status(pca)
            if 'code' in status and status['code'] == FINISHED:
                pca_info = pca[ \
                    'pca']
                fields = pca_info.get('fields', {})
                self.fields = fields
                if not self.input_fields:
                    self.input_fields = [ \
                        field_id for field_id, _ in
                        sorted(list(self.fields.items()),
                               key=lambda x: x[1].get("column_number"))]
                missing_tokens = pca_info.get("missing_tokens")
                ModelFields.__init__(
                    self, fields,
                    objective_id=None, terms=True, categories=True,
                    numerics=False, missing_tokens=missing_tokens)

                for field_id in self.categories:
                    field = self.fields[field_id]
                    probabilities = [probability for _, probability in \
                                     field["summary"]["categories"]]
                    if field["summary"].get("missing_count", 0) > 0:
                        probabilities.append(field["summary"]["missing_count"])
                    total = float(sum(probabilities))
                    if total > 0:
                        probabilities = [probability / total for probability \
                            in probabilities]
                    self.categories_probabilities[field_id] = probabilities
                self.components = pca_info.get('components')
                self.eigenvectors = pca_info.get('eigenvectors')
                self.cumulative_variance = pca_info.get('cumulative_variance')
                self.text_stats = pca_info.get('text_stats')
                self.standardized = pca_info.get('standardized')
                self.variance = pca_info.get('variance')

            else:
                raise Exception("The pca isn't finished yet")
        else:
            raise Exception("Cannot create the PCA instance."
                            " Could not find the 'pca' key"
                            " in the resource:\n\n%s" %
                            pca)


    def projection(self, input_data, max_components=None,
                   variance_threshold=None, full=False):
        """Returns the projection of input data in the new components

        input_data: Input data to be projected

        """

        new_data = self.filter_input_data( \
            input_data,
            add_unused_fields=False)

        # Strips affixes for numeric values and casts to the final field type
        cast(new_data, self.fields)

        # Computes text and categorical field expansion into an input array of
        # terms and frequencies
        unique_terms = self.get_unique_terms(new_data)


        # Creates an input vector with the values for all expanded fields.
        # The input mask marks the non-missing or categorical fields
        # The `missings` variable is a boolean indicating whether there's
        # non-categorical fields missing
        input_array, missings, input_mask = self.expand_input(new_data,
                                                              unique_terms)
        components = self.eigenvectors[:]
        if max_components is not None:
            components = components[0: max_components]
        if variance_threshold is not None:
            for index, cumulative in enumerate(self.cumulative_variance):
                if cumulative > variance_threshold:
                    components = components[0: index + 1]

        result = [value[0] for value in dot(components, [input_array])]

        # if non-categorical fields values are missing in input data
        # there's an additional normalization
        if missings:
            missing_sums = self.missing_factors(input_mask)
            for index, value in enumerate(result):
                result[index] = value / missing_sums[index] \
                    if missing_sums[index] > 0 else value
        if full:
            result = dict(list(zip(["PC%s" % index \
                for index in range(1, len(components) + 1)], result)))
        return result


    def missing_factors(self, input_mask):
        """Returns the factors to divide the PCA values when input
        data has missings

        """

        sum_eigenvectors = []
        for row in self.eigenvectors:
            eigenvector = [a * b for a, b in zip(input_mask, row)]
            sum_eigenvectors.append(dot([eigenvector], [eigenvector])[0][0])
        return sum_eigenvectors


    def _get_mean_stdev(self, field, field_id=None, index=None):
        """Returns the quantities to be used as mean and stddev to normalize

        """
        if field['optype'] == CATEGORICAL and index is not None:
            mean = self.categories_probabilities[field_id][index]
            stdev = self.famd_j * math.sqrt(mean * self.famd_j)
            return mean, stdev
        elif field['optype'] == NUMERIC:
            return field["summary"]["mean"], \
                field["summary"]["standard_deviation"]
        else:
            return self.text_stats[field_id]['means'][index], \
                self.text_stats[field_id]['standard_deviations'][index]


    def expand_input(self, input_data, unique_terms):
        """ Creates an input array with the values in input_data and
        unique_terms and the following rules:
        - fields are ordered as input_fields
        - numeric fields contain the value or 0 if missing
        - categorial fields are one-hot encoded and classes are sorted as
          they appear in the field summary. If missing_count > 0 a last
          missing element is added set to 1 if the field is missing and o
          otherwise
        - text and items fields are expanded into their elements as found
          in the corresponding summmary information and their values treated
          as numerics.
        """
        input_array = []
        input_mask = []
        missings = False
        for index, field_id in enumerate(self.input_fields):
            field = self.fields[field_id]
            optype = field["optype"]
            if optype == NUMERIC:
                input_mask.append(int(field_id in input_data))
                if field_id in input_data:
                    value = input_data.get(field_id, 0)
                    if self.standardized:
                        mean, stdev = self._get_mean_stdev(field)
                        value -= mean
                        if stdev > 0:
                            value /= stdev
                else:
                    missings = True
                    value = 0
                input_array.append(value)
            else:
                terms = getattr(self, EXPANSION_ATTRIBUTES[optype])[field_id]
                if field_id in unique_terms:
                    new_inputs = get_terms_array( \
                        terms, unique_terms, field, field_id)
                    input_mask.extend( \
                        [1] * len(new_inputs))
                else:
                    new_inputs = [0] * len(terms)
                    if optype != CATEGORICAL:
                        missings = True
                        input_mask.extend([0] * len(terms))
                    else:
                        input_mask.extend([1] * len(terms))
                        if field["summary"]["missing_count"] > 0:
                            new_inputs.append(1)
                            input_mask.append(1)

                if self.standardized:
                    for index, frequency in enumerate(new_inputs):
                        mean, stdev = self._get_mean_stdev( \
                            field, field_id, index)
                        new_inputs[index] = frequency - mean
                        if stdev > 0:
                            new_inputs[index] /= stdev
                    # indexes of non-missing values
                input_array.extend(new_inputs)

        return input_array, missings, input_mask
