# -*- coding: utf-8 -*-
#
# Copyright 2017-2020 BigML
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
from .world import world, setup_module, teardown_module, show_doc
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create
from . import create_model_steps as model_create
from . import create_time_series_steps as time_series_create
from . import create_forecast_steps as forecast_create
from . import compare_forecasts_steps as forecast_compare
from . import create_pca_steps as pca_create
from . import create_projection_steps as projection_create
from . import compare_predictions_steps as compare_predictions


class TestComparePrediction(object):

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
            print("\nTesting with:\n", example)
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
            print("\nTesting with:\n", example)
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
            print("\nTesting with:\n", example)
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
            ['data/grades.csv', '10', '100', '100', '{"000005": {"horizon": 5, "ets_models": {"names": ["naive"]}}}', '{"000005": [{"point_forecast": [61.39, 61.39, 61.39, 61.39, 61.39], "model": "naive"}]}', '{"objective_fields": ["000001", "000005"], "period": 1}'],
            ['data/grades.csv', '10', '100', '100', '{"000005": {"horizon": 5, "ets_models": {"names": ["naive"]}}}', '{"000005": [{"point_forecast": [78.89, 61.39, 78.89, 61.39, 78.89], "model": "naive"}]}', '{"objective_fields": ["000001", "000005"], "period": 2}'],
            ['data/grades.csv', '10', '100', '100', '{"000005": {"horizon": 5, "ets_models": {"names": ["mean"]}}}', '{"000005": [{"point_forecast": [68.45974, 68.45974, 68.45974, 68.45974, 68.45974], "model": "mean"}]}', '{"objective_fields": ["000001", "000005"], "period": 1}'],
            ['data/grades.csv', '10', '100', '100', '{"000005": {"horizon": 5, "ets_models": {"names": ["mean"]}}}', '{"000005": [{"point_forecast": [69.79553, 67.15821, 69.79553, 67.15821, 69.79553], "model": "mean"}]}', '{"objective_fields": ["000001", "000005"], "period": 2}'],
            ['data/grades.csv', '10', '100', '100', '{"000005": {"horizon": 5, "ets_models": {"names": ["drift"]}}}', '{"000005": [{"point_forecast": [61.50545, 61.6209, 61.73635, 61.8518, 61.96725], "model": "drift"}]}', '{"objective_fields": ["000001", "000005"], "period": 1}'],
            ['data/grades.csv', '10', '100', '100', '{"000005": {"horizon": 5, "ets_models": {"names": ["drift"]}}}', '{"000005": [{"point_forecast": [61.50545, 61.6209, 61.73635, 61.8518, 61.96725], "model": "drift"}]}', '{"objective_fields": ["000001", "000005"], "period": 2}']]
        show_doc(self.test_scenario4, examples)

        for example in examples:
            print("\nTesting with:\n", example)
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
             '{"PC2": 0, "PC3": 0, "PC1": 0, "PC6": 0, "PC4": 5e-05, "PC5": 0}', '{}'],
            ['data/iris.csv', '30', '30', '120', '{"petal length": 1}',
             '{"PC2": 0.08708, "PC3": 0.20929, "PC1": 1.56084, "PC6": -1.34463, "PC4": 0.7295, "PC5": -1.00876}', '{}'],
            ['data/iris.csv', '30', '30', '120', '{"species": "Iris-versicolor"}',
             '{"PC2": 1.8602, "PC3": -2.00864, "PC1": -0.61116, "PC6": -0.66983, "PC4": -2.44618, "PC5": 0.43414}', '{}'],
            ['data/iris.csv', '30', '30', '120', '{"petal length": 1, "sepal length": 0, "petal width": 0, "sepal width": 0, "species": "Iris-versicolor"}',
             '{"PC2": 7.18009, "PC3": 6.51511, "PC1": 2.78155, "PC6": 0.21372, "PC4": -1.94865, "PC5": 0.57646}', '{}']]
        show_doc(self.test_scenario5, examples)

        for example in examples:
            print("\nTesting with:\n", example)
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
    ['data/spam_tiny.csv', '30', '30', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"token_mode": "all"}}}}', '{"Message": "early"}', '{}', '{"PC40": 0.00416, "PC38": 0.08267, "PC39": 0.00033, "PC18": 0.28094, "PC19": -0.15056, "PC14": 0.20643, "PC15": 0.23931, "PC16": 0.03251, "PC17": 0.02776, "PC10": 0.1424, "PC11": 0.4059, "PC12": -0.1238, "PC13": 0.15131, "PC43": 0.29617, "PC42": 1.0091, "PC41": 0, "PC25": 0.07164, "PC24": -0.29904, "PC27": -0.1331, "PC26": -0.18572, "PC21": 0.25616, "PC20": 0.30424, "PC23": -0.45775, "PC22": -0.3362, "PC47": -0.13757, "PC49": 0.01864, "PC48": 0.04742, "PC29": -0.16286, "PC28": 0.42207, "PC32": -0.05917, "PC46": -0.05018, "PC31": -0.13973, "PC45": -0.05015, "PC36": 0.03017, "PC44": 0, "PC37": -0.06093, "PC34": 0.25821, "PC35": -0.22194, "PC33": -0.23398, "PC8": 0.01159, "PC9": -0.16042, "PC2": -0.09202, "PC3": 0.14371, "PC1": 0.65114, "PC6": -0.43034, "PC7": -0.02563, "PC4": -0.04947, "PC5": -0.07796, "PC50": -0.00769, "PC30": 0.07813}'],
    ['data/spam_tiny.csv', '30', '30', '30', '{"fields": {"000001": {"optype": "text", "term_analysis": {"token_mode": "all"}}}}', '{"Message": "mobile call"}', '{}', '{"PC40": 0.31818, "PC38": 0.06912, "PC39": -0.14342, "PC18": 0.22382, "PC19": 0.18518, "PC14": 0.89231, "PC15": 0.05046, "PC16": -0.00241, "PC17": 0.54501, "PC10": -0.26463, "PC11": 0.30251, "PC12": 1.16327, "PC13": 0.16973, "PC43": 0.11952, "PC42": 1.05499, "PC41": 0.51263, "PC25": 0.02467, "PC24": -0.65128, "PC27": 0.48916, "PC26": -0.45228, "PC21": -0.44167, "PC20": 0.76896, "PC23": 0.29398, "PC22": 0.06425, "PC47": 0.70416, "PC49": -0.30313, "PC48": 0.12976, "PC29": -0.34, "PC28": 0.17406, "PC32": -0.06411, "PC46": 0.69257, "PC31": 0.07523, "PC45": -0.03461, "PC36": 0.29732, "PC44": 0.14516, "PC37": -0.19109, "PC34": 0.58399, "PC35": 0.37608, "PC33": -0.00378, "PC8": -0.88156, "PC9": 0.38233, "PC2": -0.56685, "PC3": 0.56321, "PC1": 0.49171, "PC6": -0.09854, "PC7": -1.24639, "PC4": 1.50134, "PC5": -0.03161, "PC50": 0.17349, "PC30": -1.29612}']]
        show_doc(self.test_scenario6, examples)
        for example in examples:
            print("\nTesting with:\n", example)
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

    def test_scenario7(self):
        """
            Scenario: Successfully comparing remote and local predictions
                      with raw date input for PCAs:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a PC
                And I wait until the PCA is ready less than <time_3> secs
                And I create a local PCA
                When I create a projection for "<input_data>"
                Then the projection is "<projection>"
                And I create a local projection for "<data_input>"
                Then the local projection is "<projection>"

                Examples:
                | data | time_1  | time_2 | time_3 | input_data | projection


        """
        examples = [
            ['data/dates2.csv', '20', '30', '60',
             '{"time-1":"1910-05-08T19:10:23.106","cat-0":"cat2","target-2":0.4}',
             '{"PC8": -1.54293, "PC9": -0.94836, "PC2": 0.78176, "PC3": -0.62082,\
              "PC1": 0.89614, "PC10": 1.06575, "PC11": 1.3211, "PC4": 1.90088, \
              "PC5": 0.24197, "PC7": -0.37701, "PC6": 2.25007}'],
            ['data/dates2.csv', '20', '30', '60',
             '{"time-1":"1920-06-30T20:21:20.320","cat-0":"cat1","target-2":0.2}',
             '{"PC8": 0.3148, "PC9": -0.61742, "PC2": 0.93411, "PC3": 1.80286,\
               "PC1": 0.36425, "PC10": 0.7364, "PC11": 2.25863, "PC4": -1.50319,\
               "PC5": 0.17088, "PC7": 0.51738, "PC6": 0.42403}'],
            ['data/dates2.csv', '20', '30', '60',
             '{"time-1":"1932-01-30T19:24:11.440","cat-0":"cat2","target-2":0.1}',
             '{"PC8": -0.86728, "PC9": -1.85164, "PC2": 2.13206, "PC3": 0.58449,\
               "PC1": 0.28379, "PC10": 2.05465, "PC11": 0.44372, "PC4": 1.27236,\
               "PC5": 0.99468, "PC7": -0.32496, "PC6": 0.52217}'],
            ['data/dates2.csv', '20', '30', '60',
             '{"time-1":"1950-11-06T05:34:05.602","cat-0":"cat1" ,"target-2":0.9}',
             '{"PC8": 2.49563, "PC9": -0.57774, "PC2": -0.76354, "PC3": 0.19215,\
               "PC1": 0.99197, "PC10": -1.21017, "PC11": 1.55778, "PC4": -0.24013,\
               "PC5": -0.38492, "PC7": 1.82607, "PC6": 0.3736}'],
            ['data/dates2.csv', '20', '30', '60',
             '{"time-1":"1969-7-14 17:36","cat-0":"cat2","target-2":0.9}',
             '{"PC8": -0.41111, "PC9": -5.32959, "PC2": -1.25322, "PC3": 2.93113,\
               "PC1": 2.07444, "PC10": 4.8808, "PC11": 0.4185, "PC4": 3.13876,\
               "PC5": 3.70259, "PC7": 0.55665, "PC6": 5.16873}'],
            ['data/dates2.csv', '20', '30', '60',
             '{"time-1":"2001-01-05T23:04:04.693","cat-0":"cat2","target-2":0.01}',
             '{"PC8": -1.10654, "PC9": -0.34137, "PC2": 1.73362, "PC3": -0.34799,\
               "PC1": 2.32583, "PC10": 0.94566, "PC11": 0.53787, "PC4": 2.77385,\
               "PC5": -0.1017, "PC7": 0.20156, "PC6": -0.44476}'],
            ['data/dates2.csv', '20', '30', '60',
             '{"time-1":"2011-04-01T00:16:45.747","cat-0":"cat2","target-2":0.32}',
             '{"PC8": -0.514, "PC9": 0.38349, "PC2": -0.27037, "PC3": -1.82588,\
               "PC1": 1.05737, "PC10": 0.08607, "PC11": -0.97078, "PC4": 2.10426,\
               "PC5": 1.86843, "PC7": 1.55632, "PC6": 0.42395}'],
            ['data/dates2.csv', '20', '30', '60',
             '{"time-1":"1969-W29-1T17:36:39Z","cat-0":"cat1","target-2":0.87}',
             '{"PC8": 2.05525, "PC9": 1.50754, "PC2": 6.27524, "PC3": 7.74224,\
               "PC1": 5.30354, "PC10": -6.40442, "PC11": 6.90365, "PC4": -1.44431,\
               "PC5": 2.16179, "PC7": 1.35718, "PC6": 5.02426}']]
        show_doc(self.test_scenario7, examples)
        for example in examples:
            print("\nTesting with:\n", example)
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            pca_create.i_create_a_pca(self)
            pca_create.the_pca_is_finished_in_less_than(self, example[3])
            projection_create.i_create_a_projection(self, example[4])
            projection_create.the_projection_is(self, example[5])
            compare_predictions.create_local_pca(self)
            compare_predictions.i_create_a_local_projection(self, example[4])
            compare_predictions.the_local_projection_is(self, example[5])
