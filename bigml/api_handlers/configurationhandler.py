# -*- coding: utf-8 -*-
#
# Copyright 2014-2022 BigML
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

"""Base class for configurations' REST calls

   https://bigml.com/api/configurations

"""

try:
    import simplejson as json
except ImportError:
    import json


from bigml.api_handlers.resourcehandler import ResourceHandlerMixin
from bigml.api_handlers.resourcehandler import check_resource_type
from bigml.constants import CONFIGURATION_PATH


class ConfigurationHandlerMixin(ResourceHandlerMixin):
    """This class is used by the BigML class as
       a mixin that provides the REST calls. It should not
       be instantiated independently.

    """
    def __init__(self):
        """Initializes the ConfigurationHandler. This class is intended to be
           used as a mixin on ResourceHandler, that inherits its
           attributes and basic method from BigMLConnection, and must not be
           instantiated independently.

        """
        self.configuration_url = self.url + CONFIGURATION_PATH

    def create_configuration(self, configurations,
                             args=None):
        """Creates a configuration from a `configurations` dictionary.

        """
        if not isinstance(configurations, dict):
            raise AttributeError("Failed to find a configuration dictionary as"
                                 " first argument.")
        if args is None:
            args = {}
        create_args = {"configurations": configurations}
        create_args.update(args)

        body = json.dumps(create_args)
        return self._create(self.configuration_url, body)

    def get_configuration(self, configuration, query_string=''):
        """Retrieves a configuration.

           The configuration parameter should be a string containing the
           configuration id or the dict returned by create_configuration.
        """
        check_resource_type(configuration, CONFIGURATION_PATH,
                            message="A configuration id is needed.")
        return self.get_resource(configuration, query_string=query_string)

    def list_configurations(self, query_string=''):
        """Lists all your configurations.

        """
        return self._list(self.configuration_url, query_string)

    def update_configuration(self, configuration, changes):
        """Updates a configuration.

        """
        check_resource_type(configuration, CONFIGURATION_PATH,
                            message="A configuration id is needed.")
        return self.update_resource(configuration, changes)

    def delete_configuration(self, configuration):
        """Deletes a configuration.

        """
        check_resource_type(configuration, CONFIGURATION_PATH,
                            message="A configuration id is needed.")
        return self.delete_resource(configuration)
