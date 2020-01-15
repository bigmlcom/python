# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2019-2020 BigML
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

"""Base class for linear regressions' REST calls

   https://bigml.com/api/linearregressions

"""

try:
    import simplejson as json
except ImportError:
    import json


from bigml.resourcehandler import ResourceHandler
from bigml.resourcehandler import (check_resource_type, resource_is_ready,
                                   get_linear_regression_id)
from bigml.constants import LINEAR_REGRESSION_PATH


class LinearRegressionHandler(ResourceHandler):
    """This class is used by the BigML class as
       a mixin that provides the REST calls models. It should not
       be instantiated independently.

    """
    def __init__(self):
        """Initializes the LinearRegressionHandler. This class is intended
           to be used as a mixin on ResourceHandler, that inherits its
           attributes and basic method from BigMLConnection, and must not be
           instantiated independently.

        """
        self.linear_regression_url = self.url + LINEAR_REGRESSION_PATH

    def create_linear_regression(self, datasets,
                                 args=None, wait_time=3, retries=10):
        """Creates a linear regression from a `dataset`
           of a list o `datasets`.

        """
        create_args = self._set_create_from_datasets_args(
            datasets, args=args, wait_time=wait_time, retries=retries)

        body = json.dumps(create_args)
        return self._create(self.linear_regression_url, body)

    def get_linear_regression(self, linear_regression, query_string='',
                              shared_username=None, shared_api_key=None):
        """Retrieves a linear regression.

           The model parameter should be a string containing the
           linear regression id or the dict returned by
           create_linear_regression.
           As a linear regression is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, the function will
           return a dict that encloses the linear regression
           values and state info available at the time it is called.

           If this is a shared linear regression, the username and
           sharing api key must also be provided.
        """
        check_resource_type(linear_regression, LINEAR_REGRESSION_PATH,
                            message="A linear regression id is needed.")
        linear_regression_id = get_linear_regression_id(
            linear_regression)
        if linear_regression_id:
            return self._get("%s%s" % (self.url, linear_regression_id),
                             query_string=query_string,
                             shared_username=shared_username,
                             shared_api_key=shared_api_key)

    def linear_regression_is_ready(self, linear_regression, **kwargs):
        """Checks whether a linear regressioin's status is FINISHED.

        """
        check_resource_type(linear_regression, LINEAR_REGRESSION_PATH,
                            message="A linear regression id is needed.")
        resource = self.get_linear_regression(linear_regression, **kwargs)
        return resource_is_ready(resource)

    def list_linear_regressions(self, query_string=''):
        """Lists all your linear regressions.

        """
        return self._list(self.linear_regression_url, query_string)

    def update_linear_regression(self, linear_regression, changes):
        """Updates a linear regression.

        """
        check_resource_type(linear_regression, LINEAR_REGRESSION_PATH,
                            message="A linear regression id is needed.")
        linear_regression_id = get_linear_regression_id(
            linear_regression)
        if linear_regression_id:
            body = json.dumps(changes)
            return self._update(
                "%s%s" % (self.url, linear_regression_id), body)

    def delete_linear_regression(self, linear_regression):
        """Deletes a linear regression.

        """
        check_resource_type(linear_regression, LINEAR_REGRESSION_PATH,
                            message="A linear regression id is needed.")
        linear_regression_id = get_linear_regression_id(
            linear_regression)
        if linear_regression_id:
            return self._delete("%s%s" % (self.url, linear_regression_id))
