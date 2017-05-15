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

"""A BasicModel resource.

This module defines a BasicModel to hold the main information of the model
resource in BigML. It becomes the starting point for the Model class, that
is used for local predictions.

"""
import logging
import sys
import locale
import os
import json

from bigml.api import FINISHED
from bigml.api import (get_status, BigML, get_model_id,
                       check_resource, get_resource_type)
from bigml.util import utf8
from bigml.util import DEFAULT_LOCALE
from bigml.modelfields import (ModelFields, check_model_structure,
                               check_model_fields)

LOGGER = logging.getLogger('BigML')

# Query string to ask for fields: only the ones in the model, with summary
# (needed for the list of terms in text fields) and
# no pagination (all the model fields)
ONLY_MODEL = 'only_model=true;limit=-1;'
EXCLUDE_FIELDS = 'exclude=fields;'


def retrieve_resource(api, resource_id, query_string='',
                      no_check_fields=False):
    """ Retrieves resource info either from a local repo or
        from the remote server

    """
    if api.storage is not None:
        try:
            stored_resource = "%s%s%s" % (api.storage, os.sep,
                                          resource_id.replace("/", "_"))
            with open(stored_resource) as resource_file:
                resource = json.loads(resource_file.read())
            # we check that the stored resource has enough fields information
            # for local predictions to work. Otherwise we should retrieve it.
            if no_check_fields or check_model_fields(resource):
                return resource
        except ValueError:
            raise ValueError("The file %s contains no JSON")
        except IOError:
            pass
    api_getter = api.getters[get_resource_type(resource_id)]
    resource = check_resource(resource_id, api_getter, query_string)
    return resource


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
    for [field, importance] in field_importance:
        out.write(utf8(u"    %s. %s: %.2f%%\n" % (
            count,
            fields[field]['name'],
            round(importance, 4) * 100)))
        count += 1


class BaseModel(ModelFields):
    """ A lightweight wrapper of the basic model information

    Uses a BigML remote model to build a local version that contains the
    main features of a model, except its tree structure.

    """

    def __init__(self, model, api=None, fields=None):

        if check_model_structure(model):
            self.resource_id = model['resource']
        else:
            # If only the model id is provided, the short version of the model
            # resource is used to build a basic summary of the model
            if api is None:
                api = BigML()
            self.resource_id = get_model_id(model)
            if self.resource_id is None:
                raise Exception(api.error_message(model,
                                                  resource_type='model',
                                                  method='get'))
            if fields is not None and isinstance(fields, dict):
                query_string = EXCLUDE_FIELDS
            else:
                query_string = ONLY_MODEL
            model = retrieve_resource(api, self.resource_id,
                                      query_string=query_string)
            # Stored copies of the model structure might lack some necessary
            # keys
            if not check_model_structure(model):
                model = api.get_model(self.resource_id,
                                      query_string=query_string)

        if 'object' in model and isinstance(model['object'], dict):
            model = model['object']

        if 'model' in model and isinstance(model['model'], dict):
            status = get_status(model)
            if 'code' in status and status['code'] == FINISHED:
                if (fields is None and ('model_fields' in model['model'] or
                                        'fields' in model['model'])):
                    fields = model['model'].get('model_fields',
                                                model['model'].get('fields',
                                                                   []))
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
                objective_field = model['objective_fields']
                ModelFields.__init__(
                    self, fields,
                    objective_id=extract_objective(objective_field))
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
