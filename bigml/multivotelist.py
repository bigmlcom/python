# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2017-2019 BigML
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
"""Auxiliar class for lists of predictions combination.

"""
import logging


LOGGER = logging.getLogger('BigML')

from bigml.util import PRECISION


class MultiVoteList(object):
    """A multiple vote prediction in compact format

    Uses a number of predictions to generate a combined prediction.
    The input should be an ordered list of probability, counts or confidences
    for each of the classes in the objective field.

    """

    def __init__(self, predictions):
        """Init method, builds a MultiVoteList with a list of predictions
        The constuctor expects a list of well formed predictions like:
            [0.2, 0.34, 0.48] which might correspond to confidences of
            three different classes in the objective field.
        """
        if isinstance(predictions, list):
            self.predictions = predictions
        else:
            raise ValueError("Expected a list of values to create a"
                             "MultiVoteList. Found %s instead" % predictions)

    def extend(self, predictions_list):
        """Extending the extend method in lists

        """
        if isinstance(predictions_list, MultiVoteList):
            predictions_list = predictions_list.predictions
        self.predictions.extend(predictions_list)

    def append(self, prediction):
        """Extending the append method in lists

        """
        self.predictions.append(prediction)

    def combine_to_distribution(self, normalize=True):
        """Receives a list of lists. Each element is the list of probabilities
        or confidences
        associated to each class in the ensemble, as described in the
        `class_names` attribute and ordered in the same sequence. Returns the
        probability obtained by adding these predictions into a single one
        by adding their probabilities and normalizing.
        """
        total = 0.0
        output = [0.0] * len(self.predictions[0])

        for distribution in self.predictions:
            for i, vote_value in enumerate(distribution):
                output[i] += vote_value
                total += vote_value
        if not normalize:
            total = len(self.predictions)

        for i, value in enumerate(output):
            output[i] = round(value / total, PRECISION)

        return output
