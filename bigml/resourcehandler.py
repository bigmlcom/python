# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2014-2015 BigML
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

"""Common auxiliary constants, functions and class for all resources

"""

import time
import re

from bigml.util import get_exponential_wait
from bigml.bigmlconnection import HTTP_OK, HTTP_ACCEPTED, HTTP_CREATED, LOGGER
from bigml.bigmlconnection import BigMLConnection


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
SAMPLE_RE = re.compile(r'^%s/%s$' % (SAMPLE_PATH, ID_PATTERN))
CORRELATION_RE = re.compile(r'^%s/%s$' % (CORRELATION_PATH, ID_PATTERN))

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
    'batchanomalyscore': BATCH_ANOMALY_SCORE_RE,
    'project': PROJECT_RE,
    'sample': SAMPLE_RE,
    'correlation': CORRELATION_RE}

RENAMED_RESOURCES = {
    'batchprediction': 'batch_prediction',
    'batchcentroid': 'batch_centroid',
    'anomalyscore': 'anomaly_score',
    'batchanomalyscore': 'batch_anomaly_score'}

NO_QS = [EVALUATION_RE, PREDICTION_RE, BATCH_PREDICTION_RE,
         CENTROID_RE, BATCH_CENTROID_RE, ANOMALY_SCORE_RE,
         BATCH_ANOMALY_SCORE_RE, PROJECT_RE]


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


def get_status(resource):
    """Extracts status info if present or sets the default if public

    """
    if not isinstance(resource, dict):
        raise ValueError("We need a complete resource to extract its status")
    if 'object' in resource:
        if resource['object'] is None:
            raise ValueError("The resource has no status info\n%s" % resource)
        resource = resource['object']
    if not resource.get('private', True) or resource.get('status') is None:
        status = {'code': FINISHED}
    else:
        status = resource['status']
    return status


def get_source_id(source):
    """Returns a source/id.

    """
    return get_resource(SOURCE_RE, source)


def get_dataset_id(dataset):
    """Returns a dataset/id.

    """
    return get_resource(DATASET_RE, dataset)


def get_model_id(model):
    """Returns a model/id.

    """
    return get_resource(MODEL_RE, model)


def get_prediction_id(prediction):
    """Returns a prediction/id.

    """
    return get_resource(PREDICTION_RE, prediction)


def get_evaluation_id(evaluation):
    """Returns an evaluation/id.

    """
    return get_resource(EVALUATION_RE, evaluation)


def get_ensemble_id(ensemble):
    """Returns an ensemble/id.

    """
    return get_resource(ENSEMBLE_RE, ensemble)


def get_batch_prediction_id(batch_prediction):
    """Returns a batchprediction/id.

    """
    return get_resource(BATCH_PREDICTION_RE, batch_prediction)


def get_cluster_id(cluster):
    """Returns a cluster/id.

    """
    return get_resource(CLUSTER_RE, cluster)


def get_centroid_id(centroid):
    """Returns a centroid/id.

    """
    return get_resource(CENTROID_RE, centroid)


def get_batch_centroid_id(batch_centroid):
    """Returns a batchcentroid/id.

    """
    return get_resource(BATCH_CENTROID_RE, batch_centroid)


def get_anomaly_id(anomaly):
    """Returns an anomaly/id.

    """
    return get_resource(ANOMALY_RE, anomaly)


def get_anomaly_score_id(anomaly_score):
    """Returns an anomalyscore/id.

    """
    return get_resource(ANOMALY_SCORE_RE, anomaly_score)


def get_batch_anomaly_score_id(batch_anomaly_score):
    """Returns a batchanomalyscore/id.

    """
    return get_resource(BATCH_ANOMALY_SCORE_RE, batch_anomaly_score)


def get_project_id(project):
    """Returns a project/id.

    """
    return get_resource(PROJECT_RE, project)


def get_sample_id(sample):
    """Returns a sample/id.

    """
    return get_resource(SAMPLE_RE, sample)


def get_correlation_id(correlation):
    """Returns a correlation/id.

    """
    return get_resource(CORRELATION_RE, correlation)


def get_resource_id(resource):
    """Returns the resource id if it falls in one of the registered types

    """
    if isinstance(resource, dict) and 'resource' in resource:
        return resource['resource']
    elif isinstance(resource, basestring) and any(
            resource_re.match(resource) for _, resource_re
            in RESOURCE_RE.items()):
        return resource
    else:
        return


def exception_on_error(resource):
    """Raises exception if resource has error

    """
    if resource['error'] is not None:
        raise Exception(resource['error']['status']['message'])


