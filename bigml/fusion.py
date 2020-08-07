# -*- coding: utf-8 -*-
#
# Copyright 2012-2020 BigML
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

"""An local Fusion object.

This module defines a Fusion to make predictions locally using its
associated models.

This module can not only save you a few credits, but also enormously
reduce the latency for each prediction and let you use your models
offline.

from bigml.api import BigML
from bigml.fusion import Fusion

# api connection
api = BigML(storage='./storage')

# creating fusion
fusion = api.create_fusion(['model/5143a51a37203f2cf7000972',
                            'model/5143a51a37203f2cf7000985'])

# Fusion object to predict
fusion = Fusion(fusion, api)
fusion.predict({"petal length": 3, "petal width": 1})

"""
import logging
import json
import os

from functools import cmp_to_key

from bigml.api import BigML, get_fusion_id, get_resource_type, \
    get_api_connection
from bigml.model import parse_operating_point, sort_categories
from bigml.model import LAST_PREDICTION
from bigml.basemodel import get_resource_dict, retrieve_resource
from bigml.multivotelist import MultiVoteList
from bigml.util import cast, check_no_missing_numerics
from bigml.supervised import SupervisedModel
from bigml.modelfields import ModelFields



LOGGER = logging.getLogger('BigML')
OPERATING_POINT_KINDS = ["probability"]
LOCAL_SUPERVISED = ["model", "ensemble", "logisticregression", "deepnet",
                    "linearregression", "fusion"]


def rearrange_prediction(origin_classes, destination_classes, prediction):
    """Rearranges the probabilities in a compact array when the
       list of classes in the destination resource does not match the
       ones in the origin resource.

    """
    new_prediction = []
    for class_name in destination_classes:
        origin_index = origin_classes.index(class_name)
        if origin_index > -1:
            new_prediction.append(prediction[origin_index])
        else:
            new_prediction = 0.0
    return new_prediction


def get_models_weight(models_info):
    """Parses the information about model ids and weights in the `models`
    key of the fusion dictionary. The contents of this key can be either
    list of the model IDs or a list of dictionaries with one entry per
    model.

    """
    model_ids = []
    weights = []
    try:
        model_info = models_info[0]
        if isinstance(model_info, dict):
            try:
                model_ids = [model["id"] for model in models_info]
            except KeyError:
                raise ValueError("The fusion information does not contain the"
                                 " model ids.")
            try:
                weights = [model["weight"] for model in models_info]
            except KeyError:
                weights = None
        else:
            model_ids = models_info
            weights = None
        return model_ids, weights
    except KeyError:
        raise ValueError("Failed to find the models in the fusion info.")


