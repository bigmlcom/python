# -*- coding: utf-8 -*-
#
# Copyright 2014-2022 BigML
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

This module can help you enormously to
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
import csv
import codecs


from bigml.api import FINISHED
from bigml.api import get_status, get_api_connection, get_cluster_id
from bigml.util import cast, utf8, NUMERIC, use_cache, load, dump, dumps, \
    get_data_format, get_formatted_data, format_data
from bigml.centroid import Centroid
from bigml.basemodel import get_resource_dict
from bigml.generators.model import print_distribution
from bigml.predicate import TM_TOKENS, TM_FULL_TERM
from bigml.modelfields import ModelFields
from bigml.io import UnicodeWriter
from bigml.constants import OUT_NEW_FIELDS, OUT_NEW_HEADERS, INTERNAL


LOGGER = logging.getLogger('BigML')

CSV_STATISTICS = ['minimum', 'mean', 'median', 'maximum', 'standard_deviation',
                  'sum', 'sum_squares', 'variance']
INDENT = " " * 4
INTERCENTROID_MEASURES = [('Minimum', min),
                          ('Mean', lambda x: sum(x)/float(len(x))),
                          ('Maximum', max)]
GLOBAL_CLUSTER_LABEL = 'Global'

DFT_OUTPUTS = ["centroid_name", "distance"]


def parse_terms(text, case_sensitive=True):
    """Returns the list of parsed terms

    """
    if text is None:
        return []
    expression = r'(\b|_)([^\b_\s]+?)(\b|_)'
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
    for term, forms in list(term_forms.items()):
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


def cluster_global_distance():
    """Used to populate the intercentroid distances columns in the CSV
       report. For now we don't want to compute real distance and just
       display "N/A"
    """
    intercentroid_distance = []
    for measure, _ in INTERCENTROID_MEASURES:
        intercentroid_distance.append([measure, 'N/A'])
    return intercentroid_distance


def centroid_features(centroid, field_ids, encode=True):
    """Returns features defining the centroid according to the list
       of common field ids that define the centroids.

    """
    features = []
    for field_id in field_ids:
        value = centroid.center[field_id]
        if isinstance(value, str) and encode:
            value = utf8(value)
        features.append(value)
    return features


