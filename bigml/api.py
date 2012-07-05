# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2012 BigML
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
import logging
FORMAT = '%(asctime)-15s: %(message)s'
logging.basicConfig(format=FORMAT)
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

from urlparse import urlparse

# Base URL
BIGML_URL = "https://bigml.io/andromeda/"

SOURCE_PATH = 'source'
DATASET_PATH = 'dataset'
MODEL_PATH = 'model'
PREDICTION_PATH = 'prediction'

# Base Resource URLs
SOURCE_URL = BIGML_URL + SOURCE_PATH
DATASET_URL = BIGML_URL + DATASET_PATH
MODEL_URL = BIGML_URL + MODEL_PATH
PREDICTION_URL = BIGML_URL + PREDICTION_PATH

SOURCE_RE = re.compile(r'^%s/[a-f,0-9]{24}$' % SOURCE_PATH)
DATASET_RE = re.compile(r'^%s/[a-f,0-9]{24}$' % DATASET_PATH)
MODEL_RE = re.compile(r'^%s/[a-f,0-9]{24}$' % MODEL_PATH)
PREDICTION_RE = re.compile(r'^%s/[a-f,0-9]{24}$' % PREDICTION_PATH)

# Headers
SEND_JSON = {'Content-Type': 'application/json;charset=utf-8'}
ACCEPT_JSON = {'Accept': 'application/json;charset=utf-8'}

# HTTP Status Codes
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
HTTP_LENGTH_REQUIRED = 411
HTTP_INTERNAL_SERVER_ERROR = 500

# Resource status codes
WAITING = 0
QUEUED = 1
STARTED = 2
IN_PROGRESS = 3
SUMMARIZED = 4
FINISHED = 5
FAULTY = -1
UNKNOWN = -2
RUNNABLE = -3

STATUSES = {
    WAITING: "WAITING",
    QUEUED: "QUEUED",
    STARTED: "STARTED",
    IN_PROGRESS: "IN_PROGRESS",
    SUMMARIZED: "SUMMARIZED",
    FINISHED: "FINISHED",
    FAULTY: "FAULTY",
    UNKNOWN: "UNKNOWN",
    RUNNABLE: "RUNNABLE"
}

def _is_valid_remote_url(value):
    """Says if given value is a URL
        with scheme, netloc and path
        or not."""
    url = isinstance(value, basestring) and urlparse(value)
    return url and url.scheme and url.netloc and url.path

##############################################################################
#
# BigML class
#
##############################################################################


