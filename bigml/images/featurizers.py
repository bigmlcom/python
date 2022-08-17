# -*- coding: utf-8 -*-
#
# Copyright 2022 BigML
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

"""Image Featurizers

This module defines the classes that produce the features extracted from
images in BigML. They are used in Modefields to extend the original input
data provided for local predictions.

"""

import math
import numpy as np
import os


from PIL import Image
from sensenet.models.wrappers import create_image_feature_extractor
from bigml.featurizer import Featurizer, expand_date
from bigml.constants import IMAGE

TOP_SIZE = 512
N_BINS = 16
INTENSITY_RANGE = 256
BIN_WIDTH = INTENSITY_RANGE / N_BINS
HOG_BINS = 9
HOG_BIN_WIDTH = np.pi / HOG_BINS
DECOMPS = ["horizontal", "diagonal", "vertical"]

PRETRAINED = "pretrained_cnn"
WAVELET = "wavelet_subbands"

def resize_to(image, top_size=TOP_SIZE):
    """Resizing the image to a maximum width or height """
    width, height = image.size
    if width > TOP_SIZE or height > TOP_SIZE:
        if width > height:
            ratio = height / width
            image = image.resize((TOP_SIZE , int(ratio * TOP_SIZE)),
                                 Image.BICUBIC)
        else:
            ratio = width / height
            image = image.resize((int(ratio * TOP_SIZE), TOP_SIZE),
                                  Image.BICUBIC)
    return image


def grid_coords(image_a, grid_size):
    """ getting the start and end positions for each grid """
    try:
        height, width, _ = image_a.shape
    except ValueError:
        height, width = image_a.shape
    f_grid_size = float(grid_size)
    h_step = height / f_grid_size
    w_step = width / f_grid_size
    coords = []
    for h in range(0, grid_size):
        for w in range(0, grid_size):
            h_start = int(max([0, math.floor(h * h_step)]))
            w_start = int(max([0, math.floor(w * w_step)]))
            h_end = int(min([height, math.ceil((h + 1) * h_step)]))
            w_end = int(min([width, math.ceil((w + 1) * w_step)]))
            coords.append([h_start, w_start, h_end, w_end])
    return coords


def dimensions_extractor(image_file):
    """Returns the features related to the image dimensions:
       file size, width, height, aspect ratio
    """
    file_size = os.stat(image_file).st_size
    image = Image.open(image_file)
    width, height = image.size
    aspect_ratio = width / float(height)
    return [file_size, width, height, aspect_ratio]


def average_pixels_extractor(image_file):
    """ Averaging pixels for the entire image, 3x3 and 4x4 grids
    The image passed as argument should already be resized to 512 max
    """
    image = Image.open(image_file)
    image = resize_to(image)
    image_a = np.array(image)
    avg_pixels =  [np.average(image_a[:, :, n]) for n in range(0, 3)]
    coords = grid_coords(image_a, 3)
    coords.extend(grid_coords(image_a, 4))
    for h_start, w_start, h_end, w_end in coords:
        avg_pixels.extend(
            [np.average(image_a[h_start: h_end, w_start: w_end, n])
             for n in range(0, 3)])
    return avg_pixels


def get_bin(value, bin_width):
    return math.floor(value / bin_width)


def get_luminance(image_a):
    """Getting the Y coordinate in YUV in terms of the RGB channel info"""
    r = image_a[:, :, 0]
    g = image_a[:, :, 1]
    b = image_a[:, :, 2]

    image_l = 0.299 * r + 0.587 * g + 0.114 * b
    image_l = image_l.astype('d')
    return image_l

def level_histogram_extractor(image_file):
    image = Image.open(image_file)
    image = resize_to(image)
    image_a = np.array(image)
    height, width, _ = image_a.shape
    pixels_per_channel = width * height
    output = [0] * 3 * N_BINS
    for c in range(0, 3):
        offset = N_BINS * c
        for h in range(0, height):
            for w in range(0, width):
                bin_index = get_bin(image_a[h][w][c], BIN_WIDTH)
                output[bin_index + offset] += 1
    for index, _ in enumerate(output):
        output[index] /= pixels_per_channel

    return output;


