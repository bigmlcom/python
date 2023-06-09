# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled,unused-argument,no-member
#pylint: disable=locally-disabled,pointless-string-statement
#
# Copyright 2012-2023 BigML
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

from zipfile import ZipFile
from bigml.model import Model, cast_prediction
from bigml.logistic import LogisticRegression
from bigml.cluster import Cluster
from bigml.anomaly import Anomaly
from bigml.association import Association
from bigml.multimodel import MultiModel
from bigml.topicmodel import TopicModel
from bigml.deepnet import Deepnet
from bigml.linear import LinearRegression
from bigml.supervised import SupervisedModel
from bigml.local_model import LocalModel
from bigml.fusion import Fusion
from bigml.pca import PCA


from .create_prediction_steps import check_prediction
from .world import world, res_filename, eq_, approx_, ok_


def extract_zip(input_zip):
    """Extracting file names in zip"""
    with ZipFile(input_zip) as zip_handler:
        return {name: zip_handler.read(name) for name in \
            zip_handler.namelist()}


def i_retrieve_a_list_of_remote_models(step, tag):
    """Step: I retrieve a list of remote models tagged with <tag>"""
    world.list_of_models = [ \
        world.api.get_model(model['resource']) for model in
        world.api.list_models(query_string="project=%s;tags__in=%s" % \
            (world.project_id, tag))['objects']]


def i_retrieve_a_list_of_remote_logistic_regressions(step, tag):
    """Step: I retrieve a list of remote logistic regression tagged with
    <tag>
    """
    world.list_of_models = [ \
        world.api.get_logistic_regression(model['resource']) for model in
        world.api.list_logistic_regressions( \
            query_string="project=%s;tags__in=%s" % \
                (world.project_id, tag))['objects']]


def i_retrieve_a_list_of_remote_linear_regressions(step, tag):
    """Step: I retrieve a list of remote linear regression tagged with <tag>"""
    world.list_of_models = [ \
        world.api.get_linear_regression(model['resource']) for model in
        world.api.list_linear_regressions( \
            query_string="project=%s;tags__in=%s" % \
                (world.project_id, tag))['objects']]


def i_create_a_local_model_from_file(step, model_file):
    """Step: I create a local model from a <model_file> file"""
    step.bigml["local_model"] = Model(res_filename(model_file))


def i_create_a_local_deepnet_from_zip_file(step, deepnet_file,
                                           operation_settings=None):
    """Step: I create a local deepnet from a <deepnet_file> file"""
    zipped_files = extract_zip(res_filename(deepnet_file))
    deepnet = json.loads(list(zipped_files.values())[0])
    step.bigml["local_model"] = Deepnet(deepnet,
                                operation_settings=operation_settings)


def i_create_a_local_supervised_model_from_file(step, model_file):
    """Step: I create a local supervised model from a <model_file> file"""
    step.bigml["local_model"] = SupervisedModel(res_filename(model_file))


def i_create_a_local_model(step, pre_model=False):
    """Step: I create a local model"""
    step.bigml["local_model"] = Model(world.model)
    if pre_model:
        step.bigml["local_pipeline"] = step.bigml["local_model"].data_transformations()


def i_create_a_local_fusion(step):
    """Step: I create a local fusion"""
    step.bigml["local_model"] = Fusion(world.fusion['resource'])
    step.bigml["local_ensemble"] = None


def i_create_a_local_supervised_model(step, model_type=None):
    """Step: I create a local supervised model"""
    if model_type is None:
        model_type = "model"
    model = getattr(world, model_type)
    step.bigml["local_model"] = SupervisedModel(model)


def i_create_a_local_bigml_model(step, model_type=None):
    """Step: I create a local BigML model"""
    if model_type is None:
        model_type = "model"
    model = getattr(world, model_type)
    step.bigml["local_model"] = LocalModel(model)


