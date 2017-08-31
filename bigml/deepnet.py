# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2017 BigML
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

"""A local Predictive Deepnet.

This module defines a Deepnet to make predictions locally or
embedded into your application without needing to send requests to
BigML.io.

This module cannot only save you a few credits, but also enormously
reduce the latency for each prediction and let you use your models
offline.

You can also visualize your predictive model in IF-THEN rule format
and even generate a python function that implements the model.

Example usage (assuming that you have previously set up the BIGML_USERNAME
and BIGML_API_KEY environment variables and that you own the model/id below):

from bigml.api import BigML
from bigml.deepnet import Deepnet

api = BigML()

deepnet = Deepnet('deepnet/5026965515526876630001b2')
deepnet.predict({"petal length": 3, "petal width": 1})

"""
import logging
import sys
import json


from bigml.api import FINISHED
from bigml.api import BigML, get_deepnet_id, get_status
from bigml.util import cast
from bigml.basemodel import retrieve_resource, extract_objective
from bigml.basemodel import ONLY_MODEL
from bigml.modelfields import check_model_fields, ModelFields
from bigml.laminar.constants import NUMERIC, CATEGORICAL

try:
    import numpy
    import scipy
    import bigml.laminar.numpy_ops as net
    import bigml.laminar.preprocess_np as pp
except ImportError:
    import bigml.laminar.math_ops as net
    import bigml.laminar.preprocess as pp



LOGGER = logging.getLogger('BigML')

STORAGE = './storage'
MEAN = "mean"
STANDARD_DEVIATION = "stdev"

def moments(amap):
    return amap[MEAN], amap[STANDARD_DEVIATION]


def propagate(x_in, layers):
    last_X = identities = x_in[0]

    for layer in layers:
        w = layer['weights']
        m = layer['mean']
        s = layer['stdev']
        b = layer['offset']
        g = layer['scale']

        afn = layer['activation_function']

        X_dot_w = net.dot(last_X, w)

        if m is not None and s is not None:
            next_in = net.batch_norm(X_dot_w, m, s, b, g)
        else:
            next_in = net.plus(X_dot_w, b)

        if layer['residuals']:
            next_in = net.add_residuals(next_in, identities)
            last_X = net.ACTIVATORS[afn](next_in)
            identities = last_X
        else:
            last_X = net.ACTIVATORS[afn](next_in)

    return [last_X]


