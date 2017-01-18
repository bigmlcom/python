# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2014-2017 BigML
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

This module defines an Anomaly Detector to score anomlies in a dataset locally
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
from bigml.api import (BigML, get_anomaly_id, get_status)
from bigml.util import cast
from bigml.basemodel import retrieve_resource
from bigml.basemodel import ONLY_MODEL
from bigml.model import STORAGE
from bigml.modelfields import ModelFields, check_model_fields
from bigml.anomalytree import AnomalyTree


LOGGER = logging.getLogger('BigML')

DEPTH_FACTOR = 0.5772156649


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


        # checks whether the information needed for local predictions is in
        # the first argument
        if isinstance(anomaly, dict) and \
                not check_model_fields(anomaly):
            # if the fields used by the anomaly detector are not
            # available, use only ID to retrieve it again
            anomaly = get_anomaly_id(anomaly)
            self.resource_id = anomaly

        if not (isinstance(anomaly, dict) and 'resource' in anomaly and
                anomaly['resource'] is not None):
            if api is None:
                api = BigML(storage=STORAGE)
            self.resource_id = get_anomaly_id(anomaly)
            if self.resource_id is None:
                raise Exception(api.error_message(anomaly,
                                                  resource_type='anomaly',
                                                  method='get'))
            query_string = ONLY_MODEL
            anomaly = retrieve_resource(api, self.resource_id,
                                        query_string=query_string)
        else:
            self.resource_id = get_anomaly_id(anomaly)
        if 'object' in anomaly and isinstance(anomaly['object'], dict):
            anomaly = anomaly['object']
            self.sample_size = anomaly.get('sample_size')
            self.input_fields = anomaly.get('input_fields')
            self.id_fields = anomaly.get('id_fields', [])
        if 'model' in anomaly and isinstance(anomaly['model'], dict):
            ModelFields.__init__(self, anomaly['model'].get('fields'))
            if ('top_anomalies' in anomaly['model'] and
                    isinstance(anomaly['model']['top_anomalies'], list)):
                self.mean_depth = anomaly['model'].get('mean_depth')
                status = get_status(anomaly)
                if 'code' in status and status['code'] == FINISHED:
                    self.expected_mean_depth = None
                    if self.mean_depth is None or self.sample_size is None:
                        raise Exception("The anomaly data is not complete. "
                                        "Score will"
                                        " not be available")
                    else:
                        default_depth = (
                            2 * (DEPTH_FACTOR + \
                            math.log(self.sample_size - 1) - \
                            (float(self.sample_size - 1) / self.sample_size)))
                        self.expected_mean_depth = min(self.mean_depth,
                                                       default_depth)
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
                                " resource:\n\n%s" % anomaly['model'].keys())

    def anomaly_score(self, input_data, by_name=True):
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

        # Checks and cleans input_data leaving the fields used in the model
        input_data = self.filter_input_data(input_data, by_name=by_name)

        # Strips affixes for numeric values and casts to the final field type
        cast(input_data, self.fields)

        depth_sum = 0
        if self.iforest is None:
            raise Exception("We could not find the iforest information to "
                            "compute the anomaly score. Please, rebuild your "
                            "Anomaly object from a complete anomaly detector "
                            "resource.")
        for tree in self.iforest:
            depth_sum += tree.depth(input_data)[0]
        observed_mean_depth = float(depth_sum) / len(self.iforest)
        return math.pow(2, - observed_mean_depth / self.expected_mean_depth)

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
