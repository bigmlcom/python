"""Activation functions and helpers in pure python

Here are most of the vector operations and helper functions we use in
python.  We've encapsulated these here as there's a known bug that
causes numpy to hang when using Apple accelerate in some cases.  If
we're on a non-apple machine, we use numpy for the vector operations,
as shown in numpy_ops.py.

"""

import math

import numpy as np

from bigml.laminar.constants import LARGE_EXP, EPSILON

def mean(xs):
    return float(sum(xs)) / len(xs)

def broadcast(fn):
    def broadcaster(xs):
        if len(xs) == 0:
            return []
        elif isinstance(xs[0], list):
            return [fn(xvec) for xvec in xs]
        elif isinstance(xs[0], np.ndarray):
            return [fn(xvec) for xvec in xs.tolist()]
        else:
            return fn(xs)

    return broadcaster

def argmax_single(xs):
    max_val = float('-inf')
    max_idx = None

    for i, x in enumerate(xs):
        if x >= max_val:
            max_val = x
            max_idx = i

    return max_idx

argmax = broadcast(argmax_single)

def std(xs):
    n = 0
    mean = 0.0
    sum_sq = 0.0

    for x in xs:
        n += 1
        delta1 = x - mean
        mean += delta1 / n
        delta2 = x - mean
        sum_sq += delta1 * delta2

    if n < 2:
        return float('nan')
    else:
        return math.sqrt(sum_sq / (n - 1))

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
                ex_val = math.exp(x);
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
    'ReLU': broadcast(lambda xs: [x if x > 0 else 0 for x in xs]),
    'softmax': broadcast(softmax),
    'identity': broadcast(lambda xs: [float(x) for x in xs])
}

def transpose(mat):
    out_mat = []

    for idx, _ in enumerate(mat[0]):
        column = [row[idx] for row in mat]
        out_mat.append(column)

    return out_mat

def init_layers(layers):
    return [dict(layer) for layer in layers]

def sum_and_normalize(youts, classify):
    ysums = sum(youts)

    if classify:
        return ysums / np.sum(ysums, axis=1).reshape(-1, 1)
    else:
        return ysums / len(youts)

def destandardize(vec, v_mean, v_stdev):
    return [[v[0] * v_stdev + v_mean] for v in vec]

def to_width(mat, width):
    if width > len(mat[0]):
        ntiles = int(math.ceil(width / float(len(mat[0]))))
    else:
        ntiles = 1

    if isinstance(mat, np.ndarray):
        output = [(row * ntiles)[:width] for row in mat.tolist()]
    else:
        output = [(row * ntiles)[:width] for row in mat]

    return output

def add_residuals(residuals, identities):
    to_add = to_width(identities, len(residuals[0]))

    assert len(to_add[0]) == len(residuals[0])

    return [[r + v for r, v in zip(rrow, vrow)]
            for rrow, vrow in zip(residuals, to_add)]