def i_create_a_local_bigml_model_prediction(step, data=None,
    prediction_type=None, **kwargs):
    """Step: I create a local prediction for <data>"""
    if data is None:
        data = "{}"
    data = json.loads(data)
    if prediction_type is None:
        prediction_type = "prediction"
    if kwargs is None:
        kwargs = {}
    kwargs.update({"full": True})
    step.bigml["local_%s" % prediction_type] = step.bigml[
        "local_model"].predict(data, **kwargs)


def the_local_bigml_prediction_is(step, value, prediction_type=None, key=None,
    precision=None):
    prediction = step.bigml["local_%s" % prediction_type]
    if key is not None:
        prediction = prediction[key]
    eq_(value, prediction, precision=precision)


def i_create_a_local_prediction_with_confidence(step, data=None,
                                                pre_model=None):
    """Step: I create a local prediction for <data> with confidence"""
    if data is None:
        data = "{}"
    input_data = json.loads(data)
    if pre_model is not None:
        input_data = pre_model.transform([input_data])[0]
    step.bigml["local_prediction"] = step.bigml["local_model"].predict(
        input_data, full=True)


def i_create_a_local_prediction(step, data=None, pre_model=None):
    """Step: I create a local prediction for <data>"""
    if data is None:
        data = "{}"
    data = json.loads(data)
    if pre_model is not None:
        data = pre_model.transform([data])[0]
    step.bigml["local_prediction"] = step.bigml["local_model"].predict(data, full=True)


def i_create_a_local_regions_prediction(step, image_file=None):
    """Step: I create a local images prediction for <image_file>"""
    if image_file is None:
        return None
    data = res_filename(image_file)
    step.bigml["local_prediction"] = step.bigml["local_model"].predict(data, full=True)
    return step.bigml["local_prediction"]


def i_create_a_local_prediction_op(step, data=None, operating_point=None):
    """Step: I create a local prediction for <data> in operating point
    <operating_point>
    """
    if data is None:
        data = "{}"
    ok_(operating_point is not None)
    data = json.loads(data)
    step.bigml["local_prediction"] = step.bigml["local_model"].predict( \
        data, operating_point=operating_point)


def i_create_a_local_ensemble_prediction_op(step, data=None, operating_point=None):
    """Step: I create a local ensemble prediction for <data> in operating
    point <operating_point>
    """
    if data is None:
        data = "{}"
    ok_(operating_point is not None)
    data = json.loads(data)
    step.bigml["local_prediction"] = step.bigml["local_ensemble"].predict( \
        data, operating_point=operating_point)


def i_create_local_probabilities(step, data=None):
    """Step: I create local probabilities for <data>"""
    if data is None:
        data = "{}"
    data = json.loads(data)
    model = step.bigml["local_model"]
    step.bigml["local_probabilities"] = model.predict_probability(
        data, compact=True)


def i_create_a_local_ensemble_prediction(step, data=None):
    """Step: I create a local ensemble prediction for <data>"""
    if data is None:
        data = "{}"
    data = json.loads(data)
    step.bigml["local_prediction"] = step.bigml["local_ensemble"].predict(data)


def i_create_a_local_deepnet_prediction(step, data=None, image_fields=None,
                                        full=False):
    """Step: I create a local deepnet prediction for <data>"""
    if data is None:
        data = "{}"
    if image_fields is None:
        image_fields = []
    data = json.loads(data)
    for field in image_fields:
        if field in data:
            data[field] = res_filename(data[field])
    step.bigml["local_prediction"] = step.bigml["local_model"].predict(data, full=full)


def i_create_a_local_deepnet_prediction_with_op(step, data=None,
                                                operating_point=None):
    """Step: I create a local deepnet prediction with operating point
    for <data>
    """
    if data is None:
        data = "{}"
    data = json.loads(data)
    step.bigml["local_prediction"] = step.bigml["local_model"].predict( \
        data, operating_point=operating_point)


def i_create_a_local_median_prediction(step, data=None):
    """Step: I create a local prediction using median for <data>"""
    if data is None:
        data = "{}"
    data = json.loads(data)
    step.bigml["local_prediction"] = step.bigml["local_model"].predict(data, full=True)


