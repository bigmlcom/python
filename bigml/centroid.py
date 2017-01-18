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

"""Centroid structure for the BigML local Cluster

This module defines an auxiliary Centroid predicate structure that is used
in the cluster.

"""

import math
import sys

INDENT = " " * 4
STATISTIC_MEASURES = [
    'Minimum', 'Mean', 'Median', 'Maximum', 'Standard deviation', 'Sum',
    'Sum squares', 'Variance']


def cosine_distance2(terms, centroid_terms, scale):
    """Returns the distance defined by cosine similarity

    """
    # Centroid values for the field can be an empty list.
    # Then the distance for an empty input is 1
    # (before applying the scale factor).
    if not terms and not centroid_terms:
        return 0
    if not terms or not centroid_terms:
        return scale ** 2
    input_count = 0
    for term in centroid_terms:
        if term in terms:
            input_count += 1
    cosine_similarity = input_count / math.sqrt(
        len(terms) * len(centroid_terms))
    similarity_distance = scale * (1 - cosine_similarity)
    return similarity_distance ** 2


class Centroid(object):
    """A Centroid.

    """
    def __init__(self, centroid_info):
        self.center = centroid_info.get('center', {})
        self.count = centroid_info.get('count', 0)
        self.centroid_id = centroid_info.get('id', None)
        self.name = centroid_info.get('name', None)
        self.distance = centroid_info.get('distance', {})

    def distance2(self, input_data, term_sets, scales, stop_distance2=None):
        """Squared Distance from the given input data to the centroid

        """
        distance2 = 0.0
        for field_id, value in self.center.items():
            if isinstance(value, list):
                # text field
                terms = ([] if field_id not in term_sets else
                         term_sets[field_id])
                distance2 += cosine_distance2(terms, value, scales[field_id])
            elif isinstance(value, basestring):
                if field_id not in input_data or input_data[field_id] != value:
                    distance2 += 1 * scales[field_id] ** 2
            else:
                distance2 += ((input_data[field_id] - value) *
                              scales[field_id]) ** 2
            if stop_distance2 is not None and distance2 >= stop_distance2:
                return None
        return distance2

    def print_statistics(self, out=sys.stdout):
        """Print the statistics for the training data clustered around the
           centroid

        """
        out.write(u"%s%s:\n" % (INDENT, self.name))
        literal = u"%s%s: %s\n"
        for measure_title in STATISTIC_MEASURES:
            measure = measure_title.lower().replace(" ", "_")
            out.write(literal % (INDENT * 2, measure_title,
                                 self.distance[measure]))
        out.write("\n")
