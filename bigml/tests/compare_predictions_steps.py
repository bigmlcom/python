# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2012-2017 BigML
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


import json
import os

from nose.tools import eq_, assert_almost_equal
from world import world, res_filename
from bigml.model import Model
from bigml.logistic import LogisticRegression
from bigml.cluster import Cluster
from bigml.anomaly import Anomaly
from bigml.association import Association
from bigml.multimodel import MultiModel
from bigml.multivote import MultiVote
from bigml.topicmodel import TopicModel

from create_prediction_steps import check_prediction

#@step(r'I retrieve a list of remote models tagged with "(.*)"')
def i_retrieve_a_list_of_remote_models(step, tag):
    world.list_of_models = [ \
        world.api.get_model(model['resource']) for model in
        world.api.list_models(query_string="tags__in=%s" % tag)['objects']]


#@step(r'I create a local model from a "(.*)" file$')
def i_create_a_local_model_from_file(step, model_file):
    world.local_model = Model(res_filename(model_file))


#@step(r'I create a local model$')
def i_create_a_local_model(step):
    world.local_model = Model(world.model)


#@step(r'I create a multiple local prediction for "(.*)"')
def i_create_a_multiple_local_prediction(step, data=None):
    if data is None:
        data = "{}"
    data = json.loads(data)
    world.local_prediction = world.local_model.predict(data, multiple='all')


#@step(r'I create a local prediction for "(.*)" with confidence$')
def i_create_a_local_prediction_with_confidence(step, data=None):
    if data is None:
        data = "{}"
    data = json.loads(data)
    world.local_prediction = world.local_model.predict(data,
                                                       add_confidence=True)


#@step(r'I create a local prediction for "(.*)"$')
def i_create_a_local_prediction(step, data=None):
    if data is None:
        data = "{}"
    data = json.loads(data)
    world.local_prediction = world.local_model.predict(data)

#@step(r'I create a local ensemble prediction for "(.*)"$')
def i_create_a_local_ensemble_prediction(step, data=None):
    if data is None:
        data = "{}"
    data = json.loads(data)
    world.local_prediction = world.local_ensemble.predict(data)


#@step(r'I create a local prediction using median for "(.*)"$')
def i_create_a_local_median_prediction(step, data=None):
    if data is None:
        data = "{}"
    data = json.loads(data)
    world.local_prediction = world.local_model.predict(data, median=True)


#@step(r'I create a local multimodel batch prediction using median for "(.*)"$')
def i_create_a_local_mm_median_batch_prediction(self, data=None):
    if data is None:
        data = "{}"
    data = json.loads(data)
    world.local_prediction = world.local_model.batch_predict(
        [data], to_file=False, use_median=True)[0].predictions[0]['prediction']


#@step(r'I create a proportional missing strategy local prediction
# using median for "(.*)"$')
def i_create_a_local_proportional_median_prediction(step, data=None):
    if data is None:
        data = "{}"
    data = json.loads(data)
    world.local_prediction = world.local_model.predict( \
        data, missing_strategy=1, median=True)


#@step(r'I create a local cluster')
def i_create_a_local_cluster(step):
    world.local_cluster = Cluster(world.cluster)


#@step(r'I create a local centroid for "(.*)"')
def i_create_a_local_centroid(step, data=None):
    if data is None:
        data = "{}"
    data = json.loads(data)
    for key, value in data.items():
        if value == "":
            del data[key]
    world.local_centroid = world.local_cluster.centroid(data)


#@step(r'the local centroid is "(.*)" with distance "(.*)"')
def the_local_centroid_is(step, centroid, distance):
    check_prediction(world.local_centroid['centroid_name'], centroid)
    check_prediction(world.local_centroid['distance'], distance)

#@step(r'I create a local anomaly detector$')
def i_create_a_local_anomaly(step):
    world.local_anomaly = Anomaly(world.anomaly['resource'])


#@step(r'I create a local anomaly score for "(.*)"$')
def i_create_a_local_anomaly_score(step, input_data):
    input_data = json.loads(input_data)
    world.local_anomaly_score = world.local_anomaly.anomaly_score( \
        input_data, by_name=False)

#@step(r'the local anomaly score is "(.*)"$')
def the_local_anomaly_score_is(step, score):
    eq_(str(round(world.local_anomaly_score, 2)),
        str(round(float(score), 2)))


#@step(r'I create a local association')
def i_create_a_local_association(step):
    world.local_association = Association(world.association)

#@step(r'I create a proportional missing strategy local prediction for "(.*)"')
def i_create_a_proportional_local_prediction(step, data=None):
    if data is None:
        data = "{}"
    data = json.loads(data)
    world.local_prediction = world.local_model.predict(
        data, with_confidence=True, missing_strategy=1)


#@step(r'I create a prediction from a multi model for "(.*)"')
def i_create_a_prediction_from_a_multi_model(step, data=None):
    if data is None:
        data = "{}"
    data = json.loads(data)
    world.local_prediction = world.local_model.predict(data)


#@step(r'I create a batch multimodel prediction for "(.*)"')
def i_create_a_batch_prediction_from_a_multi_model(step, data=None):
    if data is None:
        data = "[{}]"
    data = json.loads(data)
    world.local_prediction = world.local_model.batch_predict(data,
                                                             to_file=False)

#@step(r'the predictions are "(.*)"')
def the_batch_mm_predictions_are(step, predictions):
    if predictions is None:
        predictions = "[{}]"
    predictions = json.loads(predictions)
    for i in range(len(predictions)):
        multivote = world.local_prediction[i]
        for prediction in multivote.predictions:
            eq_(prediction['prediction'], predictions[i])


