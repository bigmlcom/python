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

from read_tst_steps import i_get_the_tst


#@step(r'the test name is "(.*)"')
def i_check_tst_name(step, name):
    test_name = world.test['name']
    if name == test_name:
        assert True
    else:
        assert False, ("The test name is %s "
                       "and the expected name is %s" %
                       (test_name, name))


#@step(r'I create a test from a dataset$')
def i_create_a_tst_from_dataset(step):
    dataset = world.dataset.get('resource')
    resource = world.api.create_test(dataset, {'name': 'new test'})
    world.status = resource['code']
    assert world.status == HTTP_CREATED
    world.location = resource['location']
    world.test = resource['object']
    world.tests.append(resource['resource'])


#@step(r'I update the test name to "(.*)"$')
def i_update_tst_name(step, name):
    resource = world.api.update_test(world.test['resource'],
                                     {'name': name})
    world.status = resource['code']
    assert world.status == HTTP_ACCEPTED
    world.location = resource['location']
    world.test = resource['object']


#@step(r'I wait until the test status code is either (\d) or (-\d) less than (\d+)')
def wait_until_tst_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    test_id = world.test['resource']
    i_get_the_tst(step, test_id)
    status = get_status(world.test)
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
           time.sleep(3)
           assert datetime.utcnow() - start < timedelta(seconds=int(secs))
           i_get_the_tst(step, test_id)
           status = get_status(world.test)
    assert status['code'] == int(code1)


#@step(r'I wait until the test is ready less than (\d+)')
def the_tst_is_finished_in_less_than(step, secs):
    wait_until_tst_status_code_is(step, FINISHED, FAULTY, secs)
