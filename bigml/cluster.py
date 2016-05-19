# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2014-2016 BigML
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
reduce the latency for each prediction and let you use your clusters
offline.

Example usage (assuming that you have previously set up the BIGML_USERNAME
and BIGML_API_KEY environment variables and that you own the cluster/id
below):

from bigml.api import BigML
from bigml.cluster import Cluster

api = BigML()

cluster = Cluster('cluster/5026965515526876630001b2')
cluster.centroid({"petal length": 3, "petal width": 1,
                  "sepal length": 1, "sepal width": 0.5})

"""
import logging
import sys
import math
import re

from bigml.api import FINISHED
from bigml.api import (BigML, get_cluster_id, get_status)
from bigml.util import cast, utf8
from bigml.centroid import Centroid
from bigml.basemodel import retrieve_resource
from bigml.basemodel import ONLY_MODEL
from bigml.model import print_distribution
from bigml.model import STORAGE
from bigml.predicate import TM_TOKENS, TM_FULL_TERM
from bigml.modelfields import ModelFields
from bigml.io import UnicodeWriter


LOGGER = logging.getLogger('BigML')

OPTIONAL_FIELDS = ['categorical', 'text', 'items', 'datetime']
CSV_STATISTICS = ['minimum', 'mean', 'median', 'maximum', 'standard_deviation',
                  'sum', 'sum_squares', 'variance']
INDENT = " " * 4
INTERCENTROID_MEASURES = [('Minimum', min),
                          ('Mean', lambda(x): sum(x)/float(len(x))),
                          ('Maximum', max)]
GLOBAL_CLUSTER_LABEL = 'Global'

def parse_terms(text, case_sensitive=True):
    """Returns the list of parsed terms

    """
    if text is None:
        return []
    expression = ur'(\b|_)([^\b_\s]+?)(\b|_)'
    pattern = re.compile(expression)
    return [match[1] if case_sensitive else match[1].lower()
            for match in re.findall(pattern, text)]


def parse_items(text, regexp):
    """Returns the list of parsed items

    """
    if text is None:
        return []
    pattern = re.compile(regexp, flags=re.U)
    return pattern.split(text)


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

        self.resource_id = None
        self.centroids = None
        self.cluster_global = None
        self.total_ss = None
        self.within_ss = None
        self.between_ss = None
        self.ratio_ss = None
        self.critical_value = None
        self.k = None
        self.scales = {}
        self.term_forms = {}
        self.tag_clouds = {}
        self.term_analysis = {}
        self.item_analysis = {}
        self.items = {}
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
        else:
            self.resource_id = get_cluster_id(cluster)
        if 'object' in cluster and isinstance(cluster['object'], dict):
            cluster = cluster['object']

        if 'clusters' in cluster and isinstance(cluster['clusters'], dict):
            status = get_status(cluster)
            if 'code' in status and status['code'] == FINISHED:
                the_clusters = cluster['clusters']
                cluster_global = the_clusters.get('global')
                clusters = the_clusters['clusters']
                self.centroids = [Centroid(centroid) for centroid in clusters]
                self.cluster_global = cluster_global
                if cluster_global:
                    self.cluster_global = Centroid(cluster_global)
                    # "global" has no "name" and "count" then we set them
                    self.cluster_global.name = GLOBAL_CLUSTER_LABEL
                    self.cluster_global.count = \
                        self.cluster_global.distance['population']
                self.total_ss = the_clusters.get('total_ss')
                self.within_ss = the_clusters.get('within_ss')
                if not self.within_ss:
                    self.within_ss = sum(centroid.distance['sum_squares'] for
                                         centroid in self.centroids)
                self.between_ss = the_clusters.get('between_ss')
                self.ratio_ss = the_clusters.get('ratio_ss')
                self.critical_value = cluster.get('critical_value', None)
                self.k = cluster.get('k')
                self.scales.update(cluster['scales'])
                self.term_forms = {}
                self.tag_clouds = {}
                self.term_analysis = {}
                fields = cluster['clusters']['fields']
                summary_fields = cluster['summary_fields']
                for field_id in summary_fields:
                    del fields[field_id]
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
                    if field['optype'] == 'items':
                        self.items[field_id] = {}
                        self.items[field_id].update(
                            dict(field['summary']['items']))
                        self.item_analysis[field_id] = {}
                        self.item_analysis[field_id].update(
                            field['item_analysis'])

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
            if (field['optype'] not in OPTIONAL_FIELDS and
                    field_id not in input_data):
                raise Exception("Failed to predict a centroid. Input"
                                " data must contain values for all "
                                "numeric fields to find a centroid.")
        # Strips affixes for numeric values and casts to the final field type
        cast(input_data, self.fields)

        unique_terms = self.get_unique_terms(input_data)
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

    @property
    def is_g_means(self):
        """Checks whether the cluster has been created using g-means

        """
        return self.critical_value is not None

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
                    if token_mode != TM_TOKENS:
                        terms.append(
                            input_data_field if case_sensitive
                            else input_data_field.lower())
                    unique_terms[field_id] = get_unique_terms(
                        terms, self.term_forms[field_id],
                        self.tag_clouds.get(field_id, []))
                else:
                    unique_terms[field_id] = input_data_field
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
                    unique_terms[field_id] = input_data_field
                del input_data[field_id]

        return unique_terms

    def centroids_distance(self, to_centroid):
        """Statistic distance information from the given centroid
           to the rest of centroids in the cluster

        """
        intercentroid_distance = []
        unique_terms = self.get_unique_terms(to_centroid.center)
        distances = []
        for centroid in self.centroids:
            if centroid.centroid_id != to_centroid.centroid_id:
                distances.append(
                    math.sqrt(
                        centroid.distance2(to_centroid.center,
                                           unique_terms,
                                           self.scales)))
        for measure, function in INTERCENTROID_MEASURES:
            result = function(distances)
            intercentroid_distance.append([measure, result])
        return intercentroid_distance

    def cluster_global_distance(self):
        """Used to populate the intercentroid distances columns in the CSV
           report. For now we don't want to compute real distance and jsut
           display "N/A"
        """
        intercentroid_distance = []
        for measure, function in INTERCENTROID_MEASURES:
            intercentroid_distance.append([measure, 'N/A'])
        return intercentroid_distance

    def centroid_features(self, centroid, field_ids):
        """Returns features defining the centroid according to the list
           of common field ids that define the centroids.

        """
        features = []
        for field_id in field_ids:
            value = centroid.center[field_id]
            if isinstance(value, basestring):
                value = value.encode('utf-8')
            features.append(value)
        return features

    def get_data_distribution(self):
        """Returns training data distribution

        """
        distribution = [[centroid.name, centroid.count] for centroid in
                        self.centroids]
        return sorted(distribution, key=lambda x: x[0])


    def print_global_distribution(self, out=sys.stdout):
        """Prints the line Global: 100% (<total> instances)

         """
        output = u""
        if self.cluster_global:
            output += (u"    %s: 100%% (%d instances)\n" % (
                self.cluster_global.name,
                self.cluster_global.count))
        out.write(output)
        out.flush()

    def print_ss_metrics(self, out=sys.stdout):
        """Prints the block of *_ss metrics from the cluster

        """
        ss_metrics = [("total_ss (Total sum of squares)", self.total_ss),
                      ("within_ss (Total within-cluster sum of the sum "
                      "of squares)", self.within_ss),
                      ("between_ss (Between sum of squares)", self.between_ss),
                      ("ratio_ss (Ratio of sum of squares)", self.ratio_ss)]
        output = u""

        for metric in ss_metrics:
            if metric[1]:
                output += (u"%s%s: %5f\n" % (INDENT, metric[0], metric[1]))

        out.write(output)
        out.flush()

    def statistics_CSV(self, file_name=None):
        """To be deprecated. See statistics_csv

        """
        self.statistics_csv(file_name=file_name)

    def statistics_csv(self, file_name=None):
        """Clusters statistic information in CSV format

        """
        rows = []
        writer = None
        field_ids = self.centroids[0].center.keys()
        headers = [u"Centroid_name"]
        headers.extend([u"%s" % self.fields[field_id]["name"]
                        for field_id in field_ids])
        headers.extend([u"Instances"])
        intercentroids = False
        header_complete = False


        centroids_list = sorted(self.centroids, key=lambda x: x.name)
        for centroid in centroids_list:
            row = [centroid.name]
            row.extend(self.centroid_features(centroid, field_ids))
            row.append(centroid.count)
            if len(self.centroids) > 1:
                for measure, result in self.centroids_distance(centroid):
                    if not intercentroids:
                        headers.append(u"%s intercentroid distance" % \
                            measure.title())
                    row.append(result)
                intercentroids = True
            for measure, result in centroid.distance.items():
                if measure in CSV_STATISTICS:
                    if not header_complete:
                        headers.append(u"Distance %s" %
                                       measure.lower().replace("_", " "))
                    row.append(result)
            if not header_complete:
                rows.append(headers)
                header_complete = True
            rows.append(row)

        if self.cluster_global:
            row = [u"%s" % self.cluster_global.name]
            row.extend(self.centroid_features(self.cluster_global, field_ids))
            row.append(self.cluster_global.count)
            if len(self.centroids) > 1:
                for measure, result in self.cluster_global_distance():
                    row.append(result)
            for measure, result in self.cluster_global.distance.items():
                if measure in CSV_STATISTICS:
                    row.append(result)
            # header is already in rows then insert cluster_global after it
            rows.insert(1, row)

        if file_name is None:
            return rows
        with UnicodeWriter(file_name) as writer:
            for row in rows:
                writer.writerow([item if not isinstance(item, basestring)
                                 else item.encode("utf-8") for item in row])

    def summarize(self, out=sys.stdout):
        """Prints a summary of the cluster info

        """
        report_header = ''
        if self.is_g_means:
            report_header = \
                u'G-means Cluster (critical_value=%d)' % self.critical_value
        else:
            report_header = u'K-means Cluster (k=%d)' % self.k

        out.write(report_header + ' with %d centroids\n\n' %
                  len(self.centroids))

        out.write(u"Data distribution:\n")
        # "Global" is set as first entry
        self.print_global_distribution(out=out)
        print_distribution(self.get_data_distribution(), out=out)
        out.write(u"\n")
        centroids_list = [self.cluster_global] if self.cluster_global else []
        centroids_list.extend(sorted(self.centroids, key=lambda x: x.name))

        out.write(u"Cluster metrics:\n")
        self.print_ss_metrics(out=out)
        out.write(u"\n")


        out.write(u"Centroids:\n")
        for centroid in centroids_list:
            out.write(utf8(u"\n%s%s: " % (INDENT, centroid.name)))
            connector = ""
            for field_id, value in centroid.center.items():
                if isinstance(value, basestring):
                    value = u"\"%s\"" % value
                out.write(utf8(u"%s%s: %s" % (connector,
                                              self.fields[field_id]['name'],
                                              value)))
                connector = ", "
        out.write(u"\n\n")

        out.write(u"Distance distribution:\n\n")
        for centroid in centroids_list:
            centroid.print_statistics(out=out)
        out.write(u"\n")

        if len(self.centroids) > 1:
            out.write(u"Intercentroid distance:\n\n")
            centroids_list = (centroids_list[1:] if self.cluster_global else
                              centroids_list)
            for centroid in centroids_list:
                out.write(utf8(u"%sTo centroid: %s\n" % (INDENT,
                                                         centroid.name)))
                for measure, result in self.centroids_distance(centroid):
                    out.write(u"%s%s: %s\n" % (INDENT * 2, measure, result))
                out.write(u"\n")
