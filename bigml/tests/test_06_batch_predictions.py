# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015-2020 BigML
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


""" Creating batch predictions

"""
from world import world, setup_module, teardown_module
import create_source_steps as source_create
import create_dataset_steps as dataset_create
import create_model_steps as model_create
import create_ensemble_steps as ensemble_create
import create_cluster_steps as cluster_create
import create_anomaly_steps as anomaly_create
import create_batch_prediction_steps as batch_pred_create
import create_prediction_steps as prediction_create



class TestBatchPrediction(object):

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
            Scenario: Successfully creating a batch prediction:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a model
                And I wait until the model is ready less than <time_3> secs
                When I create a batch prediction for the dataset with the model
                And I wait until the batch prediction is ready less than <time_4> secs
                And I download the created predictions file to "<local_file>"
                Then the batch prediction file is like "<predictions_file>"

                Examples:
                | data             | time_1  | time_2 | time_3 | time_4 | local_file | predictions_file       |
                | ../data/iris.csv | 30      | 30     | 50     | 50     | ./tmp/batch_predictions.csv |./data/batch_predictions.csv |

        """
        print self.test_scenario1.__doc__
        examples = [
            ['data/iris.csv', '30', '30', '50', '50', 'tmp/batch_predictions.csv', 'data/batch_predictions.csv']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_model(self)
            model_create.the_model_is_finished_in_less_than(self, example[3])
            batch_pred_create.i_create_a_batch_prediction(self)
            batch_pred_create.the_batch_prediction_is_finished_in_less_than(self, example[4])
            batch_pred_create.i_download_predictions_file(self, example[5])
            batch_pred_create.i_check_predictions(self, example[6])

    def test_scenario2(self):
        """
            Scenario: Successfully creating a batch prediction for an ensemble:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create an ensemble of <number_of_models> models and <tlp> tlp
                And I wait until the ensemble is ready less than <time_3> secs
                When I create a batch prediction for the dataset with the ensemble and "<params>"
                And I wait until the batch prediction is ready less than <time_4> secs
                And I download the created predictions file to "<local_file>"
                Then the batch prediction file is like "<predictions_file>"

                Examples:
                | data             | time_1  | time_2 | number_of_models | tlp | time_3 | time_4 | local_file | predictions_file       | params
                | ../data/iris.csv | 30      | 30     | 5                | 1   | 80     | 50     | ./tmp/batch_predictions.csv | ./data/batch_predictions_e.csv | {"combiner": 0}


        """
        print self.test_scenario2.__doc__
        examples = [
            ['data/iris.csv', '30', '30', '5', '1', '180', '150', 'tmp/batch_predictions.csv', 'data/batch_predictions_e_c0.csv', {"combiner":0}],
            ['data/iris.csv', '30', '30', '5', '1', '180', '150', 'tmp/batch_predictions.csv', 'data/batch_predictions_e_c1.csv', {"combiner":1, "confidence": True}],
            ['data/iris.csv', '30', '30', '5', '1', '180', '150', 'tmp/batch_predictions.csv', 'data/batch_predictions_e_c2.csv', {"combiner":2, "confidence": True}],
            ['data/iris.csv', '30', '30', '5', '1', '180', '150', 'tmp/batch_predictions.csv', 'data/batch_predictions_e_o_k_v.csv', {"operating_kind": "votes", "confidence": True}],
            ['data/iris.csv', '30', '30', '5', '1', '180', '150', 'tmp/batch_predictions.csv', 'data/batch_predictions_e_o_k_p.csv', {"operating_kind": "probability", "probability": True}],
            ['data/iris.csv', '30', '30', '5', '1', '180', '150', 'tmp/batch_predictions.csv', 'data/batch_predictions_e_o_k_c.csv', {"operating_kind": "confidence", "confidence": True}]]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            ensemble_create.i_create_an_ensemble(self, example[3], example[4])
            ensemble_create.the_ensemble_is_finished_in_less_than(self, example[5])
            batch_pred_create.i_create_a_batch_prediction_ensemble(self, example[9])
            batch_pred_create.the_batch_prediction_is_finished_in_less_than(self, example[6])
            batch_pred_create.i_download_predictions_file(self, example[7])
            batch_pred_create.i_check_predictions(self, example[8])

    def test_scenario3(self):
        """
            Scenario: Successfully creating a batch centroid from a cluster:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a cluster
                And I wait until the cluster is ready less than <time_3> secs
                When I create a batch centroid for the dataset
                And I check the batch centroid is ok
                And I wait until the batch centroid is ready less than <time_4> secs
                And I download the created centroid file to "<local_file>"
                Then the batch centroid file is like "<predictions_file>"

                Examples:
                | data             | time_1  | time_2 | time_3 | time_4 | local_file | predictions_file       |
                | ../data/diabetes.csv | 50      | 50     | 50     | 50     | ./tmp/batch_predictions.csv |./data/batch_predictions_c.csv |


        """
        print self.test_scenario3.__doc__
        examples = [
            ['data/diabetes.csv', '50', '50', '50', '50', 'tmp/batch_predictions.csv', 'data/batch_predictions_c.csv']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            cluster_create.i_create_a_cluster(self)
            cluster_create.the_cluster_is_finished_in_less_than(self, example[3])
            batch_pred_create.i_create_a_batch_prediction_with_cluster(self)
            batch_pred_create.the_batch_centroid_is_finished_in_less_than(self, example[4])
            batch_pred_create.i_download_centroid_file(self, example[5])
            batch_pred_create.i_check_predictions(self, example[6])

    def test_scenario4(self):
        """

            Scenario: Successfully creating a source from a batch prediction:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a model
                And I wait until the model is ready less than <time_3> secs
                When I create a batch prediction for the dataset with the model
                And I wait until the batch prediction is ready less than <time_4> secs
                Then I create a source from the batch prediction
                And I wait until the source is ready less than <time_1> secs

                Examples:
                | data             | time_1  | time_2 | time_3 | time_4 |
                | ../data/iris.csv | 30      | 30     | 50     | 50     |
        """
        print self.test_scenario4.__doc__
        examples = [
            ['data/diabetes.csv', '30', '30', '50', '50']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_model(self)
            model_create.the_model_is_finished_in_less_than(self, example[3])
            batch_pred_create.i_create_a_batch_prediction(self)
            batch_pred_create.the_batch_prediction_is_finished_in_less_than(self, example[4])
            batch_pred_create.i_create_a_source_from_batch_prediction(self)
            source_create.the_source_is_finished(self, example[1])

    def test_scenario5(self):
        """
            Scenario: Successfully creating a batch anomaly score from an anomaly detector:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create an anomaly detector
                And I wait until the anomaly detector is ready less than <time_3> secs
                When I create a batch anomaly score
                And I check the batch anomaly score is ok
                And I wait until the batch anomaly score is ready less than <time_4> secs
                And I download the created anomaly score file to "<local_file>"
                Then the batch anomaly score file is like "<predictions_file>"

                Examples:
                | data             | time_1  | time_2 | time_3 | time_4 | local_file | predictions_file       |
                | ../data/tiny_kdd.csv | 30      | 30     | 50     | 50     | ./tmp/batch_predictions.csv |./data/batch_predictions_a.csv |

        """
        print self.test_scenario5.__doc__
        examples = [
            ['data/tiny_kdd.csv', '30', '30', '50', '50', 'tmp/batch_predictions.csv', 'data/batch_predictions_a.csv']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            anomaly_create.i_create_an_anomaly(self)
            anomaly_create.the_anomaly_is_finished_in_less_than(self, example[3])
            batch_pred_create.i_create_a_batch_prediction_with_anomaly(self)
            batch_pred_create.the_batch_anomaly_score_is_finished_in_less_than(self, example[4])
            batch_pred_create.i_download_anomaly_score_file(self, example[5])
            batch_pred_create.i_check_predictions(self, example[6])

    def test_scenario6(self):
        """
            Scenario: Successfully creating a batch prediction for a logistic regression:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a logistic regression
                And I wait until the logistic regression is ready less than <time_3> secs
                When I create a batch prediction for the dataset with the logistic regression
                And I wait until the batch prediction is ready less than <time_4> secs
                And I download the created predictions file to "<local_file>"
                Then the batch prediction file is like "<predictions_file>"

                Examples:
                | data             | time_1  | time_2 | time_3 | time_4 | local_file | predictions_file       |
                | ../data/iris.csv | 30      | 30     | 80     | 50     | ./tmp/batch_predictions.csv | ./data/batch_predictions_lr.csv |

        """
        print self.test_scenario6.__doc__
        examples = [
            ['data/iris.csv', '30', '30', '80', '50', 'tmp/batch_predictions.csv', 'data/batch_predictions_lr.csv']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_logistic_model(self)
            model_create.the_logistic_model_is_finished_in_less_than(self, example[3])
            batch_pred_create.i_create_a_batch_prediction_logistic_model(self)
            batch_pred_create.the_batch_prediction_is_finished_in_less_than(self, example[4])
            batch_pred_create.i_download_predictions_file(self, example[5])
            batch_pred_create.i_check_predictions(self, example[6])
