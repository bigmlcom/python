# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2012-2014 BigML
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

"""BigML.io Python bindings.

This is a simple binding to BigML.io, the BigML API.

Example usage (assuming that you have previously set up the BIGML_USERNAME and
BIGML_API_KEY environment variables):

from bigml.api import BigML

api = BigML()
source = api.create_source('./data/iris.csv')
dataset = api.create_dataset(source)
model = api.create_model(dataset)
prediction = api.create_prediction(model, {'sepal width': 1})
api.pprint(prediction)

"""
import sys
import logging
LOG_FORMAT = '%(asctime)-15s: %(message)s'
LOGGER = logging.getLogger('BigML')

import time
import os
import re
import pprint

import requests



try:
    import simplejson as json
except ImportError:
    import json

from bigml.util import (check_dir,
                        get_exponential_wait)
from bigml.bigmlconnection import BigMLConnection
from bigml.resourcehandler import ResourceHandler
from bigml.sourcehandler import SourceHandler
from bigml.datasethandler import DatasetHandler
from bigml.modelhandler import ModelHandler
from bigml.predictionhandler import PredictionHandler


# Base URL
BIGML_URL = '%s://%s/andromeda/'
# Development Mode URL
BIGML_DEV_URL = '%s://%s/dev/andromeda/'

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

PREDICTIONS_RE = []

DOWNLOAD_DIR = '/download'

# Headers
SEND_JSON = {'Content-Type': 'application/json;charset=utf-8'}
ACCEPT_JSON = {'Accept': 'application/json;charset=utf-8'}

# HTTP Status Codes from https://bigml.com/developers/status_codes
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_ACCEPTED = 202
HTTP_NO_CONTENT = 204
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_PAYMENT_REQUIRED = 402
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_METHOD_NOT_ALLOWED = 405
HTTP_TOO_MANY_REQUESTS = 429
HTTP_LENGTH_REQUIRED = 411
HTTP_INTERNAL_SERVER_ERROR = 500

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

# Map status codes to labels
STATUSES = {
    WAITING: "WAITING",
    QUEUED: "QUEUED",
    STARTED: "STARTED",
    IN_PROGRESS: "IN_PROGRESS",
    SUMMARIZED: "SUMMARIZED",
    FINISHED: "FINISHED",
    UPLOADING: "UPLOADING",
    FAULTY: "FAULTY",
    UNKNOWN: "UNKNOWN",
    RUNNABLE: "RUNNABLE"
}

# Minimum query string to get model fields
TINY_RESOURCE = "full=false"


def get_resource(regex, resource):
    """Returns a resource/id.

    """
    if isinstance(resource, dict) and 'resource' in resource:
        resource = resource['resource']
    if isinstance(resource, basestring) and regex.match(resource):
        return resource
    raise ValueError("Cannot find resource id for %s" % resource)


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


def check_resource_type(resource, expected_resource, message=None):
    """Checks the resource type.

    """
    resource_type = get_resource_type(resource)
    if not expected_resource == resource_type:
        raise Exception("%s\nFound %s." % (message, resource_type))


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


def resource_is_ready(resource):
    """Checks a fully fledged resource structure and returns True if finished.

    """
    if not isinstance(resource, dict) or not 'error' in resource:
        raise Exception("No valid resource structure found")
    if resource['error'] is not None:
        raise Exception(resource['error']['status']['message'])
    return (resource['code'] in [HTTP_OK, HTTP_ACCEPTED] and
            get_status(resource)['code'] == FINISHED)


def get_status(resource):
    """Extracts status info if present or sets the default if public

    """
    if not isinstance(resource, dict):
        raise ValueError("We need a complete resource to extract its status")
    if 'object' in resource:
        if resource['object'] is None:
            raise ValueError("The resource has no status info\n%s" % resource)
        resource = resource['object']
    if not resource.get('private', True):
        status = {'code': FINISHED}
    else:
        status = resource['status']
    return status


def check_resource(resource, get_method=None, query_string='', wait_time=1,
                   retries=None, raise_on_error=False, api=None):
    """Waits until a resource is finished.

       Given a resource and its corresponding get_method (if absent, it is
           derived from the source type)
           source, api.get_source
           dataset, api.get_dataset
           model, api.get_model
           prediction, api.get_prediction
           evaluation, api.get_evaluation
           ensemble, api.get_ensemble
           batch_prediction, api.get_batch_prediction
       and so on.
       It calls the get_method on the resource with the given query_string
       and waits with sleeping intervals of wait_time
       until the resource is in a final state (either FINISHED
       or FAULTY). The number of retries can be limited using the retries
       parameter.

    """
    def get_kwargs(resource_id):
        no_qs = [EVALUATION_RE, PREDICTION_RE, BATCH_PREDICTION_RE,
                 CENTROID_RE, BATCH_CENTROID_RE, ANOMALY_SCORE_RE,
                 BATCH_ANOMALY_SCORE_RE]
        if not (any(resource_re.match(resource_id) for
                    resource_re in no_qs)):
            return {'query_string': query_string}
        return {}

    kwargs = {}
    if isinstance(resource, basestring):
        resource_id = resource
    else:
        resource_id = get_resource_id(resource)
    resource_id = get_resource_id(resource)
    resource_type = get_resource_type(resource_id)
    if resource_id is None:
        raise ValueError("Failed to extract a valid resource id to check.")
    kwargs = get_kwargs(resource_id)

    if get_method is None and isinstance(api, BigML):
        get_method = api.getters[resource_type]
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


