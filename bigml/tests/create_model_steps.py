# -*- coding: utf-8 -*-

#
# Copyright 2012-2020 BigML
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

import time
import json
import os
from nose.tools import eq_, assert_less
from datetime import datetime
from .world import world, res_filename, logged_wait

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

from . import read_model_steps as read

NO_MISSING_SPLITS = {'missing_splits': False}

#@step(r'I create a model$')
def i_create_a_model(step):
    dataset = world.dataset.get('resource')
    resource = world.api.create_model(dataset, args=NO_MISSING_SPLITS)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.model = resource['object']
    world.models.append(resource['resource'])

#@step(r'I export the model$')
def i_export_model(step, filename):
    world.api.export(world.model.get('resource'),
                     filename=res_filename(filename))


#@step(r'I export the last model$')
def i_export_tags_model(step, filename, tag):
    world.api.export_last(tag,
                          filename=res_filename(filename))

#@step(r'I create a balanced model$')
def i_create_a_balanced_model(step):
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

#@step(r'I create a model from a dataset list$')
def i_create_a_model_from_dataset_list(step):
    resource = world.api.create_model(world.dataset_ids,
                                      args=NO_MISSING_SPLITS)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.model = resource['object']
    world.models.append(resource['resource'])

#@step(r'I wait until the model status code is either (\d) or (-\d) less than (\d+)')
def wait_until_model_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    delta = int(secs) * world.delta
    read.i_get_the_model(step, world.model['resource'])
    status = get_status(world.model)
    count = 0
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
        count += 1
        logged_wait(start, delta, count, "model")
        assert_less((datetime.utcnow() - start).seconds, delta)
        read.i_get_the_model(step, world.model['resource'])
        status = get_status(world.model)
    eq_(status['code'], int(code1))

#@step(r'I wait until the model is ready less than (\d+)')
def the_model_is_finished_in_less_than(step, secs):
    wait_until_model_status_code_is(step, FINISHED, FAULTY, secs)

#@step(r'I create a model with "(.*)"')
def i_create_a_model_with(step, data="{}"):
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

#@step(r'I create a model with missing splits')
def i_create_a_model_with_missing_splits(step):
    i_create_a_model_with(step, data='{"missing_splits": true}')

#@step(r'I create a model with missing splits')
def i_create_a_weighted_model_with_missing_splits(step):
    i_create_a_model_with(step, data='{"missing_splits": true, "balance_objective": true}')


#@step(r'I make the model public')
def make_the_model_public(step):
    resource = world.api.update_model(world.model['resource'],
                                      {'private': False, 'white_box': True})
    world.status = resource['code']
    if world.status != HTTP_ACCEPTED:
        print("unexpected status: %s" % world.status)
    eq_(world.status, HTTP_ACCEPTED)
    world.location = resource['location']
    world.model = resource['object']

#@step(r'I check the model status using the model\'s public url')
def model_from_public_url(step):
    world.model = world.api.get_model("public/%s" % world.model['resource'])
    eq_(get_status(world.model)['code'], FINISHED)

#@step(r'I make the model shared')
def make_the_model_shared(step):
    resource = world.api.update_model(world.model['resource'],
                                      {'shared': True})
    world.status = resource['code']
    eq_(world.status, HTTP_ACCEPTED)
    world.location = resource['location']
    world.model = resource['object']

#@step(r'I get the model sharing info')
def get_sharing_info(step):
    world.shared_hash = world.model['shared_hash']
    world.sharing_key = world.model['sharing_key']

#@step(r'I check the model status using the model\'s shared url')
def model_from_shared_url(step):
    world.model = world.api.get_model("shared/model/%s" % world.shared_hash)
    eq_(get_status(world.model)['code'], FINISHED)

#@step(r'I check the model status using the model\'s shared key')
def model_from_shared_key(step):
    username = os.environ.get("BIGML_USERNAME")
    world.model = world.api.get_model(world.model['resource'],
        shared_username=username, shared_api_key=world.sharing_key)
    eq_(get_status(world.model)['code'], FINISHED)

