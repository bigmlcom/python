.. toctree::
   :hidden:

Creating Resources
==================

Newly-created resources are returned in a dictionary with the following
keys:

-  **code**: If the request is successful you will get a
   ``bigml.api.HTTP_CREATED`` (201) status code. In asynchronous file uploading
   ``api.create_source`` calls, it will contain ``bigml.api.HTTP_ACCEPTED`` (202)
   status code. Otherwise, it will be
   one of the standard HTTP error codes `detailed in the
   documentation <https://bigml.com/api/status_codes>`_.
-  **resource**: The identifier of the new resource.
-  **location**: The location of the new resource.
-  **object**: The resource itself, as computed by BigML.
-  **error**: If an error occurs and the resource cannot be created, it
   will contain an additional code and a description of the error. In
   this case, **location**, and **resource** will be ``None``.

Statuses
~~~~~~~~

Please, bear in mind that resource creation is almost always
asynchronous (**predictions** are the only exception). Therefore, when
you create a new source, a new dataset or a new model, even if you
receive an immediate response from the BigML servers, the full creation
of the resource can take from a few seconds to a few days, depending on
the size of the resource and BigML's load. A resource is not fully
created until its status is ``bigml.api.FINISHED``. See the
`documentation on status
codes <https://bigml.com/api/status_codes>`_ for the listing of
potential states and their semantics. So depending on your application
you might need to import the following constants:

.. code-block:: python

    from bigml.api import WAITING
    from bigml.api import QUEUED
    from bigml.api import STARTED
    from bigml.api import IN_PROGRESS
    from bigml.api import SUMMARIZED
    from bigml.api import FINISHED
    from bigml.api import UPLOADING
    from bigml.api import FAULTY
    from bigml.api import UNKNOWN
    from bigml.api import RUNNABLE

Usually, you will simply need to wait until the resource is
in the ``bigml.api.FINISHED`` state for further processing. If that's the case,
the easiest way is calling the ``api.ok`` method and passing as first argument
the object that contains your resource:

.. code-block:: python

    from bigml.api import BigML
    api = BigML() # creates a connection to BigML's API
    source = api.create_source('my_file.csv') # creates a source object
    api.ok(source) # checks that the source is finished and updates ``source``

In this code, ``api.create_source`` will probably return a non-finished
``source`` object. Then, ``api.ok`` will query its status and update the
contents of the ``source`` variable with the retrieved information until it
reaches a ``bigml.api.FINISHED`` or ``bigml.api.FAILED`` status.

HTTP transient conditions can affect the ``api.ok`` method, as it needs to
connect to the BigML servers to retrieve the resource information. Using the
``error_retries`` parameter, you can set the  number of times that the
retrieval will be tried before failing.

.. code-block:: python

    dataset = api.get_dataset("dataset/5e4ee08e440ca13244102dbd")
    api.ok(dataset, error_retries=5)

The ``api.ok`` method is repeatedly calling the API but it sleeps for some
time between calls. The sleeping time is set by using an exponential function
that generates a random number in a range. The upper limit of that range is
increasing with the number of retries. The parameters like the initial
waiting time, the number of retries or the estimate of the maximum elapsed
time can be provided to fit every particular case.


.. code-block:: python

    dataset = api.get_dataset("anomaly/5e4ee08e440ca13244102dbd")
    api.ok(dataset, wait_time=60, max_elapsed_estimate=300)
    # if the first call response is not a finished resource, the
    # method will sleep for 60 seconds and increase this sleep time
    # boundary till the elapsed time goes over 5 minutes. When that
    # happens and the resource is still not created, counters are
    # initialized again and the sleep period will start from 60s
    # repeating the increasing process.


If you don't want the contents of the variable to be updated, you can
also use the ``check_resource`` function:

.. code-block:: python

    check_resource(resource, api.get_source)

that will constantly query the API until the resource gets to a FINISHED or
FAULTY state, or can also be used with ``wait_time`` (in seconds)
and ``retries``
arguments to control the polling:

.. code-block:: python

    check_resource(resource, api.get_source, wait_time=2, retries=20)

The ``wait_time`` value is used as seed to a wait
interval that grows exponentially with the number of retries up to the given
``retries`` limit.

However, in other scenarios you might need to control the complete
evolution of the resource, not only its final states.
There, you can query the status of any resource
with the ``status`` method, which simply returns its value and does not
update the contents of the associated variable:

.. code-block:: python

    api.status(source)
    api.status(dataset)
    api.status(model)
    api.status(prediction)
    api.status(evaluation)
    api.status(ensemble)
    api.status(batch_prediction)
    api.status(cluster)
    api.status(centroid)
    api.status(batch_centroid)
    api.status(anomaly)
    api.status(anomaly_score)
    api.status(batch_anomaly_score)
    api.status(sample)
    api.status(correlation)
    api.status(statistical_test)
    api.status(logistic_regression)
    api.status(association)
    api.status(association_set)
    api.status(topic_model)
    api.status(topic_distribution)
    api.status(batch_topic_distribution)
    api.status(time_series)
    api.status(forecast)
    api.status(optiml)
    api.status(fusion)
    api.status(pca)
    api.status(projection)
    api.status(batch_projection)
    api.status(linear_regression)
    api.status(script)
    api.status(execution)
    api.status(library)

