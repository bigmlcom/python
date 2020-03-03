Updating Resources
==================

When you update a resource, it is returned in a dictionary exactly like
the one you get when you create a new one. However the status code will
be ``bigml.api.HTTP_ACCEPTED`` if the resource can be updated without
problems or one of the HTTP standard error codes otherwise.

.. code-block:: python

    api.update_source(source, {"name": "new name"})
    api.update_dataset(dataset, {"name": "new name"})
    api.update_model(model, {"name": "new name"})
    api.update_prediction(prediction, {"name": "new name"})
    api.update_evaluation(evaluation, {"name": "new name"})
    api.update_ensemble(ensemble, {"name": "new name"})
    api.update_batch_prediction(batch_prediction, {"name": "new name"})
    api.update_cluster(cluster, {"name": "new name"})
    api.update_centroid(centroid, {"name": "new name"})
    api.update_batch_centroid(batch_centroid, {"name": "new name"})
    api.update_anomaly(anomaly, {"name": "new name"})
    api.update_anomaly_score(anomaly_score, {"name": "new name"})
    api.update_batch_anomaly_score(batch_anomaly_score, {"name": "new name"})
    api.update_project(project, {"name": "new name"})
    api.update_correlation(correlation, {"name": "new name"})
    api.update_statistical_test(statistical_test, {"name": "new name"})
    api.update_logistic_regression(logistic_regression, {"name": "new name"})
    api.update_linear_regression(linear_regression, {"name": "new name"})
    api.update_association(association, {"name": "new name"})
    api.update_association_set(association_set, {"name": "new name"})
    api.update_topic_model(topic_model, {"name": "new name"})
    api.update_topic_distribution(topic_distribution, {"name": "new name"})
    api.update_batch_topic_distribution(\
        batch_topic_distribution, {"name": "new name"})
    api.update_time_series(\
        time_series, {"name": "new name"})
    api.update_forecast(\
        forecast, {"name": "new name"})
    api.update_deepnet(deepnet, {"name": "new name"})
    api.update_fusion(fusion, {"name": "new name"})
    api.update_pca(pca, {"name": "new name"})
    api.update_projection(projection, {"name": "new name"})
    api.update_batch_projection(batch_projection, {"name": "new name"})
    api.update_script(script, {"name": "new name"})
    api.update_library(library, {"name": "new name"})
    api.update_execution(execution, {"name": "new name"})
    api.update_external_connector(external_connector, {"name": "new name"})

Updates can change resource general properties, such as the ``name`` or
``description`` attributes of a dataset, or specific properties, like
the ``missing tokens`` (strings considered as missing values). As an example,
let's say that your source has a certain field whose contents are
numeric integers. BigML will assign a numeric type to the field, but you
might want it to be used as a categorical field. You could change
its type to ``categorical`` by calling:

.. code-block:: python

    api.update_source(source, \
        {"fields": {"000001": {"optype": "categorical"}}})

where ``000001`` is the field id that corresponds to the updated field.

Another usually needed update is changing a fields' ``non-preferred``
attribute,
so that it can be used in the modeling process:


.. code-block:: python

    api.update_dataset(dataset, {"fields": {"000001": {"preferred": True}}})

where you would be setting as ``preferred`` the field whose id is ``000001``.

You may also want to change the name of one of the clusters found in your
clustering:


.. code-block:: python

    api.update_cluster(cluster, \
        {"clusters": {"000001": {"name": "my cluster"}}})

which is changing the name of the cluster whose centroid id is ``000001`` to
``my_cluster``. Or, similarly, changing the name of one detected topic:


.. code-block:: python

    api.update_topic_model(topic_model, \
        {"topics": {"000001": {"name": "my topic"}}})


You will find detailed information about
the updatable attributes of each resource in
`BigML developer's documentation <https://bigml.com/api>`_.
