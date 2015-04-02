import os
from world import world

from bigml.api import HTTP_OK

#@step(r'I get the cluster "(.*)"')
def i_get_the_cluster(step, cluster):
    resource = world.api.get_cluster(cluster)
    world.status = resource['code']
    assert world.status == HTTP_OK
    world.cluster = resource['object']

#@step(r'I get the batch centroid "(.*)"')
def i_get_the_batch_centroid(step, batch_centroid):
    resource = world.api.get_batch_centroid(batch_centroid)
    world.status = resource['code']
    assert world.status == HTTP_OK
    world.batch_centroid = resource['object']

#@step(r'I get the centroid "(.*)"')
def i_get_the_centroid(step, centroid):
    resource = world.api.get_centroid(centroid)
    world.status = resource['code']
    assert world.status == HTTP_OK
    world.centroid = resource['object']
