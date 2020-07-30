# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2014-2020 BigML
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

"""A local Predictive Anomaly Detector.

This module defines an Anomaly Detector to score anomalies in a dataset locally
or embedded into your application without needing to send requests to
BigML.io.

This module cannot only save you a few credits, but also enormously
reduce the latency for each prediction and let you use your models
offline.

Example usage (assuming that you have previously set up the BIGML_USERNAME
and BIGML_API_KEY environment variables and that you own the model/id below):

from bigml.api import BigML
from bigml.anomaly import Anomaly

api = BigML()

anomaly = Anomaly('anomaly/5126965515526876630001b2')
anomaly.anomaly_score({"src_bytes": 350})

"""
import logging
import math
import json

from bigml.api import FINISHED
from bigml.api import get_status, get_api_connection
from bigml.util import cast
from bigml.basemodel import get_resource_dict
from bigml.modelfields import ModelFields
from bigml.anomalytree import AnomalyTree


LOGGER = logging.getLogger('BigML')

DEPTH_FACTOR = 0.5772156649


def norm_factor(sample_size, mean_depth):
    """Computing the normalization factor for simple anomaly detectors

    """
    if mean_depth is not None:
        default_depth = mean_depth if sample_size == 1 else \
            (2 * (DEPTH_FACTOR + math.log(sample_size - 1) - \
            (float(sample_size - 1) / sample_size)))
        return min(mean_depth, default_depth)


class Anomaly(ModelFields):
    """ A lightweight wrapper around an anomaly detector.

    Uses a BigML remote anomaly detector model to build a local version that
    can be used to generate anomaly scores locally.

    """

    def __init__(self, anomaly, api=None):

        self.resource_id = None
        self.sample_size = None
        self.input_fields = None
        self.mean_depth = None
        self.expected_mean_depth = None
        self.iforest = None
        self.top_anomalies = None
        self.id_fields = []
        self.api = get_api_connection(api)
        self.resource_id, anomaly = get_resource_dict( \
            anomaly, "anomaly", api=self.api)

        if 'object' in anomaly and isinstance(anomaly['object'], dict):
            anomaly = anomaly['object']
            self.sample_size = anomaly.get('sample_size')
            self.input_fields = anomaly.get('input_fields')
            self.id_fields = anomaly.get('id_fields', [])
        if 'model' in anomaly and isinstance(anomaly['model'], dict):
            ModelFields.__init__( \
                self, anomaly['model'].get('fields'), \
                missing_tokens=anomaly['model'].get('missing_tokens'))
            if ('top_anomalies' in anomaly['model'] and
                    isinstance(anomaly['model']['top_anomalies'], list)):
                self.mean_depth = anomaly['model'].get('mean_depth')
                self.normalization_factor = anomaly['model'].get( \
                    'normalization_factor')
                self.nodes_mean_depth = anomaly['model'].get( \
                    'nodes_mean_depth')
                status = get_status(anomaly)
                if 'code' in status and status['code'] == FINISHED:
                    self.expected_mean_depth = None
                    if self.mean_depth is None or self.sample_size is None:
                        raise Exception("The anomaly data is not complete. "
                                        "Score will"
                                        " not be available")
                    else:
                        self.norm = self.normalization_factor if \
                            self.normalization_factor is not None else \
                            norm_factor(self.sample_size, self.mean_depth)

                    iforest = anomaly['model'].get('trees', [])
                    if iforest:
                        self.iforest = [
                            AnomalyTree(anomaly_tree['root'], self.fields)
                            for anomaly_tree in iforest]
                    self.top_anomalies = anomaly['model']['top_anomalies']
                else:
                    raise Exception("The anomaly isn't finished yet")
            else:
                raise Exception("Cannot create the Anomaly instance. Could not"
                                " find the 'top_anomalies' key in the"
                                " resource:\n\n%s" % list(anomaly['model'].keys()))

    def anomaly_score(self, input_data):
        """Returns the anomaly score given by the iforest

            To produce an anomaly score, we evaluate each tree in the iforest
            for its depth result (see the depth method in the AnomalyTree
            object for details). We find the average of these depths
            and calculate an expected mean depth using the `sample_size`
            and `mean_depth` parameters which come as part of the forest
            message.
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
            tree_depth, _ = tree.depth(input_data)
            depth_sum += tree_depth

        observed_mean_depth = float(depth_sum) / len(self.iforest)
        return math.pow(2, - observed_mean_depth / self.norm)

    def anomalies_filter(self, include=True):
        """Returns the LISP expression needed to filter the subset of
           top anomalies. When include is set to True, only the top
           anomalies are selected by the filter. If set to False, only the
           rest of the dataset is selected.

        """
        anomaly_filters = []
        for anomaly in self.top_anomalies:
            filter_rules = []
            row = anomaly.get('row', [])
            for index, value in enumerate(row):
                field_id = self.input_fields[index]
                if field_id in self.id_fields:
                    continue
                if value is None or value is "":
                    filter_rules.append('(missing? "%s")' % field_id)
                else:
                    if (self.fields[field_id]["optype"]
                            in ["categorical", "text"]):
                        value = json.dumps(value)
                    filter_rules.append('(= (f "%s") %s)' % (field_id, value))
            if filter_rules:
                anomaly_filters.append("(and %s)" % " ".join(filter_rules))

        anomalies_filter = " ".join(anomaly_filters)
        if include:
            if len(anomaly_filters) == 1:
                return anomalies_filter
            return "(or %s)" % anomalies_filter
        else:
            return "(not (or %s))" % anomalies_filter
