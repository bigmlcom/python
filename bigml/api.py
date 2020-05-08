# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2012-2020 BigML
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

"""BigML.io Python bindings.

This is a simple binding to BigML.io, the BigML API.

Example usage (assuming that you have previously set up the BIGML_USERNAME and
BIGML_API_KEY environment variables):

from bigml.api import BigML

api = BigML()
source = api.create_source('./data/iris.csv')
dataset = api.create_dataset(source)
model = api.create_model(dataset)
prediction = api.create_prediction(model, {'sepal width': 1})
api.pprint(prediction)

"""
import sys
import pprint
import os
import json


from bigml.bigmlconnection import BigMLConnection
from bigml.domain import BIGML_PROTOCOL
from bigml.resourcehandler import ResourceHandler, check_resource
from bigml.sourcehandler import SourceHandler
from bigml.datasethandler import DatasetHandler
from bigml.modelhandler import ModelHandler
from bigml.ensemblehandler import EnsembleHandler
from bigml.predictionhandler import PredictionHandler
from bigml.clusterhandler import ClusterHandler
from bigml.centroidhandler import CentroidHandler
from bigml.anomalyhandler import AnomalyHandler
from bigml.anomalyscorehandler import AnomalyScoreHandler
from bigml.evaluationhandler import EvaluationHandler
from bigml.batchpredictionhandler import BatchPredictionHandler
from bigml.batchcentroidhandler import BatchCentroidHandler
from bigml.batchanomalyscorehandler import BatchAnomalyScoreHandler
from bigml.projecthandler import ProjectHandler
from bigml.samplehandler import SampleHandler
from bigml.correlationhandler import CorrelationHandler
from bigml.statisticaltesthandler import StatisticalTestHandler
from bigml.logistichandler import LogisticRegressionHandler
from bigml.associationhandler import AssociationHandler
from bigml.associationsethandler import AssociationSetHandler
from bigml.configurationhandler import ConfigurationHandler
from bigml.topicmodelhandler import TopicModelHandler
from bigml.topicdistributionhandler import TopicDistributionHandler
from bigml.batchtopicdistributionhandler import BatchTopicDistributionHandler
from bigml.timeserieshandler import TimeSeriesHandler
from bigml.forecasthandler import ForecastHandler
from bigml.deepnethandler import DeepnetHandler
from bigml.optimlhandler import OptimlHandler
from bigml.fusionhandler import FusionHandler
from bigml.pcahandler import PCAHandler
from bigml.projectionhandler import ProjectionHandler
from bigml.linearhandler import LinearRegressionHandler
from bigml.batchprojectionhandler import BatchProjectionHandler
from bigml.scripthandler import ScriptHandler
from bigml.executionhandler import ExecutionHandler
from bigml.libraryhandler import LibraryHandler
from bigml.constants import STORAGE, ALL_FIELDS
from bigml.externalconnectorhandler import ExternalConnectorHandler


# Repeating constants and functions for backwards compatibility

# HTTP Status Codes from https://bigml.com/developers/status_codes
from bigml.bigmlconnection import (
    HTTP_OK, HTTP_CREATED, HTTP_ACCEPTED, HTTP_NO_CONTENT, HTTP_BAD_REQUEST,
    HTTP_UNAUTHORIZED, HTTP_PAYMENT_REQUIRED, HTTP_FORBIDDEN,
    HTTP_NOT_FOUND, HTTP_METHOD_NOT_ALLOWED, HTTP_TOO_MANY_REQUESTS,
    HTTP_LENGTH_REQUIRED, HTTP_INTERNAL_SERVER_ERROR, DOWNLOAD_DIR, LOGGER)


