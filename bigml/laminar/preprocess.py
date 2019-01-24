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

"""Auxiliary functions for preprocessing

"""

import math

from copy import deepcopy

from bigml.laminar.constants import NUMERIC, CATEGORICAL

MEAN = "mean"
STANDARD_DEVIATION = "stdev"

ZERO = "zero_value"
ONE = "one_value"


def dtype_ok(dtype_fn):
    return dtype_fn is not None and dtype_fn in [int, float]


def np_zeros(x_dim, y_dim, dtype_fn=None):
    value = "0"
    try:
        if dtype_ok(dtype_fn):
            value = dtype_fn(value)
    except ValueError:
        pass
    array = []
    for i in range(x_dim):
        array.append([])
        for _ in range(y_dim):
            array[i].append(value)
    return array


def np_asarray(array, dtype_fn=None):
    new_array = deepcopy(array)
    if not isinstance(array, list):
        new_array = [item for item in new_array]
    try:
        new_array = ['nan' if item is None else item for item in new_array]
        if dtype_ok(dtype_fn):
            new_array = [dtype_fn(item) for item in new_array]
    except (ValueError, NameError):
        pass
    return new_array


def np_c_(array_a, array_c):
    if array_a in [None, []]:
        return [array_c]

    new_array = deepcopy(array_a)
    new_array[0].extend(array_c)

    return new_array


def v_index(alist, value):
    try:
        return alist.index(value)
    except ValueError:
        return None

def one_hot(vector, possible_values):
    idxs = list(enumerate(v_index(possible_values, v) for v in vector[0]))
    valid_pairs = [x for x in idxs if x[1] is not None]
    outvec = np_zeros(len(idxs), len(possible_values), dtype_fn=float)
    for i, j in valid_pairs:
        outvec[i][j] = 1

    return outvec

def standardize(vector, mean, stdev):
    newvec = [component - mean for component in vector]

    if stdev > 0:
        newvec = [component / stdev for component in newvec]

    for index, component in enumerate(newvec):
        newvec[index] = 0.0 if math.isnan(component) else component
    return newvec

def binarize(vector, zero, one):
    for index, value in enumerate(vector):
        if one == 0.0:
            if value == one:
                vector[index] = 1.0
            if value != one and value != 1.0:
                vector[index] = 0.0
        else:
            if value != one:
                vector[index] = 0.0
            if value == one:
                vector[index] = 1.0

    return vector

def moments(amap):
    return amap[MEAN], amap[STANDARD_DEVIATION]

def bounds(amap):
    return amap[ZERO], amap[ONE]

def transform(vector, spec):
    vtype = spec['type']

    if vtype == NUMERIC:
        if STANDARD_DEVIATION in spec:
            mean, stdev = moments(spec)
            output = standardize(vector, mean, stdev)
        elif ZERO in spec:
            low, high = bounds(spec)
            output = binarize(vector, low, high)
        else:
            raise ValueError("'%s' is not a valid numeric spec!" % str(spec))
    elif vtype == CATEGORICAL:
        output = one_hot(vector, spec['values'])[0]
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
                preds = np_asarray(tree_preds)[0]
            else:
                for index, pred in enumerate(preds):
                    preds[index] += np_asarray(tree_preds)[0][index]

        if preds and len(preds) > 1:
            norm = sum(preds)
            preds = [pred / float(norm) for pred in preds]
        else:
            preds = [pred / float(len(model)) for pred in preds]

        return [preds]
    else:
        raise ValueError("Model is unknown type!")


def tree_transform(X, trees):
    outdata = None

    for feature_range, model in trees:
        sidx, eidx = feature_range
        inputs = X[:]
        for index, row in enumerate(inputs):
            inputs[index] = row[sidx:eidx]
        outarray = get_embedding(inputs, model)
        if outdata is not None:
            outdata = np_c_(outdata, outarray[0])
        else:
            outdata = outarray
    return np_c_(outdata, X[0])


def preprocess(columns, specs):
    outdata = None

    for spec in specs:
        column = [columns[spec['index']]]

        if spec['type'] == NUMERIC:
            column = np_asarray(column, dtype_fn=float)
        outarray = transform(column, spec)
        if outdata is not None:
            outdata = np_c_(outdata, outarray)
        else:
            outdata = [outarray]
    return outdata