Remember that, consequently, you will need to retrieve the resources
explicitly in your code to get the updated information.


Projects
~~~~~~~~

A special kind of resource is ``project``. Projects are repositories
for resources, intended to fulfill organizational purposes. Each project can
contain any other kind of resource, but the project that a certain resource
belongs to is determined by the one used in the ``source``
they are generated from. Thus, when a source is created
and assigned a certain ``project_id``, the rest of resources generated from
this source will remain in this project.

The REST calls to manage the ``project`` resemble the ones used to manage the
rest of resources. When you create a ``project``:

.. code-block:: python

    from bigml.api import BigML
    api = BigML()

    project = api.create_project({'name': 'my first project'})

the resulting resource is similar to the rest of resources, although shorter:

.. code-block:: python

    {'code': 201,
     'resource': u'project/54a1bd0958a27e3c4c0002f0',
     'location': 'http://bigml.io/andromeda/project/54a1bd0958a27e3c4c0002f0',
     'object': {u'category': 0,
                u'updated': u'2014-12-29T20:43:53.060045',
                u'resource': u'project/54a1bd0958a27e3c4c0002f0',
                u'name': u'my first project',
                u'created': u'2014-12-29T20:43:53.060013',
                u'tags': [],
                u'private': True,
                u'dev': None,
                u'description': u''},
     'error': None}

and you can use its project id to get, update or delete it:

.. code-block:: python

    project = api.get_project('project/54a1bd0958a27e3c4c0002f0')
    api.update_project(project['resource'],
                       {'description': 'This is my first project'})

    api.delete_project(project['resource'])

**Important**: Deleting a non-empty project will also delete **all resources**
assigned to it, so please be extra-careful when using
the ``api.delete_project`` call.

Creating External Connectors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To create an external connector to an existing database you need to use the
``create_external_connector`` method. The only required parameter is the
dictionary that contains the information needed to connect to the particular
database/table. The attributes of the connection dictionary needed for the
method to work will depend on the type of database used.

For instance, you can create a connection to an ``Elasticsearch`` database
hosted locally at port ``9200`` by calling:

.. code-block:: python

    from bigml.api import BigML
    api = BigML()

    external_connector = api.create_external_connector( \
        {"hosts": ["localhost:9200"]}, {"source": "elasticsearch"})

where the first argument contains the infromation about the host
and ``source`` contains the type of database to connec to (allowed types are:
``elasticsearch``, ``postgresql``, ``mysql``, ``sqlserver``). If no ``source``
type is set, ``postgresql`` will be used as default value.

You can add other properties to that second argument, like the name
to be used for this external
connector. All other arguments should be placed in the second parameter:

.. code-block:: python

    from bigml.api import BigML
    api = BigML()

    external_connector = api.create_external_connector( \
        {"hosts": ["localhost:9200"]},
        {"source": "elasticsearch",
         "name": "My elasticsearch"})


Creating Sources
~~~~~~~~~~~~~~~~

To create a source from a local data file, you can use the
``create_source`` method. The only required parameter is the path to the
data file (or file-like object). You can use a second optional parameter
to specify any of the
options for source creation described in the `BigML API
documentation <https://bigml.com/api/sources>`_.

Here's a sample invocation:

.. code-block:: python

    from bigml.api import BigML
    api = BigML()

    source = api.create_source('./data/iris.csv',
        {'name': 'my source', 'source_parser': {'missing_tokens': ['?']}})

or you may want to create a source from a file in a remote location:

.. code-block:: python

    source = api.create_source('s3://bigml-public/csv/iris.csv',
        {'name': 'my remote source', 'source_parser': {'missing_tokens': ['?']}})

or maybe reading the content from stdin:

.. code-block:: python

    content = StringIO.StringIO(sys.stdin.read())
    source = api.create_source(content,
        {'name': 'my stdin source', 'source_parser': {'missing_tokens': ['?']}})

or from an existing external connector:

.. code-block:: python

    content = {"source": "postgresql",
               "externalconnector_id": "5ea1d2f7c7736e160900001c",
               "query": "select * from table_name"}
    source = api.create_source(content,
        {'name': 'my stdin source', 'source_parser': {'missing_tokens': ['?']}})

or using data stored in a local python variable. The following example
shows the two accepted formats:

.. code-block:: python

    local = [['a', 'b', 'c'], [1, 2, 3], [4, 5, 6]]
    local2 = [{'a': 1, 'b': 2, 'c': 3}, {'a': 4, 'b': 5, 'c': 6}]
    source = api.create_source(local, {'name': 'inline source'})

As already mentioned, source creation is asynchronous. In both these examples,
the ``api.create_source`` call returns once the file is uploaded.
Then ``source`` will contain a resource whose status code will be either
``WAITING`` or ``QUEUED``.

For local data files you can go one step further and use asynchronous
uploading:

.. code-block:: python

    source = api.create_source('./data/iris.csv',
        {'name': 'my source', 'source_parser': {'missing_tokens': ['?']}},
        async_load=True)

In this case, the call fills `source` immediately with a primary resource like:

.. code-block:: python

    {'code': 202,
     'resource': None,
     'location': None,
     'object': {'status':
                   {'progress': 0.99,
                    'message': 'The upload is in progress',
                    'code': 6}},
     'error': None}

