# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015-2017 BigML
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


""" Testing MultiVote predictions

"""
from world import world, setup_module, teardown_module
import compute_multivote_prediction_steps as multivote_prediction


class TestMultiVotePrediction(object):

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
            Scenario: Successfully computing predictions combinations:
                Given I create a MultiVote for the set of predictions in file <predictions>
                When I compute the prediction with confidence using method "<method>"
                And I compute the prediction without confidence using method "<method>"
                Then the combined prediction is "<prediction>"
                And the combined prediction without confidence is "<prediction>"
                And the confidence for the combined prediction is <confidence>

                Examples:
                | predictions               | method       | prediction    | confidence            |
                | ../data/predictions_c.json| 0            | a             | 0.450471270879        |
                | ../data/predictions_c.json| 1            | a             | 0.552021302649        |
                | ../data/predictions_c.json| 2            | a             | 0.403632421178        |
                | ../data/predictions_r.json| 0            | 1.55555556667 | 0.400079152063        |
                | ../data/predictions_r.json| 1            | 1.59376845074 | 0.248366474212        |
                | ../data/predictions_r.json| 2            | 1.55555556667 | 0.400079152063        |
        """
        print self.test_scenario1.__doc__
        examples = [
            ['data/predictions_c.json', '0', 'a', '0.450471270879'],
            ['data/predictions_c.json', '1', 'a', '0.552021302649'],
            ['data/predictions_c.json', '2', 'a', '0.403632421178'],
            ['data/predictions_r.json', '0', '1.55555556667', '0.400079152063'],
            ['data/predictions_r.json', '1', '1.59376845074', '0.248366474212'],
            ['data/predictions_r.json', '2', '1.55555556667', '0.400079152063']]
        for example in examples:
            print "\nTesting with:\n", example
            multivote_prediction.i_create_a_multivote(self, example[0])
            multivote_prediction.compute_prediction(self, example[1])
            multivote_prediction.compute_prediction_no_confidence(self, example[1])
            multivote_prediction.check_combined_prediction(self, example[2])
            multivote_prediction.check_combined_prediction_no_confidence(self, example[2])
            multivote_prediction.check_combined_confidence(self, example[3])
