# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2014 BigML
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

"""

import sys
import os
import requests
import ssl

from threading import Thread

try:
    import simplejson as json
except ImportError:
    import json


import urllib2
from poster.encode import multipart_encode, MultipartParam

PYTHON_2_7_9 = len(urllib2.urlopen.__defaults__) > 2

if PYTHON_2_7_9:
    from bigml.sslposter import StreamingHTTPSHandler, register_openers
else:
    from poster.streaminghttp import StreamingHTTPSHandler, register_openers

from bigml.util import (localize, clear_console_line, reset_console_line,
                        console_log, is_url)
from bigml.bigmlconnection import BigMLConnection
from bigml.bigmlconnection import (
    HTTP_CREATED, HTTP_ACCEPTED, HTTP_BAD_REQUEST,
    HTTP_UNAUTHORIZED, HTTP_PAYMENT_REQUIRED, HTTP_NOT_FOUND,
    HTTP_TOO_MANY_REQUESTS,
    HTTP_INTERNAL_SERVER_ERROR)
from bigml.resourcehandler import (check_resource_type, get_resource,
                                   resource_is_ready, check_resource,
                                   get_source_id)
from bigml.resourcehandler import SOURCE_RE, SOURCE_PATH, UPLOADING, LOGGER
from bigml.resourcehandler import ResourceHandler


register_openers()


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

        # some basic validation
        if (not isinstance(src_obj, list) or
            (not all([isinstance(row, dict) for row in src_obj]) and
             not all([isinstance(row, list) for row in src_obj]))):
            raise TypeError(
                'ERROR: inline source must be a list of dicts or a '
                'list of lists')

        create_args.update({"data": json.dumps(src_obj)})
        body = json.dumps(create_args)
        return self._create(self.source_url, body)

    def _create_local_source(self, file_name, args=None):
        """Creates a new source using a local file.

        This function is now DEPRECATED as "requests" do not stream the file
        content and that limited the size of local files to a small number of
        GBs.

        """
        create_args = {}
        if args is not None:
            create_args.update(args)

        if 'source_parser' in create_args:
            create_args['source_parser'] = json.dumps(
                create_args['source_parser'])

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
            raise IOError("ERROR: cannot read training set")

        try:
            response = requests.post(self.source_url + self.auth,
                                     files=files,
                                     data=create_args, verify=self.verify)

            code = response.status_code
            if code == HTTP_CREATED:
                location = response.headers['location']
                resource = json.loads(response.content, 'utf-8')
                resource_id = resource['resource']
                error = None
            elif code in [HTTP_BAD_REQUEST,
                          HTTP_UNAUTHORIZED,
                          HTTP_PAYMENT_REQUIRED,
                          HTTP_NOT_FOUND,
                          HTTP_TOO_MANY_REQUESTS]:
                error = json.loads(response.content, 'utf-8')
            else:
                LOGGER.error("Unexpected error (%s)", code)
                code = HTTP_INTERNAL_SERVER_ERROR

        except ValueError:
            LOGGER.error("Malformed response")
        except requests.ConnectionError, exc:
            LOGGER.error("Connection error: %s", str(exc))
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
                name = '<none>'
                create_args.append(MultipartParam(name, filename=name,
                                                  fileobj=file_name))

        except IOError, exception:
            raise IOError("Error: cannot read training set. %s" %
                          str(exception))

        if async:
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

        if progress_bar and callback is not None:
            body, headers = multipart_encode(args, cb=callback)
        else:
            body, headers = multipart_encode(args)

        request = urllib2.Request(self.source_url + self.auth, body, headers)

        try:
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
                resource = json.loads(content, 'utf-8')
                resource_id = resource['resource']
                error = {}
        except ValueError:
            LOGGER.error("Malformed response")
        except urllib2.HTTPError, exception:
            code = exception.code
            if code in [HTTP_BAD_REQUEST,
                        HTTP_UNAUTHORIZED,
                        HTTP_PAYMENT_REQUIRED,
                        HTTP_NOT_FOUND,
                        HTTP_TOO_MANY_REQUESTS]:
                content = exception.read()
                error = json.loads(content, 'utf-8')
                LOGGER.error(self.error_message(error, method='create'))
            else:
                LOGGER.error("Unexpected error (%s)", code)
                code = HTTP_INTERNAL_SERVER_ERROR

        except urllib2.URLError, exception:
            LOGGER.error("Error establishing connection: %s", str(exception))
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
            return self._create_remote_source(path, args=args)
        elif isinstance(path, list):
            return self._create_inline_source(path, args=args)
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
