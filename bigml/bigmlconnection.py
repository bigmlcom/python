# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2014-2020 BigML
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

"""Class for the BigML connection

"""
import sys
import os
import time
import locale
import StringIO
import logging

try:
    import simplejson as json
except ImportError:
    import json

try:
    #added to allow GAE to work
    from google.appengine.api import urlfetch
    GAE_ENABLED = True
except ImportError:
    GAE_ENABLED = False
    import requests


import bigml.constants as c

from bigml.util import (check_dir,
                        maybe_save, get_exponential_wait)
from bigml.util import DEFAULT_LOCALE, PY3
from bigml.domain import Domain
from bigml.domain import DEFAULT_DOMAIN, BIGML_PROTOCOL


LOG_FORMAT = '%(asctime)-15s: %(message)s'
LOGGER = logging.getLogger('BigML')
CONSOLE = logging.StreamHandler()
CONSOLE.setLevel(logging.WARNING)
LOGGER.addHandler(CONSOLE)


# Base URL
BIGML_URL = '%s://%s/andromeda/'

DOWNLOAD_DIR = '/download'


# Headers
JSON_TYPE = 'application/json'
SEND_JSON = {'Content-Type': '%s;charset=utf-8' % JSON_TYPE}
ACCEPT_JSON = {'Accept': '%s;charset=utf-8' % JSON_TYPE}

# HTTP Status Codes from https://bigml.com/api/status_codes
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


def json_load(content):
    """Loads the bytes or string contents in the correct encoding to
       create the JSON corresponding object.

    """
    args = [content.decode('utf-8')]
    if not PY3:
        args.append('utf-8')
    return json.loads(*args)


##############################################################################
#
# Patch for requests
#
##############################################################################
def patch_requests(short_debug):
    """ Monkey patches requests to get debug output.

    """
    def debug_request(method, url, **kwargs):
        """Logs the request and response content for api's remote requests

        """
        response = original_request(method, url, **kwargs)
        logging.debug("Data: %s", response.request.body)
        response_content = "Download status is %s" % response.status_code \
            if "download" in url else \
            response.content
        response_content = response_content[0:256] if short_debug else \
        response_content
        logging.debug("Response: %s\n", response_content)
        return response
    original_request = requests.api.request
    requests.api.request = debug_request


