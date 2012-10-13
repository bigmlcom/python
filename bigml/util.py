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

BOLD_REGEX = re.compile(r'''(\*\*)(?=\S)([^\r]*?\S[*_]*)\1''')
ITALIC_REGEX = re.compile(r'''(_)(?=\S)([^\r]*?\S)\1''')
LINKS_REGEX = re.compile(r'''(\[((?:\[[^\]]*\]|[^\[\]])*)\]\([ \t]*()<?(.*?)>?[ \t]*((['"])(.*?)\6[ \t]*)?\))''', re.MULTILINE)

def invert_dictionary(dictionary, field='name'):
    """Inverts a dictionary.

    Useful to make predictions using fields' names instead of Ids.
    It does not check whether new keys are duplicated though.

    """
    return dict([[value[field], key]
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

def markdown_cleanup(text):
    """Returns the text without markdown codes

    """
    def cleanup_bold_and_italic(text):
        """Removes from text bold and italic markdowns

        """
        text = BOLD_REGEX.sub(r'''\2''', text)
        text = ITALIC_REGEX.sub(r'''\2''', text)
        return text

    def links_to_footer(text):
        """Removes from text links and adds them as footer

        """
        links_found = re.findall(LINKS_REGEX, text)
        text = LINKS_REGEX.sub(r'''\2[*]''', text)
        text ='%s\n%s' % (text, '\n'.join(['[*]%s: %s' % (link[1], link[3]) for link in links_found]))
        return text

    new_line_regex = re.compile('(\n{2,})', re.DOTALL)
    text = new_line_regex.sub('\n', text)
    text = cleanup_bold_and_italic(text)
    text = links_to_footer(text)
    return text

def prefix_as_comment(comment_prefix, text):
    """Adds comment prefixes to new lines in comments

    """
    return text.replace('\n', '\n' + comment_prefix)

def sort_fields(fields):
    """Sort fields by their column_number but put together parents and children.

    """
    fathers = [(key, val) for key, val in sorted(fields.items(), key=lambda k:k[1]['column_number']) if not 'auto_generated' in val]
    children = [(key, val) for key, val in sorted(fields.items(), key=lambda k:k[1]['column_number']) if 'auto_generated' in val]
    children.reverse()
    fathers_keys = [father[0] for father in fathers]
    for child in children:
        try:
            index = fathers_keys.index(child[1]['parent_ids'][0])
        except ValueError:
            index = -1

        if index >= 0:
            fathers.insert(index + 1, child)
        else:
            fathers.append(child)
    return fathers
