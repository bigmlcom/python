# -*- coding: utf-8 -*-
#
# Copyright 2013-2023 BigML
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

"""A ModelFields resource.

This module defines a ModelFields class to hold the information associated
to the fields of the model resource in BigML.
It becomes the starting point for the Model class, that
is used for local predictions.

"""
import logging
import re
import copy


from bigml.util import invert_dictionary, dump, dumps, DEFAULT_LOCALE
from bigml.constants import DEFAULT_MISSING_TOKENS, FIELDS_PARENT, \
    ENSEMBLE_PATH, DEFAULT_OPERATION_SETTINGS
from bigml.api_handlers.resourcehandler import get_resource_type
from bigml.predicate import TM_FULL_TERM, TM_ALL

LOGGER = logging.getLogger('BigML')

NUMERIC = "numeric"


def parse_terms(text, case_sensitive=True):
    """Returns the list of parsed terms

    """
    if text is None:
        return []
    expression = r'(\b|_)([^\b_\s]+?)(\b|_)'
    pattern = re.compile(expression)
    return [match[1] if case_sensitive else match[1].lower()
            for match in re.findall(pattern, text)]


def parse_items(text, regexp):
    """Returns the list of parsed items

    """
    if text is None:
        return []
    pattern = re.compile(regexp, flags=re.U)
    return [term.strip() for term in pattern.split(text)]


def check_resource_fields(resource):
    """Checks the resource structure to see whether it contains the required
    fields information

    """
    inner_key = FIELDS_PARENT.get(get_resource_type(resource), 'model')
    if check_resource_structure(resource, inner_key):
        resource = resource.get('object', resource)
        fields = resource.get("fields",
            resource.get(inner_key, {}).get('fields'))
        input_fields = resource.get("input_fields")
        # models only need model_fields to work. The rest of resources will
        # need all fields to work
        model_fields = list(resource.get(inner_key, {}).get( \
            'model_fields', {}).keys())
        # fusions don't have input fields
        if input_fields is None and inner_key != "fusion":
            return False
        if not model_fields:
            fields_meta = resource.get('fields_meta', \
                resource.get(inner_key, {}).get('fields_meta', {}))
            try:
                return fields_meta['count'] == fields_meta['total']
            except KeyError:
                # stored old models will not have the fields_meta info, so
                # we return True to avoid failing in this case
                return True
        else:
            if fields is None:
                return False
            return all(field_id in list(fields.keys()) \
                for field_id in model_fields)
    return False


def check_resource_structure(resource, inner_key=None):
    """Checks the resource structure to see if it contains all the
    main expected keys

    """
    if inner_key is None:
        inner_key = FIELDS_PARENT.get(get_resource_type(resource), 'model')
    # for datasets, only checking the resource ID
    if inner_key is None:
        return (isinstance(resource, dict) and 'resource' in resource and
            resource['resource'] is not None)
    # for the rest of models
    return (isinstance(resource, dict) and 'resource' in resource and
            resource['resource'] is not None and
            (('object' in resource and inner_key in resource['object']) or
             inner_key in resource))


def get_unique_terms(terms, term_forms, tag_cloud):
    """Extracts the unique terms that occur in one of the alternative forms in
       term_forms or in the tag cloud.

    """

    extend_forms = {}
    for term, forms in list(term_forms.items()):
        for form in forms:
            extend_forms[form] = term
        extend_forms[term] = term
    terms_set = {}
    for term in terms:
        if term in tag_cloud:
            if term not in terms_set:
                terms_set[term] = 0
            terms_set[term] += 1
        elif term in extend_forms:
            term = extend_forms[term]
            if term not in terms_set:
                terms_set[term] = 0
            terms_set[term] += 1
    return list(terms_set.items())


