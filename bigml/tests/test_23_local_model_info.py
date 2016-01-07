# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015-2016 BigML
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
from world import world, setup_module, teardown_module
import create_source_steps as source_create
import create_dataset_steps as dataset_create
import create_model_steps as model_create
import compare_predictions_steps as prediction_compare
import inspect_model_steps as inspect_model

class TestLocalModelOutputs(object):

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
            Scenario: Successfully creating a model and translate the tree model into a set of IF-THEN rules:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a model
                And I wait until the model is ready less than <time_3> secs
                And I create a local model
                And I translate the tree into IF_THEN rules
                Then I check the output is like "<expected_file>" expected file

                Examples:
                | data                   | time_1  | time_2 | time_3 | expected_file                                        |
                | data/iris.csv          | 10      | 10     | 10     | data/model/if_then_rules_iris.txt              |
                | data/iris_sp_chars.csv | 10      | 10     | 10     | data/model/if_then_rules_iris_sp_chars.txt     |
                | data/spam.csv          | 20      | 20     | 30     | data/model/if_then_rules_spam.txt              |
                | data/grades.csv        | 10      | 10     | 10     | data/model/if_then_rules_grades.txt            |
                | data/diabetes.csv      | 20      | 20     | 30     | data/model/if_then_rules_diabetes.txt          |
                | data/iris_missing2.csv | 10      | 10     | 10     | data/model/if_then_rules_iris_missing2.txt     |
                | data/tiny_kdd.csv      | 20      | 20     | 30     | data/model/if_then_rules_tiny_kdd.txt          |

        """
        print self.test_scenario1.__doc__
        examples = [
            ['data/iris.csv', '10', '10', '10', 'data/model/if_then_rules_iris.txt'],
            ['data/iris_sp_chars.csv', '10', '10', '10', 'data/model/if_then_rules_iris_sp_chars.txt'],
            ['data/spam.csv', '10', '10', '10', 'data/model/if_then_rules_spam.txt'],
            ['data/grades.csv', '10', '10', '10', 'data/model/if_then_rules_grades.txt'],
            ['data/diabetes.csv', '10', '10', '10', 'data/model/if_then_rules_diabetes.txt'],
            ['data/iris_missing2.csv', '10', '10', '10', 'data/model/if_then_rules_iris_missing2.txt'],
            ['data/tiny_kdd.csv', '10', '10', '10', 'data/model/if_then_rules_tiny_kdd.txt']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_model(self)
            model_create.the_model_is_finished_in_less_than(self, example[3])
            prediction_compare.i_create_a_local_model(self)
            inspect_model.i_translate_the_tree_into_IF_THEN_rules(self)
            inspect_model.i_check_if_the_output_is_like_expected_file(self, example[4])

    def test_scenario2(self):
        """
            Scenario: Successfully creating a model with missing values and translate the tree model into a set of IF-THEN rules:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a model
                And I wait until the model is ready less than <time_3> secs
                And I create a local model
                And I translate the tree into IF_THEN rules
                Then I check the output is like "<expected_file>" expected file

                Examples:
                | data                   | time_1  | time_2 | time_3 | expected_file                                         |
                | data/iris_missing2.csv | 10      | 10     | 10     | data/model/if_then_rules_iris_missing2_MISSINGS.txt     |

        """
        print self.test_scenario2.__doc__
        examples = [
            ['data/iris_missing2.csv', '10', '10', '10', 'data/model/if_then_rules_iris_missing2_MISSINGS.txt']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_model_with_missing_splits(self)
            model_create.the_model_is_finished_in_less_than(self, example[3])
            prediction_compare.i_create_a_local_model(self)
            inspect_model.i_translate_the_tree_into_IF_THEN_rules(self)
            inspect_model.i_check_if_the_output_is_like_expected_file(self, example[4])

    def test_scenario3(self):
        """
            Scenario: Successfully creating a model and translate the tree model into a set of IF-THEN rules:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I update the source with "<options>" waiting less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a model
                And I wait until the model is ready less than <time_3> secs
                And I create a local model
                And I translate the tree into IF_THEN rules
                Then I check the output is like "<expected_file>" expected file

                Examples:
                | data                   | time_1  | time_2 | time_3 | options  |   expected_file                                        |
                | data/spam.csv          | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false, "language": "en"}}}} | data/model/if_then_rules_spam_textanalysis_1.txt              |
                | data/spam.csv          | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false}}}} | data/model/if_then_rules_spam_textanalysis_2.txt              |
                | data/spam.csv          | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": false, "use_stopwords": false, "language": "en"}}}} | data/model/if_then_rules_spam_textanalysis_3.txt              |
                | data/spam.csv          | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": true, "use_stopwords": true, "language": "en"}}}} | data/model/if_then_rules_spam_textanalysis_4.txt              |
                | data/spam.csv          | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"token_mode": "full_terms_only", "language": "en"}}}} | data/model/if_then_rules_spam_textanalysis_5.txt              |
                | data/spam.csv          | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false, "language": "en"}}}} | data/model/if_then_rules_spam_textanalysis_6.txt              |

        """
        print self.test_scenario3.__doc__
        examples = [
            ['data/spam.csv', '10', '10', '10', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false, "language": "en"}}}}','data/model/if_then_rules_spam_textanalysis_1.txt'],
            ['data/spam.csv', '10', '10', '10', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false}}}}', 'data/model/if_then_rules_spam_textanalysis_2.txt'],
            ['data/spam.csv', '10', '10', '10', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": false, "use_stopwords": false, "language": "en"}}}}', 'data/model/if_then_rules_spam_textanalysis_3.txt'],
            ['data/spam.csv', '10', '10', '10', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": true, "use_stopwords": true, "language": "en"}}}}', 'data/model/if_then_rules_spam_textanalysis_4.txt'],
            ['data/spam.csv', '10', '10', '10', '{"fields": {"000001": {"optype": "text", "term_analysis": {"token_mode": "full_terms_only", "language": "en"}}}}', 'data/model/if_then_rules_spam_textanalysis_5.txt'],
            ['data/spam.csv', '10', '10', '10', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false, "language": "en"}}}}', 'data/model/if_then_rules_spam_textanalysis_6.txt']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            source_create.i_update_source_with(self, example[4])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_model(self)
            model_create.the_model_is_finished_in_less_than(self, example[3])
            prediction_compare.i_create_a_local_model(self)
            inspect_model.i_translate_the_tree_into_IF_THEN_rules(self)
            inspect_model.i_check_if_the_output_is_like_expected_file(self, example[5])


    def test_scenario4(self):
        """
            Scenario: Successfully creating a model and check its data distribution:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a model
                And I wait until the model is ready less than <time_3> secs
                And I create a local model
                And I translate the tree into IF_THEN rules
                Then I check the data distribution with "<expected_file>" file

                Examples:
                | data                   | time_1  | time_2 | time_3 | expected_file                                        |
                | data/iris.csv          | 10      | 10     | 10     | data/model/data_distribution_iris.txt              |
                | data/iris_sp_chars.csv | 10      | 10     | 10     | data/model/data_distribution_iris_sp_chars.txt     |
                | data/spam.csv          | 20      | 20     | 30     | data/model/data_distribution_spam.txt              |
                | data/grades.csv        | 10      | 10     | 10     | data/model/data_distribution_grades.txt            |
                | data/diabetes.csv      | 20      | 20     | 30     | data/model/data_distribution_diabetes.txt          |
                | data/iris_missing2.csv | 10      | 10     | 10     | data/model/data_distribution_iris_missing2.txt     |
                | data/tiny_kdd.csv      | 20      | 20     | 30     | data/model/data_distribution_tiny_kdd.txt          |

        """
        print self.test_scenario4.__doc__
        examples = [
            ['data/iris.csv', '10', '10', '10', 'data/model/data_distribution_iris.txt'],
            ['data/iris_sp_chars.csv', '10', '10', '10', 'data/model/data_distribution_iris_sp_chars.txt'],
            ['data/spam.csv', '10', '10', '10', 'data/model/data_distribution_spam.txt'],
            ['data/grades.csv', '10', '10', '10', 'data/model/data_distribution_grades.txt'],
            ['data/diabetes.csv', '10', '10', '10', 'data/model/data_distribution_diabetes.txt'],
            ['data/iris_missing2.csv', '10', '10', '10', 'data/model/data_distribution_iris_missing2.txt'],
            ['data/tiny_kdd.csv', '10', '10', '10', 'data/model/data_distribution_tiny_kdd.txt']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_model(self)
            model_create.the_model_is_finished_in_less_than(self, example[3])
            prediction_compare.i_create_a_local_model(self)
            inspect_model.i_check_the_data_distribution(self, example[4])


    def test_scenario5(self):
        """
            Scenario: Successfully creating a model and check its predictions distribution:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create a model
                And I wait until the model is ready less than <time_3> secs
                And I create a local model
                And I translate the tree into IF_THEN rules
                Then I check the predictions distribution with "<expected_file>" file

                Examples:
                | data                   | time_1  | time_2 | time_3 | expected_file                                        |
                | data/iris.csv          | 10      | 10     | 10     | data/model/predictions_distribution_iris.txt              |
                | data/iris_sp_chars.csv | 10      | 10     | 10     | data/model/predictions_distribution_iris_sp_chars.txt     |
                | data/spam.csv          | 20      | 20     | 30     | data/model/predictions_distribution_spam.txt              |
                | data/grades.csv        | 10      | 10     | 10     | data/model/predictions_distribution_grades.txt            |
                | data/diabetes.csv      | 20      | 20     | 30     | data/model/predictions_distribution_diabetes.txt          |
                | data/iris_missing2.csv | 10      | 10     | 10     | data/model/predictions_distribution_iris_missing2.txt     |
                | data/tiny_kdd.csv      | 20      | 20     | 30     | data/model/predictions_distribution_tiny_kdd.txt          |

        """
        print self.test_scenario5.__doc__
        examples = [
            ['data/iris.csv', '10', '10', '10', 'data/model/predictions_distribution_iris.txt'],
            ['data/iris_sp_chars.csv', '10', '10', '10', 'data/model/predictions_distribution_iris_sp_chars.txt'],
            ['data/spam.csv', '10', '10', '10', 'data/model/predictions_distribution_spam.txt'],
            ['data/grades.csv', '10', '10', '10', 'data/model/predictions_distribution_grades.txt'],
            ['data/diabetes.csv', '10', '10', '10', 'data/model/predictions_distribution_diabetes.txt'],
            ['data/iris_missing2.csv', '10', '10', '10', 'data/model/predictions_distribution_iris_missing2.txt'],
            ['data/tiny_kdd.csv', '10', '10', '10', 'data/model/predictions_distribution_tiny_kdd.txt']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_model(self)
            model_create.the_model_is_finished_in_less_than(self, example[3])
            prediction_compare.i_create_a_local_model(self)
            inspect_model.i_check_the_predictions_distribution(self, example[4])


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

                Examples:
                | data                   | time_1  | time_2 | time_3 | expected_file                                        |
                | data/iris.csv          | 10      | 10     | 10     | data/model/summarize_iris.txt              |
                | data/iris_sp_chars.csv | 10      | 10     | 10     | data/model/summarize_iris_sp_chars.txt     |
                | data/spam.csv          | 20      | 20     | 30     | data/model/summarize_spam.txt              |
                | data/grades.csv        | 10      | 10     | 10     | data/model/summarize_grades.txt            |
                | data/diabetes.csv      | 20      | 20     | 30     | data/model/summarize_diabetes.txt          |
                | data/iris_missing2.csv | 10      | 10     | 10     | data/model/summarize_iris_missing2.txt     |
                | data/tiny_kdd.csv      | 20      | 20     | 30     | data/model/summarize_tiny_kdd.txt          |

        """
        print self.test_scenario6.__doc__
        examples = [
            ['data/iris.csv', '10', '10', '10', 'data/model/summarize_iris.txt'],
            ['data/iris_sp_chars.csv', '10', '10', '10', 'data/model/summarize_iris_sp_chars.txt'],
            ['data/spam.csv', '10', '10', '10', 'data/model/summarize_spam.txt'],
            ['data/grades.csv', '10', '10', '10', 'data/model/summarize_grades.txt'],
            ['data/diabetes.csv', '10', '10', '10', 'data/model/summarize_diabetes.txt'],
            ['data/iris_missing2.csv', '10', '10', '10', 'data/model/summarize_iris_missing2.txt'],
            ['data/tiny_kdd.csv', '10', '10', '10', 'data/model/summarize_tiny_kdd.txt']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            model_create.i_create_a_model(self)
            model_create.the_model_is_finished_in_less_than(self, example[3])
            prediction_compare.i_create_a_local_model(self)
            inspect_model.i_check_the_model_summary_with(self, example[4])
