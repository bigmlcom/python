# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,line-too-long,attribute-defined-outside-init
#pylint: disable=locally-disabled,unused-import,no-self-use
#
# Copyright 2018-2023 BigML
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

from .world import world, teardown_fn, setup_module, ok_


class TestCleaningProject:
    """Artifact to clean all the created resources after each test execution"""

    def setup_method(self):
        """
            Debug information
        """
        print("\nFinal cleaning\n")

    def test_final(self):
        """Final empty test """
        ok_(True)

    def teardown_method(self):
        """
            Debug information
        """
        teardown_fn(force=True)
        print("\nEnd of tests.")
