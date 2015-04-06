import os
from world import world

from bigml.api import HTTP_OK

#@step(r'I get the evaluation "(.*)"')
def i_get_the_evaluation(step, evaluation):
    resource = world.api.get_evaluation(evaluation)
    world.status = resource['code']
    assert world.status == HTTP_OK
    world.evaluation = resource['object']

