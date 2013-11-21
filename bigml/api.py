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
import sys
import logging
LOG_FORMAT = '%(asctime)-15s: %(message)s'
LOGGER = logging.getLogger('BigML')

import time
import os
import re
import locale
import pprint

from threading import Thread

import requests
import urllib2
from poster.encode import multipart_encode, MultipartParam
from poster.streaminghttp import register_openers


try:
    import simplejson as json
except ImportError:
    import json

from bigml.util import (invert_dictionary, localize, is_url, check_dir,
                        clear_console_line, reset_console_line, console_log,
                        maybe_save)
from bigml.util import DEFAULT_LOCALE

register_openers()

# Base Domain
BIGML_DOMAIN = os.environ.get('BIGML_DOMAIN', 'bigml.io')

# Domain for prediction server
BIGML_PREDICTION_DOMAIN = os.environ.get('BIGML_PREDICTION_DOMAIN',
                                         BIGML_DOMAIN)
# Whether a prediction server is being used or not
PREDICTION_SERVER_ON = (BIGML_DOMAIN != BIGML_PREDICTION_DOMAIN)

# Protocol for prediction server
BIGML_PREDICTION_PROTOCOL = os.environ.get('BIGML_PREDICTION_PROTOCOL',
                                           'https')

# Check BigML.io host’s SSL certificate
# DO NOT CHANGE IT.
VERIFY = (BIGML_DOMAIN == "bigml.io")

# Check prediction server's SSL certificate
# DO NOT CHANGE IT.
VERIFY_PREDICTION_SERVER = (BIGML_PREDICTION_DOMAIN == "bigml.com")

# Base URL
BIGML_URL = 'https://%s/andromeda/' % BIGML_DOMAIN
# Development Mode URL
BIGML_DEV_URL = 'https://%s/dev/andromeda/' % BIGML_DOMAIN

# Prediction URL
BIGML_PREDICTION_URL = '%s://%s/andromeda/' % (BIGML_PREDICTION_PROTOCOL,
                                               BIGML_PREDICTION_DOMAIN)

# Basic resources
SOURCE_PATH = 'source'
DATASET_PATH = 'dataset'
MODEL_PATH = 'model'
PREDICTION_PATH = 'prediction'
EVALUATION_PATH = 'evaluation'
ENSEMBLE_PATH = 'ensemble'

# Resource Ids patterns
ID_PATTERN = '[a-f0-9]{24}'
SOURCE_RE = re.compile(r'^%s/%s$' % (SOURCE_PATH, ID_PATTERN))
DATASET_RE = re.compile(r'^(public/)?%s/%s$' % (DATASET_PATH, ID_PATTERN))
MODEL_RE = re.compile(r'^(public/)?%s/%s$|^shared/model/[a-zA-Z0-9]{27}$' % (
    MODEL_PATH, ID_PATTERN))
PREDICTION_RE = re.compile(r'^%s/%s$' % (PREDICTION_PATH, ID_PATTERN))
EVALUATION_RE = re.compile(r'^%s/%s$' % (EVALUATION_PATH, ID_PATTERN))
ENSEMBLE_RE = re.compile(r'^%s/%s$' % (ENSEMBLE_PATH, ID_PATTERN))
RESOURCE_RE = {
    'source': SOURCE_RE,
    'dataset': DATASET_RE,
    'model': MODEL_RE,
    'prediction': PREDICTION_RE,
    'evaluation': EVALUATION_RE,
    'ensemble': ENSEMBLE_RE}


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
    """Returns a evaluation/id.

    """
    return get_resource(EVALUATION_RE, evaluation)


def get_ensemble_id(ensemble):
    """Returns a ensemble/id.

    """
    return get_resource(ENSEMBLE_RE, ensemble)


