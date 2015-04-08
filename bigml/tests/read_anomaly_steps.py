import os
from world import world

from bigml.api import HTTP_OK

#@step(r'I get the anomaly detector "(.*)"')
def i_get_the_anomaly(step, anomaly):
    resource = world.api.get_anomaly(anomaly)
    world.status = resource['code']
    assert world.status == HTTP_OK
    world.anomaly = resource['object']