def HOG_transform(image_a):
    image_l = get_luminance(image_a)
    height, width = image_l.shape
    if height > 2 and width > 2:
        trans_image = np.empty(((height - 2), (width - 2), 2))
        trans_image.astype('d')
        for y in range(0, (height - 2)):
            for x in range(0, (width - 2)):
                py = y + 1
                px = x + 1
                x_edge = image_l[py][x] - image_l[py][px + 1]
                y_edge = image_l[y][px] - image_l[py + 1][px]

                trans_image[y][x][0] = math.sqrt(
                    x_edge * x_edge + y_edge * y_edge)

                # Convert to zero - pi radians
                if x_edge == 0:
                    if y_edge > 0:
                        trans_image[y][x][1] = np.pi
                    elif y_edge < 0:
                            trans_image[y][x][1] = 0
                    else:
                        trans_image[y][x][1] = np.nan
                else:
                    trans_image[y][x][1] = math.atan(
                        y_edge / x_edge) + (np.pi / 2);
    else:
        trans_image = np.empty((height, width, 2))
        for y in range(0, height):
            for x in range(0, width):
                trans_image[y][x][0] = 0
                trans_image[y][x][1] = np.nan

    return trans_image


def HOG_aggregate(trans_image, grid_size):

        # Laplace correction to avoid zero norm; kind of arbitrary
        features = np.ones(((grid_size * grid_size), HOG_BINS))

        bounds = grid_coords(trans_image, grid_size)
        for index, bound in enumerate(bounds):
            h_start, w_start, h_end, w_end = bound
            for y in range(h_start, h_end):
                for x in range(w_start, w_end):
                    mag = trans_image[y][x][0]
                    angle = trans_image[y][x][1]

                    if mag > 0:
                        if angle >= np.pi:
                            low = HOG_BINS - 1
                        else:
                            low = get_bin(angle, HOG_BIN_WIDTH)
                        high = (low + 1) % HOG_BINS;

                        high_weight = (
                            angle - low * HOG_BIN_WIDTH) / HOG_BIN_WIDTH
                        low_weight = 1 - high_weight

                        # Split vote between adjacent bins
                        features[index][low] += mag * low_weight
                        features[index][high] += mag * high_weight
            norm = np.linalg.norm(features[index])
            features[index] = features[index] / norm
        return features


def HOG_extractor(image_file):
    image = Image.open(image_file)
    image = image.convert('RGB')
    image = resize_to(image)
    image_a = np.array(image)
    transform = HOG_transform(image_a)
    features = HOG_aggregate(transform, 1)
    features3x3 = HOG_aggregate(transform, 3)
    features4x4 = HOG_aggregate(transform, 4)
    features_list = list(features.reshape(-1))
    features_list.extend(list(features3x3.reshape(-1)))
    features_list.extend(list(features4x4.reshape(-1)))
    return features_list


def energy_parameters(values, coords):
    if len(values) < 2 and len(values[0]) < 2:
        return np.array([values[0][0], 0])
    count = 0
    mean = 0
    sum_sq = 0
    h_start, w_start, h_end, w_end = coords

    for y in range(h_start, h_end):
        for x in range(w_start, w_end):
            new_value = values[y][x]
            count += 1
            delta1 = new_value - mean
            mean += delta1 / count
            delta2 = new_value - mean
            sum_sq += delta1 * delta2

    return np.array([mean, sum_sq / (count - 1)])


def haar1Ds(signal):
    output = np.empty((2, max([1, int(len(signal) / 2)])))

    if len(signal) > 1:
        for i in range(0, len(signal) - 1, 2):
            index = int(i / 2)
            output[0][index] = (signal[i] + signal[i + 1]) / 2
            output[1][index] = abs(signal[i] - signal[i + 1])

    else:
        output[0][0] = signal[0]
        output[1][0] = 0

    return output


def haar1D(image, vertical):
    if vertical:
        image = image.transpose()

    output = np.empty((2, len(image), max([1, int(len(image[0]) / 2)])))

    for i in range(0, len(image)):
        row_decomp = haar1Ds(image[i])
        output[0][i] = row_decomp[0]
        output[1][i] = row_decomp[1]

    if vertical:
        output = np.array([output[0].transpose(),
                           output[1].transpose()])

    return output


def haar2D(image):
    h_mean, h_detail = haar1D(image, False)
    average, vertical = haar1D(h_mean, True)
    horizontal, diagonal = haar1D(h_detail, True)

    return np.array([average, horizontal, diagonal, vertical])


def wavelet_subbands_aggregate(trans_image, grid_size):
        index = 0
        features = np.empty((((len(trans_image) - 1) * len(DECOMPS) + 1) *
            grid_size * grid_size * 2,))
        features.astype('d')
        bounds = []
        for i in range(len(trans_image)):
            bounds.append(grid_coords(trans_image[i][0], grid_size))
        for cell in range(grid_size * grid_size):
            for i in range(len(trans_image)):
                for j in range(len(trans_image[i])):
                    params = energy_parameters(
                        trans_image[i][j], bounds[i][cell])
                    features[index] = params[0]
                    features[index + 1] = params[1]

                    index += len(params)

        return features


