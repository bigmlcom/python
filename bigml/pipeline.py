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

import os
import zipfile
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
    format_data, get_formatted_data, save_json, fs_cache_get, fs_cache_set, \
    dump, asciify
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


def merge_input_data(input_data_list, output_data_list):
    """Adding input data to the output """
    for index, input_data in enumerate(input_data_list):
        for key, value in input_data.items():
            if key not in output_data_list[index]:
                output_data_list[index].update({key: value})
    return output_data_list


class Transformer():
    """Base class to handle transformations. It offers a transform method
    that can handle list of dictionaries or Pandas DataFrames a inputs and
    delegates to the `data_transform` method the actual transformations to
    be applied and should be implemented in the classes derived from it.
    """

    def __init__(self, generator, data_format, resource_id=None, name=None,
                 description=None):
        """Adds initial attributes:
         - generator: object, function or list of functions that will be
           doing the transformation
         - data_format: whether to accept a DataFrame or a list of dictionaries
           as inputs for the generator
         - resource_id: unique identifier for the transformer object
         - name: name for the transformer
         - description: description for the transformations in the transformer
        """
        self.generator = generator
        self.data_format = data_format
        self.resource_id = resource_id
        self.name = name
        self.description = description

    def __formatted_input(self, input_data_list):
        """Returns a copy of the input data list in the expected format """
        return get_formatted_data(input_data_list, self.data_format)

    def transform(self, input_data_list, out_format=None):
        """Returns a new input_data_list where the transformations defined
        in the generator have been applied. It handles format transformation
        if needed before applying the generator function.
        """
        data_format = get_data_format(input_data_list)
        inner_data_list = self.__formatted_input(input_data_list)
        result = self.data_transform(inner_data_list)
        if self.data_format != data_format and out_format is None:
            return format_data(result, data_format)
        if self.data_format != out_format:
            return format_data(result, out_format)
        return result

    def data_transform(self, input_data_list):
        """Method to be re-implemented in each of the transformers. Using
        identity by default."""
        raise NotImplementedError("This method needs to be implemented")


class BMLTransformer(Transformer):
    """Transformer wrapper for BigML resources."""
    def __init__(self, local_resource, outputs=None, **kwargs):
        """Receives a local resource (Dataset, SupervisedModel, Cluster...)
        and creates a `Transformer` from it to apply the corresponding
        transformations.
        - for Datasets, Flatline transformations (if any) are applied
        - for models, a batch prediction (scoring, topic distribution, etc.) is
          applied and added to the original input.

        Optional arguments are:
        :param outputs: dictionary of output fields and headers
        :type outputs: dict
        :param kwargs: dictionary of runtime settings for batch predictions
                       (e.g. missing_strategy, operating_point, etc.)
        :type kwargs: dict
        """
        try:
            generator = local_resource.transform
            self.add_input = False
        except AttributeError:
            if hasattr(local_resource, "batch_predict"):
                generator = lambda x : \
                    local_resource.batch_predict(x, outputs=outputs, **kwargs)
                self.add_input = True
            else:
                raise ValueError("The local resource needs to provide "
                                 "a transform, or batch_predict "
                                 "method to generate transformations.")
        super().__init__(generator,
                         INTERNAL,
                         local_resource.resource_id,
                         local_resource.name,
                         local_resource.description)
        self.dump = local_resource.dump

    def data_transform(self, input_data_list):
        """Returns a list of dictionaries with the generated transformations.
        The input list is expected to be a list of dictionaries"""
        return self.generator(input_data_list)


