from lettuce import *

from bigml.api import HTTP_OK
from bigml.api import HTTP_CREATED
from bigml.api import HTTP_ACCEPTED
from bigml.api import HTTP_BAD_REQUEST
from bigml.api import HTTP_UNAUTHORIZED
from bigml.api import HTTP_NOT_FOUND

@step(r'I get an OK response')
def i_get_an_OK_response(step):
    assert world.status == HTTP_OK

@step(r'I get a created response')
def i_get_a_created_response(step):
    assert world.status == HTTP_CREATED

@step(r'I get an accepted response')
def i_get_an_accepted_response(step):
    assert world.status == HTTP_ACCEPTED

@step(r'I get a bad request response')
def i_get_a_bad_request_response(step):
    assert world.status == HTTP_BAD_REQUEST

@step(r'I get a unauthorized response')
def i_get_a_unauthorized_response(step):
    assert world.status == HTTP_UNAUTHORIZED

@step(r'I get a not found response')
def i_get_a_not_found_response(step):
    assert world.status == HTTP_NOT_FOUND

@step(r'I want to use api in DEV mode')
def i_want_api_dev_mode(step):
    world.api = world.api_dev_mode
    # Update counters of resources for DEV mode
    sources = world.api.list_sources()
    assert sources['code'] == HTTP_OK
    world.init_sources_count = sources['meta']['total_count']

    datasets = world.api.list_datasets()
    assert datasets['code'] == HTTP_OK
    world.init_datasets_count = datasets['meta']['total_count']

    models = world.api.list_models("ensemble=false")
    assert models['code'] == HTTP_OK
    world.init_models_count = models['meta']['total_count']

    predictions = world.api.list_predictions()
    assert predictions['code'] == HTTP_OK
    world.init_predictions_count = predictions['meta']['total_count']

    evaluations = world.api.list_evaluations()
    assert evaluations['code'] == HTTP_OK
    world.init_evaluations_count = evaluations['meta']['total_count']

    ensembles = world.api.list_ensembles()
    assert ensembles['code'] == HTTP_OK
    world.init_ensembles_count = ensembles['meta']['total_count']

    batch_predictions = world.api.list_batch_predictions()
    assert batch_predictions['code'] == HTTP_OK
    world.init_batch_predictions_count = batch_predictions['meta']['total_count']

    clusters = world.api.list_clusters()
    assert clusters['code'] == HTTP_OK
    world.init_clusters_count = clusters['meta']['total_count']

    centroids = world.api.list_centroids()
    assert centroids['code'] == HTTP_OK
    world.init_centroids_count = centroids['meta']['total_count']

    batch_centroids = world.api.list_batch_centroids()
    assert batch_centroids['code'] == HTTP_OK
    world.init_batch_centroids_count = batch_centroids['meta']['total_count']

    anomalies = world.api.list_anomalies()
    assert anomalies['code'] == HTTP_OK
    world.init_anomalies_count = anomalies['meta']['total_count']

    anomaly_scores = world.api.list_anomaly_scores()
    assert anomaly_scores['code'] == HTTP_OK
    world.init_anomaly_scores_count = anomaly_scores['meta']['total_count']

    batch_anomaly_scores = world.api.list_batch_anomaly_scores()
    assert batch_anomaly_scores['code'] == HTTP_OK
    world.init_batch_anomaly_scores_count = batch_anomaly_scores['meta']['total_count']
