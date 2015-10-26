# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015 BigML
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

"""Item object for the Association resource.

   This module defines each item in an Association resource.
"""

from bigml.associationrule import SUPPORTED_LANGUAGES

class Item(object):
    """ Object encapsulating an Association resource item as described in
        https://bigml.com/developers/associations

    """

    def __init__(self, index, item_info, fields):
        self.index = index
        self.complement = item_info.get('complement', False)
        self.complement_id = item_info.get('complement_id')
        self.count = item_info.get('count')
        self.description = item_info.get('description')
        self.field_id = item_info.get('field_id')
        self.field_name = fields[self.field_id]["name"]
        self.name = item_info.get('name')
        self.segment_end = item_info.get('segment_end')
        self.segment_start = item_info.get('segment_start')

    def out_format(self, language="JSON"):
        """Transforming the rule structure to a string in the required format

        """
        if language in SUPPORTED_LANGUAGES:
            return self.getattr("to_%s" % language)()
        return self

    def to_CSV(self):
        """Transforming the rule to CSV formats

        """
        output = [self.complement, self.complement_id, self.count,
                  self.description, self.field_name, self.name,
                  self.segment_end, self.segment_start]
        return output

    def to_JSON(self):
        """Transforming the item to JSON

        """
        item_dict = {}
        item_dict.update(self.__dict__)
        return item_dict
