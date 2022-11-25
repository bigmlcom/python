# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument,no-member
#
# Copyright 2012-2022 BigML
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

from bigml.api import HTTP_OK
from bigml.api import HTTP_CREATED
from bigml.api import HTTP_ACCEPTED
from bigml.api import FINISHED
from bigml.api import FAULTY
from bigml.api import get_status
from bigml.api import BigML
from bigml.model import Model
from bigml.logistic import LogisticRegression
from bigml.linear import LinearRegression
from bigml.deepnet import Deepnet
from bigml.fusion import Fusion
from bigml.ensemble import Ensemble


from .read_resource_steps import wait_until_status_code_is
from .world import world, res_filename, eq_, ok_


NO_MISSING_SPLITS = {'missing_splits': False}


def i_create_a_model(step, shared=None):
    """Step: I create a model"""
    if shared is None or world.shared.get("model", {}).get(shared) is None:
        dataset = world.dataset.get('resource')
        resource = world.api.create_model(dataset, args=NO_MISSING_SPLITS)
        world.status = resource['code']
        eq_(world.status, HTTP_CREATED)
        world.location = resource['location']
        world.model = resource['object']
        world.models.append(resource['resource'])


def i_export_model(step, pmml, filename):
    """Step: I export the <pmml> model to file <filename>"""
    world.api.export(world.model["resource"], res_filename(filename), pmml)


def i_export_tags_model(step, filename, tag):
    """Step: I export the last model"""
    world.api.export_last(tag,
                          filename=res_filename(filename))


def i_create_a_balanced_model(step):
    """Step: I create a balanced model"""
    dataset = world.dataset.get('resource')
    args = {}
    args.update(NO_MISSING_SPLITS)
    args.update({"balance_objective": True})
    resource = world.api.create_model(dataset, args=args)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.model = resource['object']
    world.models.append(resource['resource'])


def i_create_a_model_from_dataset_list(step):
    """Step: I create a model from a dataset list"""
    resource = world.api.create_model(world.dataset_ids,
                                      args=NO_MISSING_SPLITS)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.model = resource['object']
    world.models.append(resource['resource'])


def wait_until_model_status_code_is(step, code1, code2, secs):
    """Step: I wait until the model status code is either
    <code1> or <code2> less than <secs>
    """
    wait_until_status_code_is(code1, code2, secs, world.model)


def the_model_is_finished_in_less_than(step, secs, shared=None):
    """Step: I wait until the model is ready less than <secs>"""
    if shared is None or world.shared.get("model", {}).get(shared) is None:
        wait_until_model_status_code_is(step, FINISHED, FAULTY, secs)
        if shared is not None:
            if "model" not in world.shared:
                world.shared["model"] = {}
            world.shared["model"][shared] = world.model
        print("New %s" % world.model["resource"])
    else:
        world.model = world.shared["model"][shared]
        print("Reusing %s" % world.model["resource"])


def i_create_a_model_with(step, data="{}"):
    """Step: I create a model with <data>"""
    args = json.loads(data)
    if not 'missing_splits' in args:
        args.update(NO_MISSING_SPLITS)
    resource = world.api.create_model(world.dataset.get('resource'),
                                      args=args)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.model = resource['object']
    world.models.append(resource['resource'])


def i_create_a_model_with_missing_splits(step):
    """Step: I create a model with missing splits"""
    i_create_a_model_with(step, data='{"missing_splits": true}')


def i_create_a_weighted_model_with_missing_splits(step):
    """Step: I create a model with missing splits"""
    i_create_a_model_with(step, data='{"missing_splits": true, "balance_objective": true}')


def make_the_model_public(step):
    """Step: I make the model public"""
    resource = world.api.update_model(world.model['resource'],
                                      {'private': False, 'white_box': True})
    world.status = resource['code']
    if world.status != HTTP_ACCEPTED:
        print("unexpected status: %s" % world.status)
    eq_(world.status, HTTP_ACCEPTED)
    world.location = resource['location']
    world.model = resource['object']


def model_from_public_url(step):
    """Step: I check the model status using the model''s public url"""
    world.model = world.api.get_model("public/%s" % world.model['resource'])
    eq_(get_status(world.model)['code'], FINISHED)


