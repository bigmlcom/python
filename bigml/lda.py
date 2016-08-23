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
from bigml.api import (BigML, get_lda_id, get_status)
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

MAX_TERM_LENGTH = 30
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
    """ A lightweight wrapper around a cluster model.

    Uses a BigML remote cluster model to build a local version that can be used
    to generate centroid predictions locally.

    """

    def __init__(self, lda_model, api=None):

        self.resource_id = None
        self._stemmer = None
        self._seed = None
        self._case_sensitive = False
        self._bigrams = False
        self._ntopics = None
        self._temp = None
        self._uni_doc_assigns = None
        self._uni_daspka = None
        self._phi = None

        if not (isinstance(lda_model, dict) and 'resource' in lda_model and
                lda_model['resource'] is not None):
            if api is None:
                api = BigML(storage=STORAGE)
            self.resource_id = get_lda_id(lda_model)
            if self.resource_id is None:
                raise Exception(api.error_message(lda_model,
                                                  resource_type='cluster',
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
                        self._stemmer = Stemmer.Stemmer(CODE_TO_NAME[lang])

                tenum = enumerate(model['termset'])
                self._term_to_idx = {self._stem(t): i for i, t in tenum}

                self._seed = model['hashed_seed']
                self._case_sensitive = model['case_sensitive']
                self._bigrams = model['bigrams']

                self._ntopics = len(model['term_topic_assignments'][0])

                self._alpha = model['alpha']
                self._ktimesalpha = self._ntopics * self._alpha

                self._uni_doc_assigns = [1] * self._ntopics
                self._uni_daspka = self._ntopics + self._ktimesalpha

                self._temp = [0] * self._ntopics

                assigns = model['term_topic_assignments']
                beta = model['beta']
                nterms = len(self._term_to_idx)

                sums = [sum(n[i] for n in assigns)
                        for i in range(self._ntopics)]

                self._phi = [[0 for _ in range(nterms)]
                             for _ in range(self._ntopics)]

                for k in range(self._ntopics):
                    norm = sums[k] + nterms * beta
                    for w in range(nterms):
                        self._phi[k][w] = (assigns[w][k] + beta) / norm

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

        # Checks that all numeric fields are present in input data
        for field_id, field in self.fields.items():
            if field_id not in input_data:
                raise Exception("Failed to predict a topic distribution.  "
                                "Input data must contain values for all "
                                "modeled text fields.")

        return self._distribution_for_text("\n\n".join(input_data.values()))

    def _distribution_for_text(self, text):
        if isinstance(text, (str, unicode)):
            astr = text
        else:
            # List of strings
            astr = "\n\n".join(text)

        doc = self._tokenize(astr)
        return self._infer(doc, UPDATES)

    def _stem(self, term):
        if not self._stemmer:
            return turn
        else:
            return self._stemmer.stemWord(term)

    def _tokenize(self, astr):
        out_terms = []

        last_term = None
        term_before = None

        space_was_sep = False
        saw_char = False

        ustr = unicode(astr)
        i = 0

        while i < len(ustr):
            if (self._bigrams and
                last_term is not None and
                term_before is not None):

                bigram = self._stem(term_before + " " + last_term)
                if bigram in self._term_to_idx:
                    out_terms.append(self._term_to_idx[bigram])

            char = ustr[i]
            buf = array.array('u')
            saw_char = False

            if not char.isalnum():
                saw_char = True

            while not char.isalnum() and i < len(ustr):
                i += 1
                char = ustr[i]

            while (i < len(ustr) and
                   (char.isalnum() or char == "'") and
                   len(buf) < MAX_TERM_LENGTH):

                buf.append(char)
                i += 1

                if i < len(ustr):
                    char = ustr[i]
                else:
                    char = None

            if len(buf) > 0:
                term_out = buf.tounicode()

                if not self._case_sensitive:
                    term_out = term_out.lower()

                if space_was_sep and not saw_char:
                    term_before = last_term
                else:
                    term_before = None

                last_term = term_out

                if char == " " or char == "\n":
                    space_was_sep = True

                tstem = self._stem(term_out)
                if tstem in self._term_to_idx:
                    out_terms.append(self._term_to_idx[tstem])

                i += 1

        if (self._bigrams and
            last_term is not None and
            term_before is not None):

            bigram = self._stem(term_before + " " + last_term)
            if bigram in self._term_to_idx:
                out_terms.append(self._term_to_idx[bigram])

        return out_terms

    def _sampleTopic(self, t, assigns, norm, rng):
        for k in range(self._ntopics):
            self._temp[k] = self._phi[k][t] * (assigns[k] + self._alpha) / norm

        for k in range(1, self._ntopics):
            self._temp[k] += self._temp[k - 1]

        rand_val = rng.random() * self._temp[-1]
        topic = 0

        while self._temp[topic] < rand_val and topic < self._ntopics:
            topic += 1

        return topic

    def _sampleUniform(self, term, rng):
        assigns = self._uni_doc_assigns
        norm = self._uni_daspka

        return self._sampleTopic(term, assigns, norm, rng)

    def _infer(self, doc, max_updates):
        rng = random.Random(self._seed)
        normalizer = len(doc) + self._ktimesalpha
        doc_assigns = [0] * self._ntopics

        for index, term in enumerate(doc):
            topic = self._sampleUniform(term, rng)
            doc_assigns[topic] += 1

        # Gibbs sampling
        for _ in range(max_updates):
            for index, term in enumerate(doc):
                topic = self._sampleTopic(term, doc_assigns, normalizer, rng)
                doc_assigns[topic] += 1
                normalizer += 1

        return [(doc_assigns[k] + self._alpha) / normalizer
                for k in range(self._ntopics)]
