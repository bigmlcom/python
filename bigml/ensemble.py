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

"""An Ensemble local object.

This module defines a Ensemble to make predictions locally using its
associated models.

This module cannot only save you a few credits, but also enormously
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
import logging
LOGGER = logging.getLogger('BigML')

from bigml.api import BigML
from bigml.util import retrieve_model
from bigml.multivote import MultiVote
from bigml.multivote import PLURALITY_CODE
from bigml.multimodel import MultiModel

STORAGE = './storage'

class Ensemble(object):
    """An ensemble local model.

       Uses a number of BigML remote models to build a local version
       that can be used to generate predictions locally.

    """

    def __init__(self, ensemble, api=None, max_models=None):

        if api is None:
            self.api = BigML(storage=STORAGE)
        else:
            self.api = api
        self.ensemble_id = api.get_resource_id(ensemble)
        ensemble = api.check_resource(ensemble, api.get_ensemble)
        models = ensemble['object']['models']
        self.model_ids = models
        number_of_models = len(models)
        if max_models is None:
            self.models_splits = [models]
        else:
            self.models_splits = [models[index:(index + max_models)] for index
                                  in range(0, number_of_models, max_models)]

    def list_models(self):
        """Lists all the model/ids that compound the ensemble.

        """
        return self.model_ids

    def predict(self, input_data, by_name=True, method=PLURALITY_CODE,
                with_confidence=False):
        """Makes a prediction based on the prediction made by every model.

           The method parameter is a numeric key to the following combination
           methods in classifications/regressions:
              0 - majority vote (plurality)/ average: PLURALITY_CODE
              1 - confidence weighted majority vote / error weighted:
                  CONFIDENCE_CODE
              2 - probability weighted majority vote / average:
                  PROBABILITY_CODE
        """
        votes = MultiVote([])
        for models_split in self.models_splits:
            models = [retrieve_model(self.api, model_id)
                      for model_id in models_split]
            multi_model = MultiModel(models)
            votes_split = multi_model.generate_votes(input_data,
                                                     by_name=by_name)
            votes.extend(votes_split.predictions)
        return votes.combine(method=method, with_confidence=with_confidence)
