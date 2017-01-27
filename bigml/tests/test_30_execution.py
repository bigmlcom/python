# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015-2017 BigML
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


""" Creating and updating scripts

"""
from world import world, setup_module, teardown_module
import create_script_steps as script_create
import create_execution_steps as execution_create

class TestExecution(object):

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
            Scenario: Successfully creating a whizzml script execution:
                Given I create a whizzml script from a excerpt of code "<source_code>"
                And I wait until the script is ready less than <time_1> secs
                And I create a whizzml script execution from an existing script
                And I wait until the execution is ready less than <time_2> secs
                And I update the execution with "<param>", "<param_value>"
                And I wait until the execution is ready less than <time_3> secs
                Then the script id is correct, the value of "<param>" is "<param_value>" and the result is "<result>"

                Examples:

                | source_code      | time_1  | time_2  | time_3  | param | param_value | result
                | (+ 1 1)          | 10      | 10      | 10      | name  | my execution | 2
        """
        print self.test_scenario1.__doc__
        examples = [
            ['(+ 1 1)', '10', '10', '10', 'name', 'my execution', 2]]

        for example in examples:
            print "\nTesting with:\n", example
            script_create.i_create_a_script(self, example[0])
            script_create.the_script_is_finished(self, example[1])
            execution_create.i_create_an_execution(self)
            execution_create.the_execution_is_finished(self, example[2])
            execution_create.i_update_an_execution(self, example[4], example[5])
            execution_create.the_execution_is_finished(self, example[3])
            execution_create.the_execution_and_attributes(self, example[4], example[5], example[6])

    def test_scenario2(self):
        """
            Scenario: Successfully creating a whizzml script execution from a list of scripts:
                Given I create a whizzml script from a excerpt of code "<source_code>"
                And I wait until the script is ready less than <time_1> secs
                And I create a whizzml script from a excerpt of code "<source_code>"
                And I wait until the script is ready less than <time_1> secs
                And I create a whizzml script execution from the last two scripts
                And I wait until the execution is ready less than <time_2> secs
                And I update the execution with "<param>", "<param_value>"
                And I wait until the execution is ready less than <time_3> secs
                Then the script ids are correct, the value of "<param>" is "<param_value>" and the result is "<result>"

                Examples:

                | source_code      | time_1  | time_2  | time_3  | param | param_value | result
                | (+ 1 1)          | 10      | 10      | 10      | name  | my execution | [2, 2]
        """
        print self.test_scenario2.__doc__
        examples = [
            ['(+ 1 1)', '10', '10', '10', 'name', 'my execution', [2, 2]]]
        for example in examples:
            print "\nTesting with:\n", example
            script_create.i_create_a_script(self, example[0])
            script_create.the_script_is_finished(self, example[1])
            script_create.i_create_a_script(self, example[0])
            script_create.the_script_is_finished(self, example[1])
            execution_create.i_create_an_execution_from_list(self, 2)
            execution_create.the_execution_is_finished(self, example[2])
            execution_create.i_update_an_execution(self, example[4], example[5])
            execution_create.the_execution_is_finished(self, example[3])
            execution_create.the_execution_ids_and_attributes(self, 2, example[4], example[5], example[6])
