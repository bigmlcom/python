# -*- coding: utf-8 -*-
#
# Copyright 2020-2022 BigML
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
A fast building local Predictive Anomaly Detector.
This module defines an Anomaly Detector to score anomalies in a dataset locally
or embedded into your application without needing to send requests to
BigML.io.
The module is also designed for situations when it is desirable to be able to
build the anomaly detector very quickly from an external representation.
It also offers the ability to load its contents from a cache system like
Redis or memcache. The `get` method of the cache system has to be passed
in the `cache_get` argument and the hash for the storage should be the
corresponding anomaly ID.
Example usage (assuming that you have previously set up the BIGML_USERNAME
and BIGML_API_KEY environment variables and that you own the model/id below):
from bigml.api import BigML
from anomaly import Anomaly
import redis
r = redis.Redis()
# First build as you would any core Anomaly object:
anomaly = Anomaly('anomaly/5126965515526876630001b2')
# Store a serialized version in Redis
anomaly.dump(cache_set=r.set)
# (retrieve the external rep from its convenient place)
# Speedy Build from external rep
anomaly = Anomaly('anomaly/5126965515526876630001b2', cache_get=r.get)
# Get scores same as always:
anomaly.anomaly_score({"src_bytes": 350})
"""


import math

from bigml.predicate_utils.utils import OPERATOR_CODE, PREDICATE_INFO_LENGTH
from bigml.predicate_utils.utils import apply_predicates
from bigml.api import FINISHED
from bigml.api import get_status, get_api_connection, get_anomaly_id
from bigml.basemodel import get_resource_dict
from bigml.modelfields import ModelFields, NUMERIC
from bigml.util import cast, use_cache, load, get_data_format, \
    get_formatted_data, format_data, get_data_transformations
from bigml.constants import OUT_NEW_HEADERS, INTERNAL, DECIMALS


DEPTH_FACTOR = 0.5772156649
PREDICATES_OFFSET = 3

DFT_OUTPUTS = ["score"]

#pylint: disable=locally-disabled,invalid-name
def get_repeat_depth(population):
    """Computes the correction to depth used to normalize repeats

    """
    repeat_depth = 0
    if population > 1:
        h = DEPTH_FACTOR + math.log(population - 1)
        repeat_depth = max([1.0,
                            2 * (h - (float(population - 1) / population))])
    return repeat_depth


def build_tree(node, add_population=False):
    """Builds a compressed version of the tree structure as an list of
    lists. Starting from the root node, each node
    is represented by a list whose elements are:
        [weight, len(predicates), operator_code, field, value, term, missing,
         ..., len(children), children_nodes_list*]

    When the normalize_repeats flag is set to True, we need to add the
    population of the node: [weight, population, len(predicates), ...]
    """
    outer = []
    outer.append(node.get('weight', 1))
    if add_population:
        outer.append(get_repeat_depth(node.get("population", 0)))
    build_predicates(node, outer)
    children = node.get("children", [])
    outer.append(len(children))

    if not children:
        return outer

    for child in children:
        outer.append(build_tree(child, add_population=add_population))

    return outer


def build_predicates(node, encoded_node):
    """Build the minified version of the predicate in a node"""
    predicates = node.get('predicates')
    if predicates and not (predicates is True or predicates == [True]):
        predicates = [x for x in predicates if x is not True]
        encoded_node.append(len(predicates))
        for pred in predicates:
            operation = pred.get('op')
            value = pred.get('value')
            missing = False
            if operation.endswith("*"):
                operation = operation[0: -1]
                missing = True
            elif operation == 'in' and None in value:
                missing = True

            encoded_node.append(OPERATOR_CODE.get(operation))
            encoded_node.append(pred.get('field'))
            encoded_node.append(value)
            encoded_node.append(pred.get('term'))
            encoded_node.append(missing)
    else:
        encoded_node.append(0) # no predicates

    return encoded_node


def calculate_depth(node, input_data, fields, depth=0,
                    normalize_repeats=False):
    """Computes the depth in the tree for the input data

    """

    weight = node[0]
    shift = 0
    repeat_depth = 0
    if normalize_repeats:
        shift = 1
        repeat_depth = node[1]

    num_predicates = node[1 + shift]
    num_children = node[2 + shift + (5 * num_predicates)]

    predicates_ok = 0

    if num_predicates > 0:
        predicates_ok = apply_predicates(node, input_data, fields,
                                         normalize_repeats=normalize_repeats)


    # some of the predicates where met and depth > 1 in a leaf
    if num_predicates > 0 and 0 < predicates_ok < num_predicates and \
            depth > 1 and num_children == 0:
        return depth + repeat_depth


    if num_predicates > 0 and predicates_ok != num_predicates:
        return depth

    depth += weight

    if num_children > 0:
        start = PREDICATES_OFFSET + (PREDICATE_INFO_LENGTH * num_predicates) \
            + shift
        end = PREDICATES_OFFSET + num_children + ( \
            PREDICATE_INFO_LENGTH * num_predicates) + shift
        children = node[slice(start, end)]
        for child in children:
            num_predicates = child[1 + shift]
            predicates_ok = apply_predicates( \
                child, input_data, fields,
                normalize_repeats=normalize_repeats)
            if predicates_ok == num_predicates:
                return calculate_depth(child, input_data, fields, depth,
                                       normalize_repeats=normalize_repeats)
    else:
        depth += repeat_depth

    return depth


class Anomaly(ModelFields):
    """ A minimal anomaly detector designed to build quickly from a
    specialized external representation. See file documentation, above,
    for usage.

    """

    def __init__(self, anomaly, api=None, cache_get=None):

        if use_cache(cache_get):
            # using a cache to store the Minomaly attributes
            self.__dict__ = load(get_anomaly_id(anomaly), cache_get)
            return

        self.resource_id = None
        self.name = None
        self.description = None
        self.parent_id = None
        self.sample_size = None
        self.input_fields = None
        self.default_numeric_value = None
        self.mean_depth = None
        self.expected_mean_depth = None
        self.normalize_repeats = None
        self.iforest = None
        self.id_fields = []
        api = get_api_connection(api)
        self.resource_id, anomaly = get_resource_dict(
            anomaly, "anomaly", api=api)

        if 'object' in anomaly and isinstance(anomaly['object'], dict):
            anomaly = anomaly['object']
        try:
            self.parent_id = anomaly.get('dataset')
            self.name = anomaly.get("name")
            self.description = anomaly.get("description")
            self.sample_size = anomaly.get('sample_size')
            self.input_fields = anomaly.get('input_fields')
            self.default_numeric_value = anomaly.get('default_numeric_value')
            self.normalize_repeats = anomaly.get('normalize_repeats', False)
            self.id_fields = anomaly.get('id_fields', [])
        except AttributeError:
            raise ValueError("Failed to find the expected "
                             "JSON structure. Check your arguments.")

        if 'model' in anomaly and isinstance(anomaly['model'], dict):
            ModelFields.__init__(
                self, anomaly['model'].get('fields'),
                missing_tokens=anomaly['model'].get('missing_tokens'))
            self.mean_depth = anomaly['model'].get('mean_depth')
            self.normalization_factor = anomaly['model'].get(
                'normalization_factor')
            self.nodes_mean_depth = anomaly['model'].get(
                'nodes_mean_depth')
            status = get_status(anomaly)
            if 'code' in status and status['code'] == FINISHED:
                self.expected_mean_depth = None
                if self.mean_depth is None or self.sample_size is None:
                    raise Exception("The anomaly data is not complete. "
                                    "Score will not be available")
                self.norm = self.normalization_factor if \
                    self.normalization_factor is not None else \
                    self.norm_factor()
                iforest = anomaly['model'].get('trees', [])
                self.iforest = []
                if iforest:
                    self.iforest = [
                        build_tree(anomaly_tree['root'],
                                   add_population=self.normalize_repeats)
                        for anomaly_tree in iforest]
                self.top_anomalies = anomaly['model']['top_anomalies']
            else:
                raise Exception("The anomaly isn't finished yet")

    def norm_factor(self):
        """Computing the normalization factor for simple anomaly detectors"""
        if self.mean_depth is not None:
            default_depth = self.mean_depth if self.sample_size == 1 else \
                (2 * (DEPTH_FACTOR + math.log(self.sample_size - 1) -
                      (float(self.sample_size - 1) / self.sample_size)))
            return min(self.mean_depth, default_depth)
        return None

    def data_transformations(self):
        """Returns the pipeline transformations previous to the modeling
        step as a pipeline, so that they can be used in local predictions.
        """
        return get_data_transformations(self.resource_id, self.parent_id)

    def anomaly_score(self, input_data):
        """Returns the anomaly score given by the iforest
            To produce an anomaly score, we evaluate each tree in the iforest
            for its depth result (see the depth method in the AnomalyTree
            object for details). We find the average of these depths
            to produce an `observed_mean_depth`. We calculate an
            `expected_mean_depth` using the `sample_size` and `mean_depth`
            parameters which come as part of the forest message.
            We combine those values as seen below, which should result in a
            value between 0 and 1.

        """
        # corner case with only one record
        if self.sample_size == 1 and self.normalization_factor is None:
            return 1
        # Checks and cleans input_data leaving the fields used in the model
        norm_input_data = self.filter_input_data(input_data)
        # Strips affixes for numeric values and casts to the final field type
        cast(norm_input_data, self.fields)

        depth_sum = 0

        if self.iforest is None:
            raise Exception("We could not find the iforest information to "
                            "compute the anomaly score. Please, rebuild your "
                            "Anomaly object from a complete anomaly detector "
                            "resource.")
        for tree in self.iforest:
            tree_depth = calculate_depth(
                tree,
                norm_input_data, self.fields,
                normalize_repeats=self.normalize_repeats)
            depth_sum += tree_depth

        observed_mean_depth = float(depth_sum) / len(self.iforest)
        return round(math.pow(2, - observed_mean_depth / self.norm),
                     DECIMALS)

    def anomalies_filter(self, include=True):
        """Returns the LISP expression needed to filter the subset of
           top anomalies. When include is set to True, only the top
           anomalies are selected by the filter. If set to False, only the
           rest of the dataset is selected.
        """
        anomaly_filters = []
        for anomaly in self.top_anomalies:
            row = anomaly.get('row_number')
            if row is not None:
                anomaly_filters.append('(= (row-number) %s)' % row)

        anomalies_filter = " ".join(anomaly_filters)
        if len(anomaly_filters) == 1:
            if include:
                return anomalies_filter
            return "(not %s)" % anomalies_filter
        if include:
            return "(or %s)" % anomalies_filter
        return "(not (or %s))" % anomalies_filter

    def fill_numeric_defaults(self, input_data):
        """Checks whether input data is missing a numeric field and
        fills it with the average quantity set in default_numeric_value

        """

        for field_id, field in list(self.fields.items()):
            if field_id not in self.id_fields and \
                    field['optype'] == NUMERIC and \
                    field_id not in input_data and \
                    self.default_numeric_value is not None:
                default_value = 0 if self.default_numeric_value == "zero" \
                    else field['summary'].get(self.default_numeric_value)
                input_data[field_id] = default_value
        return input_data

    def batch_predict(self, input_data_list, outputs=None, **kwargs):
        """Creates a batch anomaly score for a list of inputs using the local
        anomaly detector. Allows to define some output settings to decide the
        name of the header used for the score in the result. To homogeneize
        the behaviour of supervised batch_predict method, the outputs argument
        accepts a dictionary with keys: "output_fields" and "output_headers".
        In this case, output_fields is ignored, as only the score can be
        obtained from the anomaly_score method, and only "output_headers" is
        considered to allow changing the header associated to that new field.

        :param input_data_list: List of input data to be predicted
        :type input_data_list: list or Panda's dataframe
        :param dict outputs: properties that define the headers and fields to
                             be added to the input data
        :return: the list of input data plus the predicted values
        :rtype: list or Panda's dataframe depending on the input type in
                input_data_list

        """
        if outputs is None:
            outputs = {}
        new_headers = outputs.get(OUT_NEW_HEADERS, DFT_OUTPUTS)
        data_format = get_data_format(input_data_list)
        inner_data_list = get_formatted_data(input_data_list, INTERNAL)
        for input_data in inner_data_list:
            prediction = {"score": self.anomaly_score(input_data, **kwargs)}
            for index, key in enumerate(DFT_OUTPUTS):
                input_data[new_headers[index]] = prediction[key]
        if data_format != INTERNAL:
            return format_data(inner_data_list, out_format=data_format)
        return inner_data_list
