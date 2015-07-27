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

from read_correlation_steps import i_get_the_correlation


#@step(r'the correlation name is "(.*)"')
def i_check_correlation_name(step, name):
    correlation_name = world.correlation['name']
    if name == correlation_name:
        assert True
    else:
        assert False, ("The correlation name is %s "
                       "and the expected name is %s" %
                       (correlation_name, name))


#@step(r'I create a correlation from a dataset$')
def i_create_a_correlation_from_dataset(step):
    dataset = world.dataset.get('resource')
    resource = world.api.create_correlation(dataset, {'name': 'new correlation'})
    world.status = resource['code']
    assert world.status == HTTP_CREATED
    world.location = resource['location']
    world.correlation = resource['object']
    world.correlations.append(resource['resource'])


#@step(r'I update the correlation name to "(.*)"$')
def i_update_correlation_name(step, name):
    resource = world.api.update_correlation(world.correlation['resource'],
                                            {'name': name})
    world.status = resource['code']
    assert world.status == HTTP_ACCEPTED
    world.location = resource['location']
    world.correlation = resource['object']


#@step(r'I wait until the correlation status code is either (\d) or (-\d) less than (\d+)')
def wait_until_correlation_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    correlation_id = world.correlation['resource']
    i_get_the_correlation(step, correlation_id)
    status = get_status(world.correlation)
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
           time.sleep(3)
           assert datetime.utcnow() - start < timedelta(seconds=int(secs))
           i_get_the_correlation(step, correlation_id)
           status = get_status(world.correlation)
    assert status['code'] == int(code1)


#@step(r'I wait until the correlation is ready less than (\d+)')
def the_correlation_is_finished_in_less_than(step, secs):
    wait_until_correlation_status_code_is(step, FINISHED, FAULTY, secs)
