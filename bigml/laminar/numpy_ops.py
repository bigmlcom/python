# -*- coding: utf-8 -*-
#pylint: disable=invalid-name,missing-function-docstring
#
# Copyright 2017-2023 BigML
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

"""Activation functions and helpers in numpy

Here are most of the vector operations and helper functions we use in
numpy.
"""

import numpy as np

#pylint: disable=locally-disabled,no-name-in-module
from scipy.special import expit

from bigml.laminar.constants import LARGE_EXP, MATRIX_PARAMS, \
    VEC_PARAMS, ALPHA, LAMBDA, LEAKY_RELU_CONST


def to_numpy_array(xs):
    if isinstance(xs, np.ndarray):
        return np.copy(xs)
    return np.array(xs, dtype=np.float32)


def softplus(xs):
    x_cpy = to_numpy_array(xs)
    x_cpy[x_cpy < LARGE_EXP] = np.log(np.exp(x_cpy[x_cpy < LARGE_EXP]) + 1)
    return x_cpy


def relu(xs):
    x_cpy = to_numpy_array(xs)
    return x_cpy * (x_cpy > 0)


def softmax(xs):
    x_cpy = to_numpy_array(xs)

    shape0 = 1
    if len(x_cpy.shape) > 1:
        shape0 = x_cpy.shape[0]

    x_cpy = x_cpy.reshape(shape0, -1)

    maxes = np.amax(x_cpy, axis=1)
    maxes = maxes.reshape(maxes.shape[0], 1)

    exps = np.exp(x_cpy - maxes)
    dist = exps / np.sum(exps, axis=1).reshape((-1, 1))

    return dist


def selu(xs):
    x_cpy = to_numpy_array(xs)

    return np.where(x_cpy > 0,
                    LAMBDA * x_cpy,
                    LAMBDA * ALPHA * (np.exp(x_cpy) - 1))

def leaky_relu(xs):
    x_cpy = to_numpy_array(xs)

    return np.maximum(x_cpy, x_cpy * LEAKY_RELU_CONST)


ACTIVATORS = {
    'tanh': np.tanh,
    'sigmoid': expit,
    'softplus': softplus,
    'relu': relu,
    'softmax': softmax,
    'identity': lambda x: x,
    'linear': lambda x: x,
    'swish': lambda x: x * expit(x),
    'mish': lambda x: np.tanh(softplus(x)),
    'relu6': lambda x: np.clip(relu(x), 0, 6),
    'leaky_relu': leaky_relu,
    'selu': selu}


def plus(mat, vec):
    return mat + vec


def dot(mat1, mat2):
    output = []
    for row1 in mat1:
        new_row = []
        for row2 in mat2:
            new_row.append(np.dot(row1, row2).tolist())
        output.append(new_row)
    return output

def batch_norm(X, mean, stdev, shift, scale):
    return scale * (X - mean) / stdev + shift


def init_layer(layer, ftype=np.float64):
    out_layer = {}
    for key in layer:
        if layer[key] is not None:
            if key in MATRIX_PARAMS:
                out_layer[key] = np.array(layer[key], dtype=ftype)
            elif key in VEC_PARAMS:
                out_layer[key] = np.array(layer[key], dtype=ftype)
            else:
                out_layer[key] = layer[key]
        else:
            out_layer[key] = layer[key]

    return out_layer


def init_layers(layers):
    return [init_layer(layer) for layer in layers]


def destandardize(vec, v_mean, v_stdev):
    return vec * v_stdev + v_mean


def to_width(mat, width):
    if width > len(mat[0]):
        ntiles = int(np.ceil(width / float(len(mat[0]))))
    else:
        ntiles = 1

    return np.tile(mat, (1, ntiles))[:, :width]


def add_residuals(residuals, values):
    to_add = to_width(values, len(residuals[0]))
    return to_add + residuals


def sum_and_normalize(youts, is_regression):
    ysums = sum(youts)

    if is_regression:
        return ysums / len(youts)
    return ysums / np.sum(ysums, axis=1).reshape(-1, 1)


def propagate(x_in, layers):
    last_X = identities = to_numpy_array(x_in)

    if any(layer["residuals"] for layer in layers):
        first_identities = not any(layer["residuals"] for layer in layers[:2])
    else:
        first_identities = False

    for i, layer in enumerate(layers):
        w = layer['weights']
        m = layer['mean']
        s = layer['stdev']
        b = layer['offset']
        g = layer['scale']

        afn = layer['activation_function']

        X_dot_w = dot(last_X, w)
        if m is not None and s is not None:
            next_in = batch_norm(X_dot_w, m, s, b, g)
        else:
            next_in = plus(X_dot_w, b)

        if layer['residuals']:
            next_in = add_residuals(next_in, identities)
            last_X = ACTIVATORS[afn](next_in)
            identities = last_X
        else:
            last_X = ACTIVATORS[afn](next_in)

            if first_identities and i == 0:
                identities = last_X

    return last_X