where the ``source['object']`` status is set to ``UPLOADING`` and  its
``progress`` is periodically updated with the current uploading
progress ranging from 0 to 1. When upload completes, this structure will be
replaced by the real resource info as computed by BigML. Therefore source's
status will eventually be (as it is in the synchronous upload case)
``WAITING`` or ``QUEUED``.

You can retrieve the updated status at any time using the corresponding get
method. For example, to get the status of our source we would use:

.. code-block:: python

    api.status(source)

Creating Composite Sources (Images)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

BigML offers support to use images or collections of CSVs
in your Machine Learning models.
Uploading images to BigML is as easy as uploading any other file. Each
file will be ingested and a new source will be created from it. To build
Machine Learning models one typically needs lots of images and they are
usually uploaded in batches stored in
``.zip`` or ``.tar`` files. BigML is able to ingest such a file and creates a
``composite source`` from it
and for each file contained in the compressed file a
``component source`` will be created. Thus, a zip file containg two images
can be uploaded to BigML by using the ``create_source`` method:


.. code-block:: python
    from bigml.api import BigML
    api = BigML()
    composite_source = api.create_source("images_zip.zip")

and that operation will create three sources: one per image plus the composite
source that contains them.

If you put together a bunch of image sources inside a composite,
that composite will also have format "image". If you create a dataset
from it, every row will correspond to one of the images in the composite,
and have a column representing the image data, and another its filename.
Also, BigML will extract around two hundred features per image by default,
representing its gradients histogram, and you can choose several others or
add labels to each image. Please, check the complete `API documentation about
composite sources <https://bigml.com/api/sources#sr_composite_sources>`_ to
learn how to create them, update their contents while they are ``open``
(editable) and ``close`` them so that you can create datasets and models
from them. Closing a source makes it immutable, but any source
can be cloned into a new source open to modification.

.. code-block:: python
    from bigml.api import BigML
    api = BigML()
    closed_source = "source/526fc344035d071ea3031d72"
    open_source = api.clone_source(closed_source)

Images are usually associated to other information, like labels or numeric
fields, which can be regarded as additional attributes related to that
image. The associated information can be described as annotations for
each of the images. These annotations can be
provided as a JSON file that contains the properties associated to
each image and the name of the image file, that is used as foreign key.
The meta information needed to create the structure of the composite source,
such as the fields to be associated and their types,
should also be included in the annotations file.
This is an example of the expected structure of the annotations file:

.. code-block:: json

	{"description": "Fruit images to test colour distributions",
	 "images_file": "./fruits_hist.zip",
	 "new_fields": [{"name": "new_label", "optype": "categorical"}],
	 "source_id": null,
	 "annotations": [
		{"file": "f1/fruits1f.png", "new_label": "True"},
		{"file": "f1/fruits1.png", "new_label": "False"},
		{"file": "f2/fruits2e.png", "new_label": "False"}]}

The ``images_file`` attribute should contain the path to zip-compressed
images file and the "annotations" attribute the corresponding
annotations. The ``new_fields`` attribute should be a list of the fields
used as annotations for the images.

Also, if you prefer to keep your annotations in a separate file, you
can point to that file in the ``annotations`` attribute:

.. code-block:: json

	{"description": "Fruit images to test colour distributions",
	 "images_file": "./fruits_hist.zip",
	 "new_fields": [{"name": "new_label", "optype": "categorical"}],
	 "source_id": null,
	 "annotations": "./annotations_detail.json"}

The created source will contain the fields associated to the
uploaded images, plus an additional field named ``new_label`` with the
values defined in this file.

If a source has already been created from this collection of images,
you can provide the ID of this source in the ``source_id`` attribute.
If the annotations file contains the source ID information,
the existing source will be updated to add the new annotations
(if still open for editing) or will be cloned (if the source is
closed for editing) and the new source will be updated . In both cases,
images won't be uploaded again.


Creating Datasets
~~~~~~~~~~~~~~~~~

Once you have created a source, you can create a dataset. The only
required argument to create a dataset is a source id. You can add all
the additional arguments accepted by BigML and documented in the
`Datasets section of the Developer's
documentation <https://bigml.com/api/datasets>`_.

For example, to create a dataset named "my dataset" with the first 1024
bytes of a source, you can submit the following request:

.. code-block:: python

    dataset = api.create_dataset(source, {"name": "my dataset", "size": 1024})

Upon success, the dataset creation job will be queued for execution, and
you can follow its evolution using ``api.status(dataset)``.

As for the rest of resources, the create method will return an incomplete
object, that can be updated by issuing the corresponding
``api.get_dataset`` call until it reaches a ``FINISHED`` status.
Then you can export the dataset data to a CSV file using:

.. code-block:: python

    api.download_dataset('dataset/526fc344035d071ea3031d75',
        filename='my_dir/my_dataset.csv')

You can also extract samples from an existing dataset and generate a new one
with them using the ``api.create_dataset`` method. The first argument should
be the origin dataset and the rest of arguments that set the range or the
sampling rate should be passed as a dictionary. For instance, to create a new
dataset extracting the 80% of instances from an existing one, you could use:

.. code-block:: python

    dataset = api.create_dataset(origin_dataset, {"sample_rate": 0.8})

