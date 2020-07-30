# -*- coding: utf-8 -*-
# !/usr/bin/env python
#
# Copyright 2020 BigML
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
A Minimal fast building local Predictive Anomaly Detector.

This module defines an Anomaly Detector to score anomalies in a dataset locally
or embedded into your application without needing to send requests to
BigML.io.

This module doesn't have all the features of the main Anomaly module (for
instance, it does not maintain a list of top anomalies) --- it's only job is
to be able to return an anomaly score for a given instance.

The module is designed for situations when it is desirable to be able to
build the anomaly detector very quickly from an external representation.

Example usage (assuming that you have previously set up the BIGML_USERNAME
and BIGML_API_KEY environment variables and that you own the model/id below):

from bigml.api import BigML
from minomaly import Minomaly, dumps, loads

# First build as you would any core Anomaly object:
anomaly = Minomaly('anomaly/5126965515526876630001b2')

# Get a serialized version as a byte string:
fast_external_rep = dumps(anomaly)

# (store the external rep somewhere convenient)

#
# ... some other time and/or place ...
#

# (retrieve the external rep from its convenient place)

# Speedy Build from external rep
anomaly = loads(fast_external_rep)

# Get scores same as always:
anomaly.anomaly_score({"src_bytes": 350})

"""


import math
import pickle

from bigml.minmodels.predicate_utils import OPERATOR_CODE
from bigml.minmodels.predicate_utils import apply_predicates
from bigml.api import FINISHED
from bigml.api import get_status, get_api_connection, get_anomaly_id
from bigml.basemodel import get_resource_dict
from bigml.modelfields import ModelFields
from bigml.util import cast


DEPTH_FACTOR = 0.5772156649


def build_tree(children, node=None):
    """Builds a compressed version of the tree structure as an list of
    lists. Starting from the root node, that is represented by a list:
        [len(children), children1, children2, etc.]
    And each child is represented by a list whose elements are:
        [weight, len(predicates), operator_code, field, value, term, missing,
         ..., len(children), children_nodes_list*]

    """
    outer = node if node else list()
    outer.append(len(children))
    for child in children:
        inner = list()
        inner.append(child.get('weight'))
        predicates = child.get('predicates')
        if predicates and not (predicates is True or predicates == [True]):
            predicates = [x for x in predicates if x is not True]
            inner.append(len(predicates))
            for pred in predicates:
                operation = pred.get('op')
                value = pred.get('value')
                missing = False
                if operation.endswith("*"):
                    operation = operation[0: -1]
                    missing = True
                elif operation == 'in' and None in value:
                    missing = True

                inner.append(OPERATOR_CODE.get(operation))
                inner.append(pred.get('field'))
                inner.append(value)
                inner.append(pred.get('term'))
                inner.append(missing)
        else:
            inner.append(0)
        next_gen = child.get('children')
        if next_gen:
            build_tree(next_gen, node=inner)
        else:
            inner.append(0)
        outer.append(inner)

    return outer


def calculate_depth(node, input_data, fields, depth=0):
    """Computes the depth in the tree for the input data

    """

    weight = node[0] if node[0] else 1
    num_predicates = node[1]
    num_children = node[2 + (5 * num_predicates)]

    if not apply_predicates(node, input_data, fields):
        return depth

    depth += weight
    if num_children > 0:
        start = 3 + (5 * num_predicates)
        end = 3 + num_children + (5 * num_predicates)
        children = node[slice(start, end)]
        for child in children:
            if apply_predicates(child, input_data, fields):
                return calculate_depth(child, input_data, fields, depth)

    return depth


def use_cache(cache_get):
    """Checks whether the user has provided a cache get function to retrieve
       local models.

    """
    return cache_get is not None and hasattr(cache_get, '__call__')


class Minomaly(ModelFields):
    """ A minimal anomaly detector designed to build quickly from a
    specialized external representation. See file documentation, above,
    for usage.
    """

    def __init__(self, anomaly, api=None, cache_get=None):

        if use_cache(cache_get):
            # using a cache to store the Minomaly attributes
            anomaly_id = get_anomaly_id(anomaly)
            self.__dict__ = pickle.loads(cache_get(anomaly_id))
        else:
            self.resource_id = None
            self.sample_size = None
            self.input_fields = None
            self.mean_depth = None
            self.expected_mean_depth = None
            self.iforest = None
            self.id_fields = []
            self.api = get_api_connection(api)
            self.resource_id, anomaly = get_resource_dict(
                anomaly, "anomaly", api=self.api)

            if 'object' in anomaly and isinstance(anomaly['object'], dict):
                anomaly = anomaly['object']
                self.sample_size = anomaly.get('sample_size')
                self.input_fields = anomaly.get('input_fields')
                self.id_fields = anomaly.get('id_fields', [])

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
                    else:
                        self.norm = self.normalization_factor if \
                            self.normalization_factor is not None else \
                            self.norm_factor()
                    iforest = anomaly['model'].get('trees', [])
                    if iforest:
                        self.iforest = [
                            build_tree([anomaly_tree['root']])
                            for anomaly_tree in iforest]
                else:
                    raise Exception("The anomaly isn't finished yet")

    def norm_factor(self):
        """Computing the normalization factor for simple anomaly detectors"""
        if self.mean_depth is not None:
            default_depth = self.mean_depth if self.sample_size == 1 else \
                (2 * (DEPTH_FACTOR + math.log(self.sample_size - 1) -
                      (float(self.sample_size - 1) / self.sample_size)))
            return min(self.mean_depth, default_depth)

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
        input_data = self.filter_input_data(input_data)

        # Strips affixes for numeric values and casts to the final field type
        cast(input_data, self.fields)

        depth_sum = 0

        if self.iforest is None:
            raise Exception("We could not find the iforest information to "
                            "compute the anomaly score. Please, rebuild your "
                            "Anomaly object from a complete anomaly detector "
                            "resource.")
        for tree in self.iforest:
            tree_depth = calculate_depth(tree[1], input_data, self.fields)
            depth_sum += tree_depth

        observed_mean_depth = float(depth_sum) / len(self.iforest)
        return math.pow(2, - observed_mean_depth / self.norm)


    def dump(self, output):
        """Uses pickle to serialize the minomaly object

        """
        return pickle.dump(self.__dict__, output)

    def dumps(self):
        """Uses pickle to serialize the minomaly object to a string

        """
        return pickle.dumps(self.__dict__)
