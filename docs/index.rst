.. toctree::
   :hidden:

   ml_resources
   creating_resources
   101_model
   101_ensemble
   101_deepnet
   101_linear_regression
   101_logistic_regression
   101_fusion
   101_ts
   101_optiml
   101_cluster
   101_anomaly
   101_topic_model
   101_association
   101_pca
   101_scripting
   101_images_classification
   101_images_feature_extraction
   101_object_detection
   reading_resources
   updating_resources
   deleting_resources
   local_resources
   whizzml_resources


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

Only ``Python 3`` versions are currently supported by these bindings.
Support for Python 2.7.X ended in version ``4.32.3``.

The basic third-party dependencies are the
`requests <https://github.com/kennethreitz/requests>`_,
`unidecode <http://pypi.python.org/pypi/Unidecode/#downloads>`_,
`requests-toolbelt <https://pypi.python.org/pypi/requests-toolbelt>`_,
`bigml-chronos <https://pypi.org/project/bigml-chronos>`_,
`msgpack <https://pypi.org/project/msgpack>`_,
`numpy <http://www.numpy.org/>`_ and
`scipy <http://www.scipy.org/>`_ libraries. These
libraries are automatically installed during the basic setup.
Support for Google App Engine has been added as of version 3.0.0,
using the `urlfetch` package instead of `requests`.

The bindings will also use ``simplejson`` if you happen to have it
installed, but that is optional: we fall back to Python's built-in JSON
libraries is ``simplejson`` is not found.

The bindings provide support to use the ``BigML`` platform to create, update,
get and delete resources, but also to produce local predictions using the
models created in ``BigML``. Most of them will be actionable with the basic
installation, but some additional dependencies are needed
to use local ``Topic Models`` to produce ``Topic Distributions``. These can
be installed using:

.. code-block:: bash

    pip install bigml[topics]

The bindings also support local predictions for models generated from images.
To use these models, an additional set of libraries needs to be installed
using:

.. code-block:: bash

    pip install bigml[images]

The external libraries used in this case exist for the majority of recent
Operative System versions. Still, some of them might need especific
compiler versions or dlls, so their installation may require an additional
setup effort.

The full set of libraries can be installed using

.. code-block:: bash

    pip install bigml[full]

Installation
------------

To install the latest stable release with
`pip <http://www.pip-installer.org/>`_, please use:

.. code-block:: bash

    $ pip install bigml

