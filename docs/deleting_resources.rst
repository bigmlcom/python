Deleting Resources
==================

Resources can be deleted individually using the corresponding method for
each type of resource.

.. code-block:: python

    api.delete_source(source)
    api.delete_dataset(dataset)
    api.delete_model(model)
    api.delete_prediction(prediction)
    api.delete_evaluation(evaluation)
    api.delete_ensemble(ensemble)
    api.delete_batch_prediction(batch_prediction)
    api.delete_cluster(cluster)
    api.delete_centroid(centroid)
    api.delete_batch_centroid(batch_centroid)
    api.delete_anomaly(anomaly)
    api.delete_anomaly_score(anomaly_score)
    api.delete_batch_anomaly_score(batch_anomaly_score)
    api.delete_sample(sample)
    api.delete_correlation(correlation)
    api.delete_statistical_test(statistical_test)
    api.delete_logistic_regression(logistic_regression)
    api.delete_linear_regression(linear_regression)
    api.delete_association(association)
    api.delete_association_set(association_set)
    api.delete_topic_model(topic_model)
    api.delete_topic_distribution(topic_distribution)
    api.delete_batch_topic_distribution(batch_topic_distribution)
    api.delete_time_series(time_series)
    api.delete_forecast(forecast)
    api.delete_fusion(fusion)
    api.delete_pca(pca)
    api.delete_deepnet(deepnet)
    api.delete_projection(projection)
    api.delete_batch_projection(batch_projection)
    api.delete_project(project)
    api.delete_script(script)
    api.delete_library(library)
    api.delete_execution(execution)
    api.delete_external_connector(external_connector)


Each of the calls above will return a dictionary with the following
keys:

-  **code** If the request is successful, the code will be a
   ``bigml.api.HTTP_NO_CONTENT`` (204) status code. Otherwise, it wil be
   one of the standard HTTP error codes. See the `documentation on
   status codes <https://bigml.com/api/status_codes>`_ for more
   info.
-  **error** If the request does not succeed, it will contain a
   dictionary with an error code and a message. It will be ``None``
   otherwise.
