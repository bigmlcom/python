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


""" Testing MultiVote predictions

"""
from .world import world, setup_module, teardown_module, show_doc
from . import compute_multivote_prediction_steps as multivote_prediction


class TestMultiVotePrediction(object):

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
            Scenario 1: Successfully computing predictions combinations:
                Given I create a MultiVote for the set of predictions in file <predictions>
                When I compute the prediction with confidence using method "<method>"
                And I compute the prediction without confidence using method "<method>"
                Then the combined prediction is "<prediction>"
                And the combined prediction without confidence is "<prediction>"
                And the confidence for the combined prediction is <confidence>
        """
        show_doc(self.test_scenario1)
        headers = ["predictions_file", "method", "prediction", "confidence"]
        examples = [
            ['data/predictions_c.json', '0', 'a', '0.45047'],
            ['data/predictions_c.json', '1', 'a', '0.55202'],
            ['data/predictions_c.json', '2', 'a', '0.40363'],
            ['data/predictions_r.json', '0', '1.55555556667', '0.40008'],
            ['data/predictions_r.json', '1', '1.59376845074', '0.24837'],
            ['data/predictions_r.json', '2', '1.55555556667', '0.40008']]
        for example in examples:
            example = dict(zip(headers, example))
            show_method(self, sys._getframe().f_code.co_name, example)
            multivote_prediction.i_create_a_multivote(
                self, example["predictions_file"])
            multivote_prediction.compute_prediction(
            self, example["method"])
            multivote_prediction.compute_prediction_no_confidence(
                self, example["method"])
            multivote_prediction.check_combined_prediction(
                self, example["prediction"])
            multivote_prediction.check_combined_prediction_no_confidence(
                self, example["prediction"])
            multivote_prediction.check_combined_confidence(
                self, example["confidence"])
