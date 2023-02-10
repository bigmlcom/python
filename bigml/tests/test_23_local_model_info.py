# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,line-too-long,attribute-defined-outside-init
#pylint: disable=locally-disabled,unused-import
#
# Copyright 2015-2023 BigML
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


""" Testing local model information output methods

"""
from .world import world, setup_module, teardown_module, show_doc, \
    show_method
from . import create_source_steps as source_create
from . import create_dataset_steps as dataset_create
from . import create_model_steps as model_create
from . import compare_predictions_steps as prediction_compare
from . import inspect_model_steps as inspect_model

class TestLocalModelOutputs:
    """Testing local model code generators"""

    def setup_method(self, method):
        """
            Debug information
        """
        self.bigml = {}
        self.bigml["method"] = method.__name__
        print("\n-------------------\nTests in: %s\n" % __name__)

    def teardown_method(self):
        """
            Debug information
        """
        print("\nEnd of tests in: %s\n-------------------\n" % __name__)
        self.bigml = {}

    def test_scenario1(self):
        """
            Scenario: Successfully creating a model and translate the tree model into a set of IF-THEN rules:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a model
                And I wait until the model is ready less than <model_wait> secs
                And I create a local model
                And I translate the tree into IF_THEN rules
                Then I check the output is like "<output_file>" expected file
        """
        show_doc(self.test_scenario1)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "output_file"]
        examples = [
            ['data/iris.csv', '30', '30', '30',
             'data/model/if_then_rules_iris.txt'],
            ['data/iris_sp_chars.csv', '30', '30', '30',
             'data/model/if_then_rules_iris_sp_chars.txt'],
            ['data/spam.csv', '30', '30', '30',
             'data/model/if_then_rules_spam.txt'],
            ['data/grades.csv', '30', '30', '30',
             'data/model/if_then_rules_grades.txt'],
            ['data/diabetes.csv', '30', '30', '30',
             'data/model/if_then_rules_diabetes.txt'],
            ['data/iris_missing2.csv', '30', '30', '30',
             'data/model/if_then_rules_iris_missing2.txt'],
            ['data/tiny_kdd.csv', '30', '30', '30',
             'data/model/if_then_rules_tiny_kdd.txt']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(self, example["source_wait"],
                shared=example["data"])
            dataset_create.i_create_a_dataset(self, shared=example["data"])
            dataset_create.the_dataset_is_finished_in_less_than(self,
                example["dataset_wait"], shared=example["data"])
            model_create.i_create_a_model(self, shared=example["data"])
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"], shared=example["data"])
            prediction_compare.i_create_a_local_model(self)
            inspect_model.i_translate_the_tree_into_IF_THEN_rules(self)
            inspect_model.i_check_if_the_output_is_like_expected_file(
                self, example["output_file"])

    def test_scenario2(self):
        """
            Scenario: Successfully creating a model with missing values and translate the tree model into a set of IF-THEN rules:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a model
                And I wait until the model is ready less than <model_wait> secs
                And I create a local model
                And I translate the tree into IF_THEN rules
                Then I check the output is like "<output_file>" expected file
        """
        show_doc(self.test_scenario2)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "output_file"]
        examples = [
            ['data/iris_missing2.csv', '10', '10', '30', 'data/model/if_then_rules_iris_missing2_MISSINGS.txt']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            dataset_create.i_create_a_dataset(
                self, shared=example["data"])
            dataset_create.the_dataset_is_finished_in_less_than(self,
                example["dataset_wait"], shared=example["data"])
            model_create.i_create_a_model_with_missing_splits(self)
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            prediction_compare.i_create_a_local_model(self)
            inspect_model.i_translate_the_tree_into_IF_THEN_rules(self)
            inspect_model.i_check_if_the_output_is_like_expected_file(
                self, example["output_file"])

    def test_scenario3(self):
        """
            Scenario: Successfully creating a model and translate the tree model into a set of IF-THEN rules:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I update the source with "<source_conf>" waiting less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a model
                And I wait until the model is ready less than <model_wait> secs
                And I create a local model
                And I translate the tree into IF_THEN rules
                Then I check the output is like "<output_file>" expected file
        """
        show_doc(self.test_scenario3)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "source_conf", "output_file"]
        examples = [
            ['data/spam.csv', '30', '30', '30',
             '{"fields": {"000001": {"optype": "text", "term_analysis": '
             '{"case_sensitive": true, "stem_words": true, "use_stopwords": '
             'false, "language": "en"}}}}',
             'data/model/if_then_rules_spam_textanalysis_1.txt'],
            ['data/spam.csv', '30', '30', '30',
             '{"fields": {"000001": {"optype": "text", "term_analysis": '
             '{"case_sensitive": true, "stem_words": true, '
             '"use_stopwords": false}}}}',
             'data/model/if_then_rules_spam_textanalysis_2.txt'],
            ['data/spam.csv', '30', '30', '30',
             '{"fields": {"000001": {"optype": "text", "term_analysis": '
             '{"case_sensitive": false, "stem_words": false, '
             '"use_stopwords": false, "language": "en"}}}}',
             'data/model/if_then_rules_spam_textanalysis_3.txt'],
            ['data/spam.csv', '30', '30', '30',
             '{"fields": {"000001": {"optype": "text", "term_analysis": '
             '{"case_sensitive": false, "stem_words": true, "use_stopwords": '
             'true, "language": "en"}}}}',
             'data/model/if_then_rules_spam_textanalysis_4.txt'],
            ['data/spam.csv', '30', '30', '30',
             '{"fields": {"000001": {"optype": "text", "term_analysis": '
             '{"token_mode": "full_terms_only", "language": "en"}}}}',
             'data/model/if_then_rules_spam_textanalysis_5.txt'],
            ['data/spam.csv', '30', '30', '30',
             '{"fields": {"000001": {"optype": "text", "term_analysis": '
             '{"case_sensitive": true, "stem_words": true, "use_stopwords": '
             'false, "language": "en"}}}}',
             'data/model/if_then_rules_spam_textanalysis_6.txt']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            source_create.i_upload_a_file(
                self, example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"])
            source_create.i_update_source_with(self, example["source_conf"])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self,
                example["dataset_wait"])
            model_create.i_create_a_model(self)
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"])
            prediction_compare.i_create_a_local_model(self)
            inspect_model.i_translate_the_tree_into_IF_THEN_rules(self)
            inspect_model.i_check_if_the_output_is_like_expected_file(
                self, example["output_file"])

    def test_scenario4(self):
        """
            Scenario: Successfully creating a model and check its data distribution:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a model
                And I wait until the model is ready less than <model_wait> secs
                And I create a local model
                And I translate the tree into IF_THEN rules
                Then I check the data distribution with "<output_file>" file
        """
        show_doc(self.test_scenario4)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "output_file"]
        examples = [
            ['data/iris.csv', '30', '30', '30',
             'data/model/data_distribution_iris.txt'],
            ['data/iris_sp_chars.csv', '30', '30', '30',
             'data/model/data_distribution_iris_sp_chars.txt'],
            ['data/spam.csv', '30', '30', '30',
             'data/model/data_distribution_spam.txt'],
            ['data/grades.csv', '30', '30', '30',
             'data/model/data_distribution_grades.txt'],
            ['data/diabetes.csv', '30', '30', '30',
             'data/model/data_distribution_diabetes.txt'],
            ['data/iris_missing2.csv', '30', '30', '30',
             'data/model/data_distribution_iris_missing2.txt'],
            ['data/tiny_kdd.csv', '30', '30', '30',
             'data/model/data_distribution_tiny_kdd.txt']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            dataset_create.i_create_a_dataset(self, shared=example["data"])
            dataset_create.the_dataset_is_finished_in_less_than(self,
                example["dataset_wait"], shared=example["data"])
            model_create.i_create_a_model(self, shared=example["data"])
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"], shared=example["data"])
            prediction_compare.i_create_a_local_model(self)
            inspect_model.i_check_the_data_distribution(
                self, example["output_file"])

    def test_scenario5(self):
        """
            Scenario: Successfully creating a model and check its predictions distribution:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <source_wait> secs
                And I create a dataset
                And I wait until the dataset is ready less than <dataset_wait> secs
                And I create a model
                And I wait until the model is ready less than <model_wait> secs
                And I create a local model
                And I translate the tree into IF_THEN rules
                Then I check the predictions distribution with "<output_file>" file
        """
        show_doc(self.test_scenario5)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "output_file"]
        examples = [
            ['data/iris.csv', '30', '30', '30',
             'data/model/predictions_distribution_iris.txt'],
            ['data/iris_sp_chars.csv', '30', '30', '30',
             'data/model/predictions_distribution_iris_sp_chars.txt'],
            ['data/spam.csv', '30', '30', '30',
             'data/model/predictions_distribution_spam.txt'],
            ['data/grades.csv', '30', '30', '30',
             'data/model/predictions_distribution_grades.txt'],
            ['data/diabetes.csv', '30', '30', '30',
             'data/model/predictions_distribution_diabetes.txt'],
            ['data/iris_missing2.csv', '30', '30', '30',
             'data/model/predictions_distribution_iris_missing2.txt'],
            ['data/tiny_kdd.csv', '30', '30', '30',
             'data/model/predictions_distribution_tiny_kdd.txt']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            dataset_create.i_create_a_dataset(self, shared=example["data"])
            dataset_create.the_dataset_is_finished_in_less_than(self,
                example["dataset_wait"], shared=example["data"])
            model_create.i_create_a_model(self, shared=example["data"])
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"], shared=example["data"])
            prediction_compare.i_create_a_local_model(self)
            inspect_model.i_check_the_predictions_distribution(
                self, example["output_file"])


    def test_scenario6(self):
        """
            Scenario: Successfully creating a model and check its summary information:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a model
                And I wait until the model is ready less than <time_3> secs
                And I create a local model
                And I translate the tree into IF_THEN rules
                Then I check the model summary with "<expected_file>" file
        """
        show_doc(self.test_scenario6)
        headers = ["data", "source_wait", "dataset_wait", "model_wait",
                   "output_file"]
        examples = [
            ['data/iris.csv', '30', '30', '30',
             'data/model/summarize_iris.txt'],
            ['data/iris_sp_chars.csv', '30', '30', '30',
             'data/model/summarize_iris_sp_chars.txt'],
            ['data/spam.csv', '30', '30', '30',
             'data/model/summarize_spam.txt'],
            ['data/grades.csv', '30', '30', '30',
             'data/model/summarize_grades.txt'],
            ['data/diabetes.csv', '30', '30', '30',
             'data/model/summarize_diabetes.txt'],
            ['data/iris_missing2.csv', '30', '30', '30',
             'data/model/summarize_iris_missing2.txt'],
            ['data/tiny_kdd.csv', '30', '30', '30',
             'data/model/summarize_tiny_kdd.txt']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            source_create.i_upload_a_file(
                self, example["data"], shared=example["data"])
            source_create.the_source_is_finished(
                self, example["source_wait"], shared=example["data"])
            dataset_create.i_create_a_dataset(
                self, shared=example["data"])
            dataset_create.the_dataset_is_finished_in_less_than(self,
                example["dataset_wait"], shared=example["data"])
            model_create.i_create_a_model(self, shared=example["data"])
            model_create.the_model_is_finished_in_less_than(
                self, example["model_wait"], shared=example["data"])
            prediction_compare.i_create_a_local_model(self)
            inspect_model.i_check_the_model_summary_with(
                self, example["output_file"])

    def test_scenario7(self):
        """
            Scenario: Unit tests for output generators:
                Given I read a model from "<data>" file
                And I create a local model
                And I create a distribution, list fields and a tree CSV
                Then I check distribution with "<distribution>" file
                Then I check list_fields with "<list_fields>" file
                Then I check tree CSV with "<tree_csv>" file
        """

        show_doc(self.test_scenario7)
        headers = ["data", "distribution", "list_fields", "tree_csv"]
        examples = [
            ['data/model/iris.json',
             'data/model/distribution_iris.txt',
             'data/model/list_fields.txt',
             'data/model/tree_csv.txt'],
            ['data/model/regression.json',
             'data/model/rdistribution_iris.txt',
             'data/model/rlist_fields.txt',
             'data/model/rtree_csv.txt'],
            ['data/model/w_iris.json',
             'data/model/wdistribution_iris.txt',
             'data/model/wlist_fields.txt',
             'data/model/wtree_csv.txt'],
            ['data/model/w_regression.json',
             'data/model/wrdistribution_iris.txt',
             'data/model/wrlist_fields.txt',
             'data/model/wrtree_csv.txt']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, self.bigml["method"], example)
            world.debug=True
            model_create.i_read_model_file(self, example["data"])
            prediction_compare.i_create_a_local_model(self)
            inspect_model.i_check_print_distribution(
                self, example["distribution"])
            inspect_model.i_list_fields(self, example["list_fields"])
            inspect_model.i_create_tree_csv(self, example["tree_csv"])
