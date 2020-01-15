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

"""Base class for fusion's REST calls

   https://bigml.com/api/fusions

"""

try:
    import simplejson as json
except ImportError:
    import json


from bigml.resourcehandler import ResourceHandler
from bigml.resourcehandler import (check_resource_type, resource_is_ready,
                                   get_fusion_id)
from bigml.constants import FUSION_PATH, SUPERVISED_PATHS


class FusionHandler(ResourceHandler):
    """This class is used by the BigML class as
       a mixin that provides the REST calls models. It should not
       be instantiated independently.

    """
    def __init__(self):
        """Initializes the FusionHandler. This class is intended
           to be used as a mixin on ResourceHandler, that inherits its
           attributes and basic method from BigMLConnection, and must not be
           instantiated independently.

        """
        self.fusion_url = self.url + FUSION_PATH

    def create_fusion(self, models,
                      args=None, wait_time=3, retries=10):
        """Creates a fusion from a list of supervised models

        """
        create_args = self._set_create_from_models_args(
            models, SUPERVISED_PATHS,
            args=args, wait_time=wait_time, retries=retries)

        body = json.dumps(create_args)
        return self._create(self.fusion_url, body)

    def get_fusion(self, fusion, query_string='',
                   shared_username=None, shared_api_key=None):
        """Retrieves a fusion.

           The model parameter should be a string containing the
           fusion id or the dict returned by
           create_fusion.
           As a fusion is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, the function will
           return a dict that encloses the fusion
           values and state info available at the time it is called.

           If this is a shared fusion, the username and
           sharing api key must also be provided.
        """
        check_resource_type(fusion, FUSION_PATH,
                            message="A fusion id is needed.")
        fusion_id = get_fusion_id(fusion)
        if fusion_id:
            return self._get("%s%s" % (self.url, fusion_id),
                             query_string=query_string,
                             shared_username=shared_username,
                             shared_api_key=shared_api_key)

    def fusion_is_ready(self, fusion, **kwargs):
        """Checks whether a fusion's status is FINISHED.

        """
        check_resource_type(fusion, FUSION_PATH,
                            message="A fusion id is needed.")
        resource = self.get_fusion(fusion, **kwargs)
        return resource_is_ready(resource)

    def list_fusions(self, query_string=''):
        """Lists all your fusions.

        """
        return self._list(self.fusion_url, query_string)

    def update_fusion(self, fusion, changes):
        """Updates a fusion.

        """
        check_resource_type(fusion, FUSION_PATH,
                            message="A fusion id is needed.")
        fusion_id = get_fusion_id(fusion)
        if fusion_id:
            body = json.dumps(changes)
            return self._update(
                "%s%s" % (self.url, fusion_id), body)

    def delete_fusion(self, fusion):
        """Deletes a fusion.

        """
        check_resource_type(fusion, FUSION_PATH,
                            message="A fusion id is needed.")
        fusion_id = get_fusion_id(fusion)
        if fusion_id:
            return self._delete("%s%s" % (self.url, fusion_id))
