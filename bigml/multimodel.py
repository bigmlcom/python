# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2012 BigML
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

"""A Multiple Local Predictive Model.

This module defines a Multiple Model to make predictions locally using multiple
local models.

This module cannot only save you a few credits, but also enormously
reduce the latency for each prediction and let you use your models
offline.

from bigml.api import BigML
from bigml.model import MultipleModel

api = BigML()

model = MultipleModel([api.get_model('model/5026965515526876630001b2')])
model.predict({"petal length": 3, "petal width": 1})

"""
import logging
LOGGER = logging.getLogger('BigML')

import numbers
from bigml.model import Model

def avg(data):
    return float(sum(data))/len(data) if len(data) > 0 else float('nan')

def combine_predictions(predictions):
    """Reduces a number of predictions voting for classification and averaging
    predictions for regression.

    """
    if all([isinstance(prediction, numbers.Number) for prediction in
        predictions]):
        return avg(predictions)
    else:
        mode = {}
        for prediction in predictions:
            if prediction in mode:
                mode[prediction] = mode[prediction] + 1
            else:
                mode[prediction] = 1
        return max(mode)

class MultiModel(object):
    """A multiple local model.

    Uses a numbers of BigML remote models to build a local version that can be
    used to generate predictions locally.

    """

    def __init__(self, models):
        self.models = []
        if isinstance(models, list):
            for model in models:
                self.models.append(Model(model))
        else:
            self.models.apend(Model(models))


    def predict(self, input_data, by_name=False):
        """Makes a prediction based on the prediction made by every model.

        """

        predictions = []
        for model in self.models:
            predictions.append(model.predict(input_data, by_name=by_name))

        return combine_predictions(predictions)
