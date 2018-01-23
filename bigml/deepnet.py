# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2017-2018 BigML
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
import json


from bigml.api import FINISHED
from bigml.api import BigML, get_deepnet_id, get_status
from bigml.util import cast, PRECISION
from bigml.basemodel import retrieve_resource, extract_objective
from bigml.basemodel import ONLY_MODEL
from bigml.modelfields import check_model_fields, ModelFields
from bigml.laminar.constants import NUMERIC
from bigml.model import parse_operating_point, sort_categories

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


def expand_terms(terms_list, input_terms):
    """Builds a list of occurrences for all the available terms

    """
    terms_occurrences = [0.0] * len(terms_list)
    for term, occurrences in input_terms:
        index = terms_list.index(term)
        terms_occurrences[index] = occurrences
    return terms_occurrences


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
        self.network = None
        self.networks = None
        self.input_fields = []
        self.class_names = []
        self.preprocess = []
        self.optimizer = None
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
            objective_field = deepnet['objective_fields']
            deepnet = deepnet['deepnet']
            if 'code' in status and status['code'] == FINISHED:
                self.fields = deepnet['fields']
                ModelFields.__init__(
                    self, self.fields,
                    objective_id=extract_objective(objective_field),
                    terms=True, categories=True)

                self.regression = \
                    self.fields[self.objective_id]['optype'] == NUMERIC
                if not self.regression:
                    self.class_names = [category for category,_ in \
                        self.fields[self.objective_id][ \
                        'summary']['categories']]
                    self.class_names.sort()

                self.missing_numerics = deepnet.get('missing_numerics', False)
                if 'network' in deepnet:
                    network = deepnet['network']
                    self.network = network
                    self.networks = network.get('networks', [])
                    self.preprocess = network.get('preprocess')
                    self.optimizer = network.get('optimizer', {})
            else:
                raise Exception("The deepnet isn't finished yet")
        else:
            raise Exception("Cannot create the Deepnet instance. Could not"
                            " find the 'deepnet' key in the resource:\n\n%s" %
                            deepnet)

    def fill_array(self, input_data, unique_terms):
        """ Filling the input array for the network with the data in the
        input_data dictionary. Numeric missings are added as a new field
        and texts/items are processed.
        """
        columns = []
        for field_id in self.input_fields:
            # if the field is text or items, we need to expand the field
            # in one field per term and get its frequency
            if field_id in self.tag_clouds:
                terms_occurrences = expand_terms(self.tag_clouds[field_id],
                                                 unique_terms.get(field_id,
                                                                  []))
                columns.extend(terms_occurrences)
            elif field_id in self.items:
                terms_occurrences = expand_terms(self.items[field_id],
                                                 unique_terms.get(field_id,
                                                                  []))
                columns.extend(terms_occurrences)
            elif field_id in self.categories:
                category = unique_terms.get(field_id)
                if category is not None:
                    category = category[0][0]
                columns.append([category])
            else:
                # when missing_numerics is True and the field had missings
                # in the training data, then we add a new "is missing?" element
                # whose value is 1 or 0 according to whether the field is
                # missing or not in the input data
                if self.missing_numerics \
                        and self.fields[field_id][\
                        "summary"]["missing_count"] > 0:
                    if field_id in input_data:
                        columns.extend([input_data[field_id], 0.0])
                    else:
                        columns.extend([0.0, 1.0])
                else:
                    columns.append(input_data.get(field_id))
        return pp.preprocess(columns, self.preprocess)

    def predict(self, input_data, by_name=True, add_unused_fields=False,
                operating_point=None, operating_kind=None):
        """Makes a prediction based on a number of field values.

        input_data: Input data to be predicted
        by_name: Boolean, True if input_data is keyed by names
        add_unused_fields: Boolean, if True adds the information about the
                           fields in the input_data that are not being used
                           in the model as predictors.
        operating_point: In classification models, this is the point of the
                         ROC curve where the model will be used at. The
                         operating point can be defined in terms of:
                         - the positive_class, the class that is important to
                           predict accurately
                         - the probability_threshold,
                           the probability that is stablished
                           as minimum for the positive_class to be predicted.
                         The operating_point is then defined as a map with
                         two attributes, e.g.:
                           {"positive_class": "Iris-setosa",
                            "probability_threshold": 0.5}
        operating_kind: "probability". Sets the
                        property that decides the prediction. Used only if
                        no operating_point is used
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

        # When operating_point is used, we need the probabilities
        # of all possible classes to decide, so se use
        # the `predict_probability` method
        if operating_point:
            if self.regression:
                raise ValueError("The operating_point argument can only be"
                                 " used in classifications.")
            return self.predict_operating( \
                input_data, by_name=False, operating_point=operating_point)
        if operating_kind:
            if self.regression:
                raise ValueError("The operating_point argument can only be"
                                 " used in classifications.")
            return self.predict_operating_kind( \
                input_data, by_name=False, operating_kind=operating_kind)

        # Computes text and categorical field expansion
        unique_terms = self.get_unique_terms(input_data)

        input_array = self.fill_array(input_data, unique_terms)

        if self.networks:
            prediction = self.predict_list(input_array)
        else:
            prediction = self.predict_single(input_array)
        if add_unused_fields:
            prediction.update({"unused_fields": unused_fields})

        return prediction

    def predict_single(self, input_array):
        """Makes a prediction with a single network

        """
        if self.network['trees'] is not None:
            input_array = pp.tree_transform(input_array, self.network['trees'])

        return self.to_prediction(self.model_predict(input_array,
                                                     self.network))

    def predict_list(self, input_array):
        if self.network['trees'] is not None:
            input_array_trees = pp.tree_transform(input_array,
                                                  self.network['trees'])
        youts = []
        for model in self.networks:
            if model['trees']:
                youts.append(self.model_predict(input_array_trees, model))
            else:
                youts.append(self.model_predict(input_array, model))

        return self.to_prediction(net.sum_and_normalize(youts,
                                                        self.regression))

    def model_predict(self, input_array, model):
        """Prediction with one model

        """

        layers = net.init_layers(model['layers'])
        y_out = net.propagate(input_array, layers)

        if self.regression:
            y_mean, y_stdev = moments(model['output_exposition'])
            y_out = net.destandardize(y_out, y_mean, y_stdev)
            return y_out[0][0]

        return y_out

    def to_prediction(self, y_out):
        """Structuring prediction in a dictionary output

        """
        if self.regression:
            return y_out
        prediction = sorted(enumerate(y_out[0]), key=lambda x: -x[1])[0]
        prediction = {"prediction": self.class_names[prediction[0]],
                      "probability": round(prediction[1], PRECISION),
                      "distribution": [{"category": category,
                                        "probability": round(y_out[0][i],
                                                             PRECISION)} \
            for i, category in enumerate(self.class_names)]}

        return prediction

    def predict_probability(self, input_data, by_name=True, compact=False):
        """Predicts a probability for each possible output class,
        based on input values.  The input fields must be a dictionary
        keyed by field name or field ID.

        :param input_data: Input data to be predicted
        :param by_name: Boolean that is set to True if field_names (as
                        alternative to field ids) are used in the
                        input_data dict
        :param compact: If False, prediction is returned as a list of maps, one
                        per class, with the keys "prediction" and "probability"
                        mapped to the name of the class and it's probability,
                        respectively.  If True, returns a list of probabilities
                        ordered by the sorted order of the class names.
        """
        if self.regression:
            return self.predict(input_data,
                                by_name=by_name)
        else:
            distribution = self.predict(input_data,
                                        by_name=by_name)['distribution']
            distribution.sort(key=lambda x: x['category'])

            if compact:
                return [category['probability'] for category in distribution]
            else:
                return distribution

    def _sort_predictions(self, a, b, criteria):
        """Sorts the categories in the predicted node according to the
        given criteria

        """
        if a[criteria] == b[criteria]:
            return sort_categories(a, b, self.objective_categories)
        return 1 if b[criteria] > a[criteria] else - 1

    def predict_operating_kind(self, input_data, by_name=True,
                               operating_kind=None):
        """Computes the prediction based on a user-given operating kind.

        """

        kind = operating_kind.lower()
        if kind == "probability":
            predictions = self.predict_probability(input_data, by_name,
                                                   False)
        else:
            raise ValueError("Only probability is allowed as operating kind"
                             " for deepnets.")
        predictions.sort( \
            key=cmp_to_key( \
            lambda a, b : self._sort_predictions(a, b, kind)))
        prediction = predictions[0]
        prediction["prediction"] = prediction["category"]
        del prediction["category"]
        return prediction

    def predict_operating(self, input_data, by_name=True,
                          operating_point=None):
        """Computes the prediction based on a user-given operating point.

        """

        kind, threshold, positive_class = parse_operating_point( \
            operating_point, ["probability"], self.class_names)
        predictions = self.predict_probability(input_data, by_name, False)
        position = self.class_names.index(positive_class)
        if predictions[position][kind] > threshold:
            prediction = predictions[position]
        else:
            # if the threshold is not met, the alternative class with
            # highest probability or confidence is returned
            predictions.sort( \
                key=cmp_to_key( \
                lambda a, b : self._sort_predictions(a, b, kind)))
            prediction = predictions[0 : 2]
            if prediction[0]["category"] == positive_class:
                prediction = prediction[1]
            else:
                prediction = prediction[0]
        prediction["prediction"] = prediction["category"]
        del prediction["category"]
        return prediction
