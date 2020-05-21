# -*- coding: utf-8 -*-
#!/usr/bin/env python
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

"""Base class for whizzml script' REST calls

   https://bigml.com/api/scripts

"""

import os
import requests
import re
try:
    import simplejson as json
except ImportError:
    import json

from urlparse import urljoin

from bigml.resourcehandler import ResourceHandler
from bigml.resourcehandler import (check_resource_type,
                                   get_script_id, get_resource_type,
                                   check_resource)
from bigml.constants import SCRIPT_PATH, TINY_RESOURCE
from bigml.util import is_url
from bigml.bigmlconnection import HTTP_OK


def retrieve_script_args(gist_url):
    """Retrieves the information to create a script from a public
       gist url

    """

    response = requests.get(gist_url)
    response.encoding = "utf8"
    if response.status_code == HTTP_OK:
        pattern = r"\"[^\"]*?\/raw\/[^\"]*"
        urls = re.findall(pattern, response.text)
        script_args = {}

        for url in urls:
            url = urljoin(gist_url, url.replace("\"", ""))
            if url.endswith(".whizzml"):
                response = requests.get(url)
                if response.status_code == HTTP_OK:
                    script_args["source_code"] = response.text
            if url.endswith(".json"):
                response = requests.get(url, \
                    headers={"content-type": "application/json"})
                if response.status_code == HTTP_OK:
                    script_args["json"] = response.text
        return script_args
    else:
        raise ValueError("The url did not contain the expected structure.")


class ScriptHandler(ResourceHandler):
    """This class is used by the BigML class as
       a mixin that provides the whizzml script' REST calls. It should not
       be instantiated independently.

    """
    def __init__(self):
        """Initializes the ScriptHandler. This class is intended to be
           used as a mixin on ResourceHandler, that inherits its
           attributes and basic method from BigMLConnection, and must not be
           instantiated independently.

        """
        self.script_url = self.url + SCRIPT_PATH

    def create_script(self, source_code=None, args=None,
                      wait_time=3, retries=10):
        """Creates a whizzml script from its source code. The `source_code`
           parameter can be a:
            {script ID}: the ID for an existing whizzml script
            {path}: the path to a file containing the source code
            {string} : the string containing the source code for the script

        """
        create_args = {}
        if args is not None:
            create_args.update(args)

        if source_code is None:
            raise Exception('A valid code string'
                            ' or a script id must be provided.')
        resource_type = get_resource_type(source_code)
        if resource_type == SCRIPT_PATH:
            script_id = get_script_id(source_code)
            if script_id:
                check_resource(script_id,
                               query_string=TINY_RESOURCE,
                               wait_time=wait_time, retries=retries,
                               raise_on_error=True, api=self)
                create_args.update({
                    "origin": script_id})
        elif isinstance(source_code, basestring):
            if is_url(source_code):
                script_args = retrieve_script_args(source_code)
                source_code = script_args.get("source_code")
                create_args.update(json.loads(script_args.get("json")))
            else:
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
            raise Exception("A script id or a valid source code"
                            " is needed to create a"
                            " script. %s found." % resource_type)


        body = json.dumps(create_args)
        return self._create(self.script_url, body)

    def get_script(self, script, query_string=''):
        """Retrieves a script.

           The script parameter should be a string containing the
           script id or the dict returned by create_script.
           As script is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, the function will
           return a dict that encloses the script content and state info
           available at the time it is called.
        """
        check_resource_type(script, SCRIPT_PATH,
                            message="A script id is needed.")
        script_id = get_script_id(script)
        if script_id:
            return self._get("%s%s" % (self.url, script_id),
                             query_string=query_string)

    def list_scripts(self, query_string=''):
        """Lists all your scripts.

        """
        return self._list(self.script_url, query_string)

    def update_script(self, script, changes):
        """Updates a script.

        """
        check_resource_type(script, SCRIPT_PATH,
                            message="A script id is needed.")
        script_id = get_script_id(script)
        if script_id:
            body = json.dumps(changes)
            return self._update("%s%s" % (self.url, script_id), body)

    def delete_script(self, script):
        """Deletes a script.

        """
        check_resource_type(script, SCRIPT_PATH,
                            message="A script id is needed.")
        script_id = get_script_id(script)
        if script_id:
            return self._delete("%s%s" % (self.url, script_id))