Similarly, if you want to split your source into training and test datasets,
you can set the `sample_rate` as before to create the training dataset and
use the `out_of_bag` option to assign the complementary subset of data to the
test dataset. If you set the `seed` argument to a value of your choice, you
will ensure a deterministic sampling, so that each time you execute this call
you will get the same datasets as a result and they will be complementary:

.. code-block:: python

    origin_dataset = api.create_dataset(source)
    train_dataset = api.create_dataset(
        origin_dataset, {"name": "Dataset Name | Training",
                         "sample_rate": 0.8, "seed": "my seed"})
    test_dataset = api.create_dataset(
        origin_dataset, {"name": "Dataset Name | Test",
                         "sample_rate": 0.8, "seed": "my seed",
                         "out_of_bag": True})

Sometimes, like for time series evaluations, it's important that the data
in your train and test datasets is ordered. In this case, the split
cannot be done at random. You will need to start from an ordered dataset and
decide the ranges devoted to training and testing using the ``range``
attribute:

.. code-block:: python

    origin_dataset = api.create_dataset(source)
    train_dataset = api.create_dataset(
        origin_dataset, {"name": "Dataset Name | Training",
                         "range": [1, 80]})
    test_dataset = api.create_dataset(
        origin_dataset, {"name": "Dataset Name | Test",
                         "range": [81, 100]})


It is also possible to generate a dataset from a list of datasets
(multidataset):

.. code-block:: python

    dataset1 = api.create_dataset(source1)
    dataset2 = api.create_dataset(source2)
    multidataset = api.create_dataset([dataset1, dataset2])

Clusters can also be used to generate datasets containing the instances
grouped around each centroid. You will need the cluster id and the centroid id
to reference the dataset to be created. For instance,

.. code-block:: python

    cluster = api.create_cluster(dataset)
    cluster_dataset_1 = api.create_dataset(cluster,
                                           args={'centroid': '000000'})

would generate a new dataset containing the subset of instances in the cluster
associated to the centroid id ``000000``.

Existing datasets can also be cloned:

.. code-block:: python
    from bigml.api import BigML
    api = BigML()
    dataset = "dataset/526fc344035d071ea3031d76"
    cloned_dataset = api.clone_dataset(dataset)


Creating Models
~~~~~~~~~~~~~~~

Once you have created a dataset you can create a model from it. If you don't
select one, the model will use the last field of the dataset as objective
field. The only required argument to create a model is a dataset id.
You can also
include in the request all the additional arguments accepted by BigML
and documented in the `Models section of the Developer's
documentation <https://bigml.com/api/models>`_.

For example, to create a model only including the first two fields and
the first 10 instances in the dataset, you can use the following
invocation:

.. code-block:: python

    model = api.create_model(dataset, {
        "name": "my model", "input_fields": ["000000", "000001"], "range": [1, 10]})

Again, the model is scheduled for creation, and you can retrieve its
status at any time by means of ``api.status(model)``.

Models can also be created from lists of datasets. Just use the list of ids
as the first argument in the api call

.. code-block:: python

    model = api.create_model([dataset1, dataset2], {
        "name": "my model", "input_fields": ["000000", "000001"], "range": [1, 10]})

And they can also be generated as the result of a clustering procedure. When
a cluster is created, a model that predicts if a certain instance belongs to
a concrete centroid can be built by providing the cluster and centroid ids:

.. code-block:: python

    model = api.create_model(cluster, {
        "name": "model for centroid 000001", "centroid": "000001"})

if no centroid id is provided, the first one appearing in the cluster is used.

Existing models can also be cloned:

.. code-block:: python
    from bigml.api import BigML
    api = BigML()
    model = "model/526fc344035d071ea3031d76"
    cloned_model = api.clone_model(model)


Creating Clusters
~~~~~~~~~~~~~~~~~

If your dataset has no fields showing the objective information to
predict for the training data, you can still build a cluster
that will group similar data around
some automatically chosen points (centroids). Again, the only required
argument to create a cluster is the dataset id. You can also
include in the request all the additional arguments accepted by BigML
and documented in the `Clusters section of the Developer's
documentation <https://bigml.com/api/clusters>`_.

Let's create a cluster from a given dataset:

.. code-block:: python

    cluster = api.create_cluster(dataset, {"name": "my cluster",
                                           "k": 5})

that will create a cluster with 5 centroids.

Existing clusters can also be cloned:

.. code-block:: python
    from bigml.api import BigML
    api = BigML()
    cluster = "cluster/526fc344035d071ea3031d76"
    cloned_cluster = api.clone_cluster(cluster)


Creating Anomaly Detectors
~~~~~~~~~~~~~~~~~~~~~~~~~~

If your problem is finding the anomalous data in your dataset, you can
build an anomaly detector, that will use iforest to single out the
anomalous records. Again, the only required
argument to create an anomaly detector is the dataset id. You can also
include in the request all the additional arguments accepted by BigML
and documented in the `Anomaly detectors section of the Developer's
documentation <https://bigml.com/api/anomalies>`_.

Let's create an anomaly detector from a given dataset:

.. code-block:: python

    anomaly = api.create_anomaly(dataset, {"name": "my anomaly"})

that will create an anomaly resource with a `top_anomalies` block of the
most anomalous points.

Existing anomaly detectors can also be cloned:

.. code-block:: python
    from bigml.api import BigML
    api = BigML()
    anomaly = "anomaly/526fc344035d071ea3031d76"
    cloned_anomaly = api.clone_anomaly(anomaly)


