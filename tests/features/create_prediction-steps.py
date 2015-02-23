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


@step(r'I create a centroid for "(.*)"')
def i_create_a_centroid(step, data=None):
    if data is None:
        data = "{}"
    cluster = world.cluster['resource']
    data = json.loads(data)
    resource = world.api.create_centroid(cluster, data)
    world.status = resource['code']
    assert world.status == HTTP_CREATED
    world.location = resource['location']
    world.centroid = resource['object']
    world.centroids.append(resource['resource'])


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
    if str(world.prediction['prediction'][objective]) == prediction:
        assert True
    else:
        assert False, "Found: %s, expected %s" % (
            str(world.prediction['prediction'][objective]), prediction)


@step(r'the prediction using median for "(.*)" is "(.*)"')
def the_median_prediction_is(step, objective, prediction):
    median = str(world.prediction['prediction_path']
                 ['objective_summary']['median'])
    if median == prediction:
        assert True
    else:
        assert False, "Found: %s, expected %s" % (
            median, prediction)


@step(r'the centroid is "([^\"]*)" with distance "(.*)"$')
def the_centroid_is_with_distance(step, centroid, distance):
    if str(world.centroid['centroid_name']) == centroid:
        assert True
    else:
        assert False, "Found: %s, expected: %s" % (str(world.centroid['centroid_name']), centroid)
    if str(world.centroid['distance']) == distance:
        assert True
    else:
        assert False, "Found: %s, expected: %s" % (str(world.centroid['distance']), distance)

@step(r'the centroid is "([^\"]*)"$')
def the_centroid_is(step, centroid):
    if str(world.centroid['centroid_name']) == centroid:
        assert True
    else:
        assert False, "Found: %s, expected: %s" % (str(world.centroid['centroid_name']), centroid)

@step(r'I check the centroid is ok')
def the_centroid_is_ok(step):
    assert world.api.ok(world.centroid)

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

@step(r'I create a local ensemble prediction for "(.*)" in JSON adding confidence$')
def create_local_ensemble_prediction(step, input_data):
    world.local_prediction = world.local_ensemble.predict(
        json.loads(input_data), add_confidence=True)

@step(r'I create a local ensemble prediction for "(.*)"$')
def create_local_ensemble_prediction(step, input_data):
    world.local_prediction = world.local_ensemble.predict(json.loads(input_data))
    
@step(r'I create a local ensemble prediction with confidence for "(.*)"$')
def create_local_ensemble_prediction(step, input_data):
    world.local_prediction = world.local_ensemble.predict(
        json.loads(input_data), with_confidence=True)

@step(r'I create an anomaly score for "(.*)"')
def i_create_an_anomaly_score(step, data=None):
    if data is None:
        data = "{}"
    anomaly = world.anomaly['resource']
    data = json.loads(data)
    resource = world.api.create_anomaly_score(anomaly, data)
    world.status = resource['code']
    assert world.status == HTTP_CREATED
    world.location = resource['location']
    world.anomaly_score = resource['object']
    world.anomaly_scores.append(resource['resource'])

@step(r'the anomaly score is "(.*)"')
def the_anomaly_score_is(step, score):
    if str(world.anomaly_score['score']) == score:
        assert True
    else:
        assert False, "Found: %s, expected %s" % (
            str(world.anomaly_score['score']), score)
