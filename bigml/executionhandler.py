# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015 BigML
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

"""Base class for whizzml script executions' REST calls

   https://bigml.com/developers/executions

"""

try:
    import simplejson as json
except ImportError:
    import json


from bigml.resourcehandler import ResourceHandler
from bigml.resourcehandler import (check_resource_type,
                                   get_execution_id, get_resource_type,
                                   get_script_id, check_resource)
from bigml.constants import (EXECUTION_PATH, SCRIPT_PATH,
                             TINY_RESOURCE)


class ExecutionHandler(ResourceHandler):
    """This class is used by the BigML class as
       a mixin that provides the executions' REST calls. It should not
       be instantiated independently.

    """
    def __init__(self):
        """Initializes the ExecutionHandler. This class is intended to be
           used as a mixin on ResourceHandler, that inherits its
           attributes and basic method from BigMLConnection, and must not be
           instantiated independently.

        """
        self.execution_url = self.url + EXECUTION_PATH

    def create_execution(self, origin_resource, args=None,
                         wait_time=3, retries=10):
        """Creates an execution from a `script` or a list of `scripts`.

        """

        create_args = {}
        if args is not None:
            create_args.update(args)

        if (isinstance(origin_resource, basestring) or
                isinstance(origin_resource, dict)):
            # single script
            scripts = [origin_resource]
        else:
            scripts = origin_resource
        try:
            script_ids = [get_script_id(script) for script in scripts]
        except TypeError:
            raise Exception("A script id or a list of them is needed to create"
                            " a script execution. %s found." %
                            get_resource_type(origin_resource))

        if all([get_resource_type(script_id) == SCRIPT_PATH for
               script_id in script_ids]):
            for script in scripts:
                check_resource(script,
                               query_string=TINY_RESOURCE,
                               wait_time=wait_time, retries=retries,
                               raise_on_error=True, api=self)
        else:
            raise Exception("A script id or a list of them is needed to create"
                            " a script execution. %s found." %
                            get_resource_type(origin_resource))

        if len(scripts) > 1:
            create_args.update({
                "scripts": script_ids})
        else:
            create_args.update({
                "script": script_ids[0]})

        body = json.dumps(create_args)
        return self._create(self.execution_url, body)

    def get_execution(self, execution, query_string=''):
        """Retrieves an execution.

           The execution parameter should be a string containing the
           execution id or the dict returned by create_execution.
           As execution is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, the function will
           return a dict that encloses the execution contents and state info
           available at the time it is called.
        """
        check_resource_type(execution, EXECUTION_PATH,
                            message="An execution id is needed.")
        execution_id = get_execution_id(execution)
        if execution_id:
            return self._get("%s%s" % (self.url, execution_id),
                             query_string=query_string)

    def list_executions(self, query_string=''):
        """Lists all your executions.

        """
        return self._list(self.execution_url, query_string)

    def update_execution(self, execution, changes):
        """Updates an execution.

        """
        check_resource_type(execution, EXECUTION_PATH,
                            message="An execution id is needed.")
        execution_id = get_execution_id(execution)
        if execution_id:
            body = json.dumps(changes)
            return self._update("%s%s" % (self.url, execution_id), body)

    def delete_execution(self, execution):
        """Deletes an execution.

        """
        check_resource_type(execution, EXECUTION_PATH,
                            message="An execution id is needed.")
        execution_id = get_execution_id(execution)
        if execution_id:
            return self._delete("%s%s" % (self.url, execution_id))