Support for local Topic Distributions (Topic Models' predictions)
and local predictions for datasets that include Images will only be
available as extras, because the libraries used for that are not
usually available in all Operative Systems. If you need to support those,
please check the `Installation Extras <#installation-extras>`_ section.

Installation Extras
-------------------

Local Topic Distributions support can be installed using:

.. code-block:: bash

    pip install bigml[topics]

Images local predictions support can be installed using:

.. code-block:: bash

    pip install bigml[images]

The full set of features can be installed using:

.. code-block:: bash

    pip install bigml[full]


WARNING: Mind that installing these extras can require some extra work, as
explained in the `Requirements <#requirements>`_ section.

You can also install the development version of the bindings directly
from the Git repository

.. code-block:: bash

    $ pip install -e git://github.com/bigmlcom/python.git#egg=bigml_python

Importing the module
--------------------

To import the module:

.. code-block:: python

    import bigml.api

Alternatively you can just import the BigML class:

.. code-block:: python

    from bigml.api import BigML

Authentication
--------------

All the requests to BigML.io must be authenticated using your username
and `API key <https://bigml.com/account/apikey>`_ and are always
transmitted over HTTPS.

This module will look for your username and API key in the environment
variables ``BIGML_USERNAME`` and ``BIGML_API_KEY`` respectively.

Unix and MacOS
--------------

You can
add the following lines to your ``.bashrc`` or ``.bash_profile`` to set
those variables automatically when you log in:

.. code-block:: bash

    export BIGML_USERNAME=myusername
    export BIGML_API_KEY=ae579e7e53fb9abd646a6ff8aa99d4afe83ac291

refer to the next chapters to know how to do that in other operating systems.

With that environment set up, connecting to BigML is a breeze:

.. code-block:: python

    from bigml.api import BigML
    api = BigML()

Otherwise, you can initialize directly when instantiating the BigML
class as follows:

.. code-block:: python

    api = BigML('myusername', 'ae579e7e53fb9abd646a6ff8aa99d4afe83ac291')

These credentials will allow you to manage any resource in your user
environment.

In BigML a user can also work for an ``organization``.
In this case, the organization administrator should previously assign
permissions for the user to access one or several particular projects
in the organization.
Once permissions are granted, the user can work with resources in a project
according to his permission level by creating a special constructor for
each project. The connection constructor in this case
should include the ``project ID``:

.. code-block:: python

    api = BigML('myusername', 'ae579e7e53fb9abd646a6ff8aa99d4afe83ac291',
                project='project/53739b98d994972da7001d4a')

If the project used in a connection object
does not belong to an existing organization but is one of the
projects under the user's account, all the resources
created or updated with that connection will also be assigned to the
specified project.

When the resource to be managed is a ``project`` itself, the connection
needs to include the corresponding``organization ID``:

.. code-block:: python

    api = BigML('myusername', 'ae579e7e53fb9abd646a6ff8aa99d4afe83ac291',
                organization='organization/53739b98d994972da7025d4a')


Authentication on Windows
-------------------------

The credentials should be permanently stored in your system using

.. code-block:: bash

    setx BIGML_USERNAME myusername
    setx BIGML_API_KEY ae579e7e53fb9abd646a6ff8aa99d4afe83ac291

Note that ``setx`` will not change the environment variables of your actual
console, so you will need to open a new one to start using them.


Authentication on Jupyter Notebook
----------------------------------

You can set the environment variables using the ``%env`` command in your
cells:

.. code-block:: bash

    %env BIGML_USERNAME=myusername
    %env BIGML_API_KEY=ae579e7e53fb9abd646a6ff8aa99d4afe83ac291


Alternative domains
-------------------


The main public domain for the API service is ``bigml.io``, but there are some
alternative domains, either for Virtual Private Cloud setups or
the australian subdomain (``au.bigml.io``). You can change the remote
server domain
to the VPC particular one by either setting the ``BIGML_DOMAIN`` environment
variable to your VPC subdomain:

.. code-block:: bash

    export BIGML_DOMAIN=my_VPC.bigml.io

or setting it when instantiating your connection:

.. code-block:: python

    api = BigML(domain="my_VPC.bigml.io")

The corresponding SSL REST calls will be directed to your private domain
henceforth.

You can also set up your connection to use a particular PredictServer
only for predictions. In order to do so, you'll need to specify a ``Domain``
object, where you can set up the general domain name as well as the
particular prediction domain name.

.. code-block:: python

    from bigml.domain import Domain
    from bigml.api import BigML

    domain_info = Domain(prediction_domain="my_prediction_server.bigml.com",
                         prediction_protocol="http")

    api = BigML(domain=domain_info)

Finally, you can combine all the options and change both the general domain
server, and the prediction domain server.

.. code-block:: python

    from bigml.domain import Domain
    from bigml.api import BigML
    domain_info = Domain(domain="my_VPC.bigml.io",
                         prediction_domain="my_prediction_server.bigml.com",
                         prediction_protocol="https")

    api = BigML(domain=domain_info)

Some arguments for the Domain constructor are more unsual, but they can also
be used to set your special service endpoints:

- protocol (string) Protocol for the service
  (when different from HTTPS)
- verify (boolean) Sets on/off the SSL verification
- prediction_verify (boolean) Sets on/off the SSL verification
  for the prediction server (when different from the general
  SSL verification)

**Note** that the previously existing ``dev_mode`` flag:

.. code-block:: python

    api = BigML(dev_mode=True)

that caused the connection to work with the Sandbox ``Development Environment``
has been **deprecated** because this environment does not longer exist.
The existing resources that were previously
created in this environment have been moved
to a special project in the now unique ``Production Environment``, so this
flag is no longer needed to work with them.

Quick Start
-----------

Imagine that you want to use `this csv
file <https://static.bigml.com/csv/iris.csv>`_ containing the `Iris
flower dataset <http://en.wikipedia.org/wiki/Iris_flower_data_set>`_ to
predict the species of a flower whose ``petal length`` is ``2.45`` and
whose ``petal width`` is ``1.75``. A preview of the dataset is shown
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

You can easily generate a prediction following these steps:

.. code-block:: python

    from bigml.api import BigML

    api = BigML()

    source = api.create_source('./data/iris.csv')
    dataset = api.create_dataset(source)
    model = api.create_model(dataset)
    prediction = api.create_prediction(model, \
        {"petal width": 1.75, "petal length": 2.45})

You can then print the prediction using the ``pprint`` method:

.. code-block:: python

    >>> api.pprint(prediction)
    species for {"petal width": 1.75, "petal length": 2.45} is Iris-setosa

Certainly, any of the resources created in BigML can be configured using
several arguments described in the `API documentation <https://bigml.com/api>`_.
Any of these configuration arguments can be added to the ``create`` method
as a dictionary in the last optional argument of the calls:

.. code-block:: python

    from bigml.api import BigML

    api = BigML()

    source_args = {"name": "my source",
         "source_parser": {"missing_tokens": ["NULL"]}}
    source = api.create_source('./data/iris.csv', source_args)
    dataset_args = {"name": "my dataset"}
    dataset = api.create_dataset(source, dataset_args)
    model_args = {"objective_field": "species"}
    model = api.create_model(dataset, model_args)
    prediction_args = {"name": "my prediction"}
    prediction = api.create_prediction(model, \
        {"petal width": 1.75, "petal length": 2.45},
        prediction_args)

The ``iris`` dataset has a small number of instances, and usually will be
instantly created, so the ``api.create_`` calls will probably return the
finished resources outright. As BigML's API is asynchronous,
in general you will need to ensure
that objects are finished before using them by using ``api.ok``.

.. code-block:: python

    from bigml.api import BigML

    api = BigML()

    source = api.create_source('./data/iris.csv')
    api.ok(source)
    dataset = api.create_dataset(source)
    api.ok(dataset)
    model = api.create_model(dataset)
    api.ok(model)
    prediction = api.create_prediction(model, \
        {"petal width": 1.75, "petal length": 2.45})

Note that the prediction
call is not followed by the ``api.ok`` method. Predictions are so quick to be
generated that, unlike the
rest of resouces, will be generated synchronously as a finished object.

Alternatively to the ``api.ok`` method, BigML offers
`webhooks <https://bigml.com/api/requests?id=webhooks>`_ that can be set
when creating a resource and will call the url of you choice when the
finished or failed event is reached. A secret can be included in the call to
verify the webhook call authenticity, and a

.. code-block:: python

    bigml.webhooks.check_signature(request, signature)

function is offered to that end. As an example, this snippet creates a source
and sets a webhook to call ``https://my_webhook.com/endpoint`` when finished:

.. code-block:: python

    from bigml.api import BigML
    api = BigML()
    # using a webhook with a secret
    api.create_source("https://static.bigml.com/csv/iris.csv",
            {"webhook": {"url": "https://my_webhook.com/endpoint",
                     "secret": "mysecret"}})


The ``iris`` prediction example assumed that your objective
field (the one you want to predict) is the last field in the dataset.
If that's not he case, you can explicitly
set the name of this field in the creation call using the ``objective_field``
argument:


.. code-block:: python

    from bigml.api import BigML

    api = BigML()

    source = api.create_source('./data/iris.csv')
    api.ok(source)
    dataset = api.create_dataset(source)
    api.ok(dataset)
    model = api.create_model(dataset, {"objective_field": "species"})
    api.ok(model)
    prediction = api.create_prediction(model, \
        {'sepal length': 5, 'sepal width': 2.5})


You can also generate an evaluation for the model by using:

.. code-block:: python

    test_source = api.create_source('./data/test_iris.csv')
    api.ok(test_source)
    test_dataset = api.create_dataset(test_source)
    api.ok(test_dataset)
    evaluation = api.create_evaluation(model, test_dataset)
    api.ok(evaluation)


The API object also offers the ``create``, ``get``, ``update`` and ``delete``
generic methods to manage all type of resources. The type of resource to be
created is passed as first argument to the ``create`` method;

.. code-block:: python

    from bigml.api import BigML

    api = BigML()

    source = api.create('source', './data/iris.csv')
    source = api.update(source, {"name": "my new source name"})

Note that these methods don't need the ``api.ok`` method to be called
to wait for the resource to be finished.
The method waits internally for it by default.
This can be avoided by using  ``finished=False`` as one of the arguments.


.. code-block:: python

    from bigml.api import BigML

    api = BigML()

    source = api.create('source', './data/iris.csv')
    dataset = api.create('dataset', source, finished=False) # unfinished
    api.ok(dataset) # waiting explicitly for the dataset to finish
    dataset = api.update(dataset, {"name": "my_new_dataset_name"},
                         finised=False)
    api.ok(dataset)

As an example for the ``delete`` and ``get`` methods, we could
create a batch prediction, put the predictions in a
dataset object and delete the ``batch_prediction``.

.. code-block:: python

    from bigml.api import BigML

    api = BigML()

    batch_prediction = api.create('batchprediction',
                                  'model/5f3c3d2b5299637102000882',
                                  'dataset/5f29a563529963736c0116e9',
                                  args={"output_dataset": True})
    batch_prediction_dataset = api.get(batch_prediction["object"][ \
        "output_dataset_resource"])
    api.delete(batch_prediction)

If you set the ``storage`` argument in the ``api`` instantiation:

.. code-block:: python

    api = BigML(storage='./storage')

all the generated, updated or retrieved resources will be automatically
saved to the chosen directory. Once they are stored locally, the
``retrieve_resource`` method will look for the resource information
first in the local storage before trying to download the information from
the API.

.. code-block:: python

    dataset = api.retrieve_resource("dataset/5e8e5672c7736e3d830037b5",
                                    query_string="limit=-1")


Alternatively, you can use the ``export`` method to explicitly
download the JSON information
that describes any of your resources in BigML to a particular file:

.. code-block:: python

    api.export('model/5acea49a08b07e14b9001068',
               filename="my_dir/my_model.json")

This example downloads the JSON for the model and stores it in
the ``my_dir/my_model.json`` file.

In the case of models that can be represented in a `PMML` syntax, the
export method can be used to produce the corresponding `PMML` file.

.. code-block:: python

    api.export('model/5acea49a08b07e14b9001068',
               filename="my_dir/my_model.pmml",
               pmml=True)

You can also retrieve the last resource with some previously given tag:

.. code-block:: python

     api.export_last("foo",
                     resource_type="ensemble",
                     filename="my_dir/my_ensemble.json")

which selects the last ensemble that has a ``foo`` tag. This mechanism can
be specially useful when retrieving retrained models that have been created
with a shared unique keyword as tag.

For a descriptive overview of the steps that you will usually need to
follow to model
your data and obtain predictions, please see the `basic Workflow sketch
<api_sketch.html>`_
document. You can also check other simple examples in the following documents:

- `model 101 <101_model.html>`_
- `logistic regression 101 <101_logistic_regression.html>`_
- `linear regression 101 <101_linear_regression.html>`_
- `ensemble 101 <101_ensemble.html>`_
- `cluster 101 <101_cluster>`_
- `anomaly detector 101 <101_anomaly.html>`_
- `association 101 <101_association.html>`_
- `topic model 101 <101_topic_model.html>`_
- `deepnet 101 <101_deepnet.html>`_
- `time series 101 <101_ts.html>`_
- `fusion 101 <101_fusion.html>`_
- `optiml 101 <101_optiml.html>`_
- `PCA 101 <101_pca.html>`_
- `scripting 101 <101_scripting.html>`_

And for examples on Image Processing:

- `Images Classification 101 <101_images_classification.html>`_
- `Object Detection 101<101_object_detection.html>`_
- `Images Feature Extraction 101 <101_images_feature_extraction.html>`_


Fields Structure
----------------

BigML automatically generates idenfiers for each field. To see the
fields and the ids and types that have been assigned to a source you can
use ``get_fields``:

.. code-block:: python

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

When the number of fields becomes very large, it can be useful to exclude or
paginate them. This can be done using a query string expression, for instance:

.. code-block:: python

    >>> source = api.get_source(source, "offset=0;limit=10&order_by=name")

would include in the retrieved dictionary the first 10 fields sorted by name.
There's a limit to the number of fields that will be included by default in
a resource description. If your resource has more than ``1000`` fields,
you can either paginate or force all the fields to be returned by using
``limit=-1`` as query string-

To handle field structures you can use the ``Fields`` class. See the
`Fields`_ section.

ML Resources
------------

You'll find a description of the basic resources available in BigML in
`ML Resources <ml_resources.html>`_

WhizzML Resources
-----------------

You'll learn about the scripting resources available in BigML in
`WhizzML Resources <whizzml_resources.html>`_. WizzML is our scripting
language that will allow you to create any workflow.


Managing Resources
------------------

You can learn how to create, update, retrieve, list and delete any resource in:

- `Creating Resources <creating_resources.html>`_
- `Updating Resources <updating_resources.html>`_
- `Deleting Resources <deleting_resources.html>`_
- `Reading, listing and filtering Resources <reading_resources.html>`_

Local Resources
---------------

You can learn how to download and use in your local environment any of the
models created in the BigML platform in
`Local Resources <local_resources.html>`_.

Fields
------

Once you have a resource, you can use the ``Fields`` class to generate a
representation that will allow you to easily list fields, get fields ids, get a
field id by name, column number, etc.

.. code-block:: python

    from bigml.api import BigML
    from bigml.fields import Fields
    api = BigML()
    source = api.get_source("source/5143a51a37203f2cf7000974")

    fields = Fields(source)

you can also instantiate the Fields object from the fields dict itself:

.. code-block:: python

    from bigml.api import BigML
    from bigml.fields import Fields
    api = BigML()
    source = api.get_source("source/5143a51a37203f2cf7000974")

    fields = Fields(source['object']['fields'])

The newly instantiated Fields object will give direct methods to retrieve
different fields properties:

.. code-block:: python

    # Internal id of the 'sepal length' field
    fields.field_id('sepal length')

    # Field name of field with column number 0
    fields.field_name(0)

    # Column number of field name 'petal length'
    fields.field_column_number('petal length')

    # Statistics of values in field name 'petal length')
    fields.stats('petal length')

Depending on the resource type, Fields information will vary. ``Sources`` will
have only the name, label, description, type of field (``optype``) while
``dataset`` resources will have also the ``preferred`` (whether a field will is
selectable as predictor), ``missing_count``, ``errors`` and a summary of
the values found in each field. This is due to the fact that the ``source``
object is built by inspecting the contents of a sample of the uploaded file,
while the ``dataset`` resource really reads all the uploaded information. Thus,
dataset's fields structure will always be more complete than source's.

In both cases, you can extract the summarized information available using
the ``summary_csv`` method:

.. code-block:: python

    from bigml.api import BigML
    from bigml.fields import Fields
    api = BigML()
    dataset = api.get_dataset("dataset/5143a51a37203f2cf7300974")

    fields = Fields(dataset)
    fields.summary_csv("my_fields_summary.csv")

In this example, the information will be stored in the
``my_fields_summary.csv`` file. For the typical ``iris.csv`` data file, the
summary will read:

.. csv-table::
   :header: "field column","field ID","field name","field label","field description","field type","preferred","missing count","errors","contents summary","errors summary"
   :widths: 5, 10, 20, 5, 5, 10, 10, 5, 5, 100, 10

   0,000000,sepal length,,,numeric,true,0,0,"[4.3, 7.9], mean: 5.84333",
   1,000001,sepal width,,,numeric,false,0,0,"[2, 4.4], mean: 3.05733",
   2,000002,petal length,,,numeric,true,0,0,"[1, 6.9], mean: 3.758",
   3,000003,petal width,,,numeric,true,0,0,"[0.1, 2.5], mean: 1.19933",
   4,000004,species,,,categorical,true,0,0,"3 categorìes: Iris-setosa (50), Iris-versicolor (50), Iris-virginica (50)",

Another utility in the ``Fields`` object will help you update the updatable
attributes of your source or dataset fields. For instance, if you
need to update the type associated to one field in your dataset,
you can change the ``field type``
values in the previous file and use it to obtain the fields structure
needed to update your source:

.. code-block:: python

    from bigml.api import BigML
    from bigml.fields import Fields
    api = BigML()
    source = api.get_source("source/5143a51a37203f2cf7000974")

    fields = Fields(source)
    fields_update_info = fields.new_fields_structure("my_fields_summary.csv")
    source = api.update_source(source, \
        fields.filter_fields_update(fields_update_info))

where ``filter_fields_update`` will make sure that only the attributes that
can be updated in a source will be sent in the update request.
For both sources and datasets, the updatable attributes are ``name``, ``label``
and ``description``.
In ``sources`` you can also update the type of the field (``optype``), and
in ``datasets`` you can update the ``preferred`` attribute.

In addition to that, you can also easily ``pair`` a list of values with fields
ids what is very
useful to make predictions.

For example, the following snippet may be useful to create local predictions
using a csv file as input:

.. code-block:: python

    test_reader = csv.reader(open(dir + test_set))
    local_model = Model(model)
    for row in test_reader:
        input_data = fields.pair([float(val) for val in row], objective_field)
        prediction = local_model.predict(input_data)

If missing values are present, the ``Fields`` object can return a dict
with the ids of the fields that contain missing values and its count. The
following example:

.. code-block:: python

    from bigml.fields import Fields
    from bigml.api import BigML
    api = BigML()
    dataset = api.get_dataset("dataset/5339d42337203f233e000015")

    fields = Fields(dataset)
    fields.missing_counts()

would output:

.. code-block:: python

    {'000003': 1, '000000': 1, '000001': 1}

if the there was a missing value in each of the fields whose ids are
``000003``, ``000000``, ``000001``.

You can also obtain the counts of errors per field using the ``errors_count``
method of the api:

.. code-block:: python

    from bigml.api import BigML
    api = BigML()
    dataset = api.get_dataset("dataset/5339d42337203f233e000015")
    api.error_counts(dataset)

The generated output is like the one in ``missing_counts``, that is, the error
counts per field:

.. code-block:: python

    {'000000': 1}


Account and tasks
-----------------

In BigML, every account has an associated subscription level. The subscription
level will determine the number of tasks that can be performed in parallel in
the platform and the maximum allowed dataset size. This kind of information is
available through the methods ``.get_account_status`` and ``get_tasks_status``
in the connection object:

.. code-block:: python

    from bigml.api import BigML
    api = BigML()
    api.get_tasks_status()

The result will be a dictionary that contains the number of tasks in use
and their status, the maximum number of tasks and the number of tasks
available. This information can be used to manage the complexity of sending
new creation tasks to BigML.

However, we strongly discourage the use of this kind of mechanism, because
it's clearly suboptimal and cumbersome compared to using the scripting
utilities in the platform described in next sections and the ``101``
documents in the `quick start <#quick-start>`_ section. Scalability,
reproducibility and reusability are the key points in Machine Learning
automation and using WhizzML, BigML's Domain Specific Language for
Machine Learning, provides them out of the box. Client-side approaches
and/or general languages are definitely not the best fit for that.

Environment variables
---------------------

The bindings will read some configuration values from environment variables.

- ``BIGML_USERNAME``: The name of the user in BigML
- ``BIGML_API_KEY``: The API key for authentication in BigML

For VPCs or on-site API installs,
other than the general public ``bigml.io`` domain:

- ``BIGML_DOMAIN``: The domain of the BigML API endpoints
- ``BIGML_PROTOCOL``: ``http``/``https`` protocol
- ``BIGML_API_VERSION``: `andromeda`` version name (empty string if using
    PredictServer)
- ``BIGML_SSL_VERIFY``: (``0``/``1``) to set SSL verification

If you are using a Predict Server (or a different API url only for predictions)

- ``BIGML_PREDICTION_DOMAIN``: The domain of the BigML API prediction endpoint
- ``BIGML_PREDICTION_PROTOCOL``: ``http``/``https`` for prediction domain
- ``BIGML_PREDICTION_SSL_VERIFY``: (``0``/``1``) to set SSL verification for
  predictions

For users working in an organization:

- ``BIGML_ORGANIZATION``: The ID of the organization

To use external data connectors:

- ``BIGML_EXTERNAL_CONN_HOST``: Host name or IP for the external database
- ``BIGML_EXTERNAL_CONN_PORT``: Port for the exteranl database
- ``BIGML_EXTERNAL_CONN_DB``: Database name
- ``BIGML_EXTERNAL_CONN_USER``: Database user name
- ``BIGML_EXTERNAL_CONN_PWD``: Database user password
- ``BIGML_EXTERNAL_CONN_SOURCE``: Type of database: ``mysql``, ``postgresql``,
  ``elasticsearch``, etc. (see details in the
  `API documentation for external connectors <https://bigml.com/api/externalconnectors>`_)

Running the Tests
-----------------

The tests will be run using `nose <https://nose.readthedocs.org/en/latest/>`_
and `pytest <https://docs.pytest.org/en/7.2.x/>`_ as a transition to pytest
stardard tests. You'll need to set up your authentication
via environment variables, as explained
in the authentication section. Also some of the tests need other environment
variables like ``BIGML_ORGANIZATION`` to test calls when used by Organization
members and ``BIGML_EXTERNAL_CONN_HOST``, ``BIGML_EXTERNAL_CONN_PORT``,
``BIGML_EXTERNAL_CONN_DB``, ``BIGML_EXTERNAL_CONN_USER``,
``BIGML_EXTERNAL_CONN_PWD`` and ``BIGML_EXTERNAL_CONN_SOURCE``
in order to test external data connectors.

With that in place, you can run the test suite simply by issuing

.. code-block:: bash

    $ pytest

Additionally, `Tox <http://tox.testrun.org/>`_ can be used to
automatically run the test suite in virtual environments for all
supported Python versions.  To install Tox:

.. code-block:: bash

    $ pip install tox

Then run the tests from the top-level project directory:

.. code-block:: bash

    $ tox

Building the Documentation
--------------------------

Install the tools required to build the documentation:

.. code-block:: bash

    $ pip install sphinx

To build the HTML version of the documentation:

.. code-block:: bash

    $ cd docs/
    $ make html

Then launch ``docs/_build/html/index.html`` in your browser.

Additional Information
----------------------

For additional information about the API, see the
`BigML developer's documentation <https://bigml.com/api>`_.
