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

"""Miscellaneous utility functions.

"""
import re
import unidecode
from urlparse import urlparse
import locale


def invert_dictionary(dictionary):
    """Inverts a dictionary.

    Useful to make predictions using fields' names instead of Ids.
    It does not check whether new keys are duplicated though.

    """
    return dict([[value['name'], key]
                for key, value in dictionary.items()])


def slugify(name):
    """Translates a field name into a variable name.

    """
    name = unidecode.unidecode(name).lower()
    return re.sub(r'\W+', '_', name)


def localize(number):
    """Localizes `number` to show commas appropriately.

    """
    return locale.format("%d", number, grouping=True)


def is_url(value):
    """Returns True if value is a valid URL.

    """
    url = isinstance(value, basestring) and urlparse(value)
    return url and url.scheme and url.netloc and url.path


def split(children):
    """Returns the field that is used by the node to make a decision.

    """
    field = set([child.predicate.field for child in children])

    if len(field) == 1:
        return field.pop()
