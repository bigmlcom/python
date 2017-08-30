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

def check_numeric_distribution(full_vector, moments_only):
    vector = full_vector[np.isfinite(full_vector)]
    vals, counts = np.unique(vector, return_counts=True)

    if len(vals) == 1:
        return {MEAN: float(vals[0]), STANDARD_DEVIATION: 0.0}

    elif len(vals) == 2 and not moments_only:
        return {
            ZERO: float(min(vals)),
            ONE: float(max(vals))
        }
    else:
        modeocc = np.max(counts)

        if modeocc > len(vector) * MODE_CONCENTRATION and not moments_only:
            modeval = vals[np.argmax(counts)]
            return {
                MEAN: float(modeval),
                STANDARD_DEVIATION:  float(np.std(vals))
            }
        else:
            return {
                MEAN: float(np.mean(vector)),
                STANDARD_DEVIATION:  float(np.std(vector))
            }

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

def get_spec(vector, is_numeric, moments_only):
    if is_numeric:
        spec = check_numeric_distribution(np.asarray(vector), moments_only)
        spec['type'] = NUMERIC
        return spec
    else:
        possible_values = sorted(set(v for v in vector if v is not None))
        return {'type': CATEGORICAL, 'values': possible_values}

def transform_and_get_spec(vector, is_numeric):
    spec = get_spec(vector, is_numeric, False)
    output = transform(vector, spec)

    return output, spec

def moments(amap):
    return amap[MEAN], amap[STANDARD_DEVIATION]

def bounds(amap):
    return amap[ZERO], amap[ONE]

def transform(vector, spec):
    vtype = spec['type']

    if vtype == NUMERIC:
        if STANDARD_DEVIATION in spec:
            mn, stdev = moments(spec)
            print "***"
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
    print "***", output
    return output

def preprocess_and_get_specs(columns, optypes):
    outdata = None
    outspecs = []

    for i, column in enumerate(columns):
        is_numeric = optypes[i] == NUMERIC

        if is_numeric:
            column = np.asarray(column, dtype=np.float32)

        outarray, outspec = transform_and_get_spec(column, is_numeric)
        outspec['index'] = i

        if outdata is not None:
            outdata = np.c_[outdata, outarray]
        else:
            outdata = outarray

        outspecs.append(outspec)

    return outdata, outspecs

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