class Cluster(ModelFields):
    """ A lightweight wrapper around a cluster model.

    Uses a BigML remote cluster model to build a local version that can be used
    to generate centroid predictions locally.

    """

    def __init__(self, cluster, api=None, cache_get=None):

        self.api = get_api_connection(api)
        self.centroids = None
        if use_cache(cache_get):
            # using a cache to store the cluster attributes
            self.__dict__ = load(get_cluster_id(cluster), cache_get)

            for index, centroid in enumerate(self.centroids):
                self.centroids[index] = Centroid(centroid)
            self.cluster_global = Centroid(self.cluster_global)
            return

        self.resource_id = None
        self.name = None
        self.description = None
        self.dataset_id = None
        self.cluster_global = None
        self.total_ss = None
        self.within_ss = None
        self.between_ss = None
        self.ratio_ss = None
        self.critical_value = None
        self.input_fields = []
        self.default_numeric_value = None
        self.summary_fields = []
        self.default_numeric_value = None
        self.k = None
        self.summary_fields = []
        self.scales = {}
        self.term_forms = {}
        self.tag_clouds = {}
        self.term_analysis = {}
        self.item_analysis = {}
        self.items = {}
        self.datasets = {}

        self.resource_id, cluster = get_resource_dict( \
            cluster, "cluster", api=self.api)

        if 'object' in cluster and isinstance(cluster['object'], dict):
            cluster = cluster['object']
            self.dataset_id = cluster.get('dataset')
            self.name = cluster.get("name")
            self.description = cluster.get("description")
        if 'clusters' in cluster and isinstance(cluster['clusters'], dict):
            status = get_status(cluster)
            if 'code' in status and status['code'] == FINISHED:
                self.default_numeric_value = cluster.get( \
                    "default_numeric_value")
                self.summary_fields = cluster.get("summary_fields", [])
                self.input_fields = cluster.get("input_fields", [])
                self.datasets = cluster.get("cluster_datasets", {})
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
                    try:
                        del fields[field_id]
                    except KeyError:
                        # clusters retrieved from API will only contain
                        # model fields
                        pass
                missing_tokens = cluster['clusters'].get('missing_tokens')
                ModelFields.__init__(self, fields,
                                     missing_tokens=missing_tokens)
                if not all(field_id in self.fields for
                            field_id in self.scales):
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

    def centroid(self, input_data):
        """Returns the id of the nearest centroid

        """
        clean_input_data, unique_terms = self._prepare_for_distance( \
            input_data)
        nearest = {'centroid_id': None, 'centroid_name': None,
                   'distance': float('inf')}
        for centroid in self.centroids:
            distance2 = centroid.distance2(clean_input_data, unique_terms,
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

    def fill_numeric_defaults(self, input_data):
        """Checks whether input data is missing a numeric field and
        fills it with the average quantity set in default_numeric_value

        """

        for field_id, field in self.fields.items():
            if (field_id not in self.summary_fields and \
                    field['optype'] == NUMERIC and
                    field_id not in input_data):
                if self.default_numeric_value is None:
                    raise Exception("Missing values in input data. Input"
                                    " data must contain values for all "
                                    "numeric fields to compute a distance.")
                default_value = 0 if self.default_numeric_value == "zero" \
                    else field['summary'].get(self.default_numeric_value)
                input_data[field_id] = default_value
        return input_data

    def get_unique_terms(self, input_data):
        """Parses the input data to find the list of unique terms in the
           tag cloud

        """
        unique_terms = {}
        for field_id in self.term_forms:
            if field_id in input_data:
                input_data_field = input_data.get(field_id, '')
                if isinstance(input_data_field, str):
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
                        terms, self.fields[field_id]["summary"]["term_forms"],
                        self.tag_clouds.get(field_id, []))
                else:
                    unique_terms[field_id] = input_data_field
                del input_data[field_id]
        # the same for items fields
        #pylint: disable=locally-disabled,consider-using-dict-items
        for field_id in self.item_analysis:
            if field_id in input_data:
                input_data_field = input_data.get(field_id, '')
                if isinstance(input_data_field, str):
                    # parsing the items in input_data
                    separator = self.item_analysis[field_id].get(
                        'separator', ' ')
                    regexp = self.item_analysis[field_id].get(
                        'separator_regexp')
                    if regexp is None:
                        regexp = r'%s' % re.escape(separator)
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

    def _prepare_for_distance(self, input_data):
        """Prepares the fields to be able to compute the distance2

        """
        # Checks and cleans input_data leaving the fields used in the model
        # and adding default numeric values if set
        norm_input_data = self.filter_input_data(input_data)
        # Strips affixes for numeric values and casts to the final field type
        cast(norm_input_data, self.fields)

        unique_terms = self.get_unique_terms(norm_input_data)

        return norm_input_data, unique_terms

    def distances2_to_point(self, reference_point,
                            list_of_points):
        """Computes the cluster square of the distance to an arbitrary
        reference point for a list of points.
        reference_point: (dict) The field values for the point used as
                                reference
        list_of_points: (dict|Centroid) The field values or a Centroid object
                                        which contains these values


        """
        # Checks and cleans input_data leaving the fields used in the model
        reference_point, text_coords = self._prepare_for_distance( \
            reference_point)
        reference_point.update(text_coords)
        # mimic centroid structure to use it in distance computation
        point_info = {"center": reference_point}
        reference = Centroid(point_info)
        distances = []
        for point in list_of_points:
            centroid_id = None
            if isinstance(point, Centroid):
                centroid_id = point.centroid_id
                point = point.center
            clean_point, unique_terms = self._prepare_for_distance( \
                point)
            if clean_point != reference_point:
                result = {"data": point, "distance": reference.distance2( \
                    clean_point, unique_terms, self.scales)}
                if centroid_id is not None:
                    result.update({"centroid_id": centroid_id})
                distances.append(result)
        return distances

    def points_in_cluster(self, centroid_id):
        """Returns the list of data points that fall in one cluster.

        """

        cluster_datasets = self.datasets
        centroid_dataset = cluster_datasets.get(centroid_id)
        if centroid_dataset in [None, ""]:
            centroid_dataset = self.api.create_dataset( \
                self.resource_id, {"centroid": centroid_id})
            self.datasets[centroid_id] = centroid_dataset[ \
                "resource"].replace("dataset/", "")
            self.api.ok(centroid_dataset, raise_on_error=True)
        else:
            centroid_dataset = self.api.check_resource( \
                "dataset/%s" % centroid_dataset)
        # download dataset to compute local predictions
        downloaded_data = self.api.download_dataset( \
            centroid_dataset["resource"])
        text_reader = codecs.getreader("utf-8")
        downloaded_data = text_reader(downloaded_data)
        reader = csv.DictReader(downloaded_data)
        points = []
        for row in reader:
            points.append(row)
        return points

    def closest_in_cluster(self, reference_point,
                           number_of_points=None,
                           centroid_id=None):
        """Computes the list of data points closer to a reference point.
        If no centroid_id information is provided, the points are chosen
        from the same cluster as the reference point.
        The points are returned in a list, sorted according
        to their distance to the reference point. The number_of_points
        parameter can be set to truncate the list to a maximum number of
        results. The response is a dictionary that contains the
        centroid id of the cluster plus the list of points
        """
        if centroid_id is not None and centroid_id not in \
                [centroid.centroid_id for centroid in self.centroids]:
            raise AttributeError( \
                "Failed to find the provided centroid_id: %s" % centroid_id)
        if centroid_id is None:
            # finding the reference point cluster's centroid
            centroid_info = self.centroid(reference_point)
            centroid_id = centroid_info["centroid_id"]
        # reading the points that fall in the same cluster
        points = self.points_in_cluster(centroid_id)
        # computing distance to reference point
        points = self.distances2_to_point(reference_point, points)
        points = sorted(points, key=lambda x: x["distance"])
        if number_of_points is not None:
            points = points[:number_of_points]
        for point in points:
            point["distance"] = math.sqrt(point["distance"])
        return {"centroid_id": centroid_id, "reference": reference_point,
                "closest": points}

    def sorted_centroids(self, reference_point):
        """ Gives the list of centroids sorted according to its distance to
        an arbitrary reference point.

        """
        close_centroids = self.distances2_to_point( \
            reference_point, self.centroids)
        for centroid in close_centroids:
            centroid["distance"] = math.sqrt(centroid["distance"])
            centroid["center"] = centroid["data"]
            del centroid["data"]
        return {"reference": reference_point,
                "centroids": sorted(close_centroids,
                                    key=lambda x: x["distance"])}

    def get_data_distribution(self):
        """Returns training data distribution

        """
        distribution = [[centroid.name, centroid.count] for centroid in
                        self.centroids]
        return sorted(distribution, key=lambda x: x[0])


    def print_global_distribution(self, out=sys.stdout):
        """Prints the line Global: 100% (<total> instances)

         """
        output = ""
        if self.cluster_global:
            output += ("    %s: 100%% (%d instances)\n" % (
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
        output = ""

        for metric in ss_metrics:
            if metric[1]:
                output += ("%s%s: %5f\n" % (INDENT, metric[0], metric[1]))

        out.write(output)
        out.flush()

    def statistics_csv(self, file_name=None):
        """Clusters statistic information in CSV format

        """
        rows = []
        writer = None
        field_ids = self.centroids[0].center.keys()
        headers = ["Centroid_name"]
        headers.extend(["%s" % self.fields[field_id]["name"]
                        for field_id in field_ids])
        headers.extend(["Instances"])
        intercentroids = False
        header_complete = False


        centroids_list = sorted(self.centroids, key=lambda x: x.name)
        for centroid in centroids_list:
            row = [centroid.name]
            row.extend(centroid_features(centroid, field_ids,
                                         encode=False))
            row.append(centroid.count)
            if len(self.centroids) > 1:
                for measure, result in self.centroids_distance(centroid):
                    if not intercentroids:
                        headers.append("%s intercentroid distance" % \
                            measure.title())
                    row.append(result)
                intercentroids = True
            for measure, result in centroid.distance.items():
                if measure in CSV_STATISTICS:
                    if not header_complete:
                        headers.append("Distance %s" %
                                       measure.lower().replace("_", " "))
                    row.append(result)
            if not header_complete:
                rows.append(headers)
                header_complete = True
            rows.append(row)

        if self.cluster_global:
            row = ["%s" % self.cluster_global.name]
            row.extend(centroid_features(self.cluster_global, field_ids,
                                         encode=False))
            row.append(self.cluster_global.count)
            if len(self.centroids) > 1:
                for measure, result in cluster_global_distance():
                    row.append(result)
            for measure, result in self.cluster_global.distance.items():
                if measure in CSV_STATISTICS:
                    row.append(result)
            # header is already in rows then insert cluster_global after it
            rows.insert(1, row)

        if file_name is None:
            return rows
        with UnicodeWriter(file_name) as writer:
            writer.writerows(rows)
        return file_name

    def summarize(self, out=sys.stdout):
        """Prints a summary of the cluster info

        """
        report_header = ''
        if self.is_g_means:
            report_header = \
                'G-means Cluster (critical_value=%d)' % self.critical_value
        else:
            report_header = 'K-means Cluster (k=%d)' % self.k

        out.write(report_header + ' with %d centroids\n\n' %
                  len(self.centroids))

        out.write("Data distribution:\n")
        # "Global" is set as first entry
        self.print_global_distribution(out=out)
        print_distribution(self.get_data_distribution(), out=out)
        out.write("\n")
        centroids_list = [self.cluster_global] if self.cluster_global else []
        centroids_list.extend(sorted(self.centroids, key=lambda x: x.name))

        out.write("Cluster metrics:\n")
        self.print_ss_metrics(out=out)
        out.write("\n")


        out.write("Centroids:\n")
        for centroid in centroids_list:
            out.write(utf8("\n%s%s: " % (INDENT, centroid.name)))
            connector = ""
            for field_id, value in centroid.center.items():
                if isinstance(value, str):
                    value = "\"%s\"" % value
                out.write(utf8("%s%s: %s" % (connector,
                                             self.fields[field_id]['name'],
                                             value)))
                connector = ", "
        out.write("\n\n")

        out.write("Distance distribution:\n\n")
        for centroid in centroids_list:
            centroid.print_statistics(out=out)
        out.write("\n")

        if len(self.centroids) > 1:
            out.write("Intercentroid distance:\n\n")
            centroids_list = (centroids_list[1:] if self.cluster_global else
                              centroids_list)
            for centroid in centroids_list:
                out.write(utf8("%sTo centroid: %s\n" % (INDENT,
                                                        centroid.name)))
                for measure, result in self.centroids_distance(centroid):
                    out.write("%s%s: %s\n" % (INDENT * 2, measure, result))
                out.write("\n")

    def batch_predict(self, input_data_list, outputs=None, **kwargs):
        """Creates a batch centroid for a list of inputs using the local
        cluster model. Allows to define some output settings to
        decide the fields to be added to the input_data (centroid_name,
        distance, etc.) and the name that we want to assign to these new
        fields. The outputs argument accepts a dictionary with keys
        "output_fields", to contain a list of the prediction properties to add
        (["centroid_name", "distance"] by default) and "output_headers", to
        contain a list of the headers to be used when adding them (identical
        to "output_fields" list, by default).

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
        new_fields = outputs.get(OUT_NEW_FIELDS, DFT_OUTPUTS)
        new_headers = outputs.get(OUT_NEW_HEADERS, new_fields)
        if len(new_fields) > len(new_headers):
            new_headers.expand(new_fields[len(new_headers):])
        else:
            new_headers = new_headers[0: len(new_fields)]
        data_format = get_data_format(input_data_list)
        inner_data_list = get_formatted_data(input_data_list, INTERNAL)
        for input_data in inner_data_list:
            prediction = self.centroid(input_data, **kwargs)
            for index, key in enumerate(new_fields):
                input_data[new_headers[index]] = prediction[key]
        if data_format != INTERNAL:
            return format_data(inner_data_list, out_format=data_format)
        return inner_data_list

    def dump(self, output=None, cache_set=None):
        """Uses msgpack to serialize the resource object
        If cache_set is filled with a cache set method, the method is called

        """
        self_vars = vars(self)
        for index, centroid in enumerate(self_vars["centroids"]):
            self_vars["centroids"][index] = vars(centroid)
        self_vars["cluster_global"] = vars(self_vars["cluster_global"])
        del self_vars["api"]
        dump(self_vars, output=output, cache_set=cache_set)

    def dumps(self):
        """Uses msgpack to serialize the resource object to a string

        """
        self_vars = vars(self)
        for index, centroid in enumerate(self_vars["centroids"]):
            self_vars["centroids"][index] = vars(centroid)
        self_vars["cluster_global"] = vars(self_vars["cluster_global"])
        del self_vars["api"]
        dumps(self_vars)
