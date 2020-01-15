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

""" Constants for Time series

"""

SUBMODELS_CODE = {"naive": \
u"""

def _naive_forecast(components, horizon):
    \"\"\"Computing the forecast for the naive model

    \"\"\"
    return _trivial_forecast(components, horizon)

""",
                  "mean": \
u"""
def _mean_forecast(components, horizon):
    \"\"\"Computing the forecast for the mean model

    \"\"\"
    return _trivial_forecast(submodel, horizon)
""",
                  "drift": \
u"""

def _drift_forecast(components, horizon):
    \"\"\"Computing the forecast for the drift model

    \"\"\"
    points = []
    for h in range(horizon):
        points.append(components["value"] + components["slope"] * (h + 1))
    return points
""",
                  "N": \
u"""

def _N_forecast(components, horizon, seasonality):
    \"\"\"Computing the forecast for the trend=N models
    ŷ_t+h|t = l_t
    ŷ_t+h|t = l_t + s_f(s, h) (if seasonality = "A")
    ŷ_t+h|t = l_t * s_f(s, h) (if seasonality = "M")
    \"\"\"
    points = []
    l = components.get(\"l\", 0)
    s = components.get(\"s\", 0)
    for h in range(horizon):
        # each season has a different contribution
        s_i = season_contribution(s, h)
        points.append(OPERATORS[seasonality](l, s_i))
    return points
""",
                  "A": \
u"""

def _A_forecast(components, horizon, seasonality):
    \"\"\"Computing the forecast for the trend=A models
    ŷ_t+h|t = l_t + h * b_t
    ŷ_t+h|t = l_t + h * b_t + s_f(s, h) (if seasonality = "A")
    ŷ_t+h|t = (l_t + h * b_t) * s_f(s,h) (if seasonality = "M")
    \"\"\"
    points = []
    l = components.get(\"l\", 0)
    b = components.get(\"b\", 0)
    s = components.get(\"s\", 0)
    for h in range(horizon):
        # each season has a different contribution
        s_i = season_contribution(s, h)
        points.append(OPERATORS[seasonality](l + b * (h + 1), s_i))
    return points
""",
                  "Ad": \
u"""

def _Ad_forecast(components, horizon, seasonality):
    \"\"\"Computing the forecast for the trend=Ad model
    ŷ_t+h|t = l_t + phi_h * b_t
    ŷ_t+h|t = l_t + phi_h * b_t + s_f(m, h) (if seasonality = "A")
    ŷ_t+h|t = (l_t + phi_h * b_t) * s_f(m, h) (if seasonality = "M")
    with phi_0 = phi
         phi_1 = phi + phi^2
         phi_h = phi + phi^2 + ... + phi^(h + 1) (for h > 0)
    \"\"\"
    points = []
    l = components.get(\"l\", 0)
    b = components.get(\"b\", 0)
    phi = components.get(\"phi\", 0)
    s = components.get(\"s\", 0)
    phi_h = phi
    for h in range(horizon):
        # each season has a different contribution
        s_i = season_contribution(s, h)
        points.append(OPERATORS[seasonality](l + phi_h * b, s_i))
        phi_h = phi_h + pow(phi, h + 2)
    return points
""",
                  "M": \
u"""

def _M_forecast(components, horizon, seasonality):
    \"\"\"Computing the forecast for the trend=M model
    ŷ_t+h|t = l_t * b_t^h
    ŷ_t+h|t = l_t * b_t^h + s_f(m, h) (if seasonality = "A")
    ŷ_t+h|t = (l_t * b_t^h) * s_f(m, h) (if seasonality = "M")
    \"\"\"
    points = []
    l = components.get(\"l\", 0)
    b = components.get(\"b\", 0)
    s = components.get(\"s\", 0)
    for h in range(horizon):
        # each season has a different contribution
        s_i = season_contribution(s, h)
        points.append(OPERATORS[seasonality](l * pow(b, h + 1), s_i))
    return points
""",
                  "Md": \
u"""

def _Md_forecast(components, horizon, seasonality):
    \"\"\"Computing the forecast for the trend=Md model
    ŷ_t+h|t = l_t + b_t^(phi_h)
    ŷ_t+h|t = l_t + b_t^(phi_h) + s_f(m, h) (if seasonality = "A")
    ŷ_t+h|t = (l_t + b_t^(phi_h)) * s_f(m, h) (if seasonality = "M")
    with phi_0 = phi
         phi_1 = phi + phi ^ 2
         phi_h = phi + phi^2 + ... + phi^h (for h > 1)
    \"\"\"
    points = []
    l = components.get(\"l\", 0)
    b = components.get(\"b\", 0)
    s = components.get(\"s\", 0)
    phi = components.get(\"phi\", 0)
    phi_h = phi
    for h in range(horizon):
        # each season has a different contribution
        s_i = season_contribution(s, h)
        points.append(OPERATORS[seasonality](l * pow(b, phi_h), s_i))
        phi_h = phi_h + pow(phi, h + 2)
    return points

"""}

TRIVIAL_MODEL = \
u"""
def _trivial_forecast(components, horizon):
    \"\"\"Computing the forecast for the trivial models

    \"\"\"
    points = []
    submodel_points = components[\"value\"]
    period = len(submodel_points)
    if period > 1:
        # when a period is used, the points in the model are repeated
        for h in range(horizon):
            points.append(submodel_points[h % period])
    else:
        for _ in range(horizon):
            points.append(submodel_points[0])
    return points


"""

SEASONAL_CODE = \
"""
OPERATORS = {\"A\": lambda x, s: x + s,
             \"M\": lambda x, s: x * s,
             \"N\": lambda x, s: x}


def season_contribution(s_list, step):
    \"\"\"Chooses the seasonal contribution from the list in the period

    s_list: The list of contributions per season
    step: The actual prediction step

    \"\"\"
    if isinstance(s_list, list):
        period = len(s_list)
        index = abs(- period + 1 + step % period)
        return s_list[index]
    else:
        return 0


"""

FORECAST_FUNCTION = \
u"""

def forecast(field, model_name, horizon=50):
    \"\"\"Forecast using the user-given model type and horizon

    \"\"\"
    components = COMPONENTS.get(field, {}).get(model_name)
    if model_name:
        if \",\" in model_name:
            _, trend, seasonality = model_name.split(",")
            return MODELS[trend](components, horizon, seasonality)
        else:
            return MODELS[model_name](components, horizon)
    else:
        return {}
"""

USAGE_DOC = \
u"""\"\"\"Local forecast for BigML's Time Series %s.

Time Series Forecast by BigML - Machine Learning Made Easy

Add this code to your project and use the `forecast` function to make
your forecasts:

    forecast(\"%s\", "naive", horizon=10)

where the first parameter is the field to forecast, the second is the name
of the model to use and the third the number of points to generate.
\"\"\"

"""
