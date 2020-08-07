# -*- coding: utf-8 -*-
#
# Copyright 2015-2020 BigML
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
CONFIGURATION_PATH = 'configuration'
TOPIC_MODEL_PATH = 'topicmodel'
TOPIC_DISTRIBUTION_PATH = 'topicdistribution'
BATCH_TOPIC_DISTRIBUTION_PATH = 'batchtopicdistribution'
TIME_SERIES_PATH = 'timeseries'
FORECAST_PATH = 'forecast'
DEEPNET_PATH = 'deepnet'
OPTIML_PATH = 'optiml'
FUSION_PATH = 'fusion'
PCA_PATH = 'pca'
PROJECTION_PATH = 'projection'
BATCH_PROJECTION_PATH = 'batchprojection'
LINEAR_REGRESSION_PATH = 'linearregression'
SCRIPT_PATH = 'script'
EXECUTION_PATH = 'execution'
LIBRARY_PATH = 'library'
STATUS_PATH = 'status'
EXTERNAL_CONNECTOR_PATH = 'externalconnector'

SUPERVISED_PATHS = [
    MODEL_PATH,
    ENSEMBLE_PATH,
    LOGISTIC_REGRESSION_PATH,
    LINEAR_REGRESSION_PATH,
    DEEPNET_PATH,
    FUSION_PATH
]
MODELS_PATHS = [
    MODEL_PATH,
    ENSEMBLE_PATH,
    LOGISTIC_REGRESSION_PATH,
    LINEAR_REGRESSION_PATH,
    DEEPNET_PATH,
    CLUSTER_PATH,
    ANOMALY_PATH,
    ASSOCIATION_PATH,
    TOPIC_MODEL_PATH,
    TIME_SERIES_PATH,
    FUSION_PATH
]


PMML_MODELS = [
    MODEL_PATH,
    LOGISTIC_REGRESSION_PATH,
    CLUSTER_PATH,
    ASSOCIATION_PATH
]

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
CONFIGURATION_RE = re.compile(r'^%s/%s$' % \
    (CONFIGURATION_PATH, ID_PATTERN))
TOPIC_MODEL_RE = re.compile(r'^(public/)?%s/%s$|^shared/%s/%s$' % (
    TOPIC_MODEL_PATH, ID_PATTERN, TOPIC_MODEL_PATH, SHARED_PATTERN))
TOPIC_DISTRIBUTION_RE = re.compile(r'^(public/)?%s/%s$|^shared/%s/%s$' % (
    TOPIC_DISTRIBUTION_PATH, ID_PATTERN, TOPIC_DISTRIBUTION_PATH,
    SHARED_PATTERN))
BATCH_TOPIC_DISTRIBUTION_RE = re.compile(r'^(public/)?%s/%s$|^shared/%s/%s$' % (
    BATCH_TOPIC_DISTRIBUTION_PATH, ID_PATTERN, BATCH_TOPIC_DISTRIBUTION_PATH,
    SHARED_PATTERN))
TIME_SERIES_RE = re.compile(r'^%s/%s|^shared/%s/%s$' % \
    (TIME_SERIES_PATH, ID_PATTERN, TIME_SERIES_PATH, SHARED_PATTERN))
FORECAST_RE = re.compile(r'^%s/%s$' % \
    (FORECAST_PATH, ID_PATTERN))
DEEPNET_RE = re.compile(r'^%s/%s|^shared/%s/%s$' % \
    (DEEPNET_PATH, ID_PATTERN, DEEPNET_PATH, SHARED_PATTERN))
OPTIML_RE = re.compile(r'^%s/%s|^shared/%s/%s$' % \
    (OPTIML_PATH, ID_PATTERN, OPTIML_PATH, SHARED_PATTERN))
FUSION_RE = re.compile(r'^%s/%s|^shared/%s/%s$' % \
    (FUSION_PATH, ID_PATTERN, FUSION_PATH, SHARED_PATTERN))
PCA_RE = re.compile(r'^%s/%s|^shared/%s/%s$' % \
    (PCA_PATH, ID_PATTERN, PCA_PATH, SHARED_PATTERN))
PROJECTION_RE = re.compile(r'^%s/%s$' % (PROJECTION_PATH, ID_PATTERN))
BATCH_PROJECTION_RE = re.compile(r'^%s/%s$' % (BATCH_PROJECTION_PATH,
                                               ID_PATTERN))
LINEAR_REGRESSION_RE = re.compile(r'^%s/%s|^shared/%s/%s$' % \
    (LINEAR_REGRESSION_PATH, ID_PATTERN,
     LINEAR_REGRESSION_PATH, SHARED_PATTERN))
SCRIPT_RE = re.compile(r'^%s/%s|^shared/%s/%s$' % \
    (SCRIPT_PATH, ID_PATTERN, SCRIPT_PATH, SHARED_PATTERN))
EXECUTION_RE = re.compile(r'^%s/%s|^shared/%s/%s$' % \
    (EXECUTION_PATH, ID_PATTERN, EXECUTION_PATH, SHARED_PATTERN))
LIBRARY_RE = re.compile(r'^%s/%s|^shared/%s/%s$' % \
    (LIBRARY_PATH, ID_PATTERN, LIBRARY_PATH, SHARED_PATTERN))
