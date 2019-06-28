# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2014-2019 BigML
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Common auxiliary constants, functions and class for all resources

"""

import time
import os
import datetime

from xml.dom import minidom

import bigml.constants as c

from bigml.util import get_exponential_wait, get_status, is_status_final, \
    save, save_json
from bigml.util import DFT_STORAGE
from bigml.bigmlconnection import HTTP_OK, HTTP_ACCEPTED, HTTP_CREATED, LOGGER
from bigml.bigmlconnection import BigMLConnection


# Resource status codes
WAITING = 0
QUEUED = 1
STARTED = 2
IN_PROGRESS = 3
SUMMARIZED = 4
FINISHED = 5
UPLOADING = 6
FAULTY = -1
UNKNOWN = -2
RUNNABLE = -3


# Minimum query string to get model fields
TINY_RESOURCE = "full=false"

# Resource types that are composed by other resources
COMPOSED_RESOURCES = ["ensemble", "fusion"]

LIST_LAST = "limit=1;full=yes;tags=%s"

PMML_QS = "pmml=yes"


def get_resource_type(resource):
    """Returns the associated resource type for a resource

    """
    if isinstance(resource, dict) and 'resource' in resource:
        resource = resource['resource']
    if not isinstance(resource, basestring):
        raise ValueError("Failed to parse a resource string or structure.")
    for resource_type, resource_re in c.RESOURCE_RE.items():
        if resource_re.match(resource):
            return resource_type
    return None


def get_resource(resource_type, resource):
    """Returns a resource/id.

    """
    if isinstance(resource, dict) and 'resource' in resource:
        resource = resource['resource']
    if isinstance(resource, basestring):
        if c.RESOURCE_RE[resource_type].match(resource):
            return resource
        found_type = get_resource_type(resource)
        if found_type is not None and \
                resource_type != get_resource_type(resource):
            raise ValueError(
                "The resource %s has not the expected type:"
                " %s" % (
                    resource, resource_type))
    raise ValueError("%s is not a valid resource ID." % resource)


def resource_is_ready(resource):
    """Checks a fully fledged resource structure and returns True if finished.

    """
    if not isinstance(resource, dict) or 'error' not in resource:
        raise Exception("No valid resource structure found")
    if resource['error'] is not None:
        raise Exception(resource['error']['status']['message'])
    return (resource['code'] in [HTTP_OK, HTTP_ACCEPTED] and
            get_status(resource)['code'] == c.FINISHED)


def check_resource_type(resource, expected_resource, message=None):
    """Checks the resource type.

    """
    if isinstance(expected_resource, basestring):
        expected_resources = [expected_resource]
    else:
        expected_resources = expected_resource
    if isinstance(resource, dict) and 'id' in resource:
        resource = resource['id']
    resource_type = get_resource_type(resource)
    if resource_type not in expected_resources:
        raise Exception("%s\nFound %s." % (message, resource_type))


def get_source_id(source):
    """Returns a source/id.

    """
    return get_resource(c.SOURCE_PATH, source)


def get_dataset_id(dataset):
    """Returns a dataset/id.

    """
    return get_resource(c.DATASET_PATH, dataset)


def get_model_id(model):
    """Returns a model/id.

    """
    return get_resource(c.MODEL_PATH, model)


def get_prediction_id(prediction):
    """Returns a prediction/id.

    """
    return get_resource(c.PREDICTION_PATH, prediction)


def get_evaluation_id(evaluation):
    """Returns an evaluation/id.

    """
    return get_resource(c.EVALUATION_PATH, evaluation)


def get_ensemble_id(ensemble):
    """Returns an ensemble/id.

    """
    return get_resource(c.ENSEMBLE_PATH, ensemble)


def get_batch_prediction_id(batch_prediction):
    """Returns a batchprediction/id.

    """
    return get_resource(c.BATCH_PREDICTION_PATH, batch_prediction)


def get_cluster_id(cluster):
    """Returns a cluster/id.

    """
    return get_resource(c.CLUSTER_PATH, cluster)


def get_centroid_id(centroid):
    """Returns a centroid/id.

    """
    return get_resource(c.CENTROID_PATH, centroid)


def get_batch_centroid_id(batch_centroid):
    """Returns a batchcentroid/id.

    """
    return get_resource(c.BATCH_CENTROID_PATH, batch_centroid)


def get_anomaly_id(anomaly):
    """Returns an anomaly/id.

    """
    return get_resource(c.ANOMALY_PATH, anomaly)


def get_anomaly_score_id(anomaly_score):
    """Returns an anomalyscore/id.

    """
    return get_resource(c.ANOMALY_SCORE_PATH, anomaly_score)


def get_batch_anomaly_score_id(batch_anomaly_score):
    """Returns a batchanomalyscore/id.

    """
    return get_resource(c.BATCH_ANOMALY_SCORE_PATH, batch_anomaly_score)


def get_project_id(project):
    """Returns a project/id.

    """
    return get_resource(c.PROJECT_PATH, project)


def get_sample_id(sample):
    """Returns a sample/id.

    """
    return get_resource(c.SAMPLE_PATH, sample)


def get_correlation_id(correlation):
    """Returns a correlation/id.

    """
    return get_resource(c.CORRELATION_PATH, correlation)


def get_statistical_test_id(statistical_test):
    """Returns a statisticaltest/id.

    """
    return get_resource(c.STATISTICAL_TEST_PATH, statistical_test)


def get_logistic_regression_id(logistic_regression):
    """Returns a logisticregression/id.

    """
    return get_resource(c.LOGISTIC_REGRESSION_PATH, logistic_regression)


def get_association_id(association):
    """Returns an association/id.

    """
    return get_resource(c.ASSOCIATION_PATH, association)


def get_association_set_id(association_set):
    """Returns an associationset/id.

    """
    return get_resource(c.ASSOCIATION_SET_PATH, association_set)


def get_configuration_id(configuration):
    """Returns a configuration/id.

    """
    return get_resource(c.CONFIGURATION_PATH, configuration)


def get_topic_model_id(topic_model):
    """Returns a topicmodel/id.

    """
    return get_resource(c.TOPIC_MODEL_PATH, topic_model)


def get_topic_distribution_id(topic_distribution):
    """Returns a topicdistribution/id.

    """
    return get_resource(c.TOPIC_DISTRIBUTION_PATH, topic_distribution)


def get_batch_topic_distribution_id(batch_topic_distribution):
    """Returns a batchtopicdistribution/id.

    """
    return get_resource(c.BATCH_TOPIC_DISTRIBUTION_PATH,
                        batch_topic_distribution)


def get_time_series_id(time_series):
    """Returns a timeseries/id.

    """
    return get_resource(c.TIME_SERIES_PATH, time_series)


def get_forecast_id(forecast):
    """Returns a forecast/id.

    """
    return get_resource(c.FORECAST_PATH, forecast)


def get_fusion_id(fusion):
    """Returns an fusion/id.

    """
    return get_resource(c.FUSION_PATH, fusion)


def get_optiml_id(optiml):
    """Returns an optiml/id.

    """
    return get_resource(c.OPTIML_PATH, optiml)


def get_deepnet_id(deepnet):
    """Returns a deepnet/id.

    """
    return get_resource(c.DEEPNET_PATH, deepnet)


def get_pca_id(pca):
    """Returns a PCA/id.

    """
    return get_resource(c.PCA_PATH, pca)


def get_projection_id(projection):
    """Returns a projection/id.

    """
    return get_resource(c.PROJECTION_PATH, projection)


def get_batch_projection_id(batch_projection):
    """Returns a batchprojection/id.

    """
    return get_resource(c.BATCH_PROJECTION_PATH, batch_projection)


def get_linear_regression_id(linear_regression):
    """Returns a linearregression/id.

    """
    return get_resource(c.LINEAR_REGRESSION_PATH, linear_regression)


def get_script_id(script):
    """Returns a script/id.

    """
    return get_resource(c.SCRIPT_PATH, script)


def get_execution_id(execution):
    """Returns a execution/id.

    """
    return get_resource(c.EXECUTION_PATH, execution)


def get_library_id(library):
    """Returns a library/id.

    """
    return get_resource(c.LIBRARY_PATH, library)


def get_resource_id(resource):
    """Returns the resource id if it falls in one of the registered types

    """
    if isinstance(resource, dict) and 'resource' in resource:
        return resource['resource']
    elif isinstance(resource, basestring) and any(
            resource_re.match(resource) for _, resource_re
            in c.RESOURCE_RE.items()):
        return resource
    else:
        return


def exception_on_error(resource):
    """Raises exception if resource has error

    """
    if resource['error'] is not None:
        raise Exception(resource['error']['status']['message'])


def check_resource(resource, get_method=None, query_string='', wait_time=1,
                   retries=None, raise_on_error=False, api=None):
    """Waits until a resource is finished.

       Given a resource and its corresponding get_method (if absent, the
       generic get_resource is used), it calls the get_method on
       the resource with the given query_string
       and waits with sleeping intervals of wait_time
       until the resource is in a final state (either FINISHED
       or FAULTY. The number of retries can be limited using the retries
       parameter.

    """

    if isinstance(resource, basestring):
        resource_id = resource
    else:
        resource_id = get_resource_id(resource)
    resource_id = get_resource_id(resource)
    if resource_id is None:
        raise ValueError("Failed to extract a valid resource id to check.")
    kwargs = {'query_string': query_string}

    if get_method is None and hasattr(api, 'get_resource'):
        get_method = api.get_resource
    elif get_method is None:
        raise ValueError("You must supply either the get_method or the api"
                         " connection info to retrieve the resource")
    if isinstance(resource, basestring):
        resource = get_method(resource, **kwargs)
    counter = 0
    while retries is None or counter < retries:
        counter += 1
        status = get_status(resource)
        code = status['code']
        if code == c.FINISHED:
            if counter > 1:
                # final get call to retrieve complete resource
                resource = get_method(resource, **kwargs)
            if raise_on_error:
                exception_on_error(resource)
            return resource
        elif code == c.FAULTY:
            raise ValueError(status)
        time.sleep(get_exponential_wait(wait_time, counter))
        # retries for the finished status use a query string that gets the
        # minimal available resource
        if kwargs.get('query_string') is not None:
            tiny_kwargs = {'query_string': c.TINY_RESOURCE}
        else:
            tiny_kwargs = {}
        resource = get_method(resource, **tiny_kwargs)
    if raise_on_error:
        exception_on_error(resource)
    return resource


def http_ok(resource):
    """Checking the validity of the http return code

    """
    if 'code' in resource:
        return resource['code'] in [HTTP_OK, HTTP_CREATED, HTTP_ACCEPTED]



class ResourceHandler(BigMLConnection):
    """This class is used by the BigML class as
       a mixin that provides the get method for all kind of
       resources and auxiliar utilities to check their status. It should not
       be instantiated independently.

    """

    def __init__(self):
        """Initializes the ResourceHandler. This class is intended to be
           used purely as a mixin on BigMLConnection and must not be
           instantiated independently.

        """
        pass

    def get_resource(self, resource, **kwargs):
        """Retrieves a remote resource.

           The resource parameter should be a string containing the
           resource id or the dict returned by the corresponding create method.
           As each resource is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, thet function will
           return a dict that encloses the resource values and state info
           available at the time it is called.

        """
        resource_type = get_resource_type(resource)
        if resource_type is None:
            raise ValueError("A resource id or structure is needed.")
        resource_id = get_resource_id(resource)

        if resource_id:
            return self._get("%s%s" % (self.url, resource_id),
                             **kwargs)

    def ok(self, resource, query_string='', wait_time=1,
           retries=None, raise_on_error=False):
        """Waits until the resource is finished or faulty, updates it and
           returns True on success

        """
        if http_ok(resource):
            resource.update(check_resource(resource,
                                           query_string=query_string,
                                           wait_time=wait_time,
                                           retries=retries,
                                           raise_on_error=raise_on_error,
                                           api=self))
            return True
        else:
            LOGGER.error("The resource couldn't be created: %s",
                         resource['error'])

    def _set_create_from_datasets_args(self, datasets, args=None,
                                       wait_time=3, retries=10, key=None):
        """Builds args dictionary for the create call from a `dataset` or a
           list of `datasets`.

        """
        dataset_ids = []
        single = False

        create_args = {}
        if args is not None:
            create_args.update(args)

        if isinstance(datasets, basestring) and datasets.startswith('shared/'):
            origin = datasets.replace('shared/', "")
            if get_resource_type(origin) != "dataset":
                create_args.update({"shared_hash": origin.split("/")[1]})
                return create_args

        if not isinstance(datasets, list):
            single = True
            origin_datasets = [datasets]
        else:
            origin_datasets = datasets

        for dataset in origin_datasets:
            check_resource_type(dataset, c.DATASET_PATH,
                                message=("A dataset id is needed to create"
                                         " the resource."))
            if isinstance(dataset, dict) and 'id' in dataset:
                dataset['id'] = dataset['id'].replace("shared/", "")
                dataset_ids.append(dataset)
                dataset_id = dataset['id']
            else:
                dataset_id = get_dataset_id(dataset).replace( \
                    "shared/", "")
                dataset_ids.append(dataset_id)
            dataset = check_resource(dataset_id,
                                     query_string=c.TINY_RESOURCE,
                                     wait_time=wait_time, retries=retries,
                                     raise_on_error=True, api=self)
        if single:
            if key is None:
                key = "dataset"
            create_args.update({key: dataset_ids[0]})
        else:
            if key is None:
                key = "datasets"
            create_args.update({key: dataset_ids})

        return create_args

    def _set_create_from_models_args(self, models, types, args=None,
                                     wait_time=3, retries=10, key=None):
        """Builds args dictionary for the create call from a list of
        models. The first argument needs to be a list of:
            - the model IDs
            - dict objects with the "id" attribute set to the ID of the model
              and the "weight" attribute set to the weight associated to that
              model.

        """
        model_ids = []
        if not isinstance(models, list):
            origin_models = [models]
        else:
            origin_models = models

        for model in origin_models:
            if isinstance(model, dict) and model.get("id"):
                model = model.get("id")
            check_resource_type(model, types,
                                message=("A list of model ids "
                                         "is needed to create"
                                         " the resource."))
            model_ids.append(get_resource_id(model).replace("shared/", ""))
            model = check_resource(model,
                                   query_string=c.TINY_RESOURCE,
                                   wait_time=wait_time, retries=retries,
                                   raise_on_error=True, api=self)

        if not isinstance(origin_models[0], dict) \
                or not origin_models[0].get("id"):
            origin_models = model_ids

        create_args = {}
        if args is not None:
            create_args.update(args)

        create_args.update({"models": origin_models})

        return create_args

    def check_origins(self, dataset, model, args, model_types=None,
                      wait_time=3, retries=10):
        """Returns True if the dataset and model needed to build
           the batch prediction or evaluation are finished. The args given
           by the user are modified to include the related ids in the
           create call.

           If model_types is a list, then we check any of the model types in
           the list.

        """

        def args_update(resource_id):
            """Updates args when the resource is ready

            """
            if resource_id:
                check_resource(resource_id,
                               query_string=c.TINY_RESOURCE,
                               wait_time=wait_time, retries=retries,
                               raise_on_error=True, api=self)
                args.update({
                    resource_type: resource_id,
                    "dataset": dataset_id})

        if model_types is None:
            model_types = []

        resource_type = get_resource_type(dataset)
        if c.DATASET_PATH != resource_type:
            raise Exception("A dataset id is needed as second argument"
                            " to create the resource. %s found." %
                            resource_type)
        dataset_id = get_dataset_id(dataset)
        if dataset_id:
            dataset = check_resource(dataset_id,
                                     query_string=c.TINY_RESOURCE,
                                     wait_time=wait_time, retries=retries,
                                     raise_on_error=True, api=self)
            resource_type = get_resource_type(model)
            if resource_type in model_types:
                resource_id = get_resource_id(model)
                args_update(resource_id)
            elif resource_type == c.MODEL_PATH:
                resource_id = get_model_id(model)
                args_update(resource_id)
            else:
                raise Exception("A model or ensemble id is needed as first"
                                " argument to create the resource."
                                " %s found." % resource_type)

        return dataset_id and resource_id

    def export(self, resource, filename=None, pmml=False,
               **kwargs):
        """Retrieves a remote resource when finished and stores it
           in the user-given file

           The resource parameter should be a string containing the
           resource id or the dict returned by the corresponding create method.
           As each resource is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, the function will
           wait until the resource is in one of these states to store the
           associated info.

        """
        resource_type = get_resource_type(resource)
        if resource_type is None:
            raise ValueError("A resource ID or structure is needed.")

        if pmml:
            if resource_type not in c.PMML_MODELS:
                raise ValueError("Failed to export to PMML. Only some models"
                                 " can be exported to PMML.")

        resource_id = get_resource_id(resource)

        if resource_id:
            if pmml:
                # only models with no text fields can be exported
                resource_info = self._get("%s%s" % (self.url, resource_id),
                                          query_string=c.TINY_RESOURCE)
                field_types = resource_info["object"].get( \
                    "dataset_field_types", {})
                if field_types.get("items", 0) > 0 or \
                        field_types.get("text", 0) > 0:
                    raise ValueError("Failed to export to PMML. Models with "
                                     "text and items fields cannot be "
                                     "exported to PMML.")
                if kwargs.get("query_string"):
                    kwargs["query_string"] += ";%s" % PMML_QS
                else:
                    kwargs["query_string"] = PMML_QS

            if kwargs.get("query_string") and \
                    "output_format" in kwargs.get("query_string"):
                resource_info = self._get("%s%s" % (self.url,
                                                    resource_id))
            else:
                resource_info = self._get("%s%s" % (self.url, resource_id),
                                          **kwargs)
            if not is_status_final(resource_info):
                self.ok(resource_info)
            if filename is None:
                file_dir = self.storage or DFT_STORAGE
                filename = os.path.join( \
                    file_dir, resource_id.replace("/", "_"))
            if resource_type in COMPOSED_RESOURCES:
                for component_id in resource_info["object"]["models"]:
                    # for weighted fusions we need to retrieve the component
                    # ID
                    if isinstance(component_id, dict):
                        component_id = component_id['id']
                    self.export( \
                        component_id,
                        filename=os.path.join(os.path.dirname(filename),
                                              component_id.replace("/", "_")),
                        pmml=pmml,
                        **kwargs)
            if kwargs.get("query_string") and \
                    "output_format" in kwargs.get("query_string"):
                return self._download("%s%s?%s" % \
                    (self.url, resource_id, kwargs["query_string"]), filename)

            if pmml and resource_info.get("object", {}).get("pmml"):
                resource_info = resource_info.get("object", {}).get("pmml")
                resource_info = minidom.parseString( \
                    resource_info).toprettyxml()
                return save(resource_info, filename)
            return save_json(resource_info, filename)
        else:
            raise ValueError("First agument is expected to be a valid"
                             " resource ID or structure.")

    def export_last(self, tags, filename=None,
                    resource_type="model", project=None,
                    **kwargs):
        """Retrieves a remote resource by tag when finished and stores it
           in the user-given file

           The resource parameter should be a string containing the
           resource id or the dict returned by the corresponding create method.
           As each resource is an evolving object that is processed
           until it reaches the FINISHED or FAULTY state, the function will
           wait until the resource is in one of these states to store the
           associated info.

        """

        if tags is not None and tags != '':
            query_string = LIST_LAST % tags
            if project is not None:
                query_string += ";project=%s" % project

            kwargs.update({'query_string': "%s;%s" % \
                (query_string, kwargs.get('query_string', ''))})

            response = self._list("%s%s" % (self.url, resource_type),
                                  **kwargs)
            if len(response.get("objects", [])) > 0:
                resource_info = response["objects"][0]
                if not is_status_final(resource_info):
                    self.ok(resource_info)
                if filename is None:
                    file_dir = self.storage or DFT_STORAGE
                    now = datetime.datetime.now().strftime("%a%b%d%y_%H%M%S")
                    filename = os.path.join( \
                        file_dir,
                        "%s_%s.json" % (tags.replace("/", "_"), now))
                if resource_type in COMPOSED_RESOURCES:
                    for component_id in resource_info["models"]:
                        self.export( \
                            component_id,
                            filename=os.path.join( \
                                os.path.dirname(filename),
                                component_id.replace("/", "_")))
                return save_json(resource_info, filename)
            else:
                raise ValueError("No %s found with tags %s." % (resource_type,
                                                                tags))
        else:
            raise ValueError("First agument is expected to be a non-empty"
                             " tag.")