def make_the_model_shared(step):
    """Step: I make the model shared"""
    resource = world.api.update_model(world.model['resource'],
                                      {'shared': True})
    world.status = resource['code']
    eq_(world.status, HTTP_ACCEPTED)
    world.location = resource['location']
    world.model = resource['object']


def get_sharing_info(step):
    """Step: I get the model sharing info"""
    world.shared_hash = world.model['shared_hash']
    world.sharing_key = world.model['sharing_key']


def model_from_shared_url(step):
    """Step: I check the model status using the model's shared url"""
    world.model = world.api.get_model("shared/model/%s" % world.shared_hash)
    eq_(get_status(world.model)['code'], FINISHED)


def model_from_shared_key(step):
    """Step: I check the model status using the model's shared key"""
    username = os.environ.get("BIGML_USERNAME")
    world.model = world.api.get_model(world.model['resource'],
        shared_username=username, shared_api_key=world.sharing_key)
    eq_(get_status(world.model)['code'], FINISHED)


def field_name_to_new_name(step, field_id, new_name):
    """Step: <field_id> field's name is changed to <new_name>"""
    eq_(step.bigml["local_model"].fields[field_id]['name'], new_name)


def i_create_a_model_from_cluster(step, centroid_id):
    """Step: I create a model associated to centroid <centroid_id>"""
    resource = world.api.create_model(
        world.cluster['resource'],
        args={'centroid': centroid_id})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.model = resource['object']
    world.models.append(resource['resource'])


def is_associated_to_centroid_id(step, centroid_id):
    """Step: the model is associated to the centroid <centroid_id> of the
    cluster
    """
    cluster = world.api.get_cluster(world.cluster['resource'])
    world.status = cluster['code']
    eq_(world.status, HTTP_OK)
    eq_("model/%s" % (cluster['object']['cluster_models'][centroid_id]),
        world.model['resource'])


def i_create_a_logistic_model(step, shared=None):
    """Step: I create a logistic regression model"""
    if shared is None or world.shared.get("logistic", {}).get(shared) is None:
        dataset = world.dataset.get('resource')
        resource = world.api.create_logistic_regression(dataset)
        world.status = resource['code']
        eq_(world.status, HTTP_CREATED)
        world.location = resource['location']
        world.logistic_regression = resource['object']
        world.logistic_regressions.append(resource['resource'])


def i_create_a_logistic_model_with_objective_and_parms(step, objective=None,
                                                       parms=None):
    """Step: I create a logistic regression model with objective <objective>
    and parms <parms>
    """
    dataset = world.dataset.get('resource')
    if parms is None:
        parms = {}
    else:
        parms = json.loads(parms)
    if objective is not None:
        parms.update({"objective_field": objective})
    resource = world.api.create_logistic_regression( \
        dataset, parms)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.logistic_regression = resource['object']
    world.logistic_regressions.append(resource['resource'])

def wait_until_logistic_model_status_code_is(step, code1, code2, secs):
    """Step: I wait until the logistic regression model status code is either
    <code1> or <code2> less than <secs>
    """
    world.logistic_regression = wait_until_status_code_is(
        code1, code2, secs, world.logistic_regression)


def the_logistic_model_is_finished_in_less_than(step, secs, shared=None):
    """Step: I wait until the logistic regression model is ready less than
        <secs>
    """
    if shared is None or world.shared.get("logistic", {}).get(shared) is None:
        wait_until_logistic_model_status_code_is(step, FINISHED, FAULTY, secs)
        if shared is not None:
            if "logistic" not in world.shared:
                world.shared["logistic"] = {}
            world.shared["logistic"][shared] = world.logistic_regression
    else:
        world.logistic_regression = world.shared["logistic"][shared]
        print("Reusing %s" % world.logistic_regression["resource"])


def i_create_a_deepnet(step, shared=None):
    """Step: I create a deepnet model"""
    if shared is None or world.shared.get("deepnet", {}).get(shared) is None:
        dataset = world.dataset.get('resource')
        resource = world.api.create_deepnet(dataset)
        world.status = resource['code']
        eq_(world.status, HTTP_CREATED)
        world.location = resource['location']
        world.deepnet = resource['object']
        world.deepnets.append(resource['resource'])


def i_create_a_quick_deepnet(step):
    """Step: I create a quick deepnet"""
    dataset = world.dataset.get('resource')
    resource = world.api.create_deepnet(dataset, {"max_training_time": 100})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.deepnet = resource['object']
    world.deepnets.append(resource['resource'])


