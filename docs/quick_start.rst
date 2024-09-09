Quick Start
===========

Imagine that you want to use `this csv
file <https://static.bigml.com/csv/iris.csv>`_ containing the `Iris
flower dataset <http://en.wikipedia.org/wiki/Iris_flower_data_set>`_ to
predict the species of a flower whose ``petal length`` is ``2.45`` and
whose ``petal width`` is ``1.75``. A preview of the dataset is shown
below. It has 4 numeric fields: ``sepal length``, ``sepal width``,
``petal length``, ``petal width`` and a categorical field: ``species``.
By default, BigML considers the last field in the dataset as the
objective field (i.e., the field that you want to generate predictions
for).

::

    sepal length,sepal width,petal length,petal width,species
    5.1,3.5,1.4,0.2,Iris-setosa
    4.9,3.0,1.4,0.2,Iris-setosa
    4.7,3.2,1.3,0.2,Iris-setosa
    ...
    5.8,2.7,3.9,1.2,Iris-versicolor
    6.0,2.7,5.1,1.6,Iris-versicolor
    5.4,3.0,4.5,1.5,Iris-versicolor
    ...
    6.8,3.0,5.5,2.1,Iris-virginica
    5.7,2.5,5.0,2.0,Iris-virginica
    5.8,2.8,5.1,2.4,Iris-virginica

You can easily generate a prediction following these steps:

.. code-block:: python

    from bigml.api import BigML

    api = BigML()

    source = api.create_source('./data/iris.csv')
    dataset = api.create_dataset(source)
    model = api.create_model(dataset)
    prediction = api.create_prediction(model, \
        {"petal width": 1.75, "petal length": 2.45})

You can then print the prediction using the ``pprint`` method:

.. code-block:: python

    >>> api.pprint(prediction)
    species for {"petal width": 1.75, "petal length": 2.45} is Iris-setosa

Certainly, any of the resources created in BigML can be configured using
several arguments described in the `API documentation <https://bigml.com/api>`_.
Any of these configuration arguments can be added to the ``create`` method
as a dictionary in the last optional argument of the calls:

.. code-block:: python

    from bigml.api import BigML

    api = BigML()

    source_args = {"name": "my source",
         "source_parser": {"missing_tokens": ["NULL"]}}
    source = api.create_source('./data/iris.csv', source_args)
    dataset_args = {"name": "my dataset"}
    dataset = api.create_dataset(source, dataset_args)
    model_args = {"objective_field": "species"}
    model = api.create_model(dataset, model_args)
    prediction_args = {"name": "my prediction"}
    prediction = api.create_prediction(model, \
        {"petal width": 1.75, "petal length": 2.45},
        prediction_args)

The ``iris`` dataset has a small number of instances, and usually will be
instantly created, so the ``api.create_`` calls will probably return the
finished resources outright. As BigML's API is asynchronous,
in general you will need to ensure
that objects are finished before using them by using ``api.ok``.

.. code-block:: python

    from bigml.api import BigML

    api = BigML()

    source = api.create_source('./data/iris.csv')
    api.ok(source)
    dataset = api.create_dataset(source)
    api.ok(dataset)
    model = api.create_model(dataset)
    api.ok(model)
    prediction = api.create_prediction(model, \
        {"petal width": 1.75, "petal length": 2.45})

Note that the prediction
call is not followed by the ``api.ok`` method. Predictions are so quick to be
generated that, unlike the
rest of resouces, will be generated synchronously as a finished object.

Alternatively to the ``api.ok`` method, BigML offers
`webhooks <https://bigml.com/api/requests?id=webhooks>`_ that can be set
when creating a resource and will call the url of you choice when the
finished or failed event is reached. A secret can be included in the call to
verify the webhook call authenticity, and a

.. code-block:: python

    bigml.webhooks.check_signature(request, signature)

function is offered to that end. As an example, this snippet creates a source
and sets a webhook to call ``https://my_webhook.com/endpoint`` when finished:

.. code-block:: python

    from bigml.api import BigML
    api = BigML()
    # using a webhook with a secret
    api.create_source("https://static.bigml.com/csv/iris.csv",
            {"webhook": {"url": "https://my_webhook.com/endpoint",
                     "secret": "mysecret"}})


The ``iris`` prediction example assumed that your objective
field (the one you want to predict) is the last field in the dataset.
If that's not he case, you can explicitly
set the name of this field in the creation call using the ``objective_field``
argument:


