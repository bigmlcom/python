# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2017-2020 BigML
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

"""Base class for deepnets' REST calls

   https://bigml.com/api/deepnets

"""

try:
    import simplejson as json
except ImportError:
    import json


from bigml.resourcehandler import ResourceHandler
from bigml.resourcehandler import (check_resource_type, resource_is_ready,
                                   get_deepnet_id)
from bigml.constants import DEEPNET_PATH


class DeepnetHandler(ResourceHandler):
    """This class is used by the BigML class as
       a mixin that provides the REST calls models. It should not
       be instantiated independently.

    """
    def __init__(self):
        """Initializes the DeepnetHandler. This class is intended
           to be used as a mixin on ResourceHandler, that inherits its
           attributes and basic method from BigMLConnection, and must not be
           instantiated independently.

        """
        self.deepnet_url = self.url + DEEPNET_PATH

    def create_deepnet(self, datasets,
                       args=None, wait_time=3, retries=10):
        """Creates a deepnet from a `dataset`
           of a list o `datasets`.

        """
        create_args = self._set_create_from_datasets_args(
            datasets, args=args, wait_time=wait_time, retries=retries)

        body = json.dumps(create_args)
        return self._create(self.deepnet_url, body)

    def get_deepnet(self, deepnet, query_string='',
                    shared_username=None, shared_api_key=None):
        """Retrieves a deepnet.

           The model parameter should be a string containing the
           deepnet id or the dict returned by
           create_deepnet.
           As a deepnet is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, the function will
           return a dict that encloses the deepnet
           values and state info available at the time it is called.

           If this is a shared deepnet, the username and
           sharing api key must also be provided.
        """
        check_resource_type(deepnet, DEEPNET_PATH,
                            message="A deepnet id is needed.")
        deepnet_id = get_deepnet_id(deepnet)
        if deepnet_id:
            return self._get("%s%s" % (self.url, deepnet_id),
                             query_string=query_string,
                             shared_username=shared_username,
                             shared_api_key=shared_api_key)

    def deepnet_is_ready(self, deepnet, **kwargs):
        """Checks whether a deepnet's status is FINISHED.

        """
        check_resource_type(deepnet, DEEPNET_PATH,
                            message="A deepnet id is needed.")
        resource = self.get_deepnet(deepnet, **kwargs)
        return resource_is_ready(resource)

    def list_deepnets(self, query_string=''):
        """Lists all your deepnets.

        """
        return self._list(self.deepnet_url, query_string)

    def update_deepnet(self, deepnet, changes):
        """Updates a deepnet.

        """
        check_resource_type(deepnet, DEEPNET_PATH,
                            message="A deepnet id is needed.")
        deepnet_id = get_deepnet_id(deepnet)
        if deepnet_id:
            body = json.dumps(changes)
            return self._update(
                "%s%s" % (self.url, deepnet_id), body)

    def delete_deepnet(self, deepnet):
        """Deletes a deepnet.

        """
        check_resource_type(deepnet, DEEPNET_PATH,
                            message="A deepnet id is needed.")
        deepnet_id = get_deepnet_id(deepnet)
        if deepnet_id:
            return self._delete("%s%s" % (self.url, deepnet_id))
