# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2013-2017 BigML
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

from bigml.util import invert_dictionary, DEFAULT_LOCALE
from bigml.fields import DEFAULT_MISSING_TOKENS
from bigml.resourcehandler import get_resource_type
from bigml.predicate import TM_FULL_TERM, TM_ALL


LOGGER = logging.getLogger('BigML')

FIELDS_PARENT = { \
    "cluster": "clusters",
    "logisticregression": "logistic_regression",
    "ensemble": "ensemble",
    "deepnet": "deepnet"}


def parse_terms(text, case_sensitive=True):
    """Returns the list of parsed terms

    """
    if text is None:
        return []
    expression = ur'(\b|_)([^\b_\s]+?)(\b|_)'
    pattern = re.compile(expression)
    return [match[1] if case_sensitive else match[1].lower()
            for match in re.findall(pattern, text)]


def parse_items(text, regexp):
    """Returns the list of parsed items

    """
    if text is None:
        return []
    pattern = re.compile(regexp, flags=re.U)
    return pattern.split(text)


def check_model_structure(model, inner_key="model"):
    """Checks the model structure to see if it contains all the
    main expected keys

    """
    return (isinstance(model, dict) and 'resource' in model and
            model['resource'] is not None and
            ('object' in model and inner_key in model['object'] or
             inner_key in model))


def get_unique_terms(terms, term_forms, tag_cloud):
    """Extracts the unique terms that occur in one of the alternative forms in
       term_forms or in the tag cloud.

    """

    extend_forms = {}
    for term, forms in term_forms.items():
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
    return terms_set.items()


def check_model_fields(model):
    """Checks the model structure to see whether it contains the required
    fields information

    """
    inner_key = FIELDS_PARENT.get(get_resource_type(model), 'model')
    if check_model_structure(model, inner_key):
        model = model.get('object', model)
        fields = model.get("fields", model.get(inner_key, {}).get('fields'))
        # models only need model_fields to work. The rest of resources will
        # need all fields to work
        model_fields = model.get(inner_key, {}).get( \
            'model_fields', {}).keys()
        if not model_fields:
            fields_meta = model.get('fields_meta', \
                model.get(inner_key, {}).get('fields_meta', {}))
            try:
                return fields_meta['count'] == fields_meta['total']
            except KeyError:
                # stored old models will not have the fields_meta info, so
                # we return True to avoid failing in this case
                return True
        else:
            if fields is None:
                return False
            return all([field_id in fields.keys() \
                for field_id in model_fields])
    return False


class ModelFields(object):
    """ A lightweight wrapper of the field information in the model, cluster
    or anomaly objects

    """

    def __init__(self, fields, objective_id=None, data_locale=None,
                 missing_tokens=None, terms=False, categories=False,
                 numerics=False):
        if isinstance(fields, dict):
            try:
                self.objective_id = objective_id
                self.uniquify_varnames(fields)
                self.inverted_fields = invert_dictionary(fields)
                self.fields = {}
                self.fields.update(fields)
                self.data_locale = data_locale
                self.missing_tokens = missing_tokens
                if self.data_locale is None:
                    self.data_locale = DEFAULT_LOCALE
                if self.missing_tokens is None:
                    self.missing_tokens = DEFAULT_MISSING_TOKENS
                if terms:
                    # adding text and items information to handle terms
                    # expansion
                    self.term_forms = {}
                    self.tag_clouds = {}
                    self.term_analysis = {}
                    self.items = {}
                    self.item_analysis = {}
                if categories:
                    self.categories = {}
                if terms or categories or numerics:
                    self.add_terms(categories, numerics)

            except KeyError:
                raise Exception("Wrong field structure.")

    def add_terms(self, categories=False, numerics=False):
        """Adds the terms information of text and items fields

        """
        for field_id, field in self.fields.items():
            if field['optype'] == 'text':
                self.term_forms[field_id] = {}
                self.term_forms[field_id].update(
                    field['summary']['term_forms'])
                self.tag_clouds[field_id] = []
                self.tag_clouds[field_id] = [tag for [tag, _] in field[
                    'summary']['tag_cloud']]
                self.term_analysis[field_id] = {}
                self.term_analysis[field_id].update(
                    field['term_analysis'])
            if field['optype'] == 'items':
                self.items[field_id] = []
                self.items[field_id] = [item for item, _ in \
                    field['summary']['items']]
                self.item_analysis[field_id] = {}
                self.item_analysis[field_id].update(
                    field['item_analysis'])
            if categories and field['optype'] == 'categorical':
                self.categories[field_id] = [category for \
                    [category, _] in field['summary']['categories']]
            if numerics and self.missing_numerics and \
                    field['optype'] == 'numeric':
                self.numeric_fields[field_id] = True


    def uniquify_varnames(self, fields):
        """Tests if the fields names are unique. If they aren't, a
           transformation is applied to ensure unicity.

        """
        unique_names = set([fields[key]['name'] for key in fields])
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
        if isinstance(value, basestring) and not isinstance(value, unicode):
            value = unicode(value, "utf-8")
        return None if value in self.missing_tokens else value

    def filter_input_data(self, input_data, by_name=True,
                          add_unused_fields=False):
        """Filters the keys given in input_data checking against model fields.
        If `add_unused_fields` is set to True, it also
        provides information about the ones that are not used.

        """

        unused_fields = []
        new_input = {}
        if isinstance(input_data, dict):
            # remove all missing values
            for key, value in input_data.items():
                value = self.normalize(value)
                if value is None:
                    del input_data[key]

            if by_name:
                # We no longer check that the input data keys match some of
                # the dataset fields. We only remove the keys that are not
                # used as predictors in the model
                for key, value in input_data.items():
                    if key in self.inverted_fields and \
                            (self.objective_id is None or \
                             self.inverted_fields[key] != self.objective_id):
                        new_input[self.inverted_fields[key]] = value
                    else:
                        unused_fields.append(key)
            else:
                for key, value in input_data.items():
                    if key in self.fields and \
                            (self.objective_id is None or \
                             key != self.objective_id):
                        new_input[key] = value
                    else:
                        unused_fields.append(key)
            result = (new_input, unused_fields) if add_unused_fields else \
                new_input
            return result
        else:
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
                if isinstance(input_data_field, basestring):
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
                            (token_mode == TM_ALL and terms[0] != full_term):
                        terms.append(full_term)
                    unique_terms[field_id] = get_unique_terms(
                        terms, self.term_forms[field_id],
                        self.tag_clouds.get(field_id, []))
                else:
                    unique_terms[field_id] = [(input_data_field, 1)]
                del input_data[field_id]
        # the same for items fields
        for field_id in self.item_analysis:
            if field_id in input_data:
                input_data_field = input_data.get(field_id, '')
                if isinstance(input_data_field, basestring):
                    # parsing the items in input_data
                    separator = self.item_analysis[field_id].get(
                        'separator', ' ')
                    regexp = self.item_analysis[field_id].get(
                        'separator_regexp')
                    if regexp is None:
                        regexp = ur'%s' % re.escape(separator)
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