def i_create_a_local_mm_median_batch_prediction(step, data=None):
    """Step: I create a local multimodel batch prediction using median
    for <data>
    """
    if data is None:
        data = "{}"
    data = json.loads(data)
    step.bigml["local_prediction"] = step.bigml["local_model"].batch_predict(
        [data], to_file=False, use_median=True)[0].predictions[0]['prediction']


def i_create_a_local_proportional_median_prediction(step, data=None):
    """Step: I create a proportional missing strategy local prediction
    using median for <data>
    """
    if data is None:
        data = "{}"
    data = json.loads(data)
    step.bigml["local_prediction"] = step.bigml["local_model"].predict( \
        data, missing_strategy=1, full=True)


def i_create_a_local_cluster(step, pre_model=False):
    """Step: I create a local cluster"""
    step.bigml["local_cluster"] = Cluster(world.cluster["resource"])
    if pre_model:
        step.bigml["local_pipeline"] = step.bigml["local_cluster"].data_transformations()


def i_create_a_local_centroid(step, data=None, pre_model=None):
    """Step: I create a local centroid for <data>"""
    if data is None:
        data = "{}"
    data = json.loads(data)
    for key, value in list(data.items()):
        if value == "":
            del data[key]
    if pre_model is not None:
        data = pre_model.transform([data])[0]
    step.bigml["local_centroid"] = step.bigml["local_cluster"].centroid(data)


def the_local_centroid_is(step, centroid, distance):
    """Step: the local centroid is <centroid> with distance <distance>"""
    check_prediction(step.bigml["local_centroid"]['centroid_name'], centroid)
    check_prediction(step.bigml["local_centroid"]['distance'], distance)


def i_create_a_local_anomaly(step, pre_model=False):
    """Step: I create a local anomaly detector"""
    step.bigml["local_anomaly"] = Anomaly(world.anomaly["resource"])
    if pre_model:
        step.bigml["local_pipeline"] = step.bigml["local_anomaly"].data_transformations()


def i_create_a_local_anomaly_score(step, input_data, pre_model=None):
    """Step: I create a local anomaly score for <data>"""
    input_data = json.loads(input_data)
    if pre_model is not None:
        input_data = pre_model.transform([input_data])[0]
    step.bigml["local_anomaly_score"] = step.bigml["local_anomaly"].anomaly_score( \
        input_data)


def the_local_anomaly_score_is(step, score):
    """Step: the local anomaly score is <score>"""
    eq_(str(round(step.bigml["local_anomaly_score"], 2)),
        str(round(float(score), 2)))


def i_create_a_local_association(step, pre_model=False):
    """Step: I create a local association"""
    step.bigml["local_association"] = Association(world.association)
    if pre_model:
        step.bigml["local_pipeline"] = step.bigml["local_association"].data_transformations()


def i_create_a_proportional_local_prediction(step, data=None):
    """Step: I create a proportional missing strategy local prediction for
    <data>
    """
    if data is None:
        data = "{}"
    data = json.loads(data)
    step.bigml["local_prediction"] = step.bigml["local_model"].predict(
        data, missing_strategy=1, full=True)
    step.bigml["local_prediction"] = cast_prediction(step.bigml["local_prediction"],
                                             to="list",
                                             confidence=True)


def i_create_a_prediction_from_a_multi_model(step, data=None):
    """Step: I create a prediction from a multi model for <data>"""
    if data is None:
        data = "{}"
    data = json.loads(data)
    step.bigml["local_prediction"] = step.bigml["local_model"].predict(data)


def i_create_a_batch_prediction_from_a_multi_model(step, data=None):
    """Step: I create a batch multimodel prediction for <data>"""
    if data is None:
        data = "[{}]"
    data = json.loads(data)
    step.bigml["local_prediction"] = step.bigml["local_model"].batch_predict(data,
                                                             to_file=False)

