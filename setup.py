#!/usr/bin/env python
#
# Copyright 2012 - 2017-2019 BigML, Inc
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

import os
import re
import sys

import setuptools

# Get the path to this project
project_path = os.path.dirname(__file__)

# Read the version from bigml.__version__ without importing the package
# (and thus attempting to import packages it depends on that may not be
# installed yet)
version_py_path = os.path.join(project_path, 'bigml', 'version.py')
version = re.search("__version__ = '([^']+)'",
                    open(version_py_path).read()).group(1)

# Concatenate files into the long description
file_contents = []
for file_name in ('README.rst', 'HISTORY.rst'):
    path = os.path.join(os.path.dirname(__file__), file_name)
    file_contents.append(open(path).read())
long_description = '\n\n'.join(file_contents)

INSTALL_REQUIRES = ["unidecode", "bigml-chronos>=0.4.3", "requests",
                    "requests-toolbelt", "numpy", "scipy", "msgpack"]

setuptools.setup(
    name="bigml",
    description="An open source binding to BigML.io, the public BigML API",
    long_description=long_description,
    version=version,
    author="The BigML Team",
    author_email="bigml@bigml.com",
    url="https://bigml.com/developers",
    download_url="https://github.com/bigmlcom/python",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    setup_requires = ['nose'],
    install_requires = INSTALL_REQUIRES,
    packages = ['bigml', 'bigml.tests', 'bigml.laminar', 'bigml.out_model',
                'bigml.out_tree', 'bigml.tests.my_ensemble',
                'bigml.api_handlers', 'bigml.predicate_utils'],
    package_data={'bigml':['out_model/static/*']},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    test_suite='nose.collector'
)
