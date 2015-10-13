import os
from world import world

from bigml.api import HTTP_OK

#@step(r'I get the model "(.*)"')
def i_get_the_model(step, model):
    resource = world.api.get_model(model)
    world.status = resource['code']
    assert world.status == HTTP_OK
    world.model = resource['object']

#@step(r'I get the logistic regression model "(.*)"')
def i_get_the_logistic_model(step, model):
    resource = world.api.get_logistic_regression(model)
    world.status = resource['code']
    assert world.status == HTTP_OK
    world.logistic_regression = resource['object']
