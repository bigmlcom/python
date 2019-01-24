# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2016-2019 BigML
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

"""Base class for topicdistributions' REST calls

   https://bigml.com/api/topic_distributions

"""

try:
    import simplejson as json
except ImportError:
    import json


from bigml.resourcehandler import ResourceHandler
from bigml.resourcehandler import (check_resource_type,
                                   get_resource_type,
                                   get_topic_distribution_id,
                                   check_resource, get_topic_model_id)
from bigml.constants import (TOPIC_DISTRIBUTION_PATH, TINY_RESOURCE)


class TopicDistributionHandler(ResourceHandler):
    """This class is used by the BigML class as
       a mixin that provides the REST calls models. It should not
       be instantiated independently.

    """
    def __init__(self):
        """Initializes the TopicDistributionHandler. This class is intended to
           be used as a mixin on ResourceHandler, that inherits its
           attributes and basic method from BigMLConnection, and must not be
           instantiated independently.

        """
        self.topic_distribution_url = self.url + TOPIC_DISTRIBUTION_PATH

    def create_topic_distribution(self, topic_model, input_data=None,
                                  args=None, wait_time=3, retries=10):
        """Creates a new topic distribution.

        """
        topic_model_id = get_topic_model_id(topic_model)
        if topic_model_id is not None:
            check_resource(topic_model_id,
                           query_string=TINY_RESOURCE,
                           wait_time=wait_time, retries=retries,
                           raise_on_error=True, api=self)
        else:
            resource_type = get_resource_type(topic_model)
            raise Exception("A topic model id is needed to create a"
                            " topic distribution. %s found." % resource_type)

        if input_data is None:
            input_data = {}
        create_args = {}
        if args is not None:
            create_args.update(args)
        create_args.update({
            "input_data": input_data,
            "topicmodel": topic_model_id})

        body = json.dumps(create_args)
        return self._create(self.topic_distribution_url, body,
                            verify=self.verify_prediction)

    def get_topic_distribution(self, topic_distribution, query_string=''):
        """Retrieves a topic distribution.

        """
        check_resource_type(topic_distribution, TOPIC_DISTRIBUTION_PATH,
                            message="A topic distribution id is needed.")
        topic_distribution_id = get_topic_distribution_id(topic_distribution)
        if topic_distribution_id:
            return self._get("%s%s" % (self.url, topic_distribution_id),
                             query_string=query_string)

    def list_topic_distributions(self, query_string=''):
        """Lists all your topic distributions.

        """
        return self._list(self.topic_distribution_url, query_string)

    def update_topic_distribution(self, topic_distribution, changes):
        """Updates a topic distribution.

        """
        check_resource_type(topic_distribution, TOPIC_DISTRIBUTION_PATH,
                            message="A topic distribution id is needed.")
        topic_distribution_id = get_topic_distribution_id(topic_distribution)
        if topic_distribution_id:
            body = json.dumps(changes)
            return self._update("%s%s" % \
                (self.url, topic_distribution_id), body)

    def delete_topic_distribution(self, topic_distribution):
        """Deletes a topic distribution.

        """
        check_resource_type(topic_distribution, TOPIC_DISTRIBUTION_PATH,
                            message="A topic distribution id is needed.")
        topic_distribution_id = get_topic_distribution_id(topic_distribution)
        if topic_distribution_id:
            return self._delete("%s%s" % (self.url, topic_distribution_id))
