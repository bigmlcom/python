# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument,no-member
#
# Copyright 2018-2025 BigML
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


from bigml.api import HTTP_CREATED
from bigml.api import FINISHED, FAULTY
from bigml.io import UnicodeReader

from .read_resource_steps import wait_until_status_code_is
from .world import world, res_filename, eq_, ok_


def i_create_a_batch_projection(step):
    """Step: I create a batch projection for the dataset with the PCA"""
    dataset = world.dataset.get('resource')
    pca = world.pca.get('resource')
    resource = world.api.create_batch_projection(pca, dataset)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.batch_projection = resource['object']
    world.batch_projections.append(resource['resource'])


def wait_until_batch_projection_status_code_is(step, code1, code2, secs):
    """Step: I wait until the batch projection status code is either <code1>
    or <code2> less than <secs>
    """
    world.batch_projection = wait_until_status_code_is(
        code1, code2, secs, world.batch_projection)


def the_batch_projection_is_finished_in_less_than(step, secs):
    """Step: I wait until the batch projection is ready less than <secs>"""
    wait_until_batch_projection_status_code_is(step, FINISHED, FAULTY, secs)


def i_download_projections_file(step, filename):
    """Step: I download the created projections file to <filename>"""
    file_object = world.api.download_batch_projection(
        world.batch_projection, filename=res_filename(filename))
    ok_(file_object is not None)
    world.output = file_object


def i_check_projections(step, check_file):
    """Step: the batch projection file is like <check_file>"""
    with UnicodeReader(world.output) as projection_rows:
        with UnicodeReader(res_filename(check_file)) as test_rows:
            check_csv_rows(projection_rows, test_rows)


def check_csv_rows(projections, expected):
    """Checking expected projections"""
    for projection in projections:
        eq_(projection, next(expected))
