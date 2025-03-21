# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,line-too-long,attribute-defined-outside-init
#pylint: disable=locally-disabled,unused-import,no-member
#
# Copyright 2015-2025 BigML
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
from bigml.api_handlers.resourcehandler import get_id

from .world import world, setup_module, teardown_module, show_doc, \
    show_method
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create


class TestUploadSource:
    """Testing source uploads"""

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
        Scenario: Successfully uploading source:
            Given I create a data source uploading a "<data>" file with args "<source_conf>"
            And I wait until the source is ready less than <source_wait> secs
            Then the source exists and has args "<source_conf>"
        """
        show_doc(self.test_scenario1)
        headers = ["data", "source_wait", "source_conf"]
        examples = [
            ['data/iris.csv', '30', '{"tags": ["my tag", "my second tag"]}'],
            ['data/iris.csv', '30', '{"name": "Testing unicode names: áé"}']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            source_create.i_upload_a_file_with_args(
                self, example["data"], example["source_conf"])
            source_create.the_source_is_finished(self, example["source_wait"])
            source_create.source_has_args(self, example["source_conf"])

    def test_scenario2(self):
        """
        Scenario: Successfully creating composite source:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            Then I create a composite from the last two sources
            And I wait until the source is ready less than <source_wait> secs
            Then the composite exists and has the previous two sources
        """
        show_doc(self.test_scenario2)
        headers = ["data", "source_wait"]
        examples = [
            ['data/iris.csv', '30']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            sources = []
            source_create.i_upload_a_file(
                self, example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"])
            sources.append(get_id(world.source["resource"]))
            source_create.i_upload_a_file(
                self, example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"])
            sources.append(get_id(world.source["resource"]))
            source_create.i_create_composite(self, sources)
            source_create.the_source_is_finished(self, example["source_wait"])
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
        """
        show_doc(self.test_scenario3)
        headers = ["data", "source_wait"]
        examples = [
            ['data/iris.csv', '30']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            source = world.source["resource"]
            source_create.clone_source(self, source)
            source_create.the_source_is_finished(
                self, example["source_wait"])
            source_create.the_cloned_source_origin_is(self, source)
            
    def test_scenario4(self):
        """
        Scenario: Successfully adding annotatations to composite source:
            Given I create an annotated images data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            Then the new dataset has <annotations_num> annotations in the <annotations_field> field
        """
        headers = ["data", "source_wait", "dataset_wait", "annotations_num",
                   "annotations_field"]
        examples = [
            ['data/images/metadata.json', '500', '500', '12',
             '100002'],
            ['data/images/metadata_compact.json', '500', '500', '3',
             '100003']]
        show_doc(self.test_scenario4)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            source_create.i_create_annotated_source(
                self,
                example["data"],
                args={"image_analysis": {"enabled": False,
                                         "extracted_features": []}})
            source_create.the_source_is_finished(
                self, example["source_wait"])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"])
            dataset_create.check_annotations(self, 
                                             example["annotations_field"],
                                             example["annotations_num"])

