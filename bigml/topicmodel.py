# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2016-2019 BigML
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

"""A local Predictive Topic Model.

This module allows you to download and use Topic models for local
predicitons.  Specifically, the function topic_model.distribution allows you
to pass in input text and infers a generative distribution over the
topics in the learned topic model.

Example usage (assuming that you have previously set up the BIGML_USERNAME
and BIGML_API_KEY environment variables and that you own the topicmodel/id
below):

from bigml.api import BigML
from bigml.topicmodel import TopicModel

api = BigML()

topic_model = TopicModel('topicmodel/5026965515526876630001b2')
topic_distribution = topic_model.distribution({"text": "A sample string"}))

"""

import random
import logging
import array
try:
    import Stemmer
except ImportError:
    raise ImportError("Failed to import the Stemmer module. You need to"
                      " install pystemmer to use the Topic Model class.")


from bigml.api import FINISHED
from bigml.api import get_status
from bigml.basemodel import get_resource_dict
from bigml.modelfields import ModelFields


LOGGER = logging.getLogger('BigML')

MAXIMUM_TERM_LENGTH = 30
MIN_UPDATES = 16
MAX_UPDATES = 512
SAMPLES_PER_TOPIC = 128

CODE_TO_NAME = {
    "da": u'danish',
    "nl": u'dutch',
    "en": u'english',
    "fi": u'finnish',
    "fr": u'french',
    "de": u'german',
    "hu": u'hungarian',
    "it": u'italian',
    "nn": u'norwegian',
    "pt": u'portuguese',
    "ro": u'romanian',
    "ru": u'russian',
    "es": u'spanish',
    "sv": u'swedish',
    "tr": u'turkish'
}