def i_create_a_no_suggest_deepnet(step, shared=None):
    """Step: I create a non-suggested deepnet model"""
    if shared is None or \
            world.shared.get("deepnet", {}).get(shared) is None:
        dataset = world.dataset.get('resource')
        resource = world.api.create_deepnet(dataset, {"suggest_structure": False,
                                                      "max_iterations": 100,
                                                      "deepnet_seed": "bigml"})
        world.status = resource['code']
        eq_(world.status, HTTP_CREATED)
        world.location = resource['location']
        world.deepnet = resource['object']
        world.deepnets.append(resource['resource'])


def i_create_a_deepnet_with_objective_and_params(step, objective=None, parms=None):
    """Step: I create a deepnet model with objective <objective> and parms
    <parms>
    """
    dataset = world.dataset.get('resource')
    if parms is None:
        parms = {}
    else:
        parms = json.loads(parms)
    if objective is not None:
        parms.update({"objective_field": objective})
    resource = world.api.create_deepnet(dataset, parms)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.deepnet = resource['object']
    world.deepnets.append(resource['resource'])


def wait_until_deepnet_model_status_code_is(step, code1, code2, secs):
    """Step: I wait until the deepnet model status code is either <code1>
    or <code2> less than <secs>
    """
    world.deepnet = wait_until_status_code_is(code1, code2, secs, world.deepnet)


def the_deepnet_is_finished_in_less_than(step, secs, shared=None):
    """Step: wait until the deepnet model is ready less than <secs>"""
    if shared is None or world.shared.get("deepnet", {}).get(shared) is None:
        wait_until_deepnet_model_status_code_is(step, FINISHED, FAULTY, secs)
        if shared is not None:
            if "deepnete" not in world.shared:
                world.shared["deepnet"] = {}
            world.shared["deepnet"][shared] = world.deepnet
    else:
        world.deepnet = world.shared["deepnet"][shared]
        print("Reusing %s" % world.deepnet["resource"])


def i_check_model_stored(step, filename, pmml):
    """Step: I check the model is stored in <filename> file in <pmml>"""
    with open(res_filename(filename)) as file_handler:
        content = file_handler.read()
        model_id = world.model["resource"][ \
            (world.model["resource"].index("/") + 1):]
        ok_(content.index(model_id) > -1)


def i_read_model_file(step, filename):
    """Step: I read model from file <filename>"""
    with open(res_filename(filename)) as file_handler:
        content = file_handler.read()
        world.model = json.loads(content)


def i_create_an_optiml(step):
    """Step: I create an optiml"""
    dataset = world.dataset.get('resource')
    resource = world.api.create_optiml(dataset)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.optiml = resource['object']
    world.optimls.append(resource['resource'])


def i_create_an_optiml_with_objective_and_params(step, objective=None, parms=None):
    """Step: I create an optiml model with objective <objective> and parms
    <parms>
    """
    dataset = world.dataset.get('resource')
    if parms is None:
        parms = {}
    else:
        parms = json.loads(parms)
    if objective is not None:
        parms.update({"objective_field": objective})
    resource = world.api.create_optiml(dataset, parms)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.optiml = resource['object']
    world.optimls.append(resource['resource'])


def wait_until_optiml_status_code_is(step, code1, code2, secs):
    """Step: I wait until the optiml status code is either <code1> or
    <code2> less than <secs>
    """
    world.optiml = wait_until_status_code_is(code1, code2, secs, world.optiml)


def the_optiml_is_finished_in_less_than(step, secs):
    """Step: I wait until the optiml is ready less than <secs>"""
    wait_until_optiml_status_code_is(step, FINISHED, FAULTY, secs)


def i_update_optiml_name(step, name):
    """Step: I update the optiml name to <name>"""
    resource = world.api.update_optiml(world.optiml['resource'],
                                      {'name': name})
    world.status = resource['code']
    eq_(world.status, HTTP_ACCEPTED)
    world.location = resource['location']
    world.optiml = resource['object']


def i_check_optiml_name(step, name):
    """Step: the optiml name is <name>"""
    optiml_name = world.optiml['name']
    eq_(name, optiml_name)


