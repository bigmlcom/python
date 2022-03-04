# -*- coding: utf-8 -*-
#
# Copyright 2020-2022 BigML
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

"""Base class for external connectors' REST calls

   https://bigml.com/api/externalconnectors

"""
import os
try:
    import simplejson as json
except ImportError:
    import json


from bigml.api_handlers.resourcehandler import ResourceHandlerMixin
from bigml.api_handlers.resourcehandler import check_resource_type
from bigml.constants import EXTERNAL_CONNECTOR_PATH, \
    EXTERNAL_CONNECTION_ATTRS


def get_env_connection_info():
    """Retrieves the information to use in the external connection from
    environment variables.

    """
    # try to use environment variables values
    connection_info = {}
    for external_key in list(EXTERNAL_CONNECTION_ATTRS.keys()):
        if os.environ.get(external_key):
            connection_info.update( \
                {EXTERNAL_CONNECTION_ATTRS[external_key]:
                 os.environ.get(external_key)})
    return connection_info


class ExternalConnectorHandlerMixin(ResourceHandlerMixin):
    """This class is used by the BigML class as
       a mixin that provides the external connectors' REST calls. It should not
       be instantiated independently.

    """
    def __init__(self):
        """Initializes the ExternalConnectorHandler. This class is intended to
           be used as a mixin on ResourceHandler, that inherits its
           attributes and basic method from BigMLConnection, and must not be
           instantiated independently.

        """
        self.external_connector_url = self.url + EXTERNAL_CONNECTOR_PATH

    def create_external_connector(self, connection_info, args=None):
        """Creates an external connections from a dictionary containing the
        connection information.

        """

        create_args = {}
        if args is not None:
            create_args.update(args)

        if connection_info is None:
            connection_info = get_env_connection_info()

        if not isinstance(connection_info, dict):
            raise Exception("To create an external connector you need to"
                            " provide a dictionary with the connection"
                            " information. Please refer to the API external"
                            " connector docs for details.")

        source = connection_info.get("source", "postgresql")
        if "source" in connection_info:
            del connection_info["source"]

        create_args.update({"connection": connection_info})
        create_args.update({"source": source})
        body = json.dumps(create_args)
        return self._create(self.external_connector_url, body)

    def get_external_connector(self, external_connector, query_string=''):
        """Retrieves an external connector.

           The external connector parameter should be a string containing the
           external connector id or the dict returned by
           create_external_connector.
           As an external connector is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, the function will
           return a dict that encloses the connector contents and state info
           available at the time it is called.
        """
        check_resource_type(external_connector, EXTERNAL_CONNECTOR_PATH,
                            message="An external connector id is needed.")
        return self.get_resource(external_connector, query_string=query_string)

    def list_external_connectors(self, query_string=''):
        """Lists all your external connectors.

        """
        return self._list(self.external_connector_url, query_string)

    def update_external_connector(self, external_connector, changes):
        """Updates an external connector.

        """
        check_resource_type(external_connector, EXTERNAL_CONNECTOR_PATH,
                            message="An external connector id is needed.")
        return self.update_resource(external_connector, changes)

    def delete_external_connector(self, external_connector, query_string=''):
        """Deletes an external connector.

        """
        check_resource_type(external_connector, EXTERNAL_CONNECTOR_PATH,
                            message="An external connector id is needed.")
        return self.delete_resource(external_connector,
                                    query_string=query_string)
