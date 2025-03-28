# -*- coding: utf-8 -*-
#pylint: disable=unbalanced-tuple-unpacking
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

"""A class to deal with the fields of a resource.

This module helps to map between ids, names, and column_numbers in the
fields of source, dataset, or model. Also to validate your input data
for predictions or to list all the fields from a resource.

from bigml.api import BigML
from bigml.fields import Fields

api = BigML()

source = api.get_source("source/50a6bb94eabcb404d3000174")
fields = Fields(source['object']['fields'])

dataset = api.get_dataset("dataset/50a6bb96eabcb404cd000342")
fields = Fields(dataset['object']['fields'])

# Note that the fields in a model come one level deeper
model = api.get_model("model/50a6bbac035d0706db0008f8")
fields = Fields(model['object']['model']['fields'])

prediction = api.get_prediction("prediction/50a69688035d0706dd00044d")
fields =  Fields(prediction['object']['fields'])


"""
import sys
import json
import csv
import random
import numpy as np

try:
    from pandas import DataFrame
    PANDAS_READY = True
except ImportError:
    PANDAS_READY = False


from bigml.util import invert_dictionary, python_map_type, find_locale
from bigml.util import DEFAULT_LOCALE
from bigml.api_handlers.resourcehandler import get_resource_type, get_fields
from bigml.constants import (
    SOURCE_PATH, DATASET_PATH, SUPERVISED_PATHS, FUSION_PATH,
    RESOURCES_WITH_FIELDS, DEFAULT_MISSING_TOKENS, REGIONS, CATEGORICAL)
from bigml.io import UnicodeReader, UnicodeWriter

LIST_LIMIT = 10
REGIONS_ATTR = "labels"
SUMMARY_HEADERS = ["field column", "field ID", "field name", "field label",
                   "field description", "field type", "preferred",
                   "missing count", "errors", "contents summary",
                   "errors summary"]

UPDATABLE_HEADERS = {"field name": "name",
                     "field label": "label",
                     "field description": "description",
                     "field type": "optype",
                     "preferred": "preferred"}

ITEM_SINGULAR = {"categories": "category"}


def get_fields_structure(resource, errors=False):
    """Returns the field structure for a resource, its locale and
       missing_tokens

    """
    try:
        resource_type = get_resource_type(resource)
    except ValueError:
        raise ValueError("Unknown resource structure")
    field_errors = None
    resource = resource.get('object', resource)
    # locale and missing tokens
    if resource_type == SOURCE_PATH:
        resource_locale = resource['source_parser']['locale']
        missing_tokens = resource[
            'source_parser']['missing_tokens']
    else:
        resource_locale = resource.get('locale', DEFAULT_LOCALE)
        missing_tokens = resource.get('missing_tokens',
                                      DEFAULT_MISSING_TOKENS)

    fields = get_fields(resource)
    if resource_type in RESOURCES_WITH_FIELDS:
        # Check whether there's an objective id
        objective_column = None
        if resource_type == DATASET_PATH:
            objective_column = resource.get( \
                'objective_field', {}).get('id')
            if errors:
                field_errors = resource.get("status", {}).get("field_errors")
        elif resource_type in SUPERVISED_PATHS and \
                resource_type != FUSION_PATH:
            objective_id = resource.get( \
                'objective_fields', [None])[0]
            objective_column = fields.get( \
                objective_id, {}).get('column_number')
        result = fields, resource_locale, missing_tokens, objective_column
        if errors:
            result = result + (field_errors,)
        return result
    return (None, None, None, None, None) if errors else \
        (None, None, None, None)


