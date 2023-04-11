.. toctree::
   :hidden:

BigML Bindings: 101 - Images Classification
===========================================

Following the schema described in the `prediction workflow <api_sketch.html>`_,
document, this is the code snippet that shows the minimal workflow to
create a deepnet from an images dataset and produce a single prediction.

.. code-block:: python

    from bigml.api import BigML
    # step 0: creating a connection to the service (default credentials)
    api = BigML()
    # step 1: creating a source from the data in your local
    # "data/images/fruits_hist.zip" file. The file contains two folders, each
    # of which contains a collection of images. The folder name will be used
    # as label for each image it contains.
    # The source is created disabling image analysis, as we want the deepnet
    # model to take care of extracting the features. If not said otherwise,
    # the analysis would be enabled and features like the histogram of
    # gradients would be extracted to become part of the resulting dataset.
    source = api.create_source("data/images/fruits_hist.zip",
        args={"image_analysis": {"enabled": False}})
    # waiting for the source to be finished. Results will be stored in `source`
    # and the new ``image_id`` and ``label`` fields will be generated in the
    # source
    api.ok(source)
    # step 3: creating a dataset from the previously created `source`
    dataset = api.create_dataset(source)
    # waiting for the dataset to be finished
    api.ok(dataset)
    # step 5: creating a deepnet
    deepnet = api.create_deepnet(dataset)
    # waiting for the deepnet to be finished
    api.ok(deepnet)
    # the new input data to predict for should contain the path to the
    # new image to be used for testing
    input_data = {"image_id": "data/images/f2/fruits2.png"}
    # creating a single prediction: The image file is uploaded to BigML,
    # a new source is created for it and its ID is used as value
    # for the ``image_id`` field in the input data to generate the prediction
    prediction = api.create_prediction(deepnet, input_data)

In the previous code, the `api.ok <creating_resources.html>`_
method is used to wait for the resource
to be finished before calling the next create method
or accessing the resource properties.
In the first case, we could skip that `api.ok`call because the next
`create` method would internally do the waiting when needed.

You can also predict locally using the `Deepnet`
class in the `deepnet` module. A simple example of that is:

.. code-block:: python

    from bigml.deepnet import Deepnet
    local_deepnet = Deepnet("deepnet/5968ec46983efc21b000001c")
    # predicting for some input data
    input_data = {"image_id": "data/images/f2/fruits2.png"}
    local_deepnet.predict(input_data)
