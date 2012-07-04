#!/usr/bin/env python
#
# Copyright 2012 BigML, Inc
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

import distutils.core
import sys
# Importing setuptools adds some features like "setup.py develop", but
# it's optional so swallow the error if it's not there.
try:
    import setuptools
except ImportError:
    pass

version = "0.2"

distutils.core.setup(
    name="bigml",
    description="An open source binding to BigML.io, the public BigML API",
    version=version,
    author="The BigML Team",
    author_email="bigml@bigml.com",
    url="https:/bigml.com/developers",
    download_url="https://github.com/bigmlcom/io",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    setup_requires = [],
    packages = ['bigml'],
    include_package_data = True,
    install_requires = ['requests'],
)
