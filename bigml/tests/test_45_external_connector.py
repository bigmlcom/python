# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,line-too-long,attribute-defined-outside-init
#pylint: disable=locally-disabled,unused-import
#
# Copyright 2018-2022 BigML
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

from .world import world, setup_module, teardown_module, show_doc, \
    show_method
from . import create_source_steps as source_create
from . import create_external_steps as connector_create

class TestExternalConnector:
    """Testing external connector creation"""

    def setup_method(self, method):
        """
            Debug information
        """
        self.bigml = {}
        self.bigml["method"] = method.__name__
        print("\n-------------------\nTests in: %s\n" % __name__)

    def teardown_method(self):
        """
            Debug information
        """
        print("\nEnd of tests in: %s\n-------------------\n" % __name__)
        self.bigml = {}

    def test_scenario1(self):
        """
        Scenario: Successfully creating an external connector:
            Given I create an external connector from environment vars
            And I wait until the external connector is ready less than <conn_wait> secs
            And I update the external connector with args <args>
            And the external connector has arguments <args>
        """
        show_doc(self.test_scenario1)
        headers = ["conn_wait", "args"]
        examples = [
            ['20', '{"name": "my connector name"}']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            connector_create.i_create_external_connector(self)
            connector_create.the_external_connector_is_finished(
                self, example["conn_wait"])
            connector_create.i_update_external_connector_with(
                self, example["args"])
            connector_create.the_external_connector_is_finished(
                self, example["conn_wait"])
            connector_create.external_connector_has_args(
                example["args"])
