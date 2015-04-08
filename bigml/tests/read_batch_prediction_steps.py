import os
from world import world

from bigml.api import HTTP_OK

#@step(r'I get the batch prediction "(.*)"')
def i_get_the_batch_prediction(step, batch_prediction):
    resource = world.api.get_batch_prediction(batch_prediction)
    world.status = resource['code']
    assert world.status == HTTP_OK
    world.batch_prediction = resource['object']

#@step(r'I get the batch centroid "(.*)"')
def i_get_the_batch_centroid(step, batch_centroid):
    resource = world.api.get_batch_centroid(batch_centroid)
    world.status = resource['code']
    assert world.status == HTTP_OK
    world.batch_centroid = resource['object']

#@step(r'I get the batch anomaly score "(.*)"')
def i_get_the_batch_anomaly_score(step, batch_anomaly_score):
    resource = world.api.get_batch_anomaly_score(batch_anomaly_score)
    world.status = resource['code']
    assert world.status == HTTP_OK
    world.batch_anomaly_score = resource['object']
