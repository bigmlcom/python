# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2016 BigML
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
import compute_lda_prediction_steps as lda_predict

# This model is from the bigmlcom/streaming-lda; the associated test is
# for near-exact equivalence with that library (with special attention
# to random number generation).
DUMMY_MODEL = {
    "model": {
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
        "termset": ["cycling", "playing", "tacos", "unanimous court"],
        "options": {},
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
            Scenario: Successfully creating a local Topic Distribution
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
                {"TEST TEXT": "unanimous court UNANIMOUS COURT "
                              "play the plays PLAYing TACO CYCLE "
                              "cycling tacos unanimous or court"},
                [0.10093624, 0.20856967, 0.56734777, 0.12314631]
            ]
        ]

        for ex in examples:
            print "\nTesting with:\n", ex[1]
            lda_predict.i_make_a_prediction(self, ex[0], ex[1], ex[2])
