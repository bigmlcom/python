import collections

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
    valid_pairs = filter(lambda x: x[1] is not None, idxs)
    outvec = np.zeros((len(idxs), len(possible_values)), dtype=np.float32)
    outvec[[v[0] for v in valid_pairs], [v[1] for v in valid_pairs]] = 1
    return outvec

def standardize(vector, mn, stdev):
    newvec = vector - mn

    if stdev > 0:
        newvec = newvec / stdev

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