class BigML(object):
    """Entry point to create, retrieve, list, update, and delete
    sources, datasets, models and predictions.

    Full API documentation on the API can be found from BigML at:
        https://bigml.com/developers
    """
    def __init__(self, username=os.environ['BIGML_USERNAME'],
        api_key=os.environ['BIGML_API_KEY']):
        """Initialize httplib and set up username and api_key."""
        self.auth = "?username=%s;api_key=%s;" % (username, api_key)

    def _create(self, url, body):
        """Create a new resource. """
        code = HTTP_INTERNAL_SERVER_ERROR
        resource_id = None
        location = None
        resource = None
        error = {
            "status": {
                "code": code,
                "message": "The resource couldn't be created"}}
        try:
            response = requests.post(url + self.auth, headers=SEND_JSON,
                data=body)

            code = response.status_code

            if code == HTTP_CREATED:
                location = response.headers['location']
                resource = json.loads(response.content, 'utf-8')
                resource_id = resource['resource']
                error = None
            elif code in [
                HTTP_BAD_REQUEST,
                HTTP_UNAUTHORIZED,
                HTTP_PAYMENT_REQUIRED,
                HTTP_NOT_FOUND]:
                error = json.loads(response.content, 'utf-8')
            else:
                LOGGER.error("Unexpected error (%s)" % code)
                code = HTTP_INTERNAL_SERVER_ERROR

        except ValueError:
            LOGGER.error("Malformed response")
        except requests.ConnectionError:
            LOGGER.error("Connection error")
        except requests.Timeout:
            LOGGER.error("Request timed out")
        except requests.RequestException:
            LOGGER.error("Ambiguous exception occurred")

        return {
            'code': code,
            'resource': resource_id,
            'location': location,
            'object': resource,
            'error': error}

    def _get(self, url):
        """Retrieve a resource
        """
        code = HTTP_INTERNAL_SERVER_ERROR
        resource_id = None
        location = url
        resource = None
        error = {
            "status": {
                "code": HTTP_INTERNAL_SERVER_ERROR,
                "message": "The resource couldn't be retrieved"}}

        try:
            response = requests.get(url + self.auth, headers=ACCEPT_JSON)
            code = response.status_code

            if code == HTTP_OK:
                resource = json.loads(response.content, 'utf-8')
                resource_id = resource['resource']
                error = None
            elif code in [HTTP_BAD_REQUEST, HTTP_UNAUTHORIZED, HTTP_NOT_FOUND]:
                error = json.loads(response.content, 'utf-8')
            else:
                LOGGER.error("Unexpected error (%s)" % code)
                code = HTTP_INTERNAL_SERVER_ERROR

        except ValueError:
            LOGGER.error("Malformed response")
        except requests.ConnectionError:
            LOGGER.error("Connection error")
        except requests.Timeout:
            LOGGER.error("Request timed out")
        except requests.RequestException:
            LOGGER.error("Ambiguous exception occurred")

        return {
            'code': code,
            'resource': resource_id,
            'location': location,
            'object': resource,
            'error': error}

    def _list(self, url, query_string=''):
        """List resources
        """
        code = HTTP_INTERNAL_SERVER_ERROR
        meta = None
        resources = None
        error = {
            "status": {
                "code": code,
                "message": "The resource couldn't be listed"}}
        try:
            response = requests.get(url + self.auth + query_string,
                headers=ACCEPT_JSON)

            code = response.status_code

            if code == HTTP_OK:
                resource = json.loads(response.content, 'utf-8')
                meta = resource['meta']
                resources = resource['objects']
                error = None
            elif code in [HTTP_BAD_REQUEST, HTTP_UNAUTHORIZED, HTTP_NOT_FOUND]:
                error = json.loads(response.content, 'utf-8')
            else:
                LOGGER.error("Unexpected error (%s)" % code)
                code = HTTP_INTERNAL_SERVER_ERROR

        except ValueError:
            LOGGER.error("Malformed response")
        except requests.ConnectionError:
            LOGGER.error("Connection error")
        except requests.Timeout:
            LOGGER.error("Request timed out")
        except requests.RequestException:
            LOGGER.error("Ambiguous exception occurred")

        return {
            'code': code,
            'meta': meta,
            'objects': resources,
            'error': error}

    def _update(self, url, body):
        """Update a resource
        """
        code = HTTP_INTERNAL_SERVER_ERROR
        resource_id = None
        location = url
        resource = None
        error = {
            "status": {
                "code": code,
                "message": "The resource couldn't be updated"}}

        try:
            response = requests.put(url + self.auth,
                headers=SEND_JSON,
                data=body)

            code = response.status_code

            if code == HTTP_ACCEPTED:
                location = response.headers['location']
                resource = json.loads(response.content, 'utf-8')
                resource_id = resource['resource']
                error = None
            elif code in [
                HTTP_UNAUTHORIZED,
                HTTP_PAYMENT_REQUIRED,
                HTTP_METHOD_NOT_ALLOWED]:
                error = json.loads(response.content, 'utf-8')
            else:
                LOGGER.error("Unexpected error (%s)" % code)
                code = HTTP_INTERNAL_SERVER_ERROR

        except ValueError:
            LOGGER.error("Malformed response")
        except requests.ConnectionError:
            LOGGER.error("Connection error")
        except requests.Timeout:
            LOGGER.error("Request timed out")
        except requests.RequestException:
            LOGGER.error("Ambiguous exception occurred")

        return {
            'code': code,
            'resource': resource_id,
            'location': location,
            'object': resource,
            'error': error}

    def _delete(self, url):
        """Delete a resource
        """
        code = HTTP_INTERNAL_SERVER_ERROR
        error = {
            "status": {
                "code": code,
                "message": "The resource couldn't be deleted"}}

        try:
            response = requests.delete(url + self.auth)

            code = response.status_code

            if code == HTTP_NO_CONTENT:
                error = None
            elif code in [HTTP_BAD_REQUEST, HTTP_UNAUTHORIZED, HTTP_NOT_FOUND]:
                error = json.loads(response.content, 'utf-8')
            else:
                LOGGER.error("Unexpected error (%s)" % code)
                code = HTTP_INTERNAL_SERVER_ERROR

        except ValueError:
            LOGGER.error("Malformed response")
        except requests.ConnectionError:
            LOGGER.error("Connection error")
        except requests.Timeout:
            LOGGER.error("Request timed out")
        except requests.RequestException:
            LOGGER.error("Ambiguous exception occurred")


        return {
            'code': code,
            'error': error}

    ##########################################################################
    #
    # Utils
    #
    ##########################################################################

    def get_fields(self, resource):
        """Return a dictionary of fields"""
        if isinstance(resource, dict) and 'resource' in resource:
            resource_id = resource['resource']
        elif (isinstance(resource, basestring) and (
             SOURCE_RE.match(resource) or DATASET_RE.match(resource) or
                MODEL_RE.match(resource) or PREDICTION_RE.match(resource))):
            resource_id = resource
        else:
            LOGGER.error("Wrong resource id")
            return

        resource = self._get("%s%s" % (BIGML_URL, resource_id))
        if resource['code'] == HTTP_OK:
            if  MODEL_RE.match(resource_id):
                return resource['object']['model']['fields']
            else:
                return resource['object']['fields']
        return None

    def invert_dictionary(self, dictionary):
        """Invert a dictionary"""
        return dict([[value['name'], key]
            for key, value in dictionary.items()])

    def pprint(self, resource):
        """Pretty prints a resource or part of it"""
        pretty_print = pprint.PrettyPrinter(indent=4)
        if (isinstance(resource, dict) and
           'object' in resource and
           'resource' in resource):
            if SOURCE_RE.match(resource['resource']):
                print "%s (%s bytes)" % (resource['object']['name'],
                        resource['object']['size'])
            elif DATASET_RE.match(resource['resource']):
                print "%s (%s bytes)" % (resource['object']['name'],
                        resource['object']['size'])
            elif MODEL_RE.match(resource['resource']):
                print "%s (%s bytes)" % (resource['object']['name'],
                        resource['object']['size'])
            elif PREDICTION_RE.match(resource['resource']):
                objective_field_name = (
                    resource['object']['fields']
                        [resource['object']['objective_fields'][0]]['name'])
                input_data = dict(
                    [[resource['object']['fields'][key]['name'], value]
                        for key, value in
                            resource['object']['input_data'].items()])
                prediction = (
                    resource['object']['prediction']
                            [resource['object']['objective_fields'][0]])
                print("%s for %s is %s" % (objective_field_name, input_data,
                    prediction))
        else:
            pretty_print.pprint(resource)

    def status(self, resource):
        "Maps status code to string"

        if isinstance(resource, dict) and 'resource' in resource:
            resource_id = resource['resource']
        elif (isinstance(resource, basestring) and (
             SOURCE_RE.match(resource) or DATASET_RE.match(resource) or
                MODEL_RE.match(resource) or PREDICTION_RE.match(resource))):
            resource_id = resource
        else:
            LOGGER.error("Wrong resource id")
            return

        resource = self._get("%s%s" % (BIGML_URL, resource_id))
        code = resource['object']['status']['code']
        if code in STATUSES:
            return STATUSES[code]
        else:
            return "UNKNOWN"

    ##########################################################################
    #
    # Sources
    # https://bigml.com/developers/sources
    #
    ##########################################################################
    def _create_remote_source(self, url, args=None):
        """Create a new source. The source is available
           in the given URL instead of being a file
           in a local path."""
        if args is None:
            args = {}
        args.update({"remote": url})
        body = json.dumps(args)
        return self._create(SOURCE_URL, body)
    
    def _create_local_source(self, file_name, args=None):
        """Create a new source. The souce is a file in
           a local path."""
        if args is None:
            args = {}        
        elif 'source_parser' in args:
            args['source_parser'] = json.dumps(args['source_parser'])

        code = HTTP_INTERNAL_SERVER_ERROR
        resource_id = None
        location = None
        resource = None
        error = {
            "status": {
                "code": code,
                "message": "The resource couldn't be deleted"}}

        files = {os.path.basename(file_name): open(file_name, "rb")}
        try:
            response = requests.post(SOURCE_URL + self.auth,
                                files=files,
                                data=args)

            code = response.status_code

            if code == HTTP_CREATED:
                location = response.headers['location']
                resource = json.loads(response.content, 'utf-8')
                resource_id = resource['resource']
                error = None
            elif code in [
                HTTP_BAD_REQUEST,
                HTTP_UNAUTHORIZED,
                HTTP_PAYMENT_REQUIRED,
                HTTP_NOT_FOUND]:
                error = json.loads(response.content, 'utf-8')
            else:
                LOGGER.error("Unexpected error (%s)" % code)
                code = HTTP_INTERNAL_SERVER_ERROR

        except ValueError:
            LOGGER.error("Malformed response")
        except requests.ConnectionError:
            LOGGER.error("Connection error")
        except requests.Timeout:
            LOGGER.error("Request timed out")
        except requests.RequestException:
            LOGGER.error("Ambiguous exception occurred")

        return {
            'code': code,
            'resource': resource_id,
            'location': location,
            'object': resource,
            'error': error}

    def create_source(self, path, args=None):
        """Create a new source.
           The souce can be provided as a local file
           path or as a URL."""
        if not path:
            raise Exception('Source local path or a URL must be provided.')
        
        if _is_valid_remote_url(path):
            return self._create_remote_source(url=path, args=args)
        else:
            return self._create_local_source(file_name=path, args=args)

    def get_source(self, source):
        """Retrieve a source."""
        if isinstance(source, dict) and 'resource' in source:
            source_id = source['resource']
        elif isinstance(source, basestring) and SOURCE_RE.match(source):
            source_id = source
        else:
            LOGGER.error("Wrong source id")
            return
        return self._get("%s%s" % (BIGML_URL, source_id))

    def source_is_ready(self, source):
        """Check whether a source' status is FINISHED."""
        source = self.get_source(source)
        return (source['code'] == HTTP_OK and
            source['object']['status']['code'] == FINISHED)

    def list_sources(self, query_string=''):
        """List all your sources."""
        return self._list(SOURCE_URL, query_string)

    def update_source(self, source, changes):
        """Update a source."""
        if isinstance(source, dict) and 'resource' in source:
            source_id = source['resource']
        elif isinstance(source, basestring) and SOURCE_RE.match(source):
            source_id = source
        else:
            LOGGER.error("Wrong source id")
            return

        body = json.dumps(changes)
        return self._update("%s%s" % (BIGML_URL, source_id), body)

    def delete_source(self, source):
        """Delete a source."""
        if isinstance(source, dict) and 'resource' in source:
            source_id = source['resource']
        elif isinstance(source, basestring) and SOURCE_RE.match(source):
            source_id = source
        else:
            LOGGER.error("Wrong source id")
            return

        return self._delete("%s%s" % (BIGML_URL, source_id))

    ##########################################################################
    #
    # Datasets
    # https://bigml.com/developers/datasets
    #
    ##########################################################################
    def create_dataset(self, source, args=None, wait_time=3):
        """Create a dataset."""
        if isinstance(source, dict) and 'resource' in source:
            source_id = source['resource']
        elif isinstance(source, basestring) and SOURCE_RE.match(source):
            source_id = source
        else:
            LOGGER.error("Wrong source id")
            return

        if wait_time > 0:
            while not self.source_is_ready(source_id):
                time.sleep(wait_time)

        if args is None:
            args = {}
        args.update({
            "source": source_id})
        body = json.dumps(args)
        return self._create(DATASET_URL, body)

    def get_dataset(self, dataset):
        """Retrieve a dataset."""
        if isinstance(dataset, dict) and 'resource' in dataset:
            dataset_id = dataset['resource']
        elif isinstance(dataset, basestring) and DATASET_RE.match(dataset):
            dataset_id = dataset
        else:
            LOGGER.error("Wrong dataset id")
            return
        return self._get("%s%s" % (BIGML_URL, dataset_id))

    def dataset_is_ready(self, dataset):
        """Check whether a dataset' status is FINISHED."""
        resource = self.get_dataset(dataset)
        return (resource['code'] == HTTP_OK and
            resource['object']['status']['code'] == FINISHED)

    def list_datasets(self, query_string=''):
        """List all your datasets."""
        return self._list(DATASET_URL, query_string)

    def update_dataset(self, dataset, changes):
        """Update a dataset."""
        if isinstance(dataset, dict) and 'resource' in dataset:
            dataset_id = dataset['resource']
        elif isinstance(dataset, basestring) and DATASET_RE.match(dataset):
            dataset_id = dataset
        else:
            LOGGER.error("Wrong dataset id")
            return

        body = json.dumps(changes)
        return self._update("%s%s" % (BIGML_URL, dataset_id), body)

    def delete_dataset(self, dataset):
        """Delete a dataset."""
        if isinstance(dataset, dict) and 'resource' in dataset:
            dataset_id = dataset['resource']
        elif isinstance(dataset, basestring) and DATASET_RE.match(dataset):
            dataset_id = dataset
        else:
            LOGGER.error("Wrong dataset id")
            return

        return self._delete("%s%s" % (BIGML_URL, dataset_id))

    ##########################################################################
    #
    # Models
    # https://bigml.com/developers/models
    #
    ##########################################################################
    def create_model(self, dataset, args=None, wait_time=3):
        """Create a model."""
        if isinstance(dataset, dict) and 'resource' in dataset:
            dataset_id = dataset['resource']
        elif isinstance(dataset, basestring) and DATASET_RE.match(dataset):
            dataset_id = dataset
        else:
            LOGGER.error("Wrong dataset id")
            return

        if wait_time > 0:
            while not self.dataset_is_ready(dataset_id):
                time.sleep(wait_time)

        if args is None:
            args = {}
        args.update({
            "dataset": dataset_id})
        body = json.dumps(args)
        return self._create(MODEL_URL, body)

    def get_model(self, model):
        """Retrieve a model."""
        if isinstance(model, dict) and 'resource' in model:
            model_id = model['resource']
        elif isinstance(model, basestring) and MODEL_RE.match(model):
            model_id = model
        else:
            LOGGER.error("Wrong model id")
            return

        return self._get("%s%s" % (BIGML_URL, model_id))

    def model_is_ready(self, model):
        """Check whether a model' status is FINISHED."""
        resource = self.get_model(model)
        return (resource['code'] == HTTP_OK and
            resource['object']['status']['code'] == FINISHED)

    def list_models(self, query_string=''):
        """List all your models."""
        return self._list(MODEL_URL, query_string)

    def update_model(self, model, changes):
        """Update a model."""
        if isinstance(model, dict) and 'resource' in model:
            model_id = model['resource']
        elif isinstance(model, basestring) and MODEL_RE.match(model):
            model_id = model
        else:
            LOGGER.error("Wrong model id")
            return

        body = json.dumps(changes)
        return self._update("%s%s" % (BIGML_URL, model_id), body)

    def delete_model(self, model):
        """Delete a model."""
        if isinstance(model, dict) and 'resource' in model:
            model_id = model['resource']
        elif isinstance(model, basestring) and MODEL_RE.match(model):
            model_id = model
        else:
            LOGGER.error("Wrong model id")
            return

        return self._delete("%s%s" % (BIGML_URL, model_id))

    ##########################################################################
    #
    # Predictions
    # https://bigml.com/developers/predictions
    #
    ##########################################################################
    def create_prediction(self, model, input_data=None, args=None,
            wait_time=3):
        """Create a new prediction."""
        if isinstance(model, dict) and 'resource' in model:
            model_id = model['resource']
        elif isinstance(model, basestring) and MODEL_RE.match(model):
            model_id = model
        else:
            LOGGER.error("Wrong model id")
            return

        if wait_time > 0:
            while not self.model_is_ready(model_id):
                time.sleep(wait_time)

        if input_data is None:
            input_data = {}
        else:
            fields = self.get_fields(model_id)
            inverted_fields = self.invert_dictionary(fields)
            try:
                input_data = dict(
                    [[inverted_fields[key], value]
                     for key, value in input_data.items()])
            except KeyError, field:
                LOGGER.error("Wrong field name %s" % field)

        if args is None:
            args = {}
        args.update({
            "model": model_id,
            "input_data": input_data})
        body = json.dumps(args)
        return self._create(PREDICTION_URL, body)

    def get_prediction(self, prediction):
        """Retrieve a prediction."""
        if isinstance(prediction, dict) and 'resource' in prediction:
            prediction_id = prediction['resource']
        elif (isinstance(prediction, basestring) and
              PREDICTION_RE.match(prediction)):
            prediction_id = prediction
        else:
            LOGGER.error("Wrong prediction id")
            return

        return self._get("%s%s" % (BIGML_URL, prediction_id))

    def list_predictions(self, query_string=''):
        """List all your predictions."""
        return self._list(PREDICTION_URL, query_string)

    def update_prediction(self, prediction, changes):
        """Update a prediction."""
        if isinstance(prediction, dict) and 'resource' in prediction:
            prediction_id = prediction['resource']
        elif (isinstance(prediction, basestring) and
              PREDICTION_RE.match(prediction)):
            prediction_id = prediction
        else:
            LOGGER.error("Wrong prediction id")
            return

        body = json.dumps(changes)
        return self._update("%s%s" % (BIGML_URL, prediction_id), body)

    def delete_prediction(self, prediction):
        """Delete a prediction."""
        if isinstance(prediction, dict) and 'resource' in prediction:
            prediction_id = prediction['resource']
        elif (isinstance(prediction, basestring) and
             PREDICTION_RE.match(prediction)):
            prediction_id = prediction
        else:
            LOGGER.error("Wrong prediction id")
            return

        return self._delete("%s%s" %
            (BIGML_URL, prediction_id))