class Fusion(ModelFields):
    """A local predictive Fusion.

       Uses a number of BigML remote models to build local version of a fusion
       that can be used to generate predictions locally.
       The expected arguments are:

       fusion: fusion object or id
       api: connection object. If None, a new connection object is
            instantiated.
       max_models: integer that limits the number of models instantiated and
                   held in memory at the same time while predicting. If None,
                   no limit is set and all the fusion models are
                   instantiated and held in memory permanently.
       cache_get: user-provided function that should return the JSON
                  information describing the model or the corresponding
                  Model object. Can be used to read these objects from a
                  cache storage.
    """

    def __init__(self, fusion, api=None, max_models=None):

        self.resource_id = None
        self.models_ids = None
        self.objective_id = None
        self.distribution = None
        self.models_splits = []
        self.cache_get = None
        self.regression = False
        self.fields = None
        self.class_names = None
        self.importance = {}
        self.api = get_api_connection(api)

        self.resource_id, fusion = get_resource_dict( \
            fusion, "fusion", api=self.api)

        if 'object' in fusion:
            fusion = fusion.get('object', {})
        self.model_ids, self.weights = get_models_weight( \
            fusion['models'])
        model_types = [get_resource_type(model) for model in self.model_ids]

        for model_type in model_types:
            if model_type not in LOCAL_SUPERVISED:
                raise ValueError("The resource %s has not an allowed"
                                 " supervised model type." % model_type)
        self.importance = fusion.get('importance', [])
        self.missing_numerics = fusion.get('missing_numerics', True)
        if fusion.get('fusion'):
            self.fields = fusion.get( \
                'fusion', {}).get("fields")
            self.objective_id = fusion.get("objective_field")
        self.input_fields = fusion.get("input_fields")

        number_of_models = len(self.model_ids)

        # Downloading the model information to cache it
        if self.api.storage is not None:
            for model_id in self.model_ids:
                if get_resource_type(model_id) == "fusion":
                    Fusion(model_id, api=self.api)
                else:
                    SupervisedModel(model_id, api=self.api)

        if max_models is None:
            self.models_splits = [self.model_ids]
        else:
            self.models_splits = [self.model_ids[index:(index + max_models)]
                                  for index
                                  in range(0, number_of_models, max_models)]

        if self.fields:
            summary = self.fields[self.objective_id]['summary']
            if 'bins' in summary:
                distribution = summary['bins']
            elif 'counts' in summary:
                distribution = summary['counts']
            elif 'categories' in summary:
                distribution = summary['categories']
            else:
                distribution = []
            self.distribution = distribution

        self.regression = \
            self.fields[self.objective_id].get('optype') == 'numeric'

        if not self.regression:
            objective_field = self.fields[self.objective_id]
            categories = objective_field['summary']['categories']
            classes = [category[0] for category in categories]
            self.class_names = sorted(classes)
            self.objective_categories = [category for \
                category, _ in self.fields[self.objective_id][ \
               "summary"]["categories"]]

        ModelFields.__init__( \
            self, self.fields,
            objective_id=self.objective_id)

    def get_fusion_resource(self, fusion):
        """Extracts the fusion resource info. The fusion argument can be
           - a path to a local file
           - an fusion id
        """
        # the string can be a path to a JSON file
        if isinstance(fusion, str):
            try:
                path = os.path.dirname(os.path.abspath(fusion))
                with open(fusion) as fusion_file:
                    fusion = json.load(fusion_file)
                    self.resource_id = get_fusion_id(fusion)
                    if self.resource_id is None:
                        raise ValueError("The JSON file does not seem"
                                         " to contain a valid BigML fusion"
                                         " representation.")
                    else:
                        self.api = BigML(storage=path)
            except IOError:
                # if it is not a path, it can be an fusion id
                self.resource_id = get_fusion_id(fusion)
                if self.resource_id is None:
                    if fusion.find('fusion/') > -1:
                        raise Exception(
                            self.api.error_message(fusion,
                                                   resource_type='fusion',
                                                   method='get'))
                    else:
                        raise IOError("Failed to open the expected JSON file"
                                      " at %s" % fusion)
            except ValueError:
                raise ValueError("Failed to interpret %s."
                                 " JSON file expected.")
        if not isinstance(fusion, dict):
            fusion = retrieve_resource(self.api, self.resource_id,
                                       no_check_fields=False)
        return fusion

    def list_models(self):
        """Lists all the model/ids that compound the fusion.

        """
        return self.model_ids

    def predict_probability(self, input_data,
                            missing_strategy=LAST_PREDICTION,
                            compact=False):

        """For classification models, Predicts a probability for
        each possible output class, based on input values.  The input
        fields must be a dictionary keyed by field name or field ID.

        For regressions, the output is a single element list
        containing the prediction.

        :param input_data: Input data to be predicted
        :param missing_strategy: LAST_PREDICTION|PROPORTIONAL missing strategy
                                 for missing fields
        :param compact: If False, prediction is returned as a list of maps, one
                        per class, with the keys "prediction" and "probability"
                        mapped to the name of the class and it's probability,
                        respectively.  If True, returns a list of probabilities
                        ordered by the sorted order of the class names.
        """
        votes = MultiVoteList([])
        if not self.missing_numerics:
            check_no_missing_numerics(input_data, self.model_fields)

        for models_split in self.models_splits:
            models = []
            for model in models_split:
                model_type = get_resource_type(model)
                if model_type == "fusion":
                    models.append(Fusion(model, api=self.api))
                else:
                    models.append(SupervisedModel(model, api=self.api))
            votes_split = []
            for model in models:
                try:
                    kwargs = {"compact": True}
                    if model_type in ["model", "ensemble", "fusion"]:
                        kwargs.update({"missing_strategy": missing_strategy})
                    prediction = model.predict_probability( \
                        input_data, **kwargs)
                except ValueError:
                    # logistic regressions can raise this error if they
                    # have missing_numerics=False and some numeric missings
                    # are found
                    continue
                if self.regression:
                    prediction = prediction[0]
                    if self.weights is not None:
                        prediction = self.weigh(prediction, model.resource_id)
                else:
                    if self.weights is not None:
                        prediction = self.weigh( \
                            prediction, model.resource_id)
                    # we need to check that all classes in the fusion
                    # are also in the composing model
                    if not self.regression and \
                            self.class_names != model.class_names:
                        try:
                            prediction = rearrange_prediction( \
                                model.class_names,
                                self.class_names,
                                prediction)
                        except AttributeError:
                            # class_names should be defined, but just in case
                            pass
                votes_split.append(prediction)
            votes.extend(votes_split)
        if self.regression:
            total_weight = len(votes.predictions) if self.weights is None \
                else sum(self.weights)
            prediction = sum([prediction for prediction in \
                votes.predictions]) / float(total_weight)
            if compact:
                output = [prediction]
            else:
                output = {"prediction": prediction}

        else:
            output = votes.combine_to_distribution(normalize=True)
            if not compact:
                output = [{'category': class_name,
                           'probability': probability}
                          for class_name, probability in
                          zip(self.class_names, output)]

        return output

    def weigh(self, prediction, model_id):
        """Weighs the prediction according to the weight associated to the
        current model in the fusion.

        """
        if isinstance(prediction, list):
            for index, probability in enumerate(prediction):
                probability *= self.weights[ \
                        self.model_ids.index(model_id)]
                prediction[index] = probability
        else:
            prediction *= self.weights[self.model_ids.index(model_id)]

        return prediction

    def predict(self, input_data, missing_strategy=LAST_PREDICTION,
                operating_point=None, full=False):
        """Makes a prediction based on a number of field values.

        input_data: Input data to be predicted
        missing_strategy: LAST_PREDICTION|PROPORTIONAL missing strategy for
                          missing fields
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
        full: Boolean that controls whether to include the prediction's
              attributes. By default, only the prediction is produced. If set
              to True, the rest of available information is added in a
              dictionary format. The dictionary keys can be:
                  - prediction: the prediction value
                  - probability: prediction's probability
                  - unused_fields: list of fields in the input data that
                                   are not being used in the model
        """

        # Checks and cleans input_data leaving the fields used in the model
        unused_fields = []
        new_data = self.filter_input_data( \
            input_data,
            add_unused_fields=full)
        if full:
            input_data, unused_fields = new_data
        else:
            input_data = new_data

        if not self.missing_numerics:
            check_no_missing_numerics(input_data, self.model_fields)

        # Strips affixes for numeric values and casts to the final field type
        cast(input_data, self.fields)

        full_prediction = self._predict( \
            input_data, missing_strategy=missing_strategy,
            operating_point=operating_point,
            unused_fields=unused_fields)
        if full:
            return dict((key, value) for key, value in \
                full_prediction.items() if value is not None)

        return full_prediction['prediction']

    def _predict(self, input_data, missing_strategy=LAST_PREDICTION,
                 operating_point=None, unused_fields=None):
        """Makes a prediction based on a number of field values. Please,
        note that this function does not check the types for the input
        provided, so it's unsafe to use it directly without prior checking.

        """
        # When operating_point is used, we need the probabilities
        # of all possible classes to decide, so se use
        # the `predict_probability` method
        if operating_point:
            if self.regression:
                raise ValueError("The operating_point argument can only be"
                                 " used in classifications.")
            prediction = self.predict_operating( \
                input_data,
                missing_strategy=missing_strategy,
                operating_point=operating_point)
            return prediction

        result = self.predict_probability( \
            input_data,
            missing_strategy=missing_strategy,
            compact=False)

        if not self.regression:
            result = sorted(result, key=lambda x: - x["probability"])[0]
            result["prediction"] = result["category"]
            del result["category"]

        # adding unused fields, if any
        if unused_fields:
            result.update({'unused_fields': unused_fields})

        return result

    def predict_operating(self, input_data,
                          missing_strategy=LAST_PREDICTION,
                          operating_point=None):
        """Computes the prediction based on a user-given operating point.

        """
        # only probability is allowed as operating kind
        operating_point.update({"kind": "probability"})
        kind, threshold, positive_class = parse_operating_point( \
            operating_point, OPERATING_POINT_KINDS, self.class_names)
        predictions = self.predict_probability(input_data,
                                               missing_strategy, False)

        position = self.class_names.index(positive_class)
        if predictions[position][kind] > threshold:
            prediction = predictions[position]
        else:
            # if the threshold is not met, the alternative class with
            # highest probability or confidence is returned
            predictions.sort( \
                key=cmp_to_key( \
                lambda a, b: self._sort_predictions(a, b, kind)))
            prediction = predictions[0: 2]
            if prediction[0]["category"] == positive_class:
                prediction = prediction[1]
            else:
                prediction = prediction[0]
        prediction["prediction"] = prediction["category"]
        del prediction["category"]
        return prediction

    def _sort_predictions(self, a, b, criteria):
        """Sorts the categories in the predicted node according to the
        given criteria

        """
        if a[criteria] == b[criteria]:
            return sort_categories(a, b, self.objective_categories)
        return 1 if b[criteria] > a[criteria] else -1
