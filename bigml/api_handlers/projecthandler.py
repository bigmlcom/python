# -*- coding: utf-8 -*-
#pylint: disable=abstract-method
#
# Copyright 2014-2022 BigML
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

"""Base class for projects' REST calls

   https://bigml.com/api/projects

"""

try:
    import simplejson as json
except ImportError:
    import json


from bigml.api_handlers.resourcehandler import ResourceHandlerMixin
from bigml.api_handlers.resourcehandler import check_resource_type
from bigml.constants import PROJECT_PATH


class ProjectHandlerMixin(ResourceHandlerMixin):
    """This class is used by the BigML class as
       a mixin that provides the REST calls models. It should not
       be instantiated independently.

    """
    def __init__(self):
        """Initializes the ProjectHandler. This class is intended to be
           used as a mixin on ResourceHandler, that inherits its
           attributes and basic method from BigMLConnection, and must not be
           instantiated independently.

        """
        self.project_url = self.url + PROJECT_PATH

    def create_project(self, args=None):
        """Creates a project.

        """
        if args is None:
            args = {}
        body = json.dumps(args)
        return self._create(self.project_url, body, organization=True)

    def get_project(self, project, query_string=''):
        """Retrieves a project.

           The project parameter should be a string containing the
           project id or the dict returned by create_project.
           As every resource, is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state. The function will
           return a dict that encloses the project values and state info
           available at the time it is called.
        """
        check_resource_type(project, PROJECT_PATH,
                            message="A project id is needed.")
        return self.get_resource(project, query_string=query_string,
                                 organization=True)

    def list_projects(self, query_string=''):
        """Lists all your projects.

        """
        return self._list(self.project_url, query_string, organization=True)

    def update_project(self, project, changes):
        """Updates a project.

        """
        check_resource_type(project, PROJECT_PATH,
                            message="A project id is needed.")
        return self.update_resource(project, changes, organization=True)

    def delete_project(self, project):
        """Deletes a project.

        """
        check_resource_type(project, PROJECT_PATH,
                            message="A project id is needed.")
        return self.delete_resource(project, organization=True)
