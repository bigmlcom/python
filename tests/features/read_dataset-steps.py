from lettuce import step, world
from bigml.api import HTTP_OK

@step(r'I get the dataset "(.*)"')
def i_get_the_dataset(step, dataset):
    resource = world.api.get_dataset(dataset)
    world.status = resource['code']
    assert world.status == HTTP_OK
    world.dataset = resource['object']
