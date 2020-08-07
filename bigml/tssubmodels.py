# -*- coding: utf-8 -*-
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

"""Auxiliary module to store the functions to compute time-series forecasts
following the formulae in
https://www.otexts.org/sites/default/files/fpp/images/Table7-8.png
as explained in
https://www.otexts.org/fpp/7/6
"""

import inspect
import sys


OPERATORS = {"A": lambda x, s: x + s,
             "M": lambda x, s: x * s,
             "N": lambda x, s: x}


def season_contribution(s_list, step):
    """Chooses the seasonal contribution from the list in the period

    s_list: The list of contributions per season
    step: The actual prediction step

    """
    if isinstance(s_list, list):
        period = len(s_list)
        index = abs(- period + 1 + step % period)
        return s_list[index]
    else:
        return 0


def trivial_forecast(submodel, horizon):
    """Computing the forecast for the trivial models

    """
    points = []
    submodel_points = submodel["value"]
    period = len(submodel_points)
    if period > 1:
        # when a period is used, the points in the model are repeated
        for h in range(horizon):
            points.append(submodel_points[h % period])
    else:
        for _ in range(horizon):
            points.append(submodel_points[0])
    return points


def naive_forecast(submodel, horizon):
    """Computing the forecast for the naive model

    """
    return trivial_forecast(submodel, horizon)

def mean_forecast(submodel, horizon):
    """Computing the forecast for the mean model

    """
    return trivial_forecast(submodel, horizon)


def drift_forecast(submodel, horizon):
    """Computing the forecast for the drift model

    """
    points = []
    for h in range(horizon):
        points.append(submodel["value"] + submodel["slope"] * (h + 1))
    return points


def N_forecast(submodel, horizon, seasonality):
    """Computing the forecast for the trend=N models
    ŷ_t+h|t = l_t
    ŷ_t+h|t = l_t + s_f(s, h) (if seasonality = "A")
    ŷ_t+h|t = l_t * s_f(s, h) (if seasonality = "M")
    """
    points = []
    final_state = submodel.get("final_state", {})
    l = final_state.get("l", 0)
    s = final_state.get("s", 0)
    for h in range(horizon):
        # each season has a different contribution
        s_i = season_contribution(s, h)
        points.append(OPERATORS[seasonality](l, s_i))
    return points


def A_forecast(submodel, horizon, seasonality):
    """Computing the forecast for the trend=A models
    ŷ_t+h|t = l_t + h * b_t
    ŷ_t+h|t = l_t + h * b_t + s_f(s, h) (if seasonality = "A")
    ŷ_t+h|t = (l_t + h * b_t) * s_f(s,h) (if seasonality = "M")
    """
    points = []
    final_state = submodel.get("final_state", {})
    l = final_state.get("l", 0)
    b = final_state.get("b", 0)
    s = final_state.get("s", 0)
    for h in range(horizon):
        # each season has a different contribution
        s_i = season_contribution(s, h)
        points.append(OPERATORS[seasonality](l + b * (h + 1), s_i))
    return points


def Ad_forecast(submodel, horizon, seasonality):
    """Computing the forecast for the trend=Ad model
    ŷ_t+h|t = l_t + phi_h * b_t
    ŷ_t+h|t = l_t + phi_h * b_t + s_f(m, h) (if seasonality = "A")
    ŷ_t+h|t = (l_t + phi_h * b_t) * s_f(m, h) (if seasonality = "M")
    with phi_0 = phi
         phi_1 = phi + phi^2
         phi_h = phi + phi^2 + ... + phi^(h + 1) (for h > 0)
    """
    points = []
    final_state = submodel.get("final_state", {})
    l = final_state.get("l", 0)
    b = final_state.get("b", 0)
    phi = submodel.get("phi", 0)
    s = final_state.get("s", 0)
    phi_h = phi
    for h in range(horizon):
        # each season has a different contribution
        s_i = season_contribution(s, h)
        points.append(OPERATORS[seasonality](l + phi_h * b, s_i))
        phi_h = phi_h + pow(phi, h + 2)
    return points


def M_forecast(submodel, horizon, seasonality):
    """Computing the forecast for the trend=M model
    ŷ_t+h|t = l_t * b_t^h
    ŷ_t+h|t = l_t * b_t^h + s_f(m, h) (if seasonality = "A")
    ŷ_t+h|t = (l_t * b_t^h) * s_f(m, h) (if seasonality = "M")
    """
    points = []
    final_state = submodel.get("final_state", {})
    l = final_state.get("l", 0)
    b = final_state.get("b", 0)
    s = final_state.get("s", 0)
    for h in range(horizon):
        # each season has a different contribution
        s_i = season_contribution(s, h)
        points.append(OPERATORS[seasonality](l * pow(b, h + 1), s_i))
    return points


def Md_forecast(submodel, horizon, seasonality):
    """Computing the forecast for the trend=Md model
    ŷ_t+h|t = l_t + b_t^(phi_h)
    ŷ_t+h|t = l_t + b_t^(phi_h) + s_f(m, h) (if seasonality = "A")
    ŷ_t+h|t = (l_t + b_t^(phi_h)) * s_f(m, h) (if seasonality = "M")
    with phi_0 = phi
         phi_1 = phi + phi ^ 2
         phi_h = phi + phi^2 + ... + phi^h (for h > 1)
    """
    points = []
    final_state = submodel.get("final_state", {})
    l = final_state.get("l", 0)
    b = final_state.get("b", 0)
    s = final_state.get("s", 0)
    phi = submodel.get("phi", 0)
    phi_h = phi
    for h in range(horizon):
        # each season has a different contribution
        s_i = season_contribution(s, h)
        points.append(OPERATORS[seasonality](l * pow(b, phi_h), s_i))
        phi_h = phi_h + pow(phi, h + 2)
    return points


SUBMODELS = dict([\
    (name[0: -9].replace("_", ","), obj) for name, obj in
    inspect.getmembers(sys.modules[__name__])
    if inspect.isfunction(obj) and name.endswith('_forecast')])
