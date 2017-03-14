# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2013-2017 BigML
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

"""A ModelFields resource.

This module defines a ModelFields class to hold the information associated
to the fields of the model resource in BigML.
It becomes the starting point for the Model class, that
is used for local predictions.

"""
import logging

from bigml.util import invert_dictionary, DEFAULT_LOCALE
from bigml.fields import DEFAULT_MISSING_TOKENS
from bigml.resourcehandler import get_resource_type


LOGGER = logging.getLogger('BigML')

FIELDS_PARENT = { \
    "cluster": "clusters",
    "logisticregression": "logistic_regression"}


def check_model_structure(model, inner_key="model"):
    """Checks the model structure to see if it contains all the
    main expected keys

    """
    return (isinstance(model, dict) and 'resource' in model and
            model['resource'] is not None and
            ('object' in model and inner_key in model['object'] or
             inner_key in model))


def check_model_fields(model):
    """Checks the model structure to see whether it contains the required
    fields information

    """
    inner_key = FIELDS_PARENT.get(get_resource_type(model), 'model')
    if check_model_structure(model, inner_key):
        model = model.get('object', model)
        fields = model.get("fields", model.get(inner_key, {}).get('fields'))
        # models only need model_fields to work. The rest of resources will
        # need all fields to work
        model_fields = model.get(inner_key, {}).get( \
            'model_fields', {}).keys()
        if not model_fields:
            fields_meta = model.get('fields_meta', \
                model.get(inner_key, {}).get('fields_meta', {}))
            try:
                return fields_meta['count'] == fields_meta['total']
            except KeyError:
                # stored old models will not have the fields_meta info, so
                # we return True to avoid failing in this case
                return True
        else:
            if fields is None:
                return False
            return all([field_id in fields.keys() \
                for field_id in model_fields])
    return False


class ModelFields(object):
    """ A lightweight wrapper of the field information in the model, cluster
    or anomaly objects

    """

    def __init__(self, fields, objective_id=None, data_locale=None,
                 missing_tokens=None):
        if isinstance(fields, dict):
            try:
                self.objective_id = objective_id
                self.uniquify_varnames(fields)
                self.inverted_fields = invert_dictionary(fields)
                self.fields = {}
                self.fields.update(fields)
                self.data_locale = data_locale
                self.missing_tokens = missing_tokens
                if self.data_locale is None:
                    self.data_locale = DEFAULT_LOCALE
                if self.missing_tokens is None:
                    self.missing_tokens = DEFAULT_MISSING_TOKENS
            except KeyError:
                raise Exception("Wrong field structure.")

    def uniquify_varnames(self, fields):
        """Tests if the fields names are unique. If they aren't, a
           transformation is applied to ensure unicity.

        """
        unique_names = set([fields[key]['name'] for key in fields])
        if len(unique_names) < len(fields):
            self.transform_repeated_names(fields)

    def transform_repeated_names(self, fields):
        """If a field name is repeated, it will be transformed adding its
           column number. If that combination is also a field name, the
           field id will be added.

        """
        # The objective field treated first to avoid changing it.
        if self.objective_id:
            unique_names = [fields[self.objective_id]['name']]
        else:
            unique_names = []

        field_ids = sorted([field_id for field_id in fields
                            if field_id != self.objective_id])
        for field_id in field_ids:
            new_name = fields[field_id]['name']
            if new_name in unique_names:
                new_name = "{0}{1}".format(fields[field_id]['name'],
                                           fields[field_id]['column_number'])
                if new_name in unique_names:
                    new_name = "{0}_{1}".format(new_name, field_id)
                fields[field_id]['name'] = new_name
            unique_names.append(new_name)

    def normalize(self, value):
        """Transforms to unicode and cleans missing tokens

        """
        if isinstance(value, basestring) and not isinstance(value, unicode):
            value = unicode(value, "utf-8")
        return None if value in self.missing_tokens else value

    def filter_input_data(self, input_data, by_name=True,
                          add_unused_fields=False):
        """Filters the keys given in input_data checking against model fields.
        If `add_unused_fields` is set to True, it also
        provides information about the ones that are not used.

        """

        unused_fields = []
        new_input = {}
        if isinstance(input_data, dict):
            # remove all missing values
            for key, value in input_data.items():
                value = self.normalize(value)
                if value is None:
                    del input_data[key]

            if by_name:
                # We no longer check that the input data keys match some of
                # the dataset fields. We only remove the keys that are not
                # used as predictors in the model
                for key, value in input_data.items():
                    if key in self.inverted_fields and \
                            (self.objective_id is None or \
                             self.inverted_fields[key] != self.objective_id):
                        new_input[self.inverted_fields[key]] = value
                    else:
                        unused_fields.append(key)
            else:
                for key, value in input_data.items():
                    if key in self.fields and \
                            (self.objective_id is None or \
                             key != self.objective_id):
                        new_input[key] = value
                    else:
                        unused_fields.append(key)
            result = (new_input, unused_fields) if add_unused_fields else \
                new_input
            return result
        else:
            LOGGER.error("Failed to read input data in the expected"
                         " {field:value} format.")
            return ({}, []) if add_unused_fields else {}