#@step(r'"(.*)" field\'s name is changed to "(.*)"')
def field_name_to_new_name(step, field_id, new_name):
    eq_(world.local_model.tree.fields[field_id]['name'], new_name)

#@step(r'I create a model associated to centroid "(.*)"')
def i_create_a_model_from_cluster(step, centroid_id):
    resource = world.api.create_model(
        world.cluster['resource'],
        args={'centroid': centroid_id})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.model = resource['object']
    world.models.append(resource['resource'])

#@step(r'the model is associated to the centroid "(.*)" of the cluster')
def is_associated_to_centroid_id(step, centroid_id):
    cluster = world.api.get_cluster(world.cluster['resource'])
    world.status = cluster['code']
    eq_(world.status, HTTP_OK)
    eq_("model/%s" % (cluster['object']['cluster_models'][centroid_id]),
        world.model['resource'])

#@step(r'I create a logistic regression model$')
def i_create_a_logistic_model(step):
    dataset = world.dataset.get('resource')
    resource = world.api.create_logistic_regression(dataset)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.logistic_regression = resource['object']
    world.logistic_regressions.append(resource['resource'])


#@step(r'I create a logistic regression model with objective "(.*?)" and parms "(.*)"$')
def i_create_a_logistic_model_with_objective_and_parms(step, objective, parms=None):
    dataset = world.dataset.get('resource')
    if parms is None:
        parms = {}
    else:
        parms = json.loads(parms)
    parms.update({"objective_field": objective})
    resource = world.api.create_logistic_regression( \
        dataset, parms)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.logistic_regression = resource['object']
    world.logistic_regressions.append(resource['resource'])

#@step(r'I wait until the logistic regression model status code is either (\d) or (-\d) less than (\d+)')
def wait_until_logistic_model_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    delta = int(secs) * world.delta
    read.i_get_the_logistic_model(step, world.logistic_regression['resource'])
    status = get_status(world.logistic_regression)
    count = 0
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
        count += 1
        logged_wait(start, delta, count, "logisticregression")
        read.i_get_the_logistic_model(step, world.logistic_regression['resource'])
        status = get_status(world.logistic_regression)
    eq_(status['code'], int(code1))

#@step(r'I wait until the logistic regression model is ready less than (\d+)')
def the_logistic_model_is_finished_in_less_than(step, secs):
    wait_until_logistic_model_status_code_is(step, FINISHED, FAULTY, secs)

#@step(r'I create a deepnet model$')
def i_create_a_deepnet(step):
    dataset = world.dataset.get('resource')
    resource = world.api.create_deepnet(dataset)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.deepnet = resource['object']
    world.deepnets.append(resource['resource'])


#@step(r'I create a non-suggested deepnet model$')
def i_create_a_no_suggest_deepnet(step):
    dataset = world.dataset.get('resource')
    resource = world.api.create_deepnet(dataset, {"suggest_structure": False,
                                                  "max_iterations": 100,
                                                  "deepnet_seed": "bigml"})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.deepnet = resource['object']
    world.deepnets.append(resource['resource'])

#@step(r'I create a deepnet model with objective "(.*?)" and parms "(.*)"$')
def i_create_a_deepnet_with_objective_and_params(step, objective, parms=None):
    dataset = world.dataset.get('resource')
    if parms is None:
        parms = {}
    else:
        parms = json.loads(parms)
    parms.update({"objective_field": objective})
    resource = world.api.create_deepnet(dataset, parms)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.deepnet = resource['object']
    world.deepnets.append(resource['resource'])

#@step(r'I wait until the deepnet model status code is either (\d) or (-\d) less than (\d+)')
def wait_until_deepnet_model_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    delta = int(secs) * world.delta
    status = get_status(world.deepnet)
    count = 0
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
        count += 1
        logged_wait(start, delta, count, "deepnet")
        read.i_get_the_deepnet_model(step, world.deepnet['resource'])
        status = get_status(world.deepnet)
    eq_(status['code'], int(code1))

