# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,line-too-long,attribute-defined-outside-init
#pylint: disable=locally-disabled,unused-import,broad-except
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


""" Working with organizations

"""
import os
import shutil


from bigml.api import BigML

from .world import world, eq_, show_method
from .world import setup_module as general_setup_module
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create
from . import create_model_steps as model_create
from . import create_prediction_steps as prediction_create



def setup_module():
    """Operations to be performed before each module

    """
    # Project or Organization IDs

    general_setup_module()
    world.bck_api = world.api
    world.api = BigML(world.username, world.api_key, debug=world.debug,
                      project=world.project_id)
    print(world.api.connection_info())
    world.clear()

def teardown_module():
    """Operations to be performed after each module

    """

    if os.path.exists('./tmp'):
        shutil.rmtree('./tmp')

    if not world.debug:
        try:
            world.delete_resources()
        except Exception as exc:
            print(exc)
        project_stats = world.api.get_project( \
            world.project_id)['object']['stats']
        for resource_type, value in list(project_stats.items()):
            if value['count'] != 0:
                # assert False, ("Increment in %s: %s" % (resource_type, value))
                print("WARNING: Increment in %s: %s" % (resource_type, value))
        world.api.delete_project(world.project_id)
        world.project_id = None
    world.api = world.bck_api
    print(world.api.connection_info())


class TestProjPrediction:
    """Testing predictions in organization's project """

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
        Scenario: Successfully creating a prediction with a user's project connection:
            Given I create a data source uploading a "<data>" file
            And I wait until the source is ready less than <source_wait> secs
            And the source is in the project
            And I create a dataset
            And I wait until the dataset is ready less than <dataset_wait> secs
            And I create a model
            And I wait until the model is ready less than <model_wait> secs
            When I create a prediction for "<input_data>"
            Then the prediction for "<objective>" is "<prediction>"
        """
        print(self.test_scenario1.__doc__)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "input_data", "objective", "prediction"]
        examples = [
            ['data/iris.csv', '10', '10', '10', '{"petal width": 0.5}', '000004', 'Iris-setosa']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            source_create.i_upload_a_file_with_project_conn(
                self, example["data"])
            source_create.the_source_is_finished(self, example["source_wait"])
            eq_(world.source['project'], world.project_id)
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"])
            eq_(world.dataset['project'], world.project_id)
            model_create.i_create_a_model(self)
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            eq_(world.model['project'], world.project_id)
            prediction_create.i_create_a_prediction(
                self, example["input_data"])
            prediction_create.the_prediction_is(
                self, example["objective"], example["prediction"])
            eq_(world.prediction['project'], world.project_id)
