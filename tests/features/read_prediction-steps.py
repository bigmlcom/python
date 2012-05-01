import os
from lettuce import step, world
from bigml.api import HTTP_OK

@step(r'I get the prediction "(.*)"')
def i_get_the_prediction(step, prediction):
    resource = world.api.get_prediction(prediction)
    world.status = resource['code']
    assert world.status == HTTP_OK
    world.prediction = resource['object']