def the_batch_mm_predictions_are(step, predictions):
    """Step: the predictions are <predictions>"""
    if predictions is None:
        predictions = "[{}]"
    predictions = json.loads(predictions)
    for index, prediction in enumerate(predictions):
        multivote = step.bigml["local_prediction"][index]
        for mv_prediction in multivote.predictions:
            eq_(mv_prediction['prediction'], prediction)


def the_multiple_local_prediction_is(step, prediction):
    """Step: the multiple local prediction is <prediction>"""
    local_prediction = step.bigml["local_prediction"]
    prediction = json.loads(prediction)
    eq_(local_prediction, prediction)


def the_local_prediction_confidence_is(step, confidence):
    """Step: the local prediction's confidence is <confidence>"""
    if isinstance(step.bigml["local_prediction"], (list, tuple)):
        local_confidence = step.bigml["local_prediction"][1]
    else:
        local_confidence = step.bigml["local_prediction"].get('confidence', \
            step.bigml["local_prediction"].get('probability'))
    local_confidence = round(float(local_confidence), 4)
    confidence = round(float(confidence), 4)
    eq_(local_confidence, confidence)


def the_highest_local_prediction_confidence_is(
    step, input_data, confidence, missing_strategy=None):
    """Step: the highest local prediction's confidence for <input_data> is
    <confidence>"""
    input_data = json.loads(input_data)
    kwargs = {}
    if missing_strategy is not None:
        kwargs.update({"missing_strategy": missing_strategy})
    local_confidence = step.bigml["local_model"].predict_confidence(input_data,
                                                            **kwargs)
    if isinstance(local_confidence, dict):
        local_confidence = round(float(local_confidence["confidence"]), 4)
    else:
        local_confidence = round(float(max([pred["confidence"] for pred in local_confidence])), 4)
    confidence = round(float(confidence), 4)
    eq_(local_confidence, confidence)


def the_local_prediction_is(step, prediction, precision=4):
    """Step: the local prediction is <prediction>"""
    if isinstance(step.bigml["local_prediction"], (list, tuple)):
        local_prediction = step.bigml["local_prediction"][0]
    elif isinstance(step.bigml["local_prediction"], dict):
        local_prediction = step.bigml["local_prediction"]['prediction']
    else:
        local_prediction = step.bigml["local_prediction"]
    if hasattr(world, "local_ensemble") and step.bigml["local_ensemble"] is not None:
        step.bigml["local_model"] = step.bigml["local_ensemble"]
    if (hasattr(step.bigml["local_model"], "regression") and \
            step.bigml["local_model"].regression) or \
            (isinstance(step.bigml["local_model"], MultiModel) and \
            step.bigml["local_model"].models[0].regression):
        local_prediction = round(float(local_prediction), precision)
        prediction = round(float(prediction), precision)
        approx_(local_prediction, float(prediction), precision=precision)
    else:
        if isinstance(local_prediction, str):
            eq_(local_prediction, prediction)
        else:
            if isinstance(prediction, str):
                prediction = float(prediction)
            eq_(round(local_prediction, precision),
                round(float(prediction), precision))


def the_local_regions_prediction_is(step, prediction):
    """Step: the local regions prediction is <prediction>"""
    prediction = json.loads(prediction)
    eq_(prediction, step.bigml["local_prediction"])


def the_local_probabilities_are(step, prediction):
    """Step: the local probabilities are <prediction>"""
    local_probabilities = step.bigml["local_probabilities"]
    expected_probabilities = [float(p) for p in json.loads(prediction)]

    for local, expected in zip(local_probabilities, expected_probabilities):
        approx_(local, expected, precision=4)


def the_local_ensemble_prediction_is(step, prediction):
    """Step: the local ensemble prediction is <prediction>"""
    if isinstance(step.bigml["local_prediction"], (list, tuple)):
        local_prediction = step.bigml["local_prediction"][0]
    elif isinstance(step.bigml["local_prediction"], dict):
        local_prediction = step.bigml["local_prediction"]['prediction']
    else:
        local_prediction = step.bigml["local_prediction"]
    if step.bigml["local_ensemble"].regression:
        approx_(local_prediction, float(prediction), precision=5)
    else:
        eq_(local_prediction, prediction)


