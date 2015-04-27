# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2014-2015 BigML
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

"""Base class for models' REST calls

   https://bigml.com/developers/models

"""

try:
    import simplejson as json
except ImportError:
    import json


from bigml.resourcehandler import ResourceHandler
from bigml.resourcehandler import (check_resource_type, resource_is_ready,
                                   get_model_id)
from bigml.resourcehandler import MODEL_PATH


class ModelHandler(ResourceHandler):
    """This class is used by the BigML class as
       a mixin that provides the REST calls models. It should not
       be instantiated independently.

    """
    def __init__(self):
        """Initializes the ModelHandler. This class is intended to be
           used as a mixin on ResourceHandler, that inherits its
           attributes and basic method from BigMLConnection, and must not be
           instantiated independently.

        """
        self.model_url = self.url + MODEL_PATH

    def create_model(self, datasets, args=None, wait_time=3, retries=10):
        """Creates a model from a `dataset` or a list of `datasets`.

        """
        create_args = self._set_create_from_datasets_args(
            datasets, args=args, wait_time=wait_time, retries=retries)

        body = json.dumps(create_args)
        return self._create(self.model_url, body)

    def get_model(self, model, query_string='',
                  shared_username=None, shared_api_key=None):
        """Retrieves a model.

           The model parameter should be a string containing the
           model id or the dict returned by create_model.
           As model is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, the function will
           return a dict that encloses the model values and state info
           available at the time it is called.

           If this is a shared model, the username and sharing api key must
           also be provided.
        """
        check_resource_type(model, MODEL_PATH,
                            message="A model id is needed.")
        model_id = get_model_id(model)
        if model_id:
            return self._get("%s%s" % (self.url, model_id),
                             query_string=query_string,
                             shared_username=shared_username,
                             shared_api_key=shared_api_key)

    def model_is_ready(self, model, **kwargs):
        """Checks whether a model's status is FINISHED.

        """
        check_resource_type(model, MODEL_PATH,
                            message="A model id is needed.")
        resource = self.get_model(model, **kwargs)
        return resource_is_ready(resource)

    def list_models(self, query_string=''):
        """Lists all your models.

        """
        return self._list(self.model_url, query_string)

    def update_model(self, model, changes):
        """Updates a model.

        """
        check_resource_type(model, MODEL_PATH,
                            message="A model id is needed.")
        model_id = get_model_id(model)
        if model_id:
            body = json.dumps(changes)
            return self._update("%s%s" % (self.url, model_id), body)

    def delete_model(self, model):
        """Deletes a model.

        """
        check_resource_type(model, MODEL_PATH,
                            message="A model id is needed.")
        model_id = get_model_id(model)
        if model_id:
            return self._delete("%s%s" % (self.url, model_id))
