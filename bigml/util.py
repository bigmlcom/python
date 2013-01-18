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
import sys
import os

DEFAULT_LOCALE = 'en_US.UTF-8'
WINDOWS_DEFAULT_LOCALE = 'English'
LOCALE_SYNONYMS = {'en': ['en_US', 'en-US', 'en_US.UTF8', 'en_US.UTF-8',
                          'English_United States.1252'],
                   'es': ['es_ES', 'es-ES', 'es_ES.UTF8', 'es_ES.UTF-8',
                          'Spanish_Spain.1252'],
                   'sp': ['es_ES', 'es-ES', 'es_ES.UTF8', 'es_ES.UTF-8',
                          'Spanish_Spain.1252'],
                   'fr': [['fr_FR', 'fr-FR', 'fr_BE', 'fr_CH', 'fr-BE',
                           'fr-CH', 'fr_FR.UTF8', 'fr_CH.UTF8',
                           'fr_BE.UTF8', 'fr_FR.UTF-8', 'fr_CH.UTF-8',
                           'fr_BE.UTF-8', 'French_France.1252'],
                          ['fr_CA', 'fr-CA', 'fr_CA.UTF8', 'fr_CA.UTF-8',
                           'French_Canada.1252']],
                   'de': ['de_DE', 'de-DE', 'de_DE.UTF8', 'de_DE.UTF-8',
                          'German_Germany.1252'],
                   'ge': ['de_DE', 'de-DE', 'de_DE.UTF8', 'de_DE.UTF-8',
                          'German_Germany.1252'],
                   'it': ['it_IT', 'it-IT', 'it_IT.UTF8', 'it_IT.UTF-8',
                          'Italian_Italy.1252'],
                   'ca': ['ca_ES', 'ca-ES', 'ca_ES.UTF8', 'ca_ES.UTF-8',
                          'Catalan_Spain.1252']}

BOLD_REGEX = re.compile(r'''(\*\*)(?=\S)([^\r]*?\S[*_]*)\1''')
ITALIC_REGEX = re.compile(r'''(_)(?=\S)([^\r]*?\S)\1''')
LINKS_REGEX = re.compile((r'''(\[((?:\[[^\]]*\]|[^\[\]])*)\]\([ \t]*()'''
                          r'''<?(.*?)>?[ \t]*((['"])(.*?)\6[ \t]*)?\))'''),
                         re.MULTILINE)
TYPE_MAP = {
    "categorical": str,
    "numeric": locale.atof,
    "text": str
}

PYTHON_TYPE_MAP = {
    "categorical": [unicode, str],
    "numeric": [int, float],
    "text": [unicode, str]
}

PREDICTIONS_FILE_SUFFIX = '_predictions.csv'

PROGRESS_BAR_WIDTH = 50


def python_map_type(value):
    """Maps a BigML type to equivalent Python types.

    """
    if value in PYTHON_TYPE_MAP:
        return PYTHON_TYPE_MAP[value]
    else:
        return [unicode, str]


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
        text = '%s\n%s' % (text, '\n'.join(['[*]%s: %s' % (link[1], link[3])
                           for link in links_found]))
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
    """Sort fields by their column_number but put children after parents.

    """
    fathers = [(key, val) for key, val in
               sorted(fields.items(), key=lambda k:k[1]['column_number'])
               if not 'auto_generated' in val]
    children = [(key, val) for key, val in
                sorted(fields.items(), key=lambda k:k[1]['column_number'])
                if 'auto_generated' in val]
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


def utf8(text):
    """Returns text in utf-8 encoding

    """
    return text.encode("utf-8")


def map_type(value):
    """Maps a BigML type to a Python type.

    """
    if value in TYPE_MAP:
        return TYPE_MAP[value]
    else:
        return str


def locale_synonyms(main_locale, locale_alias):
    """Returns True if both strings correspond to equivalent locale conventions

    """
    language_code = main_locale[0:2]
    if not language_code in LOCALE_SYNONYMS:
        return False
    alternatives = LOCALE_SYNONYMS[language_code]
    if isinstance(alternatives[0], basestring):
        return (main_locale in alternatives and locale_alias in alternatives)
    else:
        result = False
        for subgroup in alternatives:
            if main_locale in subgroup:
                result = locale_alias in subgroup
                break
        return result


def find_locale(data_locale=DEFAULT_LOCALE, verbose=False):
    """Looks for the given locale or the closest alternatives

    """
    new_locale = None
    try:
        data_locale = str(data_locale)
    except UnicodeEncodeError:
        data_locale = data_locale.encode("utf8")
    try:
        new_locale = locale.setlocale(locale.LC_ALL, data_locale)
    except locale.Error:
        pass
    if new_locale is None:
        for locale_alias in LOCALE_SYNONYMS[data_locale[0:2]]:
            if isinstance(locale_alias, list):
                for subalias in locale_alias:
                    try:
                        new_locale = locale.setlocale(locale.LC_ALL, subalias)
                        break
                    except locale.Error:
                        pass
                if not new_locale is None:
                    break
            else:
                try:
                    new_locale = locale.setlocale(locale.LC_ALL, locale_alias)
                    break
                except locale.Error:
                    pass
    if new_locale is None:
        try:
            new_locale = locale.setlocale(locale.LC_ALL, DEFAULT_LOCALE)
        except locale.Error:
            pass
    if new_locale is None:
        try:
            new_locale = locale.setlocale(locale.LC_ALL,
                                          WINDOWS_DEFAULT_LOCALE)
        except locale.Error:
            pass
    if new_locale is None:
        new_locale = locale.setlocale(locale.LC_ALL, '')

    if verbose and not locale_synonyms(data_locale, new_locale):
        print ("WARNING: Unable to find %s locale, using %s instead. This "
               "might alter numeric fields values.\n") % (data_locale,
                                                          new_locale)


def get_predictions_file_name(model, path):
    """Returns the file name for a multimodel predictions file

    """
    if isinstance(model, dict) and 'resource' in model:
        model = model['resource']
    return "%s%s%s_%s" % (path,
                          os.sep,
                          model.replace("/", "_"),
                          PREDICTIONS_FILE_SUFFIX)


def clear_console_line(out=sys.stdout, length=PROGRESS_BAR_WIDTH):
    """Fills console line with blanks.

    """
    out.write("%s" % (" " * length))
    out.flush()


def reset_console_line(out=sys.stdout, length=PROGRESS_BAR_WIDTH):
    """Returns cursor to first column.

    """
    out.write("\b" * (length + 1))
    out.flush()


def console_log(message, out=sys.stdout, length=PROGRESS_BAR_WIDTH):
    """Prints the message to the given output

    """
    clear_console_line(out=out, length=length)
    reset_console_line(out=out, length=length)
    out.write(message)
    reset_console_line(out=out, length=length)


def get_csv_delimiter():
    """Returns the csv delimiter character

    """
    point_char = locale.localeconv()['decimal_point']
    return ',' if point_char != ',' else ';'
