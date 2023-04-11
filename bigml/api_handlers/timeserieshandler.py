# -*- coding: utf-8 -*-
#pylint: disable=abstract-method
#
# Copyright 2017-2023 BigML
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

"""Base class for time series'' REST calls

   https://bigml.com/api/timeseries

"""

try:
    import simplejson as json
except ImportError:
    import json


from bigml.api_handlers.resourcehandler import ResourceHandlerMixin
from bigml.api_handlers.resourcehandler import check_resource_type, \
    resource_is_ready
from bigml.constants import TIME_SERIES_PATH


class TimeSeriesHandlerMixin(ResourceHandlerMixin):
    """This class is used by the BigML class as
       a mixin that provides the REST calls models. It should not
       be instantiated independently.

    """
    def __init__(self):
        """Initializes the TimeSeriesHandler. This class is intended
           to be used as a mixin on ResourceHandler, that inherits its
           attributes and basic method from BigMLConnection, and must not be
           instantiated independently.

        """
        self.time_series_url = self.url + TIME_SERIES_PATH

    def create_time_series(self, datasets,
                           args=None, wait_time=3, retries=10):
        """Creates a time series from a `dataset`
           of a list o `datasets`.

        """
        create_args = self._set_create_from_datasets_args(
            datasets, args=args, wait_time=wait_time, retries=retries)

        body = json.dumps(create_args)
        return self._create(self.time_series_url, body)

    def get_time_series(self, time_series, query_string='',
                        shared_username=None, shared_api_key=None):
        """Retrieves a time series.

           The model parameter should be a string containing the
           time series id or the dict returned by
           create_time_series.
           As a time series is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, the function will
           return a dict that encloses the time series
           values and state info available at the time it is called.

           If this is a shared time series, the username and
           sharing api key must also be provided.
        """
        check_resource_type(time_series, TIME_SERIES_PATH,
                            message="A time series id is needed.")
        return self.get_resource(time_series,
                                 query_string=query_string,
                                 shared_username=shared_username,
                                 shared_api_key=shared_api_key)

    def time_series_is_ready(self, time_series, **kwargs):
        """Checks whether a time series's status is FINISHED.

        """
        check_resource_type(time_series, TIME_SERIES_PATH,
                            message="A time series id is needed.")
        resource = self.get_time_series(time_series, **kwargs)
        return resource_is_ready(resource)

    def list_time_series(self, query_string=''):
        """Lists all your time series.

        """
        return self._list(self.time_series_url, query_string)

    def update_time_series(self, time_series, changes):
        """Updates a time series.

        """
        check_resource_type(time_series, TIME_SERIES_PATH,
                            message="A time series id is needed.")
        return self.update_resource(time_series, changes)

    def delete_time_series(self, time_series, query_string=''):
        """Deletes a time series.

        """
        check_resource_type(time_series, TIME_SERIES_PATH,
                            message="A time series id is needed.")
        return self.delete_resource(time_series, query_string=query_string)

    def clone_time_series(self, time_series,
                          args=None, wait_time=3, retries=10):
        """Creates a cloned time_series from an existing `time series`

        """
        create_args = self._set_clone_from_args(
            time_series, "timeseries", args=args, wait_time=wait_time,
            retries=retries)

        body = json.dumps(create_args)
        return self._create(self.time_series_url, body)
