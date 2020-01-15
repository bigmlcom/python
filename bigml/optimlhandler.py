# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2018-2020 BigML
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

"""Base class for optiml's REST calls

   https://bigml.com/api/optimls

"""

try:
    import simplejson as json
except ImportError:
    import json


from bigml.resourcehandler import ResourceHandler
from bigml.resourcehandler import (check_resource_type, resource_is_ready,
                                   get_optiml_id)
from bigml.constants import OPTIML_PATH


class OptimlHandler(ResourceHandler):
    """This class is used by the BigML class as
       a mixin that provides the REST calls models. It should not
       be instantiated independently.

    """
    def __init__(self):
        """Initializes the OptimlHandler. This class is intended
           to be used as a mixin on ResourceHandler, that inherits its
           attributes and basic method from BigMLConnection, and must not be
           instantiated independently.

        """
        self.optiml_url = self.url + OPTIML_PATH

    def create_optiml(self, datasets,
                      args=None, wait_time=3, retries=10):
        """Creates an optiml from a `dataset`
           of a list o `datasets`.

        """
        create_args = self._set_create_from_datasets_args(
            datasets, args=args, wait_time=wait_time, retries=retries)

        body = json.dumps(create_args)
        return self._create(self.optiml_url, body)

    def get_optiml(self, optiml, query_string='',
                   shared_username=None, shared_api_key=None):
        """Retrieves an optiml.

           The model parameter should be a string containing the
           optiml id or the dict returned by
           create_optiml.
           As an optiml is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, the function will
           return a dict that encloses the optiml
           values and state info available at the time it is called.

           If this is a shared optiml, the username and
           sharing api key must also be provided.
        """
        check_resource_type(optiml, OPTIML_PATH,
                            message="An optiml id is needed.")
        optiml_id = get_optiml_id(optiml)
        if optiml_id:
            return self._get("%s%s" % (self.url, optiml_id),
                             query_string=query_string,
                             shared_username=shared_username,
                             shared_api_key=shared_api_key)

    def optiml_is_ready(self, optiml, **kwargs):
        """Checks whether an optiml's status is FINISHED.

        """
        check_resource_type(optiml, OPTIML_PATH,
                            message="An optiml id is needed.")
        resource = self.get_optiml(optiml, **kwargs)
        return resource_is_ready(resource)

    def list_optimls(self, query_string=''):
        """Lists all your optimls.

        """
        return self._list(self.optiml_url, query_string)

    def update_optiml(self, optiml, changes):
        """Updates an optiml.

        """
        check_resource_type(optiml, OPTIML_PATH,
                            message="An optiml id is needed.")
        optiml_id = get_optiml_id(optiml)
        if optiml_id:
            body = json.dumps(changes)
            return self._update(
                "%s%s" % (self.url, optiml_id), body)

    def delete_optiml(self, optiml):
        """Deletes an optiml.

        """
        check_resource_type(optiml, OPTIML_PATH,
                            message="An optiml id is needed.")
        optiml_id = get_optiml_id(optiml)
        if optiml_id:
            return self._delete("%s%s" % (self.url, optiml_id))
