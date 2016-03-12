# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015-2016 BigML
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

"""Common auxiliary constants for all resources

"""

import re

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
PROJECT_PATH = 'project'
SAMPLE_PATH = 'sample'
CORRELATION_PATH = 'correlation'
STATISTICAL_TEST_PATH = 'statisticaltest'
LOGISTIC_REGRESSION_PATH = 'logisticregression'
ASSOCIATION_PATH = 'association'
ASSOCIATION_SET_PATH = 'associationset'
SCRIPT_PATH = 'script'
EXECUTION_PATH = 'execution'
LIBRARY_PATH = 'library'


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
ANOMALY_RE = re.compile(r'^(public/)?%s/%s$|^shared/%s/%s$' % (
    ANOMALY_PATH, ID_PATTERN, ANOMALY_PATH, SHARED_PATTERN))
ANOMALY_SCORE_RE = re.compile(r'^%s/%s$' % (ANOMALY_SCORE_PATH, ID_PATTERN))
BATCH_ANOMALY_SCORE_RE = re.compile(r'^%s/%s$' % (BATCH_ANOMALY_SCORE_PATH,
                                                  ID_PATTERN))
PROJECT_RE = re.compile(r'^%s/%s$' % (PROJECT_PATH, ID_PATTERN))
SAMPLE_RE = re.compile(r'^%s/%s|^shared/%s/%s$' % (
    SAMPLE_PATH, ID_PATTERN, SAMPLE_PATH, SHARED_PATTERN))
CORRELATION_RE = re.compile(r'^%s/%s|^shared/%s/%s$' % (
    CORRELATION_PATH, ID_PATTERN, CORRELATION_PATH, SHARED_PATTERN))
STATISTICAL_TEST_RE = re.compile(r'^%s/%s|^shared/%s/%s$' % \
    (STATISTICAL_TEST_PATH, ID_PATTERN, STATISTICAL_TEST_PATH, SHARED_PATTERN))
LOGISTIC_REGRESSION_RE = re.compile(r'^%s/%s|^shared/%s/%s$' % \
    (LOGISTIC_REGRESSION_PATH, ID_PATTERN,
     LOGISTIC_REGRESSION_PATH, SHARED_PATTERN))
ASSOCIATION_RE = re.compile(r'^%s/%s|^shared/%s/%s$' % \
    (ASSOCIATION_PATH, ID_PATTERN, ASSOCIATION_PATH, SHARED_PATTERN))
ASSOCIATION_SET_RE = re.compile(r'^%s/%s$' % \
    (ASSOCIATION_SET_PATH, ID_PATTERN))
SCRIPT_RE = re.compile(r'^%s/%s|^shared/%s/%s$' % \
    (SCRIPT_PATH, ID_PATTERN, SCRIPT_PATH, SHARED_PATTERN))
EXECUTION_RE = re.compile(r'^%s/%s|^shared/%s/%s$' % \
    (EXECUTION_PATH, ID_PATTERN, EXECUTION_PATH, SHARED_PATTERN))
LIBRARY_RE = re.compile(r'^%s/%s|^shared/%s/%s$' % \
    (LIBRARY_PATH, ID_PATTERN, LIBRARY_PATH, SHARED_PATTERN))

RESOURCE_RE = {
    SOURCE_PATH: SOURCE_RE,
    DATASET_PATH: DATASET_RE,
    MODEL_PATH: MODEL_RE,
    PREDICTION_PATH: PREDICTION_RE,
    EVALUATION_PATH: EVALUATION_RE,
    ENSEMBLE_PATH: ENSEMBLE_RE,
    BATCH_PREDICTION_PATH: BATCH_PREDICTION_RE,
    CLUSTER_PATH: CLUSTER_RE,
    CENTROID_PATH: CENTROID_RE,
    BATCH_CENTROID_PATH: BATCH_CENTROID_RE,
    ANOMALY_PATH: ANOMALY_RE,
    ANOMALY_SCORE_PATH: ANOMALY_SCORE_RE,
    BATCH_ANOMALY_SCORE_PATH: BATCH_ANOMALY_SCORE_RE,
    PROJECT_PATH: PROJECT_RE,
    SAMPLE_PATH: SAMPLE_RE,
    CORRELATION_PATH: CORRELATION_RE,
    STATISTICAL_TEST_PATH: STATISTICAL_TEST_RE,
    LOGISTIC_REGRESSION_PATH: LOGISTIC_REGRESSION_RE,
    ASSOCIATION_PATH: ASSOCIATION_RE,
    ASSOCIATION_SET_PATH: ASSOCIATION_SET_RE,
    SCRIPT_PATH: SCRIPT_RE,
    EXECUTION_PATH: EXECUTION_RE,
    LIBRARY_PATH: LIBRARY_RE}


RENAMED_RESOURCES = {
    BATCH_PREDICTION_PATH: 'batch_prediction',
    BATCH_CENTROID_PATH: 'batch_centroid',
    ANOMALY_SCORE_PATH: 'anomaly_score',
    BATCH_ANOMALY_SCORE_PATH: 'batch_anomaly_score',
    STATISTICAL_TEST_PATH: 'statistical_test',
    LOGISTIC_REGRESSION_PATH: 'logistic_regression',
    ASSOCIATION_SET_PATH: 'association_set'
}


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

# Minimum query string to get model fields
TINY_RESOURCE = "full=false"
