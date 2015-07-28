# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2012-2015 BigML
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

"""A class to deal with the fields of a resource.

This module helps to map between ids, names, and column_numbers in the
fields of source, dataset, or model. Also to validate your input data
for predictions or to list all the fields from a resource.

from bigml.api import BigML
from bigml.fields import Fields

api = BigML()

source = api.get_source("source/50a6bb94eabcb404d3000174")
fields = Fields(source['object']['fields'])

dataset = api.get_dataset("dataset/50a6bb96eabcb404cd000342")
fields = Fields(dataset['object']['fields'])

# Note that the fields in a model come one level deeper
model = api.get_model("model/50a6bbac035d0706db0008f8")
fields = Fields(model['object']['model']['fields'])

prediction = api.get_prediction("prediction/50a69688035d0706dd00044d")
fields =  Fields(prediction['object']['fields'])


"""
import sys
import locale

from bigml.util import invert_dictionary, python_map_type, find_locale
from bigml.util import DEFAULT_LOCALE
from bigml.api import get_resource_type

SOURCE_TYPE = 'source'
DATASET_TYPE = 'dataset'
PREDICTION_TYPE = 'prediction'
MODEL_TYPE = 'model'
CLUSTER_TYPE = 'cluster'
ANOMALY_TYPE = 'anomaly'
SAMPLE_TYPE = 'sample'

RESOURCES_WITH_FIELDS = [SOURCE_TYPE, DATASET_TYPE, MODEL_TYPE,
                         PREDICTION_TYPE, CLUSTER_TYPE, ANOMALY_TYPE,
                         SAMPLE_TYPE]
DEFAULT_MISSING_TOKENS = ["", "N/A", "n/a", "NULL", "null", "-", "#DIV/0",
                          "#REF!", "#NAME?", "NIL", "nil", "NA", "na",
                          "#VALUE!", "#NULL!", "NaN", "#N/A", "#NUM!", "?"]


def get_fields_structure(resource):
    """Returns the field structure for a resource, its locale and
       missing_tokens

    """
    try:
        resource_type = get_resource_type(resource)
    except ValueError:
        raise ValueError("Unknown resource structure")

    if resource_type in RESOURCES_WITH_FIELDS:
        # locale and missing tokens
        if resource_type == SOURCE_TYPE:
            resource_locale = resource['object']['source_parser']['locale']
            missing_tokens = resource['object'][
                'source_parser']['missing_tokens']
        else:
            resource_locale = resource['object'].get('locale', DEFAULT_LOCALE)
            missing_tokens = resource['object'].get('missing_tokens',
                                                    DEFAULT_MISSING_TOKENS)
        # fields structure
        if resource_type in [MODEL_TYPE, ANOMALY_TYPE]:
            fields = resource['object']['model']['fields']
        elif resource_type == CLUSTER_TYPE:
            fields = resource['object']['clusters']['fields']
        elif resource_type == CORRELATIONS_TYPE:
            fields = resource['object']['correlations']['fields']
        elif resource_type == TESTS_TYPE:
            fields = resource['object']['tests']['fields']
        elif resource_type == SAMPLE_TYPE:
            fields = dict([(field['id'], field) for field in
                           resource['object']['sample']['fields']])
        else:
            fields = resource['object']['fields']
        return fields, resource_locale, missing_tokens
    else:
        return None, None, None


