# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015-2019 BigML
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
from world import world, setup_module, teardown_module
import create_configuration_steps as config_create

class TestConfiguration(object):

    def setup(self):
        """
            Debug information
        """
        print "\n-------------------\nTests in: %s\n" % __name__

    def teardown(self):
        """
            Debug information
        """
        print "\nEnd of tests in: %s\n-------------------\n" % __name__

    def test_scenario1(self):
        """
            Scenario: Successfully creating configuration:
                Given I create a configuration from "<configurations>" info
                And I update the configuration name to "<configuration_name>"
                When I wait until the configuration is ready less than <time_1> secs
                Then the configuration name is "<configuration_name>"
                And the configuration contents are "<configurations>"
        """
        print self.test_scenario1.__doc__
        examples = [
            [{
                "dataset": {
                    "name": "Customer FAQ dataset"
                }
            }, '10', {"name": 'my new configuration name'}]]
        for example in examples:
            print "\nTesting with:\n", example
            config_create.i_create_configuration(self, example[0])
            config_create.i_update_configuration(self, example[2])
            config_create.the_configuration_is_finished_in_less_than(self, example[1])
            config_create.i_check_configuration_name(self, example[2])
            config_create.i_check_configuration_conf(self, example[0])