class DFTransformer(Transformer):
    """Transformer wrapper for DataFrames """
    def __init__(self, generator, resource_id=None, name=None,
                 description=None):
        """Receives the function or list of functions to be applied on
        the input DataFrame
        Optional parameters are:
        :param resource_id: unique ID for the Transformer
        :type resource_id: str
        :param name: Transformer name
        :type name: str
        :param description: Description for the transformations.
        :type description: str
        """
        if not isinstance(generator, list):
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
    """Transformer wrapper for scikit learn pipelines or transformations """
    def __init__(self, generator, resource_id=None, name=None,
                 description=None, output=None):
        """Receives the pipeline or transformation to be applied on
        the input DataFrame
        Optional parameters are:
        :param resource_id: unique ID for the Transformer
        :type resource_id: str
        :param name: Transformer name
        :type name: str
        :param description: Description for the transformations.
        :type description: str
        :param output: Dictionary containing the headers to be used for the
                       new fields generated in the transformation.
        :type output: dict
        """

        try:
            generator_fn = generator.transform
            self.add_input = False
        except AttributeError:
            try:
                generator_fn = generator.predict
                self.add_input = True
            except AttributeError:
                try:
                    generator_fn = generator.score
                    self.add_input = True
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
        if not self.add_input:
            return result
        return concat([input_data_list, result], axis=1)


