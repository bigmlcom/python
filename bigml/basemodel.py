# -*- coding: utf-8 -*-
#
# Copyright 2013-2022 BigML
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
import json

from bigml.api import FINISHED
from bigml.api import get_status, get_model_id, ID_GETTERS, \
    get_api_connection
from bigml.util import utf8
from bigml.util import DEFAULT_LOCALE
from bigml.modelfields import ModelFields, check_model_structure, \
    check_model_fields
from bigml.api_handlers.resourcehandler import resource_is_ready

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

    check_local_fn = check_local_but_fields if no_check_fields \
        else check_local_info
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
        out.write(utf8("    %s. %s: %.2f%%\n" % (
            count,
            fields[field]['name'],
            round(importance, 4) * 100)))
        count += 1


def check_local_but_fields(model):
    """Whether the information in `model` is enough to use it locally
       except for the fields section

    """
    try:

        return resource_is_ready(model) and \
            check_model_structure(model)
    except Exception:
        return False


def check_local_info(model):
    """Whether the information in `model` is enough to use it locally

    """
    try:
        return check_local_but_fields(model) and \
            check_model_fields(model)
    except Exception:
        return False

def get_resource_dict(resource, resource_type, api=None,
                      no_check_fields=False):
    """Extracting the resource JSON info as a dict from the first argument of
       the local object constructors, that can be:

        - the path to a file that contains the JSON
        - the ID of the resource
        - the resource dict itself

    """

    get_id = ID_GETTERS[resource_type]
    resource_id = None
    # the string can be a path to a JSON file
    if isinstance(resource, str):
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
                raise IOError("Failed to open the expected JSON file"
                              " at %s." % resource)
        except ValueError:
            raise ValueError("Failed to interpret %s."
                             " JSON file expected." % resource)

    # dict resource or file path argument:
    # checks whether the information needed for local predictions is in
    # the first argument
    check_fn = check_local_but_fields if no_check_fields else \
        check_local_info

    if isinstance(resource, dict) and not check_fn( \
            resource):
        # if the fields used by the model are not
        # available, use only ID to retrieve it again
        resource = get_id(resource)
        resource_id = resource

    # resource ID or failed resource info:
    # trying to read the resource from storage or from the API
    if not (isinstance(resource, dict) and 'resource' in resource and
            resource['resource'] is not None):
        query_string = ONLY_MODEL
        resource = retrieve_resource(api, resource_id,
                                     query_string=query_string,
                                     no_check_fields=no_check_fields)
    else:
        resource_id = get_id(resource)

    return resource_id, resource


def datetime_fields(fields):
    """Returns datetime fields from a dict of fields

    """
    return {k: v for k, v in list(fields.items()) \
            if v.get("optype", False) == "datetime"}


class BaseModel(ModelFields):
    """ A lightweight wrapper of the basic model information

    Uses a BigML remote model to build a local version that contains the
    main features of a model, except its tree structure.
        model: the model dict or ID
        api: connection to the API
        fields: fields dict (used in ensembles where fields info can be shared)
        checked: boolean that avoids rechecking the model structure when it
                 has already been checked previously in a derived class
        operation_settings: operation thresholds for the classification model

    """

    def __init__(self, model, api=None, fields=None, checked=True,
                 operation_settings=None):

        check_fn = check_local_but_fields if fields is not None else \
            check_local_info
        if isinstance(model, dict) and (checked or check_fn(model)):
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
            model = retrieve_resource(api, self.resource_id,
                                      query_string=query_string,
                                      no_check_fields=fields is not None)

        if 'object' in model and isinstance(model['object'], dict):
            model = model['object']

        if 'model' in model and isinstance(model['model'], dict):
            status = get_status(model)
            if 'code' in status and status['code'] == FINISHED:
                model_fields = None
                if (fields is None and ('model_fields' in model['model'] or
                                        'fields' in model['model'])):
                    # models might use less fields that provided
                    model_fields = model['model'].get('model_fields')
                    fields = model['model'].get('fields', {})
                    # pagination or exclusion might cause a field not to
                    # be in available fields dict
                    if model_fields:
                        if not all(key in fields
                                   for key in list(model_fields.keys())):
                            raise Exception("Some fields are missing"
                                            " to generate a local model."
                                            " Please, provide a model with"
                                            " the complete list of fields.")
                        for field in model_fields:
                            field_info = fields[field]
                            if 'summary' in field_info:
                                model_fields[field]['summary'] = field_info[
                                    'summary']
                                model_fields[field]['name'] = field_info[
                                    'name']
                objective_field = model['objective_fields']
                missing_tokens = model['model'].get('missing_tokens')

                ModelFields.__init__(
                    self, fields, objective_id=extract_objective(
                        objective_field),
                        missing_tokens=missing_tokens,
                        operation_settings=operation_settings,
                        model_fields=model_fields)
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
