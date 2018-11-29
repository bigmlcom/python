# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2017-2018 BigML
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


""" Comparing remote and local predictions

"""
from world import world, setup_module, teardown_module, show_doc
import create_source_steps as source_create
import create_dataset_steps as dataset_create
import create_model_steps as model_create
import create_time_series_steps as time_series_create
import create_forecast_steps as forecast_create
import compare_forecasts_steps as forecast_compare
import create_pca_steps as pca_create
import create_projection_steps as projection_create
import compare_predictions_steps as compare_predictions


class TestComparePrediction(object):

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
            Scenario: Successfully comparing forecasts from time series:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a time series with "<params>"
                And I wait until the time series is ready less than <time_3> secs
                And I create a local time series
                When I create a forecast for "<input_data>"
                Then the forecast is "<forecasts>"
                And I create a local forecast for "<data_input>"
                Then the local forecast is "<forecasts>"

                Examples:
                | data             | time_1  | time_2 | time_3 | input_data  | forecasts | params
            ['data/grades.csv', '10', '10', '120', '{"000005": {"horizon": 5, "ets_models": {"names": ["A,Ad,N"], "criterion": "aic", "limit": 3}}}', '{"000005": [{"point_forecast":  [69.90959, 69.92755, 69.94514, 69.96236, 69.97922], "model": "A,Ad,N"}]}', '{"objective_fields": ["000001", "000005"]}'],


        """
        examples = [
            ['data/grades.csv', '30', '30', '120', '{"000005": {"horizon": 5}}', '{"000005": [{"point_forecast": [73.96192, 74.04106, 74.12029, 74.1996, 74.27899], "model": "M,M,N"}]}', '{"objective_fields": ["000001", "000005"]}'],
            ['data/grades.csv', '30', '30', '120', '{"000005": {"horizon": 5, "ets_models": {"names": ["M,N,N"], "criterion": "aic", "limit": 3}}}', '{"000005": [{"point_forecast":  [68.39832, 68.39832, 68.39832, 68.39832, 68.39832], "model": "M,N,N"}]}', '{"objective_fields": ["000001", "000005"]}'],
            ['data/grades.csv', '30', '30', '120', '{"000005": {"horizon": 5, "ets_models": {"names": ["A,A,N"], "criterion": "aic", "limit": 3}}}', '{"000005": [{"point_forecast": [72.46247, 72.56247, 72.66247, 72.76247, 72.86247], "model": "A,A,N"}]}', '{"objective_fields": ["000001", "000005"]}'],
            ['data/grades.csv', '30', '30', '120', '{"000005": {"horizon": 5}, "000001": {"horizon": 3, "ets_models": {"criterion": "aic", "limit": 2}}}', '{"000005": [{"point_forecast": [73.96192, 74.04106, 74.12029, 74.1996, 74.27899], "model": "M,M,N"}], "000001": [{"point_forecast": [55.51577, 89.69111, 82.04935], "model": "A,N,A"}, {"point_forecast": [56.67419, 91.89657, 84.70017], "model": "A,A,A"}]}', '{"objective_fields": ["000001", "000005"]}']]
        show_doc(self.test_scenario1, examples)

        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            time_series_create.i_create_a_time_series_with_params(self, example[6])
            time_series_create.the_time_series_is_finished_in_less_than(self, example[3])
            time_series_create.create_local_time_series(self)
            forecast_create.i_create_a_forecast(self, example[4])
            forecast_create.the_forecast_is(self, example[5])
            forecast_compare.i_create_a_local_forecast(self, example[4])
            forecast_compare.the_local_forecast_is(self, example[5])


    def test_scenario2(self):
        """
            Scenario: Successfully comparing forecasts from time series with "A" seasonality
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a time series with "<params>"
                And I wait until the time series is ready less than <time_3> secs
                And I create a local time series
                When I create a forecast for "<input_data>"
                Then the forecast is "<forecasts>"
                And I create a local forecast for "<data_input>"
                Then the local forecast is "<forecasts>"

                Examples:
                | data             | time_1  | time_2 | time_3 | input_data  | forecasts | params
            ['data/grades.csv', '10', '10', '120', '{"000005": {"horizon": 5, "ets_models": {"names": ["A,Ad,A"], "criterion": "aic", "limit": 3}}}', '{"000005": [{"point_forecast":[66.16225, 72.17308, 66.65573, 73.09698, 70.51449], "model": "A,Ad,A"}]}', '{"objective_fields": ["000001", "000005"], "period": 12}']
        """
        examples = [

            ['data/grades.csv', '30', '30', '120', '{"000005": {"horizon": 5}}', '{"000005": [{"point_forecast": [73.96192, 74.04106, 74.12029, 74.1996, 74.27899], "model": "M,M,N"}]}', '{"objective_fields": ["000001", "000005"], "period": 12}'],
            ['data/grades.csv', '30', '30', '120', '{"000005": {"horizon": 5, "ets_models": {"names": ["M,N,A"], "criterion": "aic", "limit": 3}}}', '{"000005": [{"point_forecast":  [67.43222, 68.24468, 64.14437, 67.5662, 67.79028], "model": "M,N,A"}]}', '{"objective_fields": ["000001", "000005"], "period": 12}'],
            ['data/grades.csv', '30', '30', '120', '{"000005": {"horizon": 5, "ets_models": {"names": ["A,A,A"], "criterion": "aic", "limit": 3}}}', '{"000005": [{"point_forecast": [74.73553, 71.6163, 71.90264, 76.4249, 75.06982], "model": "A,A,A"}]}', '{"objective_fields": ["000001", "000005"], "period": 12}']]
        show_doc(self.test_scenario2, examples)

        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            time_series_create.i_create_a_time_series_with_params(self, example[6])
            time_series_create.the_time_series_is_finished_in_less_than(self, example[3])
            time_series_create.create_local_time_series(self)
            forecast_create.i_create_a_forecast(self, example[4])
            forecast_create.the_forecast_is(self, example[5])
            forecast_compare.i_create_a_local_forecast(self, example[4])
            forecast_compare.the_local_forecast_is(self, example[5])

    def test_scenario3(self):
        """
            Scenario: Successfully comparing forecasts from time series with "M" seasonality
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a time series with "<params>"
                And I wait until the time series is ready less than <time_3> secs
                And I create a local time series
                When I create a forecast for "<input_data>"
                Then the forecast is "<forecasts>"
                And I create a local forecast for "<data_input>"
                Then the local forecast is "<forecasts>"

                Examples:
                | data             | time_1  | time_2 | time_3 | input_data  | forecasts | params

