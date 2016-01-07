#!/usr/bin/env python
#
# Copyright 2012, 2015-2016 BigML, Inc
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
init_py_path = os.path.join(project_path, 'bigml', '__init__.py')
version = re.search("__version__ = '([^']+)'",
                    open(init_py_path).read()).group(1)

# Concatenate files into the long description
file_contents = []
for file_name in ('README.rst', 'HISTORY.rst'):
    path = os.path.join(os.path.dirname(__file__), file_name)
    file_contents.append(open(path).read())
long_description = '\n\n'.join(file_contents)

PYTHON_VERSION = sys.version_info[0:3]
PYTHON_REQUESTS_CHANGE = (2, 7, 9)
REQUESTS_VERSION = "requests==2.5.3" if \
    PYTHON_VERSION < PYTHON_REQUESTS_CHANGE else "requests"
INSTALL_REQUIRES = [REQUESTS_VERSION, "unidecode"]
if PYTHON_VERSION[0] < 3:
    INSTALL_REQUIRES.append('poster')

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
    packages = ['bigml', 'bigml.tests'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    test_suite='nose.collector',
    use_2to3=True
)