EXTERNAL_CONNECTOR_RE = re.compile(r'^%s/%s$' % \
    (EXTERNAL_CONNECTOR_PATH, ID_PATTERN))


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
    CONFIGURATION_PATH: CONFIGURATION_RE,
    TOPIC_MODEL_PATH: TOPIC_MODEL_RE,
    TOPIC_DISTRIBUTION_PATH: TOPIC_DISTRIBUTION_RE,
    BATCH_TOPIC_DISTRIBUTION_PATH: BATCH_TOPIC_DISTRIBUTION_RE,
    TIME_SERIES_PATH: TIME_SERIES_RE,
    FORECAST_PATH: FORECAST_RE,
    DEEPNET_PATH: DEEPNET_RE,
    OPTIML_PATH: OPTIML_RE,
    FUSION_PATH: FUSION_RE,
    PCA_PATH: PCA_RE,
    PROJECTION_PATH: PROJECTION_RE,
    BATCH_PROJECTION_PATH: BATCH_PROJECTION_RE,
    LINEAR_REGRESSION_PATH: LINEAR_REGRESSION_RE,
    SCRIPT_PATH: SCRIPT_RE,
    EXECUTION_PATH: EXECUTION_RE,
    LIBRARY_PATH: LIBRARY_RE,
    EXTERNAL_CONNECTOR_PATH: EXTERNAL_CONNECTOR_RE}


RENAMED_RESOURCES = {
    BATCH_PREDICTION_PATH: 'batch_prediction',
    BATCH_CENTROID_PATH: 'batch_centroid',
    ANOMALY_SCORE_PATH: 'anomaly_score',
    BATCH_ANOMALY_SCORE_PATH: 'batch_anomaly_score',
    STATISTICAL_TEST_PATH: 'statistical_test',
    LOGISTIC_REGRESSION_PATH: 'logistic_regression',
    LINEAR_REGRESSION_PATH: 'linear_regression',
    ASSOCIATION_SET_PATH: 'association_set',
    TOPIC_MODEL_PATH: 'topic_model',
    TOPIC_DISTRIBUTION_PATH: 'topic_distribution',
    BATCH_TOPIC_DISTRIBUTION_PATH: 'batch_topic_distribution',
    TIME_SERIES_PATH: 'time_series',
    BATCH_PROJECTION_PATH: 'batch_projection',
    EXTERNAL_CONNECTOR_PATH: 'external_connector'
}

IRREGULAR_PLURALS = {
    ANOMALY_PATH: 'anomalies',
    BATCH_PREDICTION_PATH: 'batch_predictions',
    BATCH_CENTROID_PATH: 'batch_centroids',
    ANOMALY_SCORE_PATH: 'anomaly_scores',
    BATCH_ANOMALY_SCORE_PATH: 'batch_anomaly_scores',
    STATISTICAL_TEST_PATH: 'statistical_tests',
    LOGISTIC_REGRESSION_PATH: 'logistic_regressions',
    LINEAR_REGRESSION_PATH: 'linear_regressions',
    ASSOCIATION_SET_PATH: 'association_sets',
    TOPIC_MODEL_PATH: 'topic_models',
    TOPIC_DISTRIBUTION_PATH: 'topic_distributions',
    TIME_SERIES_PATH: 'time_series',
    LIBRARY_PATH: 'libraries',
    BATCH_PROJECTION_PATH: 'batch_projections',
    EXTERNAL_CONNECTOR_PATH: 'external_connectors'
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

# Default storage folder
STORAGE = "./storage"

# label for transient HTTP errors
TRANSIENT = "transient"

# fields related attributes
RESOURCES_WITH_FIELDS = [SOURCE_PATH, DATASET_PATH, MODEL_PATH,
                         PREDICTION_PATH, CLUSTER_PATH, ANOMALY_PATH,
                         SAMPLE_PATH, CORRELATION_PATH, STATISTICAL_TEST_PATH,
                         LOGISTIC_REGRESSION_PATH, ASSOCIATION_PATH,
                         TOPIC_MODEL_PATH, ENSEMBLE_PATH, PCA_PATH,
                         DEEPNET_PATH, LINEAR_REGRESSION_PATH]
DEFAULT_MISSING_TOKENS = ["", "N/A", "n/a", "NULL", "null", "-", "#DIV/0",
                          "#REF!", "#NAME?", "NIL", "nil", "NA", "na",
                          "#VALUE!", "#NULL!", "NaN", "#N/A", "#NUM!", "?"]
FIELDS_PARENT = { \
    "model": "model",
    "anomaly": "model",
    "cluster": "clusters",
    "logisticregression": "logistic_regression",
    "linearregression": "linear_regression",
    "ensemble": "ensemble",
    "deepnet": "deepnet",
    "topicmodel": "topic_model",
    "association": "associations",
    "fusion": "fusion",
    "correlation": "correlations",
    "sample": "sample",
    "pca": "pca",
    "timeseries": "timeseries",
    "statisticaltest": "statistical_tests"}
ALL_FIELDS = "limit=-1"

EXTERNAL_CONNECTION_ATTRS = { \
    "BIGML_EXTERNAL_CONN_HOST": "host",
    "BIGML_EXTERNAL_CONN_PORT": "port",
    "BIGML_EXTERNAL_CONN_USER": "user",
    "BIGML_EXTERNAL_CONN_PWD": "password",
    "BIGML_EXTERNAL_CONN_DB": "database",
    "BIGML_EXTERNAL_CONN_SOURCE": "source"}
