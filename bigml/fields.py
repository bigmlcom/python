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
from bigml.util import invert_dictionary

TYPE_MAP = {
    "categorical": str,
    "numeric": float,
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
    def __init__(self, fields):
        self.fields = fields
        self.fields_by_name = invert_dictionary(fields, 'name')
        self.fields_by_column_number = invert_dictionary(fields,
                                                         'column_number')

    def field_id(self, key):
        """Returns a field id.

        """

        if isinstance(key, basestring):
            return self.fields_by_name[key]
        elif isinstance(key, int):
            return self.fields_by_column_number[key]

    def field_name(self, key):
        """Returns a field name.

        """
        if isinstance(key, basestring):
            return self.fields[key]['name']
        elif isinstance(key, int):
            return self.fields[self.fields_by_column_number[key]]['name']

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

        if objective_field_present is None:
            objective_field_present = len(row) == self.len()

        pair = {}
        for index in range(self.len()):
            if objective_field_present:
                if index != objective_field:
                    pair.update({self.field_id(index):
                                map_type(self.fields[self.field_id(index)]
                                         ['optype'])(row[index])})
            else:
                if index >= objective_field:
                    pair.update({self.field_id(index + 1):
                                map_type(self.fields[self.field_id(index + 1)]
                                         ['optype'])(row[index])})
                else:
                    pair.update({self.field_id(index):
                                map_type(self.fields[self.field_id(index)]
                                         ['optype'])(row[index])})

        return pair

    def list_fields(self, out=sys.stdout):
        """Lists a description of the felds.

        """
        for field in [(val['name'], val['optype'], val['column_number'])
                      for key, val in sorted(self.fields.items(),
                                             key=lambda k:
                                             k[1]['column_number'])]:
            out.write('[%-32s : %-16s: %-8s]\n' % (field[0],
                                                   field[1], field[2]))
            out.flush()
