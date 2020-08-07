# -*- coding: utf-8 -*-
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

"""Base class for projections' REST calls

   https://bigml.com/api/projections

"""

try:
    import simplejson as json
except ImportError:
    import json


from bigml.api_handlers.resourcehandler import ResourceHandler
from bigml.api_handlers.resourcehandler import check_resource_type, \
    get_projection_id, check_resource, get_resource_id, get_resource_type
from bigml.constants import TINY_RESOURCE, PROJECTION_PATH, PCA_PATH


class ProjectionHandler(ResourceHandler):
    """This class is used by the BigML class as
       a mixin that provides the REST calls models. It should not
       be instantiated independently.

    """
    def __init__(self):
        """Initializes the ProjectionHandler. This class is intended to be
           used as a mixin on ResourceHandler, that inherits its
           attributes and basic method from BigMLConnection, and must not be
           instantiated independently.

        """
        self.projection_url = self.prediction_base_url + PROJECTION_PATH

    def create_projection(self, pca, input_data=None,
                          args=None, wait_time=3, retries=10):
        """Creates a new projection.
           The pca parameter can be a pca resource or ID

        """
        pca_id = None

        resource_type = get_resource_type(pca)
        if resource_type != PCA_PATH:
            raise Exception("A PCA resource id is needed"
                            " to create a projection. %s found." %
                            resource_type)

        pca_id = get_resource_id(pca)
        if pca_id is not None:
            check_resource(pca_id,
                           query_string=TINY_RESOURCE,
                           wait_time=wait_time, retries=retries,
                           raise_on_error=True, api=self)

        if input_data is None:
            input_data = {}
        create_args = {}
        if args is not None:
            create_args.update(args)
        create_args.update({
            "input_data": input_data})
        if pca_id is not None:
            create_args.update({
                "pca": pca_id})

        body = json.dumps(create_args)
        return self._create(self.projection_url, body,
                            verify=self.verify)

    def get_projection(self, projection, query_string=''):
        """Retrieves a projection.

        """
        check_resource_type(projection, PROJECTION_PATH,
                            message="A projection id is needed.")
        projection_id = get_projection_id(projection)
        if projection_id:
            return self._get("%s%s" % (self.url, projection_id),
                             query_string=query_string)

    def list_projections(self, query_string=''):
        """Lists all your projections.

        """
        return self._list(self.projection_url, query_string)

    def update_projection(self, projection, changes):
        """Updates a projection.

        """
        check_resource_type(projection, PROJECTION_PATH,
                            message="A projection id is needed.")
        projection_id = get_projection_id(projection)
        if projection_id:
            body = json.dumps(changes)
            return self._update("%s%s" % (self.url, projection_id), body)

    def delete_projection(self, projection):
        """Deletes a projection.

        """
        check_resource_type(projection, PROJECTION_PATH,
                            message="A projection id is needed.")
        projection_id = get_projection_id(projection)
        if projection_id:
            return self._delete("%s%s" % (self.url, projection_id))
