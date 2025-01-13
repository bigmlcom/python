# -*- coding: utf-8 -*-
#
# Copyright 2022-2025 BigML
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

"""A Featurizer to generate features for composed fields.

This module defines a Featurizer class to hold the information associated
to the subfields derived from datetime fields.
It is used for local predictions.

"""
from bigml_chronos import chronos
from bigml.constants import DATETIME


DATE_FNS = {
    "day-of-month": lambda x: x.day,
    "day-of-week": lambda x: x.weekday() + 1,
    "millisecond": lambda x: x.microsecond / 1000}

IMAGE_PROVENANCE = ["dimensions", "average_pixels", "level_histogram",
    "histogram_of_gradients", "pretrained_cnn", "wavelet_subbands"]

def expand_date(res_object, parent_id, date):
    """ Retrieves all the values of the subfields generated from
    a parent datetime field

    """
    expanded = {}
    timeformats = res_object.fields[parent_id].get('time_formats', {})
    try:
        parsed_date = chronos.parse(date, format_names=timeformats)
    except ValueError:
        return {}
    for fid, ftype in list(res_object.subfields[parent_id].items()):
        date_fn = DATE_FNS.get(ftype)
        if date_fn is not None:
            expanded.update({fid: date_fn(parsed_date)})
        else:
            expanded.update({fid: getattr(parsed_date, ftype)})
    return expanded


class Featurizer:
    """A class to generate the components derived from a composed field """

    def __init__(self, fields, input_fields, selected_fields=None,
                 preferred_only=True):
        self.fields = fields
        self.input_fields = input_fields
        self.subfields = {}
        self.generators = {}
        self.preferred_only = preferred_only
        self.selected_fields = self.add_subfields(
            selected_fields, preferred_only=preferred_only)

    def add_subfields(self, selected_fields=None, preferred_only=True):
        """Adding the subfields information in the fields structure and the
        generating functions for the subfields values.
        """
        # filling preferred fields with preferred input fields
        fields = selected_fields or self.fields

        if selected_fields is None:
            selected_fields = {}
            selected_fields.update({field_id: field for field_id, field \
                in fields.items() if field_id in self.input_fields \
                and (not preferred_only or self.fields[field_id].get(
                "preferred", True))})

        # computing the subfields generated from parsing datetimes
        for fid, finfo in list(selected_fields.items()):

            # datetime subfields
            if finfo.get('parent_optype', False) == DATETIME:
                parent_id = finfo["parent_ids"][0]
                subfield = {fid: finfo["datatype"]}
                if parent_id in list(self.subfields.keys()):
                    self.subfields[parent_id].update(subfield)
                else:
                    selected_fields[parent_id] = self.fields[parent_id]
                    self.subfields[parent_id] = subfield
                    self.generators.update({parent_id: expand_date})
            elif finfo.get('provenance', False) in IMAGE_PROVENANCE:
                raise ValueError("This model uses image-derived fields. "
                                 "Please, use the pip install bigml[images] "
                                 "option to install the libraries required "
                                 "for local predictions in this case.")

        return selected_fields

    def extend_input(self, input_data):
        """Computing the values for the generated subfields and adding them
        to the original input data. Parent fields will be removed if the
        `preferred_only` option is set, as they are not used in models.
        However, the `preferred_only` option set to False will keep them,
        allowing to be used as generators in other transformations.
        """
        extended = {}
        for f_id, value in list(input_data.items()):
            if f_id in self.subfields:
                if not self.preferred_only:
                    extended[f_id] = value
                extended.update(self.generators[f_id](self, f_id, value))
            else:
                extended[f_id] = value
        return extended
