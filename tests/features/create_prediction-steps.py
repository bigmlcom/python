import json
from lettuce import step, world
from bigml.api import HTTP_CREATED

@step(r'I create a prediction for "(.*)"')
def i_create_a_prediction(step, data=None):
    if data is None:
        data = "{}"
    model = world.model['resource']
    data = json.loads(data)
    resource = world.api.create_prediction(model, data)
    world.status = resource['code']
    assert world.status == HTTP_CREATED
    world.location = resource['location']
    world.prediction = resource['object']
    world.predictions.append(resource['resource'])

@step(r'the prediction for "(.*)" is "(.*)"')
def the_prediction_is(step, objective, prediction):
    assert world.prediction['prediction'][objective] == prediction