Creating Associations
~~~~~~~~~~~~~~~~~~~~~

To find relations between the field values you can create an association
discovery resource. The only required argument to create an association
is a dataset id.
You can also
include in the request all the additional arguments accepted by BigML
and documented in the `Association section of the Developer's
documentation <https://bigml.com/api/associations>`_.

For example, to create an association only including the first two fields and
the first 10 instances in the dataset, you can use the following
invocation:

.. code-block:: python

    association = api.create_association(dataset, { \
        "name": "my association", "input_fields": ["000000", "000001"], \
        "range": [1, 10]})

Again, the association is scheduled for creation, and you can retrieve its
status at any time by means of ``api.status(association)``.

Associations can also be created from lists of datasets. Just use the
list of ids as the first argument in the api call

.. code-block:: python

    association = api.create_association([dataset1, dataset2], { \
        "name": "my association", "input_fields": ["000000", "000001"], \
        "range": [1, 10]})

Existing associations can also be cloned:

.. code-block:: python
    from bigml.api import BigML
    api = BigML()
    association = "association/526fc344035d071ea3031d76"
    cloned_association = api.clone_association(association)


Creating Topic Models
~~~~~~~~~~~~~~~~~~~~~

To find which topics do your documents refer to you can create a topic model.
The only required argument to create a topic model
is a dataset id.
You can also
include in the request all the additional arguments accepted by BigML
and documented in the `Topic Model section of the Developer's
documentation <https://bigml.com/api/topicmodels>`_.

For example, to create a topic model including exactly 32 topics
you can use the following
invocation:

.. code-block:: python

    topic_model = api.create_topic_model(dataset, { \
        "name": "my topics", "number_of_topics": 32})

Again, the topic model is scheduled for creation, and you can retrieve its
status at any time by means of ``api.status(topic_model)``.

Topic models can also be created from lists of datasets. Just use the
list of ids as the first argument in the api call

.. code-block:: python

    topic_model = api.create_topic_model([dataset1, dataset2], { \
        "name": "my topics", "number_of_topics": 32})

Existing topic models can also be cloned:

.. code-block:: python
    from bigml.api import BigML
    api = BigML()
    topic_model = "topicmodel/526fc344035d071ea3031d76"
    cloned_topic_model = api.clone_topic_model(topic_model)

Creating Time Series
~~~~~~~~~~~~~~~~~~~~

To forecast the behaviour of any numeric variable that depends on its
historical records you can use a time series.
The only required argument to create a time series
is a dataset id.
You can also
include in the request all the additional arguments accepted by BigML
and documented in the `Time Series section of the Developer's
documentation <https://bigml.com/api/timeseries>`_.

For example, to create a time series including a forecast of 10 points
for the numeric values you can use the following
invocation:

.. code-block:: python

    time_series = api.create_time_series(dataset, { \
        "name": "my time series", "horizon": 10})

Again, the time series is scheduled for creation, and you can retrieve its
status at any time by means of ``api.status(time_series)``.

Time series also be created from lists of datasets. Just use the
list of ids as the first argument in the api call

.. code-block:: python

    time_series = api.create_time_series([dataset1, dataset2], { \
        "name": "my time series", "horizon": 10})

Existing time series can also be cloned:

.. code-block:: python
    from bigml.api import BigML
    api = BigML()
    time_series = "timeseries/526fc344035d071ea3031d76"
    cloned_time_series = api.clone_time_series(time_series)


Creating OptiML
~~~~~~~~~~~~~~~

To create an OptiML, the only required argument is a dataset id.
You can also
include in the request all the additional arguments accepted by BigML
and documented in the `OptiML section of the Developer's
documentation <https://bigml.com/api/optimls>`_.

For example, to create an OptiML which optimizes the accuracy of the model you
can use the following method

.. code-block:: python

    optiml = api.create_optiml(dataset, { \
        "name": "my optiml", "metric": "accuracy"})

The OptiML is then scheduled for creation, and you can retrieve its
status at any time by means of ``api.status(optiml)``.


Creating Fusions
~~~~~~~~~~~~~~~~

To create a Fusion, the only required argument is a list of models.
You can also
include in the request all the additional arguments accepted by BigML
and documented in the `Fusion section of the Developer's
documentation <https://bigml.com/api/fusions>`_.

For example, to create a Fusion you can use this connection method:

.. code-block:: python

    fusion = api.create_fusion(["model/5af06df94e17277501000010",
                                "model/5af06df84e17277502000019",
                                "deepnet/5af06df84e17277502000016",
                                "ensemble/5af06df74e1727750100000d"],
                                {"name": "my fusion"})

The Fusion is then scheduled for creation, and you can retrieve its
status at any time by means of ``api.status(fusion)``.

Fusions can also be created by assigning some weights to each model in the
list. In this case, the argument for the create call will be a list of
dictionaries that contain the ``id`` and ``weight`` keys:

.. code-block:: python

    fusion = api.create_fusion([{"id": "model/5af06df94e17277501000010",
                                 "weight": 10},
                                {"id": "model/5af06df84e17277502000019",
                                 "weight": 20},
                                {"id": "deepnet/5af06df84e17277502000016",
                                 "weight": 5}],
                                {"name": "my weighted fusion"})


