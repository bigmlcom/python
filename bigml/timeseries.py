# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2017-2020 BigML
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

"""A local Predictive Time Series model object

This module defines a Time Series model to make predictions locally or
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
time_series.forecast({"price": {"horizon": 10}})

"""
import logging
import re
import sys
import StringIO
import pprint

from bigml.api import FINISHED
from bigml.api import get_status, get_api_connection
from bigml.util import utf8
from bigml.basemodel import get_resource_dict, extract_objective
from bigml.modelfields import ModelFields
from bigml.tssubmodels import SUBMODELS
from bigml.tsoutconstants import SUBMODELS_CODE, TRIVIAL_MODEL, \
    SEASONAL_CODE, FORECAST_FUNCTION, USAGE_DOC

LOGGER = logging.getLogger('BigML')

REQUIRED_INPUT = "horizon"
SUBMODEL_KEYS = ["indices", "names", "criterion", "limit"]
DEFAULT_SUBMODEL = {"criterion": "aic", "limit": 1}
INDENT = " " * 4


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
            _, trend, seasonality = name.split(",")
            args = [submodel, horizon, seasonality]
        else:
            args = [submodel, horizon]

        forecasts.append( \
            {"model": name,
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

    if indices:
        # adding all submodels by index if they are not also in the names
        # list
        field_submodels = [submodel for index, submodel in \
            enumerate(submodels) if index in indices]

    # union with filtered by names
    if names:
        pattern = r'|'.join(names)
        # only adding the submodels if they have not been included by using
        # indices
        submodel_names = [submodel["name"] for submodel in field_submodels]
        named_submodels = [submodel for submodel in submodels \
            if re.search(pattern, submodel["name"]) is not None and \
            submodel["name"] not in submodel_names]
        field_submodels.extend(named_submodels)

    if not indices and not names:
        field_submodels.extend(submodels)

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
        self.ets_models = {}
        self.error = None
        self.damped_trend = None
        self.seasonality = None
        self.trend = None
        self.time_range = {}
        self.field_parameters = {}
        self._forecast = {}
        self.api = get_api_connection(api)

        self.resource_id, time_series = get_resource_dict( \
            time_series, "timeseries", api=self.api)

        if 'object' in time_series and \
            isinstance(time_series['object'], dict):
            time_series = time_series['object']
        try:
            self.input_fields = time_series.get("input_fields", [])
            self._forecast = time_series.get("forecast")
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
                self.ets_models = time_series_info.get('ets_models', {})
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

    def forecast(self, input_data=None):
        """Returns the class prediction and the confidence

        input_data: Input data to be predicted

        """
        if not input_data:
            forecasts = {}
            for field_id, value in self._forecast.items():
                forecasts[field_id] = []
                for forecast in value:
                    local_forecast = {}
                    local_forecast.update( \
                        {"point_forecast": forecast["point_forecast"]})
                    local_forecast.update( \
                        {"model": forecast["model"]})
                    forecasts[field_id].append(local_forecast)
            return forecasts

        # Checks and cleans input_data leaving only the fields used as
        # objective fields in the model
        new_data = self.filter_objectives( \
            input_data)
        input_data = new_data

        # filter submodels: filtering the submodels in the time-series
        # model to be used in the prediction
        filtered_submodels = {}
        for field_id, field_input in input_data.items():
            filter_info = field_input.get("ets_models", {})
            if not filter_info:
                filter_info = DEFAULT_SUBMODEL
            filtered_submodels[field_id] = filter_submodels( \
                self.ets_models[field_id], filter_info)

        forecasts = {}
        for field_id, submodels in filtered_submodels.items():
            forecasts[field_id] = compute_forecasts(submodels, \
                input_data[field_id]["horizon"])

        return forecasts

    def filter_objectives(self, input_data,
                          full=False):
        """Filters the keys given in input_data checking against the
        objective fields in the time-series model fields.
        If `full` is set to True, it also
        provides information about the fields that are not used.

        """

        unused_fields = []
        new_input = {}
        if isinstance(input_data, dict):

            for key, value in input_data.items():
                if key not in self.fields:
                    key = self.inverted_fields.get(key, key)
                if key in self.input_fields:
                    new_input[key] = value
                else:
                    unused_fields.append(key)

            # raise error if no horizon is provided
            for key, value in input_data.items():
                value = self.normalize(value)
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
                        value.get("ets_models", {}).keys()):
                    raise ValueError( \
                        "Only %s allowed as keys in each fields submodel"
                        " filter." % ", ".join(SUBMODEL_KEYS))

            result = (new_input, unused_fields) if full else \
                new_input
            return result
        else:
            LOGGER.error("Failed to read input data in the expected"
                         " {field:value} format.")
            return ({}, []) if full else {}

    def python(self, out=sys.stdout):
        """Generates the code in python that creates the forecasts

        """
        attributes = [u"l", u"b", u"s", u"phi", u"value", u"slope"]
        components = {}
        model_components = {}
        model_names = []
        out.write(utf8(USAGE_DOC % (self.resource_id,
                                    self.fields[self.objective_id]["name"])))
        output = [u"COMPONENTS = \\"]
        for field_id, models in self.ets_models.items():
            for model in models:
                final_state = model.get("final_state", {})
                attrs = {}
                for attribute in attributes:
                    if attribute in model:
                        attrs.update({attribute: model[attribute]})
                    elif attribute in final_state:
                        attrs.update( \
                            {attribute: final_state[attribute]})
                model_names.append(model["name"])
                model_components[model["name"]] = attrs
            field_name = self.fields[field_id]["name"]
            if field_name not in components:
                components[field_name] = model_components
        partial_output = StringIO.StringIO()
        pprint.pprint(components, stream=partial_output)
        for line in partial_output.getvalue().split("\n"):
            output.append(u"%s%s" % (INDENT, line))

        out.write(utf8(u"\n".join(output)))

        model_names = list(set(model_names))
        if any(name in model_names for name in ["naive", "mean"]):
            out.write(utf8(TRIVIAL_MODEL))
        if any("," in name and name.split(",")[2] in ["A", "M"] for \
               name in model_names):
            out.write(utf8(SEASONAL_CODE))
        trends = [name.split(",")[1] for name in model_names if "," in name]
        trends.extend([name for name in model_names if "," not in name])
        trends = set(trends)
        models_function = []
        for trend in trends:
            models_function.append("\"%s\": _%s_forecast" % (trend, trend))
            out.write(utf8(SUBMODELS_CODE[trend]))
        out.write(utf8(u"\n\nMODELS = \\\n"))
        out.write(utf8("%s%s%s" % \
            (u"    {", u",\n     ".join(models_function), u"}")))

        out.write(utf8(FORECAST_FUNCTION))
