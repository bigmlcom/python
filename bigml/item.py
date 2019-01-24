# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015-2019 BigML
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
from bigml.predicate import term_matches, item_matches

class Item(object):
    """ Object encapsulating an Association resource item as described in
    https://bigml.com/developers/associations

    """

    def __init__(self, index, item_info, fields):
        self.index = index
        self.complement = item_info.get('complement', False)
        self.complement_index = item_info.get('complement_index')
        self.count = item_info.get('count')
        self.description = item_info.get('description')
        self.field_id = item_info.get('field_id')
        self.field_info = fields[self.field_id]
        self.name = item_info.get('name')
        self.bin_end = item_info.get('bin_end')
        self.bin_start = item_info.get('bin_start')

    def out_format(self, language="JSON"):
        """Transforming the item structure to a string in the required format

        """
        if language in SUPPORTED_LANGUAGES:
            return getattr(self, "to_%s" % language)()
        return self

    def to_csv(self):
        """Transforming the item to CSV formats

        """
        output = [self.complement, self.complement_index, self.count,
                  self.description, self.field_info['name'], self.name,
                  self.bin_end, self.bin_start]
        return output

    def to_json(self):
        """Transforming the item relevant information to JSON

        """
        item_dict = {}
        item_dict.update(self.__dict__)
        del item_dict["field_info"]
        del item_dict["complement_index"]
        del item_dict["index"]
        return item_dict

    def to_lisp_rule(self):
        """Returns the LISP flatline expression to filter this item

        """
        flatline = ""
        if self.name is None:
            return u"(missing? (f %s))" % self.field_id
        field_type = self.field_info['optype']
        if field_type == "numeric":
            start = self.bin_end if self.complement else \
                self.bin_start
            end = self.bin_start if self.complement else \
                self.bin_end
            if start is not None and end is not None:
                if start < end:
                    flatline = u"(and (< %s (f %s)) (<= (f %s) %s))" % \
                        (start, self.field_id, self.field_id, end)
                else:
                    flatline = u"(or (> (f %s) %s) (<= (f %s) %s))" % \
                        (self.field_id, start, self.field_id, end)
            elif start is not None:
                flatline = u"(> (f %s) %s)" % (self.field_id, start)
            else:
                flatline = u"(<= (f %s) %s)" % (self.field_id, end)
        elif field_type == "categorical":
            operator = u"!=" if self.complement else u"="
            flatline = u"(%s (f %s) %s)" % (
                operator, self.field_id, self.name)
        elif field_type == "text":
            operator = u"=" if self.complement else u">"
            options = self.field_info['term_analysis']
            case_insensitive = not options.get('case_sensitive', False)
            case_insensitive = u'true' if case_insensitive else u'false'
            language = options.get('language')
            language = u"" if language is None else u" %s" % language
            flatline = u"(%s (occurrences (f %s) %s %s%s) 0)" % (
                operator, self.field_id, self.name,
                case_insensitive, language)
        elif field_type == 'items':
            operator = u"!" if self.complement else u""
            flatline = u"(%s (contains-items? %s %s))" % (
                operator, self.field_id, self.name)
        return flatline

    def describe(self):
        """Human-readable description of a item_dict

        """
        description = ""
        if self.name is None:
            return "%s is %smissing" % (
                self.field_info['name'], "not " if self.complement else "")
        field_name = self.field_info['name']
        field_type = self.field_info['optype']
        if field_type == "numeric":
            start = self.bin_end if self.complement else \
                self.bin_start
            end = self.bin_start if self.complement else \
                self.bin_end
            if start is not None and end is not None:
                if start < end:
                    description = "%s < %s <= %s" % (start,
                                                     field_name,
                                                     end)
                else:
                    description = "%s > %s or <= %s" % (field_name,
                                                        start,
                                                        end)
            elif start is not None:
                description = "%s > %s" % (field_name, start)
            else:
                description = "%s <= %s" % (field_name, end)
        elif field_type == "categorical":
            operator = "!=" if self.complement else "="
            description = "%s %s %s" % (field_name, operator, self.name)
        elif field_type in ["text", "items"]:
            operator = "excludes" if self.complement else "includes"
            description = "%s %s %s" % (field_name, operator, self.name)
        else:
            description = self.name
        return description

    def matches(self, value):
        """ Checks whether the value is in a range for numeric fields or
        matches a category for categorical fields.

        """
        field_type = self.field_info['optype']
        if value is None:
            return self.name is None
        if field_type == "numeric" and (
                self.bin_end is not None or self.bin_start is not None):
            if self.bin_start is not None and self.bin_end is not None:
                result = self.bin_start <= value <= self.bin_end
            elif self.bin_end is not None:
                result = value <= self.bin_end
            else:
                result = value >= self.bin_start
        elif field_type == 'categorical':
            result = self.name == value
        elif field_type == 'text':
            # for text fields, the item.name or the related term_forms should
            # be in the considered value
            all_forms = self.field_info['summary'].get('term_forms', {})
            term_forms = all_forms.get(self.name, [])
            terms = [self.name]
            terms.extend(term_forms)
            options = self.field_info['term_analysis']
            result = term_matches(value, terms, options) > 0
        elif field_type == 'items':
            # for item fields, the item.name should be in the considered value
            # surrounded by separators or regexp
            options = self.field_info['item_analysis']
            result = item_matches(value, self.name, options) > 0
        if self.complement:
            result = not result
        return result
