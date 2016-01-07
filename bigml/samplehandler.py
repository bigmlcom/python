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

"""Base class for samples' REST calls

   https://bigml.com/developers/samples

"""

try:
    import simplejson as json
except ImportError:
    import json


from bigml.resourcehandler import ResourceHandler
from bigml.resourcehandler import (check_resource_type,
                                   get_sample_id, get_resource_type,
                                   get_dataset_id, check_resource)
from bigml.constants import (SAMPLE_PATH, DATASET_PATH,
                             TINY_RESOURCE)


class SampleHandler(ResourceHandler):
    """This class is used by the BigML class as
       a mixin that provides the samples' REST calls. It should not
       be instantiated independently.

    """
    def __init__(self):
        """Initializes the SampleHandler. This class is intended to be
           used as a mixin on ResourceHandler, that inherits its
           attributes and basic method from BigMLConnection, and must not be
           instantiated independently.

        """
        self.sample_url = self.url + SAMPLE_PATH

    def create_sample(self, dataset, args=None, wait_time=3, retries=10):
        """Creates a sample from a `dataset`.

        """
        dataset_id = None
        resource_type = get_resource_type(dataset)
        if resource_type == DATASET_PATH:
            dataset_id = get_dataset_id(dataset)
            check_resource(dataset_id,
                           query_string=TINY_RESOURCE,
                           wait_time=wait_time, retries=retries,
                           raise_on_error=True, api=self)
        else:
            raise Exception("A dataset id is needed to create a"
                            " sample. %s found." % resource_type)

        create_args = {}
        if args is not None:
            create_args.update(args)
        create_args.update({
            "dataset": dataset_id})

        body = json.dumps(create_args)
        return self._create(self.sample_url, body)

    def get_sample(self, sample, query_string=''):
        """Retrieves a sample.

           The sample parameter should be a string containing the
           sample id or the dict returned by create_sample.
           As sample is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, the function will
           return a dict that encloses the sample values and state info
           available at the time it is called.
        """
        check_resource_type(sample, SAMPLE_PATH,
                            message="A sample id is needed.")
        sample_id = get_sample_id(sample)
        if sample_id:
            return self._get("%s%s" % (self.url, sample_id),
                             query_string=query_string)

    def list_samples(self, query_string=''):
        """Lists all your samples.

        """
        return self._list(self.sample_url, query_string)

    def update_sample(self, sample, changes):
        """Updates a sample.

        """
        check_resource_type(sample, SAMPLE_PATH,
                            message="A sample id is needed.")
        sample_id = get_sample_id(sample)
        if sample_id:
            body = json.dumps(changes)
            return self._update("%s%s" % (self.url, sample_id), body)

    def delete_sample(self, sample):
        """Deletes a sample.

        """
        check_resource_type(sample, SAMPLE_PATH,
                            message="A sample id is needed.")
        sample_id = get_sample_id(sample)
        if sample_id:
            return self._delete("%s%s" % (self.url, sample_id))
