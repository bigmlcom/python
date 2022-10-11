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
import numpy as np
import types

try:
    from pandas import DataFrame, concat
    PANDAS_READY = True
except ImportError:
    PANDAS_READY = False

from datetime import datetime

from bigml.constants import OUT_NEW_HEADERS, DATAFRAME, INTERNAL
from bigml.api import get_api_connection, get_resource_id, get_resource_type
from bigml.util import use_cache, load, check_dir, get_data_format, \
    format_data, get_formatted_data
from bigml.constants import STORAGE
from bigml.dataset import Dataset
from bigml.supervised import SupervisedModel
from bigml.cluster import Cluster
from bigml.anomaly import Anomaly
from bigml.pca import PCA

try:
    from bigml.topicmodel import TopicModel
    NO_TOPIC = False
except ImportError:
    NO_TOPIC = True


if NO_TOPIC:
    LOCAL_CLASSES = {
        "dataset": Dataset,
        "cluster": Cluster,
        "anomaly": Anomaly,
        "pca": PCA,
        }
else:
    LOCAL_CLASSES = {
        "dataset": Dataset,
        "cluster": Cluster,
        "anomaly": Anomaly,
        "topicmodel": TopicModel,
        "pca": PCA,
        }


def get_datasets_chain(dataset, dataset_list=None):
    """Builds recursively the chain of datasets leading to a dataset """
    if dataset_list is None:
        dataset_list = []
    dataset_list.append(dataset)
    if dataset.origin_dataset is None:
        return dataset_list

    return get_datasets_chain(dataset.origin_dataset, dataset_list)


def get_datasets_dict(dataset, dataset_dict=None):
    """Stores a dictionary dataset_id -> Dataset for the chain of datasets """
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


class Transformer():

    def __init__(self, generator, data_format, resource_id=None, name=None,
                 description=None):
        self.generator = generator
        self.data_format = data_format
        self.resource_id = resource_id,
        self.name = name
        self.description = description

    def __formatted_input(self, input_data_list):
        """Returns a copy of the input data list in the expected format """
        return get_formatted_data(input_data_list, self.data_format)

    def transform(self, input_data_list, out_format=None):
        data_format = get_data_format(input_data_list)
        inner_data_list = self.__formatted_input(input_data_list)
        result = self.data_transform(inner_data_list)
        if self.data_format != data_format and out_format is None:
            return format_data(result, data_format)
        elif self.data_format != out_format:
            return format_data(result, out_format)
        return result

    def data_transform(input_data_list):
        """Method to be re-implemented in each of the transformers """
        return input_data_list


class BMLTransformer(Transformer):

    def __init__(self, local_resource, outputs=None, **kwargs):
        try:
            generator = local_resource.transform
        except AttributeError:
            if hasattr(local_resource, "batch_predict"):
                generator = lambda x : \
                    local_resource.batch_predict(x, outputs=outputs, **kwargs)
            else:
                raise ValueError("The local resource needs to provide "
                                 "a transform, or batch_predict "
                                 "method to generate transformations.")
        super().__init__(generator,
                         INTERNAL,
                         local_resource.resource_id,
                         local_resource.name,
                         local_resource.description)

    def data_transform(self, input_data_list):
        return self.generator(input_data_list)