# Resource types and status codes
from bigml.constants import (
    WAITING, QUEUED, STARTED, IN_PROGRESS, SUMMARIZED, FINISHED, UPLOADING,
    FAULTY, UNKNOWN, RUNNABLE, RESOURCE_RE, RENAMED_RESOURCES, SOURCE_RE,
    DATASET_RE, MODEL_RE, ENSEMBLE_RE, CLUSTER_RE, CENTROID_RE, ANOMALY_RE,
    PREDICTION_RE, EVALUATION_RE, BATCH_PREDICTION_RE, BATCH_CENTROID_RE,
    BATCH_ANOMALY_SCORE_RE, ANOMALY_SCORE_RE, PROJECT_RE, SOURCE_PATH,
    DATASET_PATH, MODEL_PATH, PREDICTION_PATH, EVALUATION_PATH, ENSEMBLE_PATH,
    BATCH_PREDICTION_PATH, CLUSTER_PATH, CENTROID_PATH, BATCH_CENTROID_PATH,
    ANOMALY_PATH, ANOMALY_SCORE_PATH, BATCH_ANOMALY_SCORE_PATH, PROJECT_PATH,
    SAMPLE_PATH, SAMPLE_RE, CORRELATION_PATH, CORRELATION_RE,
    STATISTICAL_TEST_PATH, STATISTICAL_TEST_RE,
    LOGISTIC_REGRESSION_PATH, LOGISTIC_REGRESSION_RE, ASSOCIATION_PATH,
    ASSOCIATION_RE, ASSOCIATION_SET_PATH, ASSOCIATION_SET_RE, TOPIC_MODEL_PATH,
    TOPIC_MODEL_RE, TOPIC_DISTRIBUTION_PATH, BATCH_TOPIC_DISTRIBUTION_PATH,
    TOPIC_DISTRIBUTION_RE, BATCH_TOPIC_DISTRIBUTION_RE, TIME_SERIES_RE,
    TIME_SERIES_PATH, FORECAST_RE, DEEPNET_PATH, DEEPNET_RE, OPTIML_PATH,
    OPTIML_RE, FUSION_PATH, FUSION_RE, CONFIGURATION_PATH, CONFIGURATION_RE,
    FORECAST_PATH, PCA_PATH, PCA_RE, PROJECTION_PATH, PROJECTION_RE,
    BATCH_PROJECTION_PATH, BATCH_PROJECTION_RE,
    LINEAR_REGRESSION_PATH, LINEAR_REGRESSION_RE, SCRIPT_PATH, SCRIPT_RE,
    EXECUTION_PATH, EXECUTION_RE, LIBRARY_PATH, LIBRARY_RE, STATUS_PATH,
    IRREGULAR_PLURALS, RESOURCES_WITH_FIELDS, FIELDS_PARENT,
    EXTERNAL_CONNECTOR_PATH, EXTERNAL_CONNECTOR_RE)

from bigml.resourcehandler import (
    get_resource, get_resource_type, check_resource_type, get_source_id,
    get_dataset_id, get_model_id, get_ensemble_id, get_evaluation_id,
    get_cluster_id, get_centroid_id, get_anomaly_id, get_anomaly_score_id,
    get_prediction_id, get_batch_prediction_id, get_batch_centroid_id,
    get_batch_anomaly_score_id, get_resource_id, resource_is_ready,
    get_status, check_resource, http_ok, get_project_id, get_sample_id,
    get_correlation_id, get_statistical_test_id, get_logistic_regression_id,
    get_association_id, get_association_set_id, get_topic_model_id,
    get_topic_distribution_id, get_batch_topic_distribution_id,
    get_time_series_id, get_forecast_id, get_deepnet_id, get_optiml_id,
    get_fusion_id, get_pca_id, get_projection_id, get_batch_projection_id,
    get_configuration_id, get_linear_regression_id,
    get_script_id, get_execution_id, get_library_id, get_external_connector_id)


# Map status codes to labels
STATUSES = {
    WAITING: "WAITING",
    QUEUED: "QUEUED",
    STARTED: "STARTED",
    IN_PROGRESS: "IN_PROGRESS",
    SUMMARIZED: "SUMMARIZED",
    FINISHED: "FINISHED",
    UPLOADING: "UPLOADING",
    FAULTY: "FAULTY",
    UNKNOWN: "UNKNOWN",
    RUNNABLE: "RUNNABLE"
}

