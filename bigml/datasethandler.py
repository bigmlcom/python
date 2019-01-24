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

"""Base class for datasets' REST calls

   https://bigml.com/api/datasets

"""

try:
    import simplejson as json
except ImportError:
    import json


from bigml.bigmlconnection import DOWNLOAD_DIR
from bigml.resourcehandler import ResourceHandler
from bigml.resourcehandler import (check_resource_type,
                                   get_resource_type, resource_is_ready,
                                   check_resource, get_source_id,
                                   get_dataset_id, get_cluster_id)
from bigml.constants import (DATASET_PATH, SOURCE_PATH,
                             TINY_RESOURCE, CLUSTER_PATH)


class DatasetHandler(ResourceHandler):
    """This class is used by the BigML class as
       a mixin that provides the REST calls to datasets. It should not
       be instantiated independently.

    """
    def __init__(self):
        """Initializes the DatasetHandler. This class is intended to be
           used as a mixin on ResourceHandler, that inherits its
           attributes and basic method from BigMLConnection, and must not be
           instantiated independently.

        """
        self.dataset_url = self.url + DATASET_PATH

    def create_dataset(self, origin_resource, args=None,
                       wait_time=3, retries=10):
        """Creates a remote dataset.

        Uses a remote resource to create a new dataset using the
        arguments in `args`.
        The allowed remote resources can be:
            - source
            - dataset
            - list of datasets
            - cluster
        In the case of using cluster id as origin_resources, a centroid must
        also be provided in the args argument. The first centroid is used
        otherwise.
        If `wait_time` is higher than 0 then the dataset creation
        request is not sent until the `source` has been created successfuly.

        """
        create_args = {}
        if args is not None:
            create_args.update(args)

        if isinstance(origin_resource, list):
            # mutidatasets
            create_args = self._set_create_from_datasets_args(
                origin_resource, args=create_args, wait_time=wait_time,
                retries=retries, key="origin_datasets")
        else:
            # dataset from source
            resource_type = get_resource_type(origin_resource)
            if resource_type == SOURCE_PATH:
                source_id = get_source_id(origin_resource)
                if source_id:
                    check_resource(source_id,
                                   query_string=TINY_RESOURCE,
                                   wait_time=wait_time,
                                   retries=retries,
                                   raise_on_error=True, api=self)
                    create_args.update({
                        "source": source_id})
            # dataset from dataset
            elif resource_type == DATASET_PATH:
                create_args = self._set_create_from_datasets_args(
                    origin_resource, args=create_args, wait_time=wait_time,
                    retries=retries, key="origin_dataset")
            # dataset from cluster and centroid
            elif resource_type == CLUSTER_PATH:
                cluster_id = get_cluster_id(origin_resource)
                cluster = check_resource(cluster_id,
                                         query_string=TINY_RESOURCE,
                                         wait_time=wait_time,
                                         retries=retries,
                                         raise_on_error=True, api=self)
                if 'centroid' not in create_args:
                    try:
                        centroid = cluster['object'][
                            'cluster_datasets_ids'].keys()[0]
                        create_args.update({'centroid': centroid})
                    except KeyError:
                        raise KeyError("Failed to generate the dataset. A "
                                       "centroid id is needed in the args "
                                       "argument to generate a dataset from "
                                       "a cluster.")
                create_args.update({'cluster': cluster_id})
            else:
                raise Exception("A source, dataset, list of dataset ids"
                                " or cluster id plus centroid id are needed"
                                " to create a"
                                " dataset. %s found." % resource_type)

        body = json.dumps(create_args)
        return self._create(self.dataset_url, body)

    def get_dataset(self, dataset, query_string=''):
        """Retrieves a dataset.

           The dataset parameter should be a string containing the
           dataset id or the dict returned by create_dataset.
           As dataset is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, the function will
           return a dict that encloses the dataset values and state info
           available at the time it is called.
        """
        check_resource_type(dataset, DATASET_PATH,
                            message="A dataset id is needed.")
        dataset_id = get_dataset_id(dataset)
        if dataset_id:
            return self._get("%s%s" % (self.url, dataset_id),
                             query_string=query_string)

    def dataset_is_ready(self, dataset):
        """Check whether a dataset' status is FINISHED.

        """
        check_resource_type(dataset, DATASET_PATH,
                            message="A dataset id is needed.")
        resource = self.get_dataset(dataset)
        return resource_is_ready(resource)

    def list_datasets(self, query_string=''):
        """Lists all your datasets.

        """
        return self._list(self.dataset_url, query_string)

    def update_dataset(self, dataset, changes):
        """Updates a dataset.

        """
        check_resource_type(dataset, DATASET_PATH,
                            message="A dataset id is needed.")
        dataset_id = get_dataset_id(dataset)
        if dataset_id:
            body = json.dumps(changes)
            return self._update("%s%s" % (self.url, dataset_id), body)

    def delete_dataset(self, dataset):
        """Deletes a dataset.

        """
        check_resource_type(dataset, DATASET_PATH,
                            message="A dataset id is needed.")
        dataset_id = get_dataset_id(dataset)
        if dataset_id:
            return self._delete("%s%s" % (self.url, dataset_id))

    def error_counts(self, dataset, raise_on_error=True):
        """Returns the ids of the fields that contain errors and their number.

           The dataset argument can be either a dataset resource structure
           or a dataset id (that will be used to retrieve the associated
           remote resource).

        """
        errors_dict = {}
        if not isinstance(dataset, dict) or 'object' not in dataset:
            check_resource_type(dataset, DATASET_PATH,
                                message="A dataset id is needed.")
            dataset_id = get_dataset_id(dataset)
            dataset = check_resource(dataset_id, self.get_dataset,
                                     raise_on_error=raise_on_error)
            if not raise_on_error and dataset['error'] is not None:
                dataset_id = None
        else:
            dataset_id = get_dataset_id(dataset)
        if dataset_id:
            errors = dataset.get('object', {}).get(
                'status', {}).get('field_errors', {})
            for field_id in errors:
                errors_dict[field_id] = errors[field_id]['total']
        return errors_dict


    def download_dataset(self, dataset, filename=None, retries=10):
        """Donwloads dataset contents to a csv file or file object

        """
        check_resource_type(dataset, DATASET_PATH,
                            message="A dataset id is needed.")
        dataset_id = get_dataset_id(dataset)
        if dataset_id:
            return self._download("%s%s%s" % (self.url, dataset_id,
                                              DOWNLOAD_DIR),
                                  filename=filename,
                                  retries=retries)
