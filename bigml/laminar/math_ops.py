# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2017-2019 BigML
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

"""Activation functions and helpers in pure python

"""

import math

from bigml.laminar.constants import LARGE_EXP


def broadcast(fn):
    def broadcaster(xs):
        if len(xs) == 0:
            return []
        elif isinstance(xs[0], list):
            return [fn(xvec) for xvec in xs]
        else:
            return fn(xs)

    return broadcaster


def plus(mat, vec):
    return [[r + v for r, v in zip(row, vec)] for row in mat]


def minus(mat, vec):
    return [[r - v for r, v in zip(row, vec)] for row in mat]


def times(mat, vec):
    return [[r * v for r, v in zip(row, vec)] for row in mat]


def divide(mat, vec):
    return [[r / v for r, v in zip(row, vec)] for row in mat]


def dot(mat1, mat2):
    out_mat = []
    for row1 in mat1:
        new_row = [sum(m1 * m2 for m1, m2 in zip(row1, row2)) for row2 in mat2]
        out_mat.append(new_row)

    return out_mat


def batch_norm(X, mean, stdev, shift, scale):
    norm_vals = divide(minus(X, mean), stdev)
    return plus(times(norm_vals, scale), shift)


def sigmoid(xs):
    out_vec = []

    for x in xs:
        if x > 0:
            if x < LARGE_EXP:
                ex_val = math.exp(x)
                out_vec.append(ex_val / (ex_val + 1))
            else:
                out_vec.append(1)
        else:
            if -x < LARGE_EXP:
                out_vec.append(1 / (1 + math.exp(-x)))
            else:
                out_vec.append(0)

    return out_vec


def softplus(xs):
    return [math.log(math.exp(x) + 1) if x < LARGE_EXP else x for x in xs]


def softmax(xs):
    xmax = max(xs)
    exps = [math.exp(x - xmax) for x in xs]
    sumex = sum(exps)
    return [ex / sumex for ex in exps]


ACTIVATORS = {
    'tanh': broadcast(lambda xs: [math.tanh(x) for x in xs]),
    'sigmoid': broadcast(sigmoid),
    'softplus': broadcast(softplus),
    'relu': broadcast(lambda xs: [x if x > 0 else 0 for x in xs]),
    'softmax': broadcast(softmax),
    'identity': broadcast(lambda xs: [float(x) for x in xs])
}


def init_layers(layers):
    return [dict(layer) for layer in layers]


def destandardize(vec, v_mean, v_stdev):
    return [[v[0] * v_stdev + v_mean] for v in vec]


def to_width(mat, width):
    if width > len(mat[0]):
        ntiles = int(math.ceil(width / float(len(mat[0]))))
    else:
        ntiles = 1

    output = [(row * ntiles)[:width] for row in mat]

    return output


def add_residuals(residuals, identities):
    to_add = to_width(identities, len(residuals[0]))

    assert len(to_add[0]) == len(residuals[0])

    return [[r + v for r, v in zip(rrow, vrow)]
            for rrow, vrow in zip(residuals, to_add)]


def propagate(x_in, layers):
    last_X = identities = x_in
    for layer in layers:
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
    return last_X


def sum_and_normalize(youts, is_regression):
    ysums = []
    out_dist = []

    if is_regression:
        out_dist = sum(youts) / len(youts)
    else:
        for i, row in enumerate(youts[0]):
            sum_row = []
            for j, _ in enumerate(row):
                sum_row.append(sum([yout[i][j] for yout in youts]))

            ysums.append(sum_row)

        for ysum in ysums:
            rowsum = sum(ysum)
            out_dist.append([y / rowsum for y in ysum])

    return out_dist
