# -*- coding: utf-8 -*-
#
# Copyright 2014-2022 BigML
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

"""Base class for ensembles' REST calls

   https://bigml.com/api/ensembles

"""

try:
    import simplejson as json
except ImportError:
    import json


from bigml.api_handlers.resourcehandler import ResourceHandlerMixin
from bigml.api_handlers.resourcehandler import check_resource_type, \
    resource_is_ready
from bigml.constants import ENSEMBLE_PATH


class EnsembleHandlerMixin(ResourceHandlerMixin):
    """This class is used by the BigML class as
       a mixin that provides the REST calls models. It should not
       be instantiated independently.

    """
    def __init__(self):
        """Initializes the EnsembleHandler. This class is intended to be
           used as a mixin on ResourceHandler, that inherits its
           attributes and basic method from BigMLConnection, and must not be
           instantiated independently.

        """
        self.ensemble_url = self.url + ENSEMBLE_PATH

    def create_ensemble(self, datasets, args=None, wait_time=3, retries=10):
        """Creates an ensemble from a dataset or a list of datasets.

        """

        create_args = self._set_create_from_datasets_args(
            datasets, args=args, wait_time=wait_time, retries=retries)

        body = json.dumps(create_args)
        return self._create(self.ensemble_url, body)

    def get_ensemble(self, ensemble, query_string='',
                     shared_username=None, shared_api_key=None):
        """Retrieves an ensemble.

           The ensemble parameter should be a string containing the
           ensemble id or the dict returned by create_ensemble.
           As an ensemble is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, the function will
           return a dict that encloses the ensemble values and state info
           available at the time it is called.
        """
        check_resource_type(ensemble, ENSEMBLE_PATH,
                            message="An ensemble id is needed.")
        return self.get_resource(ensemble, query_string=query_string,
                                 shared_username=shared_username,
                                 shared_api_key=shared_api_key)

    def ensemble_is_ready(self, ensemble):
        """Checks whether a ensemble's status is FINISHED.

        """
        check_resource_type(ensemble, ENSEMBLE_PATH,
                            message="An ensemble id is needed.")
        resource = self.get_ensemble(ensemble)
        return resource_is_ready(resource)

    def list_ensembles(self, query_string=''):
        """Lists all your ensembles.

        """
        return self._list(self.ensemble_url, query_string)

    def update_ensemble(self, ensemble, changes):
        """Updates a ensemble.

        """
        check_resource_type(ensemble, ENSEMBLE_PATH,
                            message="An ensemble id is needed.")
        return self.update_resource(ensemble, changes)

    def delete_ensemble(self, ensemble):
        """Deletes a ensemble.

        """
        check_resource_type(ensemble, ENSEMBLE_PATH,
                            message="An ensemble id is needed.")
        return self.delete_resource(ensemble)

    def clone_ensemble(self, ensemble,
                       args=None, wait_time=3, retries=10):
        """Creates a cloned ensemble from an existing `ensemble`

        """
        create_args = self._set_clone_from_args(
            ensemble, "ensemble", args=args, wait_time=wait_time,
            retries=retries)

        body = json.dumps(create_args)
        return self._create(self.ensemble_url, body)
