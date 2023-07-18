# -*- coding: utf-8 -*-
#
# Copyright 2023 BigML
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

"""An local Evaluation object.

This module defines a local class to handle the results of an evaluation

"""
import json


from bigml.api import get_api_connection, ID_GETTERS
from bigml.basemodel import retrieve_resource, get_resource_dict

CLASSIFICATION_METRICS = [
    "accuracy", "precision", "recall", "phi" "phi_coefficient",
    "f_measure", "confusion_matrix", "per_class_statistics"]

REGRESSION_METRICS = ["mean_absolute_error", "mean_squared_error", "r_squared"]


class ClassificationEval():
    """A class to store the classification metrics """
    def __init__(self, name, per_class_statistics):
        self.name = name
        for statistics in per_class_statistics:
            if statistics["class_name"] == name:
                break
        for metric in CLASSIFICATION_METRICS:
            if metric in statistics.keys():
                setattr(self, metric, statistics.get(metric))


class Evaluation():
    """A class to deal with the information in an evaluation result

    """
    def __init__(self, evaluation, api=None):

        self.resource_id = None
        self.model_id = None
        self.test_dataset_id = None
        self.regression = None
        self.full = None
        self.random = None
        self.error = None
        self.error_message = None
        self.api = get_api_connection(api)

        try:
            self.resource_id, evaluation = get_resource_dict( \
                evaluation, "evaluation", self.api)
        except ValueError as resource:
            try:
                evaluation = json.loads(str(resource))
                self.resource_id = evaluation["resource"]
            except ValueError:
                raise ValueError("The evaluation resource was faulty: \n%s" % \
                    resource)

        if 'object' in evaluation and isinstance(evaluation['object'], dict):
            evaluation = evaluation['object']
        self.status = evaluation["status"]
        self.error = self.status.get("error")
        if self.error is not None:
            self.error_message = self.status.get("message")
        else:
            self.model_id = evaluation["model"]
            self.test_dataset_id = evaluation["dataset"]

            if 'result' in evaluation and \
                    isinstance(evaluation['result'], dict):
                self.full = evaluation.get("result", {}).get("model")
                self.random = evaluation.get("result", {}).get("random")
                self.regression =  not self.full.get("confusion_matrix")
                if self.regression:
                    self.add_metrics(self.full, REGRESSION_METRICS)
                    self.mean = evaluation.get("result", {}).get("mean")
                else:
                    self.add_metrics(self.full, CLASSIFICATION_METRICS)
                    self.mode = evaluation.get("result", {}).get("mode")
                    self.classes = evaluation.get("result", {}).get(
                        "class_names")
            else:
                raise ValueError("Failed to find the correct evaluation"
                                 " structure.")
        if not self.regression:
            self.positive_class = ClassificationEval(self.classes[-1],
                                                     self.per_class_statistics)

    def add_metrics(self, metrics_info, metrics_list, obj=None):
        """Adding the metrics in the `metrics_info` dictionary as attributes
        in the object passed as argument. If None is given, the metrics will
        be added to the self object.
        """
        if obj is None:
            obj = self

        for metric in metrics_list:
            setattr(obj, metric, metrics_info.get(metric,
                metrics_info.get("average_%s" % metric)))

    def set_positive_class(self, positive_class):
        """Changing the positive class """
        if positive_class is None or positive_class not in self.classes:
            raise ValueError("The possible classes are: %s" %
                ", ".join(self.classes))
        self.positive_class = ClassificationEval(positive_class,
                                                 self.per_class_statistics)