def attribute_summary(attribute_value, item_type, limit=None):
    """Summarizes the information in fields attributes where content is
       written as an array of arrays like tag_cloud, items, etc.
    """
    if attribute_value is None:
        return None
    if item_type != REGIONS_ATTR:
        items = ["%s (%s)" % (item, instances) for
                 item, instances in attribute_value]
        items_length = len(items)
        if limit is None or limit > items_length:
            limit = items_length
        return "%s %s: %s" % (items_length, type_singular(item_type,
                                                          items_length == 1),
                              ", ".join(items[0: limit]))
    items = ["%s (%s)" % (attr.get("label"), attr.get("count")) for
             attr in attribute_value]
    items_length = len(items)
    if limit is None or limit > items_length:
        limit = items_length
    return "%s %s: %s" % (items_length, type_singular(item_type,
                                                      items_length == 1),
                          ", ".join(items[0: limit]))


def type_singular(item_type, singular=False):
    """Singularizes item types if needed

    """
    if singular:
        return ITEM_SINGULAR.get(item_type, item_type[:-1])
    return item_type


def numeric_example(numeric_summary):
    """Generates a random numeric example in the gaussian defined by
    mean and sigma in the numeric_summary

    """
    try:
        mean = numeric_summary.get("mean")
        sigma = numeric_summary.get("standard_deviation")
        minimum = numeric_summary.get("minimum")
        maximum = numeric_summary.get("maximum")
        value = -1
        while value < minimum or value > maximum:
            value = random.gauss(mean, sigma)
        return value
    except TypeError:
        return None


def sorted_headers(fields):
    """Listing the names of the fields as ordered in the original dataset.
    The `fields` parameter is a Fields object.
    """
    header_names = []
    header_ids = []
    for column in fields.fields_columns:
        header_names.append(fields.fields[
            fields.fields_by_column_number[column]]["name"])
        header_ids.append(fields.fields_by_column_number[column])

    return header_names, header_ids


def get_new_fields(output_fields):
    """Extracts the sexpr and names of the output fields in a dataset
    generated from a new_fields transformation.
    """
    new_fields = []
    for output_field in output_fields:
        sexp = output_field.get("generator")
        names = output_field.get("names")
        new_fields.append({"field": sexp, "names": names})
    return new_fields


def one_hot_code(value, field, decode=False):
    """Translating into codes categorical values. The codes are the index
    of the value in the list of categories read from the fields summary.
    Decode set to True will cause the code to be translated to the value"""

    try:
        categories = [cat[0] for cat in field["summary"]["categories"]]
    except KeyError:
        raise KeyError("Failed to find the categories list. Check the field"
                       " information.")

    if decode:
        try:
            result = categories[int(value)]
        except KeyError:
            raise KeyError("Code not found in the categories list. %s" %
                           categories)
    else:
        try:
            result = categories.index(value)
        except ValueError:
            raise ValueError("The '%s' value is not found in the categories "
                             "list: %s" % (value, categories))
    return result


