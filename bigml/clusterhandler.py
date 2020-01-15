# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2014-2020 BigML
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

"""Base class for clusters' REST calls

   https://bigml.com/api/clusters

"""

try:
    import simplejson as json
except ImportError:
    import json


from bigml.resourcehandler import ResourceHandler
from bigml.resourcehandler import (check_resource_type, resource_is_ready,
                                   get_cluster_id)
from bigml.constants import CLUSTER_PATH


class ClusterHandler(ResourceHandler):
    """This class is used by the BigML class as
       a mixin that provides the REST calls models. It should not
       be instantiated independently.

    """
    def __init__(self):
        """Initializes the ClusterHandler. This class is intended to be
           used as a mixin on ResourceHandler, that inherits its
           attributes and basic method from BigMLConnection, and must not be
           instantiated independently.

        """
        self.cluster_url = self.url + CLUSTER_PATH

    def create_cluster(self, datasets, args=None, wait_time=3, retries=10):
        """Creates a cluster from a `dataset` or a list o `datasets`.

        """
        create_args = self._set_create_from_datasets_args(
            datasets, args=args, wait_time=wait_time, retries=retries)

        body = json.dumps(create_args)
        return self._create(self.cluster_url, body)

    def get_cluster(self, cluster, query_string='',
                    shared_username=None, shared_api_key=None):
        """Retrieves a cluster.

           The model parameter should be a string containing the
           cluster id or the dict returned by create_cluster.
           As cluster is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, the function will
           return a dict that encloses the cluster values and state info
           available at the time it is called.

           If this is a shared cluster, the username and sharing api key must
           also be provided.
        """
        check_resource_type(cluster, CLUSTER_PATH,
                            message="A cluster id is needed.")
        cluster_id = get_cluster_id(cluster)
        if cluster_id:
            return self._get("%s%s" % (self.url, cluster_id),
                             query_string=query_string,
                             shared_username=shared_username,
                             shared_api_key=shared_api_key)

    def cluster_is_ready(self, cluster, **kwargs):
        """Checks whether a cluster's status is FINISHED.

        """
        check_resource_type(cluster, CLUSTER_PATH,
                            message="A cluster id is needed.")
        resource = self.get_cluster(cluster, **kwargs)
        return resource_is_ready(resource)

    def list_clusters(self, query_string=''):
        """Lists all your clusters.

        """
        return self._list(self.cluster_url, query_string)

    def update_cluster(self, cluster, changes):
        """Updates a cluster.

        """
        check_resource_type(cluster, CLUSTER_PATH,
                            message="A cluster id is needed.")
        cluster_id = get_cluster_id(cluster)
        if cluster_id:
            body = json.dumps(changes)
            return self._update("%s%s" % (self.url, cluster_id), body)

    def delete_cluster(self, cluster):
        """Deletes a cluster.

        """
        check_resource_type(cluster, CLUSTER_PATH,
                            message="A cluster id is needed.")
        cluster_id = get_cluster_id(cluster)
        if cluster_id:
            return self._delete("%s%s" % (self.url, cluster_id))
