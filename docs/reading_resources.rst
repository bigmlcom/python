.. toctree::
   :hidden:

Reading Resources
-----------------

When retrieved individually, resources are returned as a dictionary
identical to the one you get when you create a new resource. However,
the status code will be ``bigml.api.HTTP_OK`` if the resource can be
retrieved without problems, or one of the HTTP standard error codes
otherwise. To know more about the errors that can happen when retrieving
a resource and what to expect if a resource is not correctly created, please
refer to the
`Waiting for Resources <creating_resources.html#waiting_for_resources>`_
section.

To retrieve an existing resource, you just need to use the corresponding
``get_[resouce type]`` method. There's a query string argument
that can be used to filter out or limit the attributes obtained:

.. code-block:: python

    # gets the source information with no filters
    api.get_source("source/5143a51a37203f2cf7000956")
    # gets the dataset information with only 10 of the fields
    api.get_dataset("dataset/5143a51a37203f2cf7000936",
                    query_string="limit=10")
    # gets the model information excluding the model predicates tree
    api.get_model("model/5143a51a37203f2cf7000956",
                  query_string="exclude=root")


Listing Resources
-----------------

You can list resources with the appropriate api method:

.. code-block:: python

    api.list_sources()
    api.list_datasets()
    api.list_models()
    api.list_predictions()
    api.list_evaluations()
    api.list_ensembles()
    api.list_batch_predictions()
    api.list_clusters()
    api.list_centroids()
    api.list_batch_centroids()
    api.list_anomalies()
    api.list_anomaly_scores()
    api.list_batch_anomaly_scores()
    api.list_projects()
    api.list_samples()
    api.list_correlations()
    api.list_statistical_tests()
    api.list_logistic_regressions()
    api.list_linear_regressions()
    api.list_associations()
    api.list_association_sets()
    api.list_topic_models()
    api.list_topic_distributions()
    api.list_batch_topic_distributions()
    api.list_time_series()
    api.list_deepnets()
    api.list_fusions()
    api.list_pcas()
    api.list_projections()
    api.list_batch_projections()
    api.list_forecasts()
    api.list_scripts()
    api.list_libraries()
    api.list_executions()
    api.list_external_connectors()


you will receive a dictionary with the following keys:

-  **code**: If the request is successful you will get a
   ``bigml.api.HTTP_OK`` (200) status code. Otherwise, it will be one of
   the standard HTTP error codes. See `BigML documentation on status
   codes <https://bigml.com/api/status_codes>`_ for more info.
-  **meta**: A dictionary including the following keys that can help you
   paginate listings:

   -  **previous**: Path to get the previous page or ``None`` if there
      is no previous page.
   -  **next**: Path to get the next page or ``None`` if there is no
      next page.
   -  **offset**: How far off from the first entry in the resources is
      the first one listed in the resources key.
   -  **limit**: Maximum number of resources that you will get listed in
      the resources key.
   -  **total\_count**: The total number of resources in BigML.

-  **objects**: A list of resources as returned by BigML.
-  **error**: If an error occurs and the resource cannot be created, it
   will contain an additional code and a description of the error. In
   this case, **meta**, and **resources** will be ``None``.

Filtering Resources
~~~~~~~~~~~~~~~~~~~

You can filter resources in listings using the syntax and fields labeled
as *filterable* in the `BigML
documentation <https://bigml.com/api>`_ for each resource.

A few examples:

Ids of the first 5 sources created before April 1st, 2012
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    [source['resource'] for source in
      api.list_sources("limit=5;created__lt=2012-04-1")['objects']]

Name of the first 10 datasets bigger than 1MB
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    [dataset['name'] for dataset in
      api.list_datasets("limit=10;size__gt=1048576")['objects']]

Name of models with more than 5 fields (columns)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    [model['name'] for model in api.list_models("columns__gt=5")['objects']]

Ids of predictions whose model has not been deleted
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    [prediction['resource'] for prediction in
      api.list_predictions("model_status=true")['objects']]

Ordering Resources
~~~~~~~~~~~~~~~~~~

You can order resources in listings using the syntax and fields labeled
as *sortable* in the `BigML
documentation <https://bigml.com/api>`_ for each resource.

A few examples:

Name of sources ordered by size
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    [source['name'] for source in api.list_sources("order_by=size")['objects']]

Number of instances in datasets created before April 1st, 2012 ordered by size
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    [dataset['rows'] for dataset in
      api.list_datasets(
        "created__lt=2012-04-01T00:00:00.00000;order_by=size")['objects']]

Model ids ordered by number of predictions (in descending order).
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    [model['resource'] for model in
      api.list_models("order_by=-number_of_predictions")['objects']]

Name of predictions ordered by name.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    [prediction['name'] for prediction in
      api.list_predictions("order_by=name")['objects']]

Public and shared resources
---------------------------

The previous examples use resources that were created by the same user
that asks for their retrieval or modification. If a user wants to share one
of her resources, she can make them public or share them. Declaring a resource
public means that anyone can see the resource. This can be applied to datasets
and models. To turn a dataset public, just update its ``private`` property:

.. code-block:: python

    api.update_dataset('dataset/5143a51a37203f2cf7000972', {'private': false})

and any user will be able to download it using its id prepended by ``public``:

.. code-block:: python

    api.get_dataset('public/dataset/5143a51a37203f2cf7000972')

In the models' case, you can also choose if you want the model to be fully
downloadable or just accesible to make predictions. This is controlled with the
``white_box`` property. If you want to publish your model completely, just
use:

.. code-block:: python

    api.update_model('model/5143a51a37203f2cf7000956', {'private': false,
                     'white_box': true})

Both public models and datasets, will be openly accessible for anyone,
registered or not, from the web
gallery.

Still, you may want to share your models with other users, but without making
them public for everyone. This can be achieved by setting the ``shared``
property:

.. code-block:: python

    api.update_model('model/5143a51a37203f2cf7000956', {'shared': true})

Shared models can be accessed using their share hash (propery ``shared_hash``
in the original model):

.. code-block:: python

    api.get_model('shared/model/d53iw39euTdjsgesj7382ufhwnD')

or by using their original id with the creator user as username and a specific
sharing api_key you will find as property ``sharing_api_key`` in the updated
model:

.. code-block:: python

    api.get_model('model/5143a51a37203f2cf7000956', shared_username='creator',
                  shared_api_key='c972018dc5f2789e65c74ba3170fda31d02e00c3')

Only users with the share link or credentials information will be able to
access your shared models.
