# -*- coding: utf-8 -*-
#
# Copyright 2012-2025 BigML
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
import locale
import sys
import os
import json
import math
import random
import ast
import datetime
import logging

from urllib.parse import urlparse
from unidecode import unidecode

import msgpack

import bigml.constants as c

try:
    from pandas import DataFrame
    PANDAS_READY = True
except ImportError:
    PANDAS_READY = False

DEFAULT_LOCALE = 'en_US.UTF-8'
WINDOWS_DEFAULT_LOCALE = 'English'
LOCALE_SYNONYMS = {
    'en': [['en_US', 'en-US', 'en_US.UTF8', 'en_US.UTF-8',
            'English_United States.1252', 'en-us', 'en_us',
            'en_US.utf8'],
           ['en_GB', 'en-GB', 'en_GB.UTF8', 'en_GB.UTF-8',
            'English_United Kingdom.1252', 'en-gb', 'en_gb',
            'en_GB.utf8']],
    'es': ['es_ES', 'es-ES', 'es_ES.UTF8', 'es_ES.UTF-8',
           'Spanish_Spain.1252', 'es-es', 'es_es',
           'es_ES.utf8'],
    'sp': ['es_ES', 'es-ES', 'es_ES.UTF8', 'es_ES.UTF-8',
           'Spanish_Spain.1252', 'es-es', 'es_es',
           'es_ES.utf8'],
    'fr': [['fr_FR', 'fr-FR', 'fr_BE', 'fr_CH', 'fr-BE',
            'fr-CH', 'fr_FR.UTF8', 'fr_CH.UTF8',
            'fr_BE.UTF8', 'fr_FR.UTF-8', 'fr_CH.UTF-8',
            'fr_BE.UTF-8', 'French_France.1252', 'fr-fr',
            'fr_fr', 'fr-be', 'fr_be', 'fr-ch', 'fr_ch',
            'fr_FR.utf8', 'fr_BE.utf8', 'fr_CH.utf8'],
           ['fr_CA', 'fr-CA', 'fr_CA.UTF8', 'fr_CA.UTF-8',
            'French_Canada.1252', 'fr-ca', 'fr_ca',
            'fr_CA.utf8']],
    'de': ['de_DE', 'de-DE', 'de_DE.UTF8', 'de_DE.UTF-8',
           'German_Germany.1252', 'de-de', 'de_de',
           'de_DE.utf8'],
    'ge': ['de_DE', 'de-DE', 'de_DE.UTF8', 'de_DE.UTF-8',
           'German_Germany.1252', 'de-de', 'de_de',
           'de_DE.utf8'],
    'it': ['it_IT', 'it-IT', 'it_IT.UTF8', 'it_IT.UTF-8',
           'Italian_Italy.1252', 'it-it', 'it_it',
           'it_IT.utf8'],
    'ca': ['ca_ES', 'ca-ES', 'ca_ES.UTF8', 'ca_ES.UTF-8',
           'Catalan_Spain.1252', 'ca-es', 'ca_es',
           'ca_ES.utf8']}

BOLD_REGEX = re.compile(r'''(\*\*)(?=\S)([^\r]*?\S[*_]*)\1''')
ITALIC_REGEX = re.compile(r'''(_)(?=\S)([^\r]*?\S)\1''')
LINKS_REGEX = re.compile((r'''(\[((?:\[[^\]]*\]|[^\[\]])*)\]\([ \t]*()'''
                          r'''<?(.*?)>?[ \t]*((['"])(.*?)\6[ \t]*)?\))'''),
                         re.MULTILINE)
TYPE_MAP = {
    "categorical": str,
    "numeric": locale.atof,
    "text": str,
    "items": str
}

PYTHON_TYPE_MAP = {
    "categorical": [str, str],
    "numeric": [int, float],
    "text": [str, str],
    "items": [str, str]
}

PREDICTIONS_FILE_SUFFIX = '_predictions.csv'

PROGRESS_BAR_WIDTH = 50

HTTP_INTERNAL_SERVER_ERROR = 500

PRECISION = 5

NUMERIC = "numeric"

