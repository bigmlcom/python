# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2014-2019 BigML
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


from bigml.resourcehandler import ResourceHandler
from bigml.resourcehandler import check_resource_type, get_project_id
from bigml.constants import PROJECT_PATH


class ProjectHandler(ResourceHandler):
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
        project_id = get_project_id(project)
        if project_id:
            return self._get("%s%s" % (self.url, project_id),
                             query_string=query_string, organization=True)

    def list_projects(self, query_string=''):
        """Lists all your projects.

        """
        return self._list(self.project_url, query_string, organization=True)

    def update_project(self, project, changes):
        """Updates a project.

        """
        check_resource_type(project, PROJECT_PATH,
                            message="A project id is needed.")
        project_id = get_project_id(project)
        if project_id:
            body = json.dumps(changes)
            return self._update("%s%s" % (self.url, project_id), body,
                                organization=True)

    def delete_project(self, project):
        """Deletes a project.

        """
        check_resource_type(project, PROJECT_PATH,
                            message="A project id is needed.")
        project_id = get_project_id(project)
        if project_id:
            return self._delete("%s%s" % (self.url, project_id),
                                organization=True)
