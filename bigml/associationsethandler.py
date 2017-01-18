# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015-2017 BigML
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

   https://bigml.com/developers/associationset

"""

try:
    import simplejson as json
except ImportError:
    import json


from bigml.resourcehandler import ResourceHandler
from bigml.resourcehandler import (check_resource_type, get_resource_type,
                                   check_resource,
                                   get_association_set_id, get_association_id)
from bigml.constants import (ASSOCIATION_SET_PATH, ASSOCIATION_PATH,
                             TINY_RESOURCE)


class AssociationSetHandler(ResourceHandler):
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
        if resource_type == ASSOCIATION_PATH:
            association_id = get_association_id(association)
            check_resource(association_id,
                           query_string=TINY_RESOURCE,
                           wait_time=wait_time, retries=retries,
                           raise_on_error=True, api=self)
        else:
            raise Exception("A association id is needed to create an"
                            " association set. %s found." % resource_type)

        if input_data is None:
            input_data = {}
        create_args = {}
        if args is not None:
            create_args.update(args)
        create_args.update({
            "input_data": input_data})
        create_args.update({
            "association": association_id})

        body = json.dumps(create_args)
        return self._create(self.association_set_url, body,
                            verify=self.verify)

    def get_association_set(self, association_set, query_string=''):
        """Retrieves an association set.

        """
        check_resource_type(association_set, ASSOCIATION_SET_PATH,
                            message="An association set id is needed.")
        association_set_id = get_association_set_id(association_set)
        if association_set_id:
            return self._get("%s%s" % (self.url, association_set_id),
                             query_string)

    def list_association_sets(self, query_string=''):
        """Lists all your association sets.

        """
        return self._list(self.association_set_url, query_string)

    def update_association_set(self, association_set, changes):
        """Updates a association set.

        """
        check_resource_type(association_set, ASSOCIATION_SET_PATH,
                            message="An association set id is needed.")
        association_set_id = get_association_set_id(association_set)
        if association_set_id:
            body = json.dumps(changes)
            return self._update("%s%s" % (self.url, association_set_id), body)

    def delete_association_set(self, association_set):
        """Deletes an association set.

        """
        check_resource_type(association_set, ASSOCIATION_SET_PATH,
                            message="An association set id is needed.")
        association_set_id = get_association_set_id(association_set)
        if association_set_id:
            return self._delete("%s%s" % (self.url, association_set_id))
