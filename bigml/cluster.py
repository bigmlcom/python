# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2014 BigML
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

"""A local Predictive Cluster.

This module defines a Cluster to make predictions (centroids) locally or
embedded into your application without needing to send requests to
BigML.io.

This module cannot only save you a few credits, but also enormously
reduce the latency for each prediction and let you use your models
offline.

Example usage (assuming that you have previously set up the BIGML_USERNAME
and BIGML_API_KEY environment variables and that you own the model/id below):

from bigml.api import BigML
from bigml.cluster import Cluster

api = BigML()

cluster = Cluster('cluster/5026965515526876630001b2')
cluster.predict({"petal length": 3, "petal width": 1,
                 "sepal length": 1, "sepal width": 0.5})

"""
import logging
LOGGER = logging.getLogger('BigML')

import math
import re

from bigml.api import FINISHED
from bigml.api import (BigML, get_cluster_id, get_status)
from bigml.util import cast
from bigml.centroid import Centroid
from bigml.basemodel import retrieve_resource
from bigml.basemodel import ONLY_MODEL
from bigml.model import STORAGE
from bigml.predicate import TM_TOKENS, TM_FULL_TERM
from bigml.modelfields import ModelFields


OPTIONAL_FIELDS = ['categorical', 'text']


def parse_terms(text, case_sensitive=True):
    """Returns the list of parsed terms

    """
    if text is None:
        return []
    expression = ur'(\b|_)([^\b_\s]+?)(\b|_)'
    pattern = re.compile(expression)
    return map(lambda x: x[1] if case_sensitive else x[1].lower(),
               re.findall(pattern, text))


def get_unique_terms(terms, term_forms, tag_cloud):
    """Extracts the unique terms that occur in one of the alternative forms in
       term_forms or in the tag cloud.

    """
    extend_forms = {}
    tag_cloud = tag_cloud.keys()
    for term, forms in term_forms.items():
        for form in forms:
            extend_forms[form] = term
        extend_forms[term] = term
    terms_set = set()
    for term in terms:
        if term in tag_cloud:
            terms_set.add(term)
        elif term in extend_forms:
            terms_set.add(extend_forms[term])
    return list(terms_set)


class Cluster(ModelFields):
    """ A lightweight wrapper around a cluster model.

    Uses a BigML remote cluster model to build a local version that can be used
    to generate centroid predictions locally.

    """

    def __init__(self, cluster, api=None):

        if not (isinstance(cluster, dict) and 'resource' in cluster and
                cluster['resource'] is not None):
            if api is None:
                api = BigML(storage=STORAGE)
            self.resource_id = get_cluster_id(cluster)
            if self.resource_id is None:
                raise Exception(api.error_message(cluster,
                                                  resource_type='cluster',
                                                  method='get'))
            query_string = ONLY_MODEL
            cluster = retrieve_resource(api, self.resource_id,
                                        query_string=query_string)
        if 'object' in cluster and isinstance(cluster['object'], dict):
            cluster = cluster['object']

        if 'clusters' in cluster and isinstance(cluster['clusters'], dict):
            status = get_status(cluster)
            if 'code' in status and status['code'] == FINISHED:
                clusters = cluster['clusters']['clusters']
                self.centroids = [Centroid(centroid) for centroid in clusters]
                self.scales = {}
                self.scales.update(cluster['scales'])
                self.term_forms = {}
                self.tag_clouds = {}
                self.term_analysis = {}
                fields = cluster['clusters']['fields']
                for field_id, field in fields.items():
                    if field['optype'] == 'text':

                        self.term_forms[field_id] = {}
                        self.term_forms[field_id].update(field[
                            'summary']['term_forms'])
                        self.tag_clouds[field_id] = {}
                        self.tag_clouds[field_id].update(field[
                            'summary']['tag_cloud'])
                        self.term_analysis[field_id] = {}
                        self.term_analysis[field_id].update(
                            field['term_analysis'])
                ModelFields.__init__(self, fields)
                if not all([field_id in self.fields for
                            field_id in self.scales]):
                    raise Exception("Some fields are missing"
                                    " to generate a local cluster."
                                    " Please, provide a cluster with"
                                    " the complete list of fields.")
            else:
                raise Exception("The cluster isn't finished yet")
        else:
            raise Exception("Cannot create the Cluster instance. Could not"
                            " find the 'clusters' key in the resource:\n\n%s" %
                            cluster)

    def centroid(self, input_data, by_name=True):
        """Returns the id of the nearest centroid

        """
        # Checks and cleans input_data leaving the fields used in the model
        input_data = self.filter_input_data(input_data, by_name=by_name)

        # Checks that all numeric fields are present in input data
        for field_id, field in self.fields.items():
            if (not field['optype'] in OPTIONAL_FIELDS and
                    not field_id in input_data):
                raise Exception("Failed to predict a centroid. Input"
                                " data must contain values for all "
                                "numeric fields to find a centroid.")
        # Strips affixes for numeric values and casts to the final field type
        cast(input_data, self.fields)

        unique_terms = {}
        for field_id in self.term_forms:
            if field_id in input_data:
                case_sensitive = self.term_analysis[field_id].get(
                    'case_sensitive', True)
                token_mode = self.term_analysis[field_id].get(
                    'token_mode', 'all')
                input_data_field = input_data.get(field_id, '')
                if token_mode != TM_FULL_TERM:
                    terms = parse_terms(input_data_field,
                                        case_sensitive=case_sensitive)
                else:
                    terms = []
                if token_mode != TM_TOKENS:
                    terms.append(input_data_field if case_sensitive else
                                 input_data_field.lower())
                unique_terms[field_id] = get_unique_terms(
                    terms, self.term_forms[field_id],
                    self.tag_clouds.get(field_id, []))
                del input_data[field_id]
        nearest = {'centroid_id': None, 'centroid_name': None,
                   'distance': float('inf')}
        for centroid in self.centroids:
            distance2 = centroid.distance2(input_data, unique_terms,
                                           self.scales,
                                           stop_distance2=nearest['distance'])
            if distance2 is not None:
                nearest = {'centroid_id': centroid.centroid_id,
                           'centroid_name': centroid.name,
                           'distance': distance2}
        nearest['distance'] = math.sqrt(nearest['distance'])
        return nearest
