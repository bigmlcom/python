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

@step(r'I check the anomaly detector stems from the original dataset list')
def i_check_anomaly_datasets_and_datasets_ids(step):
    anomaly = world.anomaly
    if 'datasets' in anomaly and anomaly['datasets'] == world.dataset_ids:
        assert True
    else:
        assert False, ("The anomaly detector contains only %s "
                       "and the dataset ids are %s" %
                       (",".join(anomaly['datasets']),
                        ",".join(world.dataset_ids)))


@step(r'I check the anomaly detector stems from the original dataset')
def i_check_anomaly_dataset_and_datasets_ids(step):
    anomaly = world.anomaly
    if 'dataset' in anomaly and anomaly['dataset'] == world.dataset['resource']:
        assert True
    else:
        assert False, ("The anomaly detector contains only %s "
                       "and the dataset id is %s" %
                       (anomaly['dataset'],
                        world.dataset['resource']))


@step(r'I create an anomaly detector$')
def i_create_an_anomaly_(step):
    i_create_an_anomaly_from_dataset(step)


@step(r'I create an anomaly detector from a dataset$')
def i_create_an_anomaly_from_dataset(step):
    dataset = world.dataset.get('resource')
    resource = world.api.create_anomaly(dataset, {'seed': 'BigML'})
    world.status = resource['code']
    assert world.status == HTTP_CREATED
    world.location = resource['location']
    world.anomaly = resource['object']
    world.anomalies.append(resource['resource'])


@step(r'I create an anomaly detector from a dataset list$')
def i_create_an_anomaly_from_dataset_list(step):
    resource = world.api.create_anomaly(world.dataset_ids, {'seed': 'BigML'})
    world.status = resource['code']
    assert world.status == HTTP_CREATED
    world.location = resource['location']
    world.anomaly = resource['object']
    world.anomalies.append(resource['resource'])

@step(r'I wait until the anomaly detector status code is either (\d) or (-\d) less than (\d+)')
def wait_until_anomaly_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    step.given('I get the anomaly detector "{id}"'.format(id=world.anomaly['resource']))
    status = get_status(world.anomaly)
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
           time.sleep(3)
           assert datetime.utcnow() - start < timedelta(seconds=int(secs))
           step.given('I get the anomaly detector "{id}"'.format(id=world.anomaly['resource']))
           status = get_status(world.anomaly)
    assert status['code'] == int(code1)

@step(r'I wait until the anomaly detector is ready less than (\d+)')
def the_anomaly_is_finished_in_less_than(step, secs):
    wait_until_anomaly_status_code_is(step, FINISHED, FAULTY, secs)
