# -*- coding: utf-8 -*-
#
# Copyright 2020 BigML
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


""" Creating clones for models

"""
from .world import world, setup_module, teardown_module
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create
from . import create_model_steps as model_create
from . import create_ensemble_steps as ensemble_create
from . import create_linear_steps as linear_create
from . import create_cluster_steps as cluster_create
from . import create_lda_steps as topic_create
from . import create_anomaly_steps as anomaly_create
from . import create_association_steps as association_create
from . import create_time_series_steps as time_create
from . import create_pca_steps as pca_create


class TestCloning(object):

    def setup(self):
        """
            Debug information
        """
        print("\n-------------------\nTests in: %s\n" % __name__)

    def teardown(self):
        """
            Debug information
        """
        print("\nEnd of tests in: %s\n-------------------\n" % __name__)

    def test_scenario1(self):
        """
            Scenario: Successfully creating a clone from a model:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a model
                And I wait until the model is ready less than <time_3> secs
                Then the origin model is the previous model

                Examples:
                | data                | time_1  | time_2 | time_3 |
                | ../data/iris.csv | 10      | 10     | 10     |
        """
        print(self.test_scenario1.__doc__)
        examples = [
            ['data/iris.csv', '10', '10', '10']]
        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example[2])
            model_create.i_create_a_model(self)
            model_create.the_model_is_finished_in_less_than(self, example[3])
            model = world.model["resource"]
            model_create.clone_model(self, model)
            model_create.the_cloned_model_is(self, model)

    def test_scenario2(self):
        """
            Scenario: Successfully creating a clone from a ensemble:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create an ensemble
                And I wait until the ensemble is ready less than <time_3> secs
                Then the origin ensemble is the previous ensemble

                Examples:
                | data                | time_1  | time_2 | time_3 |
                | ../data/iris.csv | 10      | 10     | 10     |
        """
        print(self.test_scenario2.__doc__)
        examples = [
            ['data/iris.csv', '10', '10', '30']]
        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example[2])
            ensemble_create.i_create_an_ensemble(self)
            ensemble_create.the_ensemble_is_finished_in_less_than(
                self, example[3])
            ensemble = world.ensemble["resource"]
            ensemble_create.clone_ensemble(self, ensemble)
            ensemble_create.the_cloned_ensemble_is(self, ensemble)

    def test_scenario3(self):
        """
            Scenario: Successfully creating a clone from a deepnet:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a quick deepnet
                And I wait until the deepnet is ready less than <time_3> secs
                Then the origin deepnet is the previous deepnet

                Examples:
                | data                | time_1  | time_2 | time_3 |
                | ../data/iris.csv | 10      | 10     | 10     |
        """
        print(self.test_scenario3.__doc__)
        examples = [
            ['data/iris.csv', '10', '10', '100']]
        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example[2])
            model_create.i_create_a_quick_deepnet(self)
            model_create.the_deepnet_is_finished_in_less_than(
                self, example[3])
            deepnet = world.deepnet["resource"]
            model_create.clone_deepnet(self, deepnet)
            model_create.the_cloned_deepnet_is(self, deepnet)

    def test_scenario4(self):
        """
            Scenario: Successfully creating a clone from a logistic regression:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a logistic regression
                And I wait until the logistic regression is ready less than <time_3> secs
                Then the origin logistic regression is the previous logistic regression

                Examples:
                | data                | time_1  | time_2 | time_3 |
                | ../data/iris.csv | 10      | 10     | 10     |
        """
        print(self.test_scenario4.__doc__)
        examples = [
            ['data/iris.csv', '10', '10', '30']]
        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example[2])
            model_create.i_create_a_logistic_model(self)
            model_create.the_logistic_model_is_finished_in_less_than(
                self, example[3])
            logistic_regression = world.logistic_regression["resource"]
            model_create.clone_logistic_regression(self, logistic_regression)
            model_create.the_cloned_logistic_regression_is(
                self, logistic_regression)

    def test_scenario5(self):
        """
            Scenario: Successfully creating a clone from a linear regression:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a linear regression
                And I wait until the linear regression is ready less than <time_3> secs
                Then the origin linear regression is the previous linear regression

                Examples:
                | data                | time_1  | time_2 | time_3 |
                | ../data/iris.csv | 10      | 10     | 10     |
        """
        print(self.test_scenario5.__doc__)
        examples = [
            ['data/iris.csv', '10', '10', '30']]
        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example[2])
            linear_create.i_create_a_linear_regression_from_dataset(self)
            linear_create.the_linear_regression_is_finished_in_less_than(
                self, example[3])
            linear_regression = world.linear_regression["resource"]
            linear_create.clone_linear_regression(self, linear_regression)
            linear_create.the_cloned_linear_regression_is(
                self, linear_regression)

    def test_scenario6(self):
        """
            Scenario: Successfully creating a clone from a cluster:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a cluster
                And I wait until the cluster is ready less than <time_3> secs
                Then the origin cluster is the previous cluster

                Examples:
                | data                | time_1  | time_2 | time_3 |
                | ../data/iris.csv | 10      | 10     | 10     |
        """
        print(self.test_scenario6.__doc__)
        examples = [
            ['data/iris.csv', '10', '10', '30']]
        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example[2])
            cluster_create.i_create_a_cluster(self)
            cluster_create.the_cluster_is_finished_in_less_than(
                self, example[3])
            cluster = world.cluster["resource"]
            cluster_create.clone_cluster(self, cluster)
            cluster_create.the_cloned_cluster_is(
                self, cluster)

    def test_scenario7(self):
        """
            Scenario: Successfully creating a clone from a topic model:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a topic model
                And I wait until the topic model is ready less than <time_3> secs
                Then the origin topic model is the previous topic model

                Examples:
                | data                | time_1  | time_2 | time_3 |
                | ../data/iris.csv | 10      | 10     | 10     |
        """
        print(self.test_scenario7.__doc__)
        examples = [
            ['data/spam.csv', '10', '10', '100', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false, "language": "en"}}}}']]
        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            source_create.i_update_source_with(self, example[4])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example[2])
            topic_create.i_create_a_topic_model(self)
            topic_create.the_topic_model_is_finished_in_less_than(
                self, example[3])
            topic_model = world.topic_model["resource"]
            topic_create.clone_topic_model(self, topic_model)
            topic_create.the_cloned_topic_model_is(
                self, topic_model)


    def test_scenario8(self):
        """
            Scenario: Successfully creating a clone from an anomaly detector:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create an anomaly detector
                And I wait until the anomaly detector is ready less than <time_3> secs
                Then the origin anomaly detector is the previous anomaly detector

                Examples:
                | data                | time_1  | time_2 | time_3 |
                | ../data/iris.csv | 10      | 10     | 10     |
        """
        print(self.test_scenario8.__doc__)
        examples = [
            ['data/iris.csv', '10', '10', '100']]
        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example[2])
            anomaly_create.i_create_an_anomaly(self)
            anomaly_create.the_anomaly_is_finished_in_less_than(
                self, example[3])
            anomaly = world.anomaly["resource"]
            anomaly_create.clone_anomaly(self, anomaly)
            anomaly_create.the_cloned_anomaly_is(
                self, anomaly)

    def test_scenario9(self):
        """
            Scenario: Successfully creating a clone from an association:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create an association
                And I wait until the association is ready less than <time_3> secs
                Then the origin association is the previous association

                Examples:
                | data                | time_1  | time_2 | time_3 |
                | ../data/iris.csv | 10      | 10     | 10     |
        """
        print(self.test_scenario9.__doc__)
        examples = [
            ['data/iris.csv', '10', '10', '100']]
        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example[2])
            association_create.i_create_an_association_from_dataset(self)
            association_create.the_association_is_finished_in_less_than(
                self, example[3])
            association = world.association["resource"]
            association_create.clone_association(self, association)
            association_create.the_cloned_association_is(
                self, association)

    def test_scenario10(self):
        """
            Scenario: Successfully creating a clone from a time series:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a time series
                And I wait until the time series is ready less than <time_3> secs
                Then the origin time series is the previous time series

                Examples:
                | data                | time_1  | time_2 | time_3 |
                | ../data/iris.csv | 10      | 10     | 10     |
        """
        print(self.test_scenario10.__doc__)
        examples = [
            ['data/iris.csv', '10', '10', '100']]
        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example[2])
            time_create.i_create_a_time_series(self)
            time_create.the_time_series_is_finished_in_less_than(
                self, example[3])
            time_series = world.time_series["resource"]
            time_create.clone_time_series(self, time_series)
            time_create.the_cloned_time_series_is(
                self, time_series)

    def test_scenario11(self):
        """
            Scenario: Successfully creating a clone from a pca:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a pca
                And I wait until the pca is ready less than <time_3> secs
                Then the origin pca is the previous pca

                Examples:
                | data                | time_1  | time_2 | time_3 |
                | ../data/iris.csv | 10      | 10     | 10     |
        """
        print(self.test_scenario11.__doc__)
        examples = [
            ['data/iris.csv', '10', '10', '100']]
        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example[2])
            pca_create.i_create_a_pca(self)
            pca_create.the_pca_is_finished_in_less_than(
                self, example[3])
            pca = world.pca["resource"]
            pca_create.clone_pca(self, pca)
            pca_create.the_cloned_pca_is(self, pca)