#@step(r'the multiple local prediction is "(.*)"')
def the_multiple_local_prediction_is(step, prediction):
    local_prediction = world.local_prediction
    prediction = json.loads(prediction)
    eq_(local_prediction, prediction)

#@step(r'the local prediction\'s confidence is "(.*)"')
def the_local_prediction_confidence_is(step, confidence):
    if (isinstance(world.local_prediction, list) or
        isinstance(world.local_prediction, tuple)):
        local_confidence = world.local_prediction[1]
    else:
        local_confidence = world.local_prediction.get('confidence', \
            world.local_prediction.get('probability'))
    local_confidence = round(float(local_confidence), 4)
    confidence = round(float(confidence), 4)
    eq_(local_confidence, confidence)

#@step(r'the local prediction is "(.*)"')
def the_local_prediction_is(step, prediction):
    if (isinstance(world.local_prediction, list) or
        isinstance(world.local_prediction, tuple)):
        local_prediction = world.local_prediction[0]
    elif isinstance(world.local_prediction, dict):
        local_prediction = world.local_prediction['prediction']
    else:
        local_prediction = world.local_prediction
    try:
        local_model = world.local_model
        if not isinstance(world.local_model, LogisticRegression):
            if isinstance(local_model, MultiModel):
                local_model = local_model.models[0]
            if local_model.regression:
                local_prediction = round(float(local_prediction), 4)
                prediction = round(float(prediction), 4)
    except AttributeError:
        local_model = world.local_ensemble
        if local_model.regression:
            assert_almost_equal(local_prediction, float(prediction), places=5)

    eq_(local_prediction, prediction)

#@step(r'the local probabilities are "(.*)"')
def the_local_probabilities_are(step, prediction):
    local_probabilities = world.local_probabilities
    expected_probabilities = [float(p) for p in json.loads(prediction)]

    for local, expected in zip(local_probabilities, expected_probabilities):
        assert_almost_equal(local, expected, places=4)

#@step(r'the local ensemble prediction is "(.*)"')
def the_local_ensemble_prediction_is(step, prediction):
    if (isinstance(world.local_prediction, list) or
        isinstance(world.local_prediction, tuple)):
        local_prediction = world.local_prediction[0]
    elif isinstance(world.local_prediction, dict):
        local_prediction = world.local_prediction['prediction']
    else:
        local_prediction = world.local_prediction
    local_model = world.local_ensemble
    if local_model.regression:
        assert_almost_equal(local_prediction, float(prediction), places=5)
    else:
        eq_(local_prediction, prediction)

#@step(r'the local probability is "(.*)"')
def the_local_probability_is(step, probability):
    probability =  round(float(probability), 4)
    local_probability = world.local_prediction["probability"]

#@step(r'I create a local multi model')
def i_create_a_local_multi_model(step):
    world.local_model = MultiModel(world.list_of_models)

#@step(r'I create a batch prediction for "(.*)" and save it in "(.*)"')
def i_create_a_batch_prediction(step, input_data_list, directory):
    if len(directory) > 0 and not os.path.exists(directory):
        os.makedirs(directory)
    input_data_list = eval(input_data_list)
    assert isinstance(input_data_list, list)
    world.local_model.batch_predict(input_data_list, directory)

#@step(r'I combine the votes in "(.*)"')
def i_combine_the_votes(step, directory):
    world.votes = world.local_model.batch_votes(directory)

#@step(r'the plurality combined predictions are "(.*)"')
def the_plurality_combined_prediction(step, predictions):
    predictions = eval(predictions)
    for i in range(len(world.votes)):
        combined_prediction = world.votes[i].combine()
        check_prediction(combined_prediction, predictions[i])

#@step(r'the confidence weighted predictions are "(.*)"')
def the_confidence_weighted_prediction(step, predictions):
    predictions = eval(predictions)
    for i in range(len(world.votes)):
        combined_prediction = world.votes[i].combine(1)
        eq_(combined_prediction, predictions[i])

#@step(r'I create a local logistic regression model$')
def i_create_a_local_logistic_model(step):
    world.local_model = LogisticRegression(world.logistic_regression)


#@step(r'I create a local topic model$')
def i_create_a_local_topic_model(step):
    world.local_topic_model = TopicModel(world.topic_model)

#@step(r'the topic distribution is "(.*)"$')
def the_topic_distribution_is(step, distribution):
    eq_(json.loads(distribution),
        world.topic_distribution['topic_distribution']['result'])


#@step(r'the local topic distribution is "(.*)"')
def the_local_topic_distribution_is(step, distribution):
    distribution = json.loads(distribution)
    for index, topic_dist in enumerate(world.local_topic_distribution):
        assert_almost_equal(topic_dist["probability"], distribution[index],
                            places=5)

#@step(r'the association set is like file "(.*)"')
def the_association_set_is_like_file(step, filename):
    filename = res_filename(filename)
    result = world.association_set.get("association_set",{}).get("result", [])
    """ Uncomment if different text settings are used
    with open(filename, "w") as filehandler:
        json.dump(result, filehandler)
    """
    with open(filename) as filehandler:
        file_result = json.load(filehandler)
    eq_(result, file_result)

#@step(r'I create a local association set$')
def i_create_a_local_association_set(step, data):
    data = json.loads(data)
    world.local_association_set = world.local_association.association_set( \
        data)

#@step(r'the local association set is like file "(.*)"')
def the_local_association_set_is_like_file(step, filename):
    filename = res_filename(filename)
    """ Uncomment if different text settings are used
    with open(filename, "w") as filehandler:
        json.dump(result, filehandler)
    """
    with open(filename) as filehandler:
        file_result = json.load(filehandler)
    eq_(world.local_association_set, file_result)
