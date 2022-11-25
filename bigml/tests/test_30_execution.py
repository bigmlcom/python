# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,line-too-long,attribute-defined-outside-init
#pylint: disable=locally-disabled,unused-import
#
# Copyright 2015-2022 BigML
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
from .world import world, setup_module, teardown_module, show_doc, \
    show_method
from . import create_script_steps as script_create
from . import create_execution_steps as execution_create

class TestExecution:
    """Testing local executions"""

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
        Scenario: Successfully creating a whizzml script execution:
            Given I create a whizzml script from a excerpt of code "<source_code>"
            And I wait until the script is ready less than <time_1> secs
            And I create a whizzml script execution from an existing script
            And I wait until the execution is ready less than <time_2> secs
            And I update the execution with "<param>", "<param_value>"
            And I wait until the execution is ready less than <time_3> secs
            And I create a local execution
            Then the script id is correct, the value of "<param>" is "<param_value>" and the result is "<result>"
            And the local execution result is "<result>"
        """
        show_doc(self.test_scenario1)
        headers = ["source_code", "script_wait", "execution_wait", "param",
                   "param_value", "result"]
        examples = [
            ['(+ 1 1)', '30', '30', 'name', 'my execution', 2]]

        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            script_create.i_create_a_script(self, example["source_code"])
            script_create.the_script_is_finished(self, example["script_wait"])
            execution_create.i_create_an_execution(self)
            execution_create.the_execution_is_finished(
                self, example["execution_wait"])
            execution_create.i_update_an_execution(
                self, example["param"], example["param_value"])
            execution_create.the_execution_is_finished(
                self, example["execution_wait"])
            execution_create.create_local_execution(self)
            execution_create.the_execution_and_attributes(
                self, example["param"], example["param_value"],
                example["result"])
            execution_create.the_local_execution_result_is(
                self, example["result"])

    def test_scenario2(self):
        """
        Scenario: Successfully creating a whizzml script execution from a list of scripts:
            Given I create a whizzml script from a excerpt of code "<source_code>"
            And I wait until the script is ready less than <script_wait> secs
            And I create a whizzml script from a excerpt of code "<source_code>"
            And I wait until the script is ready less than <script_wait> secs
            And I create a whizzml script execution from the last two scripts
            And I wait until the execution is ready less than <execution_wait> secs
            And I update the execution with "<param>", "<param_value>"
            And I wait until the execution is ready less than <execution_wait> secs
            Then the script ids are correct, the value of "<param>" is "<param_value>" and the result is "<result>"
        """
        show_doc(self.test_scenario2)
        headers = ["source_code", "script_wait", "execution_wait", "param",
                   "param_value", "result"]
        examples = [
            ['(+ 1 1)', '100', '100', 'name', 'my execution', [2, 2]]]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            script_create.i_create_a_script(self, example["source_code"])
            script_create.the_script_is_finished(self, example["script_wait"])
            script_create.i_create_a_script(self, example["source_code"])
            script_create.the_script_is_finished(self, example["script_wait"])
            execution_create.i_create_an_execution_from_list(
                self, number_of_scripts=2)
            execution_create.the_execution_is_finished(
                self, example["execution_wait"])
            execution_create.i_update_an_execution(
                self, example["param"], example["param_value"])
            execution_create.the_execution_is_finished(
                self, example["execution_wait"])
            execution_create.the_execution_ids_and_attributes(
                self, 2, example["param"], example["param_value"],
                example["result"])

    def test_scenario3(self):
        """
        Scenario: Successfully creating a whizzml script execution from a local or remote file:
            Given I create a whizzml script from a excerpt of code "<source_code>"
            And I wait until the script is ready less than <script_wait> secs
            And I create a whizzml script from a excerpt of code "<source_code>"
            And I wait until the script is ready less than <script_wait> secs
            And I create a whizzml script execution from the last two scripts
            And I wait until the execution is ready less than <execution_wait> secs
            And I update the execution with "<param>", "<param_value>"
            And I wait until the execution is ready less than <execution_wait> secs
            Then the script ids are correct, the value of "<param>" is "<param_value>" and the result is "<result>"
        """
        show_doc(self.test_scenario2)
        headers = ["source_code", "script_wait", "execution_wait", "param",
                   "param_value", "result"]
        examples = [
            ['data/one_plus_one.whizzml', '50', '50', 'name',
             'my execution', 2],
            ['https://gist.github.com/mmerce/49e0a69cab117b6a11fb490140326020',
             '30', '30', 'name', 'my execution', 2]]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            script_create.i_create_a_script_from_file_or_url(
                self, example["source_code"])
            script_create.the_script_is_finished(
                self, example["script_wait"])
            execution_create.i_create_an_execution(self)
            execution_create.the_execution_is_finished(
                self, example["execution_wait"])
            execution_create.i_update_an_execution(
                self, example["param"], example["param_value"])
            execution_create.the_execution_is_finished(
                self, example["execution_wait"])
            execution_create.the_execution_and_attributes(
                self, example["param"], example["param_value"],
                example["result"])
