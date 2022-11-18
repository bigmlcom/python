# -*- coding: utf-8 -*-
#
# Copyright 2022 BigML
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


""" Checking webhooks secrets

"""
import json

from collections import OrderedDict
from bigml.webhooks import check_signature

from .world import world, setup_module, teardown_module, show_doc, \
    show_method, delete_local


BIGML_SECRET = 'mysecret'

BIGML_REQUEST_MOCKUP = {
    "body": {
        'event': 'finished',
        'message': 'The source has been created',
        'resource': 'source/627eceb1d432eb7338001d4b',
        'timestamp': '2022-05-13 21:33:39 GMT'
    },
    "META": {
        'HTTP_X_BIGML_SIGNATURE': "sha1=af38d979e8582d678653a8059ca0821daeedebbd"
    }
}


class RequestMockup(object):
    def __init__(self, request_dict):
        self.body = json.dumps(request_dict["body"], sort_keys=True)
        self.META = request_dict["META"]


class TestWebhook(object):

    def setup_method(self):
        """
            Debug information
        """
        print("\n-------------------\nTests in: %s\n" % __name__)

    def teardown_method(self):
        """
            Debug information
        """
        delete_local()
        print("\nEnd of tests in: %s\n-------------------\n" % __name__)

    def test_scenario1(self):
        """
            Scenario: Testing webhook secret signature
        """
        show_doc(self.test_scenario1)
        assert check_signature(RequestMockup(BIGML_REQUEST_MOCKUP),
                               BIGML_SECRET)
