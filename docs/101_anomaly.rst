BigML Bindings: 101 - Using an anomaly detector
===============================================

Following the schema described in the `prediction workflow <api_sketch.html>`_,
document, this is the code snippet that shows the minimal workflow to
create an anomaly detector to produce a single anomaly score.

.. code-block:: python

    from bigml.api import BigML
    # step 0: creating a connection to the service (default credentials)
    api = BigML()
    # step 1: creating a source from the data in your local "data/iris.csv" file
    source = api.create_source("data/iris.csv")
    # waiting for the source to be finished. Results will be stored in `source`
    api.ok(source)
    # step 3: creating a dataset from the previously created `source`
    dataset = api.create_dataset(source)
    # waiting for the dataset to be finished
    api.ok(dataset)
    # step 5: creating an anomaly detector
    model = api.create_model(anomaly)
    # waiting for the anomaly detector to be finished
    api.ok(anomaly)
    # the input data to score
    input_data = {"petal length": 4, "sepal length": 2, "petal width": 1,
                  "sepal witdh": 3}
    # assigning an anomaly score to it
    anomaly_score = api.create_anomaly_score(anomaly, input_data)

If you want to assign scores to the original dataset (or a different dataset),
you can do so creating
a `batch_anomaly_score` resource. In the example, we'll be assuming you already
created an `anomaly` following the steps 0 to 5 in the previous snippet and
that you want to score the same data you used in the anomaly detector.

.. code-block:: python

    test_dataset = dataset
    # step 10: creating a batch anomaly score
    batch_anomaly_score = api.create_batch_anomaly_score(anomaly, test_dataset)
    # waiting for the batch_anomaly_score to be finished
    api.ok(batch_anomaly_score)
    # downloading the results to your computer
    api.download_batch_anomaly_score(batch_anomaly_score,
                                     filename='my_dir/my_anomaly_scores.csv')

The batch anomaly score output (as well as any of the resources created)
can be configured using additional arguments in the corresponding create calls.
Check the `API documentation <https://bigml.com/api/>`_ to learn about the
available configuration options for any BigML resource.

You can also score your data locally using the `Anomaly`
class in the `anomaly` module. A simple example of that is:

.. code-block:: python

    from bigml.anomaly import Anomaly
    local_anomaly = Anomaly("anomaly/5968ec46983efc21b000001b")
    # assigning the anomaly score to some input data
    local_time_series.anomaly_score({"petal length": 4, "sepal length": 2,
                                     "petal width": 1, "sepal witdh": 3})

Every modeling resource in BigML has its corresponding local class. Check
the `Local resources <index.html#local_resources>`_ section of the
documentation to learn more about them.
