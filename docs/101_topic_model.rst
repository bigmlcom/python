BigML Bindings: 101 - Using a Topic Model
=========================================

Following the schema described in the `prediction workflow <api_sketch.html>`_,
document, this is the code snippet that shows the minimal workflow to
create a topic model and produce a single topic distribution.

.. code-block:: python

    from bigml.api import BigML
    # step 0: creating a connection to the service (default credentials)
    api = BigML()
    # step 1: creating a source from the data in your local "data/spam.csv" file
    source = api.create_source("data/spam.csv")
    # waiting for the source to be finished. Results will be stored in `source`
    api.ok(source)
    # step 3: creating a dataset from the previously created `source`
    dataset = api.create_dataset(source)
    # waiting for the dataset to be finished
    api.ok(dataset)
    # step 5: creating a topc model
    topic_model = api.create_topic_model(dataset)
    # waiting for the topic model to be finished
    api.ok(topic_model)
    # the new input data to predict for
    input_data = {"Message": "Mobile offers, 20% discount."}
    # creating a single topic distribution
    topic_distribution = api.create_topic_distribution(topic_model, input_data)

Remember that your dataset needs to have at least a text field to be able
to create a topic model.
If you want to create topic distributions for many new inputs, you can do so by
creating
a `batch_topic_distribution` resource. First, you will need to upload
to the platform
all the input data that you want to use for and create the corresponding
`source` and `dataset` resources. In the example, we'll be assuming you already
created a `topic model` following the steps 0 to 5 in the previous snippet.

.. code-block:: python

    # step 6: creating a source from the data in your local "data/test_spam.csv" file
    test_source = api.create_source("data/test_spam.csv")
    # waiting for the source to be finished. Results will be stored in `source`
    api.ok(test_source)
    # step 8: creating a dataset from the previously created `source`
    test_dataset = api.create_dataset(test_source)
    # waiting for the dataset to be finished
    api.ok(test_dataset)
    # step 10: creating a batch topic distribution
    batch_topic_distribution = api.create_batch_topic_distribution( \
        topic_model, test_dataset)
    # waiting for the batch_topic_distribution to be finished
    api.ok(batch_topic_distribution)
    # downloading the results to your computer
    api.download_batch_topic_distribution( \
        batch_topic_distribution, filename='my_dir/my_predictions.csv')

The batch topic distribution output (as well as any of the resources created)
can be configured using additional arguments in the corresponding create calls.
For instance, to include all the information in the original dataset in the
output you would change `step 10` to:

.. code-block:: python

    batch_topic_distribution = api.create_batch_topic_distribution( \
        topic_model, test_dataset, {"all_fields": True})
Check the `API documentation <https://bigml.com/api/>`_ to learn about the
available configuration options for any BigML resource.

You can also predict locally using the `TopicModel`
class in the `topicmodel` module. A simple example of that is:

.. code-block:: python

    from bigml.topicmodel import TopicModel
    local_topic_model = TopicModel("topicmodel/5968ec46983efc21b000001b")
    # topic distribution for some input data
    local_topic_model.distribution({"Message": "Mobile offers, 20% discount."})

Or you could store first your topic model information in a file and use that
file to create the local `TopicModel` object:

.. code-block:: python

    # downloading the topic model JSON to a local file
    from bigml.api import BigML
    api = BigML()
    api.export("topicmodel/5968ec46983efc21b000001b",
               "filename": "my_topic_model.json")
    # creating the topic model from the file
    from bigml.topicmodel import TopicModel
    local_topic_model = TopicModel("my_topic_model.json")
    # topic distribution for some input data
    local_topic_model.distribution({"Message": "Mobile offers, 20% discount."})


And if you want to predict locally for all the rows in a CSV file (first line
should contain the field headers):

.. code-block:: python

    import csv
    from bigml.topicmodel import TopicModel
    local_topic_model = TopicModel("topicmodel/5a414c667811dd5057000ab5")
    with open("test_data.csv") as test_handler:
        reader = csv.DictReader(test_handler)
        for input_data in reader:
        # predicting for all rows
            print local_topic_model.distribution(input_data)

Every modeling resource in BigML has its corresponding local class. Check
the `Local resources <index.html#local-resources>`_ section of the
documentation to learn more about them.
