import os
import time
from datetime import datetime, timedelta
from lettuce import *
from bigml.api import HTTP_CREATED
from bigml.api import FINISHED
from bigml.api import FAULTY

@step(r'I create a dataset$')
def i_create_a_dataset(step):
    resource = world.api.create_dataset(world.source['resource'])
    world.status = resource['code']
    assert world.status == HTTP_CREATED
    world.location = resource['location']
    world.dataset = resource['object']
    world.datasets.append(resource['resource'])

@step(r'I wait until the dataset status code is either (\d) or (\d) less than (\d+)')
def wait_until_dataset_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    step.given('I get the dataset "{id}"'.format(id=world.dataset['resource']))
    while (world.dataset['status']['code'] != int(code1) and
           world.dataset['status']['code'] != int(code2)):
           time.sleep(3)
           assert datetime.utcnow() - start < timedelta(seconds=int(secs))
           step.given('I get the dataset "{id}"'.format(id=world.dataset['resource']))
    assert world.dataset['status']['code'] == int(code1)

@step(r'I wait until the dataset is ready less than (\d+)')
def the_dataset_is_finished_in_less_than(step, secs):
    wait_until_dataset_status_code_is(step, FINISHED, FAULTY, secs)
