# -*- coding: utf-8 -*-
#
# Copyright 2022 BigML
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

"""
Pipeline: Class that encapsulates the information needed to add new fields
and predictions locally. The argument to create a Pipeline is the list of
datasets and batch predictions (and/or batch anomaly scores, batch centroids,
etc.) that describes the input data processing.

"""

import copy
import os
import zipfile

from datetime import datetime

from bigml.api import get_api_connection, get_resource_id, get_resource_type
from bigml.util import use_cache, load, check_dir
from bigml.constants import STORAGE
from bigml.dataset import Dataset
from bigml.basemodel import BaseModel
from bigml.supervised import SupervisedModel
from bigml.cluster import Cluster
from bigml.anomaly import Anomaly
from bigml.topicmodel import TopicModel
from bigml.association import Association
from bigml.pca import PCA


LOCAL_CLASSES = {
    "dataset": Dataset,
    "cluster": Cluster,
    "anomaly": Anomaly,
    "topicmodel": TopicModel,
    "pca": PCA,
    }


def get_datasets_chain(dataset, dataset_list=None):
    if dataset_list is None:
        dataset_list = []
    dataset_list.append(dataset)
    if dataset.origin_dataset is None:
        return dataset_list

    return get_datasets_chain(dataset.origin_dataset, dataset_list)


def get_datasets_dict(dataset, dataset_dict=None):
    if dataset_dict is None:
        dataset_dict = {}
    dataset_dict.update({dataset.resource_id: dataset})
    if dataset.origin_dataset is None:
        return dataset_dict

    return get_datasets_dict(dataset.origin_dataset, dataset_dict)


def check_in_path(path, resource_list):
    """Checks whether a list of resources is stored in a folder """
    for resource_id in resource_list:
        if not os.path.exists(os.path.join(
                path, resource_id.replace("/", "_"))):
            return False
    return True


