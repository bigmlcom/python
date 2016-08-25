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

"""A local Predictive LDA Model.

This module allows you to download and use LDA models for local
predicitons.  Specifically, the function LDA.distribution allows you
to pass in input text and infers a generative distribution over the
topics in the learned LDA model.

Example usage (assuming that you have previously set up the BIGML_USERNAME
and BIGML_API_KEY environment variables and that you own the lda/id
below):

from bigml.api import BigML
from bigml.lda import LDA

api = BigML()

lda = LDA('lda/5026965515526876630001b2')
topic_distribution = lda.distribution({"text": "A sample string"}))

"""
from bigml.api import FINISHED
from bigml.api import BigML, get_lda_id, get_status
from bigml.util import cast, utf8
from bigml.basemodel import retrieve_resource
from bigml.basemodel import ONLY_MODEL
from bigml.model import STORAGE
from bigml.modelfields import ModelFields

import random
import logging
import array
import Stemmer

LOGGER = logging.getLogger('BigML')

MAXIMUM_TERM_LENGTH = 30
UPDATES = 64

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

class LDA(ModelFields):
    """ A lightweight wrapper around an LDA model.

    Uses a BigML remote LDA model to build a local version that can be used
    to generate topic distributions for input documents locally.

    """

    def __init__(self, lda_model, api=None):

        self.resource_id = None
        self.stemmer = None
        self.seed = None
        self.case_sensitive = False
        self.bigrams = False
        self.ntopics = None
        self.temp = None
        self.uniform_doc_assignments = None
        self.uniform_normalizer = None
        self.phi = None
        self.term_to_index = None

        if not (isinstance(lda_model, dict) and 'resource' in lda_model and
                lda_model['resource'] is not None):
            if api is None:
                api = BigML(storage=STORAGE)
            self.resource_id = get_lda_id(lda_model)
            if self.resource_id is None:
                raise Exception(api.error_message(lda_model,
                                                  resource_type='lda',
                                                  method='get'))
            query_string = ONLY_MODEL
            lda_model = retrieve_resource(api, self.resource_id,
                                          query_string=query_string)
        else:
            self.resource_id = get_lda_id(lda_model)

        if 'object' in lda_model and isinstance(lda_model['object'], dict):
            lda_model = lda_model['object']

        if 'model' in lda_model and isinstance(lda_model['model'], dict):
            status = get_status(lda_model)
            if 'code' in status and status['code'] == FINISHED:

                model = lda_model['model']

                if 'language' in model and  model['language'] is not None:
                    lang = model['language']
                    if lang in CODE_TO_NAME:
                        self.stemmer = Stemmer.Stemmer(CODE_TO_NAME[lang])

                self.term_to_index = {self.stem(term): index for index, term
                                      in enumerate(model['termset'])}

                self.seed = model['hashed_seed']
                self.case_sensitive = model['case_sensitive']
                self.bigrams = model['bigrams']

                self.ntopics = len(model['term_topic_assignments'][0])

                self.alpha = model['alpha']
                self.ktimesalpha = self.ntopics * self.alpha

                self.uniform_doc_assignments = [1] * self.ntopics
                self.uniform_normalizer = self.ntopics + self.ktimesalpha

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

                ModelFields.__init__(self, model['fields'])
            else:
                raise Exception("The topic model isn't finished yet")
        else:
            raise Exception("Cannot create the LDA instance. Could not"
                            " find the 'model' key in the resource:\n\n%s" %
                            lda_model)

    def distribution(self, input_data, by_name=True):
        """Returns the distribution of topics given the input text.

        """
        # Checks and cleans input_data leaving the fields used in the model
        input_data = self.filter_input_data(input_data, by_name=by_name)

        # Checks that all modeled fields are present in input data
        for field_id, field in self.fields.items():
            if field_id not in input_data:
                raise Exception("Failed to predict a topic distribution.  "
                                "Input data must contain values for all "
                                "modeled text fields.")

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
        return self.infer(doc, UPDATES)

    def stem(self, term):
        """Returns the stem of the given term, if the stemmer is defined

        """
        if not self.stemmer:
            return term
        else:
            return self.stemmer.stemWord(term)

    def append_bigram(self, out_terms, last_term, term_before):
        """Takes two terms and appends the index of their concatenation to the
           provided list of output terms

        """
        if self.bigrams and last_term is not None and term_before is not None:
            bigram = self.stem(term_before + " " + last_term)
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

        while index < len(text):
            self.append_bigram(out_terms, last_term, term_before)

            char = text[index]
            buf = array.array('u')
            saw_char = False

            if not char.isalnum():
                saw_char = True

            while not char.isalnum() and index < len(text):
                index += 1
                char = text[index]

            while (index < len(text) and
                   (char.isalnum() or char == "'") and
                   len(buf) < MAXIMUM_TERM_LENGTH):

                buf.append(char)
                index += 1

                if index < len(text):
                    char = text[index]
                else:
                    char = None

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

        self.append_bigram(out_terms, last_term, term_before)

        return out_terms

    def sampleTopic(self, term, assignments, normalizer, rng):
        """Samples a topic for the given `term`, given a set of topic
           assigments for the current document and a normalizer term
           derived from the dirichlet hyperparameters

        """
        for k in range(self.ntopics):
            topic_term = self.phi[k][term]
            topic_document =  (assignments[k] + self.alpha) / normalizer
            self.temp[k] = topic_term * topic_document

        for k in range(1, self.ntopics):
            self.temp[k] += self.temp[k - 1]

        random_value = rng.random() * self.temp[-1]
        topic = 0

        while self.temp[topic] < random_value and topic < self.ntopics:
            topic += 1

        return topic

    def sampleUniform(self, term, rng):
        """Samples a topic for the given term assuming uniform topic
           assignments for the given document.  Used to initialize the
           gibbs sampler.

        """
        assignments = self.uniform_doc_assignments
        norm = self.uniform_normalizer

        return self.sampleTopic(term, assignments, norm, rng)

    def infer(self, doc, max_updates):
        """Infer a topic distribution for a document using `max_updates`
           iterations of gibbs sampling

        """
        rng = random.Random(self.seed)
        normalizer = len(doc) + self.ktimesalpha
        doc_assignments = [0] * self.ntopics

        for index, term in enumerate(doc):
            topic = self.sampleUniform(term, rng)
            doc_assignments[topic] += 1

        # Gibbs sampling
        for _ in range(max_updates):
            for index, term in enumerate(doc):
                topic = self.sampleTopic(term, doc_assignments, normalizer, rng)
                doc_assignments[topic] += 1
                normalizer += 1

        return [(doc_assignments[k] + self.alpha) / normalizer
                for k in range(self.ntopics)]
