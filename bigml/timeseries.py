# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2017 BigML
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

"""A local Predictive Time-Series model object

This module defines a Time-Series model to make predictions locally or
embedded into your application without needing to send requests to
BigML.io.

This module cannot only save you a few credits, but also enormously
reduce the latency for each prediction and let you use your logistic
regressions offline.

Example usage (assuming that you have previously set up the BIGML_USERNAME
and BIGML_API_KEY environment variables and that you own the
logisticregression/id below):

from bigml.api import BigML
from bigml.timeseries import TimeSeries

api = BigML()

time_series = TimeSeries(
    'timeseries/5026965515526876630001b2')
time_series.predict({"results": 10)

"""
import logging
import math
import copy
import re

from bigml.api import FINISHED
from bigml.api import (BigML, get_time_series_id, get_status)
from bigml.util import cast
from bigml.basemodel import retrieve_resource, extract_objective
from bigml.basemodel import ONLY_MODEL
from bigml.model import STORAGE
from bigml.modelfields import ModelFields, check_model_fields
from bigml.tssubmodels import SUBMODELS


LOGGER = logging.getLogger('BigML')

REQUIRED_INPUT = "horizon"
SUBMODEL_KEYS = ["indices", "names", "criterion", "limit"]
DEFAULT_SUBMODEL = {"criterion": "aic", "limit": 1}


def compute_forecasts(submodels, horizon):
    """Computes the forecasts for each of the models in the submodels
    array. The number of forecasts is set by horizon.
    """
    forecasts = []
    for submodel in submodels:
        name = submodel["name"]
        trend = name
        seasonality = None
        if "," in name:
            error, trend, seasonality = name.split(",")
            args = [submodel, horizon, seasonality]
        else:
            args = [submodel, horizon]

        forecasts.append( \
            {"submodel": name,
             "point_forecast": SUBMODELS[trend](*args)})
    return forecasts


def filter_submodels(submodels, filter_info):
    """Filters the submodels available for the field in the time-series
    model according to the criteria provided in the prediction input data
    for the field.

    """
    field_submodels = []
    submodel_names = []
    # filtering by indices and/or names
    indices = filter_info.get(SUBMODEL_KEYS[0], [])
    names = filter_info.get(SUBMODEL_KEYS[1], [])

    if not indices and not names:
        return []

    if indices:
        # adding all submodels by index if they are not also in the names
        # list
        field_submodels = [submodel for index, submodel in \
            enumerate(submodels) if index in indices]

    # union with filtered by names
    if names:
        pattern  = r'|'.join(names)
        # only adding the submodels if they have not been included by using
        # indices
        submodel_names = [submodel["name"] for submodel in field_submodels]
        named_submodels = [submodel for submodel in submodels \
            if re.search(pattern, submodel["name"]) is not None and \
            submodel["name"] not in submodel_names]
        field_submodels.extend(named_submodels)

    # filtering the resulting set by criterion and limit
    criterion = filter_info.get(SUBMODEL_KEYS[2])
    if criterion is not None:
        field_submodels = sorted(field_submodels,
                                 key=lambda x: x.get(criterion, float('inf')))
        limit = filter_info.get(SUBMODEL_KEYS[3])
        if limit is not None:
            field_submodels = field_submodels[0: limit]
    return field_submodels


