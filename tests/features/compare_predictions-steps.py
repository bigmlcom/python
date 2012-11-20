import json
from lettuce import step, world
from bigml.model import Model
from bigml.multimodel import MultiModel

@step(r'I retrieve a list of remote models tagged with "(.*)"')
def i_retrieve_a_list_of_remote_models(step, tag):
    world.list_of_models = [world.api.get_model(model['resource']) for model in
                            world.api.list_models(query_string="tags__in=%s" % tag)['objects']]

@step(r'I create a local model')
def i_create_a_local_model(step):
    world.local_model = Model(world.model)

@step(r'I create a local prediction for "(.*)"')
def i_create_a_local_prediction(step, data=None):
    if data is None:
        data = "{}"
    data = json.loads(data)
    world.local_prediction = world.local_model.predict(data)

@step(r'I create a prediction from a multi model for "(.*)"')
def i_create_a_prediction_from_a_multi_model(step, data=None):
    if data is None:
        data = "{}"
    data = json.loads(data)
    world.local_prediction = world.local_model.predict(data)

@step(r'the local prediction is "(.*)"')
def the_local_prediction_is(step, prediction):
    assert world.local_prediction == prediction

@step(r'I create a local multi model')
def i_create_a_local_multi_model(step):
    world.local_model = MultiModel(world.list_of_models)

