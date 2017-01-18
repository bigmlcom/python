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

"""Base class for predictions' REST calls

   https://bigml.com/developers/predictions

"""

try:
    import simplejson as json
except ImportError:
    import json


from bigml.resourcehandler import ResourceHandler
from bigml.resourcehandler import (check_resource_type, get_prediction_id,
                                   check_resource, get_ensemble_id,
                                   get_model_id, get_logistic_regression_id,
                                   get_resource_type)
from bigml.constants import (PREDICTION_PATH, ENSEMBLE_PATH, MODEL_PATH,
                             LOGISTIC_REGRESSION_PATH, TINY_RESOURCE)

class PredictionHandler(ResourceHandler):
    """This class is used by the BigML class as
       a mixin that provides the REST calls models. It should not
       be instantiated independently.

    """
    def __init__(self):
        """Initializes the PredictionHandler. This class is intended to be
           used as a mixin on ResourceHandler, that inherits its
           attributes and basic method from BigMLConnection, and must not be
           instantiated independently.

        """
        self.prediction_url = self.prediction_url + PREDICTION_PATH

    def create_prediction(self, model, input_data=None,
                          args=None, wait_time=3, retries=10, by_name=True):
        """Creates a new prediction.
           The model parameter can be:
            - a simple tree model
            - a simple logistic regression model
            - an ensemble
           The by_name argument is now deprecated. It will be removed.

        """
        logistic_regression_id = None
        ensemble_id = None
        model_id = None

        resource_type = get_resource_type(model)
        if resource_type == ENSEMBLE_PATH:
            ensemble_id = get_ensemble_id(model)
            if ensemble_id is not None:
                check_resource(ensemble_id,
                               query_string=TINY_RESOURCE,
                               wait_time=wait_time, retries=retries,
                               raise_on_error=True, api=self)
        elif resource_type == MODEL_PATH:
            model_id = get_model_id(model)
            check_resource(model_id,
                           query_string=TINY_RESOURCE,
                           wait_time=wait_time, retries=retries,
                           raise_on_error=True, api=self)
        elif resource_type == LOGISTIC_REGRESSION_PATH:
            logistic_regression_id = get_logistic_regression_id(model)
            check_resource(logistic_regression_id,
                           query_string=TINY_RESOURCE,
                           wait_time=wait_time, retries=retries,
                           raise_on_error=True, api=self)
        else:
            raise Exception("A model or ensemble id is needed to create a"
                            " prediction. %s found." % resource_type)

        if input_data is None:
            input_data = {}
        create_args = {}
        if args is not None:
            create_args.update(args)
        create_args.update({
            "input_data": input_data})
        if model_id is not None:
            create_args.update({
                "model": model_id})
        elif ensemble_id is not None:
            create_args.update({
                "ensemble": ensemble_id})
        elif logistic_regression_id is not None:
            create_args.update({
                "logisticregression": logistic_regression_id})

        body = json.dumps(create_args)
        return self._create(self.prediction_url, body,
                            verify=self.verify_prediction)

    def get_prediction(self, prediction, query_string=''):
        """Retrieves a prediction.

        """
        check_resource_type(prediction, PREDICTION_PATH,
                            message="A prediction id is needed.")
        prediction_id = get_prediction_id(prediction)
        if prediction_id:
            return self._get("%s%s" % (self.url, prediction_id),
                             query_string=query_string)

    def list_predictions(self, query_string=''):
        """Lists all your predictions.

        """
        return self._list(self.prediction_url, query_string)

    def update_prediction(self, prediction, changes):
        """Updates a prediction.

        """
        check_resource_type(prediction, PREDICTION_PATH,
                            message="A prediction id is needed.")
        prediction_id = get_prediction_id(prediction)
        if prediction_id:
            body = json.dumps(changes)
            return self._update("%s%s" % (self.url, prediction_id), body)

    def delete_prediction(self, prediction):
        """Deletes a prediction.

        """
        check_resource_type(prediction, PREDICTION_PATH,
                            message="A prediction id is needed.")
        prediction_id = get_prediction_id(prediction)
        if prediction_id:
            return self._delete("%s%s" % (self.url, prediction_id))
