BigML Python Bindings
=====================

`BigML <https://bigml.com>`_ makes machine learning easy by taking care
of the details required to add data-driven decisions and predictive
power to your company. Unlike other machine learning services, BigML
creates
`beautiful predictive models <https://bigml.com/gallery/models>`_ that
can be easily understood and interacted with.

These BigML Python bindings allow you to interact with BigML.io, the API
for BigML. You can use it to easily create, retrieve, list, update, and
delete BigML resources (i.e., sources, datasets, models and,
predictions).

This module is licensed under the `Apache License, Version
2.0 <http://www.apache.org/licenses/LICENSE-2.0.html>`_.

Support
-------

Please report problems and bugs to our `BigML.io issue
tracker <https://github.com/bigmlcom/io/issues>`_.

Discussions about the different bindings take place in the general
`BigML mailing list <http://groups.google.com/group/bigml>`_. Or join us
in our `Campfire chatroom <https://bigmlinc.campfirenow.com/f20a0>`_.

Requirements
------------

Python 2.6 and Python 2.7 are currently supported by these bindings.

The only mandatory third-party dependencies are the
`requests <https://github.com/kennethreitz/requests>`_,
`poster <http://pypi.python.org/pypi/poster/>`_, and `unidecode
<http://http://pypi.python.org/pypi/Unidecode/>`_ libraries. These
libraries are automatically installed during the setup.

The bindings will also use ``simplejson`` if you happen to have it
installed, but that is optional: we fall back to Python's built-in JSON
libraries is ``simplejson`` is not found.

Installation
------------

To install the latest stable release with
`pip <http://www.pip-installer.org/>`_::

    $ pip install bigml

You can also install the development version of the bindings directly
from the Git repository::

    $ pip install -e git://github.com/bigmlcom/python.git#egg=bigml_python

Importing the module
--------------------

To import the module::

    import bigml.api

Alternatively you can just import the BigML class::

    from bigml.api import BigML

Authentication
--------------

All the requests to BigML.io must be authenticated using your username
and `API key <https://bigml.com/account/apikey>`_ and are always
transmitted over HTTPS.

This module will look for your username and API key in the environment
variables ``BIGML_USERNAME`` and ``BIGML_API_KEY`` respectively. You can
add the following lines to your ``.bashrc`` or ``.bash_profile`` to set
those variables automatically when you log in::

    export BIGML_USERNAME=myusername
    export BIGML_API_KEY=ae579e7e53fb9abd646a6ff8aa99d4afe83ac291

With that environment set up, connecting to BigML is a breeze::

    from bigml.api import BigML
    api = BigML()

Otherwise, you can initialize directly when instantiating the BigML
class as follows::

    api = BigML('myusername', 'ae579e7e53fb9abd646a6ff8aa99d4afe83ac291')

Also, you can initialize the library to work in the Sandbox
environment by passing the parameter ``dev_mode``::

    api = BigML(dev_mode=True)

Quick Start
-----------

Imagine that you want to use `this csv
file <https://static.bigml.com/csv/iris.csv>`_ containing the `Iris
flower dataset <http://en.wikipedia.org/wiki/Iris_flower_data_set>`_ to
predict the species of a flower whose ``sepal length`` is ``5`` and
whose ``sepal width`` is ``2.5``. A preview of the dataset is shown
below. It has 4 numeric fields: ``sepal length``, ``sepal width``,
``petal length``, ``petal width`` and a categorical field: ``species``.
By default, BigML considers the last field in the dataset as the
objective field (i.e., the field that you want to generate predictions
for).

::

    sepal length,sepal width,petal length,petal width,species
    5.1,3.5,1.4,0.2,Iris-setosa
    4.9,3.0,1.4,0.2,Iris-setosa
    4.7,3.2,1.3,0.2,Iris-setosa
    ...
    5.8,2.7,3.9,1.2,Iris-versicolor
    6.0,2.7,5.1,1.6,Iris-versicolor
    5.4,3.0,4.5,1.5,Iris-versicolor
    ...
    6.8,3.0,5.5,2.1,Iris-virginica
    5.7,2.5,5.0,2.0,Iris-virginica
    5.8,2.8,5.1,2.4,Iris-virginica

You can easily generate a prediction following these steps::

    from bigml.api import BigML

    api = BigML()

    source = api.create_source('./data/iris.csv')
    dataset = api.create_dataset(source)
    model = api.create_model(dataset)
    prediction = api.create_prediction(model, {'sepal length': 5, 'sepal width': 2.5})

You can then print the prediction using the ``pprint`` method::

    >>> api.pprint(prediction)
    species for {"sepal width": 2.5, "sepal length": 5} is Iris-virginica

