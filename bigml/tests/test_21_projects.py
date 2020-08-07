# -*- coding: utf-8 -*-
#
# Copyright 2015-2020 BigML
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


""" Testing projects REST api calls

"""
from .world import world, setup_module, teardown_module
from . import create_project_steps as create
from . import delete_project_steps as delete


class Test_projects(object):

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
        name = "my project"
        new_name = "my new project"
        create.i_create_project(self, name)
        create.the_project_is_finished(self, 10)
        create.i_check_project_name(self, name=name)
        create.i_update_project_name_with(self, name=new_name)
        create.i_check_project_name(self, name=new_name)
        delete.i_delete_the_project(self)
        delete.wait_until_project_deleted(self, 50)
