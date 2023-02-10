# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,line-too-long,attribute-defined-outside-init
#pylint: disable=locally-disabled,unused-import
#
# Copyright 2015-2023 BigML
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


""" Creating configuration

"""
from .world import world, setup_module, teardown_module, show_doc, \
    show_method
from . import create_configuration_steps as config_create

class TestConfiguration:
    """Test for Configuration methods"""

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
        Scenario: Successfully creating configuration:
            Given I create a configuration from "<configurations>" info
            And I update the configuration name to "<configuration_name>"
            When I wait until the configuration is ready less than <configuration_wait> secs
            Then the configuration name is "<configuration_name>"
            And the configuration contents are "<configurations>"
        """
        show_doc(self.test_scenario1)
        headers = ["configurations", "configuration_wait",
                   "configuration_name"]
        examples = [
            [{
                "dataset": {
                    "name": "Customer FAQ dataset"
                }
            }, '10', {"name": 'my new configuration name'}]]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            config_create.i_create_configuration(
                self, example["configurations"])
            config_create.i_update_configuration(
                self, example["configuration_name"])
            config_create.the_configuration_is_finished_in_less_than(
                self, example["configuration_wait"])
            config_create.i_check_configuration_name(
                self, example["configuration_name"])
            config_create.i_check_configuration_conf(
                self, example["configurations"])
