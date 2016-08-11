# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2016 BigML
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

"""Base class for LDAs' REST calls

   https://bigml.com/developers/ldas

"""

try:
    import simplejson as json
except ImportError:
    import json


from bigml.resourcehandler import ResourceHandler
from bigml.resourcehandler import (check_resource_type, resource_is_ready,
                                   get_lda_id)
from bigml.constants import LDA_PATH


class LDAHandler(ResourceHandler):
    """This class is used by the BigML class as
       a mixin that provides the REST calls models. It should not
       be instantiated independently.

    """
    def __init__(self):
        """Initializes the LDAHandler. This class is intended to be
           used as a mixin on ResourceHandler, that inherits its
           attributes and basic method from BigMLConnection, and must not be
           instantiated independently.

        """
        self.lda_url = self.url + LDA_PATH

    def create_lda(self, datasets, args=None, wait_time=3, retries=10):
        """Creates an LDA from a `dataset` or a list o `datasets`.

        """
        create_args = self._set_create_from_datasets_args(
            datasets, args=args, wait_time=wait_time, retries=retries)

        body = json.dumps(create_args)
        return self._create(self.lda_url, body)

    def get_lda(self, lda, query_string='',
                shared_username=None, shared_api_key=None):
        """Retrieves an LDA.

           The lda parameter should be a string containing the
           LDA id or the dict returned by create_lda.
           As LDA is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, the function will
           return a dict that encloses the LDA values and state info
           available at the time it is called.

           If this is a shared LDA, the username and sharing api key must
           also be provided.
        """
        check_resource_type(lda, LDA_PATH,
                            message="An LDA id is needed.")
        lda_id = get_lda_id(lda)
        if lda_id:
            return self._get("%s%s" % (self.url, lda_id),
                             query_string=query_string,
                             shared_username=shared_username,
                             shared_api_key=shared_api_key)

    def lda_is_ready(self, lda, **kwargs):
        """Checks whether an LDA's status is FINISHED.

        """
        check_resource_type(lda, LDA_PATH,
                            message="An LDA id is needed.")
        resource = self.get_lda(lda, **kwargs)
        return resource_is_ready(resource)

    def list_ldas(self, query_string=''):
        """Lists all your ldas.

        """
        return self._list(self.lda_url, query_string)

    def update_lda(self, lda, changes):
        """Updates an LDA.

        """
        check_resource_type(lda, LDA_PATH,
                            message="An LDA id is needed.")
        lda_id = get_lda_id(lda)
        if lda_id:
            body = json.dumps(changes)
            return self._update("%s%s" % (self.url, lda_id), body)

    def delete_lda(self, lda):
        """Deletes an LDA.

        """
        check_resource_type(lda, LDA_PATH,
                            message="An LDA id is needed.")
        lda_id = get_lda_id(lda)
        if lda_id:
            return self._delete("%s%s" % (self.url, lda_id))
