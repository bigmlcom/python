import os
from lettuce import step, world

from bigml.api import HTTP_OK

@step(r'I get the ensemble "(.*)"')
def i_get_the_ensemble(step, ensemble):
    resource = world.api.get_ensemble(ensemble)
    world.status = resource['code']
    assert world.status == HTTP_OK
    world.ensemble = resource['object']

