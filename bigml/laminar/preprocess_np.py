import math
import numpy as np

from bigml.laminar.constants import NUMERIC, CATEGORICAL


MODE_CONCENTRATION = 0.1
MODE_STRENGTH = 3

MEAN = "mean"
STANDARD_DEVIATION = "stdev"

ZERO = "zero_value"
ONE = "one_value"

def index(alist, value):
    try:
        return alist.index(value)
    except ValueError:
        return None

def one_hot(vector, possible_values):
    idxs = list(enumerate(index(possible_values, v) for v in vector))
    valid_pairs = [x for x in idxs if x[1] is not None]
    outvec = np.zeros((len(idxs), len(possible_values)), dtype=np.float32)
    for v in valid_pairs:
        outvec[v[0], v[1]] = 1
    return outvec

def standardize(vector, mn, stdev):
    newvec = vector - mn

    if stdev > 0:
        newvec = newvec / stdev

    fill_dft = lambda x: 0.0 if math.isnan(x) else x
    newvec = np.vectorize(fill_dft)(newvec)
    return newvec

def binarize(vector, zero, one):
    if one == 0.0:
        vector[vector == one] = 1.0
        vector[(vector != one) & (vector != 1.0)] = 0.0
    else:
        vector[vector != one] = 0.0
        vector[vector == one] = 1.0

    return vector

def moments(amap):
    return amap[MEAN], amap[STANDARD_DEVIATION]

def bounds(amap):
    return amap[ZERO], amap[ONE]

def transform(vector, spec):
    vtype = spec['type']

    if vtype == NUMERIC:
        if STANDARD_DEVIATION in spec:
            mn, stdev = moments(spec)
            output = standardize(vector, mn, stdev)
        elif ZERO in spec:
            low, high = bounds(spec)
            output = binarize(vector, low, high)
        else:
            raise ValueError("'%s' is not a valid numeric spec!" % str(spec))
    elif vtype == CATEGORICAL:
        output = one_hot(vector, spec['values'])
    else:
        raise ValueError("'%s' is not a valid spec type!" % vtype)
    return output


def tree_predict(tree, point):
    node = tree[:]

    while node[-1] is not None:
        if point[node[0]] <= node[1]:
            node = node[2]
        else:
            node = node[3]

    return node[0]


def get_embedding(X, model):
    if isinstance(model, list):
        preds = None
        for tree in model:
            tree_preds = []
            for row in X:
                tree_preds.append(tree_predict(tree, row))

            if preds is None:
                preds = np.array(tree_preds, dtype='float64')
            else:
                preds += np.array(tree_preds, dtype='float64')

        if len(preds[0]) > 1:
            preds /= preds.sum(axis=1, keepdims=True)
        else:
            preds /= len(model)

        return preds
    else:
        raise ValueError("Model is unknown type!")


def tree_transform(X, trees):
    outdata = None

    for feature_range, model in trees:
        sidx, eidx = feature_range
        inputs = X[:, sidx:eidx]
        outarray = get_embedding(inputs, model)
        if outdata is not None:
            outdata = np.c_[outdata, outarray]
        else:
            outdata = outarray
    return np.c_[outdata, X]


def preprocess(columns, specs):
    outdata = None

    for spec in specs:
        column = columns[spec['index']]

        if spec['type'] == NUMERIC:
            column = np.asarray(column, dtype=np.float32)

        outarray = transform(column, spec)
        if outdata is not None:
            outdata = np.c_[outdata, outarray]
        else:
            outdata = outarray

    return outdata
