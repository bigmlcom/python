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

"""Auxiliary module to store the functions to compute time-series forecasts.

"""
import inspect
import sys


OPERATORS = {"A": lambda x, y: x + y,
             "M": lambda x, y: x * y,
             "N": lambda x, y: x}

def naive_forecast(submodel, horizon):
    """Computing the forecast for the naive model

    """
    points = []
    for _ in range(horizon):
        points.append(submodel["value"][0])
    return points


def mean_forecast(submodel, horizon):
    """Computing the forecast for the mean model

    """
    points = []
    for _ in range(horizon):
        points.append(submodel["value"][0])
    return points


def drift_forecast(submodel, horizon):
    """Computing the forecast for the drift model

    """
    points = []
    for h in range(horizon):
        points.append(submodel["value"] + submodel["slope"] * (h + 1)
    return points


def N_forecast(submodel, horizon, seasonality):
    """Computing the forecast for the trend=N models
    ŷ_t+h|t = l_t
    ŷ_t+h|t = l_t + s (if seasonality = "A")
    ŷ_t+h|t = l_t * s (if seasonality = "M")
    """
    points = []
    final_state = submodel.get("final_state", {})
    l = final_state.get("l", 0)
    s = final_state.get("s", 0)
    for _ in range(horizon):
        points.append(OPERATORS[seasonality](l, s))
    return points


def A_forecast(submodel, horizon, seasonality):
    """Computing the forecast for the trend=A models
    ŷ_t+h|t = l_t + h * b_t
    ŷ_t+h|t = l_t + h * b_t + s (if seasonality = "A")
    ŷ_t+h|t = (l_t + h * b_t) * s (if seasonality = "M")
    """
    points = []
    final_state = submodel.get("final_state", {})
    l = final_state.get("l", 0)
    b = final_state.get("b", 0)
    s = final_state.get("s", 0)
    for h in range(horizon):
        points.append(OPERATORS[seasonality](l + b * (h + 1), s))
    return points


def Ad_forecast(submodel, horizon, seasonality):
    """Computing the forecast for the trend=Ad model
    ŷ_t+h|t = l_t + phi_h * b_t
    ŷ_t+h|t = l_t + phi_h * b_t + s (if seasonality = "A")
    ŷ_t+h|t = (l_t + phi_h * b_t) * s (if seasonality = "M")
    with phi_h = phi + phi^2 + ... + phi^h
    """
    points = []
    final_state = submodel.get("final_state", {})
    l = final_state.get("l", 0)
    b = final_state.get("b", 0)
    phi = final_state.get("phi", 0)
    s = submodel.get("s", 0)
    phi_h = phi
    for h in range(horizon):
        points.append(OPERATORS[seasonality](l + phi_h * b, s))
        phi_h = phi_h + pow(phi, h + 1)
    return points


def M_forecast(submodel, horizon, seasonality):
    """Computing the forecast for the trend=M model
    ŷ_t+h|t = l_t * b_t^h
    ŷ_t+h|t = l_t * b_t^h + s (if seasonality = "A")
    ŷ_t+h|t = (l_t * b_t^h) * s (if seasonality = "M")
    """
    points = []
    final_state = submodel.get("final_state", {})
    l = final_state.get("l", 0)
    b = final_state.get("b", 0)
    s = final_state.get("s", 0)
    for h in range(horizon):
        points.append(OPERATORS[seasonality](l * pow(b, h + 1), s))
    return points


def Md_forecast(submodel, horizon, seasonality):
    """Computing the forecast for the trend=Md model
    ŷ_t+h|t = l_t + b_t^(phi_h)
    ŷ_t+h|t = l_t + b_t^(phi_h) + s (if seasonality = "A")
    ŷ_t+h|t = (l_t + b_t^(phi_h)) * s (if seasonality = "M")
    with phi_h = phi + phi^2 + ... + phi^h
    """
    points = []
    final_state = submodel.get("final_state", {})
    l = final_state.get("l", 0)
    b = final_state.get("b", 0)
    s = final_state.get("s", 0)
    phi = final_state.get("phi", 0)
    phi_h = phi
    for h in range(horizon):
        points.append(OPERATORS[seasonality](l * pow(b, phi_h), s))
        phi_h = phi_h + pow(phi, h + 1)
    return points


SUBMODELS = dict([\
    (name[0: -9].replace("_", ","), obj) for name, obj in
    inspect.getmembers(sys.modules[__name__])
    if (inspect.isfunction(obj) and name.endswith('_forecast'))])
