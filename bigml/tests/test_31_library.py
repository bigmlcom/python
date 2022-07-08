# -*- coding: utf-8 -*-
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
import sys

from .world import world, setup_module, teardown_module, show_doc, \
    show_method, delete_local
from . import create_library_steps as library_create

class TestLibrary(object):

    def setup(self):
        """
            Debug information
        """
        print("\n-------------------\nTests in: %s\n" % __name__)

    def teardown(self):
        """
            Debug information
        """
        delete_local()
        print("\nEnd of tests in: %s\n-------------------\n" % __name__)

    def test_scenario1(self):
        """
            Scenario: Successfully creating a whizzml library:
                Given I create a whizzml library from a excerpt of code "<source_code>"
                And I wait until the library is ready less than <time_1> secs
                And I update the library with "<param>", "<param_value>"
                And I wait until the library is ready less than <time_2> secs
                Then the library code is "<source_code>" and the value of "<param>" is "<param_value>"
        """
        show_doc(self.test_scenario1)
        headers = ["source_code", "library_wait", "param", "param_value"]
        examples = [
            ['(define (mu x) (+ x 1))', '10', 'name', 'my library']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            library_create.i_create_a_library(self, example["source_code"])
            library_create.the_library_is_finished(
                self, example["library_wait"])
            library_create.i_update_a_library(
                self, example["param"], example["param_value"])
            library_create.the_library_is_finished(
                self, example["library_wait"])
            library_create.the_library_code_and_attributes(
                self, example["source_code"], example["param"],
                example["param_value"])
