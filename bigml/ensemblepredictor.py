# -*- coding: utf-8 -*-
#
# Copyright 2017-2022 BigML
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

"""A local Ensemble object focused on quick predictions.

This module defines an EnsemblePredictor to make predictions locally using its
associated models. To use this ensemble, you need a local directory containing
the files that store the prediction functions generated for every model in
the ensemble. Please, check `bigmler export` to see how to do that.


# Ensemble object to predict
ensemble = EnsemblePredictor(ensemble_id)
ensemble.predict({"petal length": 3, "petal width": 1})

"""
import sys
import os
import logging
import json

from bigml.api import get_ensemble_id, get_api_connection
from bigml.generators.model import print_distribution
from bigml.constants import STORAGE
from bigml.multivote import MultiVote
from bigml.multivote import PLURALITY_CODE
from bigml.basemodel import BaseModel, print_importance, retrieve_resource, \
    check_local_info
from bigml.model import Model
from bigml.flattree import FlatTree
from bigml.util import NUMERIC
from bigml.tree_utils import add_distribution


BOOSTING = 1
LOGGER = logging.getLogger('BigML')


class EnsemblePredictor():
    """A local predictive Ensemble.

       Uses a number of BigML models to build an ensemble local version
       that can be used to generate predictions locally.
       The expected arguments are:

       ensemble: ensemble object or id
       model_fns_dir: path to the local directory where the functions that
                      are to be used for each model's prediction are stored.
                      The files containing each model predictor function
                      can be obtained from the `bigmler export` command.
                      Check the bigmler docs in
                      http://bigmler.readthedocs.io/en/latest/#bigmler-export
       api: connection object. If None, a new connection object is
            instantiated.
    """

    def __init__(self, ensemble, model_fns_dir, api=None):

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
        self.regression = False
        self.fields = None
        self.class_names = None
        self.importance = {}
        self.predict_functions = []
        self.api = get_api_connection(api)

        ensemble = self.get_ensemble_resource(ensemble)
        self.resource_id = get_ensemble_id(ensemble)
        self.ensemble_id = self.resource_id

        if not check_local_info(ensemble):
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

        if model_fns_dir:
            self.get_model_fns(model_fns_dir)
        else:
            raise ValueError("The EnsemblePredictor object expects as"
                             " argument the directory where the models"
                             " predict functions are stored. To generate "
                             " them, please check the 'bigmler export'"
                             " command.")

        if self.fields:
            add_distribution(self)

        self.regression = \
            self.fields[self.objective_id].get('optype') == NUMERIC
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

    def get_model_fns(self, model_fns_dir):
        """Retrieves the predict functions for each model. The functions are
        named after the field that is being predicted prepended by the
        `predict_` string.

        """
        function_name = "predict"
        model_id = self.model_ids[0]
        module_path = ".".join(os.path.normpath(model_fns_dir).split(os.sep))
        if not os.path.isfile(os.path.join(model_fns_dir, "%s.py" %
                                           model_id.replace("/", "_"))):
            self.generate_models(model_fns_dir)
        for model_id in self.model_ids:
            module_name = "%s.%s" % (module_path,
                                     model_id.replace("/", "_"))
            try:
                __import__(module_name)
                prediction_module = sys.modules[module_name]
                function = getattr(prediction_module, function_name)
                self.predict_functions.append(function)
            except ImportError:
                raise ImportError("Failed to import the predict function"
                                  " from %s." % module_name)

    def get_ensemble_resource(self, ensemble):
        """Extracts the ensemble resource info. The ensemble argument can be
           - a path to a local file
           - an ensemble id
        """
        # the string can be a path to a JSON file
        if isinstance(ensemble, str):
            try:
                with open(ensemble) as ensemble_file:
                    path = os.path.dirname(ensemble)
                    ensemble = json.load(ensemble_file)
                    self.resource_id = get_ensemble_id(ensemble)
                    if self.resource_id is None:
                        raise ValueError("The JSON file does not seem"
                                         " to contain a valid BigML ensemble"
                                         " representation.")
                    self.api.storage = path
            except IOError:
                # if it is not a path, it can be an ensemble id
                self.resource_id = get_ensemble_id(ensemble)
                if self.resource_id is None:
                    if ensemble.find('ensemble/') > -1:
                        raise Exception(
                            self.api.error_message(ensemble,
                                                   resource_type='ensemble',
                                                   method='get'))
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

    def predict(self, input_data, method=PLURALITY_CODE, full=False):
        """Makes a prediction based on the prediction made by every model.

        :param input_data: Test data to be used as input
        :param method: numeric key code for the following combination
                       methods in classifications/regressions:
              0 - majority vote (plurality)/ average: PLURALITY_CODE
              1 - confidence weighted majority vote / error weighted:
                  CONFIDENCE_CODE
              2 - probability weighted majority vote / average:
                  PROBABILITY_CODE
        """


        # When only one group of models is found you use the
        # corresponding multimodel to predict
        votes_split = []
        options = None
        count = 1
        for fun in self.predict_functions:
            prediction = fun(input_data)
            prediction.update({"order": count, "count": 1})
            count += 1
            votes_split.append(prediction)
        votes = MultiVote(votes_split,
                          boosting_offsets=self.boosting_offsets)
        if self.boosting is not None and not self.regression:
            categories = [ \
                d[0] for d in
                self.fields[self.objective_id]["summary"]["categories"]]
            options = {"categories": categories}

        result = votes.combine(method=method, options=options, full=full)
        if isinstance(result, dict):
            del result['count']

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
                           for field_id in list(field_importance.keys())}
            return [list(importance) for importance in \
                sorted(list(field_importance.items()), key=lambda x: x[1],
                       reverse=True)], field_names

        if (self.distributions is not None and
                isinstance(self.distributions, list) and
                all('importance' in item for item in self.distributions)):
            # Extracts importance from ensemble information
            importances = [model_info['importance'] for model_info in
                           self.distributions]
            for model_info in importances:
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
            sorted(list(field_importance.items()), key=lambda x: x[1],
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
            out.write("Data distribution:\n")
            print_distribution(distribution, out=out)
            out.write("\n\n")

        if not self.boosting:
            predictions = self.get_data_distribution("predictions")

            if predictions:
                out.write("Predicted distribution:\n")
                print_distribution(predictions, out=out)
                out.write("\n\n")

        out.write("Field importance:\n")
        self.print_importance(out=out)
        out.flush()

    def generate_models(self, directory=STORAGE):
        """Generates the functions for the models in the ensemble

        """
        if not os.path.isfile(directory) and not os.path.exists(directory):
            os.makedirs(directory)
            open(os.path.join(directory, "__init__.py"), "w").close()
        for model_id in self.model_ids:
            local_model = Model(model_id, api=self.api,
                                fields=self.fields)
            local_flat_tree = FlatTree(local_model.tree, local_model.offsets,
                                       local_model.fields,
                                       local_model.objective_id,
                                       local_model.boosting)
            with open(os.path.join(directory, "%s.py" %
                                   model_id.replace("/", "_")), "w") \
                    as handler:
                local_flat_tree.python(out=handler,
                                       docstring="Model %s" % model_id)
