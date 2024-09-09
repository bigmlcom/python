.. toctree::
   :hidden:

101 - Images Feature Extraction
===============================

Following the schema described in the `prediction workflow <api_sketch.html>`_,
document, this is the code snippet that shows the minimal workflow to
extract features from images and generate an enriched dataset that can be
used to train any kind of model.

.. code-block:: python

    from bigml.api import BigML
    # step 0: creating a connection to the service (default credentials)
    api = BigML()
    # step 1: creating a source from the data in your local
    # "data/images/fruits_hist.zip" file. The file contains two folders, each
    # of which contains a collection of images. The folder name will be used
    # as label for each image it contains.
    # The source is created enabling image analysis and setting some of the
    # available features (see the API documentation at
    # https://bigml.com/api/sources?id=source-arguments
    # for details). In particular, we extract histogram of gradients and
    # average pixels.
    extracted_features = ["average_pixels", "histogram_of_gradients"]
    source = api.create_source("data/images/fruits_hist.zip",
        args={"image_analysis": {"enabled": True,
                                 "extracted_features": extracted_features}})
    # waiting for the source to be finished. Results will be stored in `source`
    # and the new extracted features will be generated.
    api.ok(source)
    # step 3: creating a dataset from the previously created `source`
    dataset = api.create_dataset(source)
    # waiting for the dataset to be finished
    api.ok(dataset)
    # step 5: creating an anomaly detector
    anomaly = api.create_anomaly(dataset)
    # waiting for the anomaly detector to be finished
    api.ok(anomaly)
    # the new input data to predict for should contain the path to the
    # new image to be used for testing
    input_data = {"image_id": "data/images/f2/fruits2.png"}
    # creating a single anomaly score: The image file is uploaded to BigML,
    # a new source is created for it using the same image_analysis
    # used in the image field, and its ID is used as value
    # for the ``image_id`` field in the input data to generate the prediction
    anomaly_score = api.create_anomaly_score(anomaly, input_data)

In the previous code, the `api.ok <creating_resources.html>`_
method is used to wait for the resource
to be finished before calling the next create method
or accessing the resource properties.
In the first case, we could skip that `api.ok`call because the next
`create` method would internally do the waiting when needed.

You can also create a local anomaly score using the `Anomaly`
class in the `anomaly` module. A simple example of that is:

.. code-block:: python

    from bigml.anomaly import Anomaly
    local_anomaly = Anomaly("anomaly/5968ec46983efc21b000001c")
    # creating a pipeline to store the feature extraction transformations
    feature_extraction_pipeline = local_anomaly.data_transformations()
    # scoring for some input data. As pipelines transform lists of rows
    # we build a list with the single input data and get the first
    # element of the output list
    input_data = feature_extraction_pipeline.transform(
        [{"image_id": "data/images/f2/fruits2.png"}])[0]
    local_anomaly.anomaly_score(input_data)
