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

"""Base class for predictions' REST calls

   https://bigml.com/api/predictions

"""

try:
    import simplejson as json
except ImportError:
    import json


from bigml.api_handlers.resourcehandler import ResourceHandlerMixin
from bigml.api_handlers.resourcehandler import check_resource_type, \
    check_resource, get_resource_id, get_resource_type
from bigml.constants import SUPERVISED_PATHS, IMAGE_FIELDS_FILTER, \
    PREDICTION_PATH, FIELDS_PARENT, SPECIFIC_EXCLUDES


class PredictionHandlerMixin(ResourceHandlerMixin):
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
        self.prediction_url = self.prediction_base_url + PREDICTION_PATH

    def create_prediction(self, model, input_data=None,
                          args=None, wait_time=3, retries=10):
        """Creates a new prediction.
           The model parameter can be:
            - a simple tree model
            - a simple logistic regression model
            - an ensemble
            - a deepnet
            . a linear regression
            - a fusion
           Note that the old `by_name` argument has been deprecated.

        """
        model_id = None

        resource_type = get_resource_type(model)
        if resource_type not in SUPERVISED_PATHS:
            raise Exception("A supervised model resource id is needed"
                            " to create a prediction. %s found." %
                            resource_type)

        model_id = get_resource_id(model)
        if model_id is None:
            raise Exception("Failed to detect a correct model structure"
                " in %s." % model)

        if isinstance(model, dict) and model.get("resource") is not None:
            # retrieving fields info from model structure
            model_info = model
        else:
            image_fields_filter = IMAGE_FIELDS_FILTER + "," + \
                ",".join(SPECIFIC_EXCLUDES[resource_type])
            model_info = check_resource(model_id,
                                        query_string=IMAGE_FIELDS_FILTER,
                                        wait_time=wait_time,
                                        retries=retries,
                                        raise_on_error=True,
                                        api=self)

        if input_data is None:
            input_data = {}
        create_args = {}
        if args is not None:
            create_args.update(args)
        create_args.update({
            "input_data": self.prepare_image_fields(model_info, input_data)})
        if model_id is not None:
            create_args.update({
                "model": model_id})

        body = json.dumps(create_args)
        return self._create(self.prediction_url, body,
                            verify=self.verify_prediction)

    def get_prediction(self, prediction, query_string=''):
        """Retrieves a prediction.

        """
        check_resource_type(prediction, PREDICTION_PATH,
                            message="A prediction id is needed.")
        return self.get_resource(prediction, query_string=query_string)

    def list_predictions(self, query_string=''):
        """Lists all your predictions.

        """
        return self._list(self.prediction_url, query_string)

    def update_prediction(self, prediction, changes):
        """Updates a prediction.

        """
        check_resource_type(prediction, PREDICTION_PATH,
                            message="A prediction id is needed.")
        return self.update_resource(prediction, changes)

    def delete_prediction(self, prediction):
        """Deletes a prediction.

        """
        check_resource_type(prediction, PREDICTION_PATH,
                            message="A prediction id is needed.")
        return self.delete_resource(prediction)
