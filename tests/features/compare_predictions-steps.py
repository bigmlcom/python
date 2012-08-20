import json
from lettuce import step, world
from bigml.model import Model

@step(r'I create a local model')
def i_create_a_local_model(step):
    world.local_model = Model(world.model)

@step(r'I create a local prediction for "(.*)"')
def i_create_a_local_prediction(step, data=None):
    if data is None:
        data = "{}"
    data = json.loads(data)
    world.local_prediction = world.local_model.predict(data)

@step(r'the local prediction is "(.*)"')
def the_local_prediction_is(step, prediction):
    assert world.local_prediction == prediction
