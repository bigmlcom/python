# -*- coding: utf-8 -*-
#
# Copyright 2022-2023 BigML
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

"""Miscellaneous utility functions for image processing

"""
import os
import tempfile

from PIL import Image

from bigml.constants import TEMP_DIR, TOP_IMAGE_SIZE as TOP_SIZE, DECIMALS


def resize_to(image, top_size=TOP_SIZE):
    """Resizing the image to a maximum width or height """
    width, height = image.size
    if width > top_size or height > top_size:
        if width > height:
            ratio = height / width
            image = image.resize((top_size , int(ratio * top_size)),
                                 Image.BICUBIC)
        else:
            ratio = width / height
            image = image.resize((int(ratio * top_size), top_size),
                                  Image.BICUBIC)
    return image


def to_relative_coordinates(image_file, regions_list):
    """Transforms predictions with regions having absolute pixels regions
    to the relative format used remotely and rounds to the same precision.
    """

    if regions_list:
        image_obj = Image.open(image_file)
        width, height = image_obj.size
        for index, region in enumerate(regions_list):
            [xmin, ymin, xmax, ymax] = region["box"]
            region["box"] = [round(xmin / width, DECIMALS),
                             round(ymin / height, DECIMALS),
                             round(xmax / width, DECIMALS),
                             round(ymax / height, DECIMALS)]
            region["score"] = round(region["score"], DECIMALS)
            regions_list[index] = region
    return regions_list


def remote_preprocess(image_file):
    """Emulating the preprocessing of images done in the backend to
    get closer results in local predictions
    """
    # converting to jpg
    image = Image.open(image_file)
    if not (image_file.lower().endswith(".jpg") or
            image_file.lower().endswith(".jpeg")):
        image = image.convert('RGB')
    # resizing to top size=512
    resize_to(image)
    with tempfile.NamedTemporaryFile(delete=False) as temp_fp:
        tmp_file_name = os.path.join(TEMP_DIR, "%s.jpg" % temp_fp.name)
        # compressing to 90%
        image.save(tmp_file_name, quality=90)
    return tmp_file_name
