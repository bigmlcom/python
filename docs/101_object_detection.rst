.. toctree::
   :hidden:

BigML Bindings: 101 - Images Object Detection
=============================================

Following the schema described in the `prediction workflow <api_sketch.html>`_,
document, this is the code snippet that shows the minimal workflow to
create a deepnet and produce a single prediction.

.. code-block:: python

    from bigml.api import BigML
    # step 0: creating a connection to the service (default credentials)
    api = BigML()
    # step 1: creating a source from the data in your local
    # "data/images/cats.zip" file, that contains a collection of images
    # and an "annotations.json" file with the corresponding annotations per
    # image describing the regions labeled in the image
    source = api.create_source("data/images/cats.zip")
    # waiting for the source to be finished. Results will be stored in `source`
    api.ok(source)
    # step 3: creating a dataset from the previously created `source`
    dataset = api.create_dataset(source)
    # waiting for the dataset to be finished
    api.ok(dataset)
    # step 5: creating a deepnet
    deepnet = api.create_deepnet(dataset)
    # waiting for the deepnet to be finished
    api.ok(deepnet)
    # the new input data to predict for
    input_data = "data/images/cats_test/pexels-pixabay-33358.jpg"
    # creating a single prediction
    prediction = api.create_prediction(deepnet, input_data)


You can also predict locally using the `Deepnet`
class in the `deepnet` module. A simple example of that is:

.. code-block:: python

    from bigml.deepnet import Deepnet
    local_deepnet = Deepnet("deepnet/5968ec46983efc21b000001c")
    # predicting for some input data
    input_data = "data/images/cats_test/pexels-pixabay-33358.jpg"
    local_deepnet.predict(input_data)
