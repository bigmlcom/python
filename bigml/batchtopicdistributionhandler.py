# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2016-2020 BigML
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

"""Base class for batch topic distributions' REST calls

   https://bigml.com/developers/batchtopicdistributions

"""

try:
    import simplejson as json
except ImportError:
    import json

from bigml.bigmlconnection import DOWNLOAD_DIR
from bigml.resourcehandler import ResourceHandler
from bigml.resourcehandler import (check_resource_type,
                                   get_batch_topic_distribution_id)
from bigml.constants import BATCH_TOPIC_DISTRIBUTION_PATH, TOPIC_MODEL_PATH


class BatchTopicDistributionHandler(ResourceHandler):
    """This class is used by the BigML class as
       a mixin that provides the REST calls models. It should not
       be instantiated independently.

    """
    def __init__(self):
        """Initializes the BatchTopidDistributionHandler. This class is
           intended to be used as a mixin on ResourceHandler, that inherits its
           attributes and basic method from BigMLConnection, and must not be
           instantiated independently.

        """
        self.batch_topic_distribution_url = self.prediction_base_url + \
            BATCH_TOPIC_DISTRIBUTION_PATH

    def create_batch_topic_distribution(self, topic_model, dataset,
                                        args=None, wait_time=3, retries=10):
        """Creates a new batch topic distribution.


        """
        create_args = {}
        if args is not None:
            create_args.update(args)

        origin_resources_checked = self.check_origins(
            dataset, topic_model, create_args, model_types=[TOPIC_MODEL_PATH],
            wait_time=wait_time, retries=retries)
        if origin_resources_checked:
            body = json.dumps(create_args)
            return self._create(self.batch_topic_distribution_url, body)

    def get_batch_topic_distribution(self, batch_topic_distribution,
                                     query_string=''):
        """Retrieves a batch topic distribution.

           The batch_topic_distribution parameter should be a string
           containing the batch_topic_distribution id or the dict
           returned by create_batch_topic_distribution.
           As batch_topic_distribution is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, the function will
           return a dict that encloses the batch_topic_distribution values
           and state info available at the time it is called.
        """
        check_resource_type(batch_topic_distribution,
                            BATCH_TOPIC_DISTRIBUTION_PATH,
                            message="A batch topic distribution id is needed.")
        batch_topic_distribution_id = get_batch_topic_distribution_id( \
            batch_topic_distribution)
        if batch_topic_distribution_id:
            return self._get("%s%s" % (self.url, batch_topic_distribution_id),
                             query_string=query_string)

    def download_batch_topic_distribution(self,
                                          batch_topic_distribution,
                                          filename=None):
        """Retrieves the batch topic distribution file.

           Downloads topic distributions, that are stored in a remote CSV file.
           If a path is given in filename, the contents of the file are
           downloaded and saved locally. A file-like object is returned
           otherwise.
        """
        check_resource_type(batch_topic_distribution,
                            BATCH_TOPIC_DISTRIBUTION_PATH,
                            message="A batch topic distribution id is needed.")
        batch_topic_distribution_id = get_batch_topic_distribution_id( \
            batch_topic_distribution)
        if batch_topic_distribution_id:
            return self._download("%s%s%s" % \
                (self.url, batch_topic_distribution_id, DOWNLOAD_DIR), \
                filename=filename)

    def list_batch_topic_distributions(self, query_string=''):
        """Lists all your batch topic distributions.

        """
        return self._list(self.batch_topic_distribution_url, query_string)

    def update_batch_topic_distribution(self, batch_topic_distribution,
                                        changes):
        """Updates a batch topic distributions.

        """
        check_resource_type(batch_topic_distribution,
                            BATCH_TOPIC_DISTRIBUTION_PATH,
                            message="A batch topic distribution id is needed.")
        batch_topic_distribution_id = get_batch_topic_distribution_id( \
            batch_topic_distribution)
        if batch_topic_distribution_id:
            body = json.dumps(changes)
            return self._update("%s%s" % (self.url,
                                          batch_topic_distribution_id), body)

    def delete_batch_topic_distribution(self, batch_topic_distribution):
        """Deletes a batch topic distribution.

        """
        check_resource_type(batch_topic_distribution,
                            BATCH_TOPIC_DISTRIBUTION_PATH,
                            message="A batch topic distribution id is needed.")
        batch_topic_distribution_id = get_batch_topic_distribution_id( \
            batch_topic_distribution)
        if batch_topic_distribution_id:
            return self._delete("%s%s" % (self.url,
                                          batch_topic_distribution_id))
