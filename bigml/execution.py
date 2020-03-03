# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2019-2020 BigML
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

"""An local Execution object.

This module defines a local class to handle the results of an execution

"""
import json

from bigml.api import FINISHED, FAULTY
from bigml.api import get_status, BigML, get_api_connection, ID_GETTERS
from bigml.basemodel import retrieve_resource



def get_resource_dict(resource, resource_type, api=None):
    """Extracting the resource JSON info as a dict from the first argument of
       the local object constructors, that can be:

        - the path to a file that contains the JSON
        - the ID of the resource
        - the resource dict itself

    """

    get_id = ID_GETTERS[resource_type]
    resource_id = None
    # the string can be a path to a JSON file
    if isinstance(resource, basestring):
        try:
            with open(resource) as resource_file:
                resource = json.load(resource_file)
                resource_id = get_id(resource)
                if resource_id is None:
                    raise ValueError("The JSON file does not seem"
                                     " to contain a valid BigML %s"
                                     " representation." % resource_type)
        except IOError:
            # if it is not a path, it can be a model id
            resource_id = get_id(resource)
            if resource_id is None:
                if resource.find("%s/" % resource_type) > -1:
                    raise Exception(
                        api.error_message(resource,
                                          resource_type=resource_type,
                                          method="get"))
                else:
                    raise IOError("Failed to open the expected JSON file"
                                  " at %s." % resource)
        except ValueError:
            raise ValueError("Failed to interpret %s."
                             " JSON file expected." % resource)

    if not (isinstance(resource, dict) and 'resource' in resource and
            resource['resource'] is not None):
        resource = retrieve_resource(api, resource_id, retries=0)
    else:
        resource_id = get_id(resource)

    return resource_id, resource


class Execution(object):
    """A class to deal with the information in an execution result

    """
    def __init__(self, execution, api=None):

        self.resource_id = None
        self.outputs = None
        self.output_types = None
        self.output_resources = None
        self.result = None
        self.status = None
        self.source_location = None
        self.error = None
        self.error_message = None
        self.error_location = None
        self.call_stack = None
        self.api = get_api_connection(api)

        try:
            self.resource_id, execution = get_resource_dict( \
                execution, "execution", self.api)
        except ValueError, resource:
            try:
                execution = json.loads(str(resource))
            except ValueError:
                raise ValueError("The execution resource was faulty: \n%s" % \
                    resource)
                pass
            self.resource_id = execution["resource"]
        if 'object' in execution and isinstance(execution['object'], dict):
            execution = execution['object']
            self.status = execution["status"]
            self.error = self.status.get("error")
            if self.error is not None:
                self.error_message = self.status.get("message")
                self.error_location = self.status.get("source_location")
                self.call_stack = self.status.get("call_stack")
            else:
                self.source_location = self.status.get("source_location")
                if 'execution' in execution and \
                        isinstance(execution['execution'], dict):
                    execution = execution.get('execution')
                    self.result = execution.get("result")
                    self.outputs = dict((output[0], output[1]) \
                        for output in execution.get("outputs"))
                    self.output_types = dict((output[0], output[2]) \
                        for output in execution.get("outputs"))
                    self.output_resources = dict((res["variable"], res["id"]) \
                        for res in execution.get("output_resources"))
                    self.execution = execution
