.. toctree::
   :hidden:

BigML Bindings: 101 - Using a Fusion Model
==========================================

Following the schema described in the `prediction workflow <api_sketch.html>`_,
document, this is the code snippet that shows the minimal workflow to
create a fusion model (assuming that some component models have
already been created) and produce a single prediction.

.. code-block:: python

    from bigml.api import BigML
    # step 0: creating a connection to the service (default credentials)
    api = BigML()
    # step 5: creating a fusion model from a preexisting model and a logistic
    #         regression with equal weight
    fusion = api.create_fusion({["id": "model/1111111111111111111111111",
                                 "weight": 1},
                                {"id": "logisticregression/222222222222222222222222",
                                 "weight": 1}])
    # waiting for the fusion to be finished
    api.ok(fusion)
    # the new input data to predict for
    input_data = {"petal width": 1.75, "petal length": 2.45}
    # creating a single prediction
    prediction = api.create_prediction(fusion, input_data)

If you want to create predictions for many new inputs, you can do so by
creating
a `batch_prediction` resource. First, you will need to upload to the platform
all the input data that you want to predict for and create the corresponding
`source` and `dataset` resources. In the example, we'll be assuming you already
created a `model` following the steps 0 to 5 in the previous snippet.

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
    batch_prediction = api.create_batch_prediction(fusion, test_dataset)
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

    batch_prediction = api.create_batch_prediction(fusion, test_dataset,
                                                   {"all_fields": True})
Check the `API documentation <https://bigml.com/api/>`_ to learn about the
available configuration options for any BigML resource.

You can also predict locally using the `Fusion`
class in the `fusion` module. A simple example of that is:

.. code-block:: python

    from bigml.fusion import Fusion
    local_fusion = Fusion("fusion/5968ec46983efc21b000001b")
    # predicting for some input data
    local_fusion.predict({"petal length": 2.45, "sepal length": 2,
                          "petal width": 1.75, "sepal witdh": 3})

Or you could store first your fusion information (together with the included
models) in a file per model and use those
files to create the local `Fusion` object:

.. code-block:: python

    # downloading the model JSON to a local file
    from bigml.api import BigML
    api = BigML()
    api.export("fusion/5968ec46983efc21b000001b",
               "filename": "my_dir/my_fusion.json")
    # creating the local fusion from the file
    from bigml.fusion import Fusion
    local_fusion = Fusion("my_dir/my_fusion.json")
    # predicting for some input data
    local_fusion.predict({"petal length": 2.45, "sepal length": 2,
                          "petal width": 1.75, "sepal witdh": 3})


And if you want to predict locally for all the rows in a CSV file (first line
should contain the field headers):

.. code-block:: python

    import csv
    from bigml.fusion import Fusion
    local_fusion = Fusion("fusion/5a414c667811dd5057000ab5")
    with open("test_data.csv") as test_handler:
        reader = csv.DictReader(test_handler)
        for input_data in reader:
        # predicting for all rows
            print local_fusion.predict(input_data)


Every modeling resource in BigML has its corresponding local class. Check
the `Local resources <index.html#local-resources>`_ section of the
documentation to learn more about them.
