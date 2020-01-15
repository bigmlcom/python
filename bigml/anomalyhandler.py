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

"""Base class for anomaly detectors' REST calls

   https://bigml.com/api/anomalies

"""

try:
    import simplejson as json
except ImportError:
    import json


from bigml.resourcehandler import ResourceHandler
from bigml.resourcehandler import (check_resource_type, resource_is_ready,
                                   get_anomaly_id)
from bigml.constants import ANOMALY_PATH


class AnomalyHandler(ResourceHandler):
    """This class is used by the BigML class as
       a mixin that provides the REST calls models. It should not
       be instantiated independently.

    """
    def __init__(self):
        """Initializes the AnomalyHandler. This class is intended to be
           used as a mixin on ResourceHandler, that inherits its
           attributes and basic method from BigMLConnection, and must not be
           instantiated independently.

        """
        self.anomaly_url = self.url + ANOMALY_PATH

    def create_anomaly(self, datasets, args=None, wait_time=3, retries=10):
        """Creates an anomaly detector from a `dataset` or a list o `datasets`.

        """
        create_args = self._set_create_from_datasets_args(
            datasets, args=args, wait_time=wait_time, retries=retries)

        body = json.dumps(create_args)
        return self._create(self.anomaly_url, body)

    def get_anomaly(self, anomaly, query_string='',
                    shared_username=None, shared_api_key=None):
        """Retrieves an anomaly detector.

           The anomaly parameter should be a string containing the
           anomaly id or the dict returned by create_anomaly.
           As the anomaly detector is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, the function will
           return a dict that encloses the model values and state info
           available at the time it is called.

           If this is a shared anomaly detector, the username and sharing api
           key must also be provided.
        """
        check_resource_type(anomaly, ANOMALY_PATH,
                            message="A anomaly id is needed.")
        anomaly_id = get_anomaly_id(anomaly)
        if anomaly_id:
            return self._get("%s%s" % (self.url, anomaly_id),
                             query_string=query_string,
                             shared_username=shared_username,
                             shared_api_key=shared_api_key)

    def anomaly_is_ready(self, anomaly, **kwargs):
        """Checks whether an anomaly detector's status is FINISHED.

        """
        check_resource_type(anomaly, ANOMALY_PATH,
                            message="An anomaly id is needed.")
        resource = self.get_anomaly(anomaly, **kwargs)
        return resource_is_ready(resource)

    def list_anomalies(self, query_string=''):
        """Lists all your anomaly detectors.

        """
        return self._list(self.anomaly_url, query_string)

    def update_anomaly(self, anomaly, changes):
        """Updates an anomaly detector.

        """
        check_resource_type(anomaly, ANOMALY_PATH,
                            message="An anomaly detector id is needed.")
        anomaly_id = get_anomaly_id(anomaly)
        if anomaly_id:
            body = json.dumps(changes)
            return self._update("%s%s" % (self.url, anomaly_id), body)

    def delete_anomaly(self, anomaly):
        """Deletes an anomaly detector.

        """
        check_resource_type(anomaly, ANOMALY_PATH,
                            message="An anomaly detector id is needed.")
        anomaly_id = get_anomaly_id(anomaly)
        if anomaly_id:
            return self._delete("%s%s" % (self.url, anomaly_id))