Creating Predictions
~~~~~~~~~~~~~~~~~~~~

You can now use the model resource identifier together with some input
parameters to ask for predictions, using the ``create_prediction``
method. You can also give the prediction a name:

.. code-block:: python

    prediction = api.create_prediction(model,
                                       {"sepal length": 5,
                                        "sepal width": 2.5},
                                        {"name": "my prediction"})

To see the prediction you can use ``pprint``:

.. code-block:: python

    api.pprint(prediction)

Predictions can be created using any supervised model (model, ensemble,
logistic regression, linear regression, deepnet and fusion) as first argument.

Creating Centroids
~~~~~~~~~~~~~~~~~~

To obtain the centroid associated to new input data, you
can now use the ``create_centroid`` method. Give the method a cluster
identifier and the input data to obtain the centroid.
You can also give the centroid predicition a name:

.. code-block:: python

    centroid = api.create_centroid(cluster,
                                   {"pregnancies": 0,
                                    "plasma glucose": 118,
                                    "blood pressure": 84,
                                    "triceps skin thickness": 47,
                                    "insulin": 230,
                                    "bmi": 45.8,
                                    "diabetes pedigree": 0.551,
                                    "age": 31,
                                    "diabetes": "true"},
                                    {"name": "my centroid"})

Creating Anomaly Scores
~~~~~~~~~~~~~~~~~~~~~~~

To obtain the anomaly score associated to new input data, you
can now use the ``create_anomaly_score`` method. Give the method an anomaly
detector identifier and the input data to obtain the score:

.. code-block:: python

    anomaly_score = api.create_anomaly_score(anomaly, {"src_bytes": 350},
                                             args={"name": "my score"})

Creating Association Sets
~~~~~~~~~~~~~~~~~~~~~~~~~

Using the association resource, you can obtain the consequent items associated
by its rules to your input data. These association sets can be obtained calling
the ``create_association_set`` method. The first argument is the association
ID or object and the next one is the input data.

.. code-block:: python

    association_set = api.create_association_set( \
        association, {"genres": "Action$Adventure"}, \
        args={"name": "my association set"})


Creating Topic Distributions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To obtain the topic distributions associated to new input data, you
can now use the ``create_topic_distribution`` method. Give
the method a topic model identifier and the input data to obtain the score:

.. code-block:: python

    topic_distribution = api.create_topic_distribution( \
        topic_model,
        {"Message": "The bubble exploded in 2007."},
        args={"name": "my topic distribution"})


Creating Forecasts
~~~~~~~~~~~~~~~~~~

To obtain the forecast associated to a numeric variable, you
can now use the ``create_forecast`` method. Give
the method a time series identifier and the input data to obtain the forecast:

.. code-block:: python

    forecast = api.create_forecast( \
        time_series,
        {"Final": {"horizon": 10}})


Creating Projections
~~~~~~~~~~~~~~~~~~~~

You can now use the PCA resource identifier together with some input
parameters to ask for the corresponding projections,
using the ``create_projection``
method. You can also give the projection a name:

.. code-block:: python

    projection = api.create_projection(pca,
                                       {"sepal length": 5,
                                        "sepal width": 2.5},
                                        {"name": "my projection"})



Creating Evaluations
~~~~~~~~~~~~~~~~~~~~

Once you have created a supervised learning model,
you can measure its perfomance by running a
dataset of test data through it and comparing its predictions to the objective
field real values. Thus, the required arguments to create an evaluation are
model id and a dataset id. You can also
include in the request all the additional arguments accepted by BigML
and documented in the `Evaluations section of the Developer's
documentation <https://bigml.com/api/evaluations>`_.

For instance, to evaluate a previously created model using an existing dataset
you can use the following call:

.. code-block:: python

    evaluation = api.create_evaluation(model, dataset, {
        "name": "my model"})

Again, the evaluation is scheduled for creation and ``api.status(evaluation)``
will show its state.

Evaluations can also check the ensembles' performance. To evaluate an ensemble
you can do exactly what we just did for the model case, using the ensemble
object instead of the model as first argument:

.. code-block:: python

    evaluation = api.create_evaluation(ensemble, dataset)

Evaluations can be created using any supervised model (including time series)
as first argument.

Creating ensembles
~~~~~~~~~~~~~~~~~~

To improve the performance of your predictions, you can create an ensemble
of models and combine their individual predictions.
The only required argument to create an ensemble is the dataset id:

.. code-block:: python

    ensemble = api.create_ensemble('dataset/5143a51a37203f2cf7000972')

BigML offers three kinds of ensembles. Two of them are known as ``Decision
Forests`` because they are built as collections of ``Decision trees``
whose predictions
are aggregated using different combiners (``plurality``,
``confidence weighted``, ``probability weighted``) or setting a ``threshold``
to issue the ensemble's
prediction. All ``Decision Forests`` use bagging to sample the
data used to build the underlying models.

As an example of how to create a ``Decision Forest``
with `20` models, you only need to provide the dataset ID that you want to
build the ensemble from and the number of models:

.. code-block:: python

    args = {'number_of_models': 20}
    ensemble = api.create_ensemble('dataset/5143a51a37203f2cf7000972', args)

If no ``number_of_models`` is provided, the ensemble will contain 10 models.

