# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2012-2016 BigML
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


from bigml.bigmlconnection import BigMLConnection
from bigml.domain import BIGML_PROTOCOL
from bigml.resourcehandler import ResourceHandler
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
from bigml.scripthandler import ScriptHandler
from bigml.executionhandler import ExecutionHandler
from bigml.libraryhandler import LibraryHandler


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
    ASSOCIATION_RE, ASSOCIATION_SET_PATH, ASSOCIATION_SET_RE,
    SCRIPT_PATH, SCRIPT_RE,
    EXECUTION_PATH, EXECUTION_RE, LIBRARY_PATH, LIBRARY_RE)

from bigml.resourcehandler import (
    get_resource, get_resource_type, check_resource_type, get_source_id,
    get_dataset_id, get_model_id, get_ensemble_id, get_evaluation_id,
    get_cluster_id, get_centroid_id, get_anomaly_id, get_anomaly_score_id,
    get_prediction_id, get_batch_prediction_id, get_batch_centroid_id,
    get_batch_anomaly_score_id, get_resource_id, resource_is_ready,
    get_status, check_resource, http_ok, get_project_id, get_sample_id,
    get_correlation_id, get_statistical_test_id, get_logistic_regression_id,
    get_association_id, get_association_set_id, get_script_id,
    get_execution_id, get_library_id)


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


def count(listing):
    """Count of existing resources

    """
    if 'meta' in listing and 'query_total' in listing['meta']:
        return listing['meta']['query_total']


class BigML(LibraryHandler, ExecutionHandler, ScriptHandler,
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
        https://bigml.com/developers

    Resources are wrapped in a dictionary that includes:
        code: HTTP status code
        resource: The resource/id
        location: Remote location of the resource
        object: The resource itself
        error: An error code and message

    """
    def __init__(self, username=None, api_key=None, dev_mode=False,
                 debug=False, set_locale=False, storage=None, domain=None):
        """Initializes the BigML API.

        If left unspecified, `username` and `api_key` will default to the
        values of the `BIGML_USERNAME` and `BIGML_API_KEY` environment
        variables respectively.

        If `dev_mode` is set to `True`, the API will be used in development
        mode where the size of your datasets are limited but you are not
        charged any credits.

        If storage is set to a directory name, the resources obtained in
        CRU operations will be stored in the given directory.

        If domain is set, the api will point to the specified domain. Default
        will be the one in the environment variable `BIGML_DOMAIN` or
        `bigml.io` if missing. The expected domain argument is a string or a
        Domain object. See Domain class for details.

        """

        BigMLConnection.__init__(self, username=username, api_key=api_key,
                                 dev_mode=dev_mode, debug=debug,
                                 set_locale=set_locale, storage=storage,
                                 domain=domain)
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
        if self.general_domain != self.prediction_domain:
            info += u"    %s (predictions only)\n" % self.prediction_domain
            if self.prediction_protocol != BIGML_PROTOCOL:
                info += u"    using %s protocol\n" % self.prediction_protocol
            info += u"    SSL verification %s\n" % (
                "on" if self.verify_prediction else "off")

        info += u"\nAuthentication string:\n"
        info += u"    %s\n" % self.auth[1:]
        return info

    def get_fields(self, resource):
        """Retrieve fields used by a resource.

        Returns a dictionary with the fields that uses
        the resource keyed by Id.

        """

        def _get_fields_key(resource):
            """Returns the fields key from a resource dict

            """
            if resource['code'] in [HTTP_OK, HTTP_ACCEPTED]:
                if (MODEL_RE.match(resource_id) or
                        ANOMALY_RE.match(resource_id)):
                    return resource['object']['model']['model_fields']
                elif CLUSTER_RE.match(resource_id):
                    return resource['object']['clusters']['fields']
                elif CORRELATION_RE.match(resource_id):
                    return resource['object']['correlations']['fields']
                elif STATISTICAL_TEST_RE.match(resource_id):
                    return resource['object']['statistical_tests']['fields']
                elif STATISTICAL_TEST_RE.match(resource_id):
                    return resource['object']['statistical_tests']['fields']
                elif LOGISTIC_REGRESSION_RE.match(resource_id):
                    return resource['object']['logistic_regression']['fields']
                elif ASSOCIATION_RE.match(resource_id):
                    return resource['object']['associations']['fields']
                elif SAMPLE_RE.match(resource_id):
                    return dict([(field['id'], field) for field in
                                 resource['object']['sample']['fields']])
                else:
                    return resource['object']['fields']
            return None

        if isinstance(resource, dict) and 'resource' in resource:
            resource_id = resource['resource']
        elif (isinstance(resource, basestring) and (
                SOURCE_RE.match(resource) or DATASET_RE.match(resource) or
                MODEL_RE.match(resource) or PREDICTION_RE.match(resource))):
            resource_id = resource
            resource = self._get("%s%s" % (self.url, resource_id))
        else:
            LOGGER.error("Wrong resource id")
            return
        # Tries to extract fields information from resource dict. If it fails,
        # a get remote call is used to retrieve the resource by id.
        fields = None
        try:
            fields = _get_fields_key(resource)
        except KeyError:
            resource = self._get("%s%s" % (self.url, resource_id))
            fields = _get_fields_key(resource)

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
                    or ANOMALY_RE.match(resource_id)):
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
