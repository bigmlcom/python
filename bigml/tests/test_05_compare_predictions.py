# -*- coding: utf-8 -*-
#
# Copyright 2015-2021 BigML
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
import sys
from .world import world, setup_module, teardown_module, show_doc, show_method
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create
from . import create_model_steps as model_create
from . import create_association_steps as association_create
from . import create_cluster_steps as cluster_create
from . import create_anomaly_steps as anomaly_create
from . import create_prediction_steps as prediction_create
from . import compare_predictions_steps as prediction_compare
from . import create_lda_steps as topic_create


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
            Scenario 1: Successfully comparing predictions:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a model
                And I wait until the model is ready less than <model_wait> secs
                And I create a local model
                When I create a prediction for "<input_data>"
                Then the prediction for "<objective>" is "<prediction>"
                And I create a local prediction for "<input_data>"
                Then the local prediction is "<prediction>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "input_data", "objective_id", "prediction"]
        examples = [
            ['data/iris.csv', '10', '10', '10', '{"petal width": 0.5}',
             '000004', 'Iris-setosa'],
            ['data/iris.csv', '10', '10', '10',
             '{"petal length": 6, "petal width": 2}', '000004',
             'Iris-virginica'],
            ['data/iris.csv', '10', '10', '10',
             '{"petal length": 4, "petal width": 1.5}', '000004',
             'Iris-versicolor'],
            ['data/iris_sp_chars.csv', '10', '10', '10',
             '{"pétal.length": 4, "pétal&width\\u0000": 1.5}', '000004',
             'Iris-versicolor']]
        show_doc(self.test_scenario1)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(self, example["data"],
                shared=example["data"])
            source_create.the_source_is_finished(self, example["source_wait"],
                shared=example["data"])
            dataset_create.i_create_a_dataset(self, shared=example["data"])
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"], shared=example["data"])
            model_create.i_create_a_model(self, shared=example["data"])
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"], shared=example["data"])
            prediction_compare.i_create_a_local_model(self)
            prediction_create.i_create_a_prediction(
                self, example["input_data"])
            prediction_create.the_prediction_is(
                self, example["objective_id"], example["prediction"])
            prediction_compare.i_create_a_local_prediction(
                self, example["input_data"])
            prediction_compare.the_local_prediction_is(
                self, example["prediction"])

    def test_scenario2(self):
        """
            Scenario 2: Successfully comparing predictions with text options:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I update the source with params "<source_conf>"
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a model
                And I wait until the model is ready less than <model_wait> secs
                And I create a local model
                When I create a prediction for "<input_data>"
                Then the prediction for "<objective>" is "<prediction>"
                And I create a local prediction for "<input_data>"
                Then the local prediction is "<prediction>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "source_conf", "input_data", "objective_id", "prediction"]
        examples = [
            ['data/spam.csv', '20', '20', '30',
             '{"fields": {"000001": {"optype": "text", "term_analysis": '
             '{"case_sensitive": true, "stem_words": true, '
             '"use_stopwords": false, "language": "en"}}}}',
             '{"Message": "Mobile call"}', '000000', 'spam'],
            ['data/spam.csv', '20', '20', '30',
             '{"fields": {"000001": {"optype": "text", "term_analysis": '
             '{"case_sensitive": true, "stem_words": true, '
             '"use_stopwords": false, "language": "en"}}}}',
             '{"Message": "A normal message"}', '000000', 'ham'],
            ['data/spam.csv', '20', '20', '30',
             '{"fields": {"000001": {"optype": "text", "term_analysis": '
             '{"case_sensitive": false, "stem_words": false, '
             '"use_stopwords": false, "language": "en"}}}}',
             '{"Message": "Mobile calls"}', '000000', 'spam'],
            ['data/spam.csv', '20', '20', '30',
             '{"fields": {"000001": {"optype": "text", "term_analysis": '
             '{"case_sensitive": false, "stem_words": false, '
             '"use_stopwords": false, "language": "en"}}}}',
             '{"Message": "A normal message"}', '000000', 'ham'],
            ['data/spam.csv', '20', '20', '30',
             '{"fields": {"000001": {"optype": "text", "term_analysis": '
             '{"case_sensitive": false, "stem_words": true, '
             '"use_stopwords": true, "language": "en"}}}}',
             '{"Message": "Mobile call"}', '000000', 'spam'],
            ['data/spam.csv', '20', '20', '30',
             '{"fields": {"000001": {"optype": "text", "term_analysis": '
             '{"case_sensitive": false, "stem_words": true, '
             '"use_stopwords": true, "language": "en"}}}}',
             '{"Message": "A normal message"}', '000000', 'ham'],
            ['data/spam.csv', '20', '20', '30',
             '{"fields": {"000001": {"optype": "text", "term_analysis": '
             '{"token_mode": "full_terms_only", "language": "en"}}}}',
             '{"Message": "FREE for 1st week! No1 Nokia tone 4 ur mob every '
             'week just txt NOKIA to 87077 Get txting and tell ur mates. zed '
             'POBox 36504 W45WQ norm150p/tone 16+"}', '000000', 'spam'],
            ['data/spam.csv', '20', '20', '30',
             '{"fields": {"000001": {"optype": "text", "term_analysis": '
             '{"token_mode": "full_terms_only", "language": "en"}}}}',
             '{"Message": "Ok"}', '000000', 'ham'],
            ['data/movies.csv', '20', '20', '30',
             '{"fields": {"000007": {"optype": "items", "item_analysis": '
             '{"separator": "$"}}}}', '{"genres": "Adventure$Action", '
             '"timestamp": 993906291, "occupation": "K-12 student"}',
             '000009', '3.92135'],
            ['data/text_missing.csv', '20', '20', '30',
             '{"fields": {"000001": {"optype": "text", "term_analysis": '
             '{"token_mode": "all", "language": "en"}}, "000000": {"optype": '
             '"text", "term_analysis": {"token_mode": "all", '
             '"language": "en"}}}}', '{}', "000003", 'swap']]
        show_doc(self.test_scenario2)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(self, example["data"])
            source_create.the_source_is_finished(self, example["source_wait"])
            source_create.i_update_source_with(self, example["source_conf"])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"])
            model_create.i_create_a_model(self)
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            prediction_compare.i_create_a_local_model(self)
            prediction_create.i_create_a_prediction(
                self, example["input_data"])
            prediction_create.the_prediction_is(
                self, example["objective_id"], example["prediction"])
            prediction_compare.i_create_a_local_prediction(
                self, example["input_data"])
            prediction_compare.the_local_prediction_is(
                self, example["prediction"])


    def test_scenario3(self):
        """
            Scenario 3: Successfully comparing predictions with proportional missing strategy:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a model
                And I wait until the model is ready less than <model_wait> secs
                And I create a local model
                When I create a proportional missing strategy prediction for "<input_data>"
                Then the prediction for "<objective_id>" is "<prediction>"
                And the confidence for the prediction is "<confidence>"
                And I create a proportional missing strategy local prediction for "<input_data>"
                Then the local prediction is "<prediction>"
                And the local prediction's confidence is "<confidence>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "input_data", "objective_id", "prediction", "confidence"]
        examples = [
            ['data/iris.csv', '50', '30', '30', '{}', '000004', 'Iris-setosa',
             '0.2629'],
            ['data/grades.csv', '50', '30', '30', '{}', '000005', '68.62224',
             '27.5358'],
            ['data/grades.csv', '50', '30', '30', '{"Midterm": 20}', '000005',
             '40.46667', '54.89713'],
            ['data/grades.csv', '50', '30', '30',
             '{"Midterm": 20, "Tutorial": 90, "TakeHome": 100}', '000005',
             '28.06', '25.65806']]
        show_doc(self.test_scenario3)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            dataset_create.i_create_a_dataset(self, shared=example["data"])
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"], shared=example["data"])
            model_create.i_create_a_model(self, shared=example["data"])
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"], shared=example["data"])
            prediction_compare.i_create_a_local_model(self)
            prediction_create.i_create_a_proportional_prediction(
                self, example["input_data"])
            prediction_create.the_prediction_is(
                self, example["objective_id"], example["prediction"])
            prediction_create.the_confidence_is(self, example["confidence"])
            prediction_compare.i_create_a_proportional_local_prediction(
                self, example["input_data"])
            prediction_compare.the_local_prediction_is(
                self, example["prediction"])
            prediction_compare.the_local_prediction_confidence_is(
                self, example["confidence"])

    def test_scenario4(self):
        """
            Scenario 4: Successfully comparing predictions with proportional missing strategy for missing_splits models:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a model with missing splits
                And I wait until the model is ready less than <model_wait> secs
                And I create a local model
                When I create a proportional missing strategy prediction for "<input_data>"
                Then the prediction for "<objective>" is "<prediction>"
                And the confidence for the prediction is "<confidence>"
                And I create a proportional missing strategy local prediction for "<input_data>"
                Then the local prediction is "<prediction>"
                And the local prediction's confidence is "<confidence>"
                And the highest local prediction's confidence is "<confidence>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "input_data", "objective_id", "prediction", "confidence"]
        examples = [
            ['data/iris_missing2.csv', '10', '10', '10',
             '{"petal width": 1}', '000004', 'Iris-setosa', '0.8064'],
            ['data/iris_missing2.csv', '10', '10', '10',
             '{"petal width": 1, "petal length": 4}', '000004',
             'Iris-versicolor', '0.7847'],
            ['data/missings_reg.csv', '10', '10', '10', '{"x2": 4}',
             '000002', '1.33333', '1.62547']
]
        show_doc(self.test_scenario4)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            dataset_create.i_create_a_dataset(self, shared=example["data"])
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"], shared=example["data"])
            model_create.i_create_a_model_with_missing_splits(self)
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            prediction_compare.i_create_a_local_model(self)
            prediction_create.i_create_a_proportional_prediction(
                self, example["input_data"])
            prediction_create.the_prediction_is(
                self, example["objective_id"], example["prediction"])
            prediction_create.the_confidence_is(self, example["confidence"])
            prediction_compare.i_create_a_proportional_local_prediction(
                self, example["input_data"])
            prediction_compare.the_local_prediction_is(
                self, example["prediction"])
            prediction_compare.the_local_prediction_confidence_is(
                self, example["confidence"])
            prediction_compare.the_highest_local_prediction_confidence_is(
                self, example["input_data"], example["confidence"])

    def test_scenario5(self):
        """
            Scenario 5: Successfully comparing logistic regression predictions:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a logistic regression model
                And I wait until the logistic regression model is ready less than <model_wait> secs
                And I create a local logistic regression model
                When I create a logistic regression prediction for "<input_data>"
                Then the logistic regression prediction is "<prediction>"
                And I create a local logistic regression prediction for "<input_data>"
                Then the local logistic regression prediction is "<prediction>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "input_data", "prediction"]
        examples = [
            ['data/iris.csv', '10', '10', '50',
             '{"petal width": 0.5, "petal length": 0.5, "sepal width": 0.5, '
             '"sepal length": 0.5}', 'Iris-versicolor'],
            ['data/iris.csv', '10', '10', '50',
             '{"petal width": 2, "petal length": 6, "sepal width": 0.5, '
             '"sepal length": 0.5}', 'Iris-versicolor'],
            ['data/iris.csv', '10', '10', '50',
             '{"petal width": 1.5, "petal length": 4, "sepal width": 0.5, '
             '"sepal length": 0.5}', 'Iris-versicolor'],
            ['data/iris.csv', '10', '10', '50',
             '{"petal length": 1}', 'Iris-setosa'],
            ['data/iris_sp_chars.csv', '10', '10', '50',
             '{"pétal.length": 4, "pétal&width\\u0000": 1.5, "sépal&width": '
             '0.5, "sépal.length": 0.5}', 'Iris-versicolor'],
            ['data/price.csv', '10', '10', '50', '{"Price": 1200}',
             'Product1']]
        show_doc(self.test_scenario5)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            dataset_create.i_create_a_dataset(self, shared=example["data"])
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"], shared=example["data"])
            model_create.i_create_a_logistic_model(
                self, shared=example["data"])
            model_create.the_logistic_model_is_finished_in_less_than(
                self, example["model_wait"], shared=example["data"])
            prediction_compare.i_create_a_local_logistic_model(self)
            prediction_create.i_create_a_logistic_prediction(
                self, example["input_data"])
            prediction_create.the_logistic_prediction_is(
                self, example["prediction"])
            prediction_compare.i_create_a_local_prediction(
                self, example["input_data"])
            prediction_compare.the_local_prediction_is(
                self, example["prediction"])


    def test_scenario6(self):
        """
            Scenario 6: Successfully comparing predictions with text options:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I update the source with params "<source_conf>"
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a logistic regression model
                And I wait until the logistic regression model is ready less than <model_wait> secs
                And I create a local logistic regression model
                When I create a logistic regression prediction for "<input_data>"
                Then the logistic regression prediction is "<prediction>"
                And I create a local logistic regression prediction for "<input_data>"
                Then the local logistic regression prediction is "<prediction>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "source_conf", "input_data", "prediction"]
        examples = [
            ['data/spam.csv', '20', '20', '30',
             '{"fields": {"000001": {"optype": "text", "term_analysis": '
             '{"case_sensitive": true, "stem_words": true, '
             '"use_stopwords": false, "language": "en"}}}}',
             '{"Message": "Mobile call"}', 'ham'],
            ['data/spam.csv', '20', '20', '30',
             '{"fields": {"000001": {"optype": "text", "term_analysis": '
             '{"case_sensitive": true, "stem_words": true, '
             '"use_stopwords": false, "language": "en"}}}}',
             '{"Message": "A normal message"}', 'ham'],
            ['data/spam.csv', '20', '20', '30',
             '{"fields": {"000001": {"optype": "text", "term_analysis": '
             '{"case_sensitive": false, "stem_words": false, '
             '"use_stopwords": false, "language": "en"}}}}',
             '{"Message": "Mobile calls"}', 'ham'],
            ['data/spam.csv', '20', '20', '30',
             '{"fields": {"000001": {"optype": "text", "term_analysis": '
             '{"case_sensitive": false, "stem_words": false, '
             '"use_stopwords": false, "language": "en"}}}}',
             '{"Message": "A normal message"}', 'ham'],
            ['data/spam.csv', '20', '20', '30',
             '{"fields": {"000001": {"optype": "text", "term_analysis": '
             '{"case_sensitive": false, "stem_words": true, '
             '"use_stopwords": true, "language": "en"}}}}',
             '{"Message": "Mobile call"}', 'ham'],
            ['data/spam.csv', '20', '20', '30',
             '{"fields": {"000001": {"optype": "text", "term_analysis": '
             '{"case_sensitive": false, "stem_words": true, '
             '"use_stopwords": true, "language": "en"}}}}',
             '{"Message": "A normal message"}', 'ham'],
            ['data/spam.csv', '20', '20', '30',
             '{"fields": {"000001": {"optype": "text", "term_analysis": '
             '{"token_mode": "full_terms_only", "language": "en"}}}}',
             '{"Message": "FREE for 1st week! No1 Nokia tone 4 ur mob every '
             'week just txt NOKIA to 87077 Get txting and tell ur mates. zed '
             'POBox 36504 W45WQ norm150p/tone 16+"}', 'ham'],
            ['data/spam.csv', '20', '20', '30',
             '{"fields": {"000001": {"optype": "text", "term_analysis": '
             '{"token_mode": "full_terms_only", "language": "en"}}}}',
             '{"Message": "Ok"}', 'ham']]
        show_doc(self.test_scenario6)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(self, example["data"])
            source_create.the_source_is_finished(self, example["source_wait"])
            source_create.i_update_source_with(self, example["source_conf"])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"])
            model_create.i_create_a_logistic_model(self)
            model_create.the_logistic_model_is_finished_in_less_than(
                self, example["model_wait"])
            prediction_compare.i_create_a_local_logistic_model(self)
            prediction_create.i_create_a_logistic_prediction(
                self, example["input_data"])
            prediction_create.the_logistic_prediction_is(
                self, example["prediction"])
            prediction_compare.i_create_a_local_prediction(
                self, example["input_data"])
            prediction_compare.the_local_prediction_is(
                self, example["prediction"])


    def test_scenario7(self):
        """
            Scenario 7: Successfully comparing predictions with text options and proportional missing strategy:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I update the source with params "<source_conf>"
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a model
                And I wait until the model is ready less than <model_wait> secs
                And I create a local model
                When I create a proportional missing strategy prediction for "<input_data>"
                Then the prediction for "<objective_id>" is "<prediction>"
                And I create a proportional missing strategy local prediction for "<input_data>"
                Then the local prediction is "<prediction>"
        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "source_conf", "input_data", "objective_id", "prediction"]
        examples = [
            ['data/text_missing.csv', '20', '20', '30',
             '{"fields": {"000001": {"optype": "text", "term_analysis": '
             '{"token_mode": "all", "language": "en"}}, "000000": {"optype": '
             '"text", "term_analysis": {"token_mode": "all", '
             '"language": "en"}}}}', '{}', "000003",'swap'],
            ['data/text_missing.csv', '20', '20', '30',
             '{"fields": {"000001": {"optype": "text", "term_analysis": '
             '{"token_mode": "all", "language": "en"}}, "000000": {"optype": '
             '"text", "term_analysis": {"token_mode": "all", '
             '"language": "en"}}}}', '{"category1": "a"}', "000003",
             'paperwork']]
        show_doc(self.test_scenario7)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(self, example["data"])
            source_create.the_source_is_finished(self, example["source_wait"])
            source_create.i_update_source_with(self, example["source_conf"])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"])
            model_create.i_create_a_model(self)
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            prediction_compare.i_create_a_local_model(self)
            prediction_create.i_create_a_proportional_prediction(
                self, example["input_data"])
            prediction_create.the_prediction_is(
                self, example["objective_id"], example["prediction"])
            prediction_compare.i_create_a_proportional_local_prediction(
                self, example["input_data"])
            prediction_compare.the_local_prediction_is(
                self, example["prediction"])


    def test_scenario8(self):
        """
            Scenario 8: Successfully comparing predictions with text options:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I update the source with params "<source_conf>"
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a logistic regression model with objective "<objective_id>" and parms "<model_conf>"
                And I wait until the logistic regression model is ready less than <model_wait> secs
                And I create a local logistic regression model
                When I create a logistic regression prediction for "<input_data>"
                Then the logistic regression prediction is "<prediction>"
                And the logistic regression probability for the prediction is "<probability>"
                And I create a local logistic regression prediction for "<input_data>"
                Then the local logistic regression prediction is "<prediction>"
                And the local logistic regression probability for the prediction is "<probability>"

        """
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "source_conf", "input_data", "prediction", "probability",
                   "objective_id", "model_conf"]
        examples = [
            ['data/iris.csv', '20', '20', '130',
             '{"fields": {"000000": {"optype": "categorical"}}}',
             '{"species": "Iris-setosa"}', '5.0', 0.0394, "000000",
             '{"field_codings": [{"field": "species", "coding": "dummy", '
             '"dummy_class": "Iris-setosa"}]}'],
            ['data/iris.csv', '20', '20', '130', '{"fields": {"000000": '
            '{"optype": "categorical"}}}', '{"species": "Iris-setosa"}',
            '5.0', 0.051, "000000", '{"balance_fields": false, '
            '"field_codings": [{"field": "species", "coding": "contrast", '
            '"coefficients": [[1, 2, -1, -2]]}]}'],
            ['data/iris.csv', '20', '20', '130',
             '{"fields": {"000000": {"optype": "categorical"}}}',
             '{"species": "Iris-setosa"}', '5.0', 0.051, "000000",
             '{"balance_fields": false, "field_codings": [{"field": "species",'
             ' "coding": "other", "coefficients": [[1, 2, -1, -2]]}]}'],
            ['data/iris.csv', '20', '20', '130',
             '{"fields": {"000000": {"optype": "categorical"}}}',
             '{"species": "Iris-setosa"}', '5.0', 0.0417, "000000",
             '{"bias": false}']]
        show_doc(self.test_scenario8)
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            source_create.i_upload_a_file(self, example["data"])
            source_create.the_source_is_finished(self, example["source_wait"])
            source_create.i_update_source_with(self, example["source_conf"])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(
                self, example["dataset_wait"])
            model_create.i_create_a_logistic_model_with_objective_and_parms(
                self, example["objective_id"], example["model_conf"])
            model_create.the_logistic_model_is_finished_in_less_than(
                self, example["model_wait"])
            prediction_compare.i_create_a_local_logistic_model(self)
            prediction_create.i_create_a_logistic_prediction(
                self, example["input_data"])
            prediction_create.the_logistic_prediction_is(
                self, example["prediction"])
            prediction_create.the_logistic_probability_is(
                self, example["probability"])
            prediction_compare.i_create_a_local_prediction(
                self, example["input_data"])
            prediction_compare.the_local_prediction_is(
                self, example["prediction"])
            prediction_compare.the_local_probability_is(
                self, example["probability"])