def exception_on_error(resource):
    """Raises exception if resource has error

    """
    if resource['error'] is not None:
        raise Exception(resource['error']['status']['message'])


def assign_dir(path):
    """Silently checks the path for existence or creates it.

       Returns either the path or None.
    """
    if not isinstance(path, basestring):
        return None
    try:
        return check_dir(path)
    except ValueError:
        return None


def stream_copy(response, filename):
    """Copies the contents of a response stream to a local file.

    """
    file_size = 0
    path = os.path.dirname(filename)
    check_dir(path)
    try:
        with open(filename, 'wb') as file_handle:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file_handle.write(chunk)
                    file_handle.flush()
                    file_size += len(chunk)
    except IOError:
        file_size = 0
    return file_size


def http_ok(resource):
    """Checking the validity of the http return code

    """
    if 'code' in resource:
        return resource['code'] in [HTTP_OK, HTTP_CREATED, HTTP_ACCEPTED]


def count(listing):
    """Count of existing resources

    """
    if 'meta' in listing and 'query_total' in listing['meta']:
        return listing['meta']['query_total']


##############################################################################
#
# Patch for requests
#
##############################################################################
def patch_requests():
    """ Monkey patches requests to get debug output.

    """
    def debug_request(method, url, **kwargs):
        """Logs the request and response content for api's remote requests

        """
        response = original_request(method, url, **kwargs)
        logging.debug("Data: {}".format(response.request.body))
        logging.debug("Response: {}".format(response.content))
        return response
    original_request = requests.api.request
    requests.api.request = debug_request


##############################################################################
#
# BigML class
#
##############################################################################


