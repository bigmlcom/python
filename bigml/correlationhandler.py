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

"""Base class for correlations' REST calls

   https://bigml.com/developers/correlations

"""

try:
    import simplejson as json
except ImportError:
    import json


from bigml.resourcehandler import ResourceHandler
from bigml.resourcehandler import (check_resource_type,
                                   get_correlation_id, get_resource_type,
                                   get_dataset_id, check_resource)
from bigml.constants import (CORRELATION_PATH, DATASET_PATH,
                             TINY_RESOURCE)


class CorrelationHandler(ResourceHandler):
    """This class is used by the BigML class as
       a mixin that provides the correlations' REST calls. It should not
       be instantiated independently.

    """
    def __init__(self):
        """Initializes the CorrelationHandler. This class is intended to be
           used as a mixin on ResourceHandler, that inherits its
           attributes and basic method from BigMLConnection, and must not be
           instantiated independently.

        """
        self.correlation_url = self.url + CORRELATION_PATH

    def create_correlation(self, dataset, args=None, wait_time=3, retries=10):
        """Creates a correlation from a `dataset`.

        """
        dataset_id = None
        resource_type = get_resource_type(dataset)
        if resource_type == DATASET_PATH:
            dataset_id = get_dataset_id(dataset)
            check_resource(dataset_id,
                           query_string=TINY_RESOURCE,
                           wait_time=wait_time, retries=retries,
                           raise_on_error=True, api=self)
        else:
            raise Exception("A dataset id is needed to create a"
                            " correlation. %s found." % resource_type)

        create_args = {}
        if args is not None:
            create_args.update(args)
        create_args.update({
            "dataset": dataset_id})

        body = json.dumps(create_args)
        return self._create(self.correlation_url, body)

    def get_correlation(self, correlation, query_string=''):
        """Retrieves a correlation.

           The correlation parameter should be a string containing the
           correlation id or the dict returned by create_correlation.
           As correlation is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, the function will
           return a dict that encloses the correlation values and state info
           available at the time it is called.
        """
        check_resource_type(correlation, CORRELATION_PATH,
                            message="A correlation id is needed.")
        correlation_id = get_correlation_id(correlation)
        if correlation_id:
            return self._get("%s%s" % (self.url, correlation_id),
                             query_string=query_string)

    def list_correlations(self, query_string=''):
        """Lists all your correlations.

        """
        return self._list(self.correlation_url, query_string)

    def update_correlation(self, correlation, changes):
        """Updates a correlation.

        """
        check_resource_type(correlation, CORRELATION_PATH,
                            message="A correlation id is needed.")
        correlation_id = get_correlation_id(correlation)
        if correlation_id:
            body = json.dumps(changes)
            return self._update("%s%s" % (self.url, correlation_id), body)

    def delete_correlation(self, correlation):
        """Deletes a correlation.

        """
        check_resource_type(correlation, CORRELATION_PATH,
                            message="A correlation id is needed.")
        correlation_id = get_correlation_id(correlation)
        if correlation_id:
            return self._delete("%s%s" % (self.url, correlation_id))