Fields
------

BigML automatically generates idenfiers for each field. To see the
fields and the ids and types that have been assigned to a source you can
use ``get_fields``::

    >>> source = api.get_source(source)
    >>> api.pprint(api.get_fields(source))
    {   u'000000': {   u'column_number': 0,
                       u'name': u'sepal length',
                       u'optype': u'numeric'},
        u'000001': {   u'column_number': 1,
                       u'name': u'sepal width',
                       u'optype': u'numeric'},
        u'000002': {   u'column_number': 2,
                       u'name': u'petal length',
                       u'optype': u'numeric'},
        u'000003': {   u'column_number': 3,
                       u'name': u'petal width',
                       u'optype': u'numeric'},
        u'000004': {   u'column_number': 4,
                       u'name': u'species',
                       u'optype': u'categorical'}}

Dataset
-------

If you want to get some basic statistics for each field you can retrieve
the ``fields`` from the dataset as follows to get a dictionary keyed by
field id::

    >>> dataset = api.get_dataset(dataset)
    >>> api.pprint(api.get_fields(dataset))
    {   u'000000': {   u'column_number': 0,
                       u'datatype': u'double',
                       u'name': u'sepal length',
                       u'optype': u'numeric',
                       u'summary': {   u'maximum': 7.9,
                                       u'median': 5.77889,
                                       u'minimum': 4.3,
                                       u'missing_count': 0,
                                       u'population': 150,
                                       u'splits': [   4.51526,
                                                      4.67252,
                                                      4.81113,

                         [... snip ... ]


        u'000004': {   u'column_number': 4,
                       u'datatype': u'string',
                       u'name': u'species',
                       u'optype': u'categorical',
                       u'summary': {   u'categories': [   [   u'Iris-versicolor',
                                                              50],
                                                          [u'Iris-setosa', 50],
                                                          [   u'Iris-virginica',
                                                              50]],
                                       u'missing_count': 0}}}

Model
-----

One of the greatest things about BigML is that the models that it
generates for you are fully white-boxed. To get the explicit tree-like
predictive model for the example above::

    >>> model = api.get_model(model)
    >>> api.pprint(model['object']['model']['root'])
    {u'children': [
      {u'children': [
        {u'children': [{u'count': 38,
                        u'distribution': [[u'Iris-virginica', 38]],
                        u'output': u'Iris-virginica',
                        u'predicate': {u'field': u'000002',
                        u'operator': u'>',
                        u'value': 5.05}},
                        u'children': [

                            [ ... ]

                           {u'count': 50,
                            u'distribution': [[u'Iris-setosa', 50]],
                            u'output': u'Iris-setosa',
                            u'predicate': {u'field': u'000002',
                                           u'operator': u'<=',
                                           u'value': 2.45}}]},
                        {u'count': 150,
                         u'distribution': [[u'Iris-virginica', 50],
                                           [u'Iris-versicolor', 50],
                                           [u'Iris-setosa', 50]],
                         u'output': u'Iris-virginica',
                         u'predicate': True}]}}}

(Note that we have abbreviated the output in the snippet above for
readability: the full predictive model you'll get is going to contain
much more details).

Creating Resources
------------------

Newly-created resources are returned in a dictionary with the following
keys:

-  **code**: If the request is successful you will get a
   ``bigml.api.HTTP_CREATED`` (201) status code. In asynchronous file uploading
   `api.create_source` calls, it will contain ``bigml.api.HTTP_ACCEPTED`` (202)
   status code. Otherwise, it will be
   one of the standard HTTP error codes `detailed in the
   documentation <https://bigml.com/developers/status_codes>`_.
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
codes <https://bigml.com/developers/status_codes>`_ for the listing of
potential states and their semantics. So depending on your application
you might need to import the following constants::

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

You can query the status of any resource with the ``status`` method::

    api.status(source)
    api.status(dataset)
    api.status(model)
    api.status(prediction)

Before invoking the creation of a new resource, the library checks that
the status of the resource that is passed as a parameter is
``FINISHED``. You can change how often the status will be checked with
the ``wait_time`` argument. By default, it is set to 3 seconds.

You can also use the ``check_resource`` method:

    api.check_resource(resource, api.get_source)

that will constantly query the API until the resource gets to a FINISHED or
FAULTY state.

Creating sources
~~~~~~~~~~~~~~~~

To create a source from a local data file, you can use the
``create_source`` method. The only required parameter is the path to the
data file. You can use a second optional parameter to specify any of the
options for source creation described in the `BigML API
documentation <https://bigml.com/developers/sources>`_.

Here's a sample invocation::

    from bigml.api import BigML
    api = BigML()

    source = api.create_source('./data/iris.csv',
        {'name': 'my source', 'source_parser': {'missing_tokens': ['?']}})

or you may want to create a source from a file in a remote location::

    source = api.create_source('s3://bigml-public/csv/iris.csv',
        {'name': 'my remote source', 'source_parser': {'missing_tokens': ['?']}})

As already mentioned, source creation is asynchronous. In both these examples,
the `api.create_source` call returns once the file is uploaded.
Then `source` will contain a resource whose status code will be either
``WAITING`` or ``QUEUED``.

For local data files you can go one step further and use asynchronous
uploading::

    source = api.create_source('./data/iris.csv',
        {'name': 'my source', 'source_parser': {'missing_tokens': ['?']}},
        async=True)

In this case, the call fills `source` immediately with a primary resource like::

    {'code': 202,
     'resource': None,
     'location': None,
     'object': {'status':
                   {'progress': 0.99,
                    'message': 'The upload is in progress',
                    'code': 6}},
     'error': None}

where the `source['object']` status is set to `UPLOADING` and  its `progress`
is periodically updated with the current uploading
progress ranging from 0 to 1. When upload completes, this structure will be
replaced by the real resource info as computed by BigML. Therefore source's
status will eventually be (as it is in the synchronous upload case)
``WAITING`` or ``QUEUED``.

You can retrieve the updated status at any time using the corresponding get
method. For example, to get the status of our source we would use::

    api.status(source)

Creating datasets
~~~~~~~~~~~~~~~~~

Once you have created a source, you can create a dataset. The only
required argument to create a dataset is a source id. You can add all
the additional arguments accepted by BigML and documented in the
`Datasets section of the Developer's
documentation <https://bigml.com/developers/datasets>`_.

For example, to create a dataset named "my dataset" with the first 1024
bytes of a source, you can submit the following request::

    dataset = api.create_dataset(source, {"name": "my dataset", "size": 1024})

Upon success, the dataset creation job will be queued for execution, and
you can follow its evolution using ``api.status(dataset)``.

Creating models
~~~~~~~~~~~~~~~

Once you have created a dataset, you can create a model. The only
required argument to create a model is a dataset id. You can also
include in the request all the additional arguments accepted by BigML
and documented in the `Models section of the Developer's
documentation <https://bigml.com/developers/models>`_.

For example, to create a model only including the first two fields and
the first 10 instances in the dataset, you can use the following
invocation::

    model = api.create_model(dataset, {
        "name": "my model", "input_fields": ["000000", "000001"], "range": [1, 10]})

Again, the model is scheduled for creation, and you can retrieve its
status at any time by means of ``api.status(model)`` .

Creating predictions
~~~~~~~~~~~~~~~~~~~~

You can now use the model resource identifier together with some input
parameters to ask for predictions, using the ``create_prediction``
method. You can also give the prediction a name::

    prediction = api.create_prediction(model,
                                       {"sepal length": 5,
                                        "sepal width": 2.5},
                                        {"name": "my prediction"})

To see the prediction you can use ``pprint``::

    api.pprint(prediction)

Reading Resources
-----------------

When retrieved individually, resources are returned as a dictionary
identical to the one you get when you create a new resource. However,
the status code will be ``bigml.api.HTTP_OK`` if the resource can be
retrieved without problems, or one of the HTTP standard error codes
otherwise.

Listing Resources
-----------------

You can list resources with the appropriate api method::

    api.list_sources()
    api.list_datasets()
    api.list_models()
    api.list_predictions()

you will receive a dictionary with the following keys:

-  **code**: If the request is successful you will get a
   ``bigml.api.HTTP_OK`` (200) status code. Otherwise, it will be one of
   the standard HTTP error codes. See `BigML documentation on status
   codes <https://bigml.com/developers/status_codes>`_ for more info.
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
documentation <https://bigml.com/developers>`_ for each resource.

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
documentation <https://bigml.com/developers>`_ for each resource.

A few examples:

Name of sources ordered by size
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    [source['name'] for source in api.list_sources("order_by=size")['objects']]

Number of instances in datasets created before April 1st, 2012 ordered by size
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    [dataset['rows'] for dataset in
      api.list_datasets("created__lt=2012-04-1;order_by=size")['objects']]

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

Updating Resources
------------------

When you update a resource, it is returned in a dictionary exactly like
the one you get when you create a new one. However the status code will
be ``bigml.api.HTTP_ACCEPTED`` if the resource can be updated without
problems or one of the HTTP standard error codes otherwise.

::

    api.update_source(source, {"name": "new name"})
    api.update_dataset(dataset, {"name": "new name"})
    api.update_model(model, {"name": "new name"})
    api.update_prediction(prediction, {"name": "new name"})

Deleting Resources
------------------

Resources can be deleted individually using the corresponding method for
each type of resource.

::

    api.delete_source(source)
    api.delete_dataset(dataset)
    api.delete_model(model)
    api.delete_prediction(prediction)

Each of the calls above will return a dictionary with the following
keys:

-  **code** If the request is successful, the code will be a
   ``bigml.api.HTTP_NO_CONTENT`` (204) status code. Otherwise, it wil be
   one of the standard HTTP error codes. See the `documentation on
   status codes <https://bigml.com/developers/status_codes>`_ for more
   info.
-  **error** If the request does not succeed, it will contain a
   dictionary with an error code and a message. It will be ``None``
   otherwise.

Local Models
------------

You can instantiate a local version of a remote mode.

::

   from bigml.api import BigML
   from bigml.model import Model

   api = BigML()

   # Use the model/id of one of your models
   model = api.get_model('model/502fdbff1552687661000261')

   local_model = Model(model)

This will return a Model object that you can use to make local predictions,
generate IF-THEN rules or a Python function that implements the model.

Local Predictions
-----------------

Once you have a local model you can use to generate predictions locally.

::

    local_model.predict({"petal length": 3, "petal width": 1})
    petal length > 2.45 AND petal width <= 1.65 AND petal length <= 4.95 =>
    Iris-versicolor

Local predictions have three clear advantages:

- Removing the dependency from BigML to make new predictions.

- No cost in BigML (i.e., you do not spend BigML credits).

- Extremely low latency to generate predictions for huge volumes of data.


Fields
------

Once you have a resource you can use the ``Fields`` class to generate a
representation that will allow you to easily list fields, get fields ids, get a
field id by name, column number, etc.

::

    from bigml.fields import Fields

    fields = Fields(source['object']['fields'])

    # Internal id of the 'sepal length' field
    fields.field_id('sepal length')

    # Field name of field with column number 0
    fields.field_name(0)

    # Column number of field name 'petal length'
    fields.field_column_number('petal length')

You can also easily ``pair`` a list of values with fields ids what is very
useful to make predictions.

For example, the following snippet may be useful to create local predictions using
a csv file as input::

    test_reader = csv.reader(open(dir + test_set))
    local_model = Model(model)
    for row in test_reader:
        input_data = fields.pair([float(val) for val in row], objective_field)
        prediction = local_model.predict(input_data, by_name=False)


Rule Generation
---------------

You can also use a local model to generate a IF-THEN rule set that can be very
helpful to understand how the model works internally.

::

     local_model.rules()
     IF petal length > 2.45 AND
         IF petal width > 1.65 AND
             IF petal length > 5.05 THEN
                 species = Iris-virginica
             IF petal length <= 5.05 AND
                 IF sepal width > 2.9 AND
                     IF sepal length > 5.95 AND
                         IF petal length > 4.95 THEN
                             species = Iris-versicolor
                         IF petal length <= 4.95 THEN
                             species = Iris-virginica
                     IF sepal length <= 5.95 THEN
                          species = Iris-versicolor
                 IF sepal width <= 2.9 THEN
                     species = Iris-virginica
         IF petal width <= 1.65 AND
             IF petal length > 4.95 AND
                 IF sepal length > 6.05 THEN
                       species = Iris-virginica
                 IF sepal length <= 6.05 AND
                     IF sepal width > 2.45 THEN
                         species = Iris-versicolor
                     IF sepal width <= 2.45 THEN
                         species = Iris-virginica
             IF petal length <= 4.95 THEN
                 species = Iris-versicolor
     IF petal length <= 2.45 THEN
         species = Iris-setosa

Python Generation
-----------------

If you prefer you can also generate a Python function that implements the model
and that can be useful to make the model actionable right away with ``local_model.python()``.

::

    local_model.python()
    def predict_species(sepal_length=5.77889, sepal_width=3.02044, petal_length=4.34142, petal_width=1.32848):
       if (petal_length > 2.45):
           if (petal_width > 1.65):
               if (petal_length > 5.05):
                   return 'Iris-virginica'
               if (petal_length <= 5.05):
                   if (sepal_width > 2.9):
                       if (sepal_length > 5.95):
                           if (petal_length > 4.95):
                               return 'Iris-versicolor'
                           if (petal_length <= 4.95):
                               return 'Iris-virginica'
                       if (sepal_length <= 5.95):
                            return 'Iris-versicolor'
                   if (sepal_width <= 2.9):
                        return 'Iris-virginica'
           if (petal_width <= 1.65):
                if (petal_length > 4.95):
                     if (sepal_length > 6.05):
                          return 'Iris-virginica'
                     if (sepal_length <= 6.05):
                          if (sepal_width > 2.45):
                               return 'Iris-versicolor'
                          if (sepal_width <= 2.45):
                               return 'Iris-virginica'
                if (petal_length <= 4.95):
                     return 'Iris-versicolor'
        if (petal_length <= 2.45):
             return 'Iris-setosa'

Summary generation
------------------

You can also print the model from the point of view of the classes it predicts
with ``local_model.summarize()``.
It shows a header section with the training data initial distribution per class
(instances and percentage) and the final predicted distribution per class.

Then each class distribution is detailed. First a header section
shows the percentage of the total data that belongs to the class (in the
training set and in the predicted results) and the rules applicable to
all the
the instances of that class (if any). Just after that, a detail section shows
each of the leaves in which the class members are distributed.
They are sorted in descending
order by the percentage of predictions of the class that fall into that leaf
and also show the full rule chain that leads to it.

::

    Data distribution:
        Iris-setosa: 33.33% (50 instances)
        Iris-versicolor: 33.33% (50 instances)
        Iris-virginica: 33.33% (50 instances)


    Predicted distribution:
        Iris-setosa: 33.33% (50 instances)
        Iris-versicolor: 33.33% (50 instances)
        Iris-virginica: 33.33% (50 instances)




    Iris-setosa : (data 33.33% / prediction 33.33%) petal length <= 2.45
        · 100.00%: petal length <= 2.45


    Iris-versicolor : (data 33.33% / prediction 33.33%) petal length > 2.45
        · 94.00%: petal length > 2.45 and petal width <= 1.65 and petal length <= 4.95
        · 2.00%: petal length > 2.45 and petal width <= 1.65 and petal length > 4.95 and sepal length <= 6.05 and sepal width > 2.45
        · 2.00%: petal length > 2.45 and petal width > 1.65 and petal length <= 5.05 and sepal width > 2.9 and sepal length <= 5.95
        · 2.00%: petal length > 2.45 and petal width > 1.65 and petal length <= 5.05 and sepal width > 2.9 and sepal length > 5.95 and petal length > 4.95


    Iris-virginica : (data 33.33% / prediction 33.33%) petal length > 2.45
        · 76.00%: petal length > 2.45 and petal width > 1.65 and petal length > 5.05
        · 12.00%: petal length > 2.45 and petal width > 1.65 and petal length <= 5.05 and sepal width <= 2.9
        · 6.00%: petal length > 2.45 and petal width <= 1.65 and petal length > 4.95 and sepal length > 6.05
        · 4.00%: petal length > 2.45 and petal width > 1.65 and petal length <= 5.05 and sepal width > 2.9 and sepal length > 5.95 and petal length <= 4.95
        · 2.00%: petal length > 2.45 and petal width <= 1.65 and petal length > 4.95 and sepal length <= 6.05 and sepal width <= 2.45

You can also use ``local_model.get_data_distribution()`` and
``local_model.get_prediction_distribution()`` to obtain the training and
prediction basic distribution
information as a list (suitable to draw histograms or any further processing).

Running the Tests
-----------------

To run the tests you will need to install
`lettuce <http://packages.python.org/lettuce/tutorial/simple.html>`_::

    $ pip install lettuce

and set up your authentication via environment variables, as explained
above. With that in place, you can run the test suite simply by::

    $ cd tests
    $ lettuce

Additionally, `Tox <http://tox.testrun.org/>`_ can be used to
automatically run the test suite in virtual environments for all
supported Python versions.  To install Tox::

    $ pip install tox

Then run the tests from the top-level project directory::

    $ tox

Note that tox checks the exit status from the test command (lettuce) to
determine pass/fail, but the latest version of lettuce (0.2.5)
erroneously exits with a non-zero exit status indicating an error. So,
tox will report failures even if the test suite is passing. This
`should be fixed <https://github.com/gabrielfalcao/lettuce/pull/270>`_
in the next release of lettuce.

Building the Documentation
--------------------------

Install the tools required to build the documentation::

    $ pip install sphinx

To build the HTML version of the documentation::

    $ cd docs/
    $ make html

Then launch ``docs/_build/html/index.html`` in your browser.

Additional Information
----------------------

For additional information about the API, see the
`BigML developer's documentation <https://bigml.com/developers>`_.
