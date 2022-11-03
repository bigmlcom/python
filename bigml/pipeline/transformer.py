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
DataTransformer classes that handle the transformations generated on input
data by Feature Engineering, Models, Anomaly Detectors, etc.
The BMLDataTransformer will take care of transformations that use BigML
objects as transformation generators. Other libraries, like Pandas
(DFDataTransfomer) and scikit-learn (SKDataTransformer)
will need their own DataTransformer subclasses to define
their own transformations.

"""

import types

from datetime import datetime

from bigml.constants import INTERNAL, DATAFRAME, OUT_NEW_HEADERS
from bigml.util import get_formatted_data, format_data, get_data_format

try:
    from pandas import DataFrame, concat
    PANDAS_READY = True
except ImportError:
    PANDAS_READY = False


class DataTransformer():
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
         - resource_id: unique identifier for the data transformer object
         - name: name for the data transformer
         - description: description for the transformations in the data
                        transformer
        """
        self.generator = generator
        self.data_format = data_format
        self.resource_id = resource_id
        self.name = name
        self.description = description

    def _formatted_input(self, input_data_list):
        """Returns a copy of the input data list in the expected format """
        return get_formatted_data(input_data_list, self.data_format)

    def transform(self, input_data_list, out_format=None):
        """Returns a new input_data_list where the transformations defined
        in the generator have been applied. It handles format transformation
        if needed before applying the generator function.
        """
        data_format = get_data_format(input_data_list)
        inner_data_list = self._formatted_input(input_data_list)
        result = self.data_transform(inner_data_list)
        if self.data_format != data_format and out_format is None:
            return format_data(result, data_format)
        if self.data_format != out_format:
            return format_data(result, out_format)
        return result

    def data_transform(self, input_data_list):
        """Method to be re-implemented in each of the data transformers. Using
        identity by default."""
        raise NotImplementedError("This method needs to be implemented")


class BMLDataTransformer(DataTransformer):
    """Transformer wrapper for BigML resources."""
    def __init__(self, local_resource, outputs=None, **kwargs):
        """Receives a local resource (Dataset, SupervisedModel, Cluster...)
        and creates a `DataTransformer` from it to apply the corresponding
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
        self.local_resource = local_resource
        self.dump = local_resource.dump

    def data_transform(self, input_data_list):
        """Returns a list of dictionaries with the generated transformations.
        The input list is expected to be a list of dictionaries"""
        return self.generator(input_data_list)

    def merge_input_data(self, input_data_list, output_data_list,
                         out_format=None):
        """Adding input data to the output """
        data_format = get_data_format(input_data_list)
        input_data_list = self._formatted_input(input_data_list)
        output_data_list = self._formatted_input(output_data_list)
        for index, input_data in enumerate(input_data_list):
            for key, value in input_data.items():
                if key not in output_data_list[index]:
                    output_data_list[index].update({key: value})
        if self.data_format != out_format:
            return format_data(output_data_list, data_format)
        return output_data_list


class DFDataTransformer(DataTransformer):
    """DataTransformer wrapper for DataFrames """
    def __init__(self, generator, resource_id=None, name=None,
                 description=None):
        """Receives the function or list of functions to be applied on
        the input DataFrame
        Optional parameters are:
        :param resource_id: unique ID for the DataTransformer
        :type resource_id: str
        :param name: DataTransformer name
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


class SKDataTransformer(DataTransformer):
    """DataTransformer wrapper for scikit learn pipelines or transformations """
    def __init__(self, generator, resource_id=None, name=None,
                 description=None, output=None):
        """Receives the pipeline or transformation to be applied on
        the input DataFrame
        Optional parameters are:
        :param resource_id: unique ID for the DataTransformer
        :type resource_id: str
        :param name: DataTransformer name
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

    @staticmethod
    def merge_input_data(input_data_list, output_data_list):
        """Adding input data to the output """
        return concat([input_data_list, output_data_list], axis=1)