class Pipeline(Transformer):
    """Class to define sequential transformations. The transformations can
    come from BigML resources or be defined as Pipe steps defined as functions
    to be applied to DataFrame pipes, scikit pipelines

    """
    def __init__(self, name, steps=None, resource_id=None, description=None):
        """Builds a Pipeline from the list of steps provided in the `steps`
        argument. It is compulsory to assign a name that will be used as
        reference
        :param name: Reference name for the pipeline
        :type name: str
        :param steps: List of Transformers. All of them need to offer a
                      `.transform` method
        :type steps: list
        :param description: Description of the transformations in the pipeline
        :type description: str
        """
        super().__init__(None, # no generator is provided
             None, # no data format is assumed
             resource_id or name,
             name,
             description)

        self.steps = []
        self.extend(steps)

    def extend(self, steps=None):
        """Adding new transformations to the Pipeline steps"""
        if steps is None:
            steps = []
        for step in steps:
            if not hasattr(step, "transform"):
                raise ValueError("Failed to find the .transform method in "
                    "all the Pipeline steps.")
        self.steps.extend(steps)

    def transform(self, input_data_list, out_format=None):
        """Applying the Pipeline transformations and predictions on the
        list of input data. `out_format` forces the output format
        to either a DataFrame or a list of dictionaries.

        """
        result = self.data_transform(input_data_list)
        if out_format is not None:
            current_format = get_data_format(result)
            if current_format != out_format:
                return format_data(result, out_format)
        return result

    def data_transform(self, input_data_list):
        """Delegates transformation to each Transformer step"""
        current_format = get_data_format(input_data_list)
        if len(self.steps) == 0:
            return input_data_list
        inner_data_list = input_data_list
        for index, step in enumerate(self.steps[:-1]):
            try:
                inner_data_list = step.transform(inner_data_list)
            except Exception as exc:
                raise ValueError(
                    "Failed to apply step number %s in pipeline %s: %s" %
                    (index, self.name, exc))
        try:
            inner_data_list = self.steps[-1].transform(
                inner_data_list, out_format=current_format)
            if hasattr(self.steps[-1], "add_input") and \
                    self.steps[-1].add_input:
                self.steps[-1].merge_input_data(input_data_list,
                                                inner_data_list)
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
      - resource_list: A list of resource IDs. Only datasets and supervised
                       or unsupervised model resources are allowed.

    When a dataset is provided, only the chain of transformations leading to
    that dataset structure is applied. When a model is provided, the input
    data is pre-modeled using that chain of transformations and the result
    is used as input for the predict-like method of the model, that adds the
    prediction to the result. If the pipeline is expected to use strictly
    the resources in the original resource_list, you can use the last_step
    argument

    """
    def __init__(self, name, resource_list=None, description=None, api=None,
                 cache_get=None, init_settings=None, execution_settings=None,
                 last_step=False):
        """The pipeline needs
        :param name: A unique name that will be used when caching the
                     resources it needs to be executed.
        :type name: str
        :param resource_list: A dataset/model ID or a list of them
                              to define the transformations and predictions
                              to be added to the input data.
        :type resource_list: list
        Optionally, it can receive:
        :param description: A description of the pipeline procedure
        :type description: str
        :param api: A BigML API connection object
        :type api: BigML
        :param cache_get: A cache_get function to retrieve cached resources
        :type cache_get: function
        :param init_settings: A dictionary describing the optional arguments
                              added when instantiating the local model
                              (one per model ID)
           e.g.:
              {"deepnet/111111111111111111": {
                  "operation_settings": {
                      "region_score_threshold": 0.6}},
               "deepnet/222222222222222222": {
                  "operation_settings": {
                      "region_score_threshold": 0.7}}}
        :type init_settings: dict
        :param execution_settings: A dictionary describing the optional
                                   arguments added when creating the
                                   predictions.
           e.g.:
              {"model/111111111111111111": {
                  "missing_strategy": 1},
               "model/222222222222222222": {
                  "operating_kind": "confidence"}}
        :type execution_settings: dict

        """

        if resource_list is None and use_cache(cache_get):
            self.__dict__ = load(name, cache_get)
        else:
            super().__init__(name, description=description)

            # API related attributes
            if resource_list is None:
                resource_list = []
            self.resource_list = resource_list
            if isinstance(resource_list, str):
                self.resource_list = [resource_list]
            for item in self.resource_list:
                resource_id = get_resource_id(item)
                if resource_id is None:
                    raise ValueError("Only resource IDs are allowed as first "
                        "argument.")
            self.init_settings = init_settings or {}
            self.execution_settings = execution_settings or {}
        self._api = get_api_connection(api)
        self._api.storage = self._get_pipeline_storage()
        self._cache_get = cache_get
        self.steps = []
        self.extend(self.__retrieve_steps(last_step))

    def __retrieve_steps(self, last_step):
        """Retrieving the steps that need to be used to reproduce the
        transformations leading to the resources given in the original list
        """
        local_resources = []
        init_settings = self.init_settings.copy()
        execution_settings = self.execution_settings.copy()
        datasets = {}
        steps = []

        kwargs = {}
        if self._api is not None:
            kwargs["api"] = self._api
        if self._cache_get is not None:
            kwargs["cache_get"] = self._cache_get

        for resource_id in self.resource_list:
            init_settings[resource_id] = init_settings.get(
                resource_id, {})
            init_settings[resource_id].update(kwargs)

        for index, resource in enumerate(self.resource_list):
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
                if not last_step:
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
            execution_settings = self.execution_settings.get(
                local_resource.resource_id, {})
            steps.append(BMLTransformer(
                local_resource, **execution_settings))
        return steps

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
            if check_in_path(path, self.resource_list):
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
        check_dir(output_directory)
        name = asciify(self.name)
        out_filename = os.path.join(output_directory, f"{name}.zip")

        # write README file with the information that describes the Pipeline
        name = self.name
        description = self.description or ""
        resources = ", ".join(self.resource_list)
        readme = (f"Pipeline name: {name}\n{description}\n\n"
                  f"Built from: {resources}")
        with open(os.path.join(self._api.storage, "README.txt"), "w",
                  encoding="utf-8") as readme_handler:
            readme_handler.write(readme)
        # write JSON file describing the pipeline resources
        pipeline_vars = vars(self)
        stored_vars = {}
        for key, value in pipeline_vars.items():
            if not key.startswith("_") and not key == "steps":
                stored_vars.update({key: value})
        pipeline_filename = os.path.join(self._api.storage, asciify(self.name))
        save_json(stored_vars, pipeline_filename)
        with zipfile.ZipFile(out_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipdir(self._api.storage, zipf)

    def dump(self, output_dir=None, cache_set=None):
        """Uses msgpack to serialize the resource object and all its steps
        If cache_set is filled with a cache set method, the method is called
        to store the serialized value
        """
        pipeline_vars = vars(self)
        stored_vars = {}
        for key, value in pipeline_vars.items():
            if not key.startswith("_") and not key == "steps":
                stored_vars.update({key: value})
        if output_dir is not None:
            check_dir(output_dir)
            cache_set = cache_set or fs_cache_set(output_dir)
        dump(stored_vars, output=None, cache_set=cache_set)
        for step in self.steps:
            step.dump(cache_set=cache_set)

    @classmethod
    def load(cls, name, dump_dir):
        """Restores the information of the pipeline and its steps from a
        previously dumped pipeline file. The objects used in each step
        of the pipeline are expected to be in the same
        """
        if dump_dir is not None and name is not None:
            return cls(name,
                       None,
                       cache_get=fs_cache_get(dump_dir))
        return None
