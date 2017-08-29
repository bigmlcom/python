"""Activation functions and helpers in numpy

Here are most of the vector operations and helper functions we use in
numpy.  We've encapsulated these here as there's a known bug that
causes numpy to hang when using Apple accelerate in some cases.  If
we're on an apple machine, we use pure python for the vector
operations, as shown in math_ops.py.

"""

import numpy as np

from scipy.special import expit

from bigml.laminar.constants import LARGE_EXP, EPSILON, MATRIX_PARAMS, \
    VEC_PARAMS

def to_numpy_array(xs):
    if isinstance(xs, np.ndarray):
        return np.copy(xs)
    else:
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

ACTIVATORS = {
    'tanh': np.tanh,
    'sigmoid': expit,
    'softplus': softplus,
    'ReLU': relu,
    'softmax': softmax,
    'identity': lambda x: x
}

def plus(mat, vec):
    return mat + vec

def dot(mat1, mat2):
    return np.dot(mat1, mat2)

def batch_norm(X, mean, stdev, shift, scale):
    return scale * (X - mean) / stdev + shift

def argmax(mat):
    return np.argmax(mat, 1)

def init_layer(layer, ftype=np.float64):
    out_layer = {}
    for key in layer:
        if layer[key] is not None:
            if key in MATRIX_PARAMS:
                out_layer[key] = np.array(layer[key], dtype=ftype).T
            elif key in VEC_PARAMS:
                out_layer[key] = np.array(layer[key], dtype=ftype)
            else:
                out_layer[key] = layer[key]
        else:
            out_layer[key] = layer[key]

    return out_layer

def init_layers(layers):
    return [init_layer(layer) for layer in layers]

def sum_and_normalize(youts, classify):
    ysums = sum(youts)

    if classify:
        return ysums / np.sum(ysums, axis=1).reshape(-1, 1)
    else:
        return ysums / len(youts)

def destandardize(vec, v_mean, v_stdev):
    return vec * v_stdev + v_mean

def to_width(mat, width):
    if width > len(mat[0]):
        ntiles = int(np.ceil(width / float(len(mat[0]))))
    else:
        ntiles = 1

    return np.tile(mat, (1, ntiles))[:,:width]

def add_residuals(residuals, values):
    to_add = to_width(values, len(residuals[0]))
    return to_add + residuals
