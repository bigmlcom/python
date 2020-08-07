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


""" Mimic World lettuce object

"""
import os
import shutil
import time
import pkg_resources
import datetime
import pprint

from bigml.api import BigML
from bigml.api import HTTP_OK, HTTP_NO_CONTENT, HTTP_UNAUTHORIZED
from bigml.constants import IRREGULAR_PLURALS, RENAMED_RESOURCES
from bigml.api_handlers.externalconnectorhandler import get_env_connection_info
from bigml.util import get_exponential_wait
from nose.tools import assert_less

MAX_RETRIES = 10
RESOURCE_TYPES = [
    'cluster',
    'fusion',
    'optiml',
    'source',
    'dataset',
    'prediction',
    'evaluation',
    'ensemble',
    'batchprediction',
    'centroid',
    'batchcentroid',
    'anomaly',
    'anomalyscore',
    'batchanomalyscore',
    'project',
    'sample',
    'correlation',
    'statisticaltest',
    'logisticregression',
    'model',
    'deepnet',
    'association',
    'associationset',
    'configuration',
    'topicmodel',
    'topicdistribution',
    'timeseries',
    'forecast',
    'pca',
    'projection',
    'batchprojection',
    'linearregression',
    'script',
    'execution',
    'library',
    'externalconnector'
]

irregular_plurals = {}
irregular_plurals.update(IRREGULAR_PLURALS)
irregular_plurals.update({"timeseries": "time_series_set"})


def plural(resource_type):
    """Creates the plural form of a resource type

    """
    return irregular_plurals.get(resource_type, "%ss" % resource_type)


def show_doc(self, examples=None):
    """ Shows the name and documentation of the method passed as argument

    """
    print("%s:\n%s" % (self.__name__, self.__doc__))
    if examples:
        print("                |%s" % \
            "\n                |".join(["|".join([str(item)
                                                  for item in example]) for
                                        example in examples]))


class World(object):

    def __init__(self):
        self.USERNAME = None
        self.API_KEY = None
        self.api = None
        self.debug = False
        try:
            self.debug = bool(os.environ.get('BIGML_DEBUG', 0))
        except ValueError:
            pass
        self.short_debug = False
        try:
            self.short_debug = bool(os.environ.get('BIGML_SHORT_DEBUG', 0))
        except ValueError:
            pass
        self.clear()
        self.dataset_ids = []
        self.fields_properties_dict = {}
        self.counters = {}
        self.test_project_name = "Test: python bindings %s" % \
            datetime.datetime.now()
        self.project_id = None
        self.print_connection_info()
        self.delta = int(os.environ.get('BIGML_DELTA', '1'))


    def print_connection_info(self):
        self.USERNAME = os.environ.get('BIGML_USERNAME')
        self.API_KEY = os.environ.get('BIGML_API_KEY')
        self.EXTERNAL_CONN = get_env_connection_info()

        if self.USERNAME is None or self.API_KEY is None:
            assert False, ("Tests use the BIGML_USERNAME and BIGML_API_KEY"
                           " environment variables to authenticate the"
                           " connection, but they seem to be unset. Please,"
                           "set them before testing.")
        self.api = BigML(self.USERNAME, self.API_KEY, debug=self.debug,
                         short_debug=self.short_debug, storage=(None if
                         not (self.debug or self.short_debug) else
                         "./debug_storage"))
        print(self.api.connection_info())
        print(self.external_connection_info())

    def external_connection_info(self):
        """Printable string: The information used to connect to a external
        data source

        """
        info = "External data connection config:\n%s" % \
            pprint.pformat(self.EXTERNAL_CONN, indent=4)
        return info

    def clear(self):
        """Clears the stored resources' ids

        """
        for resource_type in RESOURCE_TYPES:
            setattr(self, plural(resource_type), [])
            setattr(self, RENAMED_RESOURCES.get(resource_type,
                                                resource_type), None)

    def delete_resources(self):
        """Deletes the created objects

        """

        for resource_type in RESOURCE_TYPES:
            object_list = set(getattr(self, plural(resource_type)))
            if object_list:
                print("Deleting %s %s" % (len(object_list),
                                          plural(resource_type)))
                delete_method = self.api.deleters[resource_type]
                for obj_id in object_list:
                    counter = 0
                    result = delete_method(obj_id)
                    while (result['code'] != HTTP_NO_CONTENT and
                           counter < MAX_RETRIES):
                        print("Delete failed for %s. Retrying" % obj_id)
                        time.sleep(3 * self.delta)
                        counter += 1
                        result = delete_method(obj_id)
                    if counter == MAX_RETRIES:
                        print ("Retries to delete the created resources are"
                               " exhausted. Failed to delete.")


    def store_resources(self):
        """Stores the created objects

        """

        for resource_type in RESOURCE_TYPES:
            object_list = set(getattr(self, plural(resource_type)))
            if object_list:
                print("Deleting %s %s" % (len(object_list),
                                          plural(resource_type)))
                store_method = self.api.getters[resource_type]
                for obj_id in object_list:
                    counter = 0
                    result = store_method(obj_id)
                    self.api.ok(result)


world = World()

def res_filename(file):
    return pkg_resources.resource_filename('bigml', "../%s" % file)

def setup_module():
    """Operations to be performed before each module

    """
    if world.project_id is None:
        world.project_id = world.api.create_project( \
            {"name": world.test_project_name})['resource']
    world.clear()

def teardown_module():
    """Operations to be performed after each module

    """

    if os.path.exists('./tmp'):
        shutil.rmtree('./tmp')

    if not world.debug and not world.short_debug:
        world.delete_resources()
        project_stats = world.api.get_project( \
            world.project_id)['object']['stats']
        for resource_type, value in list(project_stats.items()):
            if value['count'] != 0:
                # assert False, ("Increment in %s: %s" % (resource_type, value))
                print("WARNING: Increment in %s: %s" % (resource_type, value))
        world.api.delete_project(world.project_id)
        world.project_id = None
    else:
        world.store_resources()


def teardown_class():
    """Operations to be performed after each class

    """
    world.dataset_ids = []
    world.local_ensemble = None
    world.local_model = None
    world.local_deepnet = None

def logged_wait(start, delta, count, res_description):
    """Comparing the elapsed time to the expected delta and waiting for
       the next sleep period.

    """
    wait_time = min(get_exponential_wait(delta / 100.0, count), delta)
    print("Sleeping %s" % wait_time)
    time.sleep(wait_time)
    elapsed = (datetime.datetime.utcnow() - start).seconds
    if elapsed > delta / 2.0:
        print("%s seconds waiting for %s" % \
            (elapsed, res_description))
    assert_less(elapsed, delta)
