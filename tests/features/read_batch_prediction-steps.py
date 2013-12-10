import os
from lettuce import step, world

from bigml.api import HTTP_OK

@step(r'I get the batch prediction "(.*)"')
def i_get_the_batch_prediction(step, batch_prediction):
    resource = world.api.get_batch_prediction(batch_prediction)
    world.status = resource['code']
    assert world.status == HTTP_OK
    world.batch_prediction = resource['object']