#@step(r'I wait until the deepnet model is ready less than (\d+)')
def the_deepnet_is_finished_in_less_than(step, secs):
    wait_until_deepnet_model_status_code_is(step, FINISHED, FAULTY, secs)

#@step(r'I export the "(.*)" model to file "(.*)"$')
def i_export_model(step, pmml, filename):
    world.api.export(world.model["resource"], res_filename(filename), pmml)

#@step(r'I check the model is stored in "(.*)" file in "(.*)"$')
def i_check_model_stored(step, filename, pmml):
    with open(res_filename(filename)) as file_handler:
        content = file_handler.read()
        model_id = world.model["resource"][ \
            (world.model["resource"].index("/") + 1):]
        assert(content.index(model_id) > -1)

#@step(r'I create an optiml$')
def i_create_an_optiml(step):
    dataset = world.dataset.get('resource')
    resource = world.api.create_optiml(dataset)
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.optiml = resource['object']
    world.optimls.append(resource['resource'])

#@step(r'I create an optiml model with objective "(.*?)" and parms "(.*)"$')
def i_create_an_optiml_with_objective_and_params(step, objective=None, parms=None):
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

#@step(r'I wait until the optiml status code is either (\d) or (-\d) less than (\d+)')
def wait_until_optiml_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    delta = int(secs) * world.delta
    read.i_get_the_optiml(step, world.optiml['resource'])
    status = get_status(world.optiml)
    count = 0
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
        count += 1
        logged_wait(start, delta, count, "optiml")
        read.i_get_the_optiml(step, world.optiml['resource'])
        status = get_status(world.optiml)
    eq_(status['code'], int(code1))

#@step(r'I wait until the optiml is ready less than (\d+)')
def the_optiml_is_finished_in_less_than(step, secs):
    wait_until_optiml_status_code_is(step, FINISHED, FAULTY, secs)

#@step(r'I update the optiml name to "(.*)"')
def i_update_optiml_name(step, name):
    resource = world.api.update_optiml(world.optiml['resource'],
                                      {'name': name})
    world.status = resource['code']
    eq_(world.status, HTTP_ACCEPTED)
    world.location = resource['location']
    world.optiml = resource['object']

#@step(r'the optiml name is "(.*)"')
def i_check_optiml_name(step, name):
    optiml_name = world.optiml['name']
    eq_(name, optiml_name)

#@step(r'I create a fusion$')
def i_create_a_fusion(step):
    resource = world.api.create_fusion(world.list_of_models,
                                       {"project": world.project_id})
    world.status = resource['code']
    eq_(world.status, HTTP_CREATED)
    world.location = resource['location']
    world.fusion = resource['object']
    world.fusions.append(resource['resource'])


#@step(r'I create a fusion with weights$')
def i_create_a_fusion_with_weights(step, weights=None):
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

#@step(r'I create a fusion with objective "(.*?)" and parms "(.*)"$')
def i_create_a_fusion_with_objective_and_params(step, objective, parms=None):
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

#@step(r'I wait until the fusion status code is either (\d) or (-\d) less than (\d+)')
def wait_until_fusion_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    delta = int(secs) * world.delta
    read.i_get_the_fusion(step, world.fusion['resource'])
    status = get_status(world.fusion)
    count = 0
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
        count += 1
        logged_wait(start, delta, count, "fusion")
        read.i_get_the_fusion(step, world.fusion['resource'])
        status = get_status(world.fusion)
    eq_(status['code'], int(code1))

#@step(r'I wait until the fusion is ready less than (\d+)')
def the_fusion_is_finished_in_less_than(step, secs):
    wait_until_fusion_status_code_is(step, FINISHED, FAULTY, secs)


