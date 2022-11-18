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


""" Renaming duplicated names in fields

"""
import sys

from .world import world, setup_module, teardown_module, show_doc, \
    show_method, delete_local
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create
from . import create_model_steps as model_create
from . import compare_predictions_steps as compare_preds

class TestDuplicatedFields(object):

    def setup_method(self):
        """
            Debug information
        """
        print("\n-------------------\nTests in: %s\n" % __name__)

    def teardown_method(self):
        """
            Debug information
        """
        delete_local()
        print("\nEnd of tests in: %s\n-------------------\n" % __name__)

    def test_scenario1(self):
        """
            Scenario: Successfully changing duplicated field names:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset with "<dataset_conf>"
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a model
                And I wait until the model is ready less than <model_wait> secs
                And I create a local model
                Then "<field_id>" field's name is changed to "<new_name>"
        """
        show_doc(self.test_scenario1)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "dataset_conf", "field_id", "new_name"]
        examples = [
            ['data/iris.csv', '20', '20', '30',
             '{"fields": {"000001": {"name": "species"}}}',
             '000001', 'species1'],
            ['data/iris.csv', '20', '20', '30',
             '{"fields": {"000001": {"name": "petal width"}}}',
             '000003', 'petal width3']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            dataset_create.i_create_a_dataset_with(
                self, example["dataset_conf"])
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"])
            model_create.i_create_a_model(self)
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            compare_preds.i_create_a_local_model(self)
            model_create.field_name_to_new_name(
                self, example["field_id"],  example["new_name"])
