# -*- coding: utf-8 -*-
#
# Copyright 2015-2021 BigML
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
from .world import world, setup_module, teardown_module
from . import create_source_steps as source_create
from bigml.api_handlers.resourcehandler import get_id

class TestUploadSource(object):

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

            Scenario: Successfully uploading source:
                Given I create a data source uploading a "<data>" file with args "<args>"
                And I wait until the source is ready less than <time_1> secs
                Then the source exists and has args "<args>"

                Examples:
                | data             | time_1  | args |
                | ../data/iris.csv | 30      | {"tags": ["my tag", "my second tag"]}
                | ../data/iris.csv | 30      | {"name": "Testing unicode names: áé"}]}

        """
        print(self.test_scenario1.__doc__)
        examples = [
            ['data/iris.csv', '30', '{"tags": ["my tag", "my second tag"]}'],
            ['data/iris.csv', '30', '{"name": "Testing unicode names: áé"}']]
        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_upload_a_file_with_args(self, example[0], example[2])
            source_create.the_source_is_finished(self, example[1])
            source_create.source_has_args(self, example[2])

    def test_scenario2(self):
        """

            Scenario: Successfully creating composite source:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                Then I create a composite from the last two sources
                And I wait until the source is ready less than <time_1> secs
                Then the composite exists and has the previous two sources

                Examples:
                | data             | time_1  |
                | ../data/iris.csv | 30      |

        """
        print(self.test_scenario2.__doc__)
        examples = [
            ['data/iris.csv', '30']]
        for example in examples:
            print("\nTesting with:\n", example)
            sources = []
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            sources.append(get_id(world.source["resource"]))
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            sources.append(get_id(world.source["resource"]))
            source_create.i_create_composite(self, sources)
            source_create.the_source_is_finished(self, example[1])
            for source in sources:
                world.sources.remove("source/%s" % source)
            source_create.the_composite_contains(self, sources)

    def test_scenario3(self):
        """

            Scenario: Successfully cloning source:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I clone the last source
                And I wait until the source is ready less than <time_1> secs
                Then the new source the first one as origin

                Examples:
                | data             | time_1  |
                | ../data/iris.csv | 30      |

        """
        print(self.test_scenario3.__doc__)
        examples = [
            ['data/iris.csv', '30']]
        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            source = world.source["resource"]
            source_create.clone_source(self, source)
            source_create.the_source_is_finished(self, example[1])
            source_create.the_cloned_source_origin_is(self, source)
