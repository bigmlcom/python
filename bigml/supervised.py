# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2018-2019 BigML
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

"""A local Predictive Supervised model class

This module defines a supervised model to make predictions locally or
embedded into your application without needing to send requests to
BigML.io.

This module cannot only save you a few credits, but also enormously
reduce the latency for each prediction and let you use your supervised models
offline.

Example usage (assuming that you have previously set up the BIGML_USERNAME
and BIGML_API_KEY environment variables and that you own the
logisticregression/id below):

from bigml.api import BigML
from bigml.supervised import SupervisedModel

api = BigML()

model = SupervisedModel(
    'logisticregression/5026965515526876630001b2')
model.predict({"petal length": 3, "petal width": 1,
               "sepal length": 1, "sepal width": 0.5})

"""

import json


from bigml.api import get_resource_id, get_resource_type, BigML
from bigml.model import Model
from bigml.ensemble import Ensemble
from bigml.logistic import LogisticRegression
from bigml.deepnet import Deepnet
from bigml.linear import LinearRegression
from bigml.basemodel import BaseModel
from bigml.constants import STORAGE


COMPONENT_CLASSES = {
    "model": Model,
    "ensemble": Ensemble,
    "logisticregression": LogisticRegression,
    "deepnet": Deepnet,
    "linearregression": LinearRegression}


def extract_id(model, api):
    """Extract the resource id from:
        - a resource ID string
        - a resource structure
        - the name of the file that contains a resource structure

    """
    # the string can be a path to a JSON file
    if isinstance(model, basestring):
        try:
            with open(model) as model_file:
                model = json.load(model_file)
                resource_id = get_resource_id(model)
                if resource_id is None:
                    raise ValueError("The JSON file does not seem"
                                     " to contain a valid BigML resource"
                                     " representation.")
        except IOError:
            # if it is not a path, it can be a model id
            resource_id = get_resource_id(model)
            if resource_id is None:
                if model.find('model/') > -1:
                    raise Exception(
                        api.error_message(model,
                                          resource_type='model',
                                          method='get'))
                else:
                    raise IOError("Failed to open the expected JSON file"
                                  " at %s" % model)
        except ValueError:
            raise ValueError("Failed to interpret %s."
                             " JSON file expected.")
    else:
        resource_id = get_resource_id(model)
        if resource_id is None:
            raise ValueError("The first argument does not contain a valid"
                             " supervised model structure.")
    return resource_id, model


class SupervisedModel(BaseModel):
    """ A lightweight wrapper around any supervised model.

    Uses any BigML remote supervised model to build a local version
    that can be used to generate predictions locally.

    """

    def __init__(self, model, api=None):

        if api is None:
            api = BigML(storage=STORAGE)
        resource_id, model = extract_id(model, api)
        resource_type = get_resource_type(resource_id)
        kwargs = {"api": api}
        local_model = COMPONENT_CLASSES[resource_type](model, **kwargs)
        self.__class__.__bases__ = local_model.__class__.__bases__
        for attr, value in local_model.__dict__.items():
            setattr(self, attr, value)
        self.local_model = local_model

    def predict(self, *args, **kwargs):
        return self.local_model.predict(*args, **kwargs)

    def predict_probability(self, *args, **kwargs):
        new_kwargs = {}
        new_kwargs.update(kwargs)
        try:
            return self.local_model.predict_probability(*args, **new_kwargs)
        except TypeError:
            del new_kwargs["missing_strategy"]
            return self.local_model.predict_probability(*args, **new_kwargs)
