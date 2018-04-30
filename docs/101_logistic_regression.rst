BigML Bindings: 101 - Using a Logistic Regression
=================================================

Following the schema described in the `prediction workflow <api_sketch.html>`_,
document, this is the code snippet that shows the minimal workflow to
create a logistic regression model and produce a single prediction.

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
    # step 5: creating a logistic regression
    logistic_regression = api.create_logistic_regression(dataset)
    # waiting for the logistic regression to be finished
    api.ok(logistic_regression)
    # the new input data to predict for
    input_data = {"petal length": 4, "sepal length": 2}
    # creating a single prediction
    prediction = api.create_prediction(logistic_regression, input_data)

If you want to create predictions for many new inputs, you can do so by
creating
a `batch_prediction` resource. First, you will need to upload to the platform
all the input data that you want to predict for and create the corresponding
`source` and `dataset` resources. In the example, we'll be assuming you already
created a `logistic regression` following the steps 0 to 5
in the previous snippet.

.. code-block:: python

    # step 6: creating a source from the data in your local "data/test_iris.csv" file
    test_source = api.create_source("data/test_iris.csv")
    # waiting for the source to be finished. Results will be stored in `source`
    api.ok(test_source)
    # step 8: creating a dataset from the previously created `source`
    test_dataset = api.create_dataset(test_source)
    # waiting for the dataset to be finished
    api.ok(test_dataset)
    # step 10: creating a batch prediction
    batch_prediction = api.create_batch_prediction(logistic_regression,
                                                   test_dataset)
    # waiting for the batch_prediction to be finished
    api.ok(batch_prediction)
    # downloading the results to your computer
    api.download_batch_prediction(batch_prediction,
                                  filename='my_dir/my_predictions.csv')

The batch prediction output (as well as any of the resources created)
can be configured using additional arguments in the corresponding create calls.
For instance, to include all the information in the original dataset in the
output you would change `step 10` to:

.. code-block:: python

    batch_prediction = api.create_batch_prediction(logistic_regression,
                                                   test_dataset,
                                                   {"all_fields": True})
Check the `API documentation <https://bigml.com/api/>`_ to learn about the
available configuration options for any BigML resource.

You can also predict locally using the `LogisticRegression`
class in the `logistic` module. A simple example of that is:

.. code-block:: python

    from bigml.logistic import LogisticRegression
    local_logistic_regression = LogisticRegression( \
        "logisticregression/5968ec46983efc21b000001b")
    # predicting for some input data
    local_logistic_regression.predict({"petal length": 4, "sepal length": 2,
                                       "petal width": 1, "sepal witdh": 3})

Or you could store first your logistic regression
information in a file and use that
file to create the local `LogisticRegression` object:

.. code-block:: python

    # downloading the logistic regression JSON to a local file
    from bigml.api import BigML
    api = BigML()
    api.export("logisticregression/5968ec46983efc21b000001b",
               "filename": "my_logistic_regression.json")
    # creating the logistic regression from the file
    from bigml.logistic import LogisticRegression
    local_logistic_regression = LogisticRegression( \
        "my_logistic_regression.json")
    # predicting for some input data
    local_logistic_regression.predict({"petal length": 4, "sepal length": 2,
                                       "petal width": 1, "sepal witdh": 3})


And if you want to predict locally for all the rows in a CSV file (first line
should contain the field headers):

.. code-block:: python

    import csv
    from bigml.logistic import LogisticRegression
    local_logistic_regression = LogisticRegression( \
        "logisticregression/5a414c667811dd5057000ab5")
    with open("test_data.csv") as test_handler:
        reader = csv.DictReader(test_handler)
        for input_data in reader:
        # predicting for all rows
            print local_logistic_regression.predict(input_data)

Every modeling resource in BigML has its corresponding local class. Check
the `Local resources <index.html#local-resources>`_ section of the
documentation to learn more about them.