def check_resource(resource, get_method=None, query_string='', wait_time=1,
                   retries=None, raise_on_error=False, api=None):
    """Waits until a resource is finished.

       Given a resource and its corresponding get_method (if absent, the
       generic get_resource is used), it calls the get_method on
       the resource with the given query_string
       and waits with sleeping intervals of wait_time
       until the resource is in a final state (either FINISHED
       or FAULTY. The number of retries can be limited using the retries
       parameter.

    """
    def get_kwargs(resource_id):
        if not (any(resource_re.match(resource_id) for
                    resource_re in NO_QS)):
            return {'query_string': query_string}
        return {}

    kwargs = {}
    if isinstance(resource, basestring):
        resource_id = resource
    else:
        resource_id = get_resource_id(resource)
    resource_id = get_resource_id(resource)
    if resource_id is None:
        raise ValueError("Failed to extract a valid resource id to check.")
    kwargs = get_kwargs(resource_id)

    if get_method is None and hasattr(api, 'get_resource'):
        get_method = api.get_resource
    elif get_method is None:
        raise ValueError("You must supply either the get_method or the api"
                         " connection info to retrieve the resource")
    if isinstance(resource, basestring):
        resource = get_method(resource, **kwargs)
    counter = 0
    while retries is None or counter < retries:
        counter += 1
        status = get_status(resource)
        code = status['code']
        if code == FINISHED:
            if counter > 1:
                # final get call to retrieve complete resource
                resource = get_method(resource, **kwargs)
            if raise_on_error:
                exception_on_error(resource)
            return resource
        elif code == FAULTY:
            raise ValueError(status)
        time.sleep(get_exponential_wait(wait_time, counter))
        # retries for the finished status use a query string that gets the
        # minimal available resource
        if kwargs.get('query_string') is not None:
            tiny_kwargs = {'query_string': TINY_RESOURCE}
        else:
            tiny_kwargs = {}
        resource = get_method(resource, **tiny_kwargs)
    if raise_on_error:
        exception_on_error(resource)
    return resource


def http_ok(resource):
    """Checking the validity of the http return code

    """
    if 'code' in resource:
        return resource['code'] in [HTTP_OK, HTTP_CREATED, HTTP_ACCEPTED]



class ResourceHandler(BigMLConnection):
    """This class is used by the BigML class as
       a mixin that provides the get method for all kind of
       resources and auxiliar utilities to check their status. It should not
       be instantiated independently.

    """

    def __init__(self):
        """Initializes the ResourceHandler. This class is intended to be
           used purely as a mixin on BigMLConnection and must not be
           instantiated independently.

        """
        pass

    def get_resource(self, resource, **kwargs):
        """Retrieves a remote resource.

           The resource parameter should be a string containing the
           resource id or the dict returned by the corresponding create method.
           As each resource is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, thet function will
           return a dict that encloses the resource values and state info
           available at the time it is called.

        """
        resource_type = get_resource_type(resource)
        if resource_type is None:
            raise ValueError("A resource id or structure is needed.")
        resource_id = get_resource_id(resource)
        if resource_type in NO_QS and 'query_string' in kwargs:
            del kwargs['query_string']
        if resource_id:
            return self._get("%s%s" % (self.url, resource_id),
                             **kwargs)

    def ok(self, resource, query_string='', wait_time=1,
           retries=None, raise_on_error=False):
        """Waits until the resource is finished or faulty, updates it and
           returns True on success

        """
        if http_ok(resource):
            resource.update(check_resource(resource,
                                           query_string=query_string,
                                           wait_time=wait_time,
                                           retries=retries,
                                           raise_on_error=raise_on_error,
                                           api=self))
            return True
        else:
            LOGGER.error("The resource couldn't be created: %s",
                         resource['error'])

    def _set_create_from_datasets_args(self, datasets, args=None,
                                       wait_time=3, retries=10, key=None):
        """Builds args dictionary for the create call from a `dataset` or a
           list of `datasets`.

        """
        dataset_ids = []
        if not isinstance(datasets, list):
            origin_datasets = [datasets]
        else:
            origin_datasets = datasets

        for dataset in origin_datasets:
            check_resource_type(dataset, DATASET_PATH,
                                message=("A dataset id is needed to create"
                                         " the resource."))
            dataset = check_resource(dataset,
                                     query_string=TINY_RESOURCE,
                                     wait_time=wait_time, retries=retries,
                                     raise_on_error=True, api=self)
            dataset_ids.append(get_dataset_id(dataset))

        create_args = {}
        if args is not None:
            create_args.update(args)

        if len(dataset_ids) == 1:
            if key is None:
                key = "dataset"
            create_args.update({key: dataset_ids[0]})
        else:
            if key is None:
                key = "datasets"
            create_args.update({key: dataset_ids})

        return create_args

    def check_origins(self, dataset, model, args, model_types=None,
                      wait_time=3, retries=10):
        """Returns True if the dataset and model needed to build
           the batch prediction or evaluation are finished. The args given
           by the user are modified to include the related ids in the
           create call.

           If model_types is a list, then we check any of the model types in
           the list.

        """

        def args_update(resource_id):
            """Updates args when the resource is ready

            """
            if resource_id:
                check_resource(resource_id,
                               query_string=TINY_RESOURCE,
                               wait_time=wait_time, retries=retries,
                               raise_on_error=True, api=self)
                args.update({
                    resource_type: resource_id,
                    "dataset": dataset_id})

        if model_types is None:
            model_types = []

        resource_type = get_resource_type(dataset)
        if not DATASET_PATH == resource_type:
            raise Exception("A dataset id is needed as second argument"
                            " to create the resource. %s found." %
                            resource_type)
        dataset_id = get_dataset_id(dataset)
        if dataset_id:
            dataset = check_resource(dataset_id,
                                     query_string=TINY_RESOURCE,
                                     wait_time=wait_time, retries=retries,
                                     raise_on_error=True, api=self)
            resource_type = get_resource_type(model)
            if resource_type in model_types:
                resource_id = get_resource_id(model)
                args_update(resource_id)
            elif resource_type == MODEL_PATH:
                resource_id = get_model_id(model)
                args_update(resource_id)
            else:
                raise Exception("A model or ensemble id is needed as first"
                                " argument to create the resource."
                                " %s found." % resource_type)

        return dataset_id and resource_id
