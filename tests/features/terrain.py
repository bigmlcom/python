# terrain.py
import os
import shutil

from lettuce import before, after, world

from bigml.api import BigML
from bigml.api import HTTP_OK, HTTP_NO_CONTENT

MAX_RETRIES = 10


def delete(object_list, delete_method):
    """Deletes the objects in object_list using the api delete method

    """

    for obj_id in object_list:
        counter = 0
        result = delete_method(obj_id)
        while result['code'] != HTTP_NO_CONTENT and counter < MAX_RETRIES:
            print "Delete failed for %s. Retrying" % obj_id
            time.sleep(3)
            counter += 1
            result = delete_method(obj_id)
        if counter == MAX_RETRIES:
            print ("Retries to delete the created resources are exhausted."
                   " Failed to delete.")

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

    world.sources = []
    world.datasets = []
    world.models = []
    world.predictions = []
    world.evaluations = []
    world.ensembles = []
    world.batch_predictions = []
    world.clusters = []
    world.centroids = []
    world.batch_centroids = []

    world.dataset_ids = []
    world.fields_properties_dict = {}
@after.each_feature
def cleanup_resources(feature):

    if os.path.exists('./tmp'):
        shutil.rmtree('./tmp')

    delete(world.clusters, world.api.delete_cluster)
    world.clusters = []

    delete(world.sources, world.api.delete_source)
    world.sources = []

    delete(world.datasets, world.api.delete_dataset)
    world.datasets = []

    delete(world.models, world.api.delete_model)
    world.models = []

    delete(world.predictions, world.api.delete_prediction)
    world.predictions = []

    delete(world.evaluations, world.api.delete_evaluation)
    world.evaluations = []

    delete(world.ensembles, world.api.delete_ensemble)
    world.ensembles = []

    delete(world.batch_predictions, world.api.delete_batch_prediction)
    world.batch_predictions = []

    delete(world.centroids, world.api.delete_centroid)
    world.centroids = []

    delete(world.batch_centroids, world.api.delete_batch_centroid)
    world.batch_centroids = []

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

    clusters = world.api.list_clusters()
    assert clusters['code'] == HTTP_OK
    world.final_clusters_count = clusters['meta']['total_count']

    batch_predictions = world.api.list_batch_predictions()
    assert batch_predictions['code'] == HTTP_OK
    world.final_batch_predictions_count = batch_predictions['meta']['total_count']

    centroids = world.api.list_centroids()
    assert centroids['code'] == HTTP_OK
    world.final_centroids_count = centroids['meta']['total_count']

    batch_centroids = world.api.list_batch_centroids()
    assert batch_centroids['code'] == HTTP_OK
    world.final_batch_centroids_count = batch_centroids['meta']['total_count']


    assert world.final_sources_count == world.init_sources_count
    assert world.final_datasets_count == world.init_datasets_count
    assert world.final_models_count == world.init_models_count
    assert world.final_predictions_count == world.init_predictions_count
    assert world.final_evaluations_count == world.init_evaluations_count
    assert world.final_ensembles_count == world.init_ensembles_count
    assert world.final_batch_predictions_count == world.init_batch_predictions_count
    assert world.final_clusters_count == world.init_clusters_count
    assert world.final_centroids_count == world.init_centroids_count
    assert world.final_batch_centroids_count == world.init_batch_centroids_count

@after.each_scenario
def cleanup_resources(scenario):
    world.dataset_ids = []