``Random Decision Forests`` fall
also into the ``Decision Forest`` category,
but they only use a subset of the fields chosen
at random at each split. To create this kind of ensemble, just use the
``randomize`` option:

.. code-block:: python

    args = {'number_of_models': 20, 'randomize': True}
    ensemble = api.create_ensemble('dataset/5143a51a37203f2cf7000972', args)

The third kind of ensemble is ``Boosted Trees``. This type of ensemble uses
quite a different algorithm. The trees used in the ensemble don't have as
objective field the one you want to predict, and they don't aggregate the
underlying models' votes. Instead, the goal is adjusting the coefficients
of a function that will be used to predict. The
models' objective is, therefore, the gradient that minimizes the error
of the predicting function (when comparing its output
with the real values). The process starts with
some initial values and computes these gradients. Next step uses the previous
fields plus the last computed gradient field as
the new initial state for the next iteration.
Finally, it stops when the error is smaller than a certain threshold
or iterations reach a user-defined limit.
In classification problems, every category in the ensemble's objective field
would be associated with a subset of the ``Boosted Trees``. The objective of
each subset of trees
is adjustig the function to the probability of belonging
to this particular category.

In order to build
an ensemble of ``Boosted Trees`` you need to provide the ``boosting``
attributes. You can learn about the existing attributes in the `ensembles'
section of the API documentation <https://bigml.com/api/ensembles#es_gradient_boosting>`_,
but a typical attribute to be set would
be the maximum number of iterations:

.. code-block:: python

    args = {'boosting': {'iterations': 20}}
    ensemble = api.create_ensemble('dataset/5143a51a37203f2cf7000972', args)

Existing ensembles can also be cloned:

.. code-block:: python
    from bigml.api import BigML
    api = BigML()
    ensembles = "ensembles/526fc344035d071ea3031d76"
    cloned_ensembles = api.clone_ensembles(ensembles)


Creating Linear Regressions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

For regression problems, you can choose also linear regressions to model
your data. Linear regressions expect the predicted value for the objective
field to be computable as a linear combination of the predictors.

As the rest of models, linear regressions can be created from a dataset by
calling the corresponding create method:

.. code-block:: python

    linear_regression = api.create_linear_regression( \
        'dataset/5143a51a37203f2cf7000972',
        {"name": "my linear regression",
         "objective_field": "my_objective_field"})

In this example, we created a linear regression named
``my linear regression`` and set the objective field to be
``my_objective_field``. Other arguments, like ``bias``,
can also be specified as attributes in arguments dictionary at
creation time.
Particularly for categorical fields, there are three different available
`field_codings`` options (``contrast``, ``other`` or the ``dummy``
default coding). For a more detailed description of the
``field_codings`` attribute and its syntax, please see the `Developers API
Documentation
<https://bigml.com/api/linearregressions#lr_linear_regression_arguments>`_.

Existing linear regressions can also be cloned:

.. code-block:: python
    from bigml.api import BigML
    api = BigML()
    linear_regression = "linearregression/526fc344035d071ea3031d76"
    cloned_linear_regression = api.clone_linear_regression(linear_regression)


Creating logistic regressions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For classification problems, you can choose also logistic regressions to model
your data. Logistic regressions compute a probability associated to each class
in the objective field. The probability is obtained using a logistic
function, whose argument is a linear combination of the field values.

As the rest of models, logistic regressions can be created from a dataset by
calling the corresponding create method:

.. code-block:: python

    logistic_regression = api.create_logistic_regression( \
        'dataset/5143a51a37203f2cf7000972',
        {"name": "my logistic regression",
         "objective_field": "my_objective_field"})

In this example, we created a logistic regression named
``my logistic regression`` and set the objective field to be
``my_objective_field``. Other arguments, like ``bias``, ``missing_numerics``
and ``c`` can also be specified as attributes in arguments dictionary at
creation time.
Particularly for categorical fields, there are four different available
`field_codings`` options (``dummy``, ``contrast``, ``other`` or the ``one-hot``
default coding). For a more detailed description of the
``field_codings`` attribute and its syntax, please see the `Developers API
Documentation
<https://bigml.com/api/logisticregressions#lr_logistic_regression_arguments>`_.

Existing logistic regressions can also be cloned:

.. code-block:: python
    from bigml.api import BigML
    api = BigML()
    logistic_regression = "logisticregression/526fc344035d071ea3031d76"
    cloned_logistic_regression = api.clone_logistic_regression(
        logistic_regression)

Creating Deepnets
~~~~~~~~~~~~~~~~~

Deepnets can also solve classification and regression problems.
Deepnets are an optimized version of Deep Neural Networks,
a class of machine-learned models inspired by the neural
circuitry of the human brain. In these classifiers, the input features
are fed to a group of "nodes" called a "layer".
Each node is essentially a function on the input that
transforms the input features into another value or collection of values.
Then the entire layer transforms an input vector into a new "intermediate"
feature vector. This new vector is fed as input to another layer of nodes.
This process continues layer by layer, until we reach the final "output"
layer of nodes, where the output is the network’s prediction: an array
of per-class probabilities for classification problems or a single,
real value for regression problems.

Deepnets predictions compute a probability associated to each class
in the objective field for classification problems.
As the rest of models, deepnets can be created from a dataset by
calling the corresponding create method:

