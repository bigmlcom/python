# terrain.py
import os
import shutil

from lettuce import before, after, world

from bigml.api import BigML
from bigml.api import HTTP_OK

@before.each_feature
def setup_resources(feature):
    world.USERNAME = os.environ['BIGML_USERNAME']
    world.API_KEY = os.environ['BIGML_API_KEY']
    assert world.USERNAME is not None
    assert world.API_KEY is not None
    world.api = BigML(world.USERNAME, world.API_KEY)
    world.api_dev_mode = BigML(world.USERNAME, world.API_KEY, dev_mode=True)

    sources = world.api.list_sources()
    assert sources['code'] == HTTP_OK
    world.init_sources_count = sources['meta']['total_count']

    datasets = world.api.list_datasets()
    assert datasets['code'] == HTTP_OK
    world.init_datasets_count = datasets['meta']['total_count']

    models = world.api.list_models()
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

    world.sources = []
    world.datasets = []
    world.models = []
    world.predictions = []
    world.evaluations = []
    world.ensembles = []

@after.each_feature
def cleanup_resources(feature):
    
    if os.path.exists('./tmp'):
        shutil.rmtree('./tmp')

    for id in world.sources:
        world.api.delete_source(id)
    world.sources = []

    for id in world.datasets:
        world.api.delete_dataset(id)
    world.datasets = []

    for id in world.models:
        world.api.delete_model(id)
    world.models = []

    for id in world.predictions:
        world.api.delete_prediction(id)
    world.predictions = []

    for id in world.evaluations:
        world.api.delete_evaluation(id)
    world.evaluations = []

    for id in world.ensembles:
        world.api.delete_ensemble(id)
    world.ensembles = []

    sources = world.api.list_sources()
    assert sources['code'] == HTTP_OK
    world.final_sources_count = sources['meta']['total_count']

    datasets = world.api.list_datasets()
    assert datasets['code'] == HTTP_OK
    world.final_datasets_count = datasets['meta']['total_count']

    models = world.api.list_models()
    assert models['code'] == HTTP_OK
    world.final_models_count = models['meta']['total_count']

    predictions = world.api.list_predictions()
    assert predictions['code'] == HTTP_OK
    world.final_predictions_count = predictions['meta']['total_count']

    evaluations = world.api.list_evaluations()
    assert evaluations['code'] == HTTP_OK
    world.final_evaluations_count = evaluations['meta']['total_count']

    ensembles = world.api.list_ensembles()
    assert ensembles['code'] == HTTP_OK
    world.final_ensembles_count = ensembles['meta']['total_count']

    assert world.final_sources_count == world.init_sources_count
    assert world.final_datasets_count == world.init_datasets_count
    assert world.final_models_count == world.init_models_count
    assert world.final_predictions_count == world.init_predictions_count
    assert world.final_evaluations_count == world.init_evaluations_count
    assert world.final_ensembles_count == world.init_ensembles_count
