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


""" Mimic World lettuce object

"""
import os
import re
import shutil
import time
import pkg_resources
import datetime
import pprint
import json

from bigml.api import BigML
from bigml.api import HTTP_OK, HTTP_NO_CONTENT, HTTP_UNAUTHORIZED, \
    HTTP_NOT_FOUND
from bigml.constants import IRREGULAR_PLURALS, RENAMED_RESOURCES, \
    TINY_RESOURCE, ALL_FIELDS
from bigml.api_handlers.externalconnectorhandler import get_env_connection_info
from bigml.util import get_exponential_wait
from nose.tools import assert_less, eq_

MAX_RETRIES = 10
RESOURCE_TYPES = [
    'cluster',
    'fusion',
    'optiml',
    'composite',
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

def show_method(self, method, example):
    """Prints the test class and method of the current test"""
    class_name = re.sub(".*'(.*)'.*", "\\1", str(self.__class__))
    print("\nTesting %s %s with:\n" % (class_name, method), example)


def float_round(value, precision=5):
    if isinstance(value, float):
        return round(value, precision)
    return value


def flatten_shared(shared_dict):
    """Returns the list of IDs stored in the world.shared structure """
    ids_list = []
    for _, value in world.shared.items():
        for _, resource in value.items():
            ids_list.append(resource["resource"])
    return ids_list


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
        self.errors = []
        self.shared = {}

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
                         short_debug=self.short_debug,
                         organization=None if not hasattr(
                            self.api, "organization") else organization,
                         storage=(None if not (self.debug or self.short_debug)
                         else "./debug_storage"))
        print("----------------------------------------------------------")
        print(self.api.connection_info())
        print(self.external_connection_info())
        print("----------------------------------------------------------")


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

    def _delete_resources(self, object_list, resource_type):
        """Deletes resources grouped by type"""
        if object_list:
            print("Deleting %s %s" % (len(object_list),
                                      plural(resource_type)))
            kwargs = {}
            if resource_type == "composite":
                resource_type = "source"
                kwargs = {"query_string": "delete_all=true"}
            delete_method = self.api.deleters[resource_type]
            for obj_id in object_list:
                counter = 0
                print("Deleting %s" % obj_id)
                result = delete_method(obj_id, **kwargs)
                while (result['code'] not in [HTTP_NO_CONTENT,
                                              HTTP_NOT_FOUND] and
                       counter < MAX_RETRIES):
                    print("Delete failed for %s. Retrying" % obj_id)
                    time.sleep(3 * self.delta)
                    counter += 1
                    result = delete_method(obj_id, **kwargs)
                if counter == MAX_RETRIES:
                    print ("Retries to delete the created resources are"
                           " exhausted. Failed to delete.")

    def delete_resources(self):
        """Deletes the created objects"""
        keepers = flatten_shared(self.shared)
        for resource_type in RESOURCE_TYPES:
            object_list = getattr(self, plural(resource_type))
            object_list.reverse()
            object_list = [obj for obj in object_list if obj not in keepers]
            self._delete_resources(object_list, resource_type)
        if world.errors:
            print("Failed resources: \n\n")
        for resource in world.errors:
            print(json.dumps(resource["status"], indent=4))

    def store_resources(self):
        """Stores the created objects

        """

        for resource_type in RESOURCE_TYPES:
            object_list = set(getattr(self, plural(resource_type)))
            if object_list:
                print("Storing %s %s" % (len(object_list),
                                         plural(resource_type)))
                if resource_type == "composite":
                    resource_type = "source"
                store_method = self.api.getters[resource_type]
                for obj_id in object_list:
                    counter = 0
                    result = store_method(obj_id)
                    self.api.ok(result)

    def get_minimal_resource(self, resource_id):
        """Retrieving resource info in a minimal way to get status info"""
        return self.api.get_resource(
            resource_id, query_string=TINY_RESOURCE)

    def get_maximal_resource(self, resource_id):
        """Retrieving all resource info for local handling"""
        return self.api.get_resource(
            resource_id, query_string=ALL_FIELDS)

    def eq_(*args, **kwargs):
        if "precision" in kwargs:
            precision = kwargs["precision"]
            del kwargs["precision"]
            new_args = list(args)[1:]
            for index, arg in enumerate(new_args):
                new_args[index] = float_round(arg, precision)
        return eq_(*new_args, **kwargs)


world = World()

def res_filename(file):
    return pkg_resources.resource_filename('bigml', "../%s" % file)

def setup_module():
    """Operations to be performed before each module

    """
    if world.project_id is None:
        if "project" not in world.shared:
            world.shared["project"] = {}
        world.shared["project"]["common"] = world.api.create_project( \
            {"name": world.test_project_name})
        world.project_id = world.shared["project"]["common"]['resource']
        print("Creating common project: ", world.project_id)
    world.clear()

def teardown_module():
    """Operations to be performed after each module

    """
    print("Teardown module ---------------------------")
    teardown_fn(force=False)


def teardown_fn(force=False):
    if not world.debug and not world.short_debug:
        if os.path.exists('./tmp'):
            shutil.rmtree('./tmp')

        world.delete_resources()
        project_stats = world.api.get_project( \
            world.project_id)['object']['stats']
        if force:
            world.api.delete_project(world.project_id)
            del world.shared["project"]
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


def logged_wait(start, delta, count, res_description, progress=0, status=None):
    """Comparing the elapsed time to the expected delta and waiting for
       the next sleep period.

    """
    if status is not None:
        progress = status.get("progress", 0)
        status_code = status.get("code")
    progress_dumping = progress if progress > 0.8 \
        else 0 # dumping when almost finished
    wait_time = min(get_exponential_wait(
        ((1.0 - progress_dumping) * delta / 100.0) + 0.5, count), delta)
    message = ""
    if status is not None:
        message =" (status: %s, progress: %s)" % (
            status["code"],
            progress)
    print("Waiting for %s%s %s secs." % (
        res_description,
        message,
        wait_time))
    time.sleep(wait_time)
    elapsed = (datetime.datetime.utcnow() - start).seconds
    if elapsed > delta / 2.0:
        print("%s seconds waiting for %s" % \
            (elapsed, res_description))
    assert_less(elapsed, delta)
