# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2014-2020 BigML
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


from bigml.resourcehandler import ResourceHandler
from bigml.resourcehandler import (check_resource_type,
                                   get_configuration_id)
from bigml.constants import CONFIGURATION_PATH


class ConfigurationHandler(ResourceHandler):
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
        configuration_id = get_configuration_id(configuration)
        if configuration_id:
            return self._get("%s%s" % (self.url, configuration_id),
                             query_string=query_string)

    def list_configurations(self, query_string=''):
        """Lists all your configurations.

        """
        return self._list(self.configuration_url, query_string)

    def update_configuration(self, configuration, changes):
        """Updates a configuration.

        """
        check_resource_type(configuration, CONFIGURATION_PATH,
                            message="A configuration id is needed.")
        configuration_id = get_configuration_id(configuration)
        if configuration_id:
            body = json.dumps(changes)
            return self._update("%s%s" % (self.url, configuration_id), body)

    def delete_configuration(self, configuration):
        """Deletes a configuration.

        """
        check_resource_type(configuration, CONFIGURATION_PATH,
                            message="A configuration id is needed.")
        configuration_id = get_configuration_id(configuration)
        if configuration_id:
            return self._delete("%s%s" % (self.url, configuration_id))
