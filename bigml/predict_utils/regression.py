# -*- coding: utf-8 -*-
#
# Copyright 2020-2021 BigML
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

"""Predict utilities for regressions

"""
import numbers
import math


from scipy import stats

from bigml.predict_utils.common import last_prediction_predict, \
    proportional_predict, extract_distribution
from bigml.predicate_utils.utils import pack_predicate
from bigml.util import PRECISION
from bigml.prediction import Prediction
from bigml.multivote import BINS_LIMIT, merge_bins


OFFSETS = { \
    "False": {"id": 0,
              "output": 1,
              "count": 2,
              "confidence": 3,
              "distribution": 4,
              "distribution_unit": 5,
              "max_bins": 6,
              "max": 7,
              "min": 8,
              "median": 9,
              "children#": 10,
              "children": 11},
    "True": {"id": 0,
             "output": 1,
             "count": 2,
             "confidence": 3,
             "distribution": 4,
             "distribution_unit": 5,
             "max_bins": 6,
             "max": 7,
             "min": 8,
             "median": 9,
             "wdistribution": 10,
             "wdistribution_unit": 11,
             "weight": 12,
             "children#": 13,
             "children": 14}}


def dist_median(distribution, count):
    """Returns the median value for a distribution

    """
    counter = 0
    previous_value = None
    for value, instances in distribution:
        counter += instances
        if counter > count / 2.0:
            if (not count % 2 and (counter - 1) == (count / 2) and
                    previous_value is not None):
                return (value + previous_value) / 2.0
            return value
        previous_value = value
    return None


def mean(distribution):
    """Computes the mean of a distribution in the [[point, instances]] syntax

    """
    addition = 0.0
    count = 0.0
    for point, instances in distribution:
        addition += point * instances
        count += instances
    if count > 0:
        return addition / count
    return float('nan')


def unbiased_sample_variance(distribution, distribution_mean=None):
    """Computes the standard deviation of a distribution in the
       [[point, instances]] syntax

    """
    addition = 0.0
    count = 0.0
    if (distribution_mean is None or not
            isinstance(distribution_mean, numbers.Number)):
        distribution_mean = mean(distribution)
    for point, instances in distribution:
        addition += ((point - distribution_mean) ** 2) * instances
        count += instances
    if count > 1:
        return addition / (count - 1)
    return float('nan')


def regression_error(distribution_variance, population, r_z=1.96):
    """Computes the variance error

    """
    if population > 0:
        chi_distribution = stats.chi2(population)
        ppf = chi_distribution.ppf(1 - math.erf(r_z / math.sqrt(2)))
        if ppf != 0:
            error = distribution_variance * (population - 1) / ppf
            error = error * ((math.sqrt(population) + r_z) ** 2)
            return math.sqrt(error / population)
    return float('nan')


def build_regression_tree(node_dict, node=None, distribution=None,
                          weighted=False):
    """Builds a compressed version of the tree structure as an list of
    lists. Starting from the root node, that is represented by a list:
        [weight, #predicates, op-code, field, value, term, missing...]

    And each child is represented by a list whose elements are:
        [#children, id, output, count, confidence, output, distribution,
         distribution_unit, max_bins, max. min, median,
         wdistribution, wdistribution_unit, children_nodes_list*]
    """
    predicate = node_dict.get('predicate', True)
    outer = node if node else list(pack_predicate(predicate))
    outer.append(node_dict.get("id"))
    outer.append(node_dict.get("output"))
    outer.append(node_dict.get("count"))
    outer.append(node_dict.get("confidence"))
    distribution = distribution if distribution is not None else \
        node_dict.get("objective_summary")
    distribution_unit, distribution = extract_distribution(distribution)
    outer.append(distribution)
    outer.append(distribution_unit)
    node_median = None
    summary = node_dict.get("summary", {})
    if "summary" in node_dict:
        node_median = summary.get('median')
    if not node_median:
        node_median = dist_median(distribution, node_dict.get("count"))
    node_max = summary.get('maximum') or \
        max([value for [value, _] in distribution])
    node_min = summary.get('minimum') or \
        min([value for [value, _] in distribution])
    node_max_bins = max(node_dict.get('max_bins', 0),
                        len(distribution))
    outer.append(node_max_bins)
    outer.append(node_max)
    outer.append(node_min)
    outer.append(node_median)
    if weighted:
        wdistribution_unit, wdistribution = extract_distribution( \
             node_dict.get("weighted_objective_summary"))
        outer.append(wdistribution)
        outer.append(wdistribution_unit)
        outer.append(node_dict.get("weight"))
    children = node_dict.get("children", [])
    outer.append(len(children))
    children_list = list()
    for child in children:
        predicate = child.get('predicate')
        inner = pack_predicate(predicate)
        build_regression_tree(child, node=inner, weighted=weighted)
        children_list.append(inner)
    if children_list:
        outer.append(children_list)

    return outer


def regression_proportional_predict(tree, weighted, fields, input_data):
    """Proportional prediction for regressions

    """

    offset = OFFSETS[str(weighted)]
    (final_distribution, d_min, d_max, last_node, population,
     parent_node, path) = proportional_predict( \
        tree, offset, fields, input_data, path=None)
    # singular case:
    # when the prediction is the one given in a 1-instance node
    if len(list(final_distribution.items())) == 1:
        prediction, instances = list(final_distribution.items())[0]
        if instances == 1:
            return Prediction( \
                last_node[offset["output"]],
                path,
                last_node[offset["confidence"]],
                distribution=last_node[offset["distribution"]] \
                    if not weighted else \
                    last_node[offset["wdistribution"]],
                count=instances,
                median=last_node[offset["median"]],
                distribution_unit=last_node[offset["distribution_unit"]],
                children=[] if last_node[offset["children#"]] == 0 else \
                    last_node[offset["children"]],
                d_min=last_node[offset["min"]],
                d_max=last_node[offset["max"]])
    # when there's more instances, sort elements by their mean
    distribution = [list(element) for element in
                    sorted(list(final_distribution.items()),
                           key=lambda x: x[0])]
    distribution_unit = ('bins' if len(distribution) > BINS_LIMIT
                         else 'counts')
    distribution = merge_bins(distribution, BINS_LIMIT)
    total_instances = sum([instances
                           for _, instances in distribution])
    if len(distribution) == 1:
        # where there's only one bin, there will be no error, but
        # we use a correction derived from the parent's error
        prediction = distribution[0][0]
        if total_instances < 2:
            total_instances = 1
        try:
            # some strange models can have nodes with no confidence
            confidence = round(parent_node[offset["confidence"]] /
                               math.sqrt(total_instances),
                               PRECISION)
        except AttributeError:
            confidence = None
    else:
        prediction = mean(distribution)
        # weighted trees use the unweighted population to
        # compute the associated error
        confidence = round(regression_error(
            unbiased_sample_variance(distribution, prediction),
            population), PRECISION)
    return Prediction( \
        prediction,
        path,
        confidence,
        distribution=distribution,
        count=total_instances,
        median=dist_median(distribution, total_instances),
        distribution_unit=distribution_unit,
        children=[] if last_node[offset["children#"]] == 0 else \
            last_node[offset["children"]],
        d_min=d_min,
        d_max=d_max)


def regression_last_predict(tree, weighted, fields, input_data):
    """Predict for regression and last prediction missing strategy

    """
    return last_prediction_predict(tree, OFFSETS[str(weighted)], fields,
                                   input_data)