class DFTransformer(Transformer):

    def __init__(self, generator, resource_id=None, name=None,
                 description=None):
        if isinstance(generator, list):
            generator = generator
        else:
            generator = [generator]
        for index, item in enumerate(generator):
            if not isinstance(item, tuple) and isinstance(
                    item, types.FunctionType):
                generator[index] = (item, [], {})
            elif isinstance(item, tuple) and isinstance(
                    item[0], types.FunctionType):
                try:
                    args = item[1]
                    if not isinstance(args, list):
                        raise ValueError("The syntax of the first argument is "
                                         " function or (function, list, dict)")
                except IndexError:
                    args = []
                try:
                    kwargs = item[2]
                    if not isinstance(kwargs, dict):
                        raise ValueError("The syntax of the first argument is "
                                         " function or (function, list, dict)")
                except IndexError:
                    kwargs = {}

                generator[index] = (item[0], args, kwargs)
            else:
                raise ValueError("Only functions or tuples of functions are "
                                 "allowed as first argument.")

        super().__init__(generator,
                         DATAFRAME,
                         resource_id or "dftrans_%s" %
                             str(datetime.now()).replace(" ", "_"),
                         name,
                         description)

    def data_transform(self, input_data_list):
        """Calling the corresponding method in the generator.
        The input_data_list is expected to be a Dataframe.

        """
        result = input_data_list.copy()
        for function, args, kwargs in self.generator:
            result = result.pipe(function, *args, **kwargs)
        return result


class SKTransformer(Transformer):

    def __init__(self, generator, resource_id=None, name=None,
                 description=None, output=None):
        try:
            generator_fn = generator.transform
        except AttributeError:
            try:
                generator_fn = generator.predict
            except AttributeError:
                try:
                    generator_fn = generator.score
                except AttributeError:
                    raise ValueError("Failed to find a .transform, .predict "
                                     "or .score method in the first argument "
                                     "object.")

        super().__init__(generator_fn,
                         DATAFRAME,
                         resource_id or "sktrans_%s" %
                             str(datetime.now()).replace(" ", "_"),
                         name,
                         description)
        self.output = output or {}
        try:
            self.output_headers = generator.get_feature_names_out()
        except AttributeError:
            self.output_headers = self.output.get(OUT_NEW_HEADERS)

    def data_transform(self, input_data_list):
        """Calling the corresponding method in the generator.
        The input_data_list is expected to be a Dataframe.

        """
        result = self.generator(input_data_list)
        try:
            result = result.toarray()
        except AttributeError:
            pass
        df_kwargs = {"index": input_data_list.index}
        if self.output_headers is not None:
            df_kwargs.update({"columns": self.output_headers})
        result = DataFrame(result, **df_kwargs)
        return concat([input_data_list, result], axis=1)


class Pipeline(Transformer):
    """Class to define sequential transformations. The transformations can
    come from BigML resources or be defined as Pipe steps defined as functions
    to be applied to DataFrame pipes, scikit pipelines

    """
    def __init__(self, name, steps=None, description=None):

        self.name = name
        self.description = description
        self.steps = []
        self.extend(steps)

    def extend(self, steps=None):
        if steps is None:
            steps = []
        for step in steps:
            if not hasattr(step, "transform"):
                raise ValueError("Failed to find the .transform method in "
                    "all the Pipeline steps.")
        self.steps.extend(steps)

    def transform(self, input_data_list):
        """Applying the Pipeline transformations and predictions on the
        list of input data.

        """
        current_format = get_data_format(input_data_list)
        inner_data_list = input_data_list.copy()
        if len(self.steps) > 0:
            for index, step in enumerate(self.steps[:-1]):
                try:
                    inner_data_list = step.transform(inner_data_list)
                except Exception as exc:
                    raise ValueError("Failed to apply step number %s: %s" %
                        (index, exc))
            try:
                inner_data_list = self.steps[-1].transform(
                    inner_data_list, out_format=current_format)
            except Exception as exc:
                raise ValueError("Failed to apply the last step: %s" % exc)
        return inner_data_list


