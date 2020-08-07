# -*- coding: utf-8 -*-
#
# Copyright 2018-2020 BigML
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


""" Creating external connectors

"""
import json

from .world import world, setup_module, teardown_module
from . import create_source_steps as source_create
from . import create_external_steps as connector_create

class TestExternalConnector(object):

    def setup(self):
        """
            Debug information
        """
        print("\n-------------------\nTests in: %s\n" % __name__)

    def teardown(self):
        """
            Debug information
        """
        print("\nEnd of tests in: %s\n-------------------\n" % __name__)

    def test_scenario1(self):
        """
            Scenario: Successfully creating an external connector:
                Given I create an external connector from environment vars
                And I wait until the external connector is ready less than <time_1> secs
                And I update the external connector with args <args>
                And the external connector has arguments <args>
                And I create a source from the external connector id
                Then the source has arguments "<source_args>"

                Examples:
                | time_1  | args |
                | 20 | {"name": "my connector name" |
        """
        print(self.test_scenario1.__doc__)
        examples = [
            ['20', '{"name": "my connector name"}', 20, 20]]
        for example in examples:
            print("\nTesting with:\n", example)
            connector_create.i_create_external_connector(self)
            connector_create.the_external_connector_is_finished(self, example[0])
            connector_create.i_update_external_connector_with(self, example[1])
            connector_create.the_external_connector_is_finished(self, example[2])
            connector_create.external_connector_has_args(example[1])
            args = {"source": "postgresql",
                 "externalconnector_id": world.external_connector["resource"][18:],
                 "query": "SELECT * FROM rnacen.auth_group"}
            source_create.i_create_using_connector(self, \
                {"source": "postgresql",
                 "externalconnector_id": world.external_connector["resource"][18:],
                 "query": "SELECT * FROM rnacen.auth_group"})
            source_create.the_source_is_finished(self, example[3])
            source_create.source_has_args(self, json.dumps({"external_data": args}))
