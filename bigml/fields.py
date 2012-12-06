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

from bigml.util import invert_dictionary, map_type
from bigml.util import DEFAULT_LOCALE, WINDOWS_DEFAULT_LOCALE
from bigml.util import python_map_type


class Fields(object):
    """A class to deal with BigML auto-generated ids.

    """
    def __init__(self, fields, missing_tokens=[''],
                 data_locale=DEFAULT_LOCALE):
        new_locale = None
        try:
            new_locale = locale.setlocale(locale.LC_ALL, data_locale)
        except:
            pass
        if new_locale is None:
            try:
                new_locale = locale.setlocale(locale.LC_ALL, DEFAULT_LOCALE)
            except:
                pass
        if new_locale is None:
            try:
                new_locale = locale.setlocale(locale.LC_ALL,
                                              WINDOWS_DEFAULT_LOCALE)
            except:
                pass
        if new_locale is None:
            new_locale = locale.setlocale(locale.LC_ALL, '')

        self.fields = fields
        self.fields_by_name = invert_dictionary(fields, 'name')
        self.fields_by_column_number = invert_dictionary(fields,
                                                         'column_number')
        self.missing_tokens = missing_tokens

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
        """Returns the number of fields."

        """
        return len(self.fields)

    def pair(self, row, headers=None,
             objective_field=None, objective_field_present=None):
        """Pairs a list of values with their respective field ids.

            objective_field is the column_number of the objective field.

           `objective_field_present` must be True is the objective_field column
           is present in the row.

        """

        if objective_field is None:
            objective_field = sorted(self.fields_by_column_number.keys())[-1]

        fields_names = [self.fields[self.field_id(i)]['name'] for i in
                        sorted(self.fields_by_column_number.keys())
                        if i != objective_field]

        pair = {}

        if headers:
            if not isinstance(objective_field, basestring):
                objective_field = self.field_name(objective_field)
            if objective_field_present is None:
                objective_field_present = objective_field in headers
            for index in range(len(row)):
                if index < len(row) and not row[index] in self.missing_tokens:
                    if (objective_field_present and
                            headers[index] == objective_field):
                        continue
                    field = self.fields[self.fields_by_name[headers[index]]]
                    row[index] = self.strip_affixes(row[index], field)
                    try:
                        pair.update({headers[index]:
                                     map_type(field['optype'])(row[index])})
                    except:
                        message = (u"Mismatch input data type in field "
                                   u"\"%s\" for value %s. The expected "
                                   u"fields are: \n%s" %
                                   (field['name'],
                                    row[index],
                                    ",".join(fields_names))).encode("utf-8")
                        raise Exception(message)
        else:
            if isinstance(objective_field, basestring):
                objective_field = self.field_column_number(objective_field)
            if objective_field_present is None:
                objective_field_present = len(row) == self.len()
            column_numbers = sorted(self.fields_by_column_number.keys())
            index = 0
            for column_number in column_numbers:
                if index < len(row) and not row[index] in self.missing_tokens:
                    if column_number == objective_field:
                        if objective_field_present:
                            index += 1
                        continue

                    field = self.fields[self.field_id(column_number)]
                    row[index] = self.strip_affixes(row[index], field)
                    try:
                        pair.update({self.field_id(column_number):
                                    map_type(field['optype'])(row[index])})
                    except:
                        message = (u"Mismatch input data type in field "
                                   u"\"%s\" for value %s. The expected "
                                   u"fields are: \n%s" %
                                   (field['name'],
                                    row[index],
                                    ",".join(fields_names))).encode("utf-8")
                        raise Exception(message)
                index += 1

        return pair

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

    def strip_affixes(self, value, field):
        """Strips prefixes and suffixes if present

        """
        value = unicode(value, "utf-8")
        if 'prefix' in field and value.startswith(field['prefix']):
            value = value[len(field['prefix']):]
        if 'suffix' in field and value.endswith(field['suffix']):
            value = value[0:-len(field['suffix'])]
        return value
