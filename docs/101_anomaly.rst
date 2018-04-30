BigML Bindings: 101 - Using an anomaly detector
===============================================

Following the schema described in the `prediction workflow <api_sketch.html>`_,
document, this is the code snippet that shows the minimal workflow to
create an anomaly detector to produce a single anomaly score.

.. code-block:: python

    from bigml.api import BigML
    # step 0: creating a connection to the service (default credentials)
    # check how to set your credentials in the Authentication section
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
    anomaly = api.create_anomaly(dataset)
    # waiting for the anomaly detector to be finished
    api.ok(anomaly)
    # the input data to score
    input_data = {"petal length": 4, "sepal length": 2, "petal width": 1,
                  "sepal witdh": 3}
    # assigning an anomaly score to it
    anomaly_score = api.create_anomaly_score(anomaly, input_data)

If you want to assign scores to the original dataset (or a different dataset),
you can do so by creating
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
For instance, to include all the information in the original dataset in the
output you would change `step 10` to:

.. code-block:: python

    batch_anomaly_score = api.create_batch_anomaly_score(anomaly, test_dataset,
                                                         {"all_fields": True})

Check the `API documentation <https://bigml.com/api/>`_ to learn about the
available configuration options for any BigML resource.

You can also score your data locally using the `Anomaly`
class in the `anomaly` module. A simple example of that is:

.. code-block:: python

    from bigml.anomaly import Anomaly
    local_anomaly = Anomaly("anomaly/5968ec46983efc21b000001b")
    # assigning the anomaly score to some input data
    local_anomaly.anomaly_score({"petal length": 4, "sepal length": 2,
                                 "petal width": 1, "sepal witdh": 3})

Or you could store first your anomaly information in a file and use that
file to create the local `Anomaly` object:

.. code-block:: python

    # downloading the anomaly detector JSON to a local file
    from bigml.api import BigML
    api = BigML()
    api.export("anomaly/5968ec46983efc21b000001b",
               "filename": "my_anomaly.json")
    # creating an anomaly object using the information in the file
    from bigml.anomaly import Anomaly
    local_anomaly = Anomaly("my_anomaly.json")
    # assigning the anomaly score to some input data
    local_anomaly.anomaly_score({"petal length": 4, "sepal length": 2,
                                 "petal width": 1, "sepal witdh": 3})

If you want to assign the anomaly score
locally for all the rows in a CSV file (first line
should contain the field headers):

.. code-block:: python

    import csv
    from bigml.anomaly import Anomaly
    local_anomaly = Anomaly("anomaly/5a414c667811dd5057000ab5")
    with open("test_data.csv") as test_handler:
        reader = csv.DictReader(test_handler)
        for input_data in reader:
        # predicting for all rows
            print local_anomaly.anomaly_score(input_data)

Every modeling resource in BigML has its corresponding local class. Check
the `Local resources <index.html#local-resources>`_ section of the
documentation to learn more about them.
