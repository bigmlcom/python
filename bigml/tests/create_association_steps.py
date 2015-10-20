import time
import json
import os
from datetime import datetime, timedelta
from world import world

from bigml.api import HTTP_CREATED
from bigml.api import HTTP_ACCEPTED
from bigml.api import FINISHED
from bigml.api import FAULTY
from bigml.api import get_status

from read_association_steps import i_get_the_association


#@step(r'the association name is "(.*)"')
def i_check_association_name(step, name):
    association_name = world.association['name']
    if name == association_name:
        assert True
    else:
        assert False, ("The association name is %s "
                       "and the expected name is %s" %
                       (association_name, name))


#@step(r'I create an association from a dataset$')
def i_create_an_association_from_dataset(step):
    dataset = world.dataset.get('resource')
    resource = world.api.create_association(dataset, {'name': 'new association'})
    world.status = resource['code']
    assert world.status == HTTP_CREATED
    world.location = resource['location']
    world.association = resource['object']
    world.associations.append(resource['resource'])


#@step(r'I update the association name to "(.*)"$')
def i_update_association_name(step, name):
    resource = world.api.update_association(world.association['resource'],
                                            {'name': name})
    world.status = resource['code']
    assert world.status == HTTP_ACCEPTED
    world.location = resource['location']
    world.association = resource['object']


#@step(r'I wait until the association status code is either (\d) or (-\d) less than (\d+)')
def wait_until_association_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    association_id = world.association['resource']
    i_get_the_association(step, association_id)
    status = get_status(world.association)
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
           time.sleep(3)
           assert datetime.utcnow() - start < timedelta(seconds=int(secs))
           i_get_the_association(step, association_id)
           status = get_status(world.association)
    assert status['code'] == int(code1)


#@step(r'I wait until the association is ready less than (\d+)')
def the_association_is_finished_in_less_than(step, secs):
    wait_until_association_status_code_is(step, FINISHED, FAULTY, secs)