class BigML(PredictionHandler, ModelHandler, DatasetHandler, SourceHandler,
            ResourceHandler, BigMLConnection):
    """Entry point to create, retrieve, list, update, and delete
    sources, datasets, models and predictions.

    Full API documentation on the API can be found from BigML at:
        https://bigml.com/developers

    Resources are wrapped in a dictionary that includes:
        code: HTTP status code
        resource: The resource/id
        location: Remote location of the resource
        object: The resource itself
        error: An error code and message

    """
    def __init__(self, username=None, api_key=None, dev_mode=False,
                 debug=False, set_locale=False, storage=None, domain=None):
        """Initializes the BigML API.

        If left unspecified, `username` and `api_key` will default to the
        values of the `BIGML_USERNAME` and `BIGML_API_KEY` environment
        variables respectively.

        If `dev_mode` is set to `True`, the API will be used in development
        mode where the size of your datasets are limited but you are not
        charged any credits.

        If storage is set to a directory name, the resources obtained in
        CRU operations will be stored in the given directory.

        If domain is set, the api will point to the specified domain. Default
        will be the one in the environment variable `BIGML_DOMAIN` or
        `bigml.io` if missing. The expected domain argument is a string or a
        Domain object. See Domain class for details.

        """

        BigMLConnection.__init__(self, username=username, api_key=api_key,
                                 dev_mode=dev_mode, debug=debug,
                                 set_locale=set_locale, storage=storage,
                                 domain=domain)
        ResourceHandler.__init__(self)
        SourceHandler.__init__(self)
        DatasetHandler.__init__(self)
        ModelHandler.__init__(self)
        PredictionHandler.__init__(self)
        # Base Resource URLs
        
        self.evaluation_url = self.url + EVALUATION_PATH
        self.ensemble_url = self.url + ENSEMBLE_PATH
        self.batch_prediction_url = self.url + BATCH_PREDICTION_PATH
        self.cluster_url = self.url + CLUSTER_PATH
        self.centroid_url = self.url + CENTROID_PATH
        self.batch_centroid_url = self.url + BATCH_CENTROID_PATH
        self.anomaly_url = self.url + ANOMALY_PATH
        self.anomaly_score_url = self.url + ANOMALY_SCORE_PATH
        self.batch_anomaly_score_url = self.url + BATCH_ANOMALY_SCORE_PATH


        self.getters = {}
        for resource_type in RESOURCE_RE:
            method_name = RENAMED_RESOURCES.get(resource_type, resource_type)
            self.getters[resource_type] = getattr(self, "get_%s" % method_name)
        self.creaters = {}
        for resource_type in RESOURCE_RE:
            method_name = RENAMED_RESOURCES.get(resource_type, resource_type)
            self.creaters[resource_type] = getattr(self,
                                                   "create_%s" % method_name)
        self.updaters = {}
        for resource_type in RESOURCE_RE:
            method_name = RENAMED_RESOURCES.get(resource_type, resource_type)
            self.updaters[resource_type] = getattr(self,
                                                   "update_%s" % method_name)
        self.deleters = {}
        for resource_type in RESOURCE_RE:
            method_name = RENAMED_RESOURCES.get(resource_type, resource_type)
            self.deleters[resource_type] = getattr(self,
                                                   "delete_%s" % method_name)

    def ok(self, resource, query_string='', wait_time=1,
           retries=None, raise_on_error=False):
        """Waits until the resource is finished or faulty, updates it and
           returns True on success

        """
        if http_ok(resource):
            resource_type = get_resource_type(resource)
            resource.update(check_resource(resource,
                                           self.getters[resource_type],
                                           query_string=query_string,
                                           wait_time=wait_time,
                                           retries=retries,
                                           raise_on_error=raise_on_error))
            return True
        else:
            LOGGER.error("The resource couldn't be created: %s",
                         resource['error'])

    ##########################################################################
    #
    # Utils
    #
    ##########################################################################

    def connection_info(self):
        """Printable string: domain where the connection is bound and the
           credentials used.

        """
        info = u"Connecting to:\n"
        info += u"    %s\n" % self.general_domain
        if self.general_domain != self.prediction_domain:
            info += u"    %s (predictions only)\n" % self.prediction_domain

        info += u"\nAuthentication string:\n"
        info += u"    %s\n" % self.auth[1:]
        return info

    def get_fields(self, resource):
        """Retrieve fields used by a resource.

        Returns a dictionary with the fields that uses
        the resource keyed by Id.

        """

        def _get_fields_key(resource):
            """Returns the fields key from a resource dict

            """
            if resource['code'] in [HTTP_OK, HTTP_ACCEPTED]:
                if MODEL_RE.match(resource_id):
                    return resource['object']['model']['model_fields']
                else:
                    return resource['object']['fields']
            return None

        if isinstance(resource, dict) and 'resource' in resource:
            resource_id = resource['resource']
        elif (isinstance(resource, basestring) and (
                SOURCE_RE.match(resource) or DATASET_RE.match(resource) or
                MODEL_RE.match(resource) or PREDICTION_RE.match(resource))):
            resource_id = resource
            resource = self._get("%s%s" % (self.url, resource_id))
        else:
            LOGGER.error("Wrong resource id")
            return
        # Tries to extract fields information from resource dict. If it fails,
        # a get remote call is used to retrieve the resource by id.
        fields = None
        try:
            fields = _get_fields_key(resource)
        except KeyError:
            resource = self._get("%s%s" % (self.url, resource_id))
            fields = _get_fields_key(resource)

        return fields

    def pprint(self, resource, out=sys.stdout):
        """Pretty prints a resource or part of it.

        """

        if (isinstance(resource, dict)
                and 'object' in resource
                and 'resource' in resource):

            resource_id = resource['resource']
            if (SOURCE_RE.match(resource_id) or DATASET_RE.match(resource_id)
                    or MODEL_RE.match(resource_id)
                    or EVALUATION_RE.match(resource_id)
                    or ENSEMBLE_RE.match(resource_id)
                    or CLUSTER_RE.match(resource_id)
                    or ANOMALY_RE.match(resource_id)):
                out.write("%s (%s bytes)\n" % (resource['object']['name'],
                                               resource['object']['size']))
            elif PREDICTION_RE.match(resource['resource']):
                objective_field_name = (
                    resource['object']['fields'][
                        resource['object']['objective_fields'][0]]['name'])
                input_data = {}
                for key, value in resource['object']['input_data'].items():
                    try:
                        name = resource['object']['fields'][key]['name']
                    except KeyError:
                        name = key
                    input_data[name] = value

                prediction = (
                    resource['object']['prediction'][
                        resource['object']['objective_fields'][0]])
                out.write("%s for %s is %s\n" % (objective_field_name,
                                                 input_data,
                                                 prediction))
            out.flush()
        else:
            pprint.pprint(resource, out, indent=4)

    def status(self, resource):
        """Maps status code to string.

        """
        resource_id = get_resource_id(resource)
        if resource_id:
            resource = self._get("%s%s" % (self.url, resource_id))
            status = get_status(resource)
            code = status['code']
            return STATUSES.get(code, "UNKNOWN")
        else:
            status = get_status(resource)
            if status['code'] != UPLOADING:
                LOGGER.error("Wrong resource id")
                return
            return STATUSES[UPLOADING]

    def check_resource(self, resource,
                       query_string='', wait_time=1):
        """Check resource method.

        """
        return check_resource(resource,
                              query_string=query_string, wait_time=wait_time,
                              api=self)

    def check_origins(self, dataset, model, args, model_types=None,
                      wait_time=3, retries=10):
        """Returns True if the dataset and model needed to build
           the batch prediction or evaluation are finished. The args given
           by the user are modified to include the related ids in the
           create call.

           If model_types is a list, then we check any of the model types in
           the list.

        """

        def args_update(get_method):
            """Updates args when the resource is ready

            """
            if resource_id:
                check_resource(resource_id, get_method,
                               query_string=TINY_RESOURCE,
                               wait_time=wait_time, retries=retries,
                               raise_on_error=True)
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
            dataset = check_resource(dataset_id, self.get_dataset,
                                     query_string=TINY_RESOURCE,
                                     wait_time=wait_time, retries=retries,
                                     raise_on_error=True)
            resource_type = get_resource_type(model)
            if resource_type in model_types:
                resource_id = get_resource_id(model)
                args_update(self.getters[resource_type])
            elif resource_type == MODEL_PATH:
                resource_id = get_model_id(model)
                args_update(self.get_model)
            else:
                raise Exception("A model or ensemble id is needed as first"
                                " argument to create the resource."
                                " %s found." % resource_type)

        return dataset_id and resource_id

    ##########################################################################
    #
    # Evaluations
    # https://bigml.com/developers/evaluations
    #
    ##########################################################################
    def create_evaluation(self, model, dataset,
                          args=None, wait_time=3, retries=10):
        """Creates a new evaluation.

        """
        create_args = {}
        if args is not None:
            create_args.update(args)

        model_types = [ENSEMBLE_PATH, MODEL_PATH]
        origin_resources_checked = self.check_origins(
            dataset, model, create_args, model_types=model_types,
            wait_time=wait_time, retries=retries)

        if origin_resources_checked:
            body = json.dumps(create_args)
            return self._create(self.evaluation_url, body)

    def get_evaluation(self, evaluation):
        """Retrieves an evaluation.

           The evaluation parameter should be a string containing the
           evaluation id or the dict returned by create_evaluation.
           As evaluation is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, the function will
           return a dict that encloses the evaluation values and state info
           available at the time it is called.
        """
        check_resource_type(evaluation, EVALUATION_PATH,
                            message="An evaluation id is needed.")
        evaluation_id = get_evaluation_id(evaluation)
        if evaluation_id:
            return self._get("%s%s" % (self.url, evaluation_id))

    def list_evaluations(self, query_string=''):
        """Lists all your evaluations.

        """
        return self._list(self.evaluation_url, query_string)

    def update_evaluation(self, evaluation, changes):
        """Updates an evaluation.

        """
        check_resource_type(evaluation, EVALUATION_PATH,
                            message="An evaluation id is needed.")
        evaluation_id = get_evaluation_id(evaluation)
        if evaluation_id:
            body = json.dumps(changes)
            return self._update("%s%s" % (self.url, evaluation_id), body)

    def delete_evaluation(self, evaluation):
        """Deletes an evaluation.

        """
        check_resource_type(evaluation, EVALUATION_PATH,
                            message="An evaluation id is needed.")
        evaluation_id = get_evaluation_id(evaluation)
        if evaluation_id:
            return self._delete("%s%s" % (self.url, evaluation_id))

    ##########################################################################
    #
    # Ensembles
    # https://bigml.com/developers/ensembles
    #
    ##########################################################################
    def create_ensemble(self, datasets, args=None, wait_time=3, retries=10):
        """Creates an ensemble from a dataset or a list of datasets.

        """

        create_args = self._set_create_from_datasets_args(
            datasets, args=args, wait_time=wait_time, retries=retries)

        body = json.dumps(create_args)
        return self._create(self.ensemble_url, body)

    def get_ensemble(self, ensemble, query_string=''):
        """Retrieves an ensemble.

           The ensemble parameter should be a string containing the
           ensemble id or the dict returned by create_ensemble.
           As an ensemble is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, the function will
           return a dict that encloses the ensemble values and state info
           available at the time it is called.
        """
        check_resource_type(ensemble, ENSEMBLE_PATH,
                            message="An ensemble id is needed.")
        ensemble_id = get_ensemble_id(ensemble)
        if ensemble_id:
            return self._get("%s%s" % (self.url, ensemble_id),
                             query_string=query_string)

    def ensemble_is_ready(self, ensemble):
        """Checks whether a ensemble's status is FINISHED.

        """
        check_resource_type(ensemble, ENSEMBLE_PATH,
                            message="An ensemble id is needed.")
        resource = self.get_ensemble(ensemble)
        return resource_is_ready(resource)

    def list_ensembles(self, query_string=''):
        """Lists all your ensembles.

        """
        return self._list(self.ensemble_url, query_string)

    def update_ensemble(self, ensemble, changes):
        """Updates a ensemble.

        """
        check_resource_type(ensemble, ENSEMBLE_PATH,
                            message="An ensemble id is needed.")
        ensemble_id = get_ensemble_id(ensemble)
        if ensemble_id:
            body = json.dumps(changes)
            return self._update("%s%s" % (self.url, ensemble_id), body)

    def delete_ensemble(self, ensemble):
        """Deletes a ensemble.

        """
        check_resource_type(ensemble, ENSEMBLE_PATH,
                            message="An ensemble id is needed.")
        ensemble_id = get_ensemble_id(ensemble)
        if ensemble_id:
            return self._delete("%s%s" % (self.url, ensemble_id))

    ##########################################################################
    #
    # Batch Predictions
    # https://bigml.com/developers/batch_predictions
    #
    ##########################################################################
    def create_batch_prediction(self, model, dataset,
                                args=None, wait_time=3, retries=10):
        """Creates a new batch prediction.

           The model parameter can be:
            - a simple model
            - an ensemble

        """
        create_args = {}
        if args is not None:
            create_args.update(args)

        model_types = [ENSEMBLE_PATH, MODEL_PATH]
        origin_resources_checked = self.check_origins(
            dataset, model, create_args, model_types=model_types,
            wait_time=wait_time, retries=retries)
        if origin_resources_checked:
            body = json.dumps(create_args)
            return self._create(self.batch_prediction_url, body)

    def get_batch_prediction(self, batch_prediction):
        """Retrieves a batch prediction.

           The batch_prediction parameter should be a string containing the
           batch_prediction id or the dict returned by create_batch_prediction.
           As batch_prediction is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, the function will
           return a dict that encloses the batch_prediction values and state
           info available at the time it is called.
        """
        check_resource_type(batch_prediction, BATCH_PREDICTION_PATH,
                            message="A batch prediction id is needed.")
        batch_prediction_id = get_batch_prediction_id(batch_prediction)
        if batch_prediction_id:
            return self._get("%s%s" % (self.url, batch_prediction_id))

    def download_batch_prediction(self, batch_prediction, filename=None):
        """Retrieves the batch predictions file.

           Downloads predictions, that are stored in a remote CSV file. If
           a path is given in filename, the contents of the file are downloaded
           and saved locally. A file-like object is returned otherwise.
        """
        check_resource_type(batch_prediction, BATCH_PREDICTION_PATH,
                            message="A batch prediction id is needed.")
        batch_prediction_id = get_batch_prediction_id(batch_prediction)
        if batch_prediction_id:
            return self._download("%s%s%s" % (self.url, batch_prediction_id,
                                              DOWNLOAD_DIR), filename=filename)

    def source_from_batch_prediction(self, batch_prediction, args=None):
        """Creates a source from a batch prediction using the download url

        """
        check_resource_type(batch_prediction, BATCH_PREDICTION_PATH,
                            message="A batch prediction id is needed.")
        batch_prediction_id = get_batch_prediction_id(batch_prediction)
        if batch_prediction_id:
            download_url = "%s%s%s%s" % (self.url, batch_prediction_id,
                                         DOWNLOAD_DIR, self.auth)
            return self._create_remote_source(download_url, args=args)

    def list_batch_predictions(self, query_string=''):
        """Lists all your batch predictions.

        """
        return self._list(self.batch_prediction_url, query_string)

    def update_batch_prediction(self, batch_prediction, changes):
        """Updates a batch prediction.

        """
        check_resource_type(batch_prediction, BATCH_PREDICTION_PATH,
                            message="A batch prediction id is needed.")
        batch_prediction_id = get_batch_prediction_id(batch_prediction)
        if batch_prediction_id:
            body = json.dumps(changes)
            return self._update("%s%s" % (self.url, batch_prediction_id), body)

    def delete_batch_prediction(self, batch_prediction):
        """Deletes a batch prediction.

        """
        check_resource_type(batch_prediction, BATCH_PREDICTION_PATH,
                            message="A batch prediction id is needed.")
        batch_prediction_id = get_batch_prediction_id(batch_prediction)
        if batch_prediction_id:
            return self._delete("%s%s" % (self.url, batch_prediction_id))

    ##########################################################################
    #
    # Clusters
    # https://bigml.com/developers/clusters
    #
    ##########################################################################
    def create_cluster(self, datasets, args=None, wait_time=3, retries=10):
        """Creates a cluster from a `dataset` or a list o `datasets`.

        """
        create_args = self._set_create_from_datasets_args(
            datasets, args=args, wait_time=wait_time, retries=retries)

        body = json.dumps(create_args)
        return self._create(self.cluster_url, body)

    def get_cluster(self, cluster, query_string='',
                    shared_username=None, shared_api_key=None):
        """Retrieves a cluster.

           The model parameter should be a string containing the
           cluster id or the dict returned by create_cluster.
           As cluster is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, the function will
           return a dict that encloses the cluster values and state info
           available at the time it is called.

           If this is a shared cluster, the username and sharing api key must
           also be provided.
        """
        check_resource_type(cluster, CLUSTER_PATH,
                            message="A cluster id is needed.")
        cluster_id = get_cluster_id(cluster)
        if cluster_id:
            return self._get("%s%s" % (self.url, cluster_id),
                             query_string=query_string,
                             shared_username=shared_username,
                             shared_api_key=shared_api_key)

    def cluster_is_ready(self, cluster, **kwargs):
        """Checks whether a cluster's status is FINISHED.

        """
        check_resource_type(cluster, CLUSTER_PATH,
                            message="A cluster id is needed.")
        resource = self.get_cluster(cluster, **kwargs)
        return resource_is_ready(resource)

    def list_clusters(self, query_string=''):
        """Lists all your clusters.

        """
        return self._list(self.cluster_url, query_string)

    def update_cluster(self, cluster, changes):
        """Updates a cluster.

        """
        check_resource_type(cluster, CLUSTER_PATH,
                            message="A cluster id is needed.")
        cluster_id = get_cluster_id(cluster)
        if cluster_id:
            body = json.dumps(changes)
            return self._update("%s%s" % (self.url, cluster_id), body)

    def delete_cluster(self, cluster):
        """Deletes a cluster.

        """
        check_resource_type(cluster, CLUSTER_PATH,
                            message="A cluster id is needed.")
        cluster_id = get_cluster_id(cluster)
        if cluster_id:
            return self._delete("%s%s" % (self.url, cluster_id))

    ##########################################################################
    #
    # Centroids
    # https://bigml.com/developers/centroids
    #
    ##########################################################################
    def create_centroid(self, cluster, input_data=None,
                        args=None, wait_time=3, retries=10):
        """Creates a new centroid.

        """
        cluster_id = None
        resource_type = get_resource_type(cluster)
        if resource_type == CLUSTER_PATH:
            cluster_id = get_cluster_id(cluster)
            check_resource(cluster_id, self.get_cluster,
                           query_string=TINY_RESOURCE,
                           wait_time=wait_time, retries=retries,
                           raise_on_error=True)
        else:
            raise Exception("A cluster id is needed to create a"
                            " centroid. %s found." % resource_type)

        if input_data is None:
            input_data = {}
        create_args = {}
        if args is not None:
            create_args.update(args)
        create_args.update({
            "input_data": input_data})
        create_args.update({
            "cluster": cluster_id})

        body = json.dumps(create_args)
        return self._create(self.centroid_url, body,
                            verify=self.verify)

    def get_centroid(self, centroid):
        """Retrieves a centroid.

        """
        check_resource_type(centroid, CENTROID_PATH,
                            message="A centroid id is needed.")
        centroid_id = get_centroid_id(centroid)
        if centroid_id:
            return self._get("%s%s" % (self.url, centroid_id))

    def list_centroids(self, query_string=''):
        """Lists all your centroids.

        """
        return self._list(self.centroid_url, query_string)

    def update_centroid(self, centroid, changes):
        """Updates a centroid.

        """
        check_resource_type(centroid, CENTROID_PATH,
                            message="A centroid id is needed.")
        centroid_id = get_centroid_id(centroid)
        if centroid_id:
            body = json.dumps(changes)
            return self._update("%s%s" % (self.url, centroid_id), body)

    def delete_centroid(self, centroid):
        """Deletes a centroid.

        """
        check_resource_type(centroid, CENTROID_PATH,
                            message="A centroid id is needed.")
        centroid_id = get_centroid_id(centroid)
        if centroid_id:
            return self._delete("%s%s" % (self.url, centroid_id))

    ##########################################################################
    #
    # Batch Centroids
    # https://bigml.com/developers/batch_centroids
    #
    ##########################################################################
    def create_batch_centroid(self, cluster, dataset,
                              args=None, wait_time=3, retries=10):
        """Creates a new batch centroid.


        """
        create_args = {}
        if args is not None:
            create_args.update(args)

        origin_resources_checked = self.check_origins(
            dataset, cluster, create_args, model_types=[CLUSTER_PATH],
            wait_time=wait_time, retries=retries)

        if origin_resources_checked:
            body = json.dumps(create_args)
            return self._create(self.batch_centroid_url, body)

    def get_batch_centroid(self, batch_centroid):
        """Retrieves a batch centroid.

           The batch_centroid parameter should be a string containing the
           batch_centroid id or the dict returned by create_batch_centroid.
           As batch_centroid is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, the function will
           return a dict that encloses the batch_centroid values and state
           info available at the time it is called.
        """
        check_resource_type(batch_centroid, BATCH_CENTROID_PATH,
                            message="A batch centroid id is needed.")
        batch_centroid_id = get_batch_centroid_id(batch_centroid)
        if batch_centroid_id:
            return self._get("%s%s" % (self.url, batch_centroid_id))

    def download_batch_centroid(self, batch_centroid, filename=None):
        """Retrieves the batch centroid file.

           Downloads centroids, that are stored in a remote CSV file. If
           a path is given in filename, the contents of the file are downloaded
           and saved locally. A file-like object is returned otherwise.
        """
        check_resource_type(batch_centroid, BATCH_CENTROID_PATH,
                            message="A batch centroid id is needed.")
        batch_centroid_id = get_batch_centroid_id(batch_centroid)
        if batch_centroid_id:
            return self._download("%s%s%s" % (self.url, batch_centroid_id,
                                              DOWNLOAD_DIR), filename=filename)

    def list_batch_centroids(self, query_string=''):
        """Lists all your batch centroids.

        """
        return self._list(self.batch_centroid_url, query_string)

    def update_batch_centroid(self, batch_centroid, changes):
        """Updates a batch centroid.

        """
        check_resource_type(batch_centroid, BATCH_CENTROID_PATH,
                            message="A batch centroid id is needed.")
        batch_centroid_id = get_batch_centroid_id(batch_centroid)
        if batch_centroid_id:
            body = json.dumps(changes)
            return self._update("%s%s" % (self.url, batch_centroid_id), body)

    def delete_batch_centroid(self, batch_centroid):
        """Deletes a batch centroid.

        """
        check_resource_type(batch_centroid, BATCH_CENTROID_PATH,
                            message="A batch centroid id is needed.")
        batch_centroid_id = get_batch_centroid_id(batch_centroid)
        if batch_centroid_id:
            return self._delete("%s%s" % (self.url, batch_centroid_id))

    ##########################################################################
    #
    # Anomaly detector
    # https://bigml.com/developers/anomalies
    #
    ##########################################################################
    def create_anomaly(self, datasets, args=None, wait_time=3, retries=10):
        """Creates an anomaly detector from a `dataset` or a list o `datasets`.

        """
        create_args = self._set_create_from_datasets_args(
            datasets, args=args, wait_time=wait_time, retries=retries)

        body = json.dumps(create_args)
        return self._create(self.anomaly_url, body)

    def get_anomaly(self, anomaly, query_string='',
                    shared_username=None, shared_api_key=None):
        """Retrieves an anomaly detector.

           The anomaly parameter should be a string containing the
           anomaly id or the dict returned by create_anomaly.
           As the anomaly detector is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, the function will
           return a dict that encloses the model values and state info
           available at the time it is called.

           If this is a shared anomaly detector, the username and sharing api
           key must also be provided.
        """
        check_resource_type(anomaly, ANOMALY_PATH,
                            message="A anomaly id is needed.")
        anomaly_id = get_anomaly_id(anomaly)
        if anomaly_id:
            return self._get("%s%s" % (self.url, anomaly_id),
                             query_string=query_string,
                             shared_username=shared_username,
                             shared_api_key=shared_api_key)

    def anomaly_is_ready(self, anomaly, **kwargs):
        """Checks whether an anomaly detector's status is FINISHED.

        """
        check_resource_type(anomaly, ANOMALY_PATH,
                            message="An anomaly id is needed.")
        resource = self.get_anomaly(anomaly, **kwargs)
        return resource_is_ready(resource)

    def list_anomalies(self, query_string=''):
        """Lists all your anomaly detectors.

        """
        return self._list(self.anomaly_url, query_string)

    def update_anomaly(self, anomaly, changes):
        """Updates an anomaly detector.

        """
        check_resource_type(anomaly, ANOMALY_PATH,
                            message="An anomaly detector id is needed.")
        anomaly_id = get_anomaly_id(anomaly)
        if anomaly_id:
            body = json.dumps(changes)
            return self._update("%s%s" % (self.url, anomaly_id), body)

    def delete_anomaly(self, anomaly):
        """Deletes an anomaly detector.

        """
        check_resource_type(anomaly, ANOMALY_PATH,
                            message="An anomaly detector id is needed.")
        anomaly_id = get_anomaly_id(anomaly)
        if anomaly_id:
            return self._delete("%s%s" % (self.url, anomaly_id))


    ##########################################################################
    #
    # Anomaly scores
    # https://bigml.com/developers/anomalyscores
    #
    ##########################################################################
    def create_anomaly_score(self, anomaly, input_data=None,
                            args=None, wait_time=3, retries=10):
        """Creates a new anomaly score.

        """
        anomaly_id = None
        resource_type = get_resource_type(anomaly)
        if resource_type == ANOMALY_PATH:
            anomaly_id = get_anomaly_id(anomaly)
            check_resource(anomaly_id, self.get_anomaly,
                           query_string=TINY_RESOURCE,
                           wait_time=wait_time, retries=retries,
                           raise_on_error=True)
        else:
            raise Exception("An anomaly detector id is needed to create an"
                            " anomaly score. %s found." % resource_type)

        if input_data is None:
            input_data = {}
        create_args = {}
        if args is not None:
            create_args.update(args)
        create_args.update({
            "input_data": input_data})
        create_args.update({
            "anomaly": anomaly_id})

        body = json.dumps(create_args)
        return self._create(self.anomaly_score_url, body,
                            verify=self.verify)

    def get_anomaly_score(self, anomaly_score):
        """Retrieves an anomaly score.

        """
        check_resource_type(anomaly_score, ANOMALY_SCORE_PATH,
                            message="An anomaly score id is needed.")
        anomaly_score_id = get_anomaly_score_id(anomaly_score)
        if anomaly_score_id:
            return self._get("%s%s" % (self.url, anomaly_score_id))

    def list_anomaly_scores(self, query_string=''):
        """Lists all your anomaly_scores.

        """
        return self._list(self.anomaly_score_url, query_string)

    def update_anomaly_score(self, anomaly_score, changes):
        """Updates an anomaly_score.

        """
        check_resource_type(anomaly_score, ANOMALY_SCORE_PATH,
                            message="An anomaly_score id is needed.")
        anomaly_score_id = get_anomaly_score_id(anomaly_score)
        if anomaly_score_id:
            body = json.dumps(changes)
            return self._update("%s%s" % (self.url, anomaly_score_id), body)

    def delete_anomaly_score(self, anomaly_score):
        """Deletes an anomaly_score.

        """
        check_resource_type(anomaly_score, ANOMALY_SCORE_PATH,
                            message="An anomaly_score id is needed.")
        anomaly_score_id = get_anomaly_score_id(anomaly_score)
        if anomaly_score_id:
            return self._delete("%s%s" % (self.url, anomaly_score_id))


    ##########################################################################
    #
    # Batch Anomaly Scores
    # https://bigml.com/developers/batch_anomalyscores
    #
    ##########################################################################
    def create_batch_anomaly_score(self, anomaly, dataset,
                                   args=None, wait_time=3, retries=10):
        """Creates a new batch anomaly score.


        """
        create_args = {}
        if args is not None:
            create_args.update(args)

        origin_resources_checked = self.check_origins(
            dataset, anomaly, create_args, model_types=[ANOMALY_PATH],
            wait_time=wait_time, retries=retries)

        if origin_resources_checked:
            body = json.dumps(create_args)
            return self._create(self.batch_anomaly_score_url, body)

    def get_batch_anomaly_score(self, batch_anomaly_score):
        """Retrieves a batch anomaly score.

           The batch_anomaly_score parameter should be a string containing the
           batch_anomaly_score id or the dict returned by
           create_batch_anomaly_score.
           As batch_anomaly_score is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, the function will
           return a dict that encloses the batch_anomaly_score values and state
           info available at the time it is called.
        """
        check_resource_type(batch_anomaly_score, BATCH_ANOMALY_SCORE_PATH,
                            message="A batch anomaly score id is needed.")
        batch_anomaly_score_id = get_batch_anomaly_score_id(
            batch_anomaly_score)
        if batch_anomaly_score_id:
            return self._get("%s%s" % (self.url, batch_anomaly_score_id))

    def download_batch_anomaly_score(self, batch_anomaly_score, filename=None):
        """Retrieves the batch anomaly score file.

           Downloads anomaly scores, that are stored in a remote CSV file. If
           a path is given in filename, the contents of the file are downloaded
           and saved locally. A file-like object is returned otherwise.
        """
        check_resource_type(batch_anomaly_score, BATCH_ANOMALY_SCORE_PATH,
                            message="A batch anomaly score id is needed.")
        batch_anomaly_score_id = get_batch_anomaly_score_id(
            batch_anomaly_score)
        if batch_anomaly_score_id:
            return self._download("%s%s%s" % (self.url, batch_anomaly_score_id,
                                              DOWNLOAD_DIR), filename=filename)

    def list_batch_anomaly_scores(self, query_string=''):
        """Lists all your batch anomaly scores.

        """
        return self._list(self.batch_anomaly_score_url, query_string)

    def update_batch_anomaly_score(self, batch_anomaly_score, changes):
        """Updates a batch anomaly scores.

        """
        check_resource_type(batch_anomaly_score, BATCH_ANOMALY_SCORE_PATH,
                            message="A batch anomaly score id is needed.")
        batch_anomaly_score_id = get_batch_anomaly_score_id(
            batch_anomaly_score)
        if batch_anomaly_score_id:
            body = json.dumps(changes)
            return self._update("%s%s" % (self.url,
                                          batch_anomaly_score_id), body)

    def delete_batch_anomaly_score(self, batch_anomaly_score):
        """Deletes a batch anomaly score.

        """
        check_resource_type(batch_anomaly_score, BATCH_ANOMALY_SCORE_PATH,
                            message="A batch anomaly score id is needed.")
        batch_anomaly_score_id = get_batch_anomaly_score_id(
            batch_anomaly_score)
        if batch_anomaly_score_id:
            return self._delete("%s%s" % (self.url, batch_anomaly_score_id))
