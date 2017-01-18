# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2014-2017 BigML
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

# Protocol for main server
BIGML_PROTOCOL = os.environ.get('BIGML_PROTOCOL',
                                DEFAULT_PROTOCOL)

# SSL Verification
BIGML_SSL_VERIFY = os.environ.get('BIGML_SSL_VERIFY')

# Domain for prediction server
BIGML_PREDICTION_DOMAIN = os.environ.get('BIGML_PREDICTION_DOMAIN',
                                         BIGML_DOMAIN)

# Protocol for prediction server
BIGML_PREDICTION_PROTOCOL = os.environ.get('BIGML_PREDICTION_PROTOCOL',
                                           DEFAULT_PROTOCOL)

# SSL Verification for prediction server
BIGML_PREDICTION_SSL_VERIFY = os.environ.get('BIGML_PREDICTION_SSL_VERIFY')


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
                 prediction_protocol=None, protocol=None, verify=None,
                 prediction_verify=None):
        """Domain object constructor.

            @param: domain string Domain name
            @param: prediction_domain string Domain for the prediction server
                    (when different from the general domain)
            @param: prediction_protocol string Protocol for prediction server
                    (when different from the general protocol)
            @param: protocol string Protocol for the service
                    (when different from HTTPS)
            @param: verify boolean Sets on/off the SSL verification
            @param: prediction_verify boolean Sets on/off the SSL verification
                    for the prediction server (when different from the general
                    SSL verification)

        """
        # Base domain for remote resources
        self.general_domain = domain or BIGML_DOMAIN
        self.general_protocol = protocol or BIGML_PROTOCOL
        # Usually, predictions are served from the same domain
        if prediction_domain is None:
            if domain is not None:
                self.prediction_domain = domain
                self.prediction_protocol = protocol or BIGML_PROTOCOL
            else:
                self.prediction_domain = BIGML_PREDICTION_DOMAIN
                self.prediction_protocol = BIGML_PREDICTION_PROTOCOL
        # If the domain for predictions is different from the general domain,
        # for instance in high-availability prediction servers
        else:
            self.prediction_domain = prediction_domain
            self.prediction_protocol = prediction_protocol or \
                BIGML_PREDICTION_PROTOCOL

        # Check SSL when comming from `bigml.io` subdomains or when forced
        # by the external BIGML_SSL_VERIFY environment variable or verify
        # arguments
        self.verify = None
        self.verify_prediction = None
        if self.general_protocol == BIGML_PROTOCOL and \
                (verify is not None or BIGML_SSL_VERIFY is not None):
            try:
                self.verify = verify if verify is not None \
                    else bool(int(BIGML_SSL_VERIFY))
            except ValueError:
                pass
        if self.verify is None:
            self.verify = self.general_domain.lower().endswith(DEFAULT_DOMAIN)
        if  self.prediction_protocol == BIGML_PROTOCOL and \
                (prediction_verify or BIGML_PREDICTION_SSL_VERIFY is not None):
            try:
                self.verify_prediction = prediction_verify \
                    if prediction_verify is not None else \
                    bool(int(BIGML_PREDICTION_SSL_VERIFY))
            except ValueError:
                pass
        if self.verify_prediction is None:
            self.verify_prediction = (
                (self.prediction_domain.lower().endswith(DEFAULT_DOMAIN) and
                 self.prediction_protocol == DEFAULT_PROTOCOL))
