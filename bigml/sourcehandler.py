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

"""Base class for sources' REST calls

   https://bigml.com/api/sources

"""

import sys
import os
import urllib2
import numbers
try:
    #added to allow GAE to work
    from google.appengine.api import urlfetch
    GAE_ENABLED = True
except ImportError:
    GAE_ENABLED = False
    import ssl

try:
    import simplejson as json
except ImportError:
    import json


from threading import Thread


PYTHON_2_7_9 = len(urllib2.urlopen.__defaults__) > 2
PYTHON_2 = sys.version_info < (3, 0)

if PYTHON_2:
    from poster.encode import multipart_encode, MultipartParam
if PYTHON_2_7_9:
    from bigml.sslposter import StreamingHTTPSHandler, register_openers
elif PYTHON_2:
    from poster.streaminghttp import StreamingHTTPSHandler, register_openers
else:
    from requests_toolbelt import MultipartEncoder
    import mimetypes

from bigml.util import (localize, clear_console_line, reset_console_line,
                        console_log, is_url)
from bigml.bigmlconnection import (
    HTTP_CREATED, HTTP_ACCEPTED, HTTP_BAD_REQUEST,
    HTTP_UNAUTHORIZED, HTTP_PAYMENT_REQUIRED, HTTP_NOT_FOUND,
    HTTP_TOO_MANY_REQUESTS, HTTP_FORBIDDEN,
    HTTP_INTERNAL_SERVER_ERROR, GAE_ENABLED, SEND_JSON)
from bigml.bigmlconnection import json_load
from bigml.resourcehandler import (check_resource_type,
                                   resource_is_ready,
                                   get_source_id)
from bigml.constants import SOURCE_PATH, UPLOADING
from bigml.resourcehandler import ResourceHandler, LOGGER

if PYTHON_2:
    register_openers()
else:
    import requests
    from bigml.util import maybe_save

