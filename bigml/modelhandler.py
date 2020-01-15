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

"""Base class for models' REST calls

   https://bigml.com/api/models

"""

try:
    import simplejson as json
except ImportError:
    import json


from bigml.resourcehandler import ResourceHandler
from bigml.resourcehandler import (check_resource_type, resource_is_ready,
                                   get_resource_type, check_resource,
                                   get_model_id, get_cluster_id)
from bigml.constants import (MODEL_PATH, CLUSTER_PATH, DATASET_PATH,
                             TINY_RESOURCE)


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

    def create_model(self, origin_resource, args=None, wait_time=3, retries=10):
        """Creates a model from an origin_resource.

        Uses a remote resource to create a new model using the
        arguments in `args`.
        The allowed remote resources can be:
            - dataset
            - list of datasets
            - cluster
        In the case of using cluster id as origin_resource, a centroid must
        also be provided in the args argument. The first centroid is used
        otherwise.

        """

        create_args = {}
        if args is not None:
            create_args.update(args)
        if isinstance(origin_resource, list):
            # mutidatasets
            create_args = self._set_create_from_datasets_args(
                origin_resource, args=create_args, wait_time=wait_time,
                retries=retries)
        else:
            resource_type = get_resource_type(origin_resource)
            # model from cluster and centroid
            if resource_type == CLUSTER_PATH:
                cluster_id = get_cluster_id(origin_resource)
                cluster = check_resource(cluster_id,
                                         query_string=TINY_RESOURCE,
                                         wait_time=wait_time,
                                         retries=retries,
                                         raise_on_error=True, api=self)
                if 'centroid' not in create_args:
                    try:
                        centroid = cluster['object'][
                            'cluster_models'].keys()[0]
                        create_args.update({'centroid': centroid})
                    except KeyError:
                        raise KeyError("Failed to generate the model. A "
                                       "centroid id is needed in the args "
                                       "argument to generate a model from "
                                       "a cluster.")
                create_args.update({'cluster': cluster_id})
            elif resource_type == DATASET_PATH:
                create_args = self._set_create_from_datasets_args(
                    origin_resource, args=create_args, wait_time=wait_time,
                    retries=retries)
            else:
                raise Exception("A dataset, list of dataset ids"
                                " or cluster id plus centroid id are needed"
                                " to create a"
                                " dataset. %s found." % resource_type)

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