,
            ['data/grades.csv', '10', '10', '120', '{"000005": {"horizon": 5, "ets_models": {"names": ["M,Ad,M"], "criterion": "aic", "limit": 3}}}', '{"000005": [{"point_forecast": [73.75816, 74.60699, 66.71212, 72.49586, 71.76787], "model": "M,Ad,M"}]}', '{"objective_fields": ["000001", "000005"], "period": 12}'],
            ['data/grades.csv', '10', '10', '120', '{"000005": {"horizon": 5, "ets_models": {"names": ["M,Md,M"], "criterion": "aic", "limit": 3}}}', '{"000005": [{"point_forecast": [74.3725, 75.02963, 67.15826, 73.19628, 71.66919], "model": "M,Md,M"}]}', '{"objective_fields": ["000001", "000005"], "period": 12}']

        """
        examples = [
            ['data/grades.csv', '30', '30', '120', '{"000005": {"horizon": 5, "ets_models": {"names": ["M,N,M"], "criterion": "aic", "limit": 3}}}', '{"000005": [{"point_forecast":  [68.99775, 72.76777, 66.5556, 70.90818, 70.92998], "model": "M,N,M"}]}', '{"objective_fields": ["000001", "000005"], "period": 12}'],
            ['data/grades.csv', '30', '30', '120', '{"000005": {"horizon": 5, "ets_models": {"names": ["M,A,M"], "criterion": "aic", "limit": 3}}}', '{"000005": [{"point_forecast": [70.65993, 78.20652, 69.64806, 75.43716, 78.13556], "model": "M,A,M"}]}', '{"objective_fields": ["000001", "000005"], "period": 12}'],
            ['data/grades.csv', '30', '30', '120', '{"000005": {"horizon": 5, "ets_models": {"names": ["M,M,M"], "criterion": "aic", "limit": 3}}}', '{"000005": [{"point_forecast": [71.75055, 80.67195, 70.81368, 79.84999, 78.27634], "model": "M,M,M"}]}', '{"objective_fields": ["000001", "000005"], "period": 12}']]
        show_doc(self.test_scenario3, examples)

        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            time_series_create.i_create_a_time_series_with_params(self, example[6])
            time_series_create.the_time_series_is_finished_in_less_than(self, example[3])
            time_series_create.create_local_time_series(self)
            forecast_create.i_create_a_forecast(self, example[4])
            forecast_create.the_forecast_is(self, example[5])
            forecast_compare.i_create_a_local_forecast(self, example[4])
            forecast_compare.the_local_forecast_is(self, example[5])


    def test_scenario4(self):
        """
            Scenario: Successfully comparing forecasts from time series with trivial models
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a time series with "<params>"
                And I wait until the time series is ready less than <time_3> secs
                And I create a local time series
                When I create a forecast for "<input_data>"
                Then the forecast is "<forecasts>"
                And I create a local forecast for "<data_input>"
                Then the local forecast is "<forecasts>"

                Examples:
                | data             | time_1  | time_2 | time_3 | input_data  | forecasts | params

        """
        examples = [
            ['data/grades.csv', '10', '1000', '1000', '{"000005": {"horizon": 5, "ets_models": {"names": ["naive"]}}}', '{"000005": [{"point_forecast": [61.39, 61.39, 61.39, 61.39, 61.39], "model": "naive"}]}', '{"objective_fields": ["000001", "000005"], "period": 1}'],
            ['data/grades.csv', '10', '1000', '1000', '{"000005": {"horizon": 5, "ets_models": {"names": ["naive"]}}}', '{"000005": [{"point_forecast": [78.89, 61.39, 78.89, 61.39, 78.89], "model": "naive"}]}', '{"objective_fields": ["000001", "000005"], "period": 2}'],
            ['data/grades.csv', '10', '1000', '1000', '{"000005": {"horizon": 5, "ets_models": {"names": ["mean"]}}}', '{"000005": [{"point_forecast": [68.45974, 68.45974, 68.45974, 68.45974, 68.45974], "model": "mean"}]}', '{"objective_fields": ["000001", "000005"], "period": 1}'],
            ['data/grades.csv', '10', '1000', '1000', '{"000005": {"horizon": 5, "ets_models": {"names": ["mean"]}}}', '{"000005": [{"point_forecast": [69.79553, 67.15821, 69.79553, 67.15821, 69.79553], "model": "mean"}]}', '{"objective_fields": ["000001", "000005"], "period": 2}'],
            ['data/grades.csv', '10', '1000', '1000', '{"000005": {"horizon": 5, "ets_models": {"names": ["drift"]}}}', '{"000005": [{"point_forecast": [61.50545, 61.6209, 61.73635, 61.8518, 61.96725], "model": "drift"}]}', '{"objective_fields": ["000001", "000005"], "period": 1}'],
            ['data/grades.csv', '10', '1000', '1000', '{"000005": {"horizon": 5, "ets_models": {"names": ["drift"]}}}', '{"000005": [{"point_forecast": [61.50545, 61.6209, 61.73635, 61.8518, 61.96725], "model": "drift"}]}', '{"objective_fields": ["000001", "000005"], "period": 2}']]
        show_doc(self.test_scenario4, examples)

        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            time_series_create.i_create_a_time_series_with_params(self, example[6])
            time_series_create.the_time_series_is_finished_in_less_than(self, example[3])
            time_series_create.create_local_time_series(self)
            forecast_create.i_create_a_forecast(self, example[4])
            forecast_create.the_forecast_is(self, example[5])
            forecast_compare.i_create_a_local_forecast(self, example[4])
            forecast_compare.the_local_forecast_is(self, example[5])


    def test_scenario5(self):
        """
            Scenario: Successfully comparing projections for PCAs:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a PCA with "<params>"
                And I wait until the PCA is ready less than <time_3> secs
                And I create a local PCA
                When I create a projection for "<input_data>"
                Then the projection is "<projection>"
                And I create a local projection for "<data_input>"
                Then the local projection is "<projection>"

                Examples:
                | data             | time_1  | time_2 | time_3 | input_data  | projection | params


        """
        examples = [
            ['data/iris.csv', '30', '30', '120', '{}',
             '{"PC2": 0, "PC3": 1e-05, "PC1": 2e-05, "PC6": 0, "PC4": 0, "PC5": -2e-05}', '{}'],
            ['data/iris.csv', '30', '30', '120', '{"petal length": 1}',
             '{"PC2": 0.10109, "PC3": 0.16123, "PC1": 3.07314, "PC6": -0.1652, "PC4": 0.28663, "PC5": -0.16477}', '{}'],
            ['data/iris.csv', '30', '30', '120', '{"species": "Iris-versicolor"}',
             '{"PC2": 2.15914, "PC3": -1.54734, "PC1": -1.20336, "PC6": -0.08233, "PC4": -0.96098, "PC5": 0.07091}', '{}'],
            ['data/iris.csv', '30', '30', '120', '{"petal length": 1, "sepal length": 0, "petal width": 0, "sepal width": 0, "species": "Iris-versicolor"}',
             '{"PC2": 8.33399, "PC3": 5.01889, "PC1": 5.47656, "PC6": 0.02629, "PC4": -0.76555, "PC5": 0.09413}', '{}']]
        show_doc(self.test_scenario5, examples)

        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            pca_create.i_create_a_pca_with_params(self, example[6])
            pca_create.the_pca_is_finished_in_less_than(self, example[3])
            compare_predictions.create_local_pca(self)
            projection_create.i_create_a_projection(self, example[4])
            projection_create.the_projection_is(self, example[5])
            compare_predictions.i_create_a_local_projection(self, example[4])
            compare_predictions.the_local_projection_is(self, example[5])



    def test_scenario6(self):
        """
            Scenario: Successfully comparing projections for PCAs:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a PCA with "<params>"
                And I wait until the PCA is ready less than <time_3> secs
                And I create a local PCA
                When I create a projection for "<input_data>"
                Then the projection is "<projection>"
                And I create a local projection for "<data_input>"
                Then the local projection is "<projection>"

                Examples:
                | data             | time_1  | time_2 | time_3 | input_data  | projection | params


        """
        examples = [
    ['data/spam_tiny.csv', '30', '30', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"token_mode": "all"}}}}', '{"Message": "early"}', '{}', '{"PC40": 0.0, "PC38": 0.01197, "PC39": -1e-05, "PC18": 0.30635, "PC19": 0.15681, "PC14": -0.24903, "PC15": 0.2853, "PC16": 0.03769, "PC17": 0.03074, "PC10": 0.20212, "PC11": 0.55543, "PC12": -0.15796, "PC13": 0.186, "PC43": 0.0, "PC42": 0.0, "PC41": 0.0, "PC25": 0.05249, "PC24": -0.2261, "PC27": -0.08064, "PC26": -0.12261, "PC21": -0.23743, "PC20": 0.29411, "PC23": -0.35753, "PC22": 0.29116, "PC47": 0.0, "PC49": 0.0, "PC48": 0.0, "PC29": -0.0918, "PC28": 0.24181, "PC32": 0.02223, "PC46": 0.0, "PC31": -0.06144, "PC45": 0.0, "PC36": 0.00743, "PC44": 0.0, "PC37": -0.01394, "PC34": 0.09211, "PC35": 0.07081, "PC33": -0.08747, "PC8": 0.01767, "PC9": -0.24043, "PC2": -0.17494, "PC3": -0.26523, "PC1": 1.6119, "PC6": -0.67905, "PC7": -0.0393, "PC4": -0.08702, "PC5": -0.13242, "PC50": 0.0, "PC30": 0.03738}'],
    ['data/spam_tiny.csv', '30', '30', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"token_mode": "all"}}}}', '{"Message": "mobile call"}', '{}', '{"PC40": 0.0, "PC38": 0.01001, "PC39": 2e-05, "PC18": 0.2441, "PC19": -0.19299, "PC14": -1.0761, "PC15": 0.05998, "PC16": -0.003, "PC17": 0.60312, "PC10": -0.3755, "PC11": 0.414, "PC12": 1.484, "PC13": 0.20872, "PC43": 0.0, "PC42": 0.0, "PC41": 0.0, "PC25": 0.01801, "PC24": -0.49236, "PC27": 0.2963, "PC26": -0.29859, "PC21": 0.4093, "PC20": 0.74333, "PC23": 0.22959, "PC22": -0.05565, "PC47": 0.0, "PC49": 0.0, "PC48": 0.0, "PC29": -0.19166, "PC28": 0.09974, "PC32": 0.02409, "PC46": 0.0, "PC31": 0.03303, "PC45": 0.0, "PC36": 0.07305, "PC44": 0.0, "PC37": -0.04376, "PC34": 0.20832, "PC35": -0.11997, "PC33": -0.00143, "PC8": -1.3324, "PC9": 0.57226, "PC2": -1.07758, "PC3": -1.03979, "PC1": 1.21728, "PC6": -0.15558, "PC7": -1.91064, "PC4": 2.64089, "PC5": -0.05378, "PC50": 0.0, "PC30": -0.62013}']]
        show_doc(self.test_scenario6, examples)
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            source_create.i_update_source_with(self, example[4])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            pca_create.i_create_a_pca_with_params(self, example[6])
            pca_create.the_pca_is_finished_in_less_than(self, example[3])
            projection_create.i_create_a_projection(self, example[5])
            projection_create.the_projection_is(self, example[7])
            compare_predictions.create_local_pca(self)
            compare_predictions.i_create_a_local_projection(self, example[5])
            compare_predictions.the_local_projection_is(self, example[7])
