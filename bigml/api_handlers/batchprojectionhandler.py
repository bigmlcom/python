# -*- coding: utf-8 -*-
#
# Copyright 2018-2022 BigML
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

"""Base class for batch projections' REST calls

   https://bigml.com/api/batchprojections

"""

try:
    import simplejson as json
except ImportError:
    import json

from bigml.api_handlers.resourcehandler import ResourceHandlerMixin
from bigml.api_handlers.resourcehandler import check_resource_type
from bigml.constants import BATCH_PROJECTION_PATH, PCA_PATH


class BatchProjectionHandlerMixin(ResourceHandlerMixin):
    """This class is used by the BigML class as
       a mixin that provides the REST calls models. It should not
       be instantiated independently.

    """
    def __init__(self):
        """Initializes the BatchProjectionHandler. This class is intended to be
           used as a mixin on ResourceHandler, that inherits its
           attributes and basic method from BigMLConnection, and must not be
           instantiated independently.

        """
        self.batch_projection_url = self.prediction_base_url + \
            BATCH_PROJECTION_PATH

    def create_batch_projection(self, pca, dataset,
                                args=None, wait_time=3, retries=10):
        """Creates a new batch projection.

           The pca parameter can be a pca resoruce or ID

        """
        create_args = {}
        if args is not None:
            create_args.update(args)

        origin_resources_checked = self.check_origins(
            dataset, pca, create_args, model_types=[PCA_PATH],
            wait_time=wait_time, retries=retries)
        if origin_resources_checked:
            body = json.dumps(create_args)
            return self._create(self.batch_projection_url, body)

    def get_batch_projection(self, batch_projection, query_string=''):
        """Retrieves a batch projection.

           The batch_projection parameter should be a string containing the
           batch_projection id or the dict returned by create_batch_projection.
           As batch_projection is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, the function will
           return a dict that encloses the batch_projection values and state
           info available at the time it is called.
        """
        check_resource_type(batch_projection, BATCH_PROJECTION_PATH,
                            message="A batch projection id is needed.")
        return self.get_resource(batch_projection, query_string=query_string)

    def download_batch_projection(self, batch_projection, filename=None,
                                  retries=10):
        """Retrieves the batch projections file.

           Downloads projections, that are stored in a remote CSV file. If
           a path is given in filename, the contents of the file are downloaded
           and saved locally. A file-like object is returned otherwise.
        """
        check_resource_type(batch_projection, BATCH_PROJECTION_PATH,
                            message="A batch projection id is needed.")
        return self._download_resource(batch_projection, filename,
                                       retries=retries)

    def list_batch_projections(self, query_string=''):
        """Lists all your batch projections.

        """
        return self._list(self.batch_projection_url, query_string)

    def update_batch_projection(self, batch_projection, changes):
        """Updates a batch projection.

        """
        check_resource_type(batch_projection, BATCH_PROJECTION_PATH,
                            message="A batch projection id is needed.")
        return self.update_resource(batch_projection, changes)

    def delete_batch_projection(self, batch_projection):
        """Deletes a batch projection.

        """
        check_resource_type(batch_projection, BATCH_PROJECTION_PATH,
                            message="A batch projection id is needed.")
        return self.delete_resource(batch_projection)
