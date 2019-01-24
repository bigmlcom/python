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

"""Base class for anomaly scores' REST calls

   https://bigml.com/api/anomalyscores

"""

try:
    import simplejson as json
except ImportError:
    import json


from bigml.resourcehandler import ResourceHandler
from bigml.resourcehandler import (check_resource_type, get_resource_type,
                                   check_resource,
                                   get_anomaly_score_id, get_anomaly_id)
from bigml.constants import (ANOMALY_SCORE_PATH, ANOMALY_PATH,
                             TINY_RESOURCE)


class AnomalyScoreHandler(ResourceHandler):
    """This class is used by the BigML class as
       a mixin that provides the REST calls models. It should not
       be instantiated independently.

    """
    def __init__(self):
        """Initializes the AnomalyScoreHandler. This class is intended to be
           used as a mixin on ResourceHandler, that inherits its
           attributes and basic method from BigMLConnection, and must not be
           instantiated independently.

        """
        self.anomaly_score_url = self.url + ANOMALY_SCORE_PATH

    def create_anomaly_score(self, anomaly, input_data=None,
                             args=None, wait_time=3, retries=10):
        """Creates a new anomaly score.

        """
        anomaly_id = None
        resource_type = get_resource_type(anomaly)
        if resource_type == ANOMALY_PATH:
            anomaly_id = get_anomaly_id(anomaly)
            check_resource(anomaly_id,
                           query_string=TINY_RESOURCE,
                           wait_time=wait_time, retries=retries,
                           raise_on_error=True, api=self)
        else:
            raise Exception("An anomaly detector id is needed to create an"
                            " anomaly score. %s found." % resource_type)

        if input_data is None:
            input_data = {}
        create_args = {}
        if args is not None:
            create_args.update(args)
        create_args.update({
            "input_data": input_data})
        create_args.update({
            "anomaly": anomaly_id})

        body = json.dumps(create_args)
        return self._create(self.anomaly_score_url, body,
                            verify=self.verify)

    def get_anomaly_score(self, anomaly_score, query_string=''):
        """Retrieves an anomaly score.

        """
        check_resource_type(anomaly_score, ANOMALY_SCORE_PATH,
                            message="An anomaly score id is needed.")
        anomaly_score_id = get_anomaly_score_id(anomaly_score)
        if anomaly_score_id:
            return self._get("%s%s" % (self.url, anomaly_score_id),
                             query_string=query_string)

    def list_anomaly_scores(self, query_string=''):
        """Lists all your anomaly_scores.

        """
        return self._list(self.anomaly_score_url, query_string)

    def update_anomaly_score(self, anomaly_score, changes):
        """Updates an anomaly_score.

        """
        check_resource_type(anomaly_score, ANOMALY_SCORE_PATH,
                            message="An anomaly_score id is needed.")
        anomaly_score_id = get_anomaly_score_id(anomaly_score)
        if anomaly_score_id:
            body = json.dumps(changes)
            return self._update("%s%s" % (self.url, anomaly_score_id), body)

    def delete_anomaly_score(self, anomaly_score):
        """Deletes an anomaly_score.

        """
        check_resource_type(anomaly_score, ANOMALY_SCORE_PATH,
                            message="An anomaly_score id is needed.")
        anomaly_score_id = get_anomaly_score_id(anomaly_score)
        if anomaly_score_id:
            return self._delete("%s%s" % (self.url, anomaly_score_id))
