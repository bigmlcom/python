# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2014-2019 BigML
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


from bigml.resourcehandler import ResourceHandler
from bigml.resourcehandler import (check_resource_type, get_resource_type,
                                   check_resource,
                                   get_centroid_id, get_cluster_id)
from bigml.constants import CENTROID_PATH, CLUSTER_PATH, TINY_RESOURCE


class CentroidHandler(ResourceHandler):
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
        self.centroid_url = self.url + CENTROID_PATH

    def create_centroid(self, cluster, input_data=None,
                        args=None, wait_time=3, retries=10):
        """Creates a new centroid.

        """
        cluster_id = None
        resource_type = get_resource_type(cluster)
        if resource_type == CLUSTER_PATH:
            cluster_id = get_cluster_id(cluster)
            check_resource(cluster_id,
                           query_string=TINY_RESOURCE,
                           wait_time=wait_time, retries=retries,
                           raise_on_error=True, api=self)
        else:
            raise Exception("A cluster id is needed to create a"
                            " centroid. %s found." % resource_type)

        if input_data is None:
            input_data = {}
        create_args = {}
        if args is not None:
            create_args.update(args)
        create_args.update({
            "input_data": input_data})
        create_args.update({
            "cluster": cluster_id})

        body = json.dumps(create_args)
        return self._create(self.centroid_url, body,
                            verify=self.verify)

    def get_centroid(self, centroid, query_string=''):
        """Retrieves a centroid.

        """
        check_resource_type(centroid, CENTROID_PATH,
                            message="A centroid id is needed.")
        centroid_id = get_centroid_id(centroid)
        if centroid_id:
            return self._get("%s%s" % (self.url, centroid_id),
                             query_string=query_string)

    def list_centroids(self, query_string=''):
        """Lists all your centroids.

        """
        return self._list(self.centroid_url, query_string)

    def update_centroid(self, centroid, changes):
        """Updates a centroid.

        """
        check_resource_type(centroid, CENTROID_PATH,
                            message="A centroid id is needed.")
        centroid_id = get_centroid_id(centroid)
        if centroid_id:
            body = json.dumps(changes)
            return self._update("%s%s" % (self.url, centroid_id), body)

    def delete_centroid(self, centroid):
        """Deletes a centroid.

        """
        check_resource_type(centroid, CENTROID_PATH,
                            message="A centroid id is needed.")
        centroid_id = get_centroid_id(centroid)
        if centroid_id:
            return self._delete("%s%s" % (self.url, centroid_id))