DFT_STORAGE = "./storage"
DFT_STORAGE_FILE = os.path.join(DFT_STORAGE, "BigML_%s.json")

DECIMAL_DIGITS = 5


def python_map_type(value):
    """Maps a BigML type to equivalent Python types.

    """
    if value in PYTHON_TYPE_MAP:
        return PYTHON_TYPE_MAP[value]
    return [str, str]


def invert_dictionary(dictionary, field='name'):
    """Inverts a dictionary.

    Useful to make predictions using fields' names instead of Ids.
    It does not check whether new keys are duplicated though.

    """
    return {value[field]: key for key, value in dictionary.items()}


def localize(number):
    """Localizes `number` to show commas appropriately.

    """
    return locale.format_string("%d", number, grouping=True)


def is_url(value):
    """Returns True if value is a valid URL.

    """
    url = isinstance(value, str) and urlparse(value)
    return url and url.scheme and url.netloc and url.path


def is_in_progress(resource):
    """Returns True if the resource has no error and has not finished yet

    """
    return resource.get("error") is None \
        and get_status(resource).get("code") != c.FINISHED


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


def utf8(bytes_str):
    """Returns utf-8 string for bytes or string objects

    """
    try:
        return str(bytes_str, 'utf-8')
    except TypeError:
        return bytes_str


def map_type(value):
    """Maps a BigML type to a Python type.

    """
    if value in TYPE_MAP:
        return TYPE_MAP[value]
    return str


def locale_synonyms(main_locale, locale_alias):
    """Returns True if both strings correspond to equivalent locale conventions

    """
    language_code = main_locale[0:2]
    if language_code not in LOCALE_SYNONYMS:
        return False
    alternatives = LOCALE_SYNONYMS[language_code]
    if isinstance(alternatives[0], str):
        return locale_alias in alternatives
    result = False
    for subgroup in alternatives:
        result = locale_alias in subgroup
        break
    return result


def bigml_locale(locale_alias):
    """Returns the locale used in bigml.com for the given locale_alias

       The result is the locale code used in bigml.com provided that
       the locale user code has been correctly mapped. None otherwise.
    """
    language_code = locale_alias.lower()[0:2]
    if language_code not in LOCALE_SYNONYMS:
        return None
    alternatives = LOCALE_SYNONYMS[language_code]
    if isinstance(alternatives[0], str):
        return (alternatives[0] if locale_alias in alternatives
                else None)
    result = None
    for subgroup in alternatives:
        if locale_alias in subgroup:
            result = subgroup[0]
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
        new_locale = locale.setlocale(locale.LC_NUMERIC, data_locale)
    except locale.Error:
        pass
    if new_locale is None:
        for locale_alias in LOCALE_SYNONYMS.get(data_locale[0:2], []):
            if isinstance(locale_alias, list):
                for subalias in locale_alias:
                    try:
                        new_locale = locale.setlocale(locale.LC_NUMERIC, subalias)
                        break
                    except locale.Error:
                        pass
                if new_locale is not None:
                    break
            else:
                try:
                    new_locale = locale.setlocale(locale.LC_NUMERIC, locale_alias)
                    break
                except locale.Error:
                    pass
    if new_locale is None:
        try:
            new_locale = locale.setlocale(locale.LC_NUMERIC, DEFAULT_LOCALE)
        except locale.Error:
            pass
    if new_locale is None:
        try:
            new_locale = locale.setlocale(locale.LC_NUMERIC,
                                          WINDOWS_DEFAULT_LOCALE)
        except locale.Error:
            pass
    if new_locale is None:
        new_locale = locale.setlocale(locale.LC_NUMERIC, '')

    if verbose and not locale_synonyms(data_locale, new_locale):
        print(("WARNING: Unable to find %s locale, using %s instead. This "
               "might alter numeric fields values.\n") % (data_locale,
                                                          new_locale))


def asciify(name):
    """Translating to ascii and underscores """

    if len(name) == 0:
        # case of empty name?
        return name

    name = unidecode(name).lower()
    name = re.sub(r'\W+', '_', name)
    return name


def res_filename(storage_dir, resource_id, extension=None):
    """Returns a filename from a resource id"""
    basename = asciify(resource_id)
    if extension is None:
        extension = ""
    basename = f"{basename}{extension}"
    filename = os.path.join(storage_dir, basename)
    return filename