class Fields(object):
    """A class to deal with BigML auto-generated ids.

    """
    def __init__(self, resource_or_fields, missing_tokens=None,
                 data_locale=None, verbose=False,
                 objective_field=None, objective_field_present=False,
                 include=None):

        # The constructor can be instantiated with resources or a fields
        # structure. The structure is checked and fields structure is returned
        # if a resource type is matched.
        try:
            resource_info = get_fields_structure(resource_or_fields)
            (self.fields,
             resource_locale,
             resource_missing_tokens) = resource_info
            if data_locale is None:
                data_locale = resource_locale
            if missing_tokens is None:
                if resource_missing_tokens:
                    missing_tokens = resource_missing_tokens
        except ValueError:
            # If the resource structure is not in the expected set, fields
            # structure is assumed
            self.fields = resource_or_fields
            if data_locale is None:
                data_locale = DEFAULT_LOCALE
            if missing_tokens is None:
                missing_tokens = DEFAULT_MISSING_TOKENS
        if self.fields is None:
            raise ValueError("No fields structure was found.")
        self.fields_by_name = invert_dictionary(self.fields, 'name')
        self.fields_by_column_number = invert_dictionary(self.fields,
                                                         'column_number')
        find_locale(data_locale, verbose)
        self.missing_tokens = missing_tokens
        self.fields_columns = sorted(self.fields_by_column_number.keys())
        # Ids of the fields to be included
        self.filtered_fields = (self.fields.keys() if include is None
                                else include)
        # To be updated in update_objective_field
        self.row_ids = None
        self.headers = None
        self.objective_field = None
        self.objective_field_present = None
        self.filtered_indexes = None
        self.update_objective_field(objective_field, objective_field_present)

    def update_objective_field(self, objective_field, objective_field_present,
                               headers=None):
        """Updates objective_field and headers info

            Permits to update the objective_field, objective_field_present and
            headers info from the constructor and also in a per row basis.
        """
        # If no objective field, select the last column, else store its column
        if objective_field is None:
            self.objective_field = self.fields_columns[-1]
        elif isinstance(objective_field, basestring):
            self.objective_field = self.field_column_number(objective_field)
        else:
            self.objective_field = objective_field

        # If present, remove the objective field from the included fields
        objective_id = self.field_id(self.objective_field)
        if objective_id in self.filtered_fields:
            del self.filtered_fields[self.filtered_fields.index(objective_id)]

        self.objective_field_present = objective_field_present
        if headers is None:
            # The row is supposed to contain the fields sorted by column number
            self.row_ids = [item[0] for item in
                            sorted(self.fields.items(),
                                   key=lambda x: x[1]['column_number'])
                            if objective_field_present or
                            item[1]['column_number'] != self.objective_field]
            self.headers = self.row_ids
        else:
            # The row is supposed to contain the fields as sorted in headers
            self.row_ids = map(self.field_id, headers)
            self.headers = headers
        # Mapping each included field to its correspondent index in the row.
        # The result is stored in filtered_indexes.
        self.filtered_indexes = []
        for field in self.filtered_fields:
            try:
                index = self.row_ids.index(field)
                self.filtered_indexes.append(index)
            except ValueError:
                continue

    def field_id(self, key):
        """Returns a field id.

        """

        if isinstance(key, basestring):
            try:
                id = self.fields_by_name[key]
            except KeyError:
                raise ValueError("Error: field name '%s' does not exist" % key)
            return id
        elif isinstance(key, int):
            try:
                id = self.fields_by_column_number[key]
            except KeyError:
                raise ValueError("Error: field column number '%s' does not"
                                 " exist" % key)
            return id

    def field_name(self, key):
        """Returns a field name.

        """
        if isinstance(key, basestring):
            try:
                name = self.fields[key]['name']
            except KeyError:
                raise ValueError("Error: field id '%s' does not exist" % key)
            return name
        elif isinstance(key, int):
            try:
                name = self.fields[self.fields_by_column_number[key]]['name']
            except KeyError:
                raise ValueError("Error: field column number '%s' does not"
                                 " exist" % key)
            return name

    def field_column_number(self, key):
        """Returns a field column number.

        """
        try:
            return self.fields[key]['column_number']
        except KeyError:
            return self.fields[self.fields_by_name[key]]['column_number']

    def len(self):
        """Returns the number of fields.

        """
        return len(self.fields)

    def pair(self, row, headers=None,
             objective_field=None, objective_field_present=None):
        """Pairs a list of values with their respective field ids.

            objective_field is the column_number of the objective field.

           `objective_field_present` must be True is the objective_field column
           is present in the row.

        """
        # Try to get objective field form Fields or use the last column
        if objective_field is None:
            if self.objective_field is None:
                objective_field = self.fields_columns[-1]
            else:
                objective_field = self.objective_field
        # If objective fields is a name or an id, retrive column number
        if isinstance(objective_field, basestring):
            objective_field = self.field_column_number(objective_field)

        # Try to guess if objective field is in the data by using headers or
        # comparing the row length to the number of fields
        if objective_field_present is None:
            if headers:
                objective_field_present = (self.field_name(objective_field) in
                                           headers)
            else:
                objective_field_present = len(row) == self.len()

        # If objective field, its presence or headers have changed, update
        if (objective_field != self.objective_field or
                objective_field_present != self.objective_field_present or
                (headers is not None and headers != self.headers)):
            self.update_objective_field(objective_field,
                                        objective_field_present, headers)

        row = map(self.normalize, row)
        return self.to_input_data(row)

    def list_fields(self, out=sys.stdout):
        """Lists a description of the fields.

        """
        for field in [(val['name'], val['optype'], val['column_number'])
                      for _, val in sorted(self.fields.items(),
                                           key=lambda k:
                                           k[1]['column_number'])]:
            out.write('[%-32s: %-16s: %-8s]\n' % (field[0],
                                                  field[1], field[2]))
            out.flush()

    def preferred_fields(self):
        """Returns fields where attribute preferred is set to True or where
           it isn't set at all.

        """
        return {key: field for key, field in self.fields.iteritems()
                if (not 'preferred' in field) or field['preferred']}

    def validate_input_data(self, input_data, out=sys.stdout):
        """Validates whether types for input data match types in the
        fields definition.

        """
        if isinstance(input_data, dict):
            for name in input_data:
                if name in self.fields_by_name:
                    out.write('[%-32s: %-16s: %-16s: ' %
                              (name, type(input_data[name]),
                               self.fields[self.fields_by_name[name]]
                               ['optype']))
                    if (type(input_data[name]) in python_map_type(self.fields[
                            self.fields_by_name[name]]['optype'])):
                        out.write('OK\n')
                    else:
                        out.write('WRONG\n')
                else:
                    out.write("Field '%s' does not exist\n" % name)
        else:
            out.write("Input data must be a dictionary")

    def normalize(self, value):
        """Transforms to unicode and cleans missing tokens

        """
        if not isinstance(value, unicode):
            value = unicode(value, "utf-8")
        return None if value in self.missing_tokens else value

    def to_input_data(self, row):
        """Builds dict with field, value info only for the included headers

        """
        pair = []
        for index in self.filtered_indexes:
            pair.append((self.headers[index], row[index]))
        return dict(pair)

    def missing_counts(self):
        """Returns the ids for the fields that contain missing values

        """
        summaries = [(field_id, field.get('summary', {}))
                     for field_id, field in self.fields.items()]
        if len(summaries) == 0:
            raise ValueError("The structure has not enough information "
                             "to extract the fields containing missing values."
                             "Only datasets and models have such information. "
                             "You could retry the get remote call "
                             " with 'limit=-1' as query string.")

        return dict([(field_id, summary.get('missing_count', 0))
                     for field_id, summary in summaries
                     if summary.get('missing_count', 0) > 0])

    def stats(self, field_name):
        """Returns the summary information for the field

        """
        field_id = self.field_id(field_name)
        summary = self.fields[field_id].get('summary', {})
        return summary