class ModelFields:
    """ A lightweight wrapper of the field information in the model, cluster
    or anomaly objects

    """
    #pylint: disable=locally-disabled,no-member,access-member-before-definition
    def __init__(self, fields, objective_id=None, data_locale=None,
                 missing_tokens=None, categories=False,
                 numerics=False, operation_settings=None, model_fields=None):
        if isinstance(fields, dict):
            tmp_fields = copy.deepcopy(fields)
            try:
                self.objective_id = objective_id
                self.uniquify_varnames(tmp_fields)
                self.inverted_fields = invert_dictionary(tmp_fields)
                self.fields = tmp_fields
                if not (hasattr(self, "input_fields") and self.input_fields):
                    self.input_fields = [field_id for field_id, field in \
                        sorted(list(self.fields.items()),
                               key=lambda x: x[1].get("column_number")) \
                        if not self.objective_id or \
                        field_id != self.objective_id]
                if model_fields is not None:
                    self.model_fields = model_fields
                else:
                    self.model_fields = {}
                    self.model_fields.update(
                        {field_id: field for field_id, field \
                        in self.fields.items() if field_id in \
                        self.input_fields and self.fields[field_id].get(
                        "preferred", True)})
                self.data_locale = data_locale
                self.missing_tokens = missing_tokens
                if self.data_locale is None:
                    self.data_locale = DEFAULT_LOCALE
                if self.missing_tokens is None:
                    self.missing_tokens = DEFAULT_MISSING_TOKENS
                # adding text and items information to handle terms
                # expansion
                self.term_forms = []
                self.tag_clouds = {}
                self.term_analysis = {}
                self.items = {}
                self.item_analysis = {}
                if categories:
                    self.categories = {}
                self.add_terms(categories, numerics)

                if self.objective_id is not None and \
                        hasattr(self, "resource_id") and self.resource_id and \
                        get_resource_type(self.resource_id) != ENSEMBLE_PATH:
                    # Only for models. Ensembles need their own logic
                    self.regression = \
                        (not hasattr(self, "boosting") or not self.boosting) \
                        and self.fields[self.objective_id][ \
                        'optype'] == NUMERIC \
                        or (hasattr(self, "boosting") and self.boosting and \
                        self.boosting.get("objective_class") is None)
                self.operation_settings = self._add_operation_settings(
                    operation_settings)
            except KeyError:
                raise Exception("Wrong field structure.")

    def _add_operation_settings(self, operation_settings):
        """Checks and adds the user-given operation settings """
        if operation_settings is None:
            return None
        if self.regression:
            raise ValueError("No operating settings are allowed"
                             " for regressions")
        return {setting: operation_settings[setting] for
            setting in operation_settings.keys() if setting in
            DEFAULT_OPERATION_SETTINGS
        }

    def add_terms(self, categories=False, numerics=False):
        """Adds the terms information of text and items fields

        """
        for field_id, field in list(self.fields.items()):
            if field['optype'] == 'text' and \
                    self.fields[field_id]['summary'].get('tag_cloud'):
                self.term_forms.append(field_id)
                self.tag_clouds[field_id] = []
                self.tag_clouds[field_id] = [tag for [tag, _] in field[
                    'summary']['tag_cloud']]
                del self.fields[field_id]["summary"]["tag_cloud"]
                self.term_analysis[field_id] = {}
                self.term_analysis[field_id].update(
                    field['term_analysis'])
            if field['optype'] == 'items' and \
                    self.fields[field_id]["summary"].get("items"):
                self.items[field_id] = []
                self.items[field_id] = [item for item, _ in \
                    field['summary']['items']]
                del self.fields[field_id]["summary"]["items"]
                self.item_analysis[field_id] = {}
                self.item_analysis[field_id].update(
                    field['item_analysis'])
            if categories and field['optype'] == 'categorical' and \
                    self.fields[field_id]["summary"]["categories"]:
                self.categories[field_id] = [category for \
                    [category, _] in field['summary']['categories']]
            if field['optype'] == 'datetime' and \
                    hasattr(self, "coeff_ids"):
                self.coeff_id = [coeff_id for coeff_id in self.coeff_ids \
                    if coeff_id != field_id]
            if numerics and hasattr(self, "missing_numerics") and \
                    self.missing_numerics and field['optype'] == 'numeric' \
                    and hasattr(self, "numeric_fields"):
                self.numeric_fields[field_id] = True


    def uniquify_varnames(self, fields):
        """Tests if the fields names are unique. If they aren't, a
           transformation is applied to ensure unicity.

        """
        unique_names = {fields[key]['name'] for key in fields}
        if len(unique_names) < len(fields):
            self.transform_repeated_names(fields)

    def transform_repeated_names(self, fields):
        """If a field name is repeated, it will be transformed adding its
           column number. If that combination is also a field name, the
           field id will be added.

        """
        # The objective field treated first to avoid changing it.
        if self.objective_id:
            unique_names = [fields[self.objective_id]['name']]
        else:
            unique_names = []

        field_ids = sorted([field_id for field_id in fields
                            if field_id != self.objective_id])
        for field_id in field_ids:
            new_name = fields[field_id]['name']
            if new_name in unique_names:
                new_name = "{0}{1}".format(fields[field_id]['name'],
                                           fields[field_id]['column_number'])
                if new_name in unique_names:
                    new_name = "{0}_{1}".format(new_name, field_id)
                fields[field_id]['name'] = new_name
            unique_names.append(new_name)

    def normalize(self, value):
        """Transforms to unicode and cleans missing tokens

        """
        if isinstance(value, str) and not isinstance(value, str):
            value = str(value, "utf-8")
        return None if value in self.missing_tokens else value

    def fill_numeric_defaults(self, input_data):
        """Fills the value set as default for numeric missing fields if user
        created the model with the default_numeric_value option

        """
        if hasattr(self, "default_numeric_value") and \
                self.default_numeric_value is not None:
            for key in self.fields:
                if key in self.model_fields and \
                        (self.objective_id is None or \
                         key != self.objective_id) and  \
                        self.fields[key]["optype"] == NUMERIC and \
                        input_data.get(key) is None:
                    input_data[key] = self.fields[key]["summary"].get( \
                        self.default_numeric_value, 0)
        return input_data

    def filter_input_data(self, input_data,
                          add_unused_fields=False):
        """Filters the keys given in input_data checking against model fields.
        If `add_unused_fields` is set to True, it also
        provides information about the ones that are not used.

        """
        unused_fields = []
        new_input = {}
        tmp_input = {}
        tmp_input.update(input_data)
        if isinstance(tmp_input, dict):
            # remove all missing values
            for key, value in list(tmp_input.items()):
                value = self.normalize(value)
                if value is None:
                    del tmp_input[key]
            for key, value in list(tmp_input.items()):
                if key not in self.fields:
                    key = self.inverted_fields.get(key, key)
                # only the fields that are listed in input_fields and appear
                # as preferred are used in predictions
                if key in self.model_fields and \
                        (self.objective_id is None or \
                         key != self.objective_id):
                    new_input[key] = value
                else:
                    unused_fields.append(key)
            # Feature generation (datetime and image features) is now done
            # when a Pipeline is created for the model, so no features are
            # added any more at this point.
            # We fill the input with the chosen default, if selected
            new_input = self.fill_numeric_defaults(new_input)
            final_input = {}
            for key, value in new_input.items():
                if key in self.model_fields:
                    final_input.update({key: value})
            result = (final_input, unused_fields) if add_unused_fields else \
                final_input
            return result
        LOGGER.error("Failed to read input data in the expected"
                     " {field:value} format.")
        return ({}, []) if add_unused_fields else {}

    def get_unique_terms(self, input_data):
        """Parses the input data to find the list of unique terms in the
           tag cloud

        """
        unique_terms = {}
        for field_id in self.term_forms:
            if field_id in input_data:
                input_data_field = input_data.get(field_id, '')
                if isinstance(input_data_field, str):
                    case_sensitive = self.term_analysis[field_id].get(
                        'case_sensitive', True)
                    token_mode = self.term_analysis[field_id].get(
                        'token_mode', 'all')
                    if token_mode != TM_FULL_TERM:
                        terms = parse_terms(input_data_field,
                                            case_sensitive=case_sensitive)
                    else:
                        terms = []
                    full_term = input_data_field if case_sensitive \
                        else input_data_field.lower()
                    # We add full_term if needed. Note that when there's
                    # only one term in the input_data, full_term and term are
                    # equal. Then full_term will not be added to avoid
                    # duplicated counters for the term.
                    if token_mode == TM_FULL_TERM or \
                            (token_mode == TM_ALL and (len(terms) == 0 or
                                                       terms[0] != full_term)):
                        terms.append(full_term)
                    unique_terms[field_id] = get_unique_terms(
                        terms, self.fields[field_id]["summary"]["term_forms"],
                        self.tag_clouds.get(field_id, []))
                else:
                    unique_terms[field_id] = [(input_data_field, 1)]
                del input_data[field_id]
        # the same for items fields
        #pylint: disable=locally-disabled,consider-using-dict-items
        for field_id in self.item_analysis:
            if field_id in input_data:
                input_data_field = input_data.get(field_id, '')
                if isinstance(input_data_field, str):
                    # parsing the items in input_data
                    separator = self.item_analysis[field_id].get(
                        'separator', ' ')
                    regexp = self.item_analysis[field_id].get(
                        'separator_regexp')
                    if regexp is None:
                        regexp = r'%s' % re.escape(separator)
                    terms = parse_items(input_data_field, regexp)
                    unique_terms[field_id] = get_unique_terms(
                        terms, {},
                        self.items.get(field_id, []))
                else:
                    unique_terms[field_id] = [(input_data_field, 1)]
                del input_data[field_id]

        if hasattr(self, "categories") and self.categories:
            for field_id in self.categories:
                if field_id in input_data:
                    input_data_field = input_data.get(field_id, '')
                    unique_terms[field_id] = [(input_data_field, 1)]
                    del input_data[field_id]
        return unique_terms

    def dump(self, output=None, cache_set=None):
        """Uses msgpack to serialize the resource object
        If cache_set is filled with a cache set method, the method is called

        """
        self_vars = vars(self)
        dump(self_vars, output=output, cache_set=cache_set)

    def dumps(self):
        """Uses msgpack to serialize the resource object to a string

        """
        self_vars = vars(self)
        return dumps(self_vars)
