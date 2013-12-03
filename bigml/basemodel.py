# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2013 BigML
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

"""A BasicModel resource.

This module defines a BasicModel to hold the main information of the model
resource in BigML. It becomes the starting point for the Model class, that
is used for local predictions.

"""
import logging
LOGGER = logging.getLogger('BigML')

import sys
import locale
import os
import json

from bigml.api import FINISHED
from bigml.api import (get_status, error_message, BigML, get_model_id,
                       check_resource)
from bigml.util import invert_dictionary, utf8
from bigml.util import DEFAULT_LOCALE


ONLY_MODEL = 'only_model=true'
EXCLUDE_ROOT = 'exclude=root;shorten=true'


def retrieve_model(api, model_id, query_string=''):
    """ Retrieves model info either from a local repo or from the remote server

    """
    if api.storage is not None:
        try:
            with open("%s%s%s" % (api.storage, os.sep,
                                  model_id.replace("/", "_"))) as model_file:
                model = json.loads(model_file.read())
            return model
        except ValueError:
            raise ValueError("The file %s contains no JSON")
        except IOError:
            pass
    model = check_resource(model_id, api.get_model, query_string)
    return model


def extract_objective(objective_field):
    """Extract the objective field id from the model structure

    """
    if isinstance(objective_field, list):
        return objective_field[0]
    return objective_field


def print_importance(instance, out=sys.stdout):
    """Print a field importance structure

    """
    count = 1
    field_importance, fields = instance.field_importance_data()
    print field_importance
    for [field, importance] in field_importance:
        out.write(utf8(u"    %s. %s: %.2f%%\n" % (count,
                       fields[field]['name'],
                       round(importance, 4) * 100)))
        count += 1


class BaseModel(object):
    """ A lightweight wrapper of the basic model information

    Uses a BigML remote model to build a local version that contains the
    main features of a model, except its tree structure.

    """

    def __init__(self, model, api=None):

        if (isinstance(model, dict) and 'resource' in model and
                model['resource'] is not None):
            self.resource_id = model['resource']
        else:
            # If only the model id is provided, the short version of the model
            # resource is used to build a basic summary of the model
            if api is None:
                api = BigML()
            self.resource_id = get_model_id(model)
            if self.resource_id is None:
                raise Exception(error_message(model,
                                              resource_type='model',
                                              method='get'))
            query_string = '%s;%s' % (ONLY_MODEL, EXCLUDE_ROOT)
            model = retrieve_model(api, self.resource_id,
                                   query_string=query_string)

        if ('object' in model and isinstance(model['object'], dict)):
            model = model['object']

        if ('model' in model and isinstance(model['model'], dict)):
            status = get_status(model)
            if ('code' in status and status['code'] == FINISHED):
                if 'model_fields' in model['model']:
                    fields = model['model']['model_fields']
                    # pagination or exclusion might cause a field not to
                    # be in available fields dict
                    if not all(key in model['model']['fields']
                               for key in fields.keys()):
                        raise Exception("Some fields are missing"
                                        " to generate a local model."
                                        " Please, provide a model with"
                                        " the complete list of fields.")
                    for field in fields:
                        field_info = model['model']['fields'][field]
                        if 'summary' in field_info:
                            fields[field]['summary'] = field_info['summary']
                        fields[field]['name'] = field_info['name']
                else:
                    fields = model['model']['fields']
                objective_field = model['objective_fields']
                self.objective_field = extract_objective(objective_field)
                self.uniquify_varnames(fields)
                self.inverted_fields = invert_dictionary(fields)
                self.all_inverted_fields = invert_dictionary(model['model']
                                                             ['fields'])
                self.fields = fields
                self.description = model['description']
                self.field_importance = model['model'].get('importance',
                                                           None)
                if self.field_importance:
                    self.field_importance = [element for element
                                             in self.field_importance
                                             if element[0] in fields]
                self.locale = model.get('locale', DEFAULT_LOCALE)

            else:
                raise Exception("The model isn't finished yet")
        else:
            raise Exception("Cannot create the BaseModel instance. Could not"
                            " find the 'model' key in the resource:\n\n%s" %
                            model)

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
        unique_names = [fields[self.objective_field]['name']]

        field_ids = [field_id for field_id in fields
                     if field_id != self.objective_field]
        for field_id in field_ids:
            new_name = fields[field_id]['name']
            if new_name in unique_names:
                new_name = "{0}{1}".format(fields[field_id]['name'],
                                           fields[field_id]['column_number'])
                if new_name in unique_names:
                    new_name = "{0}_{1}".format(new_name, field_id)
                fields[field_id]['name'] = new_name
            unique_names.append(new_name)

    def resource(self):
        """Returns the model resource ID

        """
        return self.resource_id

    def field_importance_data(self):
        """Returns field importance related info

        """
        return self.field_importance, self.fields

    def print_importance(self, out=sys.stdout):
        """Prints the importance data

        """
        print_importance(self, out=out)
