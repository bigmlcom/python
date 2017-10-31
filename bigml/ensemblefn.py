# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2012-2017 BigML
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

"""An local Ensemble object.

This module defines an Ensemble to make predictions locally using its
associated models.

This module can not only save you a few credits, but also enormously
reduce the latency for each prediction and let you use your models
offline.

from bigml.api import BigML
from bigml.ensemble import Ensemble

# api connection
api = BigML(storage='./storage')

# creating ensemble
ensemble = api.create_ensemble('dataset/5143a51a37203f2cf7000972')

# Ensemble object to predict
ensemble = Ensemble(ensemble, api)
ensemble.predict({"petal length": 3, "petal width": 1})

"""
import sys
import logging
import gc
import json
import os

from bigml.api import BigML, get_ensemble_id, get_model_id
from bigml.model import Model, retrieve_resource, print_distribution, \
    parse_operating_point
from bigml.model import STORAGE, ONLY_MODEL, LAST_PREDICTION, EXCLUDE_FIELDS
from bigml.multivote import MultiVote
from bigml.multivote import PLURALITY_CODE, PROBABILITY_CODE, CONFIDENCE_CODE
from bigml.multimodel import MultiModel
from bigml.basemodel import BaseModel, print_importance
from bigml.util import slugify

BOOSTING = 1
LOGGER = logging.getLogger('BigML')
OPERATING_POINT_KINDS = ["probability", "confidence", "voting"]


def use_cache(cache_get):
    """Checks whether the user has provided a cache get function to retrieve
       local models.

    """
    return cache_get is not None and hasattr(cache_get, '__call__')


def boosted_list_error(boosting):
    """The local ensemble cannot be built from a list of boosted models

    """
    if boosting:
        raise ValueError("Failed to build the local ensemble. Boosted"
                         " ensembles cannot be built from a list"
                         " of boosting models.")