class Fields():
    """A class to deal with BigML auto-generated ids.

    """
    def __init__(self, resource_or_fields, missing_tokens=None,
                 data_locale=None, verbose=False,
                 objective_field=None, objective_field_present=False,
                 include=None, errors=None):

        # The constructor can be instantiated with resources or a fields
        # structure. The structure is checked and fields structure is returned
        # if a resource type is matched.
        try:
            self.resource_type = get_resource_type(resource_or_fields)
            resource_info = get_fields_structure(resource_or_fields, True)
            (self.fields,
             resource_locale,
             resource_missing_tokens,
             objective_column,
             resource_errors) = resource_info
            if data_locale is None:
                data_locale = resource_locale
            if missing_tokens is None:
                if resource_missing_tokens:
                    missing_tokens = resource_missing_tokens
            if errors is None:
                errors = resource_errors
        except ValueError:
            # If the resource structure is not in the expected set, fields
            # structure is assumed
            self.fields = resource_or_fields
            if data_locale is None:
                data_locale = DEFAULT_LOCALE
            if missing_tokens is None:
                missing_tokens = DEFAULT_MISSING_TOKENS
            objective_column = None
        if self.fields is None:
            raise ValueError("No fields structure was found.")
        self.fields_by_name = invert_dictionary(self.fields, 'name')
        self.fields_by_column_number = invert_dictionary(self.fields,
                                                         'column_number')
        find_locale(data_locale, verbose)
        self.missing_tokens = missing_tokens
        self.fields_columns = sorted(self.fields_by_column_number.keys())
        # Ids of the fields to be included
        self.filtered_fields = (list(self.fields.keys()) if include is None
                                else include)
        # To be updated in update_objective_field
        self.row_ids = None
        self.headers = None
        self.objective_field = None
        self.objective_field_present = None
        self.filtered_indexes = None
        self.field_errors = errors
        # if the objective field is not set by the user
        # use the one extracted from the resource info
        if objective_field is None and objective_column is not None:
            objective_field = objective_column
            objective_field_present = True
        if self.fields:
            # empty composite sources will not have an objective field
            self.update_objective_field(objective_field,
                                        objective_field_present)

    def update_objective_field(self, objective_field, objective_field_present,
                               headers=None):
        """Updates objective_field and headers info

            Permits to update the objective_field, objective_field_present and
            headers info from the constructor and also in a per row basis.
        """
        # If no objective field, select the last column, else store its column
        if objective_field is None:
            self.objective_field = self.fields_columns[-1]
        elif isinstance(objective_field, str):
            try:
                self.objective_field = self.field_column_number( \
                    objective_field)
            except KeyError:
                # if the name of the objective field is not found, use the last
                # field as objective
                self.objective_field = self.fields_columns[-1]
        else:
            self.objective_field = objective_field

        # If present, remove the objective field from the included fields
        objective_id = self.field_id(self.objective_field)
        if objective_id in self.filtered_fields:
            del self.filtered_fields[self.filtered_fields.index(objective_id)]

        self.objective_field_present = objective_field_present
        if headers is None:
            # The row is supposed to contain the fields sorted by column number
            self.row_ids = [item[0] for item in
                            sorted(list(self.fields.items()),
                                   key=lambda x: x[1]['column_number'])
                            if objective_field_present or
                            item[1]['column_number'] != self.objective_field]
            self.headers = self.row_ids
        else:
            # The row is supposed to contain the fields as sorted in headers
            self.row_ids = [self.field_id(header) for header in headers]
            self.headers = headers
        # Mapping each included field to its correspondent index in the row.
        # The result is stored in filtered_indexes.
        self.filtered_indexes = []
        for field in self.filtered_fields:
            try:
                index = self.row_ids.index(field)
                self.filtered_indexes.append(index)
            except ValueError:
                continue

    def field_id(self, key):
        """Returns a field id.

        """

        if isinstance(key, str):
            try:
                f_id = self.fields_by_name[key]
            except KeyError:
                raise ValueError("Error: field name '%s' does not exist" % key)
            return f_id
        if isinstance(key, int):
            try:
                f_id = self.fields_by_column_number[key]
            except KeyError:
                raise ValueError("Error: field column number '%s' does not"
                                 " exist" % key)
            return f_id
        return None

    def field_name(self, key):
        """Returns a field name.

        """
        if isinstance(key, str):
            try:
                name = self.fields[key]['name']
            except KeyError:
                raise ValueError("Error: field id '%s' does not exist" % key)
            return name
        if isinstance(key, int):
            try:
                name = self.fields[self.fields_by_column_number[key]]['name']
            except KeyError:
                raise ValueError("Error: field column number '%s' does not"
                                 " exist" % key)
            return name
        return None

    def field_column_number(self, key):
        """Returns a field column number.

        """
        try:
            return self.fields[key]['column_number']
        except KeyError:
            return self.fields[self.fields_by_name[key]]['column_number']

    def len(self):
        """Returns the number of fields.

        """
        return len(self.fields)

    def pair(self, row, headers=None,
             objective_field=None, objective_field_present=None):
        """Pairs a list of values with their respective field ids.

            objective_field is the column_number of the objective field.

           `objective_field_present` must be True is the objective_field column
           is present in the row.

        """
        # Try to get objective field form Fields or use the last column
        if objective_field is None:
            if self.objective_field is None:
                objective_field = self.fields_columns[-1]
            else:
                objective_field = self.objective_field
        # If objective fields is a name or an id, retrive column number
        if isinstance(objective_field, str):
            objective_field = self.field_column_number(objective_field)

        # Try to guess if objective field is in the data by using headers or
        # comparing the row length to the number of fields
        if objective_field_present is None:
            if headers:
                objective_field_present = (self.field_name(objective_field) in
                                           headers)
            else:
                objective_field_present = len(row) == self.len()

        # If objective field, its presence or headers have changed, update
        if (objective_field != self.objective_field or
                objective_field_present != self.objective_field_present or
                (headers is not None and headers != self.headers)):
            self.update_objective_field(objective_field,
                                        objective_field_present, headers)

        row = [self.normalize(info) for info in row]
        return self.to_input_data(row)

    def list_fields(self, out=sys.stdout):
        """Lists a description of the fields.

        """
        for field in [(val['name'], val['optype'], val['column_number'])
                      for _, val in sorted(list(self.fields.items()),
                                           key=lambda k:
                                           k[1]['column_number'])]:
            out.write('[%-32s: %-16s: %-8s]\n' % (field[0],
                                                  field[1], field[2]))
            out.flush()

    def preferred_fields(self):
        """Returns fields where attribute preferred is set to True or where
           it isn't set at all.

        """
        return {key: field for key, field in self.fields.items()
                if ('preferred' not in field) or field['preferred']}

    def validate_input_data(self, input_data, out=sys.stdout):
        """Validates whether types for input data match types in the
        fields definition.

        """
        if isinstance(input_data, dict):
            for name in input_data:
                if name in self.fields_by_name:
                    out.write('[%-32s: %-16s: %-16s: ' %
                              (name, type(input_data[name]),
                               self.fields[self.fields_by_name[name]]
                               ['optype']))
                    if (type(input_data[name]) in python_map_type(self.fields[
                            self.fields_by_name[name]]['optype'])):
                        out.write('OK\n')
                    else:
                        out.write('WRONG\n')
                else:
                    out.write("Field '%s' does not exist\n" % name)
        else:
            out.write("Input data must be a dictionary")

    def normalize(self, value):
        """Transforms to unicode and cleans missing tokens

        """
        if not isinstance(value, str):
            value = str(value, "utf-8")
        return None if value in self.missing_tokens else value

    def to_input_data(self, row):
        """Builds dict with field, value info only for the included headers

        """
        pair = []
        for index in self.filtered_indexes:
            pair.append((self.headers[index], row[index]))
        return dict(pair)

    def missing_counts(self):
        """Returns the ids for the fields that contain missing values

        """
        summaries = [(field_id, field.get('summary', {}))
                     for field_id, field in list(self.fields.items())]
        if len(summaries) == 0:
            raise ValueError("The structure has not enough information "
                             "to extract the fields containing missing values."
                             "Only datasets and models have such information. "
                             "You could retry the get remote call "
                             " with 'limit=-1' as query string.")

        return {field_id: summary.get('missing_count', 0)
                for field_id, summary in summaries
                if summary.get('missing_count', 0) > 0}

    def stats(self, field_name):
        """Returns the summary information for the field

        """
        field_id = self.field_id(field_name)
        summary = self.fields[field_id].get('summary', {})
        return summary

    def objective_field_info(self):
        """Returns the fields structure for the objective field"""
        if self.objective_field is None:
            return None
        objective_id = self.field_id(self.objective_field)
        return {objective_id: self.fields[objective_id]}

    def sorted_field_ids(self, objective=False):
        """List of field IDs ordered by column number. If objective is
        set to False, the objective field will be excluded.
        """
        fields = {}
        fields.update(self.fields_by_column_number)
        if not objective and self.objective_field is not None:
            del(fields[self.objective_field])
        field_ids = fields.values()
        return field_ids

    def to_numpy(self, input_data_list, objective=False):
        """Transforming input data to numpy syntax. Fields are sorted
        in the dataset order and categorical fields are one-hot encoded.
        If objective set to False, the objective field will not be included"""
        if PANDAS_READY and isinstance(input_data_list, DataFrame):
            inner_data_list = input_data_list.to_dict('records')
        else:
            inner_data_list = input_data_list
        field_ids = self.sorted_field_ids(objective=objective)
        np_input_list = np.empty(shape=(len(input_data_list),
                                        len(field_ids)))
        for index, input_data in enumerate(inner_data_list):
            np_input = np.array([])
            for field_id in field_ids:
                field_input = input_data.get(field_id,
                    input_data.get(self.field_name(field_id)))
                field = self.fields[field_id]
                if field["optype"] == CATEGORICAL:
                    field_input = one_hot_code(field_input, field)
                np_input = np.append(np_input, field_input)
            np_input_list[index] = np_input
        return np_input_list

    def from_numpy(self, np_data_list, objective=False, by_name=True):
        """Transforming input data from numpy syntax. Fields are sorted
        in the dataset order and categorical fields are one-hot encoded."""
        input_data_list = []
        field_ids = self.sorted_field_ids(objective=objective)
        for np_data in np_data_list:
            if len(np_data) != len(field_ids):
                raise ValueError("Wrong number of features in data: %s"
                " found, %s expected" % (len(np_data), len(field_ids)))
            input_data = {}
            for index, field_id in enumerate(field_ids):
                field_input = None if np.isnan(np_data[index]) else \
                    np_data[index]
                field = self.fields[field_id]
                if field["optype"] == CATEGORICAL:
                    field_input = one_hot_code(field_input, field, decode=True)
                if by_name:
                    field_id = self.fields[field_id]["name"]
                input_data.update({field_id: field_input})
            input_data_list.append(input_data)
        return input_data_list

    def one_hot_codes(self, field_name):
        """Returns the codes used for every category in a categorical field"""
        field = self.fields[self.field_id(field_name)]
        if field["optype"] != CATEGORICAL:
            raise ValueError("Only categorical fields are encoded")
        categories = [cat[0] for cat in field["summary"]["categories"]]
        return dict(zip(categories, range(0, len(categories))))

    def summary_csv(self, filename=None):
        """Summary of the contents of the fields

        """

        summary = []
        writer = None
        if filename is not None:
            writer = UnicodeWriter(filename,
                                   quoting=csv.QUOTE_NONNUMERIC).open_writer()
            writer.writerow(SUMMARY_HEADERS)
        else:
            summary.append(SUMMARY_HEADERS)

        for field_column in self.fields_columns:
            field_id = self.field_id(field_column)
            field = self.fields.get(field_id)
            field_summary = []
            field_summary.append(field.get('column_number'))
            field_summary.append(field_id)
            field_summary.append(field.get('name'))
            field_summary.append(field.get('label'))
            field_summary.append(field.get('description'))
            field_summary.append(field.get('optype'))
            field_summary_value = field.get('summary', {})

            if not field_summary_value:
                field_summary.append("") # no preferred info
                field_summary.append("") # no missing info
                field_summary.append("") # no error info
                field_summary.append("") # no content summary
                field_summary.append("") # no error summary
            else:
                field_summary.append(json.dumps(field.get('preferred')))
                field_summary.append(field_summary_value.get("missing_count"))
                if self.field_errors and field_id in list(self.field_errors.keys()):
                    errors = self.field_errors.get(field_id)
                    field_summary.append(errors.get("total"))
                else:
                    field_summary.append("0")
                if field['optype'] == 'numeric':
                    field_summary.append("[%s, %s], mean: %s" % \
                        (field_summary_value.get("minimum"),
                         field_summary_value.get("maximum"),
                         field_summary_value.get("mean")))
                elif field['optype'] == 'categorical':
                    categories = field_summary_value.get("categories")
                    field_summary.append( \
                        attribute_summary(categories, "categorìes",
                                          limit=LIST_LIMIT))
                elif field['optype'] == REGIONS:
                    labels_info = field_summary_value.get("labels")
                    field_summary.append( \
                        attribute_summary(labels_info, "labels",
                                          limit=LIST_LIMIT))
                elif field['optype'] == "text":
                    terms = field_summary_value.get("tag_cloud")
                    field_summary.append( \
                        attribute_summary(terms, "terms",
                                          limit=LIST_LIMIT))
                elif field['optype'] == "items":
                    items = field_summary_value.get("items")
                    field_summary.append( \
                        attribute_summary(items, "items", limit=LIST_LIMIT))
                else:
                    field_summary.append("")
                if self.field_errors and field_id in list(self.field_errors.keys()):
                    field_summary.append( \
                        attribute_summary(errors.get("sample"), "errors",
                                          limit=None))
                else:
                    field_summary.append("")
            if writer:
                writer.writerow(field_summary)
            else:
                summary.append(field_summary)
        if writer is None:
            return summary
        writer.close_writer()
        return filename

    def new_fields_structure(self, csv_attributes_file=None,
                             attributes=None, out_file=None):
        """Builds the field structure needed to update a fields dictionary
        in a BigML resource.

        :param csv_attributes_file: (string) Path to a CSV file like the one
                                             generated by summary_csv.
        :param attributes: (list) list of rows containing the
                                  attributes information ordered
                                  as in the summary_csv output.
        :param out_file: (string) Path to a JSON file that will be used
                                  to store the new fields structure. If None,
                                  the output is returned as a dict.
        """
        if csv_attributes_file is not None:
            reader = UnicodeReader(csv_attributes_file).open_reader()
            attributes = list(reader)
        new_fields_structure = {}
        if "field ID" in attributes[0] or "field column" in attributes[0]:
            # headers are used
            for index in range(1, len(attributes)):
                new_attributes = dict(list(zip(attributes[0],
                                               attributes[index])))
                if new_attributes.get("field ID"):
                    field_id = new_attributes.get("field ID")
                    if not field_id in list(self.fields.keys()):
                        raise ValueError("Field ID %s not found"
                                         " in this resource" % field_id)
                    del new_attributes["field ID"]
                else:
                    try:
                        field_column = int(new_attributes.get("field column"))
                    except TypeError:
                        raise ValueError(
                            "Field column %s not found"
                            " in this resource" % new_attributes.get(
                            "field_column"))
                    if not field_column in self.fields_columns:
                        raise ValueError("Field column %s not found"
                                         " in this resource" % field_column)
                    field_id = self.field_id(field_column)
                    del new_attributes["field column"]
                new_attributes_headers = list(new_attributes.keys())
                for attribute in new_attributes_headers:
                    if not attribute in list(UPDATABLE_HEADERS.keys()):
                        del new_attributes[attribute]
                    else:
                        new_attributes[UPDATABLE_HEADERS[attribute]] = \
                            new_attributes[attribute]
                        if attribute != UPDATABLE_HEADERS[attribute]:
                            del new_attributes[attribute]
                if "preferred" in new_attributes:
                    new_attributes['preferred'] = json.loads( \
                        new_attributes['preferred'])
                new_fields_structure[field_id] = new_attributes
        else:
            # assume the order given in the summary_csv method
            first_attribute = attributes[0][0]
            first_column_is_id = False
            try:
                field_id = self.field_id(int(first_attribute))
            except ValueError:
                field_id = first_attribute
                first_column_is_id = True
            if not field_id in self.fields:
                raise ValueError("The first column should contain either the"
                                 " column or ID of the fields. Failed to find"
                                 " %s as either of them." % field_id)
            headers = SUMMARY_HEADERS[2: 7]
            headers = [UPDATABLE_HEADERS[header] for header in headers]
            try:
                for field_attributes in attributes:
                    if field_attributes[6] is not None:
                        field_attributes[6] = json.loads(field_attributes[6])
                    field_id = field_attributes[0] if first_column_is_id else \
                        self.field_id(int(field_attributes[0]))
                    new_fields_structure[field_id] = \
                        dict(list(zip(headers, field_attributes[1: 6])))
            except ValueError:
                raise ValueError("The first column should contain either the"
                                 " column or ID of the fields. Failed to find"
                                 " %s as either of them." % field_id)
        new_fields_structure = {"fields": new_fields_structure}
        if out_file is None:
            return new_fields_structure
        try:
            with open(out_file, "w") as out:
                json.dump(new_fields_structure, out)
        except IOError:
            raise IOError("Failed writing the fields structure file in"
                          " %s- Please, check your arguments." %
                          out_file)
        return out_file

    def training_data_example(self, missings=False):
        """Generates an example of training data based on the contents of the
        summaries of every field

        If missings is set to true, missing values are allowed

        """
        training_data = {}
        for _, field in list(self.fields.items()):
            if field.get("summary") is not None:
                value = None
                optype = field.get("optype")
                if optype == "numeric":
                    if missings and random.randint(0, 5) > 3:
                        value = None
                    else:
                        value = numeric_example(field["summary"])
                if optype == "categorical":
                    if missings and random.randint(0, 5) > 3:
                        value = None
                    else:
                        categories = [cat[0] for cat in field["summary"]["categories"]]
                        weights = [cat[1] for cat in field["summary"]["categories"]]
                        value = random.choices(categories, weights)[0]
                if optype == "text":
                    if missings and random.randint(0, 5) > 3:
                        value = None
                    else:
                        text_number = len(field["summary"]["tag_cloud"])
                        index = random.randint(0, text_number - 1)
                        value = field["summary"]["tag_cloud"][index][0]
                if optype == "items":
                    if missings and random.randint(0, 5) > 3:
                        value = None
                    else:
                        items_number = len(field["summary"]["items"])
                        index = random.randint(0, items_number - 1)
                        value = field["summary"]["items"][index][0]
                if optype == REGIONS:
                    if missings and random.randint(0, 5) > 3:
                        value = None
                    else:
                        labels_number = len(field["summary"]["labels"])
                        index = random.randint(0, labels_number - 1)
                        field_summary = field["summary"]["labels"][index]
                        label = field_summary["label"]
                        xmin = numeric_example(field_summary["xmin"])
                        xmax = numeric_example(field_summary["xmax"])
                        ymin = numeric_example(field_summary["ymin"])
                        ymax = numeric_example(field_summary["ymax"])
                        #pylint: disable=locally-disabled,too-many-boolean-expressions
                        if None in [xmin, xmax, ymin, ymax] or xmax < xmin or \
                                ymax < ymin or xmin < 0 or xmax < 0 or \
                                ymin < 0 or ymax < 0:
                            value = []
                        else:
                            value = [[label, xmin, xmax, ymin, ymax]]

                if value is not None:
                    training_data.update({field["name"]: value})
        return training_data

    def filter_fields_update(self, update_body):
        """Filters the updatable attributes according to the type of resource

        """
        fields_info = update_body.get("fields")
        if self.resource_type and fields_info is not None:
            if self.resource_type == "dataset":
                for _, field in list(fields_info.items()):
                    if field.get("optype") is not None:
                        del field["optype"]
            elif self.resource_type == "source":
                for _, field in list(fields_info.items()):
                    if field.get("preferred") is not None:
                        del field["preferred"]
            update_body["fields"] = fields_info
        return update_body
