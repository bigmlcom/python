# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2018-2020 BigML
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


""" Creating tests for building local models from files

"""
from world import world, setup_module, teardown_module
import create_model_steps as model_create
import create_linear_steps as linear_create
import create_source_steps as source_create
import create_dataset_steps as dataset_create
import create_ensemble_steps as ensemble_create
import create_anomaly_steps as anomaly_create
import create_time_series_steps as timeseries_create
import create_association_steps as association_create
import create_cluster_steps as cluster_create
import create_lda_steps as topic_create
import compare_predictions_steps as prediction_compare
from bigml.util import PY3

class TestLocalFromFile(object):

    def setup(self):
        """
            Debug information
        """
        print "\n-------------------\nTests in: %s\n" % __name__

    def teardown(self):
        """
            Debug information
        """
        print "\nEnd of tests in: %s\n-------------------\n" % __name__

    def test_scenario1(self):
        """
            Scenario 1: Successfully creating a local model from an exported file:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a model
                And I wait until the model is ready less than <time_3> secs
                And I export the "<pmml>" model to "<exported_file>"
                When I create a local model from the file "<exported_file>"
                Then the model ID and the local model ID match
                Examples:
                | data                | time_1  | time_2 | time_3 | pmml | exported_file
                | ../data/iris.csv | 10      | 10     | 10 | False | ./tmp/model.json
        """
        print self.test_scenario1.__doc__
        examples = [
            ['data/iris.csv', '10', '10', '10', False, './tmp/model.json']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_model(self)
            model_create.the_model_is_finished_in_less_than(self, example[3])
            model_create.i_export_model(self, example[4], example[5])
            model_create.i_create_local_model_from_file(self, example[5])
            model_create.check_model_id_local_id(self)


    def test_scenario2(self):
        """
            Scenario 2: Successfully creating a local ensemble from an exported file:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create an ensemble
                And I wait until the ensemble is ready less than <time_3> secs
                And I export the ensemble to "<exported_file>"
                When I create a local ensemble from the file "<exported_file>"
                Then the ensemble ID and the local ensemble ID match
                Examples:
                | data                | time_1  | time_2 | time_3 | exported_file
                | ../data/iris.csv | 10      | 10     | 50 | ./tmp/ensemble.json
        """
        print self.test_scenario2.__doc__
        examples = [
            ['data/iris.csv', '10', '10', '50', './tmp/ensemble.json']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            ensemble_create.i_create_an_ensemble(self)
            ensemble_create.the_ensemble_is_finished_in_less_than(self, example[3])
            ensemble_create.i_export_ensemble(self, example[4])
            ensemble_create.i_create_local_ensemble_from_file(self, example[4])
            ensemble_create.check_ensemble_id_local_id(self)


    def test_scenario3(self):
        """
            Scenario 3: Successfully creating a local logistic regression from an exported file:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a logistic regression
                And I wait until the logistic regression is ready less than <time_3> secs
                And I export the logistic regression to "<exported_file>"
                When I create a local logistic regression from the file "<exported_file>"
                Then the logistic regression ID and the local logistic regression ID match
                Examples:
                | data                | time_1  | time_2 | time_3 | exported_file
                | ../data/iris.csv | 10      | 10     | 50 | ./tmp/logistic.json
        """
        print self.test_scenario3.__doc__
        examples = [
            ['data/iris.csv', '10', '10', '50', './tmp/logistic.json']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_logistic_model(self)
            model_create.the_logistic_model_is_finished_in_less_than(self, example[3])
            model_create.i_export_logistic_regression(self, example[4])
            model_create.i_create_local_logistic_regression_from_file(self, example[4])
            model_create.check_logistic_regression_id_local_id(self)


    def test_scenario4(self):
        """
            Scenario 4: Successfully creating a local deepnet from an exported file:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a deepnet
                And I wait until the deepnet is ready less than <time_3> secs
                And I export the deepnet to "<exported_file>"
                When I create a local deepnet from the file "<exported_file>"
                Then the deepnet ID and the local deepnet ID match
                Examples:
                | data                | time_1  | time_2 | time_3 | exported_file
                | ../data/iris.csv | 10      | 10     | 50 | ./tmp/deepnet.json
        """
        print self.test_scenario4.__doc__
        examples = [
            ['data/iris.csv', '10', '10', '500', './tmp/deepnet.json']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_deepnet(self)
            model_create.the_deepnet_is_finished_in_less_than(self, example[3])
            model_create.i_export_deepnet(self, example[4])
            model_create.i_create_local_deepnet_from_file(self, example[4])
            model_create.check_deepnet_id_local_id(self)


    def test_scenario5(self):
        """
            Scenario 5: Successfully creating a local cluster from an exported file:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a cluster
                And I wait until the cluster is ready less than <time_3> secs
                And I export the cluster to "<exported_file>"
                When I create a local cluster from the file "<exported_file>"
                Then the cluster ID and the local cluster ID match
                Examples:
                | data                | time_1  | time_2 | time_3 | exported_file
                | ../data/iris.csv | 10      | 10     | 50 | ./tmp/cluster.json
        """
        print self.test_scenario5.__doc__
        examples = [
            ['data/iris.csv', '10', '10', '500', './tmp/cluster.json']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            cluster_create.i_create_a_cluster(self)
            cluster_create.the_cluster_is_finished_in_less_than(self, example[3])
            cluster_create.i_export_cluster(self, example[4])
            cluster_create.i_create_local_cluster_from_file(self, example[4])
            cluster_create.check_cluster_id_local_id(self)


    def test_scenario6(self):
        """
            Scenario 6: Successfully creating a local anomaly from an exported file:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create an anomaly
                And I wait until the anomaly is ready less than <time_3> secs
                And I export the anomaly to "<exported_file>"
                When I create a local anomaly from the file "<exported_file>"
                Then the anomaly ID and the local anomaly ID match
                Examples:
                | data                | time_1  | time_2 | time_3 | exported_file
                | ../data/iris.csv | 10      | 10     | 50 | ./tmp/anomaly.json
        """
        print self.test_scenario6.__doc__
        examples = [
            ['data/iris.csv', '10', '10', '500', './tmp/anomaly.json']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            anomaly_create.i_create_an_anomaly(self)
            anomaly_create.the_anomaly_is_finished_in_less_than(self, example[3])
            anomaly_create.i_export_anomaly(self, example[4])
            anomaly_create.i_create_local_anomaly_from_file(self, example[4])
            anomaly_create.check_anomaly_id_local_id(self)

    def test_scenario7(self):
        """
            Scenario 7: Successfully creating a local association from an exported file:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create an association
                And I wait until the association is ready less than <time_3> secs
                And I export the association to "<exported_file>"
                When I create a local association from the file "<exported_file>"
                Then the association ID and the local association ID match
                Examples:
                | data                | time_1  | time_2 | time_3 | exported_file
                | ../data/iris.csv | 10      | 10     | 50 | ./tmp/association.json
        """
        print self.test_scenario7.__doc__
        examples = [
            ['data/iris.csv', '10', '10', '500', './tmp/association.json']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            association_create.i_create_an_association_from_dataset(self)
            association_create.the_association_is_finished_in_less_than(self, example[3])
            association_create.i_export_association(self, example[4])
            association_create.i_create_local_association_from_file(self, example[4])
            association_create.check_association_id_local_id(self)

    def test_scenario8(self):
        """
            Scenario 8: Successfully creating a local topic model from an exported file:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a topic model
                And I wait until the topic model is ready less than <time_3> secs
                And I export the topic model to "<exported_file>"
                When I create a local topic model from the file "<exported_file>"
                Then the topic model ID and the local topic model ID match
                Examples:
                | data                | time_1  | time_2 | time_3 | exported_file
                | ../data/iris.csv | 10      | 10     | 50 | ./tmp/topic_model.json
        """
        print self.test_scenario8.__doc__
        examples = [
            ['data/spam.csv', '10', '10', '500', './tmp/topic_model.json', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false, "language": "en"}}}}']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            source_create.i_update_source_with(self, example[5])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            topic_create.i_create_a_topic_model(self)
            topic_create.the_topic_model_is_finished_in_less_than(self, example[3])
            topic_create.i_export_topic_model(self, example[4])
            topic_create.i_create_local_topic_model_from_file(self, example[4])
            topic_create.check_topic_model_id_local_id(self)

    def test_scenario9(self):
        """
            Scenario 9: Successfully creating a local association from an exported file:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a time series
                And I wait until the time series is ready less than <time_3> secs
                And I export the time series to "<exported_file>"
                When I create a local time series from the file "<exported_file>"
                Then the time series ID and the local time series ID match
                Examples:
                | data                | time_1  | time_2 | time_3 | exported_file
                | ../data/iris.csv | 10      | 10     | 50 | ./tmp/time_series.json
        """
        print self.test_scenario9.__doc__
        examples = [
            ['data/iris.csv', '10', '10', '500', './tmp/time_series.json']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            timeseries_create.i_create_a_time_series(self)
            timeseries_create.the_time_series_is_finished_in_less_than(self, example[3])
            timeseries_create.i_export_time_series(self, example[4])
            timeseries_create.i_create_local_time_series_from_file(self, example[4])
            timeseries_create.check_time_series_id_local_id(self)


    def test_scenario10(self):
        """
            Scenario 10: Successfully creating a local fusion from an exported file:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a model with "<params>"
                And I wait until the model is ready less than <time_3> secs
                And I create a model with "<params>"
                And I wait until the model is ready less than <time_3> secs
                And I create a model with "<params>"
                And I wait until the model is ready less than <time_3> secs
                And I retrieve a list of remote models tagged with "<tag>"
                And I create a fusion from a list of models
                And I wait until the fusion is ready less than <time_3> secs
                And I export the fusion to "<exported_file>"
                When I create a local fusion from the file "<exported_file>"
                Then the fusion ID and the local fusion ID match
                Examples:
                | data                | time_1  | time_2 | time_3 | exported_file | params | tag
                | ../data/iris.csv | 10      | 10     | 50 | ./tmp/fusion.json
        """
        print self.test_scenario10.__doc__
        examples = [
            ['data/iris.csv', '10', '10', '50', './tmp/fusion.json', 'my_fusion_tag']]
        for example in examples:
            print "\nTesting with:\n", example
            tag = "%s_%s" % (example[5], PY3)
            tag_args = '{"tags":["%s"]}' % tag
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_model_with(self, tag_args)
            model_create.the_model_is_finished_in_less_than(self, example[3])
            model_create.i_create_a_model_with(self, tag_args)
            model_create.the_model_is_finished_in_less_than(self, example[3])
            model_create.i_create_a_model_with(self, tag_args)
            model_create.the_model_is_finished_in_less_than(self, example[3])
            prediction_compare.i_retrieve_a_list_of_remote_models(self, tag)
            model_create.i_create_a_fusion(self)
            model_create.the_fusion_is_finished_in_less_than(self, example[3])
            model_create.i_export_fusion(self, example[4])
            model_create.i_create_local_fusion_from_file(self, example[4])
            model_create.check_fusion_id_local_id(self)


    def test_scenario11(self):
        """
            Scenario 11: Successfully creating a local linear regression from an exported file:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a linear regression
                And I wait until the linear regression is ready less than <time_3> secs
                And I export the linear regression to "<exported_file>"
                When I create a local linear regression from the file "<exported_file>"
                Then the linear regression ID and the local linear regression ID match
                Examples:
                | data                | time_1  | time_2 | time_3 | exported_file
                | ../data/grades.csv | 10      | 10     | 50 | ./tmp/linear.json
        """
        print self.test_scenario11.__doc__
        examples = [
            ['data/grades.csv', '20', '20', '50', './tmp/linear.json']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            linear_create.i_create_a_linear_regression_from_dataset(self)
            linear_create.the_linear_regression_is_finished_in_less_than(self, example[3])
            model_create.i_export_linear_regression(self, example[4])
            model_create.i_create_local_linear_regression_from_file(self, example[4])
            model_create.check_linear_regression_id_local_id(self)
