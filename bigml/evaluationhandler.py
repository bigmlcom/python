# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2014-2017 BigML
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

"""Base class for evaluations' REST calls

   https://bigml.com/developers/evaluations

"""

try:
    import simplejson as json
except ImportError:
    import json


from bigml.resourcehandler import ResourceHandler
from bigml.resourcehandler import (check_resource_type,
                                   get_evaluation_id)
from bigml.constants import (EVALUATION_PATH, MODEL_PATH, ENSEMBLE_PATH,
                             LOGISTIC_REGRESSION_PATH)


class EvaluationHandler(ResourceHandler):
    """This class is used by the BigML class as
       a mixin that provides the REST calls models. It should not
       be instantiated independently.

    """
    def __init__(self):
        """Initializes the EvaluationHandler. This class is intended to be
           used as a mixin on ResourceHandler, that inherits its
           attributes and basic method from BigMLConnection, and must not be
           instantiated independently.

        """
        self.evaluation_url = self.url + EVALUATION_PATH

    def create_evaluation(self, model, dataset,
                          args=None, wait_time=3, retries=10):
        """Creates a new evaluation.

        """
        create_args = {}
        if args is not None:
            create_args.update(args)

        model_types = [ENSEMBLE_PATH, MODEL_PATH, LOGISTIC_REGRESSION_PATH]
        origin_resources_checked = self.check_origins(
            dataset, model, create_args, model_types=model_types,
            wait_time=wait_time, retries=retries)

        if origin_resources_checked:
            body = json.dumps(create_args)
            return self._create(self.evaluation_url, body)

    def get_evaluation(self, evaluation, query_string=''):
        """Retrieves an evaluation.

           The evaluation parameter should be a string containing the
           evaluation id or the dict returned by create_evaluation.
           As evaluation is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, the function will
           return a dict that encloses the evaluation values and state info
           available at the time it is called.
        """
        check_resource_type(evaluation, EVALUATION_PATH,
                            message="An evaluation id is needed.")
        evaluation_id = get_evaluation_id(evaluation)
        if evaluation_id:
            return self._get("%s%s" % (self.url, evaluation_id),
                             query_string=query_string)

    def list_evaluations(self, query_string=''):
        """Lists all your evaluations.

        """
        return self._list(self.evaluation_url, query_string)

    def update_evaluation(self, evaluation, changes):
        """Updates an evaluation.

        """
        check_resource_type(evaluation, EVALUATION_PATH,
                            message="An evaluation id is needed.")
        evaluation_id = get_evaluation_id(evaluation)
        if evaluation_id:
            body = json.dumps(changes)
            return self._update("%s%s" % (self.url, evaluation_id), body)

    def delete_evaluation(self, evaluation):
        """Deletes an evaluation.

        """
        check_resource_type(evaluation, EVALUATION_PATH,
                            message="An evaluation id is needed.")
        evaluation_id = get_evaluation_id(evaluation)
        if evaluation_id:
            return self._delete("%s%s" % (self.url, evaluation_id))
