# -*- coding: utf-8 -*-
#
# Copyright 2015-2022 BigML
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

"""Base class for associationset' REST calls

   https://bigml.com/api/associationset

"""

try:
    import simplejson as json
except ImportError:
    import json


from bigml.api_handlers.resourcehandler import ResourceHandlerMixin
from bigml.api_handlers.resourcehandler import check_resource_type, \
    get_resource_type, check_resource, get_association_id
from bigml.constants import ASSOCIATION_SET_PATH, ASSOCIATION_PATH, \
    IMAGE_FIELDS_FILTER, SPECIFIC_EXCLUDES


class AssociationSetHandlerMixin(ResourceHandlerMixin):
    """This class is used by the BigML class as
       a mixin that provides the REST calls models. It should not
       be instantiated independently.

    """
    def __init__(self):
        """Initializes the AssociationSetHandler. This class is intended to be
           used as a mixin on ResourceHandler, that inherits its
           attributes and basic method from BigMLConnection, and must not be
           instantiated independently.

        """
        self.association_set_url = self.url + ASSOCIATION_SET_PATH

    def create_association_set(self, association, input_data=None,
                               args=None, wait_time=3, retries=10):
        """Creates a new association set.

        """
        association_id = None
        resource_type = get_resource_type(association)
        if resource_type != ASSOCIATION_PATH:
            raise Exception("An association id is needed to create an"
                            " association set. %s found." % resource_type)

        association_id = get_association_id(association)
        if association_id is None:
            raise Exception("Failed to detect a correct association "
                "structure in %s." % association)

        if isinstance(association, dict) and \
                association.get("resource") is not None:
            # retrieving fields info from model structure
            model_info = association
        else:
            image_fields_filter = IMAGE_FIELDS_FILTER + "," + \
                ",".join(SPECIFIC_EXCLUDES[resource_type])
            model_info = check_resource(association_id,
                                        query_string=IMAGE_FIELDS_FILTER,
                                        wait_time=wait_time,
                                        retries=retries,
                                        raise_on_error=True,
                                        api=self)

        if input_data is None:
            input_data = {}
        create_args = {}
        if args is not None:
            create_args.update(args)
        create_args.update({
            "input_data": self.prepare_image_fields(model_info, input_data)})
        create_args.update({
            "association": association_id})

        body = json.dumps(create_args)
        return self._create(self.association_set_url, body,
            verify=self.domain.verify_prediction)

    def get_association_set(self, association_set, query_string=''):
        """Retrieves an association set.

        """
        check_resource_type(association_set, ASSOCIATION_SET_PATH,
                            message="An association set id is needed.")
        return self.get_resource(association_set, query_string=query_string)

    def list_association_sets(self, query_string=''):
        """Lists all your association sets.

        """
        return self._list(self.association_set_url, query_string)

    def update_association_set(self, association_set, changes):
        """Updates a association set.

        """
        check_resource_type(association_set, ASSOCIATION_SET_PATH,
                            message="An association set id is needed.")
        return self.update_resource(association_set, changes)

    def delete_association_set(self, association_set):
        """Deletes an association set.

        """
        check_resource_type(association_set, ASSOCIATION_SET_PATH,
                            message="An association set id is needed.")
        return self.delete_resource(association_set)