def fs_cache_get(storage_dir, minimized=True):
    """Returns a function that retrieves a minimized resource from the file
    system
    """
    extension = ".min" if minimized else ""
    def cache_get(resource_id):
        filename = res_filename(storage_dir, asciify(resource_id), extension)
        if not os.path.exists(filename):
            raise ValueError(f"Failed to find the dump file {filename}.")
        with open(filename, "rb") as handler:
            return handler.read()

    return cache_get


def fs_cache_set(storage_dir, minimized=True):
    """Returns a function that stores a minimized resource in the file system """
    extension = ".min" if minimized else ""
    check_dir(storage_dir)

    def cache_set(resource_id, msg):
        filename = res_filename(storage_dir, asciify(resource_id), extension)
        with open(filename, "wb") as handler:
            handler.write(msg)
            return filename

    return cache_set


def get_predictions_file_name(model, path):
    """Returns the file name for a multimodel predictions file

    """
    if isinstance(model, dict) and 'resource' in model:
        model = model['resource']
    filename = res_filename(path, model)
    return f"{filename}_{PREDICTIONS_FILE_SUFFIX}"


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


def console_log(message, out=sys.stdout, length=PROGRESS_BAR_WIDTH,
                reset=False):
    """Prints the message to the given output

       :param out: output handler
       :param length: maximum length
       :param reset: whether the line has to be reused and cursor reset to
              the beggining of it
    """
    if reset:
        clear_console_line(out=out, length=length)
        reset_console_line(out=out, length=length)
    out.write(message)
    if reset:
        reset_console_line(out=out, length=length)


def get_csv_delimiter():
    """Returns the csv delimiter character

    """
    point_char = locale.localeconv()['decimal_point']
    return ',' if point_char != ',' else ';'


def strip_affixes(value, field):
    """Strips prefixes and suffixes if present

    """
    if not isinstance(value, str):
        value = str(value, "utf-8")
    if 'prefix' in field and value.startswith(field['prefix']):
        value = value[len(field['prefix']):]
    if 'suffix' in field and value.endswith(field['suffix']):
        value = value[0:-len(field['suffix'])]
    return value


def cast(input_data, fields):
    """Checks expected type in input data values, strips affixes and casts

    """
    for (key, value) in list(input_data.items()):
        # inputs not in fieldsor empty
        if key not in fields or value is None:
            continue
        # strings given as booleans
        if isinstance(value, bool) and \
                fields[key]['optype'] == 'categorical' and \
                len(fields[key]['summary']['categories']) == 2:
            try:
                booleans = {}
                categories = [category for category, _ in \
                    fields[key]['summary']['categories']]
                # checking which string represents the boolean
                for category in categories:
                    bool_key = 'True' if ast.literal_eval( \
                        category.capitalize()) else 'False'
                    booleans[bool_key] = category
                # converting boolean to the corresponding string
                input_data.update({key: booleans[str(value)]})
            except ValueError:
                raise ValueError("Mismatch input data type in field "
                                 "\"%s\" for value %s. String expected" %
                                 (fields[key]['name'], value))
        # numerics given as strings
        elif (
                (fields[key]['optype'] == NUMERIC and
                 isinstance(value, str)) or
                (fields[key]['optype'] != NUMERIC and
                 not isinstance(value, str))):
            try:
                if fields[key]['optype'] == NUMERIC:
                    value = strip_affixes(value, fields[key])
                input_data.update({key:
                                   map_type(fields[key]
                                            ['optype'])(value)})
            except ValueError:
                raise ValueError("Mismatch input data type in field "
                                 "\"%s\" for value %s." %
                                 (fields[key]['name'],
                                  value))
        elif (fields[key]['optype'] == NUMERIC and
              isinstance(value, bool)):
            raise ValueError("Mismatch input data type in field "
                             "\"%s\" for value %s. Numeric expected." %
                             (fields[key]['name'], value))
        if fields[key]['optype'] == NUMERIC and isinstance(value, float):
            input_data.update({key: round(value, DECIMAL_DIGITS)})


