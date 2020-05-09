# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2016-2020 BigML
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


""" Creating a local Topic distribution from Topic Model

"""
from world import world, setup_module, teardown_module
import create_source_steps as source_create
import create_dataset_steps as dataset_create
import create_lda_steps as topic_create
import compute_lda_prediction_steps as lda_predict


# This model is from the bigmlcom/streaming-lda; the associated test is
# for near-exact equivalence with that library (with special attention
# to random number generation).
DUMMY_MODEL = {
    "input_fields": ["000001"],
    "topic_model": {
        "alpha": 0.08,
        "beta": 0.1,
        "hashed_seed": 0,
        "language": "en",
        "bigrams": True,
        "case_sensitive": False,
        "term_topic_assignments": [[0, 0, 1, 2],
                                   [0, 1, 2, 0],
                                   [1, 2, 0, 0],
                                   [0, 0, 2, 0]],
        "termset": [u"cycling", u"playing", u"shouldn't", u"uńąnimous court"],
        "options": {},
        "topics": [{"name": "Topic 1",
                    "id": "000000",
                    "top_terms": ["a", "b"],
                    "probability": 0.1},
                   {"name": "Topic 2",
                    "id": "000001",
                    "top_terms": ["c", "d"],
                    "probability": 0.1},
                   {"name": "Topic 3",
                    "id": "000000",
                    "top_terms": ["e", "f"],
                    "probability": 0.1},
                   {"name": "Topic 4",
                    "id": "000000",
                    "top_terms": ["g", "h"],
                    "probability": 0.1}],
        "fields": {
            "000001": {
                "datatype": "string",
                "name": "TEST TEXT",
                "optype": "text",
                "order": 0,
                "preferred": True,
                "summary": {},
                "term_analysis": {}
            }
        }
    },
    "resource": "topicmodel/aaaaaabbbbbbccccccdddddd"
}


class TestTopicModel(object):

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
            Scenario 1: Successfully creating a local Topic Distribution
                Given I have a block of text and an LDA model
                And I use the model to predict the topic distribution
                Then the value of the distribution matches the expected distribution

                Examples:
                | model | text            | expected_distribution  |
                | {...} | "hello, world!" | [0.5, 0.3, 0.2]        |
        """
        print self.test_scenario1.__doc__
        examples = [
            # This example is a replication of a test in bigmlcom/streaming-lda
            [
                DUMMY_MODEL,
                {"TEST TEXT": u"uńąnimous court 'UŃĄNIMOUS COURT' "
                 u"`play``the plays PLAYing SHOULDN'T CYCLE "
                 u"cycling shouldn't uńąnimous or court's"},
                    [
                      {"name": 'Topic 1', "probability": 0.1647366},
                      {"name": 'Topic 2', "probability": 0.1885310},
                      {"name": 'Topic 3', "probability": 0.4879441},
                      {"name": 'Topic 4', "probability": 0.1587880}]

            ]
        ]

        for ex in examples:
            print "\nTesting with:\n", ex[1]
            lda_predict.i_make_a_prediction(self, ex[0], ex[1], ex[2])

    def test_scenario2(self):
        """
            Scenario 2: Successfully creating Topic Model from a dataset:
                Given I create a data source uploading a "<data>" file
                And I wait until the source is ready less than <time_1> secs
                And I create a dataset
                And I wait until the dataset is ready less than <time_2> secs
                And I create topic model from a dataset
                And I wait until the topic model is ready less than <time_3> secs
                And I update the topic model name to "<topic_model_name>"
                When I wait until the topic_model is ready less than <time_4> secs
                Then the topic model name is "<topic_model_name>"

                Examples:
                | data             | time_1  | time_2 | time_3 | time_4 | topic_model_name | params
                | ../data/spam.csv | 100      | 100     | 100     | 100 | my new topic model name | '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false, "language": "en"}}}}'
        """
        print self.test_scenario2.__doc__
        examples = [
            ['data/spam.csv', '100', '100', '100', '100', 'my new topic model name', '{"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false, "language": "en"}}}}']]
        for example in examples:
            print "\nTesting with:\n", example
            source_create.i_upload_a_file(self, example[0])
            source_create.the_source_is_finished(self, example[1])
            source_create.i_update_source_with(self, example[6])
            dataset_create.i_create_a_dataset(self)
            dataset_create.the_dataset_is_finished_in_less_than(self, example[2])
            topic_create.i_create_a_topic_model(self)
            topic_create.the_topic_model_is_finished_in_less_than(self, example[3])
            topic_create.i_update_topic_model_name(self, example[5])
            topic_create.the_topic_model_is_finished_in_less_than(self, example[4])
            topic_create.i_check_topic_model_name(self, example[5])