#@step(r'I update the fusion name to "(.*)"')
def i_update_fusion_name(step, name):
    resource = world.api.update_fusion(world.fusion['resource'],
                                       {'name': name})
    world.status = resource['code']
    eq_(world.status, HTTP_ACCEPTED)
    world.location = resource['location']
    world.fusion = resource['object']

#@step(r'the fusion name is "(.*)"')
def i_check_fusion_name(step, name):
    fusion_name = world.fusion['name']
    eq_(name, fusion_name)

#@step(r'I create a local model from file "(.*)"')
def i_create_local_model_from_file(step, export_file):
    world.local_model = Model( \
        res_filename(export_file),
        api=BigML("wrong-user", "wrong-api-key"))


#@step(r'the model ID and the local model ID match')
def check_model_id_local_id(step):
    eq_(world.local_model.resource_id, world.model["resource"])


#@step(r'I export the ensemble$')
def i_export_ensemble(step, filename):
    world.api.export(world.ensemble.get('resource'),
                     filename=res_filename(filename))

#@step(r'I create a local ensemble from file "(.*)"')
def i_create_local_ensemble_from_file(step, export_file):
    world.local_ensemble = Ensemble( \
        res_filename(export_file),
        api=BigML("wrong-user", "wrong-api-key"))


#@step(r'the ensemble ID and the local ensemble ID match')
def check_ensemble_id_local_id(step):
    eq_(world.local_ensemble.resource_id, world.ensemble["resource"])


#@step(r'I export the logistic regression$')
def i_export_logistic_regression(step, filename):
    world.api.export(world.logistic_regression.get('resource'),
                     filename=res_filename(filename))

#@step(r'I create a local logistic regressin from file "(.*)"')
def i_create_local_logistic_regression_from_file(step, export_file):
    world.local_logistic = LogisticRegression( \
        res_filename(export_file),
        api=BigML("wrong-user", "wrong-api-key"))


#@step(r'the logistic ID and the local logistic ID match')
def check_logistic_regression_id_local_id(step):
    eq_(world.local_logistic.resource_id, world.logistic_regression["resource"])


#@step(r'I export the deepnet$')
def i_export_deepnet(step, filename):
    world.api.export(world.deepnet.get('resource'),
                     filename=res_filename(filename))

#@step(r'I create a local deepnet from file "(.*)"')
def i_create_local_deepnet_from_file(step, export_file):
    world.local_deepnet = Deepnet(res_filename(export_file),
                                  api=BigML("wrong-user", "wrong-api-key"))


#@step(r'the deepnet ID and the local deepnet ID match')
def check_deepnet_id_local_id(step):
    eq_(world.local_deepnet.resource_id, world.deepnet["resource"])

#@step(r'I export the fusion$')
def i_export_fusion(step, filename):
    world.api.export(world.fusion.get('resource'),
                     filename=res_filename(filename))

#@step(r'I create a local fusion from file "(.*)"')
def i_create_local_fusion_from_file(step, export_file):
    world.local_fusion = Fusion( \
        res_filename(export_file), api=BigML("wrong-user", "wrong-api-key"))


#@step(r'the fusion ID and the local fusion ID match')
def check_fusion_id_local_id(step):
    eq_(world.local_fusion.resource_id, world.fusion["resource"])


#@step(r'I export the linear regression$')
def i_export_linear_regression(step, filename):
    world.api.export(world.linear_regression.get('resource'),
                     filename=res_filename(filename))


#@step(r'I create a local linear regression from file "(.*)"')
def i_create_local_linear_regression_from_file(step, export_file):
    world.local_linear_regression = LinearRegression( \
        res_filename(export_file), api=BigML("wrong-user", "wrong-api-key"))


#@step(r'the linear regression ID and the local linear regression ID match')
def check_linear_regression_id_local_id(step):
    eq_(world.local_linear_regression.resource_id,
        world.linear_regression["resource"])
