import os
import time
from datetime import datetime, timedelta
from lettuce import *
from bigml.api import HTTP_CREATED
from bigml.api import HTTP_ACCEPTED
from bigml.api import FINISHED
from bigml.api import FAULTY
from bigml.api import get_status

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
    status = get_status(world.dataset)
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
        time.sleep(3)
        assert datetime.utcnow() - start < timedelta(seconds=int(secs))
        step.given('I get the dataset "{id}"'.format(id=world.dataset['resource']))
        status = get_status(world.dataset)
    assert status['code'] == int(code1)

@step(r'I wait until the dataset is ready less than (\d+)')
def the_dataset_is_finished_in_less_than(step, secs):
    wait_until_dataset_status_code_is(step, FINISHED, FAULTY, secs)

@step(r'I make the dataset public')
def make_the_dataset_public(step):
    resource = world.api.update_dataset(world.dataset['resource'],
                                        {'private': False})
    world.status = resource['code']
    assert world.status == HTTP_ACCEPTED
    world.location = resource['location']
    world.dataset = resource['object']

@step(r'I get the dataset status using the dataset\'s public url')
def build_local_dataset_from_public_url(step):
    world.dataset = world.api.get_dataset("public/%s" % world.dataset['resource'])

@step(r'the dataset\'s status is FINISHED')
def dataset_status_finished(step):
    assert get_status(world.dataset)['code'] == FINISHED

@step(r'I create a dataset extracting a (.*) sample$')
def i_create_a_split_dataset(step, rate):
    world.origin_dataset = world.dataset
    resource = world.api.create_dataset(world.dataset['resource'], {'sample_rate': float(rate)})
    world.status = resource['code']
    assert world.status == HTTP_CREATED
    world.location = resource['location']
    world.dataset = resource['object']
    world.datasets.append(resource['resource'])

@step(r'I compare the datasets\' instances$')
def i_compare_datasets_instances(step):
    world.datasets_instances = (world.dataset['rows'], world.origin_dataset['rows'])

@step(r'the proportion of instances between datasets is (.*)$')
def proportion_datasets_instances(step, rate):
    assert int(world.datasets_instances[1] * float(rate)) == world.datasets_instances[0]
