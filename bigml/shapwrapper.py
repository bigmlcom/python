# -*- coding: utf-8 -*-
# pylint: disable=super-init-not-called
#
# Copyright 2023 BigML
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

"""A wrapper for models to produce predictions as expected by Shap Explainer

"""
import numpy as np

from bigml.supervised import SupervisedModel, extract_id
from bigml.fusion import Fusion
from bigml.fields import Fields
from bigml.api import get_resource_type, get_api_connection


class ShapWrapper():
    """ A lightweight wrapper around any supervised model that offers a
    predict method adapted to the expected Shap Explainer syntax"""

    def __init__(self, model, api=None, cache_get=None,
                 operation_settings=None):

        self.api = get_api_connection(api)
        resource_id, model = extract_id(model, self.api)
        resource_type = get_resource_type(resource_id)
        model_class = Fusion if resource_type == "fusion" else SupervisedModel
        self.local_model = model_class(model, api=api, cache_get=cache_get,
            operation_settings=operation_settings)
        objective_id = getattr(self.local_model, "objective_id", None)
        self.fields = Fields(self.local_model.fields,
                             objective_field=objective_id)
        self.x_headers = [self.fields.field_name(field_id) for field_id in
                          self.fields.sorted_field_ids()]
        self.y_header = self.fields.field_name(self.fields.objective_field)

    def predict(self, x_test, **kwargs):
        """Prediction method that interfaces with the Shap library"""
        input_data_list = self.fields.from_numpy(x_test)
        batch_prediction = self.local_model.batch_predict(
            input_data_list, outputs={"output_fields": ["prediction"],
                                      "output_headers": [self.y_header]},
            all_fields=False, **kwargs)
        objective_field = self.fields.objective_field_info()
        pred_fields = Fields(objective_field)
        return pred_fields.to_numpy(batch_prediction,
                                    objective=True).reshape(-1)

    def predict_proba(self, x_test):
        """Prediction method that interfaces with the Shap library"""
        if self.local_model.regression:
            raise ValueError("This method is only available for classification"
                             " models.")
        input_data_list = self.fields.from_numpy(x_test)
        predictions = np.ndarray([])
        for input_data in inner_data_list:
            prediction = self.predict_probability(input_data, compact=True)
            np.append(predictions, np.ndarray(prediction))
        return predictions