def check_dir(path):
    """Creates a directory if it doesn't exist

    """
    if os.path.exists(path):
        if not os.path.isdir(path):
            raise ValueError("The given path is not a directory")
    elif len(path) > 0:
        os.makedirs(path)
    return path


def resource_structure(code, resource_id, location, resource, error):
    """Returns the corresponding JSON structure for a resource

    """
    return {
        'code': code,
        'resource': resource_id,
        'location': location,
        'object': resource,
        'error': error}


def empty_resource():
    """Creates an empty resource JSON structure

    """
    return resource_structure(
        HTTP_INTERNAL_SERVER_ERROR,
        None,
        None,
        None,
        {
            "status": {
                "code": HTTP_INTERNAL_SERVER_ERROR,
                "message": "The resource couldn't be created"}})


def get_status(resource):
    """Extracts status info if present or sets the default if public

    """
    if not isinstance(resource, dict):
        raise ValueError("We need a complete resource to extract its status")
    if 'object' in resource:
        if resource['object'] is None:
            raise ValueError("The resource has no status info\n%s" % resource)
        resource = resource['object']
    if not resource.get('private', True) or resource.get('status') is None:
        status = {'code': c.FINISHED}
    else:
        status = resource['status']
    return status


def maybe_save(resource_id, path,
               code=None, location=None,
               resource=None, error=None):
    """Builds the resource dict response and saves it if a path is provided.

    The resource is saved in a local repo json file in the given path.
    Only final resources are stored. Final resources should be FINISHED or
    FAILED

    """
    resource = resource_structure(code, resource_id, location, resource, error)
    if resource_id is not None and path is not None and \
            is_status_final(resource):
        resource_file_name = "%s%s%s" % (path, os.sep,
                                         resource_id.replace('/', '_'))
        save_json(resource, resource_file_name)
    return resource


def is_status_final(resource):
    """Try whether a resource is in a final state

    """
    status = {}
    try:
        status = get_status(resource)
    except ValueError:
        pass
    return status.get('code') in [c.FINISHED, c.FAULTY]


def save_json(resource, path):
    """Stores the resource in the user-given path in a JSON format

    """
    try:
        resource_json = json.dumps(resource)
        return save(resource_json, path)
    except ValueError:
        print("The resource has an invalid JSON format")
    except IOError:
        print("Failed writing resource to %s" % path)
    return None


def save(content, path):
    """Stores content in an utf-8 file

    """
    if path is None:
        datestamp = datetime.datetime.now().strftime("%a%b%d%y_%H%M%S")
        path = DFT_STORAGE_FILE % datestamp
    check_dir(os.path.dirname(path))
    with open(path, "wb", 0) as file_handler:
        content = content.encode('UTF-8')
        file_handler.write(content)
    return path


def plural(text, num):
    """Pluralizer: adds "s" at the end of a string if a given number is > 1

    """
    return "%s%s" % (text, "s"[num == 1:])


def get_exponential_wait(wait_time, retry_count):
    """Computes the exponential wait time used in next request using the
    base values provided by the user:
        - wait_time: starting wait time (seconds)
        - retries_count: number of retries

    """
    delta = (retry_count ** 2) * wait_time / 2
    exp_factor = delta if retry_count > 1 else 0
    return wait_time + math.floor(random.random() * exp_factor)


def check_no_missing_numerics(input_data, fields, weight_field=None):
    """Checks whether some numeric fields are missing in the input data

    """
    for field_id, field in list(fields.items()):
        if (field['optype'] == NUMERIC and (weight_field is None or \
                field_id != weight_field) and \
                not field_id in input_data):
            raise ValueError("Failed to predict. Input"
                             " data must contain values for all numeric"
                             " fields to get a prediction.")

#pylint: disable=locally-disabled,too-many-boolean-expressions
def check_no_training_missings(input_data, fields, weight_field=None,
                               objective_id=None):
    """Checks whether some input fields are missing in the input data
    while not training data has no missings in that field

    """
    for field_id, field in fields.items():
        if (field["optype"] != "datetime" and \
                field_id not in input_data and \
                field['summary']['missing_count'] == 0 and \
                (weight_field is None or field_id != weight_field) and \
                (objective_id is None or field_id != objective_id)):
            raise ValueError("Failed to predict. Input"
                             " data must contain values for field '%s' "
                             "to get a prediction." % field['name'])


