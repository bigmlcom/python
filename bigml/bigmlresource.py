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

"""Common auxiliary constants and functions for resources

"""

import re

from bigml.bigmlconnection import HTTP_OK, HTTP_ACCEPTED


# Basic resources
SOURCE_PATH = 'source'
DATASET_PATH = 'dataset'
MODEL_PATH = 'model'
PREDICTION_PATH = 'prediction'
EVALUATION_PATH = 'evaluation'
ENSEMBLE_PATH = 'ensemble'
BATCH_PREDICTION_PATH = 'batchprediction'
CLUSTER_PATH = 'cluster'
CENTROID_PATH = 'centroid'
BATCH_CENTROID_PATH = 'batchcentroid'
ANOMALY_PATH = 'anomaly'
ANOMALY_SCORE_PATH = 'anomalyscore'
BATCH_ANOMALY_SCORE_PATH = 'batchanomalyscore'


# Resource Ids patterns
ID_PATTERN = '[a-f0-9]{24}'
SHARED_PATTERN = '[a-zA-Z0-9]{24,30}'
SOURCE_RE = re.compile(r'^%s/%s$' % (SOURCE_PATH, ID_PATTERN))
DATASET_RE = re.compile(r'^(public/)?%s/%s$|^shared/%s/%s$' % (
    DATASET_PATH, ID_PATTERN, DATASET_PATH, SHARED_PATTERN))
MODEL_RE = re.compile(r'^(public/)?%s/%s$|^shared/%s/%s$' % (
    MODEL_PATH, ID_PATTERN, MODEL_PATH, SHARED_PATTERN))
PREDICTION_RE = re.compile(r'^%s/%s$' % (PREDICTION_PATH, ID_PATTERN))
EVALUATION_RE = re.compile(r'^%s/%s$' % (EVALUATION_PATH, ID_PATTERN))
ENSEMBLE_RE = re.compile(r'^%s/%s$' % (ENSEMBLE_PATH, ID_PATTERN))
BATCH_PREDICTION_RE = re.compile(r'^%s/%s$' % (BATCH_PREDICTION_PATH,
                                               ID_PATTERN))
CLUSTER_RE = re.compile(r'^(public/)?%s/%s$|^shared/%s/%s$' % (
    CLUSTER_PATH, ID_PATTERN, CLUSTER_PATH, SHARED_PATTERN))
CENTROID_RE = re.compile(r'^%s/%s$' % (CENTROID_PATH, ID_PATTERN))
BATCH_CENTROID_RE = re.compile(r'^%s/%s$' % (BATCH_CENTROID_PATH,
                                             ID_PATTERN))
ANOMALY_RE = re.compile(r'^%s/%s$' % (ANOMALY_PATH, ID_PATTERN))
ANOMALY_SCORE_RE = re.compile(r'^%s/%s$' % (ANOMALY_SCORE_PATH, ID_PATTERN))
BATCH_ANOMALY_SCORE_RE = re.compile(r'^%s/%s$' % (BATCH_ANOMALY_SCORE_PATH,
                                                  ID_PATTERN))


RESOURCE_RE = {
    'source': SOURCE_RE,
    'dataset': DATASET_RE,
    'model': MODEL_RE,
    'prediction': PREDICTION_RE,
    'evaluation': EVALUATION_RE,
    'ensemble': ENSEMBLE_RE,
    'batchprediction': BATCH_PREDICTION_RE,
    'cluster': CLUSTER_RE,
    'centroid': CENTROID_RE,
    'batchcentroid': BATCH_CENTROID_RE,
    'anomaly': ANOMALY_RE,
    'anomalyscore': ANOMALY_SCORE_RE,
    'batchanomalyscore': BATCH_ANOMALY_SCORE_RE}

RENAMED_RESOURCES = {
    'batchprediction': 'batch_prediction',
    'batchcentroid': 'batch_centroid',
    'anomalyscore': 'anomaly_score',
    'batchanomalyscore': 'batch_anomaly_score'}


# Resource status codes
WAITING = 0
QUEUED = 1
STARTED = 2
IN_PROGRESS = 3
SUMMARIZED = 4
FINISHED = 5
UPLOADING = 6
FAULTY = -1
UNKNOWN = -2
RUNNABLE = -3

def get_resource_type(resource):
    """Returns the associated resource type for a resource

    """
    if isinstance(resource, dict) and 'resource' in resource:
        resource = resource['resource']
    if not isinstance(resource, basestring):
        raise ValueError("Failed to parse a resource string or structure.")
    for resource_type, resource_re in RESOURCE_RE.items():
        if resource_re.match(resource):
            return resource_type
    return None


def get_resource(regex, resource):
    """Returns a resource/id.

    """
    if isinstance(resource, dict) and 'resource' in resource:
        resource = resource['resource']
    if isinstance(resource, basestring) and regex.match(resource):
        return resource
    raise ValueError("Cannot find resource id for %s" % resource)


def resource_is_ready(resource):
    """Checks a fully fledged resource structure and returns True if finished.

    """
    if not isinstance(resource, dict) or not 'error' in resource:
        raise Exception("No valid resource structure found")
    if resource['error'] is not None:
        raise Exception(resource['error']['status']['message'])
    return (resource['code'] in [HTTP_OK, HTTP_ACCEPTED] and
            get_status(resource)['code'] == FINISHED)


def check_resource_type(resource, expected_resource, message=None):
    """Checks the resource type.

    """
    resource_type = get_resource_type(resource)
    if not expected_resource == resource_type:
        raise Exception("%s\nFound %s." % (message, resource_type))
