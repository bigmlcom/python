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

"""Common auxiliary constants, functions and class for all resources

"""

import time

import bigml.constants as c

from bigml.util import get_exponential_wait
from bigml.bigmlconnection import HTTP_OK, HTTP_ACCEPTED, HTTP_CREATED, LOGGER
from bigml.bigmlconnection import BigMLConnection



NO_QS = [c.EVALUATION_RE, c.PREDICTION_RE, c.BATCH_PREDICTION_RE,
         c.CENTROID_RE, c.BATCH_CENTROID_RE, c.ANOMALY_SCORE_RE,
         c.BATCH_ANOMALY_SCORE_RE, c.PROJECT_RE, c.ASSOCIATION_SET_RE]


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
    for resource_type, resource_re in c.RESOURCE_RE.items():
        if resource_re.match(resource):
            return resource_type
    return None


def get_resource(resource_type, resource):
    """Returns a resource/id.

    """
    if isinstance(resource, dict) and 'resource' in resource:
        resource = resource['resource']
    if isinstance(resource, basestring):
        if c.RESOURCE_RE[resource_type].match(resource):
            return resource
        found_type = get_resource_type(resource)
        if found_type is not None and \
                resource_type != get_resource_type(resource):
            raise ValueError(
                "The resource %s has not the expected type:"
                " %s" % (
                    resource, resource_type))
    raise ValueError("%s is not a valid resource ID." % resource)


def resource_is_ready(resource):
    """Checks a fully fledged resource structure and returns True if finished.

    """
    if not isinstance(resource, dict) or 'error' not in resource:
        raise Exception("No valid resource structure found")
    if resource['error'] is not None:
        raise Exception(resource['error']['status']['message'])
    return (resource['code'] in [HTTP_OK, HTTP_ACCEPTED] and
            get_status(resource)['code'] == c.FINISHED)


def check_resource_type(resource, expected_resource, message=None):
    """Checks the resource type.

    """
    resource_type = get_resource_type(resource)
    if expected_resource != resource_type:
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
        status = {'code': c.FINISHED}
    else:
        status = resource['status']
    return status


def get_source_id(source):
    """Returns a source/id.

    """
    return get_resource(c.SOURCE_PATH, source)


def get_dataset_id(dataset):
    """Returns a dataset/id.

    """
    return get_resource(c.DATASET_PATH, dataset)


def get_model_id(model):
    """Returns a model/id.

    """
    return get_resource(c.MODEL_PATH, model)


def get_prediction_id(prediction):
    """Returns a prediction/id.

    """
    return get_resource(c.PREDICTION_PATH, prediction)


def get_evaluation_id(evaluation):
    """Returns an evaluation/id.

    """
    return get_resource(c.EVALUATION_PATH, evaluation)


def get_ensemble_id(ensemble):
    """Returns an ensemble/id.

    """
    return get_resource(c.ENSEMBLE_PATH, ensemble)


def get_batch_prediction_id(batch_prediction):
    """Returns a batchprediction/id.

    """
    return get_resource(c.BATCH_PREDICTION_PATH, batch_prediction)


def get_cluster_id(cluster):
    """Returns a cluster/id.

    """
    return get_resource(c.CLUSTER_PATH, cluster)


def get_centroid_id(centroid):
    """Returns a centroid/id.

    """
    return get_resource(c.CENTROID_PATH, centroid)


def get_batch_centroid_id(batch_centroid):
    """Returns a batchcentroid/id.

    """
    return get_resource(c.BATCH_CENTROID_PATH, batch_centroid)


def get_anomaly_id(anomaly):
    """Returns an anomaly/id.

    """
    return get_resource(c.ANOMALY_PATH, anomaly)


def get_anomaly_score_id(anomaly_score):
    """Returns an anomalyscore/id.

    """
    return get_resource(c.ANOMALY_SCORE_PATH, anomaly_score)


def get_batch_anomaly_score_id(batch_anomaly_score):
    """Returns a batchanomalyscore/id.

    """
    return get_resource(c.BATCH_ANOMALY_SCORE_PATH, batch_anomaly_score)


def get_project_id(project):
    """Returns a project/id.

    """
    return get_resource(c.PROJECT_PATH, project)


def get_sample_id(sample):
    """Returns a sample/id.

    """
    return get_resource(c.SAMPLE_PATH, sample)


def get_correlation_id(correlation):
    """Returns a correlation/id.

    """
    return get_resource(c.CORRELATION_PATH, correlation)


def get_statistical_test_id(statistical_test):
    """Returns a statisticaltest/id.

    """
    return get_resource(c.STATISTICAL_TEST_PATH, statistical_test)


def get_logistic_regression_id(logistic_regression):
    """Returns a logisticregression/id.

    """
    return get_resource(c.LOGISTIC_REGRESSION_PATH, logistic_regression)


def get_association_id(association):
    """Returns an association/id.

    """
    return get_resource(c.ASSOCIATION_PATH, association)


def get_association_set_id(association_set):
    """Returns an associationset/id.

    """
    return get_resource(c.ASSOCIATION_SET_PATH, association_set)


def get_script_id(script):
    """Returns a script/id.

    """
    return get_resource(c.SCRIPT_PATH, script)


def get_execution_id(execution):
    """Returns a execution/id.

    """
    return get_resource(c.EXECUTION_PATH, execution)


def get_library_id(library):
    """Returns a library/id.

    """
    return get_resource(c.LIBRARY_PATH, library)


def get_resource_id(resource):
    """Returns the resource id if it falls in one of the registered types

    """
    if isinstance(resource, dict) and 'resource' in resource:
        return resource['resource']
    elif isinstance(resource, basestring) and any(
            resource_re.match(resource) for _, resource_re
            in c.RESOURCE_RE.items()):
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
        if code == c.FINISHED:
            if counter > 1:
                # final get call to retrieve complete resource
                resource = get_method(resource, **kwargs)
            if raise_on_error:
                exception_on_error(resource)
            return resource
        elif code == c.FAULTY:
            raise ValueError(status)
        time.sleep(get_exponential_wait(wait_time, counter))
        # retries for the finished status use a query string that gets the
        # minimal available resource
        if kwargs.get('query_string') is not None:
            tiny_kwargs = {'query_string': c.TINY_RESOURCE}
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
            check_resource_type(dataset, c.DATASET_PATH,
                                message=("A dataset id is needed to create"
                                         " the resource."))
            dataset = check_resource(dataset,
                                     query_string=c.TINY_RESOURCE,
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
                               query_string=c.TINY_RESOURCE,
                               wait_time=wait_time, retries=retries,
                               raise_on_error=True, api=self)
                args.update({
                    resource_type: resource_id,
                    "dataset": dataset_id})

        if model_types is None:
            model_types = []

        resource_type = get_resource_type(dataset)
        if c.DATASET_PATH != resource_type:
            raise Exception("A dataset id is needed as second argument"
                            " to create the resource. %s found." %
                            resource_type)
        dataset_id = get_dataset_id(dataset)
        if dataset_id:
            dataset = check_resource(dataset_id,
                                     query_string=c.TINY_RESOURCE,
                                     wait_time=wait_time, retries=retries,
                                     raise_on_error=True, api=self)
            resource_type = get_resource_type(model)
            if resource_type in model_types:
                resource_id = get_resource_id(model)
                args_update(resource_id)
            elif resource_type == c.MODEL_PATH:
                resource_id = get_model_id(model)
                args_update(resource_id)
            else:
                raise Exception("A model or ensemble id is needed as first"
                                " argument to create the resource."
                                " %s found." % resource_type)

        return dataset_id and resource_id
