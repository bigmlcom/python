# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015-2016 BigML
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

from bigml.api import BigML
from bigml.api import HTTP_OK, HTTP_NO_CONTENT, HTTP_UNAUTHORIZED

MAX_RETRIES = 10
RESOURCE_TYPES = [
    'cluster',
    'source',
    'dataset',
    'model',
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
    'association',
    'script',
    'execution',
    'library'
]
IRREGULAR_PLURALS = {
    'anomaly': 'anomalies',
    'batchprediction': 'batch_predictions',
    'batchcentroid': 'batch_centroids',
    'anomalyscore': 'anomaly_scores',
    'batchanomalyscore': 'batch_anomaly_scores',
    'statisticaltest': 'statistical_tests',
    'logisticregression': 'logistic_regressions',
    'library': 'libraries'
}

TRANSLATED_RESOURCES = {
    'batchprediction': 'batch_prediction',
    'batchcentroid': 'batch_centroid',
    'anomalyscore': 'anomaly_score',
    'batchanomalyscore': 'batch_anomaly_score',
    'statisticaltest': 'statistical_test',
    'logisticregression': 'logistic_regression'
}


def plural(resource_type):
    """Creates the plural form of a resource type

    """
    return IRREGULAR_PLURALS.get(resource_type, "%ss" % resource_type)


class World(object):

    def __init__(self):
        self.USERNAME = None
        self.API_KEY = None
        self.api = None
        self.api_dev_mode = None
        self.reset_api()
        self.clear()
        self.dataset_ids = []
        self.fields_properties_dict = {}
        self.counters = {}
        self.print_connection_info()
        self.test_project_name = "Test: python bindings %s" % \
            datetime.datetime.now()
        self.project_id = None

    def print_connection_info(self):
        self.USERNAME = os.environ.get('BIGML_USERNAME')
        self.API_KEY = os.environ.get('BIGML_API_KEY')
        if self.USERNAME is None or self.API_KEY is None:
            assert False, ("Tests use the BIGML_USERNAME and BIGML_API_KEY"
                           " environment variables to authenticate the"
                           " connection, but they seem to be unset. Please,"
                           "set them before testing.")
        else:
            assert True
        self.api = BigML(self.USERNAME, self.API_KEY)
        print self.api.connection_info()

    def clear(self):
        """Clears the stored resources' ids

        """
        for resource_type in RESOURCE_TYPES:
            setattr(self, plural(resource_type), [])
            setattr(self, TRANSLATED_RESOURCES.get(resource_type,
                                                   resource_type), None)

    def reset_api(self):
        """Reset the api connection values

        """
        self.api = BigML(self.USERNAME, self.API_KEY)
        self.api_dev_mode = BigML(self.USERNAME, self.API_KEY, dev_mode=True)

    def delete_resources(self):
        """Deletes the created objects

        """

        for resource_type in RESOURCE_TYPES:
            object_list = getattr(self, plural(resource_type))
            if object_list:
                print "Deleting %s %s" % (len(object_list),
                                          plural(resource_type))
                delete_method = self.api.deleters[resource_type]
                for obj_id in object_list:
                    counter = 0
                    result = delete_method(obj_id)
                    while (result['code'] != HTTP_NO_CONTENT and
                           counter < MAX_RETRIES):
                        print "Delete failed for %s. Retrying" % obj_id
                        time.sleep(3)
                        counter += 1
                        result = delete_method(obj_id)
                    if counter == MAX_RETRIES:
                        print ("Retries to delete the created resources are"
                               " exhausted. Failed to delete.")


world = World()

def res_filename(file):
    return pkg_resources.resource_filename('bigml', "../../../%s" % file)

def setup_module():
    """Operations to be performed before each module

    """
    world.reset_api()
    if world.project_id is None:
        world.project_id = world.api.create_project( \
            {"name": world.test_project_name})['resource']
    world.clear()

def teardown_module():
    """Operations to be performed after each module

    """

    if os.path.exists('./tmp'):
        shutil.rmtree('./tmp')

    world.delete_resources()
    project_stats = world.api.get_project( \
        world.project_id)['object']['stats']
    for resource_type, value in project_stats.items():
        if value['count'] != 0:
            # assert False, ("Increment in %s: %s" % (resource_type, value))
            print "WARNING: Increment in %s: %s" % (resource_type, value)
    world.api.delete_project(world.project_id)
    world.project_id = None


def teardown_class():
    """Operations to be performed after each class

    """
    world.dataset_ids = []
