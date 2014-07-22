# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2014 BigML
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

"""Domain class to handle domain assignation for VPCs

"""
import os

# Default domain and protocol
DEFAULT_DOMAIN = 'bigml.io'
DEFAULT_PROTOCOL = 'https'

# Base Domain
BIGML_DOMAIN = os.environ.get('BIGML_DOMAIN', DEFAULT_DOMAIN)

# Domain for prediction server
BIGML_PREDICTION_DOMAIN = os.environ.get('BIGML_PREDICTION_DOMAIN',
                                         BIGML_DOMAIN)

# Protocol for prediction server
BIGML_PREDICTION_PROTOCOL = os.environ.get('BIGML_PREDICTION_PROTOCOL',
                                           DEFAULT_PROTOCOL)


class Domain(object):
    """A Domain object to store the remote domain information for the API

       The domain that serves the remote resources can be set globally for
       all the resources either by setting the BIGML_DOMAIN environment
       variable

       export BIGML_DOMAIN=my_VPC.bigml.io

       or can be given in the constructor using the `domain` argument.

       my_domain = Domain("my_VPC.bigml.io")

       You can also specify a separate domain to handle predictions. This can
       be set by using the BIGML_PREDICTION_DOMAIN and
       BIGML_PREDICTION_PROTOCOL
       environment variables

       export BIGML_PREDICTION_DOMAIN=my_prediction_server.bigml.com
       export BIGML_PREDICITION_PROTOCOL=https

       or the `prediction_server` and `prediction_protocol` arguments.

       The constructor values will override the environment settings.
    """

    def __init__(self, domain=None, prediction_domain=None,
                 prediction_protocol=None):
        # Base domain for remote resources
        self.general_domain = BIGML_DOMAIN if domain is None else domain

        # Usually, predictions are served from the same domain
        if prediction_domain is None:
            if domain is not None:
                self.prediction_domain = domain
                self.prediction_protocol = DEFAULT_PROTOCOL
            else:
                self.prediction_domain = BIGML_PREDICTION_DOMAIN
                self.prediction_protocol = BIGML_PREDICTION_PROTOCOL
        # If the domain for predictions is different from the general domain,
        # for instance in high-availability prediction servers
        else:
            self.prediction_domain = prediction_domain
            if prediction_protocol is None:
                self.prediction_protocol = BIGML_PREDICTION_PROTOCOL
            else:
                self.prediction_protocol = prediction_protocol

        # Check SSL when comming from `bigml.io` subdomains
        self.verify = self.general_domain.lower().endswith(DEFAULT_DOMAIN)
        self.verify_prediction = (
            (self.prediction_domain.lower().endswith(DEFAULT_DOMAIN) and
             self.prediction_protocol == DEFAULT_PROTOCOL))