.. code-block:: python

    from bigml.api import BigML

    api = BigML()

    source = api.create_source('./data/iris.csv')
    api.ok(source)
    dataset = api.create_dataset(source)
    api.ok(dataset)
    model = api.create_model(dataset, {"objective_field": "species"})
    api.ok(model)
    prediction = api.create_prediction(model, \
        {'sepal length': 5, 'sepal width': 2.5})


You can also generate an evaluation for the model by using:

.. code-block:: python

    test_source = api.create_source('./data/test_iris.csv')
    api.ok(test_source)
    test_dataset = api.create_dataset(test_source)
    api.ok(test_dataset)
    evaluation = api.create_evaluation(model, test_dataset)
    api.ok(evaluation)


The API object also offers the ``create``, ``get``, ``update`` and ``delete``
generic methods to manage all type of resources. The type of resource to be
created is passed as first argument to the ``create`` method;

.. code-block:: python

    from bigml.api import BigML

    api = BigML()

    source = api.create('source', './data/iris.csv')
    source = api.update(source, {"name": "my new source name"})

Note that these methods don't need the ``api.ok`` method to be called
to wait for the resource to be finished.
The method waits internally for it by default.
This can be avoided by using  ``finished=False`` as one of the arguments.


.. code-block:: python

    from bigml.api import BigML

    api = BigML()

    source = api.create('source', './data/iris.csv')
    dataset = api.create('dataset', source, finished=False) # unfinished
    api.ok(dataset) # waiting explicitly for the dataset to finish
    dataset = api.update(dataset, {"name": "my_new_dataset_name"},
                         finised=False)
    api.ok(dataset)

As an example for the ``delete`` and ``get`` methods, we could
create a batch prediction, put the predictions in a
dataset object and delete the ``batch_prediction``.

.. code-block:: python

    from bigml.api import BigML

    api = BigML()

    batch_prediction = api.create('batchprediction',
                                  'model/5f3c3d2b5299637102000882',
                                  'dataset/5f29a563529963736c0116e9',
                                  args={"output_dataset": True})
    batch_prediction_dataset = api.get(batch_prediction["object"][ \
        "output_dataset_resource"])
    api.delete(batch_prediction)

If you set the ``storage`` argument in the ``api`` instantiation:

.. code-block:: python

    api = BigML(storage='./storage')

all the generated, updated or retrieved resources will be automatically
saved to the chosen directory. Once they are stored locally, the
``retrieve_resource`` method will look for the resource information
first in the local storage before trying to download the information from
the API.

.. code-block:: python

    dataset = api.retrieve_resource("dataset/5e8e5672c7736e3d830037b5",
                                    query_string="limit=-1")


Alternatively, you can use the ``export`` method to explicitly
download the JSON information
that describes any of your resources in BigML to a particular file:

.. code-block:: python

    api.export('model/5acea49a08b07e14b9001068',
               filename="my_dir/my_model.json")

This example downloads the JSON for the model and stores it in
the ``my_dir/my_model.json`` file.

In the case of models that can be represented in a `PMML` syntax, the
export method can be used to produce the corresponding `PMML` file.

.. code-block:: python

    api.export('model/5acea49a08b07e14b9001068',
               filename="my_dir/my_model.pmml",
               pmml=True)

You can also retrieve the last resource with some previously given tag:

.. code-block:: python

     api.export_last("foo",
                     resource_type="ensemble",
                     filename="my_dir/my_ensemble.json")

which selects the last ensemble that has a ``foo`` tag. This mechanism can
be specially useful when retrieving retrained models that have been created
with a shared unique keyword as tag.

For a descriptive overview of the steps that you will usually need to
follow to model
your data and obtain predictions, please see the `basic Workflow sketch
<api_sketch.html>`_
document. You can also check other simple examples in the following documents:

- `model 101 <101_model.html>`_
- `logistic regression 101 <101_logistic_regression.html>`_
- `linear regression 101 <101_linear_regression.html>`_
- `ensemble 101 <101_ensemble.html>`_
- `cluster 101 <101_cluster>`_
- `anomaly detector 101 <101_anomaly.html>`_
- `association 101 <101_association.html>`_
- `topic model 101 <101_topic_model.html>`_
- `deepnet 101 <101_deepnet.html>`_
- `time series 101 <101_ts.html>`_
- `fusion 101 <101_fusion.html>`_
- `optiml 101 <101_optiml.html>`_
- `PCA 101 <101_pca.html>`_
- `scripting 101 <101_scripting.html>`_

And for examples on Image Processing:

- `Images Classification 101 <101_images_classification.html>`_
- `Object Detection 101<101_object_detection.html>`_
- `Images Feature Extraction 101 <101_images_feature_extraction.html>`_
