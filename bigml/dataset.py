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
Class to store Dataset transformations based on the Dataset API response

"""

import copy

from bigml.fields import Fields, sorted_headers, get_new_fields
from bigml.api import get_api_connection, get_dataset_id, get_status
from bigml.basemodel import get_resource_dict
from bigml.util import DEFAULT_LOCALE, use_cache, cast
from bigml.constants import FINISHED
from bigml.flatline import Flatline


class Dataset:
    """Local representation of a BigML Dataset. It can store a sample of
    data whose fields are a subset of the ones defined in the fields
    attribute.
    """
    def __init__(self, dataset, api=None, cache_get=None):
        if use_cache(cache_get):
            self.__dict__ = load(get_dataset_id(dataset), cache_get)
            return

        self.resource_id = None
        self.rows = None
        self.origin_dataset = None
        self.in_fields = None
        self.out_fields = None
        self.description = None
        self.locale = None
        self.api = get_api_connection(api)
        self.cache_get = cache_get
        self.transformations = None

        # retrieving dataset information from
        self.resource_id, dataset = get_resource_dict( \
            dataset, "dataset", api=self.api, no_check_fields=False)

        if 'object' in dataset and isinstance(dataset['object'], dict):
            dataset = dataset['object']

        if 'fields' in dataset and isinstance(dataset['fields'], dict):
            status = get_status(dataset)
            if 'code' in status and status['code'] == FINISHED:
                self.out_fields = Fields(dataset)
                self.out_header_names, _ = sorted_headers(self.out_fields)
                self.description = dataset["description"]
                self.locale = dataset.get('locale', DEFAULT_LOCALE)
                self.rows = dataset.get("rows", 0)
                # we extract the generators and names from the "output_fields"
                new_fields = get_new_fields(dataset.get("output_fields", []))
                origin_dataset = dataset.get("origin_dataset")
                if origin_dataset:
                    self.add_transformations(origin_dataset, new_fields)
                    self.in_header_names, self.in_header_ids = sorted_headers(
                        self.in_fields)

    def add_transformations(self, origin_dataset, new_fields):
        """Adds a new transformation where the new fields provided are
        defined
        """
        _, origin_dataset = get_resource_dict(
            origin_dataset, "dataset", api=self.api)
        self.origin_dataset = Dataset(origin_dataset, api=self.api,
                                      cache_get=self.cache_get)
        self.in_fields = self.origin_dataset.out_fields
        if new_fields:
            self.transformations = new_fields

    def get_sample(self, rows_number=32):
        """Gets a sample of data representing the dataset """
        sample = self.api.create_sample(self.resource_id)
        if self.api.ok(sample):
            sample = self.api.get_sample(
                sample["resource"], "rows=%s" % rows_number)
            return sample.get("object", {}).get("sample", {}).get("rows")
        return []

    def get_inputs_sample(self, rows_number=32):
        """Gets a sample of data representing the origin dataset """
        if self.origin_dataset is None:
            return []
        return self.origin_dataset.get_sample(rows_number=rows_number)

    def _input_array(self, input_data):
        """Transform the dict-like input data into a row """
        input_names = input_data.keys()
        new_input_data = {}
        for key, value in input_data.items():
            headers = self.in_header_ids
            if key not in self.in_fields.fields:
                key = self.in_fields.fields_by_name.get(key, key)
                headers = self.in_header_names
            new_input_data.update({key: value})
        cast(new_input_data, self.in_fields.fields)
        row = []
        for name in self.in_header_ids:
            row.append(None if not name in new_input_data else
                new_input_data[name])
        return row

    def _transform(self, input_arrays):
        """Given a list of inputs that match the origin dataset structure,
        apply the Flatline transformations used in the dataset

        """
        new_input_arrays = []
        out_headers = []
        fields = {"fields": self.in_fields.fields}
        out_arrays = []
        for transformation in self.transformations:
            expr = transformation.get("field")
            names = transformation.get("names", [])
            out_headers.extend(names)
            # evaluating first to raise an alert if the expression is failing
            check = Flatline.interpreter.evaluate_sexp(
                expr, fields, True).valueOf()
            if "error" in check:
                raise ValueError(check["error"])
            new_input = Flatline.interpreter.eval_and_apply_sexp(
                expr, fields, input_arrays)
            for index, _ in enumerate(new_input):
                try:
                    new_input_arrays[index]
                except IndexError:
                    new_input_arrays.append([])
                new_input_arrays[index].extend(new_input[index])
        for index, input_array in enumerate(new_input_arrays):
            try:
                out_arrays[index]
            except IndexError:
                out_arrays.append([])
            out_arrays[index].extend(input_array)
        return [out_headers, out_arrays]


    def transform(self, input_data_list):
        """Applies the transformations to the given input data and returns
        the result. Usually, the input_data_list will contain a single
        dictionary, but it can contain a list of them if needed for window
        functions.
        """
        if self.transformations is None:
            return input_data_list
        rows = [self._input_array(input_data) for input_data in
            input_data_list]
        out_headers, out_arrays = self._transform(rows)
        results = [dict(zip(out_headers, row)) for row
            in out_arrays]
        for index, result in enumerate(results):
            results[index] = {key: value for key, value in result.items()
                              if value is not None}
        return results