class Pipeline:
    """The class represents the sequential transformations (and predictions)
    that the input data goes through in a prediction workflow.
    Reproduces the pre-modeling steps that need to be applied before
    the application of the model predict (centroid, anomaly score, etc.)
    method to add the final prediction. The mandatory arguments for the class
    are:
      - name: Each pipeline needs to be identified with a unique name
      - resource_ids: A list of resource IDs. Only datasets and supervised
                      or unsupervised model resources are allowed.

    When a dataset is provided, only the chain of transformations leading to
    that dataset structure is applied. When a model is provided, the input
    data is pre-modeled using that chain of transformations and the result
    is used as input for the predict-like method of the model, that adds the
    prediction to the result.

    """
    def __init__(self, resource_list, name, description=None, api=None,
                 cache_get=None, init_settings=None, execution_settings=None):
        """The pipeline needs
              - resource_list (list): a dataset/model ID or a list of them
                to define the transformations and predictions to be added to
                the input data.
              - name (string): a unique name that will be used when caching the
                resources it needs to be executed
        Optionally, it can receive:
              - description (string): a description of the pipeline procedure
              - api (BigML): a BigML API connection object
              - cache (function): a cache_get function to retrieve cached
                                  resources
              - init_settings (map): a map describing the optional
                                     arguments added when instantiating the
                                     local model (one per model). E.g.:
                  {"deepnet/111111111111111111": {
                      "operation_settings": {
                          "region_score_threshold": 0.6}},
                   "deepnet/222222222222222222": {
                      "operation_settings": {
                          "region_score_threshold": 0.7}}}
              - execution_settings (map): a map describing the optional
                                          arguments added when creating the
                                          predictions. E.g.:

                  {"model/111111111111111111": {
                      "missing_strategy": 1},
                   "model/222222222222222222": {
                      "operating_kind": "confidence"}}

        """

        if use_cache(cache_get):
            self.__dict__ = load(name, cache_get)
            return

        self.name = name
        self.description = description
        self.resource_list = resource_list
        if isinstance(resource_list, str):
            self.resource_list = [resource_list]
        self.local_resources = []
        self.init_settings = init_settings or {}
        self.execution_settings = execution_settings or {}
        self.api = get_api_connection(api)
        self.api.storage = self._get_pipeline_storage()
        self.cache_get = cache_get
        self.datasets = {}

        kwargs = {}
        if self.api is not None:
            kwargs["api"] = self.api
        if cache_get is not None:
            kwargs["cache_get"] = cache_get

        for resource_id in self.resource_list:
            self.init_settings[resource_id] = self.init_settings.get(
                resource_id, {})
            self.init_settings[resource_id].update(kwargs)

        for index, resource in enumerate(self.resource_list):
            resource_id = get_resource_id(resource)
            resource_type = get_resource_type(resource_id)
            local_class = LOCAL_CLASSES.get(resource_type, SupervisedModel)
            kwargs = self.init_settings.get(resource_id, {})
            local_resource = local_class(resource, **kwargs)
            if isinstance(local_resource, SupervisedModel):
                self.execution_settings[resource_id] = \
                    self.execution_settings.get(
                        resource_id, {})
                self.execution_settings[resource_id].update({"full": True})
            self.local_resources.append([local_resource])
            if (hasattr(local_resource, "dataset_id") and \
                    local_resource.dataset_id) or \
                    isinstance(local_resource, Dataset):
                if local_resource.dataset_id in self.datasets:
                    dataset = self.datasets[local_resource.dataset_id]
                else:
                    dataset = Dataset(local_resource.dataset_id, api=self.api)
                    self.datasets = get_datasets_dict(dataset, self.datasets)
                dataset_chain = get_datasets_chain(dataset)
                self.local_resources[index].extend(dataset_chain)
                self.local_resources[index].reverse()

        new_resources = self.local_resources[0][:]
        for index, resources in enumerate(self.local_resources):
            if index < 1:
                continue
            for resource in resources:
                if resource not in new_resources:
                    new_resources.append(resource)
        self.local_resources = new_resources

    def _get_pipeline_storage(self):
        """ Creating a separate folder inside the given storage folder to
        contain the pipeline related models based on the pipeline name.
        If the folder already exists, first we check that all the resources
        in the resources list are already stored there. If that's not the
        case, we rename the folder by adding a datetime suffix and create a
        new pipeline folder to store them.
        """
        if self.api.storage is None:
            self.api.storage = STORAGE
        path = os.path.join(self.api.storage, self.name)
        if os.path.exists(path):
            if check_in_path(path, self.resource_list):
                return path
            # adding a suffix to store old pipeline version
            bck_path = "%s_%s_bck" % (path,
                                      str(datetime.now()).replace(" ", "_"))
            os.rename(path, bck_path)
        check_dir(path)
        return path

    def execute(self, input_data_list):
        """Applying the Pipeline transformations and predictions on the
        list of input data.

        """

        inner_data = copy.deepcopy(input_data_list)
        for index, local_resource in enumerate(self.local_resources):
            # first dataset will never contain transformations
            if index < 1:
                continue
            if isinstance(local_resource, Dataset):
                inner_data = local_resource.transform(inner_data)
            else:
                execution_settings = self.execution_settings.get(
                    local_resource.resource_id, {})
                inner_data = local_resource.batch_predict(
                    inner_data, **execution_settings)
        return inner_data

    def export(self, output_directory=None):
        """Exports all the resources needed in the pipeline to the user-given
        output directory. The entire pipeline folder is exported and its name
        is used as filename.
        """
        def zipdir(path, ziph):
            # ziph is zipfile handle
            for root, dirs, files in os.walk(path):
                for file in files:
                    ziph.write(os.path.join(root, file),
                               os.path.relpath(os.path.join(root, file),
                                               os.path.join(path, '..')))

        if output_directory is None:
            output_directory = os.getcwd()
        out_filename = os.path.join(output_directory, "%s.zip" % self.name)
        # write README file with the information that describes the Pipeline
        readme = "Pipeline name: %s\n%s\n\nBuilt from: %s" % (
            self.name, self.description or "", ", ".join(self.resource_list))
        with open(os.path.join(self.api.storage, "README.txt"), "w") as \
                readme_handler:
            readme_handler.write(readme)
        with zipfile.ZipFile(out_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipdir(self.api.storage, zipf)