def get_resource_id(resource):
    """Returns the resource id if it falls in one of the registered types

    """
    if isinstance(resource, dict) and 'resource' in resource:
        return resource['resource']
    elif isinstance(resource, basestring) and (
            SOURCE_RE.match(resource)
            or DATASET_RE.match(resource)
            or MODEL_RE.match(resource)
            or PREDICTION_RE.match(resource)
            or EVALUATION_RE.match(resource)
            or ENSEMBLE_RE.match(resource)):
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
    return (resource['code'] == HTTP_OK and
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


def check_resource(resource, get_method, query_string='', wait_time=1):
    """Waits until a resource is finished.

       Given a resource and its corresponding get_method
           source, api.get_source
           dataset, api.get_dataset
           model, api.get_model
           prediction, api.get_prediction
           evaluation, api.get_evaluation
           ensemble, api.get_ensemble
       it calls the get_method on the resource with the given query_string
       and waits with sleeping intervals of wait_time
       until the resource is in a final state (either FINISHED
       or FAULTY)

    """
    def get_kwargs(resource_id):
        if not (EVALUATION_RE.match(resource_id) or
                PREDICTION_RE.match(resource_id)):
            return {'query_string': query_string}
        return {}

    kwargs = {}
    if isinstance(resource, basestring):
        resource_id = resource
        kwargs = get_kwargs(resource_id)
        resource = get_method(resource, **kwargs)
    else:
        resource_id = get_resource_id(resource)
        if resource_id is None:
            raise ValueError("Failed to extract a valid resource id to check.")
        kwargs = get_kwargs(resource_id)

    while True:
        status = get_status(resource)
        code = status['code']
        if code == FINISHED:
            return resource
        elif code == FAULTY:
            raise ValueError(status)
        time.sleep(wait_time)
        resource = get_method(resource, **kwargs)


def error_message(resource, resource_type='resource', method=None):
    """Error message for each type of resource

    """
    error = None
    error_info = None
    if isinstance(resource, dict):
        if 'error' in resource:
            error_info = resource['error']
        elif ('code' in resource
              and 'status' in resource):
            error_info = resource
    if error_info is not None and 'code' in error_info:
        code = error_info['code']
        if ('status' in error_info and
                'message' in error_info['status']):
            error = error_info['status']['message']
        if code == HTTP_NOT_FOUND and method == 'get':
            alternate_message = ''
            if BIGML_DOMAIN != 'bigml.io':
                alternate_message = (
                    u'- The %s was not created in %s.\n' % (
                        resource_type, BIGML_DOMAIN))
            error += (
                u'\nCouldn\'t find a %s matching the given'
                u' id. The most probable causes are:\n\n%s'
                u'- A typo in the %s\'s id.\n'
                u'- The %s id cannot be accessed with your credentials.\n'
                u'\nDouble-check your %s and'
                u' credentials info and retry.' % (
                    resource_type, alternate_message, resource_type,
                    resource_type, resource_type))
            return error
        if code == HTTP_UNAUTHORIZED:
            error += u'\nDouble-check your credentials, please.'
            return error
        if code == HTTP_BAD_REQUEST:
            error += u'\nDouble-check the arguments for the call, please.'
            return error
        elif code == HTTP_PAYMENT_REQUIRED:
            error += (u'\nYou\'ll need to buy some more credits to perform'
                      u' the chosen action')
            return error

    return "Invalid %s structure:\n\n%s" % (resource_type, resource)


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


class BigML(object):
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
                 debug=False, set_locale=False, storage=None):
        """Initializes the BigML API.

        If left unspecified, `username` and `api_key` will default to the
        values of the `BIGML_USERNAME` and `BIGML_API_KEY` environment
        variables respectively.

        If `dev_mode` is set to `True`, the API will be used in development
        mode where the size of your datasets are limited but you are not
        charged any credits.

        If storage is set to a directory name, the resources obtained in
        CRU operations will be stored in the given directory.

        """

        logging_level = logging.ERROR
        if debug:
            logging_level = logging.DEBUG
            patch_requests()

        logging.basicConfig(format=LOG_FORMAT,
                            level=logging_level,
                            stream=sys.stdout)

        if username is None:
            try:
                username = os.environ['BIGML_USERNAME']
            except KeyError:
                sys.exit("Cannot find BIGML_USERNAME in your environment")

        if api_key is None:
            try:
                api_key = os.environ['BIGML_API_KEY']
            except KeyError:
                sys.exit("Cannot find BIGML_API_KEY in your environment")

        self.auth = "?username=%s;api_key=%s;" % (username, api_key)
        self.dev_mode = dev_mode

        if dev_mode:
            self.url = BIGML_DEV_URL
            self.prediction_url = BIGML_DEV_URL
        else:
            self.url = BIGML_URL
            self.prediction_url = BIGML_PREDICTION_URL

        # Base Resource URLs
        self.source_url = self.url + SOURCE_PATH
        self.dataset_url = self.url + DATASET_PATH
        self.model_url = self.url + MODEL_PATH
        self.prediction_url = self.prediction_url + PREDICTION_PATH
        self.evaluation_url = self.url + EVALUATION_PATH
        self.ensemble_url = self.url + ENSEMBLE_PATH

        if set_locale:
            locale.setlocale(locale.LC_ALL, DEFAULT_LOCALE)
        self.storage = assign_dir(storage)

    def _create(self, url, body, verify=VERIFY):
        """Creates a new remote resource.

        Posts `body` in JSON to `url` to create a new remote resource.

        Returns a BigML resource wrapped in a dictionary that includes:
            code: HTTP status code
            resource: The resource/id
            location: Remote location of the resource
            object: The resource itself
            error: An error code and message

        """
        code = HTTP_INTERNAL_SERVER_ERROR
        resource_id = None
        location = None
        resource = None
        error = {
            "status": {
                "code": code,
                "message": "The resource couldn't be created"}}

        # If a prediction server is in use, the first prediction request might
        # return a HTTP_ACCEPTED (202) while the model or ensemble is being
        # downloaded.
        code = HTTP_ACCEPTED
        while code == HTTP_ACCEPTED:
            try:
                response = requests.post(url + self.auth,
                                         headers=SEND_JSON,
                                         data=body, verify=verify)
                code = response.status_code

                if code in [HTTP_CREATED, HTTP_OK]:
                    if 'location' in response.headers:
                        location = response.headers['location']
                    resource = json.loads(response.content, 'utf-8')
                    resource_id = resource['resource']
                    error = None
                elif code in [HTTP_BAD_REQUEST,
                              HTTP_UNAUTHORIZED,
                              HTTP_PAYMENT_REQUIRED,
                              HTTP_FORBIDDEN,
                              HTTP_NOT_FOUND]:
                    error = json.loads(response.content, 'utf-8')
                    LOGGER.error(error_message(error, method='create'))
                elif code != HTTP_ACCEPTED:
                    LOGGER.error("Unexpected error (%s)" % code)
                    code = HTTP_INTERNAL_SERVER_ERROR

            except ValueError:
                LOGGER.error("Malformed response")
                code = HTTP_INTERNAL_SERVER_ERROR
            except requests.ConnectionError:
                LOGGER.error("Connection error")
                code = HTTP_INTERNAL_SERVER_ERROR
            except requests.Timeout:
                LOGGER.error("Request timed out")
                code = HTTP_INTERNAL_SERVER_ERROR
            except requests.RequestException:
                LOGGER.error("Ambiguous exception occurred")
                code = HTTP_INTERNAL_SERVER_ERROR

        return maybe_save(resource_id, self.storage, code,
                          location, resource, error)

    def _get(self, url, query_string='',
             shared_username=None, shared_api_key=None):
        """Retrieves a remote resource.

        Uses HTTP GET to retrieve a BigML `url`.

        Returns a BigML resource wrapped in a dictionary that includes:
            code: HTTP status code
            resource: The resource/id
            location: Remote location of the resource
            object: The resource itself
            error: An error code and message

        """
        code = HTTP_INTERNAL_SERVER_ERROR
        resource_id = None
        location = url
        resource = None
        error = {
            "status": {
                "code": HTTP_INTERNAL_SERVER_ERROR,
                "message": "The resource couldn't be retrieved"}}
        auth = (self.auth if shared_username is None
                else "?username=%s;api_key=%s" % (
                    shared_username, shared_api_key))
        try:
            response = requests.get(url + self.auth + query_string,
                                    headers=ACCEPT_JSON,
                                    verify=VERIFY)
            code = response.status_code

            if code == HTTP_OK:
                resource = json.loads(response.content, 'utf-8')
                resource_id = resource['resource']
                error = None
            elif code in [HTTP_BAD_REQUEST, HTTP_UNAUTHORIZED, HTTP_NOT_FOUND]:
                error = json.loads(response.content, 'utf-8')
                LOGGER.error(error_message(error, method='get'))
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

        return maybe_save(resource_id, self.storage, code,
                          location, resource, error)

    def _list(self, url, query_string=''):
        """Lists all existing remote resources.

        Resources in listings can be filterd using `query_string` formatted
        according to the syntax and fields labeled as filterable in the BigML
        documentation for each resource.

        Sufixes:
            __lt: less than
            __lte: less than or equal to
            __gt: greater than
            __gte: greater than or equal to

        For example:

            'size__gt=1024'

        Resources can also be sortened including a sort_by statement within
        the `query_sting`. For example:

            'order_by=size'

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
                                    headers=ACCEPT_JSON, verify=VERIFY)
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
        """Updates a remote resource.

        Uses PUT to update a BigML resource. Only the new fields that
        are going to be updated need to be included in the `body`.

        Returns a resource wrapped in a dictionary:
            code: HTTP_ACCEPTED if the update has been OK or an error
                  code otherwise.
            resource: Resource/id
            location: Remote location of the resource.
            object: The new updated resource
            error: Error code if any. None otherwise

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
                                    data=body, verify=VERIFY)

            code = response.status_code

            if code == HTTP_ACCEPTED:
                resource = json.loads(response.content, 'utf-8')
                resource_id = resource['resource']
                error = None
            elif code in [HTTP_UNAUTHORIZED,
                          HTTP_PAYMENT_REQUIRED,
                          HTTP_METHOD_NOT_ALLOWED]:
                error = json.loads(response.content, 'utf-8')
                LOGGER.error(error_message(error, method='update'))
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

        return maybe_save(resource_id, self.storage, code,
                          location, resource, error)

    def _delete(self, url):
        """Permanently deletes a remote resource.

        If the request is successful the status `code` will be HTTP_NO_CONTENT
        and `error` will be None. Otherwise, the `code` will be an error code
        and `error` will be provide a specific code and explanation.

        """
        code = HTTP_INTERNAL_SERVER_ERROR
        error = {
            "status": {
                "code": code,
                "message": "The resource couldn't be deleted"}}

        try:
            response = requests.delete(url + self.auth, verify=VERIFY)
            code = response.status_code

            if code == HTTP_NO_CONTENT:
                error = None
            elif code in [HTTP_BAD_REQUEST, HTTP_UNAUTHORIZED, HTTP_NOT_FOUND]:
                error = json.loads(response.content, 'utf-8')
                LOGGER.error(error_message(error, method='delete'))
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
        """Retrieve fields used by a resource.

        Returns a dictionary with the fields that uses
        the resource keyed by Id.

        """
        if isinstance(resource, dict) and 'resource' in resource:
            resource_id = resource['resource']
        elif (isinstance(resource, basestring) and (
              SOURCE_RE.match(resource) or DATASET_RE.match(resource) or
              MODEL_RE.match(resource) or PREDICTION_RE.match(resource))):
            resource_id = resource
        else:
            LOGGER.error("Wrong resource id")
            return

        resource = self._get("%s%s" % (self.url, resource_id))
        if resource['code'] == HTTP_OK:
            if MODEL_RE.match(resource_id):
                return resource['object']['model']['model_fields']
            else:
                return resource['object']['fields']
        return None

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
                    or ENSEMBLE_RE.match(resource_id)):
                out.write("%s (%s bytes)\n" % (resource['object']['name'],
                                               resource['object']['size']))
            elif PREDICTION_RE.match(resource['resource']):
                objective_field_name = (resource['object']['fields']
                                                [resource['object']
                                                 ['objective_fields'][0]]
                                                ['name'])
                input_data = (dict([[resource['object']['fields'][key]['name'],
                                    value]
                                    for key, value in
                                    resource['object']['input_data'].items()]))
                prediction = (
                    resource['object']['prediction']
                            [resource['object']['objective_fields'][0]])
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
        if not resource_id:
            LOGGER.error("Wrong resource id")
            return
        resource = self._get("%s%s" % (self.url, resource_id))
        status = get_status(resource)
        code = status['code']
        if code in STATUSES:
            return STATUSES[code]
        else:
            return "UNKNOWN"

    def check_resource(self, resource, get_method,
                       query_string='', wait_time=1):
        """Deprecated method. Use check_resource function instead.

        """
        return check_resource(resource, get_method,
                              query_string=query_string, wait_time=wait_time)

    ##########################################################################
    #
    # Sources
    # https://bigml.com/developers/sources
    #
    ##########################################################################
    def _create_remote_source(self, url, args=None):
        """Creates a new source using a URL

        """
        if args is None:
            args = {}
        args.update({"remote": url})
        body = json.dumps(args)
        return self._create(self.source_url, body)

    def _create_local_source(self, file_name, args=None):
        """Creates a new source using a local file.

        This function is now DEPRECATED as "requests" do not stream the file
        content what limited the size of local files to a small number of GBs.

        """
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
                "message": "The resource couldn't be created"}}

        try:
            files = {os.path.basename(file_name): open(file_name, "rb")}
        except IOError:
            sys.exit("ERROR: cannot read training set")

        try:
            response = requests.post(self.source_url + self.auth,
                                     files=files,
                                     data=args, verify=VERIFY)

            code = response.status_code

            if code == HTTP_CREATED:
                location = response.headers['location']
                resource = json.loads(response.content, 'utf-8')
                resource_id = resource['resource']
                error = None
            elif code in [HTTP_BAD_REQUEST,
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

    def _upload_source(self, args, source, out=sys.stdout):
        """Uploads a source asynchronously.

        """

        def update_progress(param, current, total):
            """Updates source's progress.

            """
            progress = round(current * 1.0 / total, 2)
            if progress < 1.0:
                source['object']['status']['progress'] = progress

        resource = self._process_source(source['resource'], source['location'],
                                        source['object'],
                                        args=args, progress_bar=True,
                                        callback=update_progress, out=out)
        source['code'] = resource['code']
        source['resource'] = resource['resource']
        source['location'] = resource['location']
        source['object'] = resource['object']
        source['error'] = resource['error']

    def _stream_source(self, file_name, args=None, async=False,
                       progress_bar=False, out=sys.stdout):
        """Creates a new source.

        """

        def draw_progress_bar(param, current, total):
            """Draws a text based progress report.

            """
            pct = 100 - ((total - current) * 100) / (total)
            console_log("Uploaded %s out of %s bytes [%s%%]" % (
                localize(current), localize(total), pct))

        if args is None:
            args = {}
        elif 'source_parser' in args:
            args['source_parser'] = json.dumps(args['source_parser'])

        resource_id = None
        location = None
        resource = None
        error = None

        try:
            if isinstance(file_name, basestring):
                args.update({os.path.basename(file_name):
                             open(file_name, "rb")})
            else:
                args = args.items()
                name = '<none>'
                args.append(MultipartParam(name, filename=name,
                                           fileobj=file_name))

        except IOError, exception:
            sys.exit("Error: cannot read training set. %s" % str(exception))

        if async:
            source = {
                'code': HTTP_ACCEPTED,
                'resource': resource_id,
                'location': location,
                'object': {'status': {'message': 'The upload is in progress',
                                      'code': UPLOADING,
                                      'progress': 0.0}},
                'error': error}
            upload_args = (args, source)
            thread = Thread(target=self._upload_source,
                            args=upload_args,
                            kwargs={'out': out})
            thread.start()
            return source
        return self._process_source(resource_id, location, resource,
                                    args=args, progress_bar=progress_bar,
                                    callback=draw_progress_bar, out=out)

    def _process_source(self, resource_id, location, resource,
                        args=None, progress_bar=False, callback=None,
                        out=sys.stdout):
        """Creates a new source.

        """
        code = HTTP_INTERNAL_SERVER_ERROR
        error = {
            "status": {
                "code": code,
                "message": "The resource couldn't be created"}}

        if progress_bar and callback is not None:
            body, headers = multipart_encode(args, cb=callback)
        else:
            body, headers = multipart_encode(args)

        request = urllib2.Request(self.source_url + self.auth, body, headers)

        try:
            response = urllib2.urlopen(request)
            clear_console_line(out=out)
            reset_console_line(out=out)
            code = response.getcode()
            if code == HTTP_CREATED:
                location = response.headers['location']
                content = response.read()
                resource = json.loads(content, 'utf-8')
                resource_id = resource['resource']
                error = {}
        except ValueError:
            LOGGER.error("Malformed response")
        except urllib2.HTTPError, exception:
            LOGGER.error("Error %s", exception.code)
            code = exception.code
            if code in [HTTP_BAD_REQUEST,
                        HTTP_UNAUTHORIZED,
                        HTTP_PAYMENT_REQUIRED,
                        HTTP_NOT_FOUND]:
                content = exception.read()
                error = json.loads(content, 'utf-8')
            else:
                LOGGER.error("Unexpected error (%s)" % code)
                code = HTTP_INTERNAL_SERVER_ERROR

        except urllib2.URLError, exception:
            LOGGER.error("Error establishing connection")
            error = exception.args
        return {
            'code': code,
            'resource': resource_id,
            'location': location,
            'object': resource,
            'error': error}

    def create_source(self, path=None, args=None, async=False,
                      progress_bar=False, out=sys.stdout):
        """Creates a new source.

           The source can be a local file path or a URL.

        """

        if path is None:
            raise Exception('A local path or a valid URL must be provided.')

        if is_url(path):
            return self._create_remote_source(url=path, args=args)
        else:
            return self._stream_source(file_name=path, args=args, async=async,
                                       progress_bar=progress_bar, out=out)

    def get_source(self, source, query_string=''):
        """Retrieves a remote source.

           The source parameter should be a string containing the
           source id or the dict returned by create_source.
           As source is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, thet function will
           return a dict that encloses the source values and state info
           available at the time it is called.

        """
        check_resource_type(source, SOURCE_PATH,
                            message="A source id is needed.")
        source_id = get_source_id(source)
        if source_id:
            return self._get("%s%s" % (self.url, source_id),
                             query_string=query_string)

    def source_is_ready(self, source):
        """Checks whether a source' status is FINISHED.

        """
        check_resource_type(source, SOURCE_PATH,
                            message="A source id is needed.")
        source = self.get_source(source)
        return resource_is_ready(source)

    def list_sources(self, query_string=''):
        """Lists all your remote sources.

        """
        return self._list(self.source_url, query_string)

    def update_source(self, source, changes):
        """Updates a source.

        Updates remote `source` with `changes'.

        """
        check_resource_type(source, SOURCE_PATH,
                            message="A source id is needed.")
        source_id = get_source_id(source)
        if source_id:
            body = json.dumps(changes)
            return self._update("%s%s" % (self.url, source_id), body)

    def delete_source(self, source):
        """Deletes a remote source permanently.

        """
        check_resource_type(source, SOURCE_PATH,
                            message="A source id is needed.")
        source_id = get_source_id(source)
        if source_id:
            return self._delete("%s%s" % (self.url, source_id))

    ##########################################################################
    #
    # Datasets
    # https://bigml.com/developers/datasets
    #
    ##########################################################################
    def create_dataset(self, source_or_dataset, args=None,
                       wait_time=3, retries=10):
        """Creates a remote dataset.

        Uses remote `source` or `dataset` to create a new dataset using the
        arguments in `args`.
        If `wait_time` is higher than 0 then the dataset creation
        request is not sent until the `source` has been created successfuly.

        """
        if args is None:
            args = {}

        resource_type = get_resource_type(source_or_dataset)
        if resource_type == SOURCE_PATH:
            source_id = get_source_id(source_or_dataset)
            if source_id:
                if wait_time > 0:
                    count = 0
                    while (not self.source_is_ready(source_id) and
                           count < retries):
                        time.sleep(wait_time)
                        count += 1
                args.update({
                    "source": source_id})
        elif resource_type == DATASET_PATH:
            dataset_id = get_dataset_id(source_or_dataset)
            if dataset_id:
                if wait_time > 0:
                    count = 0
                    while (not self.dataset_is_ready(dataset_id) and
                           count < retries):
                        time.sleep(wait_time)
                        count += 1
            args.update({
                "origin_dataset": dataset_id})
        else:
            raise Exception("A source or dataset id is needed to create a"
                            " dataset. %s found." % resource_type)

        body = json.dumps(args)
        return self._create(self.dataset_url, body)

    def get_dataset(self, dataset, query_string=''):
        """Retrieves a dataset.

           The dataset parameter should be a string containing the
           dataset id or the dict returned by create_dataset.
           As dataset is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, the function will
           return a dict that encloses the dataset values and state info
           available at the time it is called.
        """
        check_resource_type(dataset, DATASET_PATH,
                            message="A dataset id is needed.")
        dataset_id = get_dataset_id(dataset)
        if dataset_id:
            return self._get("%s%s" % (self.url, dataset_id),
                             query_string=query_string)

    def dataset_is_ready(self, dataset):
        """Check whether a dataset' status is FINISHED.

        """
        check_resource_type(dataset, DATASET_PATH,
                            message="A dataset id is needed.")
        resource = self.get_dataset(dataset)
        return resource_is_ready(resource)

    def list_datasets(self, query_string=''):
        """Lists all your datasets.

        """
        return self._list(self.dataset_url, query_string)

    def update_dataset(self, dataset, changes):
        """Updates a dataset.

        """
        check_resource_type(dataset, DATASET_PATH,
                            message="A dataset id is needed.")
        dataset_id = get_dataset_id(dataset)
        if dataset_id:
            body = json.dumps(changes)
            return self._update("%s%s" % (self.url, dataset_id), body)

    def delete_dataset(self, dataset):
        """Deletes a dataset.

        """
        check_resource_type(dataset, DATASET_PATH,
                            message="A dataset id is needed.")
        dataset_id = get_dataset_id(dataset)
        if dataset_id:
            return self._delete("%s%s" % (self.url, dataset_id))

    ##########################################################################
    #
    # Models
    # https://bigml.com/developers/models
    #
    ##########################################################################
    def create_model(self, dataset, args=None, wait_time=3, retries=10):
        """Creates a model.

        """
        check_resource_type(dataset, DATASET_PATH,
                            message="A dataset id is needed to create a"
                                    " model.")
        dataset_id = get_dataset_id(dataset)

        if dataset_id:
            if wait_time > 0:
                count = 0
                while (not self.dataset_is_ready(dataset_id) and
                       count < retries):
                    time.sleep(wait_time)
                    count += 1

            if args is None:
                args = {}
            args.update({
                "dataset": dataset_id})

            body = json.dumps(args)
            return self._create(self.model_url, body)

    def get_model(self, model, query_string='',
                  shared_username=None, shared_api_key=None):
        """Retrieves a model.

           The model parameter should be a string containing the
           model id or the dict returned by create_model.
           As model is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, the function will
           return a dict that encloses the model values and state info
           available at the time it is called.

           If this is a shared model, the username and sharing api key must
           also be provided.
        """
        check_resource_type(model, MODEL_PATH,
                            message="A model id is needed.")
        model_id = get_model_id(model)
        if model_id:
            return self._get("%s%s" % (self.url, model_id),
                             query_string=query_string,
                             shared_username=shared_username,
                             shared_api_key=shared_api_key)

    def model_is_ready(self, model, **kwargs):
        """Checks whether a model's status is FINISHED.

        """
        check_resource_type(model, MODEL_PATH,
                            message="A model id is needed.")
        resource = self.get_model(model, **kwargs)
        return resource_is_ready(resource)

    def list_models(self, query_string=''):
        """Lists all your models.

        """
        return self._list(self.model_url, query_string)

    def update_model(self, model, changes):
        """Updates a model.

        """
        check_resource_type(model, MODEL_PATH,
                            message="A model id is needed.")
        model_id = get_model_id(model)
        if model_id:
            body = json.dumps(changes)
            return self._update("%s%s" % (self.url, model_id), body)

    def delete_model(self, model):
        """Deletes a model.

        """
        check_resource_type(model, MODEL_PATH,
                            message="A model id is needed.")
        model_id = get_model_id(model)
        if model_id:
            return self._delete("%s%s" % (self.url, model_id))

    ##########################################################################
    #
    # Predictions
    # https://bigml.com/developers/predictions
    #
    ##########################################################################
    def create_prediction(self, model_or_ensemble, input_data=None,
                          by_name=True, args=None, wait_time=3, retries=10):
        """Creates a new prediction.

        """
        ensemble_id = None
        model_id = None

        resource_type = get_resource_type(model_or_ensemble)
        if resource_type == ENSEMBLE_PATH:
            ensemble_id = get_ensemble_id(model_or_ensemble)
            if ensemble_id is not None:
                if wait_time > 0:
                    count = 0
                    while (not self.ensemble_is_ready(ensemble_id) and
                           count < retries):
                        time.sleep(wait_time)
                        count += 1
                try:
                    ensemble = self.get_ensemble(ensemble_id)
                    model_id = ensemble['object']['models'][0]
                except (KeyError, IndexError), exc:
                    LOGGER.error("The ensemble has no valid model"
                                 " information: %s" % str(exc))
                    model_id = None
        elif resource_type == MODEL_PATH:
            model_id = get_model_id(model_or_ensemble)
        else:
            raise Exception("A model or ensemble id is needed to create a"
                            " prediction. %s found." % resource_type)

        if model_id is not None:
            if ensemble_id is None:
                if wait_time > 0:
                    count = 0
                    while (not self.model_is_ready(model_id) and
                           count < retries):
                        time.sleep(wait_time)
                        count += 1

            if input_data is None:
                input_data = {}
            elif by_name:
                fields = self.get_fields(model_id)
                inverted_fields = invert_dictionary(fields)
                wrong_keys = [key for key in input_data.keys() if not key
                              in inverted_fields]
                if wrong_keys:
                    LOGGER.info(("Some input fields are"
                                 " not used in the model: %s") %
                                ", ".join(wrong_keys))
                input_data = dict(
                    [[inverted_fields[key], value]
                     for key, value in input_data.items()
                     if key in inverted_fields])

            if args is None:
                args = {}
            args.update({
                "input_data": input_data})
            if ensemble_id is None:
                args.update({
                    "model": model_id})
            else:
                args.update({
                    "ensemble": ensemble_id})

            body = json.dumps(args)
            return self._create(self.prediction_url, body,
                                verify=VERIFY_PREDICTION_SERVER)

    def get_prediction(self, prediction):
        """Retrieves a prediction.

        """
        check_resource_type(prediction, PREDICTION_PATH,
                            message="A prediction id is needed.")
        prediction_id = get_prediction_id(prediction)
        if prediction_id:
            return self._get("%s%s" % (self.url, prediction_id))

    def list_predictions(self, query_string=''):
        """Lists all your predictions.

        """
        return self._list(self.prediction_url, query_string)

    def update_prediction(self, prediction, changes):
        """Updates a prediction.

        """
        check_resource_type(prediction, PREDICTION_PATH,
                            message="A prediction id is needed.")
        prediction_id = get_prediction_id(prediction)
        if prediction_id:
            body = json.dumps(changes)
            return self._update("%s%s" % (self.url, prediction_id), body)

    def delete_prediction(self, prediction):
        """Deletes a prediction.

        """
        check_resource_type(prediction, PREDICTION_PATH,
                            message="A prediction id is needed.")
        prediction_id = get_prediction_id(prediction)
        if prediction_id:
            return self._delete("%s%s" % (self.url, prediction_id))

    ##########################################################################
    #
    # Evaluations
    # https://bigml.com/developers/evaluations
    #
    ##########################################################################
    def create_evaluation(self, model_or_ensemble, dataset,
                          args=None, wait_time=3, retries=10):
        """Creates a new evaluation.

        """

        def args_update(check_resource_is_ready):
            """Updates args when the resource is ready

            """
            if resource_id:
                if wait_time > 0:
                    count = 0
                    while (not check_resource_is_ready(resource_id) and
                           count < retries):
                        time.sleep(wait_time)
                        count += 1
                args.update({
                    resource_type: resource_id,
                    "dataset": dataset_id})

        if args is None:
            args = {}
        resource_type = get_resource_type(dataset)
        if not DATASET_PATH == resource_type:
            raise Exception("A dataset id is needed as second argument"
                            " to create an evaluation. %s found." %
                            resource_type)
        dataset_id = get_dataset_id(dataset)
        if dataset_id:
            if wait_time > 0:
                count = 0
                while (not self.dataset_is_ready(dataset_id) and
                       count < retries):
                    time.sleep(wait_time)
                    count += 1

        resource_type = get_resource_type(model_or_ensemble)
        if resource_type == MODEL_PATH:
            resource_id = get_model_id(model_or_ensemble)
            args_update(self.model_is_ready)
        elif resource_type == ENSEMBLE_PATH:
            resource_id = get_ensemble_id(model_or_ensemble)
            args_update(self.ensemble_is_ready)
        else:
            raise Exception("A model or ensemble id is needed as first"
                            " argument to create an"
                            " evaluation. %s found." % resource_type)

        body = json.dumps(args)
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
    def create_ensemble(self, dataset, args=None, wait_time=3, retries=10):
        """Creates an ensemble.

        """
        check_resource_type(dataset, DATASET_PATH,
                            message="A dataset id is needed.")
        dataset_id = get_dataset_id(dataset)

        if dataset_id:
            if wait_time > 0:
                count = 0
                while (not self.dataset_is_ready(dataset_id) and
                       count < retries):
                    time.sleep(wait_time)
                    count += 1

            if args is None:
                args = {}
            args.update({
                "dataset": dataset_id})
            body = json.dumps(args)
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