def i_create_a_fusion(step):
    """Step: I create a fusion"""
    resource = world.api.create_fusion(world.list_of_models,
                                       {"project": world.project_id})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.fusion = resource['object']
    world.fusions.append(resource['resource'])


def i_create_a_fusion_with_weights(step, weights=None):
    """Step: I create a fusion with weights"""
    if weights is None:
        weights = list(range(1, len(world.list_of_models)))
    else:
        weights = json.loads(weights)
    models = []
    try:
        for index, model in enumerate(world.list_of_models):
            models.append({"id": model["resource"], "weight": weights[index]})
    except IndexError:
        pass
    resource = world.api.create_fusion(models,
                                       {"project": world.project_id})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.fusion = resource['object']
    world.fusions.append(resource['resource'])


def i_create_a_fusion_with_objective_and_params(step, objective, parms=None):
    """Step: I create a fusion with objective <objective> and parms <parms>"""
    models = world.list_models
    if parms is None:
        parms = {}
    else:
        parms = json.loads(parms)
    parms.update({"objective_field": objective, "project": world.project_id})
    resource = world.api.create_fusion(models, parms)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.fusion = resource['object']
    world.fusions.append(resource['resource'])


def wait_until_fusion_status_code_is(step, code1, code2, secs):
    """Step: I wait until the fusion status code is either <code1> or
    <code2> less than <secs>
    """
    world.fusion = wait_until_status_code_is(code1, code2, secs, world.fusion)


def the_fusion_is_finished_in_less_than(step, secs):
    """Step: I wait until the fusion is ready less than <secs>"""
    wait_until_fusion_status_code_is(step, FINISHED, FAULTY, secs)


def i_update_fusion_name(step, name):
    """Step: I update the fusion name to <name>"""
    resource = world.api.update_fusion(world.fusion['resource'],
                                       {'name': name})
    world.status = resource['code']
    eq_(world.status, HTTP_ACCEPTED)
    world.location = resource['location']
    world.fusion = resource['object']


def i_check_fusion_name(step, name):
    """Step: the fusion name is <name>"""
    fusion_name = world.fusion['name']
    eq_(name, fusion_name)


def i_create_local_model_from_file(step, export_file):
    """Step: I create a local model from file <export_file>"""
    step.bigml["local_model"] = Model( \
        res_filename(export_file),
        api=BigML("wrong-user", "wrong-api-key"))


def check_model_id_local_id(step):
    """Step: the model ID and the local model ID match"""
    eq_(step.bigml["local_model"].resource_id, world.model["resource"])


def i_export_ensemble(step, filename):
    """Step: I export the ensemble"""
    world.api.export(world.ensemble.get('resource'),
                     filename=res_filename(filename))


def i_create_local_ensemble_from_file(step, export_file):
    """Step: I create a local ensemble from file <export_file>"""
    step.bigml["local_ensemble"] = Ensemble( \
        res_filename(export_file),
        api=BigML("wrong-user", "wrong-api-key"))


def check_ensemble_id_local_id(step):
    """Step: the ensemble ID and the local ensemble ID match"""
    eq_(step.bigml["local_ensemble"].resource_id, world.ensemble["resource"])


def i_export_logistic_regression(step, filename):
    """Step: I export the logistic regression"""
    world.api.export(world.logistic_regression.get('resource'),
                     filename=res_filename(filename))


def i_create_local_logistic_regression_from_file(step, export_file):
    """Step: I create a local logistic regressin from file <export_file>"""
    step.bigml["local_logistic"] = LogisticRegression( \
        res_filename(export_file),
        api=BigML("wrong-user", "wrong-api-key"))


def check_logistic_regression_id_local_id(step):
    """Step: the logistic ID and the local logistic ID match"""
    eq_(step.bigml["local_logistic"].resource_id, world.logistic_regression["resource"])


def i_export_deepnet(step, filename):
    """Step: I export the deepnet"""
    world.api.export(world.deepnet.get('resource'),
                     filename=res_filename(filename))


def i_create_local_deepnet_from_file(step, export_file):
    """Step: I create a local deepnet from file <export_file>"""
    step.bigml["local_deepnet"] = Deepnet(res_filename(export_file),
                                  api=BigML("wrong-user", "wrong-api-key"))


def i_export_fusion(step, filename):
    """Step: I export the fusion"""
    world.api.export(world.fusion.get('resource'),
                     filename=res_filename(filename))


