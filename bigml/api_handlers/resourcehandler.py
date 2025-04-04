# -*- coding: utf-8 -*-
#pylint: disable=abstract-method,unused-import
#
# Copyright 2014-2025 BigML
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIn545D, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Common auxiliary constants, functions and class for all resources

"""

import time
import os
import datetime
import json
import re
import abc

from xml.dom import minidom

import bigml.constants as c

from bigml.util import get_exponential_wait, get_status, is_status_final, \
    save, save_json
from bigml.util import DFT_STORAGE
from bigml.bigmlconnection import HTTP_OK, HTTP_ACCEPTED, HTTP_CREATED, \
    LOGGER, DOWNLOAD_DIR, HTTP_INTERNAL_SERVER_ERROR
from bigml.constants import WAITING, QUEUED, STARTED, IN_PROGRESS, \
    SUMMARIZED, FINISHED, UPLOADING, FAULTY, UNKNOWN, RUNNABLE
from bigml.exceptions import FaultyResourceError

# Minimum query string to get model fields
TINY_RESOURCE = "full=false"

# Resource types that are composed by other resources
COMPOSED_RESOURCES = ["ensemble", "fusion"]

LIST_LAST = "limit=1&full=yes&tags=%s"

PMML_QS = "pmml=yes"


def get_resource_type(resource):
    """Returns the associated resource type for a resource

    """
    if isinstance(resource, dict) and 'resource' in resource:
        resource = resource['resource']
    if not isinstance(resource, str):
        raise ValueError("Failed to parse a resource string or structure.")
    for resource_type, resource_re in list(c.RESOURCE_RE.items()):
        if resource_re.match(resource):
            return resource_type
    return None


def get_resource(resource_type, resource):
    """Returns a resource/id.

    """
    if isinstance(resource, dict) and 'resource' in resource:
        resource = resource['resource']
    if isinstance(resource, str):
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


def get_id(pure_id):
    """Returns last part or a resource ID.

    """
    if isinstance(pure_id, str):
        pure_id = re.sub(r'^[^/]*/(%s)' % c.ID_PATTERN, r'\1', pure_id)
        if c.ID_RE.match(pure_id):
            return pure_id
    raise ValueError("%s is not a valid ID." % pure_id)


def get_fields(resource):
    """Returns the field information in a resource dictionary structure

    """
    try:
        resource_type = get_resource_type(resource)
    except ValueError:
        raise ValueError("Unknown resource structure. Failed to find"
                         " a valid resource dictionary as argument.")

    if resource_type in c.RESOURCES_WITH_FIELDS:
        resource = resource.get('object', resource)
        # fields structure
        if resource_type in list(c.FIELDS_PARENT.keys()) and \
                c.FIELDS_PARENT[resource_type] is not None:
            fields = resource[c.FIELDS_PARENT[resource_type]].get('fields', {})
        else:
            fields = resource.get('fields', {})

        if resource_type == c.SAMPLE_PATH:
            fields = {field['id']: field for field in fields}
    return fields


def resource_is_ready(resource):
    """Checks a fully fledged resource structure and returns True if finished.

    """
    if not isinstance(resource, dict):
        raise Exception("No valid resource structure found")
    # full resources
    if 'object' in resource:
        if 'error' not in resource:
            raise Exception("No valid resource structure found")
        if resource['error'] is not None:
            raise Exception(resource['error']['status']['message'])
        return (resource['code'] in [HTTP_OK, HTTP_ACCEPTED] and
                get_status(resource)['code'] == c.FINISHED)
    # only API response contents
    return get_status(resource)['code'] == c.FINISHED


def check_resource_type(resource, expected_resource, message=None):
    """Checks the resource type.

    """
    if isinstance(expected_resource, str):
        expected_resources = [expected_resource]
    else:
        expected_resources = expected_resource
    if isinstance(resource, dict) and 'id' in resource:
        resource = resource['id']
    resource_type = get_resource_type(resource)
    if resource_type not in expected_resources:
        raise Exception("%s\nFound %s." % (message, resource_type))


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


def get_configuration_id(configuration):
    """Returns a configuration/id.

    """
    return get_resource(c.CONFIGURATION_PATH, configuration)


def get_topic_model_id(topic_model):
    """Returns a topicmodel/id.

    """
    return get_resource(c.TOPIC_MODEL_PATH, topic_model)


def get_topic_distribution_id(topic_distribution):
    """Returns a topicdistribution/id.

    """
    return get_resource(c.TOPIC_DISTRIBUTION_PATH, topic_distribution)


def get_batch_topic_distribution_id(batch_topic_distribution):
    """Returns a batchtopicdistribution/id.

    """
    return get_resource(c.BATCH_TOPIC_DISTRIBUTION_PATH,
                        batch_topic_distribution)


def get_time_series_id(time_series):
    """Returns a timeseries/id.

    """
    return get_resource(c.TIME_SERIES_PATH, time_series)


def get_forecast_id(forecast):
    """Returns a forecast/id.

    """
    return get_resource(c.FORECAST_PATH, forecast)


def get_fusion_id(fusion):
    """Returns an fusion/id.

    """
    return get_resource(c.FUSION_PATH, fusion)


def get_optiml_id(optiml):
    """Returns an optiml/id.

    """
    return get_resource(c.OPTIML_PATH, optiml)


def get_deepnet_id(deepnet):
    """Returns a deepnet/id.

    """
    return get_resource(c.DEEPNET_PATH, deepnet)


def get_pca_id(pca):
    """Returns a PCA/id.

    """
    return get_resource(c.PCA_PATH, pca)


def get_projection_id(projection):
    """Returns a projection/id.

    """
    return get_resource(c.PROJECTION_PATH, projection)


def get_batch_projection_id(batch_projection):
    """Returns a batchprojection/id.

    """
    return get_resource(c.BATCH_PROJECTION_PATH, batch_projection)


def get_linear_regression_id(linear_regression):
    """Returns a linearregression/id.

    """
    return get_resource(c.LINEAR_REGRESSION_PATH, linear_regression)


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


def get_external_connector_id(library):
    """Returns a externalconnector/id.

    """
    return get_resource(c.EXTERNAL_CONNECTOR_PATH, library)


def get_resource_id(resource):
    """Returns the resource id if it falls in one of the registered types

    """
    if isinstance(resource, dict) and 'resource' in resource:
        return resource['resource']
    if isinstance(resource, str) and any(
            resource_re.match(resource) for _, resource_re
            in list(c.RESOURCE_RE.items())):
        return resource
    return None


def exception_on_error(resource, logger=None):
    """Raises exception if the resource has an error. The error can be
    due to a problem in the API call to retrieve it or because the
    resource is FAULTY.

    """
    if resource.get('error') is not None:
        # http error calling the API
        message = "API connection problem - %s" % resource.get('error', \
            {}).get('status', {}).get('message')
        if logger is not None:
            logger.error(message)
        raise Exception(message)
    if resource.get('object', resource).get('status', {}).get('error') \
            is not None:
        # Faulty resource problem
        status = resource.get('object', resource).get( \
            'status', {})
        message = "Faulty resource %s - %s" % (resource["resource"],
            status.get('cause', status).get('message'))
        if logger is not None:
            logger.error(message)
        raise FaultyResourceError(message)


def check_resource(resource, get_method=None, query_string='', wait_time=1,
                   retries=None, raise_on_error=False,
                   max_elapsed_estimate=float('inf'), api=None, debug=False,
                   progress_cb=None):
    """Waits until a resource is finished.

       Given a resource and its corresponding get_method (if absent, the
       generic get_resource is used), it calls the get_method on
       the resource with the given query_string
       and waits with sleeping intervals of wait_time
       until the resource is in a final state (either FINISHED
       or FAULTY. The number of retries can be limited using the retries
       parameter.

    """

    resource_id = get_resource_id(resource)
    # ephemeral predictions
    if isinstance(resource, dict) and resource.get("resource") is None:
        return resource
    if resource_id is None:
        raise ValueError("Failed to extract a valid resource id to check.")
    if wait_time <= 0:
        raise ValueError("The time to wait needs to be positive.")
    debug = debug or (api is not None and (api.debug or api.short_debug))
    if debug:
        print("Checking resource: %s" % resource_id)
    kwargs = {'query_string': query_string}
    if hasattr(api, 'shared_ref') or (get_method is None and
            hasattr(api, 'get_resource')):
        get_method = api.get_resource
    elif get_method is None:
        raise ValueError("You must supply either the get_method or the api"
                         " connection info to retrieve the resource")

    if not isinstance(resource, dict) or not http_ok(resource) or \
            resource.get("object") is None:
        resource = resource_id

    if isinstance(resource, str):
        if debug:
            print("Getting resource %s" % resource_id)
        resource = get_method(resource_id, **kwargs)
        if not http_ok(resource):
            if raise_on_error:
                raise Exception("API connection problem: %s" %
                    json.dumps(resource))
            return resource

    counter = 0
    elapsed = 0
    while retries is None or counter < retries:

        counter += 1
        status = get_status(resource)
        code = status['code']
        if debug:
            print("The resource has status code: %s" % code)
        if code == c.FINISHED:
            if counter > 1:
                if debug:
                    print("Getting resource %s with args %s" % (resource_id,
                                                                kwargs))
                # final get call to retrieve complete resource
                resource = get_method(resource, **kwargs)
            if raise_on_error:
                exception_on_error(resource)
            return resource
        if code == c.FAULTY:
            if raise_on_error:
                exception_on_error(resource)
            return resource
        # resource is ok
        progress = 0
        #pylint: disable=locally-disabled, bare-except
        if status is not None:
            progress = status.get("progress", 0)
            if debug:
                print("Progress: %s" % progress)
            try:
                if progress_cb is not None:
                    progress_cb(progress, resource)
            except:
                print("WARNING: Progress callback raised exception. Please,"
                      "double check your function.")
            progress = progress if progress > 0.8 \
                else 0 # dumping when almost finished
        progress_dumping = (1 - progress)
        _wait_time = get_exponential_wait(wait_time,
            max(int(counter * progress_dumping), 1))
        _max_wait = max_elapsed_estimate - _wait_time
        _wait_time = min(_max_wait, _wait_time)
        if _wait_time <= 0:
            # when the max_expected_elapsed time is met, we still wait for
            # the resource to be finished but we restart all counters and
            # the exponentially growing time is initialized
            _wait_time = wait_time
            counter = 0
            elapsed = 0
        if debug:
            print("Sleeping %s" % _wait_time)
        time.sleep(_wait_time)
        elapsed += _wait_time
        # retries for the finished status use a query string that gets the
        # minimal available resource
        if kwargs.get('query_string') is not None:
            tiny_kwargs = {'query_string': c.TINY_RESOURCE}
        else:
            tiny_kwargs = {}
        if debug:
            print("Getting only status for resource %s" % resource_id)
        resource = get_method(resource, **tiny_kwargs)
        if not http_ok(resource):
            resource["resource"] = resource_id
            if raise_on_error:
                raise Exception("API connection problem: %s" %
                    json.dumps(resource))
            return resource

    if raise_on_error:
        exception_on_error(resource)
    return resource


def http_ok(resource):
    """Checking the validity of the http return code

    """
    if 'code' in resource:
        return resource['code'] in [HTTP_OK, HTTP_CREATED, HTTP_ACCEPTED]
    return False


class ResourceHandlerMixin(metaclass=abc.ABCMeta):
    """This class is used by the BigML class as
       a mixin that provides the get method for all kind of
       resources and auxiliar utilities to check their status. It should not
       be instantiated independently.

    """
    @abc.abstractmethod
    def prepare_image_fields(self, model_info, input_data):
        """This is an abstract method that should be implemented in the API
        final class to create sources for the image fields used in the model

        """

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

        # adding the shared_ref if the API connection object has one
        if hasattr(self, "shared_ref"):
            kwargs.update({"shared_ref": self.shared_ref})

        if resource_id:
            kwargs.update({"resource_id": resource_id})
            return self._get("%s%s" % (self.url, resource_id), **kwargs)
        return None

    def update_resource(self, resource, changes, **kwargs):
        """Updates a remote resource.

           The resource parameter should be a string containing the
           resource id or the dict returned by the corresponding create method.

        """
        resource_id, error = self.final_resource(resource)
        if error or resource_id is None:
            raise Exception("Failed to update %s. Only correctly finished "
                            "resources can be updated. Please, check "
                            "the resource status." % resource_id)
        kwargs.update({"resource_id": resource_id})
        body = json.dumps(changes)
        return self._update("%s%s" % (self.url, resource_id), body, **kwargs)

    def delete_resource(self, resource, **kwargs):
        """Delete a remote resource

        """
        resource_id = get_resource_id(resource)
        if resource_id:
            return self._delete("%s%s" % (self.url, resource_id), **kwargs)
        return None

    def _download_resource(self, resource, filename, retries=10):
        """Download CSV information from downloadable resources

        """
        resource_id, error = self.final_resource(resource, retries=retries)
        if error or resource_id is None:
            raise Exception("Failed to download %s. Only correctly finished "
                            "resources can be downloaded. Please, check "
                            "the resource status. %s" % (resource_id, error))
        return self._download("%s%s%s" % (self.url, resource_id,
                                          DOWNLOAD_DIR),
                              filename=filename,
                              retries=retries)

    #pylint: disable=locally-disabled,invalid-name
    def ok(self, resource, query_string='', wait_time=1,
           max_requests=None, raise_on_error=False, retries=None,
           error_retries=None, max_elapsed_estimate=float('inf'), debug=False,
           progress_cb=None):
        """Waits until the resource is finished or faulty, updates it and
           returns True when a finished resource is correctly retrieved
           and False if the retrieval fails or the resource is faulty.

             resource: (map) Resource structure
             query_string: (string) Filters used on the resource attributes
             wait_time: (number) Time to sleep between get requests
             max_requests: (integer) Maximum number of get requests
             raise_on_error: (boolean) Whether to raise errors or log them
             retries: (integer) Now `max_requests` (deprecated)
             error_retries: (integer) Retries for transient HTTP errors
             max_elapsed_estimate: (integer) Elapsed number of seconds that we
                                    expect the resource to be finished in.
                                    This is not a hard limit for the method
                                    to end, but an estimation of time to wait.
             debug: (boolean) Whether to print traces for every get call
             progress_cb: (function) Callback function to log progress

        """
        def maybe_retrying(resource, error_retries, new_resource=None):
            """Retrying retrieval if it's due to a transient error """
            if new_resource is None:
                new_resource = resource
            else:
                new_resource.update({"object": resource["object"]})
            if new_resource.get('error', {}).get(
                    'status', {}).get('type') == c.TRANSIENT \
                    and error_retries is not None and error_retries > 0:
                time.sleep(wait_time)
                return self.ok(resource, query_string, wait_time,
                               max_requests, raise_on_error, retries,
                               error_retries - 1, max_elapsed_estimate,
                               debug)
            resource.update(new_resource)
            if raise_on_error:
                exception_on_error(resource, logger=LOGGER)
            return False

        new_resource = check_resource( \
            resource,
            query_string=query_string,
            wait_time=wait_time,
            retries=max_requests,
            max_elapsed_estimate=max_elapsed_estimate,
            raise_on_error=False, # we don't raise on error to update always
            api=self,
            debug=debug,
            progress_cb=progress_cb)

        if http_ok(new_resource):
            resource.update(new_resource)
            # try to recover from transient errors
            if resource["error"] is not None:
                return maybe_retrying(resource, error_retries)

            #pylint: disable=locally-disabled,bare-except
            if raise_on_error:
                exception_on_error(resource, logger=LOGGER)
            else:
                try:
                    exception_on_error(resource)
                except:
                    return False
            return True
        return maybe_retrying(resource, error_retries,
                              new_resource=new_resource)

    def _set_create_from_datasets_args(self, datasets, args=None,
                                       wait_time=3, retries=10, key=None):
        """Builds args dictionary for the create call from a `dataset` or a
           list of `datasets`.

        """
        dataset_ids = []
        single = False

        create_args = {}
        if args is not None:
            create_args.update(args)

        if isinstance(datasets, str) and datasets.startswith('shared/'):
            origin = datasets.replace('shared/', "")
            if get_resource_type(origin) != "dataset":
                create_args.update({"shared_hash": origin.split("/")[1]})
                return create_args

        if not isinstance(datasets, list):
            single = True
            origin_datasets = [datasets]
        else:
            origin_datasets = datasets

        for dataset in origin_datasets:
            check_resource_type(dataset, c.DATASET_PATH,
                                message=("A dataset id is needed to create"
                                         " the resource."))
            if isinstance(dataset, dict) and 'id' in dataset:
                dataset['id'] = dataset['id'].replace("shared/", "")
                dataset_ids.append(dataset)
                dataset_id = dataset['id']
            else:
                dataset_id = get_dataset_id(dataset).replace( \
                    "shared/", "")
                dataset_ids.append(dataset_id)
            dataset = check_resource(dataset_id,
                                     query_string=c.TINY_RESOURCE,
                                     wait_time=wait_time, retries=retries,
                                     raise_on_error=True, api=self)
        if single:
            if key is None:
                key = "dataset"
            create_args.update({key: dataset_ids[0]})
        else:
            if key is None:
                key = "datasets"
            create_args.update({key: dataset_ids})

        return create_args

    def _set_create_from_models_args(self, models, types, args=None,
                                     wait_time=3, retries=10):
        """Builds args dictionary for the create call from a list of
        models. The first argument needs to be a list of:
            - the model IDs
            - dict objects with the "id" attribute set to the ID of the model
              and the "weight" attribute set to the weight associated to that
              model.

        """
        model_ids = []
        if not isinstance(models, list):
            origin_models = [models]
        else:
            origin_models = models

        for model in origin_models:
            if isinstance(model, dict) and model.get("id"):
                model = model.get("id")
            check_resource_type(model, types,
                                message=("A list of model ids "
                                         "is needed to create"
                                         " the resource."))
            model_ids.append(get_resource_id(model).replace("shared/", ""))
            model = check_resource(model,
                                   query_string=c.TINY_RESOURCE,
                                   wait_time=wait_time, retries=retries,
                                   raise_on_error=True, api=self)

        if not isinstance(origin_models[0], dict) \
                or not origin_models[0].get("id"):
            origin_models = model_ids

        create_args = {}
        if args is not None:
            create_args.update(args)

        create_args.update({"models": origin_models})

        return create_args

    def _set_clone_from_args(self, origin, resource_type, args=None,
                             wait_time=3, retries=10):
        """Builds args dictionary for the create call to clone resources.
           The first argument needs to be a resource or resource ID that
           has one of the types in resource_type

        """
        if isinstance(origin, dict) and origin.get("id"):
            origin = origin.get("id")

        origin_id = get_resource_id(origin)

        if origin_id is not None:
            check_resource_type(origin, resource_type,
                                message=("Failed to find a %s as the resource"
                                         " to clone." % resource_type))
            origin = check_resource(origin,
                                    query_string=c.TINY_RESOURCE,
                                    wait_time=wait_time, retries=retries,
                                    raise_on_error=True, api=self)

        create_args = {}
        if args is not None:
            create_args.update(args)

        if isinstance(origin, dict) and origin["object"].get("shared_hash"):
            attr = "shared_hash"
            origin_id = origin["object"][attr]
        else:
            attr = "origin"
        create_args.update({attr: origin_id})

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

    def export(self, resource, filename=None, pmml=False,
               **kwargs):
        """Retrieves a remote resource when finished and stores it
           in the user-given file

           The resource parameter should be a string containing the
           resource id or the dict returned by the corresponding create method.
           As each resource is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, the function will
           wait until the resource is in one of these states to store the
           associated info.

        """
        resource_type = get_resource_type(resource)
        if resource_type is None:
            raise ValueError("A resource ID or structure is needed.")

        if pmml:
            if resource_type not in c.PMML_MODELS:
                raise ValueError("Failed to export to PMML. Only some models"
                                 " can be exported to PMML.")

        resource_id = get_resource_id(resource)
        if resource_id:
            if pmml:
                # only models with no text fields can be exported
                resource_info = self._get("%s%s" % (self.url, resource_id),
                                          query_string=c.TINY_RESOURCE)
                field_types = resource_info["object"].get( \
                    "dataset_field_types", {})
                if field_types.get("items", 0) > 0 or \
                        field_types.get("text", 0) > 0:
                    raise ValueError("Failed to export to PMML. Models with "
                                     "text and items fields cannot be "
                                     "exported to PMML.")
                if kwargs.get("query_string"):
                    kwargs["query_string"] += "&%s" % PMML_QS
                else:
                    kwargs["query_string"] = PMML_QS

            if kwargs.get("query_string") and \
                    "output_format" in kwargs.get("query_string"):
                resource_info = self._get("%s%s" % (self.url,
                                                    resource_id))
            else:
                resource_info = self._get("%s%s" % (self.url, resource_id),
                                          **kwargs)
            if not is_status_final(resource_info):
                self.ok(resource_info)
            if filename is None:
                file_dir = self.storage or DFT_STORAGE
                filename = os.path.join( \
                    file_dir, resource_id.replace("/", "_"))
            if resource_type in COMPOSED_RESOURCES:
                # inner models in composed resources need the shared reference
                # to be downloaded
                if resource.startswith("shared"):
                    kwargs.update(
                        {"shared_ref": resource_id.replace("shared/", "")})
                elif "shared_ref" in kwargs and not resource.startswith("shared"):
                    kwargs["shared_ref"] = "%s,%s" % (kwargs["shared_ref"],
                                                      resource_id)
                for component_id in resource_info["object"]["models"]:
                    # for weighted fusions we need to retrieve the component ID
                    if isinstance(component_id, dict):
                        component_id = component_id['id']
                    component_filename = os.path.join(
                        os.path.dirname(filename),
                        component_id.replace("/", "_"))
                    self.export( \
                        component_id,
                        filename=component_filename,
                        pmml=pmml,
                        **kwargs)
            if kwargs.get("query_string") and \
                    "output_format" in kwargs.get("query_string"):
                return self._download("%s%s?%s" % \
                    (self.url, resource_id, kwargs["query_string"]), filename)

            if pmml and resource_info.get("object", {}).get("pmml"):
                resource_info = resource_info.get("object", {}).get("pmml")
                resource_info = minidom.parseString( \
                    resource_info).toprettyxml()
                return save(resource_info, filename)
            return save_json(resource_info, filename)
        raise ValueError("First agument is expected to be a valid"
                         " resource ID or structure.")

    def export_last(self, tags, filename=None,
                    resource_type="model", project=None,
                    **kwargs):
        """Retrieves a remote resource by tag when finished and stores it
           in the user-given file

           The resource parameter should be a string containing the
           resource id or the dict returned by the corresponding create method.
           As each resource is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, the function will
           wait until the resource is in one of these states to store the
           associated info.

        """

        if tags is not None and tags != '':
            query_string = LIST_LAST % tags
            if project is not None:
                query_string += "&project=%s" % project

            kwargs.update({'query_string': "%s&%s" % \
                (query_string, kwargs.get('query_string', ''))})

            response = self._list("%s%s" % (self.url, resource_type),
                                  **kwargs)
            if len(response.get("objects", [])) > 0:
                resource_info = response["objects"][0]
                if not is_status_final(resource_info):
                    self.ok(resource_info)
                if filename is None:
                    file_dir = self.storage or DFT_STORAGE
                    now = datetime.datetime.now().strftime("%a%b%d%y_%H%M%S")
                    filename = os.path.join( \
                        file_dir,
                        "%s_%s.json" % (tags.replace("/", "_"), now))
                if resource_type in COMPOSED_RESOURCES:
                    for component_id in resource_info["models"]:
                        self.export( \
                            component_id,
                            filename=os.path.join( \
                                os.path.dirname(filename),
                                component_id.replace("/", "_")))
                return save_json(resource_info, filename)
            raise ValueError("No %s found with tags %s." % (resource_type,
                                                            tags))
        raise ValueError("First agument is expected to be a non-empty"
                         " tag.")

    def final_resource(self, resource, retries=10):
        """Waits for a resource to finish or fail and returns
           its ID and the error information

        """
        resource = check_resource( \
            resource,
            query_string=c.TINY_RESOURCE,
            retries=retries,
            api=self)
        error = resource.get("error")
        try:
            if resource.get("object", resource)["status"]["code"] == c.FAULTY:
                error = "%s (%s)" % (resource.get("error"),
                                     resource.get("object", resource)[ \
                                        "status"]["message"])
        except KeyError:
            error = "Could not get resource status info for %s" % \
                resource.get("resource", resource)
        return get_resource_id(resource), error