class Deepnet(ModelFields):
    """ A lightweight wrapper around Deepnet model.

    Uses a BigML remote model to build a local version that can be used
    to generate predictions locally.

    """

    def __init__(self, deepnet, api=None):
        """The Deepnet constructor can be given as first argument:
            - a deepnet structure
            - a deepnet id
            - a path to a JSON file containing a deepnet structure

        """
        self.resource_id = None
        self.regression = False
        self.layers = None
        self.output_exposition = None
        self.input_fields = []
        self.class_names = []
        self.preprocess = []
        self.missing_numerics = False
        # the string can be a path to a JSON file
        if isinstance(deepnet, basestring):
            try:
                with open(deepnet) as deepnet_file:
                    deepnet = json.load(deepnet_file)
                    self.resource_id = get_deepnet_id(deepnet)
                    if self.resource_id is None:
                        raise ValueError("The JSON file does not seem"
                                         " to contain a valid BigML deepnet"
                                         " representation.")
            except IOError:
                # if it is not a path, it can be a deepnet id
                self.resource_id = get_deepnet_id(deepnet)
                if self.resource_id is None:
                    if deepnet.find('deepnet/') > -1:
                        raise Exception(
                            api.error_message(deepnet,
                                              resource_type='deepnet',
                                              method='get'))
                    else:
                        raise IOError("Failed to open the expected JSON file"
                                      " at %s" % deepnet)
            except ValueError:
                raise ValueError("Failed to interpret %s."
                                 " JSON file expected.")

        # checks whether the information needed for local predictions is in
        # the first argument
        if isinstance(deepnet, dict) and \
                not fields and \
                not check_model_fields(deepnet):
            # if the fields used by the deepenet are not
            # available, use only ID to retrieve it again
            deepnet = get_deepnet_id(deepnet)
            self.resource_id = deepnet

        if not (isinstance(deepnet, dict) and 'resource' in deepnet and
                deepnet['resource'] is not None):
            if api is None:
                api = BigML(storage=STORAGE)
            query_string = ONLY_MODEL
            deepnet = retrieve_resource(api, self.resource_id,
                                        query_string=query_string)
        else:
            self.resource_id = get_deepnet_id(deepnet)
        if 'object' in deepnet and isinstance(deepnet['object'], dict):
            deepnet = deepnet['object']
            self.input_fields = deepnet['input_fields']
        if 'deepnet' in deepnet and isinstance(deepnet['deepnet'], dict):
            status = get_status(deepnet)
            deepnet = deepnet['deepnet']
            if 'code' in status and status['code'] == FINISHED:
                self.fields = deepnet['fields']
                objective_field = deepnet['objective_fields']
                ModelFields.__init__(
                    self, self.fields,
                    objective_id=extract_objective(objective_field))

                self.regression = \
                    self.fields[self.objective_id]['optype'] == 'numeric'
                if not self.regression:
                    self.class_names = [category for category,_ in \
                        self.fields[self.objective_id][ \
                        'summary']['categories']]

                self.missing_numerics = deepnet.get('missing_numerics', False)
           # TODO: add properties here
                if 'network' in deepnet:
                    network = deepnet['network']

                    self.layers = net.init_layers(network['layers'])
                    self.output_exposition = network['output_exposition']
                    self.preprocess = network['preprocess']
                    self.beta1 = network.get('beta1', 0.9)
                    self.beta2 = network.get('beta2', 0.999)
                    self.decay = network.get('decay', 0.0)
                    self.descent_algorithm = network.get('descent_algorithm',
                                                         'adam')
                    self.epsilon = network.get('epsilon', 1e-08)
                    self.hidden_layers = network.get('hidden_layers', [])
                    self.initial_accumulator_value = network.get( \
                        'initial_accumulator_value', 0)
                    self.l1_regularization = network.get( \
                        'l1_regularization', 0)
                    self.l2_regularization = network.get( \
                        'l2_regularization', 0)
                    self.learning_rate = network.get('learning_rate', 0.001)
                    self.learning_rate_power = network.get( \
                        'learning_rate_power', -0.5)
                    # max_iterations or max_training_time needs to be filled
                    self.max_iterations = network.get('max_iterations')
                    self.max_training_time = network.get('max_training_time',
                                                         1800)
                    self.momentum = network.get('momentum', 0.99)
            else:
                raise Exception("The deepnet isn't finished yet")
        else:
            raise Exception("Cannot create the Deepnet instance. Could not"
                            " find the 'deepnet' key in the resource:\n\n%s" %
                            deepnet)

    def fill_array(self, input_data):
        """ Filling the input array for the network with the data in the
        input_data dictionary. Numeric missings are added as a new field
        and texts/items are processed.
        """
        columns = []
        for field_id in self.input_fields:
            columns.append([input_data.get(field_id, None)])
        return pp.preprocess(columns, self.preprocess)

    def predict(self, input_data, by_name=True, add_unused_fields=False):
        """Makes a prediction based on a number of field values.


        """

        # Checks and cleans input_data leaving the fields used in the model
        new_data = self.filter_input_data( \
            input_data, by_name=by_name,
            add_unused_fields=add_unused_fields)
        if add_unused_fields:
            input_data, unused_fields = new_data
        else:
            input_data = new_data

        # Strips affixes for numeric values and casts to the final field type
        cast(input_data, self.fields)

        input_array = self.fill_array(input_data)

        x_in = [input_array]

        """
        if self.trees is not None:
            x_in = tree_transform(x_in, self.trees, None)
        """

        y_out = propagate(x_in, self.layers)

        if self.regression:
            y_mean, y_stdev = moments(self.output_exposition)
            y_out = net.destandardize(y_out, y_mean, y_stdev)

        return y_out[0]