def wavelet_subbands_transform(image_a, levels):
    image_l = get_luminance(image_a)
    height, width = image_l.shape

    output = []

    for i in range(0, levels):
        level_output = []
        decomp = haar2D(image_l)
        for j in range(0, len(DECOMPS)):
            level_output.append(decomp[j + 1])
        image_l = decomp[0];
        output.append(level_output)

    output.append([image_l])

    return output


def wavelet_subbands_extractor(image_file, levels):
    image = Image.open(image_file)
    image = image.convert('RGB')
    image = resize_to(image)
    image_a = np.array(image)
    transform = wavelet_subbands_transform(image_a, levels)
    features = wavelet_subbands_aggregate(transform, 1)
    features2x2 = wavelet_subbands_aggregate(transform, 2)
    features_list = list(features.reshape(-1))
    features_list.extend(list(features2x2.reshape(-1)))
    return features_list


IMAGE_EXTRACTORS = {
    "dimensions": dimensions_extractor,
    "average_pixels": average_pixels_extractor,
    "level_histogram": level_histogram_extractor,
    "histogram_of_gradients": HOG_extractor
}

IMAGE_PROVENANCE = list(IMAGE_EXTRACTORS.keys()) + [PRETRAINED, WAVELET]


def get_image_extractors(res_object, field_id):
    """Returns the feature extractor function for an image field"""
    extractors = []
    try:
        extracted_features = res_object.fields[field_id].get(
            "image_analysis", {}).get("extracted_features")
        for feature in extracted_features:
            if isinstance(feature, list) and feature[0] == PRETRAINED:
                _, cnn_name = feature[:]
                extractors.append(lambda x: list(
                    create_image_feature_extractor(cnn_name, None)(x))[0])
            elif isinstance(feature, list) and feature[0] == WAVELET:
                _, levels = feature[:]
                extractors.append(lambda x:
                    wavelet_subbands_extractor(x, levels))
            else:
                extractors.append(IMAGE_EXTRACTORS[feature])

    except:
        pass
    return extractors


def expand_image(res_object, parent_id, image_file):
    """ Retrieves all the values of the subfields generated from
    a parent image field

    """
    expanded = {}
    keys = res_object.fields[parent_id]["child_ids"]
    values = []
    for generator in res_object.generators[parent_id]:
        values.extend(generator(image_file))
    expanded = dict(zip(keys, values))
    return expanded


class ImageFeaturizer(Featurizer):

    def __init__(self, fields, input_fields, out_fields=None):
        self.fields = fields
        self.input_fields = input_fields
        self.subfields = {}
        self.generators = {}
        self.out_fields = self.add_subfields(out_fields)

    def _add_subfield(self, field_id, field):
        """Adding a subfield and the corresponding generator """
        parent_id = field["parent_ids"][0]
        subfield = {field_id: field["datatype"]}
        if parent_id in list(self.subfields.keys()):
            self.subfields[parent_id].update(subfield)
        else:
            parent_type = self.fields[parent_id]["optype"]
            expand_fn_list = get_image_extractors(self, parent_id) \
                if parent_type == IMAGE else [expand_date]
            self.out_fields[parent_id] = self.fields[parent_id]
            self.subfields[parent_id] = subfield
            self.generators.update({parent_id: expand_fn_list})

    def add_subfields(self, out_fields=None):
        """Adding the subfields information in the fields structure and the
        generating functions for the subfields values.
        """
        # filling out fields with preferred input fields
        fields = out_fields or self.fields
        self.out_fields = {}
        self.out_fields.update({field_id: field for field_id, field \
            in fields.items() if field_id in self.input_fields \
            and self.fields[field_id].get("preferred", True)})

        # computing the generated subfields
        subfields = {}

        for fid, finfo in list(self.out_fields.items()):
            if finfo.get('parent_optype', False) == 'datetime' or \
                finfo.get('provenance', False) in IMAGE_PROVENANCE:
                # datetime and image subfields
                self._add_subfield(fid, finfo)

        self.subfields = subfields

        return self.out_fields

    def extend_input(self, input_data):
        """Computing the values for the generated subfields and adding them
        to the original input data. Parent fields will be removed.
        """
        expanded = {}
        for f_id, value in list(input_data.items()):
            if f_id in self.generators.keys():
                if self.fields[f_id]["optype"] == IMAGE:
                    expanded.update(expand_image(self, f_id, input_data[f_id]))
                else:
                    expanded.update(
                        self.generator[f_id][0](self, f_id, input_data[f_id]))
            else:
                expanded[f_id] = value
        return expanded
