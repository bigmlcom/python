# -*- coding: utf-8 -*-
#pylint: disable=abstract-method
#
# Copyright 2014-2023 BigML
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

"""Base class for centroids' REST calls

   https://bigml.com/api/centroids

"""

try:
    import simplejson as json
except ImportError:
    import json


from bigml.api_handlers.resourcehandler import ResourceHandlerMixin
from bigml.api_handlers.resourcehandler import check_resource_type, \
    get_resource_type, check_resource, get_cluster_id
from bigml.constants import CENTROID_PATH, CLUSTER_PATH, SPECIFIC_EXCLUDES, \
    IMAGE_FIELDS_FILTER


class CentroidHandlerMixin(ResourceHandlerMixin):
    """This class is used by the BigML class as
       a mixin that provides the REST calls models. It should not
       be instantiated independently.

    """
    def __init__(self):
        """Initializes the CentroidHandler. This class is intended to be
           used as a mixin on ResourceHandler, that inherits its
           attributes and basic method from BigMLConnection, and must not be
           instantiated independently.

        """
        self.centroid_url = self.prediction_base_url + CENTROID_PATH

    def create_centroid(self, cluster, input_data=None,
                        args=None, wait_time=3, retries=10):
        """Creates a new centroid.

        """
        cluster_id = None
        resource_type = get_resource_type(cluster)
        if resource_type != CLUSTER_PATH:
            raise Exception("A cluster id is needed to create a"
                            " centroid. %s found." % resource_type)

        cluster_id = get_cluster_id(cluster)
        if cluster_id is None:
            raise Exception("Failed to detect a correct cluster "
                "structure in %s." % cluster)

        if isinstance(cluster, dict) and cluster.get("resource") is not None:
            # retrieving fields info from model structure
            model_info = cluster
        else:
            image_fields_filter = IMAGE_FIELDS_FILTER + "," + \
                ",".join(SPECIFIC_EXCLUDES[resource_type])
            model_info = check_resource(cluster_id,
                                        query_string=image_fields_filter,
                                        wait_time=wait_time,
                                        retries=retries,
                                        raise_on_error=True,
                                        api=self)

        if input_data is None:
            input_data = {}
        create_args = {}
        if args is not None:
            create_args.update(args)
        create_args.update({
            "input_data": self.prepare_image_fields(model_info, input_data)})
        create_args.update({
            "cluster": cluster_id})

        body = json.dumps(create_args)
        return self._create(self.centroid_url, body,
                            verify=self.domain.verify_prediction)

    def get_centroid(self, centroid, query_string=''):
        """Retrieves a centroid.

        """
        check_resource_type(centroid, CENTROID_PATH,
                            message="A centroid id is needed.")
        return self.get_resource(centroid, query_string=query_string)

    def list_centroids(self, query_string=''):
        """Lists all your centroids.

        """
        return self._list(self.centroid_url, query_string)

    def update_centroid(self, centroid, changes):
        """Updates a centroid.

        """
        check_resource_type(centroid, CENTROID_PATH,
                            message="A centroid id is needed.")
        return self.update_resource(centroid, changes)

    def delete_centroid(self, centroid):
        """Deletes a centroid.

        """
        check_resource_type(centroid, CENTROID_PATH,
                            message="A centroid id is needed.")
        return self.delete_resource(centroid)