class Ensemble_fn(object):
    """A local predictive Ensemble.

       Uses a number of BigML remote models to build an ensemble local version
       that can be used to generate predictions locally.
       The expected arguments are:

       ensemble: ensemble object or id, list of model objects or
                 ids or list of local model objects (see Model)
       api: connection object. If None, a new connection object is
            instantiated.
       max_models: integer that limits the number of models instantiated and
                   held in memory at the same time while predicting. If None,
                   no limit is set and all the ensemble models are
                   instantiated and held in memory permanently.
    """

    def __init__(self, ensemble, api=None, max_models=None, cache_get=None,
                 model_dir=None):

        if api is None:
            self.api = BigML(storage=STORAGE)
        else:
            self.api = api
        self.resource_id = None
        # to be deprecated
        self.ensemble_id = None
        self.objective_id = None
        self.distributions = None
        self.distribution = None
        self.models_splits = []
        self.multi_model = None
        self.boosting = None
        self.boosting_offsets = None
        self.cache_get = None
        self.regression = False
        self.fields = None
        self.class_names = None
        self.importance = []
        self.predict_functions = []
        query_string = ONLY_MODEL
        no_check_fields = False

        ensemble = self.get_ensemble_resource(ensemble)
        self.resource_id = get_ensemble_id(ensemble)
        self.ensemble_id = self.resource_id
        # avoid checking fields because of old ensembles
        ensemble = retrieve_resource(self.api, self.resource_id,
                                     no_check_fields=True)
        if ensemble['object'].get('type') == BOOSTING:
            self.boosting = ensemble['object'].get('boosting')
        models = ensemble['object']['models']
        self.distributions = ensemble['object'].get('distributions', [])
        self.importance = ensemble['object'].get('importance', [])
        self.model_ids = models
        # new ensembles have the fields structure
        if ensemble['object'].get('ensemble'):
            self.fields = ensemble['object'].get( \
                'ensemble', {}).get("fields")
            self.objective_id = ensemble['object'].get("objective_field")
            self.input_fields = ensemble['object'].get("input_fields")
            query_string = EXCLUDE_FIELDS
            no_check_fields = True

        if model_dir:
            self.get_model_fns(model_dir)

        number_of_models = len(models)

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
        if self.boosting:
            self.boosting_offsets = ensemble['object'].get('initial_offset',
                                                           0) \
                if self.regression else dict(ensemble['object'].get( \
                    'initial_offsets', []))

        if not self.regression and self.boosting is None:
            try:
                objective_field = self.fields[self.objective_id]
                categories = objective_field['summary']['categories']
                classes = [category[0] for category in categories]
            except (AttributeError, KeyError):
                classes = set()
                for distribution in self.distributions:
                    for category in distribution['training']['categories']:
                        classes.add(category[0])

            self.class_names = sorted(classes)


    def get_model_fns(self, model_dir):
        function_name = "predict_%s" % \
            slugify(self.fields[self.objective_id]["name"])
        for model_id in self.model_ids:
            module_name = "%s.%s" % (self.ensemble_id.replace("/", "_"),
                                     model_id.replace("/", "_"))
            __import__(module_name)
            prediction_module = sys.modules[module_name]
            function = getattr(prediction_module, function_name)
            self.predict_functions.append(function)


    def get_ensemble_resource(self, ensemble):
        """Extracts the ensemble resource info. The ensemble argument can be
           - a path to a local file
           - an ensemble id
        """
        # the string can be a path to a JSON file
        if isinstance(ensemble, basestring):
            try:
                with open(ensemble) as ensemble_file:
                    ensemble = json.load(ensemble_file)
                    self.resource_id = get_ensemble_id(ensemble)
                    if self.resource_id is None:
                        raise ValueError("The JSON file does not seem"
                                         " to contain a valid BigML ensemble"
                                         " representation.")
            except IOError:
                # if it is not a path, it can be an ensemble id
                self.resource_id = get_ensemble_id(ensemble)
                if self.resource_id is None:
                    if ensemble.find('ensemble/') > -1:
                        raise Exception(
                            self.api.error_message(ensemble,
                                                   resource_type='ensemble',
                                                   method='get'))
                    else:
                        raise IOError("Failed to open the expected JSON file"
                                      " at %s" % ensemble)
            except ValueError:
                raise ValueError("Failed to interpret %s."
                                 " JSON file expected.")
        return ensemble

    def list_models(self):
        """Lists all the model/ids that compound the ensemble.

        """
        return self.model_ids

    def predict_probability(self, input_data, by_name=True,
                            missing_strategy=LAST_PREDICTION,
                            compact=False):

        """For classification models, Predicts a probability for
        each possible output class, based on input values.  The input
        fields must be a dictionary keyed by field name or field ID.

        For regressions, the output is a single element list
        containing the prediction.

        :param input_data: Input data to be predicted
        :param by_name: Boolean that is set to True if field_names (as
                        alternative to field ids) are used in the
                        input_data dict
        :param missing_strategy: LAST_PREDICTION|PROPORTIONAL missing strategy
                                 for missing fields
        :param compact: If False, prediction is returned as a list of maps, one
                        per class, with the keys "prediction" and "probability"
                        mapped to the name of the class and it's probability,
                        respectively.  If True, returns a list of probabilities
                        ordered by the sorted order of the class names.
        """
        if self.regression:
            prediction = self.predict(input_data,
                                      by_name=by_name,
                                      missing_strategy=missing_strategy)

            if compact:
                output = [prediction]
            else:
                output = {'prediction': prediction}
        elif self.boosting is not None:
            probabilities = self.predict(input_data,
                                         by_name=by_name,
                                         missing_strategy=missing_strategy,
                                         add_probability=True)['probabilities']

            probabilities.sort(key=lambda x: x['prediction'])

            if compact:
                output = [probability['probability']
                          for probability in probabilities]
            else:
                output = probabilities
        else:
            output = self._combine_distributions( \
                input_data,
                by_name,
                missing_strategy)

            if not compact:
                names_probabilities = zip(self.class_names, output)
                output = [{'category': class_name,
                           'probability': probability}
                          for class_name, probability in names_probabilities]

        return output

    def predict_confidence(self, input_data, by_name=True,
                           missing_strategy=LAST_PREDICTION,
                           compact=False):

        """For classification models, Predicts a confidence for
        each possible output class, based on input values.  The input
        fields must be a dictionary keyed by field name or field ID.

        For regressions, the output is a single element list
        containing the prediction.

        :param input_data: Input data to be predicted
        :param by_name: Boolean that is set to True if field_names (as
                        alternative to field ids) are used in the
                        input_data dict
        :param missing_strategy: LAST_PREDICTION|PROPORTIONAL missing strategy
                                 for missing fields
        :param compact: If False, prediction is returned as a list of maps, one
                        per class, with the keys "prediction" and "probability"
                        mapped to the name of the class and it's probability,
                        respectively.  If True, returns a list of probabilities
                        ordered by the sorted order of the class names.
        """
        if self.regression or self.boosting:
            # we use boosting probabilities as confidences also
            return self.predict_probability(input_data, by_name=by_name,
                                            missing_strategy=missing_strategy,
                                            compact=compact)
        else:
            output= self._combine_distributions( \
                input_data,
                by_name,
                missing_strategy,
                method=CONFIDENCE_CODE)
            if not compact:
                names_confidences = zip(self.class_names, output)
                output = [{'category': class_name,
                           'confidence': confidence}
                          for class_name, confidence in names_confidences]

        return output

    def predict_voting(self, input_data, by_name=True,
                       missing_strategy=LAST_PREDICTION,
                       compact=False):

        """For classification models, Predicts the votes for
        each possible output class, based on input values.  The input
        fields must be a dictionary keyed by field name or field ID.

        For regressions, the output is a single element list
        containing the prediction.

        :param input_data: Input data to be predicted
        :param by_name: Boolean that is set to True if field_names (as
                        alternative to field ids) are used in the
                        input_data dict
        :param missing_strategy: LAST_PREDICTION|PROPORTIONAL missing strategy
                                 for missing fields
        :param compact: If False, prediction is returned as a list of maps, one
                        per class, with the keys "prediction" and "probability"
                        mapped to the name of the class and it's probability,
                        respectively.  If True, returns a list of probabilities
                        ordered by the sorted order of the class names.
        """
        if self.regression:
            prediction = self.predict(input_data,
                                      by_name=by_name,
                                      method=method,
                                      missing_strategy=missing_strategy)

            if compact:
                output = [prediction]
            else:
                output = {'prediction': prediction}
        elif self.boosting is not None:
            raise ValueError("Voting cannot be computed for boosted"
                             " ensembles.")
        else:
            output = self._combine_distributions( \
                input_data,
                by_name,
                missing_strategy,
                method=PLURALITY_CODE)
            if not compact:
                names_votes = zip(self.class_names, output)
                output = [{'category': class_name,
                           'k': k}
                          for class_name, k in names_votes]

        return output

    def _combine_distributions(self, input_data, by_name, missing_strategy,
                               method=PROBABILITY_CODE):
        """Computes the predicted distributions and combines them to give the
        final predicted distribution. Depending on the method parameter
        probability, votes or the confidence are used to weight the models.

        """

        if len(self.models_splits) > 1:
            # If there's more than one chunk of models, they must be
            # sequentially used to generate the votes for the prediction
            votes = MultiVoteList([])

            for models_split in self.models_splits:
                models = self._get_models(models_split)
                multi_model = MultiModel(models,
                                         api=self.api,
                                         fields=self.fields,
                                         class_names=self.class_names)

                votes_split = multi_model.generate_votes_distribution( \
                    input_data, by_name=by_name,
                    missing_strategy=missing_strategy,
                    method=method)

                votes.extend(votes_split)
        else:
            # When only one group of models is found you use the
            # corresponding multimodel to predict
            votes = self.multi_model.generate_votes_distribution( \
                input_data, by_name=by_name,
                missing_strategy=missing_strategy, method=method)

        return votes.combine_to_distribution()

    def _get_models(self, models_split):
        if not isinstance(models_split[0], Model):
            if self.cache_get is not None and \
                    hasattr(self.cache_get, '__call__'):
                # retrieve the models from a cache get function
                try:
                    models = [self.cache_get(model_id) for model_id
                              in models_split]
                except Exception, exc:
                    raise Exception('Error while calling the '
                                    'user-given'
                                    ' function %s: %s' %
                                    (self.cache_get.__name__,
                                     str(exc)))
            else:
                models = [retrieve_resource(self.api, model_id,
                                            query_string=ONLY_MODEL)
                          for model_id in models_split]

        return models

    def predict_operating(self, input_data, by_name=True,
                          missing_strategy=LAST_PREDICTION,
                          operating_point=None, compact=False):
        """Computes the prediction based on a user-given operating point.

        """
        kind, threshold, positive_class = parse_operating_point( \
            operating_point, OPERATING_POINT_KINDS, self.class_names)

        try:
            predict_method = None
            predict_method = getattr(self, "predict_%s" % kind)

            predictions = predict_method(input_data, by_name,
                                         missing_strategy, compact)
            position = self.class_names.index(positive_class)
        except KeyError:
            raise ValueError("The operating point needs to contain a valid"
                             " positive class, kind and a threshold.")
        attribute = kind
        if kind == "voting":
            attribute = "k"
        if predictions[position][attribute] < threshold:
            # if the threshold is not met, the alternative class with
            # highest probability or confidence is returned
            prediction = sorted(predictions,
                                key=lambda x: - x[attribute])[0 : 2]
            if prediction[0]["category"] == positive_class:
                prediction = prediction[1]
            else:
                prediction = prediction[0]
        else:
            prediction = predictions[position]
        prediction["prediction"] = prediction["category"]
        del prediction["category"]
        return prediction

    def predict(self, input_data, by_name=True, method=PLURALITY_CODE):
        """Makes a prediction based on the prediction made by every model.

        :param input_data: Test data to be used as input
        :param by_name: Boolean that is set to True if field_names (as
                        alternative to field ids) are used in the
                        input_data dict
        :param method: numeric key code for the following combination
                       methods in classifications/regressions:
              0 - majority vote (plurality)/ average: PLURALITY_CODE
              1 - confidence weighted majority vote / error weighted:
                  CONFIDENCE_CODE
              2 - probability weighted majority vote / average:
                  PROBABILITY_CODE
              3 - threshold filtered vote / doesn't apply:
                  THRESHOLD_CODE
        """


        # When only one group of models is found you use the
        # corresponding multimodel to predict
        input_data_array = self.format_input_data(input_data)
        votes_split = []
        for fn in self.predict_functions:
            votes_split.append(fn(*input_data_array))

        votes = MultiVote(votes_split,
                          boosting_offsets=self.boosting_offsets)
        if self.boosting is not None and not self.regression:
            categories = [ \
                d[0] for d in
                self.fields[self.objective_id]["summary"]["categories"]]
            options = {"categories": categories}

        result = votes.combine(method=method)

        return result

    def field_importance_data(self):
        """Computes field importance based on the field importance information
           of the individual models in the ensemble.

        """
        field_importance = {}
        field_names = {}
        if self.importance:
            field_importance = self.importance
            field_names = {field_id: {'name': self.fields[field_id]["name"]} \
                           for field_id in field_importance.keys()}
            return [list(importance) for importance in \
                sorted(field_importance.items(), key=lambda x: x[1],
                       reverse=True)], field_names

        if (self.distributions is not None and
                isinstance(self.distributions, list) and
                all('importance' in item for item in self.distributions)):
            # Extracts importance from ensemble information
            importances = [model_info['importance'] for model_info in
                           self.distributions]
            for index in range(0, len(importances)):
                model_info = importances[index]
                for field_info in model_info:
                    field_id = field_info[0]
                    if field_id not in field_importance:
                        field_importance[field_id] = 0.0
                        name = self.fields[field_id]['name']
                        field_names[field_id] = {'name': name}
                    field_importance[field_id] += field_info[1]
        else:
            # Old ensembles, extracts importance from model information
            for model_id in self.model_ids:
                local_model = BaseModel(model_id, api=self.api)
                for field_info in local_model.field_importance:
                    field_id = field_info[0]
                    if field_info[0] not in field_importance:
                        field_importance[field_id] = 0.0
                        name = self.fields[field_id]['name']
                        field_names[field_id] = {'name': name}
                    field_importance[field_id] += field_info[1]

        number_of_models = len(self.model_ids)
        for field_id in field_importance:
            field_importance[field_id] /= number_of_models
        return [list(importance) for importance in \
            sorted(field_importance.items(), key=lambda x: x[1],
                   reverse=True)], field_names

    def print_importance(self, out=sys.stdout):
        """Prints ensemble field importance

        """
        print_importance(self, out=out)

    def get_data_distribution(self, distribution_type="training"):
        """Returns the required data distribution by adding the distributions
           in the models

        """
        ensemble_distribution = []
        categories = []
        distribution = []
        # ensembles have now the field information
        if self.distribution and self.boosting:
            return sorted(self.distribution, key=lambda x: x[0])

        for model_distribution in self.distributions:
            summary = model_distribution[distribution_type]
            if 'bins' in summary:
                distribution = summary['bins']
            elif 'counts' in summary:
                distribution = summary['counts']
            elif 'categories' in summary:
                distribution = summary['categories']
            else:
                distribution = []
            for point, instances in distribution:
                if point in categories:
                    ensemble_distribution[
                        categories.index(point)][1] += instances
                else:
                    categories.append(point)
                    ensemble_distribution.append([point, instances])

        return sorted(ensemble_distribution, key=lambda x: x[0])

    def summarize(self, out=sys.stdout):
        """Prints ensemble summary. Only field importance at present.

        """
        distribution = self.get_data_distribution("training")

        if distribution:
            out.write(u"Data distribution:\n")
            print_distribution(distribution, out=out)
            out.write(u"\n\n")

        if not self.boosting:
            predictions = self.get_data_distribution("predictions")

            if predictions:
                out.write(u"Predicted distribution:\n")
                print_distribution(predictions, out=out)
                out.write(u"\n\n")

        out.write(u"Field importance:\n")
        self.print_importance(out=out)
        out.flush()

    def all_model_fields(self, max_models=None):
        """Retrieves the fields used as predictors in all the ensemble
           models

        """

        fields = {}
        models = []
        objective_id = None
        no_objective_id = False
        if isinstance(self.models_splits[0][0], Model):
            for split in self.models_splits:
                models.extend(split)
        else:
            models = self.model_ids
        for index, model_id in enumerate(models):
            if isinstance(model_id, Model):
                local_model = model_id
            elif self.cache_get is not None:
                local_model = self.cache_get(model_id)
            else:
                local_model = Model(model_id, self.api)
            if (max_models is not None and index > 0 and
                    index % max_models == 0):
                gc.collect()
            fields.update(local_model.fields)
            if (objective_id is not None and
                    objective_id != local_model.objective_id):
                # the models' objective field have different ids, no global id
                no_objective_id = True
            else:
                objective_id = local_model.objective_id
        if no_objective_id:
            objective_id = None
        gc.collect()
        return fields, objective_id

    def format_input_data(self, input_data):
        input_data_array = []
        for field_id in self.input_fields:
            value = input_data.get(field_id)
            input_data_array.append(value)

        return input_data_array