ID_GETTERS = {
    PROJECT_PATH: get_project_id,
    SOURCE_PATH: get_source_id,
    DATASET_PATH: get_dataset_id,
    MODEL_PATH: get_model_id,
    ENSEMBLE_PATH: get_ensemble_id,
    LOGISTIC_REGRESSION_PATH: get_logistic_regression_id,
    DEEPNET_PATH: get_deepnet_id,
    EVALUATION_PATH: get_evaluation_id,
    CLUSTER_PATH: get_cluster_id,
    ANOMALY_PATH: get_anomaly_id,
    TOPIC_MODEL_PATH: get_topic_model_id,
    ASSOCIATION_PATH: get_association_id,
    TIME_SERIES_PATH: get_time_series_id,
    OPTIML_PATH: get_optiml_id,
    FUSION_PATH: get_fusion_id,
    PREDICTION_PATH: get_prediction_id,
    CENTROID_PATH: get_centroid_id,
    ANOMALY_SCORE_PATH: get_anomaly_score_id,
    TOPIC_DISTRIBUTION_PATH: get_topic_distribution_id,
    ASSOCIATION_SET_PATH: get_association_set_id,
    BATCH_PREDICTION_PATH: get_batch_prediction_id,
    BATCH_CENTROID_PATH: get_batch_centroid_id,
    BATCH_ANOMALY_SCORE_PATH: get_batch_anomaly_score_id,
    BATCH_TOPIC_DISTRIBUTION_PATH: get_batch_topic_distribution_id,
    FORECAST_PATH: get_forecast_id,
    CORRELATION_PATH: get_correlation_id,
    STATISTICAL_TEST_PATH: get_statistical_test_id,
    SAMPLE_PATH: get_sample_id,
    CONFIGURATION_PATH: get_configuration_id,
    PCA_PATH: get_pca_id,
    PROJECTION_PATH: get_projection_id,
    BATCH_PROJECTION_PATH: get_batch_projection_id,
    LINEAR_REGRESSION_PATH: get_linear_regression_id,
    SCRIPT_PATH: get_script_id,
    LIBRARY_PATH: get_library_id,
    EXECUTION_PATH: get_execution_id,
    EXTERNAL_CONNECTOR_PATH: get_external_connector_id
}


def count(listing):
    """Count of existing resources

    """
    if 'meta' in listing and 'query_total' in listing['meta']:
        return listing['meta']['query_total']



def get_fields(resource):
    """Returns the field information in a resource dictionary structure

    """
    try:
        resource_type = get_resource_type(resource)
    except ValueError:
        raise ValueError("Unknown resource structure. Failed to find"
                         " a valid resource dictionary as argument.")

    if resource_type in RESOURCES_WITH_FIELDS:
        resource = resource.get('object', resource)
        # fields structure
        if resource_type in FIELDS_PARENT.keys():
            fields = resource[FIELDS_PARENT[resource_type]].get('fields', {})
        else:
            fields = resource.get('fields', {})

        if resource_type == SAMPLE_PATH:
            fields = dict([(field['id'], field) for field in
                           fields])
    return fields