def the_local_probability_is(step, probability):
    """Step: the local probability is <probability>"""
    local_probability = step.bigml["local_prediction"]["probability"]
    if isinstance(probability, str):
        probability = float(probability)
    eq_(local_probability, probability, precision=4)


def eq_local_and_remote_probability(step):
    """Step: check local and remote probability"""
    local_probability = round(step.bigml["local_prediction"]["probability"], 3)
    remote_probability = round(world.prediction["probability"], 3)
    approx_(local_probability, remote_probability)


def i_create_a_local_multi_model(step):
    """Step: I create a local multi model"""
    step.bigml["local_model"] = MultiModel(world.list_of_models)
    step.bigml["local_ensemble"] = None


def i_create_a_batch_prediction(step, input_data_list, directory):
    """Step: I create a batch prediction for <input_data_list> and save it
    in <directory>
    """
    if len(directory) > 0 and not os.path.exists(directory):
        os.makedirs(directory)
    input_data_list = json.loads(input_data_list)
    ok_(isinstance(input_data_list, list))
    step.bigml["local_model"].batch_predict(input_data_list, directory)


def i_combine_the_votes(step, directory):
    """Step: I combine the votes in <directory>"""
    world.votes = step.bigml["local_model"].batch_votes(directory)


def the_plurality_combined_prediction(step, predictions):
    """Step: the plurality combined predictions are <predictions>"""
    predictions = json.loads(predictions)
    for i, votes_row in enumerate(world.votes):
        combined_prediction = votes_row.combine()
        check_prediction(combined_prediction, predictions[i])


def the_confidence_weighted_prediction(step, predictions):
    """Step: the confidence weighted predictions are <predictions>"""
    predictions = json.loads(predictions)
    for i, votes_row in enumerate(world.votes):
        combined_prediction = votes_row.combine(1)
        eq_(combined_prediction, predictions[i])


def i_create_a_local_logistic_model(step, pre_model=False):
    """Step: I create a local logistic regression model"""
    step.bigml["local_model"] = LogisticRegression(world.logistic_regression)
    if pre_model:
        step.bigml["local_pipeline"] = step.bigml[
            "local_model"].data_transformations()
    if hasattr(world, "local_ensemble"):
        step.bigml["local_ensemble"] = None


def i_create_a_local_deepnet(step):
    """Step: I create a local deepnet model"""
    step.bigml["local_model"] = Deepnet({"resource": world.deepnet['resource'],
                                 "object": world.deepnet})
    if hasattr(world, "local_ensemble"):
        step.bigml["local_ensemble"] = None


def i_create_a_local_topic_model(step):
    """Step: I create a local topic model"""
    step.bigml["local_topic_model"] = TopicModel(world.topic_model)


def the_topic_distribution_is(step, distribution):
    """Step: the topic distribution is <distribution>"""
    eq_(json.loads(distribution),
        world.topic_distribution['topic_distribution']['result'])


def the_local_topic_distribution_is(step, distribution):
    """Step: the local topic distribution is <distribution>"""
    distribution = json.loads(distribution)
    for index, topic_dist in enumerate(step.bigml["local_topic_distribution"]):
        approx_(topic_dist["probability"], distribution[index])


def the_association_set_is_like_file(step, filename):
    """Step: the association set is like file <filename>"""
    filename = res_filename(filename)
    result = world.association_set.get("association_set",{}).get("result", [])
    """ Uncomment if different text settings are used
    with open(filename, "w") as filehandler:
        json.dump(result, filehandler)
    """
    with open(filename) as filehandler:
        file_result = json.load(filehandler)
    eq_(result, file_result)


def i_create_a_local_association_set(step, data, pre_model=None):
    """Step: I create a local association set"""
    data = json.loads(data)
    if pre_model is not None:
        data = pre_model.transform([data])[0]
    step.bigml["local_association_set"] = step.bigml["local_association"].association_set( \
        data)


