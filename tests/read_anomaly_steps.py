import os
from world import world

from bigml.api import HTTP_OK

#@step(r'I get the anomaly detector "(.*)"')
def i_get_the_anomaly(step, anomaly):
    resource = world.api.get_anomaly(anomaly)
    world.status = resource['code']
    assert world.status == HTTP_OK
    world.anomaly = resource['object']

#@step(r'I get the batch anomaly score "(.*)"')
def i_get_the_batch_anomaly_score(step, batch_anomaly_score):
    resource = world.api.get_batch_anomaly_score(batch_anomaly_score)
    world.status = resource['code']
    assert world.status == HTTP_OK
    world.batch_anomaly_score = resource['object']

