# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2018-2019 BigML
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


from bigml.api import BigML

from world import world
from world import setup_module as general_setup_module
import create_source_steps as source_create
import create_dataset_steps as dataset_create
import create_model_steps as model_create
import create_prediction_steps as prediction_create



def setup_module():
    """Operations to be performed before each module

    """
    # Project or Organization IDs

    general_setup_module()
    world.bck_api = world.api
    world.api = BigML(world.USERNAME, world.API_KEY, debug=world.debug,
                      project=world.project_id)
    print world.api.connection_info()
    world.clear()


def teardown_module():
    """Operations to be performed after each module

    """

    if os.path.exists('./tmp'):
        shutil.rmtree('./tmp')

    if not world.debug:
        try:
            world.delete_resources()
        except Exception, exc:
            print exc
        project_stats = world.api.get_project( \
            world.project_id)['object']['stats']
        for resource_type, value in project_stats.items():
            if value['count'] != 0:
                # assert False, ("Increment in %s: %s" % (resource_type, value))
                print "WARNING: Increment in %s: %s" % (resource_type, value)
        world.api.delete_project(world.project_id)
        world.project_id = None
    world.api = world.bck_api
    print world.api.connection_info()


class TestProjPrediction(object):

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
            Scenario: Successfully creating a prediction with a user's project connection:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And the source is in the project
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a model
                And I wait until the model is ready less than <time_3> secs
                When I create a prediction for "<data_input>"
                Then the prediction for "<objective>" is "<prediction>"

                Examples:
                | data                | time_1  | time_2 | time_3 | data_input    | objective | prediction  |
                | ../data/iris.csv | 10      | 10     | 10     | {"petal width": 0.5} | 000004    | Iris-setosa |

        """
        print self.test_scenario1.__doc__
        examples = [
            ['data/iris.csv', '10', '10', '10', '{"petal width": 0.5}', '000004', 'Iris-setosa']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file_with_project_conn(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            assert world.source['project'] == world.project_id
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            assert world.dataset['project'] == world.project_id
            model_create.i_create_a_model(self)
            model_create.the_model_is_finished_in_less_than(self, example[3])
            assert world.model['project'] == world.project_id
            prediction_create.i_create_a_prediction(self, example[4])
            prediction_create.the_prediction_is(self, example[5], example[6])
            assert world.prediction['project'] == world.project_id
