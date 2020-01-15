# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2017-2020 BigML
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

"""Base class for forecasts' REST calls

   https://bigml.com/api/forecasts

"""

try:
    import simplejson as json
except ImportError:
    import json


from bigml.resourcehandler import ResourceHandler
from bigml.resourcehandler import (check_resource_type, get_forecast_id,
                                   check_resource, get_time_series_id,
                                   get_resource_type)
from bigml.constants import (FORECAST_PATH, TIME_SERIES_PATH, TINY_RESOURCE)

class ForecastHandler(ResourceHandler):
    """This class is used by the BigML class as
       a mixin that provides the REST calls models. It should not
       be instantiated independently.

    """
    def __init__(self):
        """Initializes the ForecastHandler. This class is intended to be
           used as a mixin on ResourceHandler, that inherits its
           attributes and basic method from BigMLConnection, and must not be
           instantiated independently.

        """
        self.forecast_url = self.prediction_base_url + FORECAST_PATH

    def create_forecast(self, time_series, input_data=None,
                        args=None, wait_time=3, retries=10):
        """Creates a new forecast.

        """
        time_series_id = get_time_series_id(time_series)
        resource_type = get_resource_type(time_series_id)
        if resource_type == TIME_SERIES_PATH and time_series_id is not None:
            check_resource(time_series_id,
                           query_string=TINY_RESOURCE,
                           wait_time=wait_time, retries=retries,
                           raise_on_error=True, api=self)
        else:
            raise Exception("A time series model id is needed to create a"
                            " forecast. %s found." % resource_type)

        if input_data is None:
            input_data = {}
        create_args = {}
        if args is not None:
            create_args.update(args)
        create_args.update({
            "input_data": input_data})
        if time_series_id is not None:
            create_args.update({
                "timeseries": time_series_id})

        body = json.dumps(create_args)
        return self._create(self.forecast_url, body,
                            verify=self.verify_prediction)

    def get_forecast(self, forecast, query_string=''):
        """Retrieves a forecast.

        """
        check_resource_type(forecast, FORECAST_PATH,
                            message="A forecast id is needed.")
        forecast_id = get_forecast_id(forecast)
        if forecast_id:
            return self._get("%s%s" % (self.url, forecast_id),
                             query_string=query_string)

    def list_forecasts(self, query_string=''):
        """Lists all your forecasts.

        """
        return self._list(self.forecast_url, query_string)

    def update_forecast(self, forecast, changes):
        """Updates a forecast.

        """
        check_resource_type(forecast, FORECAST_PATH,
                            message="A forecast id is needed.")
        forecast_id = get_forecast_id(forecast)
        if forecast_id:
            body = json.dumps(changes)
            return self._update("%s%s" % (self.url, forecast_id), body)

    def delete_forecast(self, forecast):
        """Deletes a forecast.

        """
        check_resource_type(forecast, FORECAST_PATH,
                            message="A forecast id is needed.")
        forecast_id = get_forecast_id(forecast)
        if forecast_id:
            return self._delete("%s%s" % (self.url, forecast_id))
