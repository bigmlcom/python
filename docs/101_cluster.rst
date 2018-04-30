BigML Bindings: 101 - Using a Cluster
=====================================

Following the schema described in the `prediction workflow <api_sketch.html>`_,
document, this is the code snippet that shows the minimal workflow to
create a cluster and find the centroid associated to a single instance.

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
    # step 5: creating a cluster
    cluster = api.create_cluster(dataset)
    # waiting for the cluster to be finished
    api.ok(cluster)
    # the new input data to find the centroid. All numeric fields are to be
    # provided.
    input_data = {"petal length": 4, "sepal length": 2, "petal width": 3,
                  "sepal width": 1, "species": "Iris-setosa"}
    # getting the associated centroid
    centroid = api.create_centroid(cluster, input_data)

If you want to find the centroids for many inputs at once, you can do so by
creating a `batch_centroid` resource. You can create a `batch_centroid` using
the same `dataset` that you used to built the `cluster` and this will produce a
new dataset with a new column that contains the name of the cluster each
instance has been assigned to.

Of course, you can also apply the `cluster`
to new data to find the associated centroids. Then, you will first
need to upload to the platform
all the input data that you want to use and create the corresponding
`source` and `dataset` resources. In the example, we'll be assuming you already
created a `cluster` following the `steps 0 to 5` in the previous snippet.
In the
next example, `steps 6 and 8` will only be necessary if you want
to use new data
to be clustered. If you just want the information about the cluster assigned
to each instance in the clustering algorithm, you can go to `step 10` and use
the dataset created in `step 3` as `test_dataset`.

.. code-block:: python

    # step 6: creating a source from the data in your local "data/test_iris.csv" file
    test_source = api.create_source("data/test_iris.csv")
    # waiting for the source to be finished. Results will be stored in `source`
    api.ok(test_source)
    # step 8: creating a dataset from the previously created `source`
    test_dataset = api.create_dataset(test_source)
    # waiting for the dataset to be finished
    api.ok(test_dataset)
    # step 10: creating a batch centroid
    batch_centroid = api.create_batch_centroid(cluster, test_dataset)
    # waiting for the batch_centroid to be finished
    api.ok(batch_centroid)
    # downloading the results to your computer
    api.download_batch_centroid(batch_centroid,
                                filename='my_dir/my_centroids.csv')

The batch centroid output (as well as any of the resources created)
can be configured using additional arguments in the corresponding create calls.
For instance, to include all the information in the original dataset in the
output you would change `step 10` to:

.. code-block:: python

    bach_centroid = api.create_batch_centroid(cluster, test_dataset,
                                              {"all_fields": True})


Check the `API documentation <https://bigml.com/api/>`_ to learn about the
available configuration options for any BigML resource.

You can also associate centroids locally using the `Cluster`
class in the `cluster` module. A simple example of that is:

.. code-block:: python

    from bigml.cluster import Cluster
    local_cluster = Cluster("cluster/5968ec46983efc21b000001b")
    # associated centroid for some input data
    local_cluster.centroid({"petal length": 4, "sepal length": 2,
                            "petal width": 1, "sepal witdh": 3})

Or you could store first your cluster information in a file and use that
file to create the local `Cluster` object:

.. code-block:: python

    # downloading the cluster JSON to a local file
    from bigml.api import BigML
    api = BigML()
    api.export("cluster/5968ec46983efc21b000001b",
               "filename": "my_cluster.json")
    # creating the cluster from the file
    from bigml.cluster import Cluster
    local_cluster = Cluster("my_cluster.json")
    # associated centroid for some input data
    local_cluster.centroid({"petal length": 4, "sepal length": 2,
                            "petal width": 1, "sepal witdh": 3})


And if you want to find out locally the associated centroids
for all the rows in a CSV file (first line
should contain the field headers):

.. code-block:: python

    import csv
    from bigml.cluster import Cluster
    local_cluster = Cluster("cluster/5a414c667811dd5057000ab5")
    with open("test_data.csv") as test_handler:
        reader = csv.DictReader(test_handler)
        for input_data in reader:
        # predicting for all rows
            print local_cluster.centroid(input_data)

Every modeling resource in BigML has its corresponding local class. Check
the `Local resources <index.html#local-resources>`_ section of the
documentation to learn more about them.