class BigML(ExternalConnectorHandler,
            LinearRegressionHandler, BatchProjectionHandler,
            ProjectionHandler, PCAHandler,
            ConfigurationHandler, FusionHandler,
            OptimlHandler,
            DeepnetHandler, ForecastHandler, TimeSeriesHandler,
            BatchTopicDistributionHandler, TopicDistributionHandler,
            TopicModelHandler, LibraryHandler, ExecutionHandler, ScriptHandler,
            AssociationSetHandler, AssociationHandler,
            LogisticRegressionHandler,
            StatisticalTestHandler, CorrelationHandler,
            SampleHandler, ProjectHandler,
            BatchAnomalyScoreHandler, BatchCentroidHandler,
            BatchPredictionHandler, EvaluationHandler, AnomalyScoreHandler,
            AnomalyHandler, CentroidHandler, ClusterHandler, PredictionHandler,
            EnsembleHandler, ModelHandler, DatasetHandler,
            SourceHandler, ResourceHandler, BigMLConnection):
    """Entry point to create, retrieve, list, update, and delete
    BigML resources.

    Full API documentation on the API can be found from BigML at:
        https://bigml.com/api

    Resources are wrapped in a dictionary that includes:
        code: HTTP status code
        resource: The resource/id
        location: Remote location of the resource
        object: The resource itself
        error: An error code and message

    """
    def __init__(self, username=None, api_key=None,
                 debug=False, set_locale=False, storage=None, domain=None,
                 project=None, organization=None, short_debug=False):
        """Initializes the BigML API.

        If left unspecified, `username` and `api_key` will default to the
        values of the `BIGML_USERNAME` and `BIGML_API_KEY` environment
        variables respectively.

        `dev_mode` has been deprecated. Now all resources coexisit in the
        same production environment.

        If storage is set to a directory name, the resources obtained in
        CRU operations will be stored in the given directory.

        If domain is set, the api will point to the specified domain. Default
        will be the one in the environment variable `BIGML_DOMAIN` or
        `bigml.io` if missing. The expected domain argument is a string or a
        Domain object. See Domain class for details.

        When project is set to a project ID,
        the user is considered to be working in an
        organization project. The scope of the API requests will be limited
        to this project and permissions should be previously given by the
        organization administrator.

        When organization is set to an organization ID,
        the user is considered to be working for an
        organization. The scope of the API requests will be limited to the
        projects of the organization and permissions need to be previously
        given by the organization administrator.

        """

        BigMLConnection.__init__(self, username=username, api_key=api_key,
                                 debug=debug,
                                 set_locale=set_locale, storage=storage,
                                 domain=domain, project=project,
                                 organization=organization,
                                 short_debug=short_debug)
        ResourceHandler.__init__(self)
        SourceHandler.__init__(self)
        DatasetHandler.__init__(self)
        ModelHandler.__init__(self)
        EnsembleHandler.__init__(self)
        PredictionHandler.__init__(self)
        ClusterHandler.__init__(self)
        CentroidHandler.__init__(self)
        AnomalyHandler.__init__(self)
        AnomalyScoreHandler.__init__(self)
        EvaluationHandler.__init__(self)
        BatchPredictionHandler.__init__(self)
        BatchCentroidHandler.__init__(self)
        BatchAnomalyScoreHandler.__init__(self)
        ProjectHandler.__init__(self)
        SampleHandler.__init__(self)
        CorrelationHandler.__init__(self)
        StatisticalTestHandler.__init__(self)
        LogisticRegressionHandler.__init__(self)
        AssociationHandler.__init__(self)
        AssociationSetHandler.__init__(self)
        ScriptHandler.__init__(self)
        ExecutionHandler.__init__(self)
        LibraryHandler.__init__(self)
        TopicModelHandler.__init__(self)
        TopicDistributionHandler.__init__(self)
        BatchTopicDistributionHandler.__init__(self)
        TimeSeriesHandler.__init__(self)
        ForecastHandler.__init__(self)
        DeepnetHandler.__init__(self)
        OptimlHandler.__init__(self)
        FusionHandler.__init__(self)
        ConfigurationHandler.__init__(self)
        PCAHandler.__init__(self)
        ProjectionHandler.__init__(self)
        BatchProjectionHandler.__init__(self)
        LinearRegressionHandler.__init__(self)
        ExternalConnectorHandler.__init__(self)
        self.status_url = "%s%s" % (self.url, STATUS_PATH)


        self.getters = {}
        for resource_type in RESOURCE_RE:
            method_name = RENAMED_RESOURCES.get(resource_type, resource_type)
            self.getters[resource_type] = getattr(self, "get_%s" % method_name)
        self.creaters = {}
        for resource_type in RESOURCE_RE:
            method_name = RENAMED_RESOURCES.get(resource_type, resource_type)
            self.creaters[resource_type] = getattr(self,
                                                   "create_%s" % method_name)
        self.updaters = {}
        for resource_type in RESOURCE_RE:
            method_name = RENAMED_RESOURCES.get(resource_type, resource_type)
            self.updaters[resource_type] = getattr(self,
                                                   "update_%s" % method_name)
        self.deleters = {}
        for resource_type in RESOURCE_RE:
            method_name = RENAMED_RESOURCES.get(resource_type, resource_type)
            self.deleters[resource_type] = getattr(self,
                                                   "delete_%s" % method_name)
        self.listers = {}
        for resource_type in RESOURCE_RE:
            method_name = IRREGULAR_PLURALS.get( \
                resource_type, "%ss" % RENAMED_RESOURCES.get( \
                resource_type, resource_type))
            self.listers[resource_type] = getattr(self,
                                                  "list_%s" % method_name)

    def connection_info(self):
        """Printable string: domain where the connection is bound and the
           credentials used.

        """
        info = u"Connecting to:\n"
        info += u"    %s\n" % self.general_domain
        if self.general_protocol != BIGML_PROTOCOL:
            info += u"    using %s protocol\n" % self.general_protocol
        info += u"    SSL verification %s\n" % (
            "on" if self.verify else "off")
        short = "(shortened)" if self.short_debug else ""
        if self.debug:
            info += u"    Debug on %s\n" % short
        if self.general_domain != self.prediction_domain:
            info += u"    %s (predictions only)\n" % self.prediction_domain
            if self.prediction_protocol != BIGML_PROTOCOL:
                info += u"    using %s protocol\n" % self.prediction_protocol
            info += u"    SSL verification %s\n" % (
                "on" if self.verify_prediction else "off")

        if self.project or self.organization:
            info += u"    Scope info: %s\n" % \
                u"%s\n                %s" % (self.organization or "",
                                             self.project or "")


        info += u"\nAuthentication string:\n"
        info += u"    %s\n" % self.auth[1:]
        return info

    def get_account_status(self):
        """Retrieve the account information: tasks, available_tasks, max_tasks, .

        Returns a dictionary with the summarized information about the account

        """
        if self.organization is not None:
            return self._status(self.status_url,
                                organization=self.organization)
        return self._status(self.status_url)

    def get_tasks_status(self):
        """Retrieve the tasks information of the account

        Returns a dictionary with the summarized information about the tasks

        """
        if self.organization is not None:
            status = self._status(self.status_url,
                                  organization=self.organization)["object"]
        else:
            status = self._status(self.status_url)["object"]
        return {
            "tasks": status["tasks"],
            "max_tasks": status["subscription"]["max_tasks"],
            "available_tasks": (status["subscription"]["max_tasks"]
                                - status["tasks"]),
            "tasks_in_progress": status["tasks_in_progress"]}

    def get_fields(self, resource):
        """Retrieve fields used by a resource.

        Returns a dictionary with the fields that uses
        the resource keyed by Id.

        """

        if isinstance(resource, dict) and 'resource' in resource:
            resource_id = resource['resource']
        elif isinstance(resource, basestring) and get_resource_type(resource) \
                in RESOURCES_WITH_FIELDS:
            resource_id = resource
            resource = self.retrieve_resource(resource,
                                              query_string=ALL_FIELDS)
        else:
            LOGGER.error("Wrong resource id")
            return
        # Tries to extract fields information from resource dict. If it fails,
        # a get remote call is used to retrieve the resource by id.
        fields = None
        try:
            fields = get_fields(resource)
        except KeyError:
            resource = self._get("%s%s" % (self.url, resource_id))
            fields = get_fields(resource)

        return fields

    def pprint(self, resource, out=sys.stdout):
        """Pretty prints a resource or part of it.

        """

        if (isinstance(resource, dict)
                and 'object' in resource
                and 'resource' in resource):

            resource_id = resource['resource']
            if (SOURCE_RE.match(resource_id) or DATASET_RE.match(resource_id)
                    or MODEL_RE.match(resource_id)
                    or EVALUATION_RE.match(resource_id)
                    or ENSEMBLE_RE.match(resource_id)
                    or CLUSTER_RE.match(resource_id)
                    or ANOMALY_RE.match(resource_id)
                    or TOPIC_MODEL_RE.match(resource_id)
                    or LOGISTIC_REGRESSION_RE.match(resource_id)
                    or TIME_SERIES_RE.match(resource_id)
                    or DEEPNET_RE.match(resource_id)
                    or FUSION_RE.match(resource_id)
                    or PCA_RE.match(resource_id)
                    or LINEAR_REGRESSION_RE.match(resource_id)
                    or OPTIML_RE.match(resource_id)):
                out.write("%s (%s bytes)\n" % (resource['object']['name'],
                                               resource['object']['size']))
            elif PREDICTION_RE.match(resource['resource']):
                objective_field_name = (
                    resource['object']['fields'][
                        resource['object']['objective_fields'][0]]['name'])
                input_data = {}
                for key, value in resource['object']['input_data'].items():
                    try:
                        name = resource['object']['fields'][key]['name']
                    except KeyError:
                        name = key
                    input_data[name] = value

                prediction = (
                    resource['object']['prediction'][
                        resource['object']['objective_fields'][0]])
                out.write("%s for %s is %s\n" % (objective_field_name,
                                                 input_data,
                                                 prediction))
            out.flush()
        else:
            pprint.pprint(resource, out, indent=4)

    def status(self, resource):
        """Maps status code to string.

        """
        resource_id = get_resource_id(resource)
        if resource_id:
            resource = self._get("%s%s" % (self.url, resource_id))
            status = get_status(resource)
            code = status['code']
            return STATUSES.get(code, "UNKNOWN")
        else:
            status = get_status(resource)
            if status['code'] != UPLOADING:
                LOGGER.error("Wrong resource id")
                return
            return STATUSES[UPLOADING]

    def check_resource(self, resource,
                       query_string='', wait_time=1):
        """Check resource method.

        """
        return check_resource(resource,
                              query_string=query_string, wait_time=wait_time,
                              api=self)

    def source_from_batch_prediction(self, batch_prediction, args=None):
        """Creates a source from a batch prediction using the download url

        """
        check_resource_type(batch_prediction, BATCH_PREDICTION_PATH,
                            message="A batch prediction id is needed.")
        batch_prediction_id = get_batch_prediction_id(batch_prediction)
        if batch_prediction_id:
            download_url = "%s%s%s%s" % (self.url, batch_prediction_id,
                                         DOWNLOAD_DIR, self.auth)
            return self._create_remote_source(download_url, args=args)

    def retrieve_resource(self, resource_id, query_string=None,
                          check_local_fn=None, retries=None):
        """ Retrieves resource info either from the local repo or
            from the remote server

        """
        if query_string is None:
            query_string = ''
        if self.storage is not None:
            try:
                stored_resource = os.path.join(self.storage,
                                              resource_id.replace("/", "_"))
                with open(stored_resource) as resource_file:
                    resource = json.loads(resource_file.read())
                # we check that the stored resource has the information
                # needed (for instance, input_fields for predicting)
                if check_local_fn is None or check_local_fn(resource):
                    return resource
            except ValueError:
                raise ValueError("The file %s contains no JSON")
            except IOError:
                pass
        if self.auth == '?username=;api_key=;':
            raise ValueError("The credentials information is missing. This"
                             " information is needed to download resource %s"
                             " for the first time and store it locally for further"
                             " use. Please export BIGML_USERNAME"
                             " and BIGML_API_KEY."  % resource_id)
        api_getter = self.getters[get_resource_type(resource_id)]
        resource = check_resource(resource_id, query_string=query_string,
                                  api=self, retries=retries)
        return resource


def get_api_connection(api, store=True, context=None):
    """Checks whether there's a valid api connection. If there's not
    such object, it creates a default connection with the credentials
    and other attributes provided in the context dictionary

        api: (BigML) customized api connection (if provided)
        store: (boolean) use storage when creating the connection
        context: (dict) parameters to be provided when creating the connection
    """
    if api is None or not isinstance(api, BigML):
        if context is None:
            context = {}
        storage = context.get("storage") or STORAGE
        context.update({"storage": storage} if store else {})
        try:
            api = BigML(**context)
        except AttributeError:
            context.update({"username": "", "api_key": ""})
            api = BigML(**context)
            # API connection with
            # False credentials is returned. It can only access the
            # local resources stored in the storage directory when present
    return api
