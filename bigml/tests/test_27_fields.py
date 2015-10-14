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


""" Testing Fields object properties

"""
from world import world, setup_module, teardown_module
import fields_steps
import create_source_steps as source_create

class TestFields(object):

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
            Scenario: Successfully creating a Fields object:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a Fields object from the source with objective column "<objective_column>"
                Then the object id is "<objective_id>"

                Examples:
                | data                | time_1  | objective_column | objective_id |
                | ../data/iris.csv | 10      | 0 | 000000 |
        """
        print self.test_scenario1.__doc__
        examples = [
            ['data/iris.csv', '10', '0', '000000']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            fields_steps.create_fields(self, example[2])
            fields_steps.check_objective(self, example[3])
