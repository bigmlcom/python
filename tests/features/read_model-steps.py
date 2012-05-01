import os
from lettuce import step, world

from bigml.api import HTTP_OK

@step(r'I get the model "(.*)"')
def i_get_the_model(step, model):
    resource = world.api.get_model(model)
    world.status = resource['code']
    assert world.status == HTTP_OK
    world.model = resource['object']

