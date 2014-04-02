import json
import time
from datetime import datetime, timedelta
from lettuce import step, world
from bigml.api import HTTP_CREATED
from bigml.api import FINISHED, FAULTY
from bigml.api import get_status


@step(r'I create a prediction for "(.*)"')
def i_create_a_prediction(step, data=None):
    if data is None:
        data = "{}"
    model = world.model['resource']
    data = json.loads(data)
    resource = world.api.create_prediction(model, data)
    world.status = resource['code']
    assert world.status == HTTP_CREATED
    world.location = resource['location']
    world.prediction = resource['object']
    world.predictions.append(resource['resource'])


@step(r'I create a proportional missing strategy prediction for "(.*)"')
def i_create_a_proportional_prediction(step, data=None):
    if data is None:
        data = "{}"
    model = world.model['resource']
    data = json.loads(data)
    resource = world.api.create_prediction(model, data,
                                           args={'missing_strategy': 1})
    world.status = resource['code']
    assert world.status == HTTP_CREATED
    world.location = resource['location']
    world.prediction = resource['object']
    world.predictions.append(resource['resource'])


@step(r'the prediction for "(.*)" is "(.*)"')
def the_prediction_is(step, objective, prediction):
    assert str(world.prediction['prediction'][objective]) == prediction


@step(r'the confidence for the prediction is "(.*)"')
def the_confidence_is(step, confidence):
    local_confidence = round(float(world.prediction['confidence']), 4)
    confidence = round(float(confidence), 4)
    assert local_confidence == confidence


@step(r'I create an ensemble prediction for "(.*)"')
def i_create_an_ensemble_prediction(step, data=None):
    if data is None:
        data = "{}"
    ensemble = world.ensemble['resource']
    data = json.loads(data)
    resource = world.api.create_prediction(ensemble, data)
    world.status = resource['code']
    assert world.status == HTTP_CREATED
    world.location = resource['location']
    world.prediction = resource['object']
    world.predictions.append(resource['resource'])

@step(r'I wait until the prediction status code is either (\d) or (\d) less than (\d+)')
def wait_until_prediction_status_code_is(step, code1, code2, secs):
    start = datetime.utcnow()
    step.given('I get the prediction "{id}"'.format(id=world.prediction['resource']))
    status = get_status(world.prediction)
    while (status['code'] != int(code1) and
           status['code'] != int(code2)):
        time.sleep(3)
        assert datetime.utcnow() - start < timedelta(seconds=int(secs))
        step.given('I get the prediction "{id}"'.format(id=world.prediction['resource']))
        status = get_status(world.prediction)
    assert status['code'] == int(code1)

@step(r'I wait until the prediction is ready less than (\d+)')
def the_prediction_is_finished_in_less_than(step, secs):
    wait_until_prediction_status_code_is(step, FINISHED, FAULTY, secs)

@step(r'I create a local ensemble prediction for "(.*)"$')
def create_local_ensemble_prediction(step, input_data):
    world.local_prediction = world.local_ensemble.predict(json.loads(input_data))