def the_local_association_set_is_like_file(step, filename):
    """Step: the local association set is like file <filename>"""
    filename = res_filename(filename)
    """ Uncomment if different text settings are used
    with open(filename, "w") as filehandler:
        json.dump(result, filehandler)
    """
    with open(filename) as filehandler:
        file_result = json.load(filehandler)
        for index, result in enumerate(file_result):
            approx_(result['score'], step.bigml["local_association_set"][
                index]['score'])
            eq_(result['rules'],
                step.bigml["local_association_set"][index]['rules'])


def i_create_a_local_prediction_op_kind(step, data=None, operating_kind=None):
    """Step: I create a local prediction for <data> in operating kind
    <operating_kind>
    """
    if data is None:
        data = "{}"
    ok_(operating_kind is not None)
    data = json.loads(data)
    step.bigml["local_prediction"] = step.bigml["local_model"].predict( \
        data, operating_kind=operating_kind)


def i_create_a_local_ensemble_prediction_op_kind( \
        step, data=None, operating_kind=None):
    """Step: I create a local ensemble prediction for <data> in operating
    kind <operating_kind>"""
    if data is None:
        data = "{}"
    ok_(operating_kind is not None)
    data = json.loads(data)
    step.bigml["local_prediction"] = step.bigml["local_ensemble"].predict( \
        data, operating_kind=operating_kind)


def i_create_a_local_deepnet_prediction_op_kind( \
        step, data=None, operating_kind=None):
    """Step: I create a local deepnet for <data> in operating kind
    <operating_kind>
    """
    if data is None:
        data = "{}"
    ok_(operating_kind is not None)
    data = json.loads(data)
    step.bigml["local_prediction"] = step.bigml["local_model"].predict( \
        data, operating_kind=operating_kind)


def i_create_a_local_logistic_prediction_op_kind( \
        step, data=None, operating_kind=None):
    """Step: I create a local logistic regression for <data> in operating
    kind <operating_kind>
    """
    if data is None:
        data = "{}"
    ok_(operating_kind is not None)
    data = json.loads(data)
    step.bigml["local_prediction"] = step.bigml["local_model"].predict( \
        data, operating_kind=operating_kind)


def create_local_pca(step, pre_model=False):
    """Step: I create a local PCA"""
    step.bigml["local_pca"] = PCA(world.pca["resource"])
    if pre_model:
        step.bigml["local_pipeline"] = step.bigml["local_pca"].data_transformations()


def i_create_a_local_linear(step):
    """Step: I create a local linear regression"""
    step.bigml["local_model"] = LinearRegression(world.linear_regression["resource"])


def i_create_a_local_projection(step, data=None, pre_model=None):
    """Step: I create a local projection for <data>"""
    if data is None:
        data = "{}"
    data = json.loads(data)
    if pre_model is not None:
        data = pre_model.transform([data])[0]
    for key, value in list(data.items()):
        if value == "":
            del data[key]
    step.bigml["local_projection"] = step.bigml["local_pca"].projection(data, full=True)
    for name, value in list(step.bigml["local_projection"].items()):
        step.bigml["local_projection"][name] = round(value, 5)


def i_create_a_local_linear_prediction(step, data=None):
    """Step: I create a local linear regression prediction for <data>"""
    if data is None:
        data = "{}"
    data = json.loads(data)
    for key, value in list(data.items()):
        if value == "":
            del data[key]
    step.bigml["local_prediction"] = step.bigml["local_model"].predict(data, full=True)
    for name, value in list(step.bigml["local_prediction"].items()):
        if isinstance(value, float):
            step.bigml["local_prediction"][name] = round(value, 5)


def the_local_projection_is(step, projection):
    """Step: checking the local projection"""
    if projection is None:
        projection = "{}"
    projection = json.loads(projection)
    eq_(len(list(projection.keys())), len(list(step.bigml["local_projection"].keys())))
    for name, _ in list(projection.items()):
        eq_(step.bigml["local_projection"][name], projection[name],
            msg="local: %s, %s - expected: %s" % ( \
                name, step.bigml["local_projection"][name], projection[name]))