class TimeSeries(ModelFields):
    """ A lightweight wrapper around a time series model.

    Uses a BigML remote time series model to build a local version
    that can be used to generate predictions locally.

    """

    def __init__(self, time_series, api=None):

        self.resource_id = None
        self.input_fields = []
        self.objective_fields = []
        self.all_numeric_objectives = False
        self.period = 1
        self.submodels = {}
        self.error = None
        self.damped_trend = None
        self.seasonality = None
        self.trend = None
        self.time_range = {}
        self.field_parameters = {}

        # checks whether the information needed for local predictions is in
        # the first argument
        if isinstance(time_series, dict) and \
                not check_model_fields(ltime_series):
            # if the fields used by the logistic regression are not
            # available, use only ID to retrieve it again
            time_series = get_time_series_id( \
                time_series)
            self.resource_id = time_series

        if not (isinstance(time_series, dict)
                and 'resource' in time_series and
                time_series['resource'] is not None):
            if api is None:
                api = BigML(storage=STORAGE)
            self.resource_id = get_time_series_id(time_series)
            if self.resource_id is None:
                raise Exception(
                    api.error_message(time_series,
                                      resource_type='time_series',
                                      method='get'))
            query_string = ONLY_MODEL
            time_series = retrieve_resource(
                api, self.resource_id, query_string=query_string)
        else:
            self.resource_id = get_time_series_id(time_series)

        if 'object' in time_series and \
            isinstance(time_series['object'], dict):
            time_series = time_series['object']
        try:
            self.input_fields = time_series.get("input_fields", [])
            self.objective_fields = time_series.get(
                "objective_fields", [])
            objective_field = time_series['objective_field'] if \
                time_series.get('objective_field') else \
                time_series['objective_fields']
        except KeyError:
            raise ValueError("Failed to find the time series expected "
                             "JSON structure. Check your arguments.")
        if 'time_series' in time_series and \
            isinstance(time_series['time_series'], dict):
            status = get_status(time_series)
            if 'code' in status and status['code'] == FINISHED:
                time_series_info = time_series['time_series']
                fields = time_series_info.get('fields', {})
                self.fields = fields
                if not self.input_fields:
                    self.input_fields = [ \
                        field_id for field_id, _ in
                        sorted(self.fields.items(),
                               key=lambda x: x[1].get("column_number"))]
                self.all_numeric_objectives = time_series_info.get( \
                    'all_numeric_objectives')
                self.period = time_series_info.get('period', 1)
                self.submodels = time_series_info.get('submodels', {})
                self.error = time_series_info.get('error')
                self.damped_trend = time_series_info.get('damped_trend')
                self.seasonality = time_series_info.get('seasonality')
                self.trend = time_series_info.get('trend')
                self.time_range = time_series_info.get('time_range')
                self.field_parameters = time_series_info.get( \
                    'field_parameters', {})

                objective_id = extract_objective(objective_field)
                ModelFields.__init__(
                    self, fields,
                    objective_id=objective_id)
            else:
                raise Exception("The time series isn't finished yet")
        else:
            raise Exception("Cannot create the TimeSeries instance."
                            " Could not find the 'time_series' key"
                            " in the resource:\n\n%s" %
                            time_series)

    def forecast(self, input_data, by_name=True, add_unused_fields=False):
        """Returns the class prediction and the confidence
        By default the input fields must be keyed by field name but you can use
        `by_name` to input them directly keyed by id.

        input_data: Input data to be predicted
        by_name: Boolean, True if input_data is keyed by names
        add_unused_fields: Boolean, True if the prediction should inform about
                           any fields in the input data that are not
                           objective fields in the model

        """

        # Checks and cleans input_data leaving only the fields used as
        # objective fields in the model
        new_data = self.filter_objectives( \
            input_data, by_name=by_name,
            add_unused_fields=False)
        if add_unused_fields:
            new_data, unused_fields = new_data
        input_data = new_data

        # filter submodels: filtering the submodels in the time-series
        # model to be used in the prediction

        filtered_submodels = {}
        for field_id, field_input in input_data.items():
            filter_info = field_input.get("submodels", {})
            if not filter_info:
                filter_info = DEFAULT_SUBMODEL
            filtered_submodels[field_id] = filter_submodels( \
                self.submodels[field_id], filter_info)

        forecasts = {}
        for field_id, submodels in filtered_submodels.items():
            forecasts[field_id] = compute_forecasts(submodels, \
                input_data[field_id]["horizon"])
        return forecasts

    def filter_objectives(self, input_data, by_name=True,
                          add_unused_fields=False):
        """Filters the keys given in input_data checking against the
        objective fields in the time-series model fields.
        If `add_unused_fields` is set to True, it also
        provides information about the ones that are not used.

        """

        unused_fields = []
        new_input = {}
        if isinstance(input_data, dict):
            if by_name:
                # We only remove the keys that are not
                # used as objective fields in the model
                for key, value in input_data.items():
                    if key in self.inverted_fields and \
                            self.inverted_fields[key]:
                        new_input[self.inverted_fields[key]] = value
                    else:
                        unused_fields.append(key)
            else:
                for key, value in input_data.items():
                    if key in self.input_fields:
                        new_input[key] = value
                    else:
                        unused_fields.append(key)

            # raise error if no horizon is provided
            for key, value in input_data.items():
                value = self.normalize(value)
                if value is None:
                    raise ValueError( \
                        "Input data cannot be empty.")
                if not isinstance(value, dict):
                    raise ValueError( \
                        "Each field input data needs to be specified "
                        "as a dictionary. Found %s for field %s." % ( \
                            type(value).name, key))
                if REQUIRED_INPUT not in value:
                    raise ValueError( \
                        "Each field in input data must contain at"
                        "least a \"horizon\" attribute.")
                if any(key not in SUBMODEL_KEYS for key in \
                        value.get("submodel", {}).keys()):
                    raise ValueError( \
                        "Only %s allowed as keys in each fields submodel"
                        " filter." % ", ".join(SUBMODEL_KEYS))

            result = (new_input, unused_fields) if add_unused_fields else \
                new_input
            return result
        else:
            LOGGER.error("Failed to read input data in the expected"
                         " {field:value} format.")
            return ({}, []) if add_unused_fields else {}
