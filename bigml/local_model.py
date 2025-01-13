# -*- coding: utf-8 -*-
# pylint: disable=super-init-not-called
#
# Copyright 2023-2025 BigML
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

"""A local Predictive model class abstracting all kind of models

This module abstracts any BigML model to make predictions locally or
embedded into your application without needing to send requests to
BigML.io.

This module cannot only save you a few credits, but also enormously
reduce the latency for each prediction and let you use your supervised models
offline.

Example usage (assuming that you have previously set up the BIGML_USERNAME
and BIGML_API_KEY environment variables and that you own the
logisticregression/id below):

from bigml.api import BigML
from bigml.local_model import LocalModel

api = BigML()

model = LocalModel(
    'logisticregression/5026965515526876630001b2')
model.predict({"petal length": 3, "petal width": 1,
               "sepal length": 1, "sepal width": 0.5})

"""

import json
import os


from bigml.api import get_resource_id, get_resource_type, \
    get_api_connection, get_ensemble_id
from bigml.basemodel import BaseModel
from bigml.model import Model
from bigml.ensemble import Ensemble
from bigml.logistic import LogisticRegression
from bigml.deepnet import Deepnet
from bigml.linear import LinearRegression
from bigml.fusion import Fusion
from bigml.cluster import Cluster
from bigml.anomaly import Anomaly
from bigml.association import Association
from bigml.timeseries import TimeSeries
try:
    from bigml.topicmodel import TopicModel
    TOPIC_ENABLED = True
except ImportError:
    TOPIC_ENABLED = False
from bigml.pca import PCA
from bigml.constants import OUT_NEW_FIELDS, OUT_NEW_HEADERS, INTERNAL
from bigml.util import get_data_format, get_formatted_data, format_data


SUPERVISED_CLASSES = {
    "model": Model,
    "ensemble": Ensemble,
    "logisticregression": LogisticRegression,
    "deepnet": Deepnet,
    "linearregression": LinearRegression,
    "fusion": Fusion}


DFT_OUTPUTS = ["prediction", "probability"]


MODEL_CLASSES = {
    "cluster": Cluster,
    "anomaly": Anomaly,
    "association": Association,
    "pca": PCA,
    "timeseries": TimeSeries}
MODEL_CLASSES.update(SUPERVISED_CLASSES)
if TOPIC_ENABLED:
    MODEL_CLASSES.update({"topicmodel": TopicModel})


def extract_id(model, api):
    """Extract the resource id from:
        - a resource ID string
        - a list of resources (ensemble +  models)
        - a resource structure
        - the name of the file that contains a resource structure

    """
    # the string can be a path to a JSON file
    if isinstance(model, str):
        try:
            path = os.path.dirname(os.path.abspath(model))
            with open(model) as model_file:
                model = json.load(model_file)
                resource_id = get_resource_id(model)
                if resource_id is None:
                    raise ValueError("The JSON file does not seem"
                                     " to contain a valid BigML resource"
                                     " representation.")
                api.storage = path
        except IOError:
            # if it is not a path, it can be a model id
            resource_id = get_resource_id(model)
            if resource_id is None:
                for resource_type in MODEL_CLASSES.keys():
                    if model.find("%s/" % resource_type) > -1:
                        raise Exception(
                            api.error_message(model,
                                              resource_type=resource_type,
                                              method="get"))
                raise IOError("Failed to open the expected JSON file"
                              " at %s." % model)
        except ValueError:
            raise ValueError("Failed to interpret %s."
                             " JSON file expected.")
    if isinstance(model, list):
        resource_id = get_ensemble_id(model[0])
        if resource_id is None:
            raise ValueError("The first argument does not contain a valid"
                             " BigML model structure.")
    else:
        resource_id = get_resource_id(model)
        if resource_id is None:
            raise ValueError("The first argument does not contain a valid"
                             " BigML model structure.")
    return resource_id, model


class LocalModel(BaseModel):
    """ A lightweight wrapper around any BigML model.

    Uses any BigML remote model to build a local version
    that can be used to generate predictions locally.

    """

    def __init__(self, model, api=None, cache_get=None,
                 operation_settings=None):

        self.api = get_api_connection(api)
        resource_id, model = extract_id(model, self.api)
        resource_type = get_resource_type(resource_id)
        if resource_type == "topicmodel" and not TOPIC_ENABLED:
            raise ValueError("Failed to import the TopicModel class. "
                "Please, check the bindings extra options to install"
                " the class.")
        kwargs = {"api": self.api, "cache_get": cache_get}
        if resource_type in SUPERVISED_CLASSES.keys() and \
                resource_type != "linearregression":
            kwargs.update({"operation_settings": operation_settings})
        local_model = MODEL_CLASSES[resource_type](model, **kwargs)
        self.__class__.__bases__ = local_model.__class__.__bases__
        for attr, value in list(local_model.__dict__.items()):
            setattr(self, attr, value)
        self.local_model = local_model
        self.supervised = resource_type in SUPERVISED_CLASSES.keys()
        self.name = self.local_model.name
        self.description = self.local_model.description

    def predict(self, *args, **kwargs):
        """Delegating method to local model object"""
        return self.local_model.predict(*args, **kwargs)

    def data_transformations(self):
        """Returns the pipeline transformations previous to the modeling
        step as a pipeline, so that they can be used in local predictions.
        """
        return self.local_model.data_transformations()

    def batch_predict(self, input_data_list, outputs=None, **kwargs):
        """Creates a batch prediction for a list of inputs using the local
        BigML model. Allows to define some output settings to
        decide the fields to be added to the input_data (prediction,
        probability, etc.) and the name that we want to assign to these new
        fields. The outputs argument accepts a dictionary with keys
        "output_fields", to contain a list of the prediction properties to add
        (["prediction", "probability"] by default) and "output_headers", to
        contain a list of the headers to be used when adding them (identical
        to "output_fields" list, by default).

        :param input_data_list: List of input data to be predicted
        :type input_data_list: list or Panda's dataframe
        :param dict outputs: properties that define the headers and fields to
                             be added to the input data
        :return: the list of input data plus the predicted values
        :rtype: list or Panda's dataframe depending on the input type in
                input_data_list
        """
        if isinstance(self.local_model, (Association, TimeSeries)):
            raise ValueError("The method is not available for Associations or "
                  "TimeSeries.")
        if self.supervised:
            if outputs is None:
                outputs = {}
            new_fields = outputs.get(OUT_NEW_FIELDS, DFT_OUTPUTS)
            new_headers = outputs.get(OUT_NEW_HEADERS, new_fields)
            if len(new_fields) > len(new_headers):
                new_headers.expand(new_fields[len(new_headers):])
            else:
                new_headers = new_headers[0: len(new_fields)]
            data_format = get_data_format(input_data_list)
            inner_data_list = get_formatted_data(input_data_list, INTERNAL)
            kwargs.update({"full": True})
            for input_data in inner_data_list:
                prediction = self.predict(input_data, **kwargs)
                for index, key in enumerate(new_fields):
                    try:
                        input_data[new_headers[index]] = prediction[key]
                    except KeyError:
                        pass
            if data_format != INTERNAL:
                return format_data(inner_data_list, out_format=data_format)
            return inner_data_list
        return self.local_model.batch_predict(input_data_list,
            outputs=outputs, **kwargs)

    #pylint: disable=locally-disabled,arguments-differ
    def dump(self, **kwargs):
        """Delegate to local model"""
        self.local_model.dump(**kwargs)

    def dumps(self):
        """Delegate to local model"""
        return self.local_model.dumps()
