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

"""Base class for whizzml libraries' REST calls

   https://bigml.com/api/libraries

"""

try:
    import simplejson as json
except ImportError:
    import json
import os

from bigml.api_handlers.resourcehandler import ResourceHandler
from bigml.api_handlers.resourcehandler import check_resource_type, \
    get_library_id, get_resource_type, check_resource
from bigml.constants import LIBRARY_PATH, TINY_RESOURCE


class LibraryHandler(ResourceHandler):
    """This class is used by the BigML class as
       a mixin that provides the whizzml libraries' REST calls. It should not
       be instantiated independently.

    """
    def __init__(self):
        """Initializes the LibraryHandler. This class is intended to be
           used as a mixin on ResourceHandler, that inherits its
           attributes and basic method from BigMLConnection, and must not be
           instantiated independently.

        """
        self.library_url = self.url + LIBRARY_PATH

    def create_library(self, source_code=None, args=None,
                       wait_time=3, retries=10):
        """Creates a whizzml library from its source code. The `source_code`
           parameter can be a:
            {library ID}: the ID for an existing whizzml library
            {path}: the path to a file containing the source code
            {string} : the string containing the source code for the library

        """
        create_args = {}
        if args is not None:
            create_args.update(args)

        if source_code is None:
            raise Exception('A valid code string'
                            ' or a library id must be provided.')
        resource_type = get_resource_type(source_code)
        if resource_type == LIBRARY_PATH:
            library_id = get_library_id(source_code)
            if library_id:
                check_resource(library_id,
                               query_string=TINY_RESOURCE,
                               wait_time=wait_time, retries=retries,
                               raise_on_error=True, api=self)
                create_args.update({
                    "origin": library_id})
        elif isinstance(source_code, str):
            try:
                if os.path.exists(source_code):
                    with open(source_code) as code_file:
                        source_code = code_file.read()
            except IOError:
                raise IOError("Could not open the source code file %s." %
                              source_code)
            create_args.update({
                "source_code": source_code})
        else:
            raise Exception("A library id or a valid source code"
                            " is needed to create a"
                            " library. %s found." % resource_type)


        body = json.dumps(create_args)
        return self._create(self.library_url, body)

    def get_library(self, library, query_string=''):
        """Retrieves a library.

           The library parameter should be a string containing the
           library id or the dict returned by create_script.
           As library is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, the function will
           return a dict that encloses the library content and state info
           available at the time it is called.
        """
        check_resource_type(library, LIBRARY_PATH,
                            message="A library id is needed.")
        library_id = get_library_id(library)
        if library_id:
            return self._get("%s%s" % (self.url, library_id),
                             query_string=query_string)

    def list_libraries(self, query_string=''):
        """Lists all your libraries.

        """
        return self._list(self.library_url, query_string)

    def update_library(self, library, changes):
        """Updates a library.

        """
        check_resource_type(library, LIBRARY_PATH,
                            message="A library id is needed.")
        library_id = get_library_id(library)
        if library_id:
            body = json.dumps(changes)
            return self._update("%s%s" % (self.url, library_id), body)

    def delete_library(self, library):
        """Deletes a library.

        """
        check_resource_type(library, LIBRARY_PATH,
                            message="A library id is needed.")
        library_id = get_library_id(library)
        if library_id:
            return self._delete("%s%s" % (self.url, library_id))