def i_create_local_fusion_from_file(step, export_file):
    """Step: I create a local fusion from file <export_file>"""
    step.bigml["local_fusion"] = Fusion( \
        res_filename(export_file), api=BigML("wrong-user", "wrong-api-key"))


def check_fusion_id_local_id(step):
    """Step: the fusion ID and the local fusion ID match"""
    eq_(step.bigml["local_fusion"].resource_id, world.fusion["resource"])


def i_export_linear_regression(step, filename):
    """Step: I export the linear regression"""
    world.api.export(world.linear_regression.get('resource'),
                     filename=res_filename(filename))


def i_create_local_linear_regression_from_file(step, export_file):
    """Step: I create a local linear regression from file <export_file>"""
    step.bigml["local_linear_regression"] = LinearRegression( \
        res_filename(export_file), api=BigML("wrong-user", "wrong-api-key"))


def check_linear_regression_id_local_id(step):
    """Step: the linear regression ID and the local linear regression ID
    match
    """
    eq_(step.bigml["local_linear_regression"].resource_id,
        world.linear_regression["resource"])


def local_logistic_prediction_is(step, input_data, prediction):
    """Checking local logistic prediction"""
    eq_(step.bigml["local_logistic"].predict(input_data), prediction)


def local_linear_prediction_is(step, input_data, prediction):
    """Checking local linear prediction"""
    eq_(step.bigml["local_linear_regression"].predict(input_data),
        prediction, precision=5)

def local_deepnet_prediction_is(step, input_data, prediction):
    """Checking local deepnet prediction"""
    eq_(step.bigml["local_deepnet"].predict(input_data), prediction, precision=4)


def local_ensemble_prediction_is(step, input_data, prediction):
    """Checking local ensemble prediction"""
    eq_(step.bigml["local_ensemble"].predict(input_data), prediction, precision=5)


def local_model_prediction_is(step, input_data, prediction):
    """Checking local model prediction"""
    eq_(step.bigml["local_model"].predict(input_data), prediction, precision=5)


def local_cluster_prediction_is(step, input_data, prediction):
    """Checking local cluster prediction"""
    eq_(step.bigml["local_cluster"].centroid(input_data), prediction)


def local_anomaly_prediction_is(step, input_data, prediction):
    """Checking local anomaly prediction"""
    eq_(step.bigml["local_anomaly"].anomaly_score(input_data), prediction)


def local_association_prediction_is(step, input_data, prediction):
    """Checking local association prediction"""
    eq_(step.bigml["local_association"].association_set(input_data), prediction)


def local_time_series_prediction_is(step, input_data, prediction):
    """Checking local time series prediction"""
    eq_(step.bigml["local_time_series"].centroid(input_data), prediction)


def clone_model(step, model):
    """Step: I clone model
    """
    resource = world.api.clone_model(model, {'project': world.project_id})
    # update status
    world.status = resource['code']
    world.location = resource['location']
    world.model = resource['object']
    # save reference
    world.models.append(resource['resource'])

def the_cloned_model_is(step, model):
    """Checking the model is a clone"""
    eq_(world.model["origin"], model)


def clone_deepnet(step, deepnet):
    """Step: I clone deepnet"""
    resource = world.api.clone_deepnet(deepnet, {'project': world.project_id})
    # update status
    world.status = resource['code']
    world.location = resource['location']
    world.deepnet = resource['object']
    # save reference
    world.deepnets.append(resource['resource'])


def the_cloned_deepnet_is(step, deepnet):
    """Checking the deepnet is a clone"""
    eq_(world.deepnet["origin"], deepnet)


def clone_logistic_regression(step, logistic_regression):
    """Step: I clone logistic regression"""
    resource = world.api.clone_logistic_regression(
        logistic_regression, {'project': world.project_id})
    # update status
    world.status = resource['code']
    world.location = resource['location']
    world.logistic_regression = resource['object']
    # save reference
    world.logistic_regressions.append(resource['resource'])


def the_cloned_logistic_regression_is(step, logistic_regression):
    """Checking logistic regression is a clone"""
    eq_(world.logistic_regression["origin"], logistic_regression)


def check_deepnet_id_local_id(step):
    """Checking that deepnet ID and local deepnet ID match"""
    eq_(world.deepnet["resource"], step.bigml["local_deepnet"].resource_id)