.. code-block:: python

    deepnet = api.create_deepnet( \
        'dataset/5143a51a37203f2cf7000972',
        {"name": "my deepnet",
         "objective_field": "my_objective_field"})

In this example, we created a deepnet named
``my deepnet`` and set the objective field to be
``my_objective_field``. Other arguments, like ``number_of_hidden_layers``,
``learning_rate``
and ``missing_numerics`` can also be specified as attributes
in an arguments dictionary at
creation time. For a more detailed description of the
available attributes and its syntax, please see the `Developers API
Documentation
<https://bigml.com/api/deepnets#dn_deepnet_arguments>`_.

Existing deepnets can also be cloned:

.. code-block:: python
    from bigml.api import BigML
    api = BigML()
    deepnets = "deepnets/526fc344035d071ea3031d76"
    cloned_deepnets = api.clone_deepnets(deepnets)


Creating PCAs
~~~~~~~~~~~~~

In order to reduce the number of features used in the modeling steps,
you can use a PCA (Principal Component Analysis) to find out the best
combination of features that describe the variance of your data.
As the rest of models, PCAs can be created from a dataset by
calling the corresponding create method:

.. code-block:: python

    pca = api.create_pca( \
        'dataset/5143a51a37203f2cf7000972',
        {"name": "my PCA"})

In this example, we created a PCA named
``my PCA``. Other arguments, like ``standardized``
can also be specified as attributes in arguments dictionary at
creation time.
Please see the `Developers API
Documentation
<https://bigml.com/api/pcas>`_.

Creating Batch Predictions
~~~~~~~~~~~~~~~~~~~~~~~~~~

We have shown how to create predictions individually, but when the amount
of predictions to make increases, this procedure is far from optimal. In this
case, the more efficient way of predicting remotely is to create a dataset
containing the input data you want your model to predict from and to give its
id and the one of the model to the ``create_batch_prediction`` api call:

.. code-block:: python

    batch_prediction = api.create_batch_prediction(model, dataset, {
        "name": "my batch prediction", "all_fields": True,
        "header": True,
        "confidence": True})

In this example, setting ``all_fields`` to true causes the input
data to be included in the prediction output, ``header`` controls whether a
headers line is included in the file or not and ``confidence`` set to true
causes the confidence of the prediction to be appended. If none of these
arguments is given, the resulting file will contain the name of the
objective field as a header row followed by the predictions.

As for the rest of resources, the create method will return an incomplete
object, that can be updated by issuing the corresponding
``api.get_batch_prediction`` call until it reaches a ``FINISHED`` status.
Then you can download the created predictions file using:

.. code-block:: python

    api.download_batch_prediction('batchprediction/526fc344035d071ea3031d70',
        filename='my_dir/my_predictions.csv')

that will copy the output predictions to the local file given in
``filename``. If no ``filename`` is provided, the method returns a file-like
object that can be read as a stream:

.. code-block:: python

    CHUNK_SIZE = 1024
    response = api.download_batch_prediction(
        'batchprediction/526fc344035d071ea3031d70')
    chunk = response.read(CHUNK_SIZE)
    if chunk:
        print chunk

The output of a batch prediction can also be transformed to a source object
using the ``source_from_batch_prediction`` method in the api:

.. code-block:: python

    api.source_from_batch_prediction(
        'batchprediction/526fc344035d071ea3031d70',
        args={'name': 'my_batch_prediction_source'})

This code will create a new source object, that can be used again as starting
point to generate datasets.


Creating Batch Centroids
~~~~~~~~~~~~~~~~~~~~~~~~

As described in the previous section, it is also possible to make centroids'
predictions in batch. First you create a dataset
containing the input data you want your cluster to relate to a centroid.
The ``create_batch_centroid`` call will need the id of the input
data dataset and the
cluster used to assign a centroid to each instance:

.. code-block:: python

    batch_centroid = api.create_batch_centroid(cluster, dataset, {
        "name": "my batch centroid", "all_fields": True,
        "header": True})

Creating Batch Anomaly Scores
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Input data can also be assigned an anomaly score in batch. You train an
anomaly detector with your training data and then build a dataset from your
input data. The ``create_batch_anomaly_score`` call will need the id
of the dataset and of the
anomaly detector to assign an anomaly score to each input data instance:

.. code-block:: python

    batch_anomaly_score = api.create_batch_anomaly_score(anomaly, dataset, {
        "name": "my batch anomaly score", "all_fields": True,
        "header": True})

Creating Batch Topic Distributions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Input data can also be assigned a topic distribution in batch. You train a
topic model with your training data and then build a dataset from your
input data. The ``create_batch_topic_distribution`` call will need the id
of the dataset and of the
topic model to assign a topic distribution to each input data instance:

.. code-block:: python

    batch_topic_distribution = api.create_batch_topic_distribution( \
        topic_model, dataset, {
        "name": "my batch topic distribution", "all_fields": True,
        "header": True})

Creating Batch Projections
~~~~~~~~~~~~~~~~~~~~~~~~~~

Input data can also be assigned a projection in batch. You train a
PCA with your training data and then build a dataset from your
input data. The ``create_batch_projection`` call will need the id
of the input data dataset and of the
PCA to compute the projection that corresponds to each input data instance:

.. code-block:: python

    batch_projection = api.create_batch_projection( \
        pca, dataset, {
        "name": "my batch pca", "all_fields": True,
        "header": True})