def flatten(inner_array):
    """ Flattens an array with inner arrays

    """
    new_array = []

    for element in inner_array:
        if isinstance(element, list):
            new_array.extend(element)
        else:
            new_array.append(element)

    return new_array


def use_cache(cache_get):
    """Checks whether the user has provided a cache get function to retrieve
       local models.

    """
    return cache_get is not None and hasattr(cache_get, '__call__')


def dump(local_attrs, output=None, cache_set=None):
    """Uses msgpack to serialize the local resource object
    If cache_set is filled with a cache set method, the method is called

    """
    if use_cache(cache_set):
        dump_string = msgpack.dumps(local_attrs)
        cache_set(local_attrs["resource_id"], dump_string)
    else:
        msgpack.pack(local_attrs, output)


def dumps(local_attrs):
    """Uses msgpack to serialize the anomaly object to a string

    """

    return msgpack.dumps(local_attrs)


def load(resource_id, cache_get):
    """Uses msgpack to load the resource stored by ID

    """

    return msgpack.loads(cache_get(resource_id))


def filter_by_extension(file_list, extension_list):
    """Returns the files that match the given extensions

    """
    return [filename for filename in file_list if
        os.path.splitext(filename)[1].replace(".", "").lower()
        in extension_list]


def infer_field_type(field, value):
    """Returns a dictionary containing the name and optype of the objective
    field as inferred from the corresponding value
    """
    if isinstance(value, str):
        optype = "categorical"
    elif isinstance(value, list):
        optype = "regions"
    else:
        optype = "numeric"
    return {"name": field, "optype": optype}


def is_image(filename):
    """Checking whether the file is an image based on its extension """
    return os.path.splitext(filename)[1].replace(".", "").lower() \
        in c.IMAGE_EXTENSIONS


def get_data_format(input_data_list):
    """Returns the format used in input_data_list: DataFrame or
    list of dicts.

    """
    if PANDAS_READY and isinstance(input_data_list, DataFrame):
        return c.DATAFRAME
    if isinstance(input_data_list, list) and (len(input_data_list) == 0 or
            isinstance(input_data_list[0], dict)):
        return c.INTERNAL
    raise ValueError("Data is expected to be provided as a list of "
                     "dictionaries or Pandas' DataFrame.")


#pylint: disable=locally-disabled,comparison-with-itself
def format_data(input_data_list, out_format=None):
    """Transforms the input data format to the one expected """
    if out_format == c.DATAFRAME:
        input_data_list = DataFrame.from_dict(input_data_list)
    elif out_format == c.INTERNAL:
        input_data_list = input_data_list.to_dict('records')
        # pandas nan, NaN, etc. outputs need to be changed to None
        for row in input_data_list:
            for key, value in row.items():
                if value != value:
                    row[key] = None
    return input_data_list


def get_formatted_data(input_data_list, out_format=None):
    """Checks the type of data and transforms if needed """
    current_format = get_data_format(input_data_list)
    if current_format != out_format:
        inner_data_list = format_data(input_data_list, out_format)
    else:
        inner_data_list = input_data_list.copy()
    return inner_data_list


#pylint: disable=locally-disabled,import-outside-toplevel
def get_data_transformations(resource_id, parent_id):
    """Returns the pipeline that contains the tranformations and derived
    features created from the raw data to the actual resource.

    """
    if parent_id is None:
        raise ValueError("Failed to find the dataset information "
                         "needed to buid the data transformations "
                         "pipeline.")
    from bigml.pipeline.pipeline import BMLPipeline
    return BMLPipeline("dt-%s" % resource_id, [parent_id])


def sensenet_logging():
    """Removes warnings unnecessary logging when using sensenet"""
    logging.disable(logging.WARNING)
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    os.environ["TF_USE_LEGACY_KERAS"] = "1"
    import tensorflow as tf
    tf.autograph.set_verbosity(0)
    logging.getLogger("tensorflow").setLevel(logging.ERROR)
