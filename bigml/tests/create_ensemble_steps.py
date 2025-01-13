# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument,no-member,broad-except
#
# Copyright 2012-2025 BigML
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

import json
import os

from bigml.api import HTTP_CREATED
from bigml.api import FINISHED, FAULTY
from bigml.ensemble import Ensemble
from bigml.ensemblepredictor import EnsemblePredictor
from bigml.model import Model
from bigml.supervised import SupervisedModel
from bigml.local_model import LocalModel

from .read_resource_steps import wait_until_status_code_is
from .world import world, res_filename, eq_

NO_MISSING_SPLITS = {'missing_splits': False}
ENSEMBLE_SAMPLE = {'seed': 'BigML',
                   'ensemble_sample': {"rate": 0.7, "seed": 'BigML'}}


def i_create_an_ensemble(step, number_of_models=2, shared=None):
    """Step: I create an ensemble of <number_of_models> models"""
    if shared is None or world.shared.get("ensemble", {}).get(shared) is None:
        dataset = world.dataset.get('resource')
        try:
            number_of_models = int(number_of_models)
            # tlp is no longer used
            args = {'number_of_models': number_of_models}
        except Exception:
            args = {}
        args.update(NO_MISSING_SPLITS)
        args.update(ENSEMBLE_SAMPLE)
        resource = world.api.create_ensemble(dataset, args=args)
        world.status = resource['code']
        eq_(world.status, HTTP_CREATED)
        world.location = resource['location']
        world.ensemble = resource['object']
        world.ensemble_id = resource['resource']
        world.ensembles.append(resource['resource'])


def wait_until_ensemble_status_code_is(step, code1, code2, secs):
    """Step: I wait until the ensemble status code is either <code1> or
    <code2> less than <secs>
    """
    world.ensemble = wait_until_status_code_is(
        code1, code2, secs, world.ensemble)


def the_ensemble_is_finished_in_less_than(step, secs, shared=None):
    """Step: I wait until the ensemble is ready less than <secs>"""
    if shared is None or world.shared.get("ensemble", {}).get(shared) is None:
        wait_until_ensemble_status_code_is(step, FINISHED, FAULTY, secs)
        if shared is not None:
            if "ensemble" not in world.shared:
                world.shared["ensemble"] = {}
            world.shared["ensemble"][shared] = world.ensemble
    else:
        world.ensemble = world.shared["ensemble"][shared]
        world.ensemble_id = world.ensemble["resource"]
        print("Reusing %s" % world.ensemble["resource"])


def create_local_ensemble(step, path=None):
    """Step: I create a local Ensemble"""
    if path is None:
        step.bigml["local_ensemble"] = Ensemble(world.ensemble_id, world.api)
        step.bigml["local_model"] = Model(
            step.bigml["local_ensemble"].model_ids[0], world.api)
    else:
        step.bigml["local_ensemble"] = Ensemble(res_filename(path))
        step.bigml["local_model"] = step.bigml[
            "local_ensemble"].multi_model.models[0]


def create_local_supervised_ensemble(step):
    """Step: I create a local Ensemble"""
    step.bigml["local_ensemble"] = SupervisedModel(world.ensemble_id, world.api)
    step.bigml["local_model"] = Model(step.bigml[
        "local_ensemble"].model_ids[0], world.api)


def create_local_bigml_ensemble(step):
    """Step: I create a local Ensemble"""
    step.bigml["local_ensemble"] = LocalModel(world.ensemble_id, world.api)
    step.bigml["local_model"] = Model(step.bigml[
        "local_ensemble"].model_ids[0], world.api)

def create_local_ensemble_predictor(step, directory):
    """Step: I create a local EnsemblePredictor from <directory>"""
    directory_path = res_filename(directory)
    with open(os.path.join(directory_path, "ensemble.json")) as file_handler:
        ensemble = json.load(file_handler)
    step.bigml["local_ensemble"] = EnsemblePredictor(ensemble, directory)


def load_full_ensemble(step, directory):
    """Step: Given I load the full ensemble information from <directory>"""
    model_list = []
    directory_path = res_filename(directory)
    with open(os.path.join(directory_path, "ensemble.json")) as file_handler:
        ensemble = json.load(file_handler)
        model_list.append(ensemble)
    for model_id in ensemble["object"]["models"]:
        with open(os.path.join(directory_path, model_id.replace("/", "_"))) \
                as file_handler:
            model = json.load(file_handler)
            model_list.append(model)
    return model_list


def create_local_ensemble_with_list(step, number_of_models):
    """Step: I create a local Ensemble with the last <number_of_models>
    models
    """
    step.bigml["local_ensemble"] = Ensemble(world.models[-int(number_of_models):],
                                    world.api)


def create_local_ensemble_from_list(step, model_list):
    """Step: I create a local ensemble from the ensemble <model_list>
    models list
    """
    step.bigml["local_ensemble"] = Ensemble(model_list)


def create_local_ensemble_with_list_of_local_models(step, number_of_models):
    """Step: I create a local Ensemble with the last <number_of_models>
    local models"""
    local_models = [Model(model) for model in
                    world.models[-int(number_of_models):]]
    step.bigml["local_ensemble"] = Ensemble(local_models, world.api)


def field_importance_print(step, field_importance):
    """Step: the field importance text is <field_importance>"""
    field_importance_data = step.bigml["local_ensemble"].field_importance_data()[0]
    eq_(field_importance_data, json.loads(field_importance))


def i_create_an_ensemble_with_params(step, params):
    """Step: I create an ensemble with <params>"""
    dataset = world.dataset.get('resource')
    try:
        args = json.loads(params)
    except Exception:
        args = {}
    args.update(ENSEMBLE_SAMPLE)
    resource = world.api.create_ensemble(dataset, args=args)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.ensemble = resource['object']
    world.ensemble_id = resource['resource']
    world.ensembles.append(resource['resource'])


def i_export_ensemble(step, filename):
    """Step: I export the ensemble"""
    world.api.export(world.ensemble.get('resource'),
                     filename=res_filename(filename))


def i_create_local_ensemble_from_file(step, export_file):
    """Step: I create a local ensemble from file <export_file>"""
    step.bigml["local_ensemble"] = Ensemble(res_filename(export_file))


def check_ensemble_id_local_id(step):
    """Step: the ensemble ID and the local ensemble ID match"""
    eq_(step.bigml["local_ensemble"].resource_id, world.ensemble["resource"])


def clone_ensemble(step, ensemble):
    """Step: I clone ensemble"""
    resource = world.api.clone_ensemble(ensemble,
                                        {'project': world.project_id})
    # update status
    world.status = resource['code']
    world.location = resource['location']
    world.ensemble = resource['object']
    # save reference
    world.ensembles.append(resource['resource'])


def the_cloned_ensemble_is(step, ensemble):
    """Checking the ensemble is a clone"""
    eq_(world.ensemble["origin"], ensemble)