class TopicModel(ModelFields):
    """ A lightweight wrapper around a Topic Model.

    Uses a BigML remote Topic Model to build a local version that can be used
    to generate topic distributions for input documents locally.

    """

    def __init__(self, topic_model, api=None):

        self.resource_id = None
        self.stemmer = None
        self.seed = None
        self.case_sensitive = False
        self.bigrams = False
        self.ntopics = None
        self.temp = None
        self.phi = None
        self.term_to_index = None
        self.topics = []

        self.resource_id, topic_model = get_resource_dict( \
            topic_model, "topicmodel", api=api)

        if 'object' in topic_model and isinstance(topic_model['object'], dict):
            topic_model = topic_model['object']

        if 'topic_model' in topic_model \
                and isinstance(topic_model['topic_model'], dict):
            status = get_status(topic_model)
            if 'code' in status and status['code'] == FINISHED:
                self.input_fields = topic_model['input_fields']
                model = topic_model['topic_model']
                self.topics = model['topics']

                if 'language' in model and  model['language'] is not None:
                    lang = model['language']
                    if lang in CODE_TO_NAME:
                        self.stemmer = Stemmer.Stemmer(CODE_TO_NAME[lang])

                self.term_to_index = {self.stem(term): index for index, term
                                      in enumerate(model['termset'])}

                self.seed = abs(model['hashed_seed'])
                self.case_sensitive = model['case_sensitive']
                self.bigrams = model['bigrams']

                self.ntopics = len(model['term_topic_assignments'][0])

                self.alpha = model['alpha']
                self.ktimesalpha = self.ntopics * self.alpha

                self.temp = [0] * self.ntopics

                assignments = model['term_topic_assignments']
                beta = model['beta']
                nterms = len(self.term_to_index)

                sums = [sum(n[index] for n in assignments) for index
                        in range(self.ntopics)]

                self.phi = [[0 for _ in range(nterms)]
                            for _ in range(self.ntopics)]

                for k in range(self.ntopics):
                    norm = sums[k] + nterms * beta
                    for w in range(nterms):
                        self.phi[k][w] = (assignments[w][k] + beta) / norm

                missing_tokens = model.get("missing_tokens")
                ModelFields.__init__(self, model['fields'],
                                     missing_tokens=missing_tokens)
            else:
                raise Exception("The topic model isn't finished yet")
        else:
            raise Exception("Cannot create the topic model instance. Could not"
                            " find the 'topic_model' key in the"
                            " resource:\n\n%s" % topic_model)

    def distribution(self, input_data):
        """Returns the distribution of topics given the input text.

        """
        # Checks and cleans input_data leaving the fields used in the model
        input_data = self.filter_input_data(input_data)

        return self.distribution_for_text("\n\n".join(input_data.values()))

    def distribution_for_text(self, text):
        """Returns the topic distribution of the given `text`, which can
           either be a string or a list of strings

        """
        if isinstance(text, (str, unicode)):
            astr = text
        else:
            # List of strings
            astr = "\n\n".join(text)

        doc = self.tokenize(astr)
        topics_probability = self.infer(doc)
        return [{"name": self.topics[index]["name"], \
            "probability": probability} \
            for index, probability in enumerate(topics_probability)]

    def stem(self, term):
        """Returns the stem of the given term, if the stemmer is defined

        """
        if not self.stemmer:
            return term
        else:
            return self.stemmer.stemWord(term)

    def append_bigram(self, out_terms, first, second):
        """Takes two terms and appends the index of their concatenation to the
           provided list of output terms

        """
        if self.bigrams and first is not None and second is not None:
            bigram = self.stem(first + " " + second)
            if bigram in self.term_to_index:
                out_terms.append(self.term_to_index[bigram])

    def tokenize(self, astr):
        """Tokenizes the input string `astr` into a list of integers, one for
           each term term present in the `self.term_to_index`
           dictionary.  Uses word stemming if applicable.

        """
        out_terms = []

        last_term = None
        term_before = None

        space_was_sep = False
        saw_char = False

        text = unicode(astr)
        index = 0
        length = len(text)

        def next_char(text, index):
            """Auxiliary function to get next char and index with end check

            """
            index += 1
            if index < length:
                char = text[index]
            else:
                char = ''
            return char, index

        while index < length:
            self.append_bigram(out_terms, term_before, last_term)

            char = text[index]
            buf = array.array('u')
            saw_char = False

            if not char.isalnum():
                saw_char = True

            while not char.isalnum() and index < length:
                char, index = next_char(text, index)

            while (index < length and
                   (char.isalnum() or char == "'") and
                   len(buf) < MAXIMUM_TERM_LENGTH):

                buf.append(char)
                char, index = next_char(text, index)

            if len(buf) > 0:
                term_out = buf.tounicode()

                if not self.case_sensitive:
                    term_out = term_out.lower()

                if space_was_sep and not saw_char:
                    term_before = last_term
                else:
                    term_before = None

                last_term = term_out

                if char == " " or char == "\n":
                    space_was_sep = True

                tstem = self.stem(term_out)
                if tstem in self.term_to_index:
                    out_terms.append(self.term_to_index[tstem])

                index += 1

        self.append_bigram(out_terms, term_before, last_term)

        return out_terms


    def sample_topics(self, document, assignments, normalizer, updates, rng):
        """Samples topics for the terms in the given `document` for `updates`
           iterations, using the given set of topic `assigments` for
           the current document and a `normalizer` term derived from
           the dirichlet hyperparameters

        """
        counts = [0] * self.ntopics

        for _ in range(updates):
            for term in document:
                for k in range(self.ntopics):
                    topic_term = self.phi[k][term]
                    topic_document = (assignments[k] + self.alpha) / normalizer
                    self.temp[k] = topic_term * topic_document

                for k in range(1, self.ntopics):
                    self.temp[k] += self.temp[k - 1]

                random_value = rng.random() * self.temp[-1]
                topic = 0

                while self.temp[topic] < random_value and topic < self.ntopics:
                    topic += 1

                counts[topic] += 1

        return counts

    def sample_uniform(self, document, updates, rng):
        """Samples topics for the terms in the given `document` assuming
           uniform topic assignments for `updates` iterations.  Used
           to initialize the gibbs sampler.

        """
        counts = [0] * self.ntopics

        for _ in range(updates):
            for term in document:
                for k in range(self.ntopics):
                    self.temp[k] = self.phi[k][term]

                for k in range(1, self.ntopics):
                    self.temp[k] += self.temp[k - 1]

                random_value = rng.random() * self.temp[-1]
                topic = 0

                while self.temp[topic] < random_value and topic < self.ntopics:
                    topic += 1

                counts[topic] += 1

        return counts


    def infer(self, list_of_indices):
        """Infer a topic distribution for a document, presented as a list of
           term indices.

        """

        doc = sorted(list_of_indices)
        updates = 0

        if len(doc) > 0:
            updates = SAMPLES_PER_TOPIC * self.ntopics / len(doc)
            updates = int(min(MAX_UPDATES, max(MIN_UPDATES, updates)))

        rng = random.Random(self.seed)
        normalizer = (len(doc) * updates) + self.ktimesalpha

        # Initialization
        uniform_counts = self.sample_uniform(doc, updates, rng)

        # Burn-in
        burn_counts = self.sample_topics(doc,
                                         uniform_counts,
                                         normalizer,
                                         updates,
                                         rng)
        # Sampling
        sample_counts = self.sample_topics(doc,
                                           burn_counts,
                                           normalizer,
                                           updates,
                                           rng)

        return [(sample_counts[k] + self.alpha) / normalizer
                for k in range(self.ntopics)]