class SourceHandler(ResourceHandler):

    """This class is used by the BigML class as
       a mixin that provides the REST calls to sources. It should not
       be instantiated independently.

    """

    def __init__(self):
        """Initializes the SourceHandler. This class is intended to be
           used as a mixin on ResourceHandler, that inherits its
           attributes and basic method from BigMLConnection, and must not be
           instantiated independently.

        """
        self.source_url = self.url + SOURCE_PATH

    def _create_remote_source(self, url, args=None):
        """Creates a new source using a URL

        """
        create_args = {}
        if args is not None:
            create_args.update(args)
        create_args.update({"remote": url})
        create_args = self._add_project(create_args)
        body = json.dumps(create_args)
        return self._create(self.source_url, body)

    def _create_connector_source(self, connector, args=None):
        """Creates a new source using an external connector

        """
        create_args = {}
        if args is not None:
            create_args.update(args)
        create_args.update({"external_data": connector})
        create_args = self._add_project(create_args)
        body = json.dumps(create_args)
        return self._create(self.source_url, body)

    def _create_inline_source(self, src_obj, args=None):
        """Create source from inline data

           The src_obj data should be a list of rows stored as dict or
           list objects.
        """
        create_args = {}
        if args is not None:
            create_args.update(args)
        create_args = self._add_project(create_args)

        # some basic validation
        if (not isinstance(src_obj, list) or (
                not all([isinstance(row, dict) for row in src_obj]) and
                not all([isinstance(row, list) for row in src_obj]))):
            raise TypeError(
                'ERROR: inline source must be a list of dicts or a '
                'list of lists')

        create_args.update({"data": json.dumps(src_obj)})
        body = json.dumps(create_args)
        return self._create(self.source_url, body)

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

    def _stream_source(self, file_name, args=None, async_load=False,
                       progress_bar=False, out=sys.stdout):
        """Creates a new source.

        """

        def draw_progress_bar(param, current, total):
            """Draws a text based progress report.

            """
            pct = 100 - ((total - current) * 100) / (total)
            console_log("Uploaded %s out of %s bytes [%s%%]" % (
                localize(current), localize(total), pct), reset=True)
        create_args = {}
        if args is not None:
            create_args.update(args)
        if 'source_parser' in create_args:
            create_args['source_parser'] = json.dumps(
                create_args['source_parser'])

        resource_id = None
        location = None
        resource = None
        error = None

        try:
            if isinstance(file_name, basestring):
                create_args.update({os.path.basename(file_name):
                                    open(file_name, "rb")})
            else:
                create_args = create_args.items()
                name = 'Stdin input'
                create_args.append(MultipartParam(name, filename=name,
                                                  fileobj=file_name))
        except IOError, exception:
            raise IOError("Error: cannot read training set. %s" %
                          str(exception))

        if async_load:
            source = {
                'code': HTTP_ACCEPTED,
                'resource': resource_id,
                'location': location,
                'object': {'status': {'message': 'The upload is in progress',
                                      'code': UPLOADING,
                                      'progress': 0.0}},
                'error': error}
            upload_args = (create_args, source)
            thread = Thread(target=self._upload_source,
                            args=upload_args,
                            kwargs={'out': out})
            thread.start()
            return source
        return self._process_source(resource_id, location, resource,
                                    args=create_args,
                                    progress_bar=progress_bar,
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

        if args is None:
            args = {}
        args = self._add_project(args, True)

        if progress_bar and callback is not None:
            body, headers = multipart_encode(args, cb=callback)
        else:
            body, headers = multipart_encode(args)

        url = self._add_credentials(self.source_url)

        if GAE_ENABLED:
            try:
                response = urlfetch.fetch(url=url,
                                          payload="".join(body),
                                          method=urlfetch.POST,
                                          headers=headers)
                code = response.status_code
                content = response.content
                if code in [HTTP_CREATED]:
                    if 'location' in response.headers:
                        location = response.headers['location']
                    resource = json_load(response.content)
                    resource_id = resource['resource']
                    error = {}
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
            except urlfetch.Error, exception:
                LOGGER.error("Error establishing connection: %s",
                             str(exception))
        else:
            try:
                request = urllib2.Request(url,
                                          body, headers)
                # try using the new SSL checking in python 2.7.9
                try:
                    if not self.verify and PYTHON_2_7_9:
                        context = ssl.create_default_context(
                            ssl.Purpose.CLIENT_AUTH)
                        context.verify_mode = ssl.CERT_NONE
                        https_handler = StreamingHTTPSHandler(context=context)
                        opener = urllib2.build_opener(https_handler)
                        urllib2.install_opener(opener)
                        response = urllib2.urlopen(request)
                    else:
                        response = urllib2.urlopen(request)
                except AttributeError:
                    response = urllib2.urlopen(request)
                clear_console_line(out=out)
                reset_console_line(out=out)
                code = response.getcode()
                if code == HTTP_CREATED:
                    location = response.headers['location']
                    content = response.read()
                    resource = json_load(content)
                    resource_id = resource['resource']
                    error = {}
                    if self.debug:
                        LOGGER.debug("Data: %s", body)
                        LOGGER.debug("Response: %s", content)
            except ValueError:
                LOGGER.error("Malformed response.")
            except urllib2.HTTPError, exception:
                code = exception.code
                if code in [HTTP_BAD_REQUEST,
                            HTTP_UNAUTHORIZED,
                            HTTP_PAYMENT_REQUIRED,
                            HTTP_NOT_FOUND,
                            HTTP_TOO_MANY_REQUESTS]:
                    content = exception.read()
                    error = json_load(content)
                    if self.debug:
                        LOGGER.debug("Data: %s", body)
                        LOGGER.debug("Response: %s", content)
                    LOGGER.error(self.error_message(error, method='create'))
                else:
                    LOGGER.error("Unexpected error (%s)", code)
                    code = HTTP_INTERNAL_SERVER_ERROR

            except urllib2.URLError, exception:
                LOGGER.error("Error establishing connection: %s",
                             str(exception))
                error = exception.args
        return {
            'code': code,
            'resource': resource_id,
            'location': location,
            'object': resource,
            'error': error}

    def _create_local_source(self, file_name, args=None):
        """Creates a new source using a local file.

        This function is only used from Python 3. No async-prepared.

        """
        create_args = {}
        if args is not None:
            create_args.update(args)

        for key, value in create_args.items():
            if value is not None and (isinstance(value, list) or
                                      isinstance(value, dict)):
                create_args[key] = json.dumps(value)
            elif value is not None and isinstance(value, numbers.Number):
                # the multipart encoder only accepts strings and files
                create_args[key] = str(value)


        code = HTTP_INTERNAL_SERVER_ERROR
        resource_id = None
        location = None
        resource = None
        error = {
            "status": {
                "code": code,
                "message": "The resource couldn't be created"}}

        try:

            if isinstance(file_name, basestring):
                name = os.path.basename(file_name)
                file_handler = open(file_name, "rb")
            else:
                name = 'Stdin input'
                file_handler = file_name
        except IOError:
            sys.exit("ERROR: cannot read training set")

        url = self._add_credentials(self.source_url)
        create_args = self._add_project(create_args, True)
        if GAE_ENABLED:
            try:
                req_options = {
                    'url': url,
                    'method': urlfetch.POST,
                    'headers': SEND_JSON,
                    'data': create_args,
                    'files': {name: file_handler},
                    'validate_certificate': self.verify
                }
                response = urlfetch.fetch(**req_options)
            except urlfetch.Error, exception:
                LOGGER.error("HTTP request error: %s",
                             str(exception))
                return maybe_save(resource_id, self.storage, code,
                                  location, resource, error)
        else:
            try:
                files = {"file": (name,
                                  file_handler,
                                  mimetypes.guess_type(name)[0])}
                files.update(create_args)
                multipart = MultipartEncoder(fields=files)
                response = requests.post( \
                    url,
                    headers={'Content-Type': multipart.content_type},
                    data=multipart, verify=self.verify)
            except (requests.ConnectionError,
                    requests.Timeout,
                    requests.RequestException), exc:
                LOGGER.error("HTTP request error: %s", str(exc))
                code = HTTP_INTERNAL_SERVER_ERROR
                return maybe_save(resource_id, self.storage, code,
                                  location, resource, error)
        try:
            code = response.status_code
            if code == HTTP_CREATED:
                location = response.headers['location']
                resource = json_load(response.content)
                resource_id = resource['resource']
                error = None
            elif code in [HTTP_BAD_REQUEST,
                          HTTP_UNAUTHORIZED,
                          HTTP_PAYMENT_REQUIRED,
                          HTTP_NOT_FOUND,
                          HTTP_TOO_MANY_REQUESTS]:
                error = json_load(response.content)
            else:
                LOGGER.error("Unexpected error (%s)" % code)
                code = HTTP_INTERNAL_SERVER_ERROR

        except ValueError:
            LOGGER.error("Malformed response")

        return maybe_save(resource_id, self.storage, code,
                          location, resource, error)

    def create_source(self, path=None, args=None, async_load=False,
                      progress_bar=False, out=sys.stdout):
        """Creates a new source.

           The source can be a local file path or a URL.

        """

        if path is None:
            raise Exception('A local path or a valid URL must be provided.')

        if is_url(path):
            return self._create_remote_source(path, args=args)
        elif isinstance(path, list):
            return self._create_inline_source(path, args=args)
        elif isinstance(path, dict):
            return self._create_connector_source(path, args=args)
        elif PYTHON_2:
            return self._stream_source(file_name=path, args=args,
                                       async_load=async_load,
                                       progress_bar=progress_bar, out=out)
        else:
            return self._create_local_source(file_name=path, args=args)

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
