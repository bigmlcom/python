# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2013-2020 BigML
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
from bigml.api import get_status, BigML, get_model_id, ID_GETTERS, \
    check_resource, get_resource_type, get_api_connection
from bigml.util import utf8
from bigml.util import DEFAULT_LOCALE
from bigml.modelfields import (ModelFields, check_model_structure,
                               check_model_fields)

LOGGER = logging.getLogger('BigML')

# Query string to ask for fields: only the ones in the model, with summary
# (needed for the list of terms in text fields) and
# no pagination (all the model fields)

# We need datefields in the download models, and apian sometimes
# remove them when we use only_model=true so we will set it to
# false until the problem in apian is fixed

ONLY_MODEL = 'only_model=false;limit=-1;'
EXCLUDE_FIELDS = 'exclude=fields;'


def retrieve_resource(api, resource_id, query_string=ONLY_MODEL,
                      no_check_fields=False, retries=None):
    """ Retrieves resource info either from a local repo or
        from the remote server

    """

    check_local_fn = None if no_check_fields else check_model_fields
    return api.retrieve_resource(resource_id, query_string=query_string,
                                 check_local_fn=check_local_fn,
                                 retries=retries)


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


def get_resource_dict(resource, resource_type, api=None):
    """Extracting the resource JSON info as a dict from the first argument of
       the local object constructors, that can be:

        - the path to a file that contains the JSON
        - the ID of the resource
        - the resource dict itself

    """

    get_id = ID_GETTERS[resource_type]
    resource_id = None
    # the string can be a path to a JSON file
    if isinstance(resource, basestring):
        try:
            with open(resource) as resource_file:
                resource = json.load(resource_file)
                resource_id = get_id(resource)
                if resource_id is None:
                    raise ValueError("The JSON file does not seem"
                                     " to contain a valid BigML %s"
                                     " representation." % resource_type)
        except IOError:
            # if it is not a path, it can be a model id
            resource_id = get_id(resource)
            if resource_id is None:
                if resource.find("%s/" % resource_type) > -1:
                    raise Exception(
                        api.error_message(resource,
                                          resource_type=resource_type,
                                          method="get"))
                else:
                    raise IOError("Failed to open the expected JSON file"
                                  " at %s." % resource)
        except ValueError:
            raise ValueError("Failed to interpret %s."
                             " JSON file expected." % resource)

    # checks whether the information needed for local predictions is in
    # the first argument
    if isinstance(resource, dict) and \
            not check_model_fields(resource):
        # if the fields used by the model are not
        # available, use only ID to retrieve it again
        resource = get_id(resource)
        resource_id = resource

    if not (isinstance(resource, dict) and 'resource' in resource and
            resource['resource'] is not None):
        query_string = ONLY_MODEL
        resource = retrieve_resource(api, resource_id,
                                     query_string=query_string)
    else:
        resource_id = get_id(resource)

    return resource_id, resource


def datetime_fields(fields):
    """Returns datetime fields from a dict of fields

    """
    return {k: v for k, v in fields.items() \
            if v.get("optype", False) == "datetime"}


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
            self.api = get_api_connection(api)
            self.resource_id = get_model_id(model)
            if self.resource_id is None:
                raise Exception(self.api.error_message(model,
                                                       resource_type='model',
                                                       method='get'))
            if fields is not None and isinstance(fields, dict):
                query_string = EXCLUDE_FIELDS
            else:
                query_string = ONLY_MODEL
            model = retrieve_resource(self.api, self.resource_id,
                                      query_string=query_string)
            # Stored copies of the model structure might lack some necessary
            # keys
            if not check_model_structure(model):
                model = self.api.get_model(self.resource_id,
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
                    # model_fields doesn't contain the datetime fields
                    fields.update(datetime_fields(model['model'].get('fields',
                                                                     {})))
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
                missing_tokens = model['model'].get('missing_tokens')

                ModelFields.__init__(
                    self, fields, objective_id=extract_objective(objective_field),
                    missing_tokens=missing_tokens)
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
