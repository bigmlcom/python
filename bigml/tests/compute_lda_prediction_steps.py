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

from bigml.lda import LDA

from nose.tools import assert_almost_equals

#@step(r'predict the topic distribution for the text "(.*)"$')
def i_make_a_prediction(step, model, text, expected):
    lda_model = LDA(model)
    distribution = lda_model.distribution(text)

    msg = ("Computed distribution is %s, but expected distribution is %s" %
           (str(distribution), str(expected)))

    assert len(distribution) == len(expected), msg

    for d, e in zip(distribution, expected):
        assert_almost_equals(d, e, places=6, msg=msg)
