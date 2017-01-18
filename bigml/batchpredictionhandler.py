# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2014-2017 BigML
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

"""Base class for batch predictions' REST calls

   https://bigml.com/developers/batchpredictions

"""

try:
    import simplejson as json
except ImportError:
    import json

from bigml.bigmlconnection import DOWNLOAD_DIR
from bigml.resourcehandler import ResourceHandler
from bigml.resourcehandler import (check_resource_type,
                                   get_batch_prediction_id)
from bigml.constants import (BATCH_PREDICTION_PATH, ENSEMBLE_PATH,
                             MODEL_PATH, LOGISTIC_REGRESSION_PATH)


class BatchPredictionHandler(ResourceHandler):
    """This class is used by the BigML class as
       a mixin that provides the REST calls models. It should not
       be instantiated independently.

    """
    def __init__(self):
        """Initializes the BatchPredictionHandler. This class is intended to be
           used as a mixin on ResourceHandler, that inherits its
           attributes and basic method from BigMLConnection, and must not be
           instantiated independently.

        """
        self.batch_prediction_url = self.url + BATCH_PREDICTION_PATH

    def create_batch_prediction(self, model, dataset,
                                args=None, wait_time=3, retries=10):
        """Creates a new batch prediction.

           The model parameter can be:
            - a simple model
            - an ensemble

        """
        create_args = {}
        if args is not None:
            create_args.update(args)

        model_types = [ENSEMBLE_PATH, MODEL_PATH, LOGISTIC_REGRESSION_PATH]
        origin_resources_checked = self.check_origins(
            dataset, model, create_args, model_types=model_types,
            wait_time=wait_time, retries=retries)
        if origin_resources_checked:
            body = json.dumps(create_args)
            return self._create(self.batch_prediction_url, body)

    def get_batch_prediction(self, batch_prediction, query_string=''):
        """Retrieves a batch prediction.

           The batch_prediction parameter should be a string containing the
           batch_prediction id or the dict returned by create_batch_prediction.
           As batch_prediction is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, the function will
           return a dict that encloses the batch_prediction values and state
           info available at the time it is called.
        """
        check_resource_type(batch_prediction, BATCH_PREDICTION_PATH,
                            message="A batch prediction id is needed.")
        batch_prediction_id = get_batch_prediction_id(batch_prediction)
        if batch_prediction_id:
            return self._get("%s%s" % (self.url, batch_prediction_id),
                             query_string=query_string)

    def download_batch_prediction(self, batch_prediction, filename=None):
        """Retrieves the batch predictions file.

           Downloads predictions, that are stored in a remote CSV file. If
           a path is given in filename, the contents of the file are downloaded
           and saved locally. A file-like object is returned otherwise.
        """
        check_resource_type(batch_prediction, BATCH_PREDICTION_PATH,
                            message="A batch prediction id is needed.")
        batch_prediction_id = get_batch_prediction_id(batch_prediction)
        if batch_prediction_id:
            return self._download("%s%s%s" % (self.url, batch_prediction_id,
                                              DOWNLOAD_DIR), filename=filename)

    def list_batch_predictions(self, query_string=''):
        """Lists all your batch predictions.

        """
        return self._list(self.batch_prediction_url, query_string)

    def update_batch_prediction(self, batch_prediction, changes):
        """Updates a batch prediction.

        """
        check_resource_type(batch_prediction, BATCH_PREDICTION_PATH,
                            message="A batch prediction id is needed.")
        batch_prediction_id = get_batch_prediction_id(batch_prediction)
        if batch_prediction_id:
            body = json.dumps(changes)
            return self._update("%s%s" % (self.url, batch_prediction_id), body)

    def delete_batch_prediction(self, batch_prediction):
        """Deletes a batch prediction.

        """
        check_resource_type(batch_prediction, BATCH_PREDICTION_PATH,
                            message="A batch prediction id is needed.")
        batch_prediction_id = get_batch_prediction_id(batch_prediction)
        if batch_prediction_id:
            return self._delete("%s%s" % (self.url, batch_prediction_id))
