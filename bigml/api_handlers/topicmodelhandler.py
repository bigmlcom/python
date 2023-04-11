# -*- coding: utf-8 -*-
#pylint: disable=abstract-method
#
# Copyright 2016-2023 BigML
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

"""Base class for TopicModel's REST calls

   https://bigml.com/api/topicmodels

"""

try:
    import simplejson as json
except ImportError:
    import json


from bigml.api_handlers.resourcehandler import ResourceHandlerMixin
from bigml.api_handlers.resourcehandler import check_resource_type, \
    resource_is_ready
from bigml.constants import TOPIC_MODEL_PATH


class TopicModelHandlerMixin(ResourceHandlerMixin):
    """This class is used by the BigML class as
       a mixin that provides the REST calls models. It should not
       be instantiated independently.

    """
    def __init__(self):
        """Initializes the TopicModelHandler. This class is intended to be
           used as a mixin on ResourceHandler, that inherits its
           attributes and basic method from BigMLConnection, and must not be
           instantiated independently.

        """
        self.topic_model_url = self.url + TOPIC_MODEL_PATH

    def create_topic_model(self, datasets, args=None, wait_time=3, retries=10):
        """Creates a Topic Model from a `dataset` or a list o `datasets`.

        """
        create_args = self._set_create_from_datasets_args(
            datasets, args=args, wait_time=wait_time, retries=retries)

        body = json.dumps(create_args)
        return self._create(self.topic_model_url, body)

    def get_topic_model(self, topic_model, query_string='',
                        shared_username=None, shared_api_key=None):
        """Retrieves a Topic Model.

           The topic_model parameter should be a string containing the
           topic model ID or the dict returned by create_topic_model.
           As the topic model is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, the function will
           return a dict that encloses the topic model values and state info
           available at the time it is called.

           If this is a shared topic model, the username and sharing api key
           must also be provided.
        """
        check_resource_type(topic_model, TOPIC_MODEL_PATH,
                            message="A Topic Model id is needed.")
        return self.get_resource(topic_model,
                                 query_string=query_string,
                                 shared_username=shared_username,
                                 shared_api_key=shared_api_key)


    def topic_model_is_ready(self, topic_model, **kwargs):
        """Checks whether a topic model's status is FINISHED.

        """
        check_resource_type(topic_model, TOPIC_MODEL_PATH,
                            message="A topic model id is needed.")
        resource = self.get_topic_model(topic_model, **kwargs)
        return resource_is_ready(resource)

    def list_topic_models(self, query_string=''):
        """Lists all your Topic Models.

        """
        return self._list(self.topic_model_url, query_string)

    def update_topic_model(self, topic_model, changes):
        """Updates a Topic Model.

        """
        check_resource_type(topic_model, TOPIC_MODEL_PATH,
                            message="A topic model id is needed.")
        return self.update_resource(topic_model, changes)

    def delete_topic_model(self, topic_model, query_string=''):
        """Deletes a Topic Model.

        """
        check_resource_type(topic_model, TOPIC_MODEL_PATH,
                            message="A topic model id is needed.")
        return self.delete_resource(topic_model, query_string=query_string)

    def clone_topic_model(self, topic_model,
                          args=None, wait_time=3, retries=10):
        """Creates a cloned topic model from an existing `topic model`

        """
        create_args = self._set_clone_from_args(
            topic_model, "topicmodel", args=args, wait_time=wait_time,
            retries=retries)

        body = json.dumps(create_args)
        return self._create(self.topic_model_url, body)
