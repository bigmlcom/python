# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015 BigML
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


""" Uploading source with structured args

"""
from world import world, setup_module, teardown_module
import create_source_steps as source_create

class TestUploadSource(object):

    def test_scenario1(self):
        """

            Scenario: Successfully uploading source:
                Given I create a data source uploading a "<data>" file with args "<args>"
                And I wait until the source is ready less than <time_1> secs
                Then the source exists and has args "<args>"

                Examples:
                | data             | time_1  | args |
                | ../data/iris.csv | 30      | {"tags": ["my tag", "my second tag"]}
        """
        print self.test_scenario1.__doc__
        examples = [
            ['data/iris.csv', '30', '{"tags": ["my tag", "my second tag"]}']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file_with_args(self, example[0], example[2])
            source_create.the_source_is_finished(self, example[1])
            source_create.source_has_args(self, example[2])