class BMLPipeline(Pipeline):
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

        super().__init__(name, description=description)

        # API related attributes
        self._resource_list = resource_list
        if isinstance(resource_list, str):
            self._resource_list = [resource_list]
        for item in self._resource_list:
            resource_id = get_resource_id(item)
            if resource_id is None:
                raise ValueError("Only resource IDs are allowed as first "
                    "argument.")
        self._api = get_api_connection(api)
        self._api.storage = self._get_pipeline_storage()
        self._cache_get = cache_get

        local_resources = []
        init_settings = init_settings or {}
        execution_settings = execution_settings or {}
        datasets = {}
        steps = []

        kwargs = {}
        if self._api is not None:
            kwargs["api"] = self._api
        if cache_get is not None:
            kwargs["cache_get"] = cache_get

        for resource_id in self._resource_list:
            init_settings[resource_id] = init_settings.get(
                resource_id, {})
            init_settings[resource_id].update(kwargs)

        for index, resource in enumerate(self._resource_list):
            resource_id = get_resource_id(resource)
            resource_type = get_resource_type(resource_id)
            local_class = LOCAL_CLASSES.get(resource_type, SupervisedModel)
            kwargs = init_settings.get(resource_id, {})
            local_resource = local_class(resource, **kwargs)
            if isinstance(local_resource, SupervisedModel):
                execution_settings[resource_id] = \
                    execution_settings.get(
                        resource_id, {})
                execution_settings[resource_id].update({"full": True})
            local_resources.append([local_resource])
            if (hasattr(local_resource, "dataset_id") and \
                    local_resource.dataset_id) or \
                    isinstance(local_resource, Dataset):
                if local_resource.dataset_id in datasets:
                    dataset = datasets[local_resource.dataset_id]
                else:
                    dataset = Dataset(local_resource.dataset_id,
                                      api=self._api)
                    datasets = get_datasets_dict(dataset, datasets)
                dataset_chain = get_datasets_chain(dataset)
                local_resources[index].extend(dataset_chain)
                local_resources[index].reverse()

        try:
            new_resources = local_resources[0][:]
        except IndexError:
            new_resources = []
        for index, resources in enumerate(local_resources):
            if index < 1:
                continue
            for resource in resources:
                if resource not in new_resources:
                    new_resources.append(resource)
        local_resources = new_resources
        for local_resource in local_resources:
            # non-flatline datasets will not add transformations
            if isinstance(local_resource, Dataset) and \
                    local_resource.transformations is None:
                continue
            steps.append(BMLTransformer(
                local_resource, **execution_settings.get(
                local_resource.resource_id, {})))
        self.extend(steps)

    def _get_pipeline_storage(self):
        """ Creating a separate folder inside the given storage folder to
        contain the pipeline related models based on the pipeline name.
        If the folder already exists, first we check that all the resources
        in the resources list are already stored there. If that's not the
        case, we rename the folder by adding a datetime suffix and create a
        new pipeline folder to store them.
        """
        if self._api.storage is None:
            self._api.storage = STORAGE
        path = os.path.join(self._api.storage, self.name)
        if os.path.exists(path):
            if check_in_path(path, self._resource_list):
                return path
            # adding a suffix to store old pipeline version
            datetime_str = str(datetime.now()).replace(" ", "_")
            bck_path = f"{path}_{datetime_str}_bck"
            os.rename(path, bck_path)
        check_dir(path)
        return path

    def export(self, output_directory=None):
        """Exports all the resources needed in the pipeline to the user-given
        output directory. The entire pipeline folder is exported and its name
        is used as filename.
        """
        def zipdir(path, ziph):
            # ziph is zipfile handle
            for root, _, files in os.walk(path):
                for file in files:
                    ziph.write(os.path.join(root, file),
                               os.path.relpath(os.path.join(root, file),
                                               os.path.join(path, '..')))

        if output_directory is None:
            output_directory = os.getcwd()
        out_filename = os.path.join(output_directory, f"{self.name}.zip")
        # write README file with the information that describes the Pipeline
        name = self.name
        description = self.description or ""
        resources = ", ".join(self._resource_list)
        readme = (f"Pipeline name: {name}\n{description}\n\n"
                  f"Built from: {resources}")
        with open(os.path.join(self._api.storage, "README.txt"), "w",
                  encoding="utf-8") as readme_handler:
            readme_handler.write(readme)
        with zipfile.ZipFile(out_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipdir(self._api.storage, zipf)