class BigMLConnection(object):
    """Low level point to create, retrieve, list, update, and delete
    sources, datasets, models and predictions.


    Resources are wrapped in a dictionary that includes:
        code: HTTP status code
        resource: The resource/id
        location: Remote location of the resource
        object: The resource itself
        error: An error code and message

    """
    def __init__(self, username=None, api_key=None,
                 debug=False, set_locale=False, storage=None, domain=None,
                 project=None, organization=None, short_debug=False):
        """Initializes the BigML API.

        If left unspecified, `username` and `api_key` will default to the
        values of the `BIGML_USERNAME` and `BIGML_API_KEY` environment
        variables respectively.

        `dev_mode` has been deprecated. Now all resources coexist in the
        same production environment. Existing resources generated in
        development mode have been archived under a special project and
        are now accessible in production mode.

        If storage is set to a directory name, the resources obtained in
        CRU operations will be stored in the given directory.

        If domain is set, the api will point to the specified domain. Default
        will be the one in the environment variable `BIGML_DOMAIN` or
        `bigml.io` if missing. The expected domain argument is a string or a
        Domain object. See Domain class for details.

        When project is set to a project ID,
        the user is considered to be working in an
        organization project. The scope of the API requests will be limited
        to this project and permissions should be previously given by the
        organization administrator.

        When organization is set to an organization ID,
        the user is considered to be working for an
        organization. The scope of the API requests will be limited to the
        projects of the organization and permissions need to be previously
        given by the organization administrator.

        """


        logging_level = logging.ERROR
        if debug or short_debug:
            try:
                logging_level = logging.DEBUG
                patch_requests(short_debug)
            except Exception:
                # when using GAE will fail
                pass

        logging.basicConfig(format=LOG_FORMAT,
                            level=logging_level,
                            stream=sys.stdout)

        if username is None:
            try:
                username = os.environ['BIGML_USERNAME']
            except KeyError:
                raise AttributeError("Cannot find BIGML_USERNAME in"
                                     " your environment")

        if api_key is None:
            try:
                api_key = os.environ['BIGML_API_KEY']
            except KeyError:
                raise AttributeError("Cannot find BIGML_API_KEY in"
                                     " your environment")

        self.auth = "?username=%s;api_key=%s;" % (username, api_key)
        self.project = None
        self.organization = None
        if project is not None:
            self.project = project
        if organization is not None:
            self.organization = organization
        self.debug = debug
        self.short_debug = short_debug
        self.general_domain = None
        self.general_protocol = None
        self.prediction_domain = None
        self.prediction_protocol = None
        self.verify = None
        self.verify_prediction = None
        self.url = None
        self.prediction_base_url = None

        self._set_api_urls(domain=domain)

        # if verify is not set, we capture warnings to avoid `requests` library
        # warnings: InsecurePlatformWarning
        logging.captureWarnings(not self.verify)
        if set_locale:
            locale.setlocale(locale.LC_ALL, DEFAULT_LOCALE)
        self.storage = assign_dir(storage)

    def _set_api_urls(self, dev_mode=False, domain=None):
        """Sets the urls that point to the REST api methods for each resource

        dev_mode` has been deprecated. Now all resources coexist in the
        same production environment. Existing resources generated in
        development mode have been archived under a special project and
        are now accessible in production mode.

        """
        if dev_mode:
            LOGGER.warning("Development mode is deprecated and the dev_mode"
                           " flag will be removed soon.")
        if domain is None:
            domain = Domain()
        elif isinstance(domain, basestring):
            domain = Domain(domain=domain)
        elif not isinstance(domain, Domain):
            raise ValueError("The domain must be set using a Domain object.")
        # Setting the general and prediction domain options
        self.general_domain = domain.general_domain
        self.general_protocol = domain.general_protocol
        self.prediction_domain = domain.prediction_domain
        self.prediction_protocol = domain.prediction_protocol
        self.verify = domain.verify
        self.verify_prediction = domain.verify_prediction
        self.url = BIGML_URL % (BIGML_PROTOCOL, self.general_domain)
        self.prediction_base_url = BIGML_URL % (
            self.prediction_protocol, self.prediction_domain)


    def _add_credentials(self, url, organization=False, shared_auth=None):
        """Adding the credentials and project or organization information
        for authentication

        The organization argument is a boolean that controls authentication
        profiles in organizations. When set to true,
        the organization ID is used to access the projects and tasks in an
        organization. If false, a particular project ID must be used.

        The shared_auth string provides the alternative credentials for
        shared resources.

        """
        auth = self.auth if shared_auth is None else shared_auth
        auth = auth if "?" not in url else ";%s" % auth[1:]
        return "%s%s%s" % (url, auth,
                           "organization=%s;" % self.organization if
                           organization and self.organization
                           else "project=%s;" % self.project if self.project
                           else "")

    def _add_project(self, payload, include=True):
        """Adding project id as attribute when it has been set in the
        connection arguments.

        """
        to_string = False
        if self.project and include:
            # Adding project ID to args if it's not set
            if isinstance(payload, basestring):
                payload = json.loads(payload)
                to_string = True
            if payload.get("project") is None:
                payload["project"] = self.project
            if to_string:
                return json.dumps(payload)
        return payload

    def _create(self, url, body, verify=None, organization=None):
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
        if verify is None:
            verify = self.verify

        url = self._add_credentials(url, organization=organization)
        body = self._add_project(body, not organization)
        while code == HTTP_ACCEPTED:
            if GAE_ENABLED:
                try:
                    req_options = {
                        'url': url,
                        'method': urlfetch.POST,
                        'headers': SEND_JSON,
                        'payload': body,
                        'validate_certificate': verify
                    }
                    response = urlfetch.fetch(**req_options)
                except urlfetch.Error, exception:
                    LOGGER.error("HTTP request error: %s",
                                 str(exception))
                    error["status"]["type"] = c.TRANSIENT
                    return maybe_save(resource_id, self.storage, code,
                                      location, resource, error)
            else:
                try:
                    response = requests.post(url,
                                             headers=SEND_JSON,
                                             data=body, verify=verify)
                except (requests.ConnectionError,
                        requests.Timeout,
                        requests.RequestException), exc:
                    LOGGER.error("HTTP request error: %s", str(exc))
                    code = HTTP_INTERNAL_SERVER_ERROR
                    error["status"]["type"] = c.TRANSIENT
                    return maybe_save(resource_id, self.storage, code,
                                      location, resource, error)
            try:
                code = response.status_code
                if code in [HTTP_CREATED, HTTP_OK]:
                    if 'location' in response.headers:
                        location = response.headers['location']
                    resource = json_load(response.content)
                    resource_id = resource.get('resource')
                    error = None
                elif code in [HTTP_BAD_REQUEST,
                              HTTP_UNAUTHORIZED,
                              HTTP_PAYMENT_REQUIRED,
                              HTTP_FORBIDDEN,
                              HTTP_NOT_FOUND,
                              HTTP_TOO_MANY_REQUESTS]:
                    error = json_load(response.content)
                    LOGGER.error(self.error_message(error, method='create'))
                elif code != HTTP_ACCEPTED:
                    LOGGER.error("Unexpected error (%s)", code)
                    code = HTTP_INTERNAL_SERVER_ERROR
            except ValueError, exc:
                LOGGER.error("Malformed response: %s", str(exc))
                code = HTTP_INTERNAL_SERVER_ERROR

        return maybe_save(resource_id, self.storage, code,
                          location, resource, error)

    def _get(self, url, query_string='',
             shared_username=None, shared_api_key=None, organization=None):
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

        kwargs = {"organization": organization}
        if shared_username is not None and shared_api_key is not None:
            kwargs.update({"shared_auth": auth})

        url = self._add_credentials(url, **kwargs) + query_string
        if GAE_ENABLED:
            try:
                req_options = {
                    'url': url,
                    'method': urlfetch.GET,
                    'headers': ACCEPT_JSON,
                    'validate_certificate': self.verify
                }
                response = urlfetch.fetch(**req_options)
            except urlfetch.Error, exception:
                LOGGER.error("HTTP request error: %s",
                             str(exception))
                error["status"]["type"] = c.TRANSIENT
                return maybe_save(resource_id, self.storage, code,
                                  location, resource, error)
        else:
            try:
                response = requests.get(url, headers=ACCEPT_JSON,
                                        verify=self.verify)
            except (requests.ConnectionError,
                    requests.Timeout,
                    requests.RequestException), exc:
                LOGGER.error("HTTP request error: %s", str(exc))
                error["status"]["type"] = c.TRANSIENT
                return maybe_save(resource_id, self.storage, code,
                                  location, resource, error)
        try:
            code = response.status_code
            if code == HTTP_OK:
                resource = json_load(response.content)
                resource_id = resource['resource']
                error = None
            elif code in [HTTP_BAD_REQUEST,
                          HTTP_UNAUTHORIZED,
                          HTTP_NOT_FOUND,
                          HTTP_TOO_MANY_REQUESTS]:
                error = json_load(response.content)
                LOGGER.error(self.error_message(error, method='get'))
            else:
                LOGGER.error("Unexpected error (%s)", code)
                code = HTTP_INTERNAL_SERVER_ERROR

        except ValueError, exc:
            if "output_format" in query_string:
                # output can be an xml file that is returned without storing
                return response.content
            else:
                LOGGER.error("Malformed response: %s" % str(exc))

        return maybe_save(resource_id, self.storage, code,
                          location, resource, error)

    def _list(self, url, query_string='', organization=None):
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

        url = self._add_credentials(url, organization=organization) + \
            query_string
        if GAE_ENABLED:
            try:
                req_options = {
                    'url': url,
                    'method': urlfetch.GET,
                    'headers': ACCEPT_JSON,
                    'validate_certificate': self.verify
                }
                response = urlfetch.fetch(**req_options)
            except urlfetch.Error, exception:
                LOGGER.error("HTTP request error: %s",
                             str(exception))
                error["status"]["type"] = c.TRANSIENT
                return {
                    'code': code,
                    'meta': meta,
                    'objects': resources,
                    'error': error}
        else:
            try:
                response = requests.get(url, headers=ACCEPT_JSON,
                                        verify=self.verify)
            except (requests.ConnectionError,
                    requests.Timeout,
                    requests.RequestException), exc:
                LOGGER.error("HTTP request error: %s", str(exc))
                error["status"]["type"] = c.TRANSIENT
                return {
                    'code': code,
                    'meta': meta,
                    'objects': resources,
                    'error': error}
        try:
            code = response.status_code

            if code == HTTP_OK:
                resource = json_load(response.content)
                meta = resource['meta']
                resources = resource['objects']
                error = None
            elif code in [HTTP_BAD_REQUEST,
                          HTTP_UNAUTHORIZED,
                          HTTP_NOT_FOUND,
                          HTTP_TOO_MANY_REQUESTS]:
                error = json_load(response.content)
            else:
                LOGGER.error("Unexpected error (%s)", code)
                code = HTTP_INTERNAL_SERVER_ERROR
        except ValueError, exc:
            LOGGER.error("Malformed response: %s", str(exc))

        return {
            'code': code,
            'meta': meta,
            'objects': resources,
            'error': error}

    def _update(self, url, body, organization=None):
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

        url = self._add_credentials(url, organization=organization)
        body = self._add_project(body, not organization)
        if GAE_ENABLED:
            try:
                req_options = {
                    'url': url,
                    'method': urlfetch.PUT,
                    'headers': SEND_JSON,
                    'payload': body,
                    'validate_certificate': self.verify
                }
                response = urlfetch.fetch(**req_options)
            except urlfetch.Error, exception:
                LOGGER.error("HTTP request error: %s",
                             str(exception))
                error["status"]["type"] = c.TRANSIENT
                return maybe_save(resource_id, self.storage, code,
                                  location, resource, error)
        else:
            try:
                response = requests.put(url,
                                        headers=SEND_JSON,
                                        data=body, verify=self.verify)
            except (requests.ConnectionError,
                    requests.Timeout,
                    requests.RequestException), exc:
                LOGGER.error("HTTP request error: %s", str(exc))
                error["status"]["type"] = c.TRANSIENT
                return maybe_save(resource_id, self.storage, code,
                                  location, resource, error)
        try:
            code = response.status_code

            if code == HTTP_ACCEPTED:
                resource = json_load(response.content)
                resource_id = resource['resource']
                error = None
            elif code in [HTTP_UNAUTHORIZED,
                          HTTP_PAYMENT_REQUIRED,
                          HTTP_METHOD_NOT_ALLOWED,
                          HTTP_TOO_MANY_REQUESTS]:
                error = json_load(response.content)
                LOGGER.error(self.error_message(error, method='update'))
            else:
                LOGGER.error("Unexpected error (%s)", code)
                code = HTTP_INTERNAL_SERVER_ERROR
        except ValueError:
            LOGGER.error("Malformed response")

        return maybe_save(resource_id, self.storage, code,
                          location, resource, error)

    def _delete(self, url, query_string='', organization=None):
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

        url = self._add_credentials(url, organization=organization) + \
            query_string
        if GAE_ENABLED:
            try:
                req_options = {
                    'url': url,
                    'method': urlfetch.DELETE,
                    'validate_certificate': self.verify
                }
                response = urlfetch.fetch(**req_options)
            except urlfetch.Error, exception:
                LOGGER.error("HTTP request error: %s",
                             str(exception))
                error["status"]["type"] = c.TRANSIENT
                return {
                    'code': code,
                    'error': error}
        else:
            try:
                response = requests.delete(url, verify=self.verify)
            except (requests.ConnectionError,
                    requests.Timeout,
                    requests.RequestException), exc:
                LOGGER.error("HTTP request error: %s", str(exc))
                error["status"]["type"] = c.TRANSIENT
                return {
                    'code': code,
                    'error': error}
        try:
            code = response.status_code

            if code == HTTP_NO_CONTENT:
                error = None
            elif code in [HTTP_BAD_REQUEST,
                          HTTP_UNAUTHORIZED,
                          HTTP_NOT_FOUND,
                          HTTP_TOO_MANY_REQUESTS]:
                error = json_load(response.content)
                LOGGER.error(self.error_message(error, method='delete'))
            else:
                LOGGER.error("Unexpected error (%s)", code)
                code = HTTP_INTERNAL_SERVER_ERROR

        except ValueError:
            LOGGER.error("Malformed response")

        return {
            'code': code,
            'error': error}

    def _download(self, url, filename=None, wait_time=10, retries=10,
                  counter=0):
        """Retrieves a remote file.

        Uses HTTP GET to download a file object with a BigML `url`.
        """
        code = HTTP_INTERNAL_SERVER_ERROR
        file_object = None

        # if retries for the creation and download have been exhausted,
        # return None
        if counter > 2 * retries:
            LOGGER.error("Retries exhausted trying to download the file.")
            return file_object

        if GAE_ENABLED:
            try:
                req_options = {
                    'url': self._add_credentials(url),
                    'method': urlfetch.GET,
                    'validate_certificate': self.verify
                }
                response = urlfetch.fetch(**req_options)
            except urlfetch.Error, exception:
                LOGGER.error("HTTP request error: %s",
                             str(exception))
                return file_object
        else:
            try:
                response = requests.get(self._add_credentials(url),
                                        verify=self.verify, stream=True)
            except (requests.ConnectionError,
                    requests.Timeout,
                    requests.RequestException), exc:
                LOGGER.error("HTTP request error: %s", str(exc))
                return file_object
        try:
            code = response.status_code
            if code == HTTP_OK:
                # starting the dataset export procedure
                if response.headers.get("content-type") == JSON_TYPE:
                    try:
                        if counter < retries:
                            download_status = json_load(response.content)
                            if download_status and isinstance(download_status,
                                                              dict):
                                if download_status['status']['code'] != 5:
                                    time.sleep(get_exponential_wait(wait_time,
                                                                    counter))
                                    counter += 1
                                    return self._download(url,
                                                          filename=filename,
                                                          wait_time=wait_time,
                                                          retries=retries,
                                                          counter=counter)
                                else:
                                    return self._download(url,
                                                          filename=filename,
                                                          wait_time=wait_time,
                                                          retries=retries,
                                                          counter=retries + 1)
                        elif counter == retries:
                            LOGGER.error("The maximum number of retries "
                                         " for the download has been "
                                         " exceeded. You can retry your "
                                         " command again in"
                                         " a while.")
                            return None
                    except ValueError:
                        LOGGER.error("Failed getting a valid JSON structure.")
                else:
                    # When download starts, content-type is no longer a
                    # JSON object.
                    if filename is not None and GAE_ENABLED:
                        LOGGER.error("No support for downloading"
                                     " to local files in Google App Engine.")
                        filename = None
                    if filename is None:
                        if GAE_ENABLED:
                            file_object = StringIO.StringIO(response.content)
                        else:
                            file_object = response.raw
                    else:
                        try:
                            total_size = int(
                                response.headers.get("content-length"))
                        except ValueError:
                            total_size = None
                        file_size = stream_copy(response, filename)
                        if file_size == 0:
                            LOGGER.error("Error copying file to %s", filename)
                        else:
                            file_object = filename
                        # if transient connection errors prevent the download,
                        # retry
                        if total_size is None or file_size < total_size:
                            LOGGER.error("Error downloading: "
                                         "total size=%s, %s downloaded",
                                         total_size, file_size)
                            time.sleep(get_exponential_wait(wait_time,
                                                            counter))
                            return self._download(url, filename=filename,
                                                  wait_time=wait_time,
                                                  retries=retries,
                                                  counter=counter + 1)
            elif code in [HTTP_BAD_REQUEST,
                          HTTP_UNAUTHORIZED,
                          HTTP_NOT_FOUND,
                          HTTP_TOO_MANY_REQUESTS]:
                error = response.content
                LOGGER.error("Error downloading: %s", error)
            else:
                LOGGER.error("Unexpected error (%s)", code)
                code = HTTP_INTERNAL_SERVER_ERROR
        except ValueError:
            LOGGER.error("Malformed response")

        return file_object

    def _status(self, url, query_string='', organization=None):
        """Returns the status of the account.


        """
        code = HTTP_INTERNAL_SERVER_ERROR
        meta = None
        resources = None
        error = {
            "status": {
                "code": code,
                "message": "Failed to obtain the account status info"}}

        url = self._add_credentials(url, organization=organization) \
            + query_string
        if GAE_ENABLED:
            try:
                req_options = {
                    'url': url,
                    'method': urlfetch.GET,
                    'headers': ACCEPT_JSON,
                    'validate_certificate': self.verify
                }
                response = urlfetch.fetch(**req_options)
            except urlfetch.Error, exception:
                LOGGER.error("HTTP request error: %s",
                             str(exception))
                return {
                    'code': code,
                    'object': resources,
                    'error': error}
        else:
            try:
                response = requests.get(url, headers=ACCEPT_JSON,
                                        verify=self.verify)
            except (requests.ConnectionError,
                    requests.Timeout,
                    requests.RequestException), exc:
                LOGGER.error("HTTP request error: %s", str(exc))
                return {
                    'code': code,
                    'object': resources,
                    'error': error}
        try:
            code = response.status_code

            if code == HTTP_OK:
                resource = json_load(response.content)
                resources = resource
                error = None
            elif code in [HTTP_BAD_REQUEST,
                          HTTP_UNAUTHORIZED,
                          HTTP_NOT_FOUND,
                          HTTP_TOO_MANY_REQUESTS]:
                error = json_load(response.content)
            else:
                LOGGER.error("Unexpected error (%s)", code)
                code = HTTP_INTERNAL_SERVER_ERROR
        except ValueError, exc:
            LOGGER.error("Malformed response: %s", str(exc))

        return {
            'code': code,
            'object': resources,
            'error': error}

    def error_message(self, resource, resource_type='resource', method=None):
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
                extra = error_info['status'].get('extra', None)
                if extra is not None:
                    error += ": %s" % extra
            if code == HTTP_NOT_FOUND and method == 'get':
                alternate_message = ''
                if self.general_domain != DEFAULT_DOMAIN:
                    alternate_message = (
                        u'- The %s was not created in %s.\n' % (
                            resource_type, self.general_domain))
                error += (
                    u'\nCouldn\'t find a %s matching the given'
                    u' id in %s. The most probable causes are:\n\n%s'
                    u'- A typo in the %s\'s id.\n'
                    u'- The %s id cannot be accessed with your credentials'
                    u' or was not created in %s.\n'
                    u'\nDouble-check your %s and'
                    u' credentials info and retry.' % (
                        resource_type, self.general_domain,
                        alternate_message, resource_type,
                        resource_type, self.general_domain, resource_type))
                return error
            if code == HTTP_UNAUTHORIZED:
                error += (u'\nDouble-check your credentials and the general'
                          u' domain your account is registered with (currently'
                          u' using %s), please.' % self.general_domain)
                return error
            if code == HTTP_BAD_REQUEST:
                error += u'\nDouble-check the arguments for the call, please.'
                return error
            if code == HTTP_TOO_MANY_REQUESTS:
                error += (u'\nToo many requests. Please stop '
                          u' requests for a while before resuming.')
                return error
            elif code == HTTP_PAYMENT_REQUIRED:
                error += (u'\nYou\'ll need to buy some more credits to perform'
                          u' the chosen action')
                return error

        return "Invalid %s structure:\n\n%s" % (resource_type, resource)
