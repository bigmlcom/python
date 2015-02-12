import time
import json
import os
from datetime import datetime, timedelta
from lettuce import step, world

from bigml.api import HTTP_CREATED
from bigml.api import HTTP_ACCEPTED
from bigml.api import FINISHED
from bigml.api import FAULTY
from bigml.api import get_status


@step(r'the sample name is "(.*)"')
def i_check_sample_name(step, name):
    sample_name = world.sample['name']
    if name == sample_name:
        assert True
    else:
        assert False, ("The sample name is %s "
                       "and the expected name is %s" %
                       (sample_name, name))


@step(r'I create a sample from a dataset$')
def i_create_a_sample_from_dataset(step):
    dataset = world.dataset.get('resource')
    resource = world.api.create_sample(dataset, {'name': 'new sample'})
    world.status = resource['code']
    assert world.status == HTTP_CREATED
    world.location = resource['location']
    world.sample = resource['object']
    world.samples.append(resource['resource'])
    print "create"


@step(r'I update the sample name to "(.*)"$')
def i_update_sample_name(step, name):
    resource = world.api.update_sample(world.sample['resource'],
                                       {'name': name})
    world.status = resource['code']
    assert world.status == HTTP_ACCEPTED
    world.location = resource['location']
    world.sample = resource['object']
    print "update"


@step(r'I wait until the sample status code is either (\d) or (-\d) less than (\d+)')
def wait_until_sample_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    sample_id = world.sample['resource']
    step.given('I get the sample "{id}"'.format(id=sample_id))
    status = get_status(world.sample)
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
           time.sleep(3)
           assert datetime.utcnow() - start < timedelta(seconds=int(secs))
           step.given('I get the sample "{id}"'.format(id=sample_id))
           status = get_status(world.sample)
    assert status['code'] == int(code1)
    

@step(r'I wait until the sample is ready less than (\d+)')
def the_sample_is_finished_in_less_than(step, secs):
    wait_until_sample_status_code_is(step, FINISHED, FAULTY, secs)
