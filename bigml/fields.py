# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2012 BigML
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


class Fields(object):
    """A class to deal with BigML auto-generated ids.

    """
    def __init__(self, fields, missing_tokens=[''],
                 data_locale=DEFAULT_LOCALE, verbose=False,
                 objective_field=None, objective_field_present=False,
                 include=None):

        find_locale(data_locale, verbose)

        self.fields = fields
        self.fields_by_name = invert_dictionary(fields, 'name')
        self.fields_by_column_number = invert_dictionary(fields,
                                                         'column_number')
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
            del(self.filtered_fields[self.filtered_fields.index(objective_id)])

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
            self.row_ids = map(lambda x: self.field_id(x), headers)
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
                sys.exit("Error: field name '%s' does not exist" % key)
            return id
        elif isinstance(key, int):
            try:
                id = self.fields_by_column_number[key]
            except KeyError:
                sys.exit("Error: field column number '%s' does not exist" %
                         key)
            return id

    def field_name(self, key):
        """Returns a field name.

        """
        if isinstance(key, basestring):
            try:
                name = self.fields[key]['name']
            except KeyError:
                sys.exit("Error: field id '%s' does not exist" % key)
            return name
        elif isinstance(key, int):
            try:
                name = self.fields[self.fields_by_column_number[key]]['name']
            except KeyError:
                sys.exit("Error: field column number '%s' does not exist" %
                         key)
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
        # If objective fiels is a name or an id, retrive column number
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
                      for key, val in sorted(self.fields.items(),
                                             key=lambda k:
                                             k[1]['column_number'])]:
            out.write('[%-32s: %-16s: %-8s]\n' % (field[0],
                                                  field[1], field[2]))
            out.flush()

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
                    if (type(input_data[name]) in
                        python_map_type(self.fields[self.fields_by_name[name]]
                                        ['optype'])):
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
