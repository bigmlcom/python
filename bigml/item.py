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
        self.field_type = fields[self.field_id]["optype"]
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

    def describe(self):
        """Human-readable description of a item_dict

        """
        description = ""

        if self.field_type == "numeric":
            previous = self.segment_end if self.complement else \
                self.segment_start
            next = self.segment_start if self.complement else \
                self.segment_end
            if previous and next:
                if previous < next:
                    description = "%s < %s <= %s" % (previous, self.field_name,
                                                     next)
                else:
                    description = "%s > %s or <= %s" % (self.field_name,
                                                        previous,
                                                        next)
            elif previous:
                description = "%s > %s" % (self.field_name, previous)
            else:
                description = "%s <= %s" % (self.field_name, next)
        elif self.field_type == "categorical":
            operator = "!=" if self.complement else "="
            description = "%s %s %s" % (self.field_name, operator, self.name)
        elif self.field_type == text:
            operator = "excludes" if self.complement else "includes"
            description = "%s %s %s" % (self.field_name, operator, self.name)
        else:
            description = self.name
        return description

    def matches(self, value):
        """ Checks whether the value is in a range for numeric fields or
            matches a category for categorical fields.

        """
        if value is None:
            return False
        if self.segment_end is not None or self.segment_start is not None:
            if self.segment_start is not None and self.segment_end is not None:
                return self.segment_start <= value <= self.segment_end
            elif self.segment_end is not None:
                return value <= self.segment_end
            else:
                return value >= self.segment_start
        else:
            return self.name == value
