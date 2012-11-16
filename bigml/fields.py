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
fields of source, dataset, or model.

"""
import sys
import locale
from bigml.util import invert_dictionary
from bigml.util import DEFAULT_LOCALE
from bigml.util import LOCALE_MAP

TYPE_MAP = {
    "categorical": str,
    "numeric": locale.atof,
    "text": str
}


def map_type(value):
    """Maps a BigML type to a Python type.

    """
    if value in TYPE_MAP:
        return TYPE_MAP[value]
    else:
        return str


class Fields(object):
    """A class to deal with BigML auto-generated ids.

    """
    def __init__(self, fields, missing_tokens=[''], data_locale=DEFAULT_LOCALE):
        if data_locale in LOCALE_MAP:
            data_locale = LOCALE_MAP[data_locale]
        else:
            data_locale = DEFAULT_LOCALE
        locale.setlocale(locale.LC_ALL, data_locale)
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
                sys.exit("Error: field column number '%s' does not exist" % key)
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
                sys.exit("Error: field column number '%s' does not exist" % key)
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

    def pair(self, row, objective_field=None, objective_field_present=None):
        """Pairs a list of values with their respective field ids.

            objective_field is the column_number of the objective field.

           `objective_field_present` must be True is the objective_field column
           is present in the row.

        """

        if objective_field is None:
            objective_field = self.len() - 1
        elif isinstance(objective_field, basestring):
            objective_field = self.field_column_number(objective_field)

        if objective_field_present is None:
            objective_field_present = len(row) == self.len()

        pair = {}

        for index in range(self.len()):
            field_index = None
            if index < len(row) and not row[index] in self.missing_tokens:
                if objective_field_present:
                    if index != objective_field:
                        field_index = index
                else:
                    if index >= objective_field and index + 1 < self.len():
                        field_index = index + 1
                    else:
                        field_index = index

                if not field_index is None:
                    field = self.fields[self.field_id(field_index)]
                    row[index] = self.strip_affixes(row[index], field)
                    pair.update({self.field_id(field_index):
                                map_type(field['optype'])(row[index])})

        return pair

    def list_fields(self, out=sys.stdout):
        """Lists a description of the fields.

        """
        for field in [(val['name'], val['optype'], val['column_number'])
                      for key, val in sorted(self.fields.items(),
                                             key=lambda k:
                                             k[1]['column_number'])]:
            out.write('[%-32s : %-16s: %-8s]\n' % (field[0],
                                                   field[1], field[2]))
            out.flush()

    def strip_affixes(self, value, field):
        """Strips prefixes and suffixes if present

        """
        value = unicode(value, "utf-8")
        if 'prefix' in field and value.startswith(field['prefix']):
            value = value[len(field['prefix']):]
        if 'suffix' in field and value.endswith(field['suffix']):
            value = value[0:-len(field['suffix'])]
        return value
