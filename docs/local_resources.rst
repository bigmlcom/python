.. toctree::
   :hidden:

Local Resources
===============

All the resources in BigML can be downloaded and used locally with no
connection whatsoever to BigML's servers. This is specially important
for all Supervised and Unsupervised models, that can be used to generate
predictions in any programmable device. The next sections describe how to
do that for each type of resource, but as a general rule, resources can be
exported to a JSON file in your file system using the ``export`` method.

.. code-block:: python

    api.export('model/5143a51a37203f2cf7000956',
               'filename': 'my_dir/my_model.json')

The contents of the generated file can be used just as the remote model
to generate predictions. As you'll see in next section, the local ``Model``
object can be instantiated by giving the path to this file as first argument:

.. code-block:: python

    from bigml.model import Model
    local_model = Model("my_dir/my_model.json")
    local_model.predict({"petal length": 3, "petal width": 1})
    Iris-versicolor

These bindings define a particular class for each type of Machine Learning
model that is able to interpret the corresponding JSON and create
the local predictions. The classes can be instantiated using:

- The ID of the resource: In this case, the class looks for the JSON
  information of the resource first locally (expecting to find a file
  in the local storage directory --``./storage`` by default --
  whose name is the ID of the model after replacing ``/`` by ``_``)
  and also remotely if absent.

.. code-block:: python

    from bigml.model import Model
    from bigml.api import BigML

    local_model = Model('model/502fdbff15526876610002615')

- A dictionary containing the resource information. In this case, the class
  checks that this information belongs to a finished resource and
  contains the attributes needed to create predictions, like the fields
  structure. If any of these attributes is absent, retrieves the ID of the
  model and tries to download the correct JSON from the API to store it
  locally for further use.


.. code-block:: python

    from bigml.anomaly import Anomaly
    from bigml.api import BigML
    api = BigML()
    anomaly = api.get_anomaly('anomaly/502fdbff15526876610002615',
                              query_string='only_model=true;limit=-1')

    local_anomaly = Anomaly(anomaly)

- A path to the file that contains the JSON information for the resource.
  In this case, the
  file is read and the same checks mentioned above are done. If any of these
  checks fails, it tries to retrieve the correct JSON from the API to store
  it locally for further use.

.. code-block:: python

    from bigml.logistic import LogisticRegression
    local_logistic_regression = LogisticRegression('./my_logistic.json')

Internally, these classes need a connection object (``api = BigML()``) to:

- Know the local storage in your file system.
- Download the JSON of the resource if the information provided is not the
  full finished resource content.

Users can provide the connection as a second argument when instantiating the
class:

.. code-block:: python

    from bigml.cluster import Cluster
    from bigml.api import BigML

    local_cluster = Cluster('cluster/502fdbff15526876610002435',
                            api=BigML(my_username,
                                      my_api_key
                                      storage="my_storage"))

If no connection is provided, a default connection will be
instantiated internally. This default connection will use ``./storage``
as default storage directory and the credentials used to connect to
the API when needed are retrieved from the ``BIGML_USERNAME`` and
``BIGML_API_KEY`` environment variables. If no credentials are found in your
environment, any attempt to download the information will raise a condition
asking the user to set these variables.

Ensembles and composite objects, like Fusions, need more than one resource
to be downloaded and stored locally for the class to work. In this case,
the class needs all the component models,
so providing only a local file or a dictionary containing the
JSON for the resource is not enough for the ``Ensemble`` or ``Fusion``
objects to be fully instantiated. If you only provide that partial information,
the class will use the internal API connection the first time
to download the components.
However, using the ``api.export`` method for ensembles or fusions
will download these component models for you
and will store them in the same directory as the file used to store
the ensemble or fusion information. After that, you can
instantiate the object using the path to the file where the ensemble
or fusion information was stored. The class will look internally for the
rest of components in the same directory and find them, so no connection to
the API will be done.

If you use a tag to label the resource, you can also ask for the last resource
that has the tag:

.. code-block:: python

    api.export_last('my_tag',
                    resource_type='ensemble',
                    'filename': 'my_dir/my_ensemble.json')

and even for a resource inside a project:

.. code-block:: python

    api.export_last('my_tag',
                    resource_type='dataset',
                    project='project/5143a51a37203f2cf7000959',
                    'filename': 'my_dir/my_dataset.json')


Local Models
------------

You can instantiate a local version of a remote model.

.. code-block:: python

    from bigml.model import Model
    local_model = Model('model/502fdbff15526876610002615')

This will retrieve the remote model information, using an implicitly built
``BigML()`` connection object (see the `Authentication <#authentication>`_
section for more
details on how to set your credentials) and return a Model object
that will be stored in the ``./storage`` directory and
you can use to make local predictions. If you want to use a
specific connection object for the remote retrieval or a different storage
directory, you can set it as second parameter:

.. code-block:: python

    from bigml.model import Model
    from bigml.api import BigML

    local_model = Model('model/502fdbff15526876610002615',
                        api=BigML(my_username,
                                  my_api_key,
                                  storage="my_storage"))

or even use the remote model information previously retrieved to build the
local model object:

.. code-block:: python

    from bigml.model import Model
    from bigml.api import BigML
    api = BigML()
    model = api.get_model('model/502fdbff15526876610002615',
                          query_string='only_model=true;limit=-1')

    local_model = Model(model)

As you can see, the ``query_string`` used to retrieve the model has two parts.
They both act on the ``fields``
information that is added to the JSON response. First
``only_model=true`` is used to restrict the fields described in the
``fields`` structure of the response to those used as
predictors in the model. Also
``limit=-1`` avoids the pagination of fields which is used by default and
includes them all at once. These details are already taken care of in the
two previous examples, where the model ID is used as argument.

Any of these methods will return a ``Model`` object that you can use to make
local predictions, generate IF-THEN rules, Tableau rules
or a Python function that implements the model.

You can also build a local model from a model previously retrieved and stored
in a JSON file:

.. code-block:: python

    from bigml.model import Model
    local_model = Model('./my_model.json')


Local Predictions
-----------------

Once you have a local model you can use to generate predictions locally.

.. code-block:: python

    local_model.predict({"petal length": 3, "petal width": 1})
    Iris-versicolor

Local predictions have three clear advantages:

- Removing the dependency from BigML to make new predictions.

- No cost (i.e., you do not spend BigML credits).

- Extremely low latency to generate predictions for huge volumes of data.

The default output for local predictions is the prediction itself, but you can
also add other properties associated to the prediction, like its
confidence or probability, the distribution of values in the predicted node
(for decision tree models), and the number of instances supporting the
prediction. To obtain a
dictionary with the prediction and the available additional
properties use the ``full=True`` argument:

.. code-block:: python

    local_model.predict({"petal length": 3, "petal width": 1}, full=True)

that will return:

.. code-block:: python

    {'count': 47,
     'confidence': 0.92444,
     'probability': 0.9861111111111112,
     'prediction': u'Iris-versicolor',
     'distribution_unit': 'categories',
     'path': [u'petal length > 2.45',
              u'petal width <= 1.75',
              u'petal length <= 4.95',
              u'petal width <= 1.65'],
     'distribution': [[u'Iris-versicolor', 47]]}

Note that the ``path`` attribute for the ``proportional`` missing strategy
shows the path leading to a final unique node, that gives the prediction, or
to the first split where a missing value is found. Other optional
attributes are
``next`` which contains the field that determines the next split after
the prediction node and ``distribution`` that adds the distribution
that leads to the prediction. For regression models, ``min`` and
``max`` will add the limit values for the data that supports the
prediction.

When your test data has missing values, you can choose between ``last
prediction`` or ``proportional`` strategy to compute the
prediction. The ``last prediction`` strategy is the one used by
default. To compute a prediction, the algorithm goes down the model's
decision tree and checks the condition it finds at each node (e.g.:
'sepal length' > 2). If the field checked is missing in your input
data you have two options: by default (``last prediction`` strategy)
the algorithm will stop and issue the last prediction it computed in
the previous node. If you chose ``proportional`` strategy instead, the
algorithm will continue to go down the tree considering both branches
from that node on. Thus, it will store a list of possible predictions
from then on, one per valid node. In this case, the final prediction
will be the majority (for categorical models) or the average (for
regressions) of values predicted by the list of predicted values.

You can set this strategy by using the ``missing_strategy``
argument with code ``0`` to use ``last prediction`` and ``1`` for
``proportional``.

.. code-block:: python

    from bigml.model import LAST_PREDICTION, PROPORTIONAL
    # LAST_PREDICTION = 0; PROPORTIONAL = 1
    local_model.predict({"petal length": 3, "petal width": 1},
                        missing_strategy=PROPORTIONAL)

For classification models, it is sometimes useful to obtain a
probability or confidence prediction for each possible class of the
objective field.  To do this, you can use the ``predict_probability``
and ``predict_confidence`` methods respectively.  The former gives a
prediction based on the distribution of instances at the appropriate
leaf node, with a Laplace correction based on the root node
distribution.  The latter returns a lower confidence bound on the leaf
node probability based on the Wilson score interval.

Each of these methods take the ``missing_strategy``
argument that functions as it does in ``predict``, and one additional
argument, ``compact``.  If ``compact`` is ``False`` (the default), the
output of these functions is a list of maps, each with the keys
``prediction`` and ``probability`` (or ``confidence``) mapped to the
class name and its associated probability (or confidence). Note that these
methods substitute the deprecated ``multiple`` parameter in the ``predict``
method functionallity.

So, for example, the following:

.. code-block:: python

    local_model.predict_probability({"petal length": 3})

would result in

.. code-block:: python

    [{'prediction': u'Iris-setosa',
      'probability': 0.0033003300330033},
     {'prediction': u'Iris-versicolor',
      'probability': 0.4983498349834984},
     {'prediction': u'Iris-virginica',
      'probability': 0.4983498349834984}]

If ``compact`` is ``True``, only the probabilities themselves are
returned, as a list in class name order.  Note that, for reference,
the attribute ``Model.class_names`` contains the class names in the
appropriate ordering.

To illustrate, the following:

.. code-block:: python

    local_model.predict_probability({"petal length": 3}, compact=True)

would result in

.. code-block:: python

    [0.0033003300330033, 0.4983498349834984, 0.4983498349834984]

The output of ``predict_confidence`` is the same, except that the
output maps are keyed with ``confidence`` instead of ``probability``.


For classifications, the prediction of a local model will be one of the
available categories in the objective field and an associated ``confidence``
or ``probability`` that is used to decide which is the predicted category.
If you prefer the model predictions to be operated using any of them, you can
use the ``operating_kind`` argument in the ``predict`` method.
Here's the example
to use predictions based on ``confidence``:

.. code-block:: python

    local_model.predict({"petal length": 3, "petal width": 1},
                        {"operating_kind": "confidence"})

Previous versions of the bindings had additional arguments in the ``predict``
method that were used to format the prediction attributes. The signature of
the method has been changed to accept only arguments that affect the
prediction itself, (like ``missing_strategy``, ``operating_kind`` and
``opreating_point``) and ``full`` which is a boolean that controls whether
the output is the prediction itself or a dictionary will all the available
properties associated to the prediction. Formatting can be achieved by using
the ``cast_prediction`` function:

.. code-block:: python

    def cast_prediction(full_prediction, to=None,
                        confidence=False, probability=False,
                        path=False, distribution=False,
                        count=False, next=False, d_min=False,
                        d_max=False, median=False,
                        unused_fields=False):

whose first argument is the prediction obtained with the ``full=True``
argument, the second one defines the type of output (``None`` to obtain
the prediction output only, "list" or "dict") and the rest of booleans
cause the corresponding property to be included or not.

Operating point's predictions
-----------------------------

In classification problems,
Models, Ensembles and Logistic Regressions can be used at different
operating points, that is, associated to particular thresholds. Each
operating point is then defined by the kind of property you use as threshold,
its value and a the class that is supposed to be predicted if the threshold
is reached.

Let's assume you decide that you have a binary problem, with classes ``True``
and ``False`` as possible outcomes. Imagine you want to be very sure to
predict the `True` outcome, so you don't want to predict that unless the
probability associated to it is over ``0,8``. You can achieve this with any
classification model by creating an operating point:

.. code-block:: python

    operating_point = {"kind": "probability",
                       "positive_class": "True",
                       "threshold": 0.8};

to predict using this restriction, you can use the ``operating_point``
parameter:

.. code-block:: python

    prediction = local_model.predict(inputData,
                                     operating_point=operating_point)

where ``inputData`` should contain the values for which you want to predict.
Local models allow two kinds of operating points: ``probability`` and
``confidence``. For both of them, the threshold can be set to any number
in the ``[0, 1]`` range.


Local Clusters
--------------

You can also instantiate a local version of a remote cluster.

.. code-block:: python

    from bigml.cluster import Cluster
    local_cluster = Cluster('cluster/502fdbff15526876610002435')

This will retrieve the remote cluster information, using an implicitly built
``BigML()`` connection object (see the `Authentication <#authentication>`_
section for more
details on how to set your credentials) and return a ``Cluster`` object
that will be stored in the ``./storage`` directory and
you can use to make local centroid predictions. If you want to use a
specific connection object for the remote retrieval or a different storage
directory, you can set it as second
parameter:

.. code-block:: python

    from bigml.cluster import Cluster
    from bigml.api import BigML

    local_cluster = Cluster('cluster/502fdbff15526876610002435',
                            api=BigML(my_username,
                                      my_api_key
                                      storage="my_storage"))

or even use the remote cluster information previously retrieved to build the
local cluster object:

.. code-block:: python

    from bigml.cluster import Cluster
    from bigml.api import BigML
    api = BigML()
    cluster = api.get_cluster('cluster/502fdbff15526876610002435',
                              query_string='limit=-1')

    local_cluster = Cluster(cluster)

Note that in this example we used a ``limit=-1`` query string for the cluster
retrieval. This ensures that all fields are retrieved by the get method in the
same call (unlike in the standard calls where the number of fields returned is
limited).

Local clusters provide also methods for the significant operations that
can be done using clusters: finding the centroid assigned to a certain data
point, sorting centroids according to their distance to a data point,
summarizing
the centroids intra-distances and inter-distances and also finding the
closest points to a given one. The `Local Centroids <#local-centroids>`_
and the
`Summary generation <#summary-generation>`_ sections will
explain these methods.

Local Centroids
---------------

Using the local cluster object, you can predict the centroid associated to
an input data set:

.. code-block:: python

    local_cluster.centroid({"pregnancies": 0, "plasma glucose": 118,
                            "blood pressure": 84, "triceps skin thickness": 47,
                            "insulin": 230, "bmi": 45.8,
                            "diabetes pedigree": 0.551, "age": 31,
                            "diabetes": "true"})
    {'distance': 0.454110207355, 'centroid_name': 'Cluster 4',
     'centroid_id': '000004'}


You must keep in mind, though, that to obtain a centroid prediction, input data
must have values for all the numeric fields. No missing values for the numeric
fields are allowed unless you provided a ``default_numeric_value`` in the
cluster construction configuration. If so, this value will be used to fill
the missing numeric fields.

As in the local model predictions, producing local centroids can be done
independently of BigML servers, so no cost or connection latencies are
involved.

Another interesting method in the cluster object is
``local_cluster.closests_in_cluster``, which given a reference data point
will provide the rest of points that fall into the same cluster sorted
in an ascending order according to their distance to this point. You can limit
the maximum number of points returned by setting the ``number_of_points``
argument to any positive integer.

.. code-block:: python

    local_cluster.closests_in_cluster( \
        {"pregnancies": 0, "plasma glucose": 118,
         "blood pressure": 84, "triceps skin thickness": 47,
         "insulin": 230, "bmi": 45.8,
         "diabetes pedigree": 0.551, "age": 31,
         "diabetes": "true"}, number_of_points=2)

The response will be a dictionary with the centroid id of the cluster an
the list of closest points and their distances to the reference point.

.. code-block:: python

    {'closest': [ \
        {'distance': 0.06912270988567025,
         'data': {'plasma glucose': '115', 'blood pressure': '70',
                  'triceps skin thickness': '30', 'pregnancies': '1',
                  'bmi': '34.6', 'diabetes pedigree': '0.529',
                  'insulin': '96', 'age': '32', 'diabetes': 'true'}},
        {'distance': 0.10396456577958413,
         'data': {'plasma glucose': '167', 'blood pressure': '74',
         'triceps skin thickness': '17', 'pregnancies': '1', 'bmi': '23.4',
         'diabetes pedigree': '0.447', 'insulin': '144', 'age': '33',
         'diabetes': 'true'}}],
    'reference': {'age': 31, 'bmi': 45.8, 'plasma glucose': 118,
                  'insulin': 230, 'blood pressure': 84,
                  'pregnancies': 0, 'triceps skin thickness': 47,
                  'diabetes pedigree': 0.551, 'diabetes': 'true'},
    'centroid_id': u'000000'}

No missing numeric values are allowed either in the reference data point.
If you want the data points to belong to a different cluster, you can
provide the ``centroid_id`` for the cluster as an additional argument.

Other utility methods are ``local_cluster.sorted_centroids`` which given
a reference data point will provide the list of centroids sorted according
to the distance to it

.. code-block:: python

    local_cluster.sorted_centroids( \
    {'plasma glucose': '115', 'blood pressure': '70',
     'triceps skin thickness': '30', 'pregnancies': '1',
     'bmi': '34.6', 'diabetes pedigree': '0.529',
     'insulin': '96', 'age': '32', 'diabetes': 'true'})
    {'centroids': [{'distance': 0.31656890408929705,
                    'data': {u'000006': 0.34571, u'000007': 30.7619,
                             u'000000': 3.79592, u'000008': u'false'},
                    'centroid_id': u'000000'},
                   {'distance': 0.4424198506958207,
                    'data': {u'000006': 0.77087, u'000007': 45.50943,
                             u'000000': 5.90566, u'000008': u'true'},
                    'centroid_id': u'000001'}],
     'reference': {'age': '32', 'bmi': '34.6', 'plasma glucose': '115',
                   'insulin': '96', 'blood pressure': '70',
                   'pregnancies': '1', 'triceps skin thickness': '30',
                   'diabetes pedigree': '0.529', 'diabetes': 'true'}}



or ``points_in_cluster`` that returns the list of
data points assigned to a certain cluster, given its ``centroid_id``.

.. code-block:: python

    centroid_id = "000000"
    local_cluster.points_in_cluster(centroid_id)


Local Anomaly Detector
----------------------

You can also instantiate a local version of a remote anomaly.

.. code-block:: python

    from bigml.anomaly import Anomaly
    local_anomaly = Anomaly('anomaly/502fcbff15526876610002435')

This will retrieve the remote anomaly detector information, using an implicitly
built ``BigML()`` connection object (see the `Authentication <#authentication>`_
section for
more details on how to set your credentials) and return an ``Anomaly`` object
that will be stored in the ``./storage`` directory and
you can use to make local anomaly scores. If you want to use a
specific connection object for the remote retrieval or a different storage
directory, you can set it as second
parameter:

.. code-block:: python

    from bigml.anomaly import Anomaly
    from bigml.api import BigML

    local_anomaly = Anomaly('anomaly/502fcbff15526876610002435',
                            api=BigML(my_username,
                                      my_api_key,
                                      storage="my_storage_dir"))

or even use the remote anomaly information retrieved previously to build the
local anomaly detector object:

.. code-block:: python

    from bigml.anomaly import Anomaly
    from bigml.api import BigML
    api = BigML()
    anomaly = api.get_anomaly('anomaly/502fcbff15526876610002435',
                              query_string='limit=-1')

    local_anomaly = Anomaly(anomaly)

Note that in this example we used a ``limit=-1`` query string for the anomaly
retrieval. This ensures that all fields are retrieved by the get method in the
same call (unlike in the standard calls where the number of fields returned is
limited).

The anomaly detector object has also the method ``anomalies_filter``
that will build the LISP filter you would need to filter the original
dataset and create a new one excluding
the top anomalies. Setting the ``include`` parameter to True you can do the
inverse and create a dataset with only the most anomalous data points.


Local Anomaly Scores
--------------------

Using the local anomaly detector object, you can predict the anomaly score
associated to an input data set:

.. code-block:: python

    local_anomaly.anomaly_score({"src_bytes": 350})
    0.9268527808726705


As in the local model predictions, producing local anomaly scores can be done
independently of BigML servers, so no cost or connection latencies are
involved.

Local Anomaly caching
---------------------

Anomalies can become quite large objects. That's why their use of memory
resources can be heavy. If your usual scenario is using many of them
constantly in a disordered way, the best strategy is setting up a cache
system to store them. The local anomaly class provides helpers to
interact with that cache. Here's an example using ``Redis``.

.. code-block:: python

    from anomaly import Anomaly
    import redis
    r = redis.Redis()
    # First build as you would any core Anomaly object:
    anomaly = Anomaly('anomaly/5126965515526876630001b2')
    # Store a serialized version in Redis
    anomaly.dump(cache_set=r.set)
    # (retrieve the external rep from its convenient place)
    # Speedy Build from external rep
    anomaly = Anomaly('anomaly/5126965515526876630001b2', cache_get=r.get)
    # Get scores same as always:
    anomaly.anomaly_score({"src_bytes": 350})


Local Logistic Regression
-------------------------

You can also instantiate a local version of a remote logistic regression.

.. code-block:: python

    from bigml.logistic import LogisticRegression
    local_log_regression = LogisticRegression(
        'logisticregression/502fdbff15526876610042435')

This will retrieve the remote logistic regression information,
using an implicitly built
``BigML()`` connection object (see the `Authentication <#authentication>`_
section for more
details on how to set your credentials) and return a ``LogisticRegression``
object that will be stored in the ``./storage`` directory and
you can use to make local predictions. If you want to use a
specific connection object for the remote retrieval or a different storage
directory, you can set it as second
parameter:

.. code-block:: python

    from bigml.logistic import LogisticRegression
    from bigml.api import BigML

    local_log_regression = LogisticRegression(
        'logisticregression/502fdbff15526876610602435',
        api=BigML(my_username, my_api_key, storage="my_storage"))

You can also reuse a remote logistic regression JSON structure
as previously retrieved to build the
local logistic regression object:

.. code-block:: python

    from bigml.logistic import LogisticRegression
    from bigml.api import BigML
    api = BigML()
    logistic_regression = api.get_logistic_regression(
        'logisticregression/502fdbff15526876610002435',
        query_string='limit=-1')

    local_log_regression = LogisticRegression(logistic_regression)

Note that in this example we used a ``limit=-1`` query string for the
logistic regression retrieval. This ensures that all fields are
retrieved by the get method in the same call (unlike in the standard
calls where the number of fields returned is limited).

Local Logistic Regression Predictions
-------------------------------------

Using the local logistic regression object, you can predict the prediction for
an input data set:

.. code-block:: python

    local_log_regression.predict({"petal length": 2, "sepal length": 1.5,
                                  "petal width": 0.5, "sepal width": 0.7},
                                  full=True)
    {'distribution': [
        {'category': u'Iris-virginica', 'probability': 0.5041444478857267},
        {'category': u'Iris-versicolor', 'probability': 0.46926542042788333},
        {'category': u'Iris-setosa', 'probability': 0.02659013168639014}],
        'prediction': u'Iris-virginica', 'probability': 0.5041444478857267}

As you can see, the prediction contains the predicted category and the
associated probability. It also shows the distribution of probabilities for
all the possible categories in the objective field. If you only need the
predicted value, you can remove the ``full`` argument.

You must keep in mind, though, that to obtain a logistic regression
prediction, input data
must have values for all the numeric fields. No missing values for the numeric
fields are allowed.

For consistency of interface with the ``Model`` class, logistic
regressions again have a ``predict_probability`` method, which takes
the same argument as ``Model.predict``:
``compact``.  As stated above, missing values are not allowed, and so
there is no ``missing_strategy`` argument.

As with local Models, if ``compact`` is ``False`` (the default), the
output is a list of maps, each with the keys ``prediction`` and
``probability`` mapped to the class name and its associated
probability.

So, for example

.. code-block:: python

    local_log_regression.predict_probability({"petal length": 2, "sepal length": 1.5,
                                              "petal width": 0.5, "sepal width": 0.7})

    [{'category': u'Iris-setosa', 'probability': 0.02659013168639014},
     {'category': u'Iris-versicolor', 'probability': 0.46926542042788333},
     {'category': u'Iris-virginica', 'probability': 0.5041444478857267}]

If ``compact`` is ``True``, only the probabilities themselves are
returned, as a list in class name order, again, as is the case with
local Models.

Operating point predictions are also available for local logistic regressions
and an example of it would be:

.. code-block:: python

    operating_point = {"kind": "probability",
                       "positive_class": "True",
                       "threshold": 0.8}
    local_logistic.predict(inputData, operating_point=operating_point)

You can check the
`Operating point's predictions <#operating-point's-predictions>`_ section
to learn about
operating points. For logistic regressions, the only available kind is
``probability``, that sets the threshold of probability to be reached for the
prediction to be the positive class.

Local Logistic Regression
-------------------------

You can also instantiate a local version of a remote logistic regression:

.. code-block:: python

    from bigml.logistic import LogisticRegression
    local_log_regression = LogisticRegression(
        'logisticregression/502fdbff15526876610042435')

This will retrieve the remote logistic regression information,
using an implicitly built
``BigML()`` connection object (see the `Authentication <#authentication>`_
section for more
details on how to set your credentials) and return a ``LogisticRegression``
object that will be stored in the ``./storage`` directory and
you can use to make local predictions. If you want to use a
specific connection object for the remote retrieval or a different storage
directory, you can set it as second
parameter:

.. code-block:: python

    from bigml.logistic import LogisticRegression
    from bigml.api import BigML

    local_log_regression = LogisticRegression(
        'logisticregression/502fdbff15526876610602435',
        api=BigML(my_username, my_api_key, storage="my_storage"))

You can also reuse a remote logistic regression JSON structure
as previously retrieved to build the
local logistic regression object:

.. code-block:: python

    from bigml.logistic import LogisticRegression
    from bigml.api import BigML
    api = BigML()
    logistic_regression = api.get_logistic_regression(
        'logisticregression/502fdbff15526876610002435',
        query_string='limit=-1')

    local_log_regression = LogisticRegression(logistic_regression)

Note that in this example we used a ``limit=-1`` query string for the
logistic regression retrieval. This ensures that all fields are
retrieved by the get method in the same call (unlike in the standard
calls where the number of fields returned is limited).

Local Linear Regression Predictions
-----------------------------------

Using the local ``LinearRegression`` class, you can predict the prediction for
an input data set:

.. code-block:: python

    local_linear_regression.predict({"petal length": 2, "sepal length": 1.5,
                                     "species": "Iris-setosa",
                                     "sepal width": 0.7},
                                     full=True)
    {'confidence_bounds': {
        'prediction_interval': 0.43783924497784293,
        'confidence_interval': 0.2561542783257394},
     'prediction': -0.6109005499999999, 'unused_fields': ['petal length']}


To obtain a linear regression prediction, input data can only have missing
values for fields that had already some missings in training data.

The ``full=True`` in the predict method will cause the prediction to include
``confidence bounds`` when available. Some logistic regressions will not
contain such information by construction. Also, in order to compute these
bounds locally, you will need ``numpy`` and ``scipy`` in place.
As they are quite heavy libraries, they aren't automatically installed as
dependencies of these bindings.

Local Deepnet
-------------

You can also instantiate a local version of a remote Deepnet.

.. code-block:: python

    from bigml.deepnet import Deepnet
    local_deepnet = Deepnet(
        'deepnet/502fdbff15526876610022435')

This will retrieve the remote deepnet information,
using an implicitly built
``BigML()`` connection object (see the `Authentication <#authentication>`_
section for more
details on how to set your credentials) and return a ``Deepnet``
object that will be stored in the ``./storage`` directory and
you can use to make local predictions. If you want to use a
specific connection object for the remote retrieval or a different storage
directory, you can set it as second
parameter:

.. code-block:: python

    from bigml.deepnet import Deepnet
    from bigml.api import BigML

    local_deepnet = Deepnet(
        'deepnet/502fdbff15526876610602435',
        api=BigML(my_username, my_api_key, storage="my_storage"))

You can also reuse a remote Deepnet JSON structure
as previously retrieved to build the
local Deepnet object:

.. code-block:: python

    from bigml.deepnet import Deepnet
    from bigml.api import BigML
    api = BigML()
    deepnet = api.get_deepnet(
        'deepnet/502fdbff15526876610002435',
        query_string='limit=-1')

    local_deepnet = Deepnet(deepnet)

Note that in this example we used a ``limit=-1`` query string for the
deepnet retrieval. This ensures that all fields are
retrieved by the get method in the same call (unlike in the standard
calls where the number of fields returned is limited).

Local Deepnet Predictions
-------------------------

Using the local deepnet object, you can predict the prediction for
an input data set:

.. code-block:: python

    local_deepnet.predict({"petal length": 2, "sepal length": 1.5,
                           "petal width": 0.5, "sepal width": 0.7},
                           full=True)
    {'distribution': [
        {'category': u'Iris-virginica', 'probability': 0.5041444478857267},
        {'category': u'Iris-versicolor', 'probability': 0.46926542042788333},
        {'category': u'Iris-setosa', 'probability': 0.02659013168639014}],
        'prediction': u'Iris-virginica', 'probability': 0.5041444478857267}

As you can see, the full prediction contains the predicted category and the
associated probability. It also shows the distribution of probabilities for
all the possible categories in the objective field. If you only need the
predicted value, you can remove the ``full`` argument.

To be consistent with the ``Model`` class interface, deepnets
have also a ``predict_probability`` method, which takes
the same argument as ``Model.predict``:
``compact``.

As with local Models, if ``compact`` is ``False`` (the default), the
output is a list of maps, each with the keys ``prediction`` and
``probability`` mapped to the class name and its associated
probability.

So, for example

.. code-block:: python

    local_deepnet.predict_probability({"petal length": 2, "sepal length": 1.5,
                                       "petal width": 0.5, "sepal width": 0.7})

    [{'category': u'Iris-setosa', 'probability': 0.02659013168639014},
     {'category': u'Iris-versicolor', 'probability': 0.46926542042788333},
     {'category': u'Iris-virginica', 'probability': 0.5041444478857267}]

If ``compact`` is ``True``, only the probabilities themselves are
returned, as a list in class name order, again, as is the case with
local Models.

Operating point predictions are also available for local deepnets and an
example of it would be:

.. code-block:: python

    operating_point = {"kind": "probability",
                       "positive_class": "True",
                       "threshold": 0.8};
    prediction = local_deepnet.predict(inputData,
                                       operating_point=operating_point)

**Note**: Local predictions for deepnets built on images datasets can differ
slightly from the predictions obtained by using BigML's API create prediction
call. When uploaded to BigML, images are standardized to a particular
resolution and compressed using the JPEG algorithm while local predictions
maintain the original image information. That can cause minor variations in
regression predictions or the probability associated to classification
predictions. If anything, the local value will always be slightly
more accurate.


Local Fusion
------------

You can also instantiate a local version of a remote Fusion.

.. code-block:: python

    from bigml.fusion import Fusion
    local_fusion = Fusion(
        'fusion/502fdbff15526876610022438')

This will retrieve the remote fusion information,
using an implicitly built
``BigML()`` connection object (see the `Authentication <#authentication>`_
section for more
details on how to set your credentials) and return a ``Fusion``
object that will be stored in the ``./storage`` directory and
you can use to make local predictions. If you want to use a
specific connection object for the remote retrieval or a different storage
directory, you can set it as second
parameter:

.. code-block:: python

    from bigml.fusion import Fusion
    from bigml.api import BigML

    local_fusion = Fusion(
        'fusion/502fdbff15526876610602435',
        api=BigML(my_username, my_api_key, storage="my_storage"))

You can also reuse a remote Fusion JSON structure
as previously retrieved to build the
local Fusion object:

.. code-block:: python

    from bigml.fusion import Fusion
    from bigml.api import BigML
    api = BigML()
    fusion = api.get_fusion(
        'fusion/502fdbff15526876610002435',
        query_string='limit=-1')

    local_fusion = Fusion(fusion)

Note that in this example we used a ``limit=-1`` query string for the
fusion retrieval. This ensures that all fields are
retrieved by the get method in the same call (unlike in the standard
calls where the number of fields returned is limited).

Local Fusion Predictions
-------------------------

Using the local fusion object, you can predict the prediction for
an input data set:

.. code-block:: python

    local_fusion.predict({"petal length": 2, "sepal length": 1.5,
                          "petal width": 0.5, "sepal width": 0.7},
                          full=True)
    {'prediction': u'Iris-setosa', 'probability': 0.45224}


As you can see, the full prediction contains the predicted category and the
associated probability. If you only need the
predicted value, you can remove the ``full`` argument.

To be consistent with the ``Model`` class interface, fusions
have also a ``predict_probability`` method, which takes
the same argument as ``Model.predict``:
``compact``.

As with local Models, if ``compact`` is ``False`` (the default), the
output is a list of maps, each with the keys ``prediction`` and
``probability`` mapped to the class name and its associated
probability.

So, for example

.. code-block:: python

    local_fusion.predict_probability({"petal length": 2, "sepal length": 1.5,
                                      "petal width": 0.5, "sepal width": 0.7})

    [{'category': u'Iris-setosa', 'probability': 0.45224},
     {'category': u'Iris-versicolor', 'probability': 0.2854},
     {'category': u'Iris-virginica', 'probability': 0.26236}]


If ``compact`` is ``True``, only the probabilities themselves are
returned, as a list in class name order, again, as is the case with
local Models.

Operating point predictions are also available with probability as threshold
for local fusions and an
example of it would be:

.. code-block:: python

    operating_point = {"kind": "probability",
                       "positive_class": "True",
                       "threshold": 0.8};
    prediction = local_fusion.predict(inputData,
                                      operating_point=operating_point)

Local Association
-----------------

You can also instantiate a local version of a remote association resource.

.. code-block:: python

    from bigml.association import Association
    local_association = Association('association/502fdcff15526876610002435')

This will retrieve the remote association information, using an implicitly
built
``BigML()`` connection object (see the `Authentication <#authentication>`_
section for more
details on how to set your credentials) and return an ``Association`` object
that will be stored in the ``./storage`` directory and
you can use to extract the rules found in the original dataset.
If you want to use a
specific connection object for the remote retrieval or a different storage
directory, you can set it as second
parameter:

.. code-block:: python

    from bigml.association import Association
    from bigml.api import BigML

    local_association = Association('association/502fdcff15526876610002435',
                                    api=BigML(my_username,
                                              my_api_key
                                              storage="my_storage"))

or even use the remote association information retrieved previously
to build the
local association object:

.. code-block:: python

    from bigml.association import Association
    from bigml.api import BigML
    api = BigML()
    association = api.get_association('association/502fdcff15526876610002435',
                                      query_string='limit=-1')

    local_association = Association(association)

Note that in this example we used a ``limit=-1`` query string for the
association retrieval. This ensures that all fields are retrieved by the get
method in the
same call (unlike in the standard calls where the number of fields returned is
limited).

The created ``Association`` object has some methods to help retrieving the
association rules found in the original data. The ``get_rules`` method will
return the association rules. Arguments can be set to filter the rules
returned according to its ``leverage``, ``strength``, ``support``, ``p_value``,
a list of items involved in the rule or a user-given filter function.

.. code-block:: python

    from bigml.association import Association
    local_association = Association('association/502fdcff15526876610002435')
    local_association.get_rules(item_list=["Edible"], min_p_value=0.3)

In this example, the only rules that will be returned by the ``get_rules``
method will be the ones that mention ``Edible`` and their ``p_value``
is greater or equal to ``0.3``.

The rules can also be stored in a CSV file using ``rules_CSV``:


.. code-block:: python

    from bigml.association import Association
    local_association = Association('association/502fdcff15526876610002435')
    local_association.rules_CSV(file_name='/tmp/my_rules.csv',
                                min_strength=0.1)

This example will store the rules whose strength is bigger or equal to 0.1 in
the ``/tmp/my_rules.csv`` file.

You can also obtain the list of ``items`` parsed in the dataset using the
``get_items`` method. You can also filter the results by field name, by
item names and by a user-given function:

.. code-block:: python

    from bigml.association import Association
    local_association = Association('association/502fdcff15526876610002435')
    local_association.get_items(field="Cap Color",
                                names=["Brown cap", "White cap", "Yellow cap"])

This will recover the ``Item`` objects found in the ``Cap Color`` field for
the names in the list, with their properties as described in the
`developers section <https://bigml.com/api/associations#ad_retrieving_an_association>`_


Local Association Sets
----------------------

Using the local association object, you can predict the association sets
related to an input data set:

.. code-block:: python

    local_association.association_set( \
        {"gender": "Female", "genres": "Adventure$Action", \
         "timestamp": 993906291, "occupation": "K-12 student",
         "zipcode": 59583, "rating": 3})
    [{'item': {'complement': False,
               'count': 70,
               'field_id': u'000002',
               'name': u'Under 18'},
      'rules': ['000000'],
      'score': 0.0969181441561211},
     {'item': {'complement': False,
               'count': 216,
               'field_id': u'000007',
               'name': u'Drama'},
      'score': 0.025050115102862636},
     {'item': {'complement': False,
               'count': 108,
               'field_id': u'000007',
               'name': u'Sci-Fi'},
      'rules': ['000003'],
      'score': 0.02384578264599424},
     {'item': {'complement': False,
               'count': 40,
               'field_id': u'000002',
               'name': u'56+'},
      'rules': ['000008',
                '000020'],
      'score': 0.021845366022721312},
     {'item': {'complement': False,
               'count': 66,
               'field_id': u'000002',
               'name': u'45-49'},
      'rules': ['00000e'],
      'score': 0.019657155185835006}]

As in the local model predictions, producing local association sets can be done
independently of BigML servers, so no cost or connection latencies are
involved.

Local Topic Model
-----------------

You can also instantiate a local version of a remote topic model.

.. code-block:: python

    from bigml.topicmodel import TopicModel
    local_topic_model = TopicModel(
        'topicmodel/502fdbcf15526876210042435')

This will retrieve the remote topic model information,
using an implicitly built
``BigML()`` connection object (see the `Authentication <#authentication>`_
section for more
details on how to set your credentials) and return a ``TopicModel``
object that will be stored in the ``./storage`` directory and
you can use to obtain local topic distributions.
If you want to use a
specific connection object for the remote retrieval or a different storage
directory, you can set it as second
parameter:

.. code-block:: python

    from bigml.topicmodel import TopicModel
    from bigml.api import BigML

    local_topic_model = TopicModel(
        'topicmodel/502fdbcf15526876210042435',
        api=BigML(my_username, my_api_key, storage="my_storage"))

You can also reuse a remote topic model JSON structure
as previously retrieved to build the
local topic model object:

.. code-block:: python

    from bigml.topicmodel import TopicModel
    from bigml.api import BigML
    api = BigML()
    topic_model = api.get_topic_model(
        'topicmodel/502fdbcf15526876210042435',
        query_string='limit=-1')

    local_topic_model = TopicModel(topic_model)

Note that in this example we used a ``limit=-1`` query string for the topic
model retrieval. This ensures that all fields are retrieved by the get
method in the
same call (unlike in the standard calls where the number of fields returned is
limited).

Local Topic Distributions
-------------------------

Using the local topic model object, you can predict the local topic
distribution for
an input data set:

.. code-block:: python

    local_topic_model.distribution({"Message": "Our mobile phone is free"})
    [   {   'name': u'Topic 00', 'probability': 0.002627154266498529},
        {   'name': u'Topic 01', 'probability': 0.003257671290458176},
        {   'name': u'Topic 02', 'probability': 0.002627154266498529},
        {   'name': u'Topic 03', 'probability': 0.1968263976460698},
        {   'name': u'Topic 04', 'probability': 0.002627154266498529},
        {   'name': u'Topic 05', 'probability': 0.002627154266498529},
        {   'name': u'Topic 06', 'probability': 0.13692728036990331},
        {   'name': u'Topic 07', 'probability': 0.6419714165615805},
        {   'name': u'Topic 08', 'probability': 0.002627154266498529},
        {   'name': u'Topic 09', 'probability': 0.002627154266498529},
        {   'name': u'Topic 10', 'probability': 0.002627154266498529},
        {   'name': u'Topic 11', 'probability': 0.002627154266498529}]


As you can see, the topic distribution contains the name of the
possible topics in the model and the
associated probabilities.

Local Time Series
-----------------

You can also instantiate a local version of a remote time series.

.. code-block:: python

    from bigml.timeseries import TimeSeries
    local_time_series = TimeSeries(
        'timeseries/502fdbcf15526876210042435')

This will create a series of models from
the remote time series information,
using an implicitly built
``BigML()`` connection object (see the `Authentication <#authentication>`_
section for more
details on how to set your credentials) and return a ``TimeSeries``
object that will be stored in the ``./storage`` directory and
you can use to obtain local forecasts.
If you want to use a
specific connection object for the remote retrieval or a different storage
directory, you can set it as second
parameter:

.. code-block:: python

    from bigml.timeseries import TimeSeries
    from bigml.api import BigML

    local_time_series = TimeSeries( \
        'timeseries/502fdbcf15526876210042435',
        api=BigML(my_username, my_api_key, storage="my_storage"))

You can also reuse a remote time series JSON structure
as previously retrieved to build the
local time series object:

.. code-block:: python

    from bigml.timeseries import TimeSeries
    from bigml.api import BigML
    api = BigML()
    time_series = api.get_time_series( \
        'timeseries/502fdbcf15526876210042435',
        query_string='limit=-1')

    local_time_series = TimeSeries(time_series)

Note that in this example we used a ``limit=-1`` query string for the time
series retrieval. This ensures that all fields are retrieved by the get
method in the
same call (unlike in the standard calls where the number of fields returned is
limited).


Local Forecasts
---------------

Using the local time series object, you can forecast any of the objective
field values:

.. code-block:: python

    local_time_series.forecast({"Final": {"horizon": 5}, "Assignment": { \
        "horizon": 10, "ets_models": {"criterion": "aic", "limit": 2}}})
    {u'000005': [
        {'point_forecast': [68.53181, 68.53181, 68.53181, 68.53181, 68.53181],
         'model': u'A,N,N'}],
     u'000001': [{'point_forecast': [54.776650000000004, 90.00943000000001,
                                     83.59285000000001, 85.72403000000001,
                                     72.87196, 93.85872, 84.80786, 84.65522,
                                     92.52545, 88.78403],
                  'model': u'A,N,A'},
                 {'point_forecast': [55.882820120000005, 90.5255466567616,
                                     83.44908577909621, 87.64524353046498,
                                     74.32914583152592, 95.12372848262932,
                                     86.69298716626228, 85.31630744944385,
                                     93.62385478607113, 89.06905451921818],
                  'model': u'A,Ad,A'}]}


As you can see, the forecast contains the ID of the forecasted field, the
computed points and the name of the models meeting the criterion.
For more details about the available parameters, please check the `API
documentation <https://bigml.com/api/forecasts>`_.


Local PCAs
----------

The `PCA` class will create a local version of a remote PCA.

.. code-block:: python

    from bigml.pca import PCA
    local_pca = PCA(
        'pca/502fdbcf15526876210042435')


This will create an object that stores the remote information that defines
the PCA, needed to generate
projections to the new dimensionally reduced components. The remote resource
is automatically downloaded the first time the the PCA is instantiated by
using an implicitly built
``BigML()`` connection object (see the
`Authentication <#authentication>`_ section for more
details on how to set your credentials). The JSON that contains this
information is stored in a ``./storage`` directory, which is the default
choice. If you want to use a
specific connection object to define the credentials for the authentication
in BigML or the directory where the JSON information is stored,
you can set it as the second parameter:

.. code-block:: python

    from bigml.pca import PCA
    from bigml.api import BigML

    local_pca = PCA( \
        'timeseries/502fdbcf15526876210042435',
        api=BigML(my_username, my_api_key, storage="my_storage"))

You can also reuse a remote PCA JSON structure
as previously retrieved to build the
local PCA object:

.. code-block:: python

    from bigml.pca import PCA
    from bigml.api import BigML
    api = BigML()
    time_series = api.get_pca( \
        'pca/502fdbcf15526876210042435',
        query_string='limit=-1')

    local_pca = PCA(pca)

Note that in this example we used a ``limit=-1`` query string for the PCA
retrieval. This ensures that all fields are retrieved by the get
method in the
same call (unlike in the standard calls where the number of fields returned is
limited).


Local Projections
-----------------

Using the local PCA object, you can compute the projection of
an input dataset into the new components:

.. code-block:: python

    local_pca.projection({"species": "Iris-versicolor"})
    [6.03852, 8.35456, 5.04432, 0.75338, 0.06787, 0.03018]

You can use the ``max_components`` and ``variance_threshold`` arguments
to limit the number of components generated. You can also use the ``full``
argument to produce a dictionary whose keys are the names of the generated
components.

.. code-block:: python

    local_pca.projection({"species": "Iris-versicolor"}, full=yes)
    {'PCA1': 6.03852, 'PCA2': 8.35456, 'PCA3': 5.04432, 'PCA4': 0.75338,
     'PCA5': 0.06787, 'PCA6': 0.03018}

As in the local model predictions, producing local projections can be done
independently of BigML servers, so no cost or connection latencies are
involved.


Local Forecasts
---------------

Using the local time series object, you can forecast any of the objective
field values:

.. code-block:: python

    local_time_series.forecast({"Final": {"horizon": 5}, "Assignment": { \
        "horizon": 10, "ets_models": {"criterion": "aic", "limit": 2}}})
    {u'000005': [
        {'point_forecast': [68.53181, 68.53181, 68.53181, 68.53181, 68.53181],
         'model': u'A,N,N'}],
     u'000001': [{'point_forecast': [54.776650000000004, 90.00943000000001,
                                     83.59285000000001, 85.72403000000001,
                                     72.87196, 93.85872, 84.80786, 84.65522,
                                     92.52545, 88.78403],
                  'model': u'A,N,A'},
                 {'point_forecast': [55.882820120000005, 90.5255466567616,
                                     83.44908577909621, 87.64524353046498,
                                     74.32914583152592, 95.12372848262932,
                                     86.69298716626228, 85.31630744944385,
                                     93.62385478607113, 89.06905451921818],
                  'model': u'A,Ad,A'}]}


As you can see, the forecast contains the ID of the forecasted field, the
computed points and the name of the models meeting the criterion.
For more details about the available parameters, please check the `API
documentation <https://bigml.com/api/forecasts>`_.


Multi Models
------------

Multi Models use a numbers of BigML remote models to build a local version
that can be used to generate predictions locally. Predictions are generated
combining the outputs of each model.

.. code-block:: python

    from bigml.api import BigML
    from bigml.multimodel import MultiModel

    api = BigML()

    model = MultiModel([api.get_model(model['resource']) for model in
                       api.list_models(query_string="tags__in=my_tag")
                       ['objects']])

    model.predict({"petal length": 3, "petal width": 1})

This will create a multi model using all the models that have been previously
tagged with ``my_tag`` and predict by combining each model's prediction.
The combination method used by default is ``plurality`` for categorical
predictions and mean value for numerical ones. You can also use ``confidence
weighted``:

.. code-block:: python

    model.predict({"petal length": 3, "petal width": 1}, method=1)

that will weight each vote using the confidence/error given by the model
to each prediction, or even ``probability weighted``:

.. code-block:: python

    model.predict({"petal length": 3, "petal width": 1}, method=2)

that weights each vote by using the probability associated to the training
distribution at the prediction node.

There's also a ``threshold`` method that uses an additional set of options:
threshold and category. The category is predicted if and only if
the number of predictions for that category is at least the threshold value.
Otherwise, the prediction is plurality for the rest of predicted values.

An example of ``threshold`` combination method would be:

.. code-block:: python

    model.predict({'petal length': 0.9, 'petal width': 3.0}, method=3,
                  options={'threshold': 3, 'category': 'Iris-virginica'})


When making predictions on a test set with a large number of models,
``batch_predict`` can be useful to log each model's predictions in a
separated file. It expects a list of input data values and the directory path
to save the prediction files in.

.. code-block:: python

    model.batch_predict([{"petal length": 3, "petal width": 1},
                         {"petal length": 1, "petal width": 5.1}],
                        "data/predictions")

The predictions generated for each model will be stored in an output
file in `data/predictions` using the syntax
`model_[id of the model]__predictions.csv`. For instance, when using
`model/50c0de043b563519830001c2` to predict, the output file name will be
`model_50c0de043b563519830001c2__predictions.csv`. An additional feature is
that using ``reuse=True`` as argument will force the function to skip the
creation of the file if it already exists. This can be
helpful when using repeatedly a bunch of models on the same test set.

.. code-block:: python

    model.batch_predict([{"petal length": 3, "petal width": 1},
                         {"petal length": 1, "petal width": 5.1}],
                        "data/predictions", reuse=True)

Prediction files can be subsequently retrieved and converted into a votes list
using ``batch_votes``:

.. code-block:: python

    model.batch_votes("data/predictions")

which will return a list of MultiVote objects. Each MultiVote contains a list
of predictions (e.g. ``[{'prediction': u'Iris-versicolor', 'confidence': 0.34,
'order': 0}, {'prediction': u'Iris-setosa', 'confidence': 0.25,
'order': 1}]``).
These votes can be further combined to issue a final
prediction for each input data element using the method ``combine``

.. code-block:: python

    for multivote in model.batch_votes("data/predictions"):
        prediction = multivote.combine()

Again, the default method of combination is ``plurality`` for categorical
predictions and mean value for numerical ones. You can also use ``confidence
weighted``:

.. code-block:: python

    prediction = multivote.combine(1)

or ``probability weighted``:

.. code-block:: python

    prediction = multivote.combine(2)

You can also get a confidence measure for the combined prediction:

.. code-block:: python

    prediction = multivolte.combine(0, with_confidence=True)

For classification, the confidence associated to the combined prediction
is derived by first selecting the model's predictions that voted for the
resulting prediction and computing the weighted average of their individual
confidence. Nevertheless, when ``probability weighted`` is used,
the confidence is obtained by using each model's distribution at the
prediction node to build a probability distribution and combining them.
The confidence is then computed as the wilson score interval of the
combined distribution (using as total number of instances the sum of all
the model's distributions original instances at the prediction node)

In regression, all the models predictions' confidences contribute
to the weighted average confidence.


Local Ensembles
---------------

Remote ensembles can also be used locally through the ``Ensemble``
class. The simplest way to access an existing ensemble and using it to
predict locally is:

.. code-block:: python

    from bigml.ensemble import Ensemble
    ensemble = Ensemble('ensemble/5143a51a37203f2cf7020351')
    ensemble.predict({"petal length": 3, "petal width": 1})

This is the simpler method to create a local Ensemble. The
``Ensemble('ensemble/5143a51a37203f2cf7020351')`` constructor, that fetches
all the related JSON files and stores them in an ``./storage`` directory. Next
calls to ``Ensemble('ensemble/50c0de043b5635198300033c')`` will retrieve the
files from this local storage, so that internet connection will only be needed
the first time an ``Ensemble`` is built.

However, that method can only be used to work with the ensembles in our
account in BigML. If we intend to use ensembles created under an
``Organization``, then
we need to provide the information about the ``project`` that the ensemble
is included in. You need to provide a connection object for that:

.. code-block:: python

    from bigml.ensemble import Ensemble
    from bigml.api import BigML

    # connection object that informs about the project ID and the
    # directory where the ensemble will be stored for local use

    api = BigML(project="project/5143a51a37203f2cf7020001",
                storage="my_storage_directory")

    ensemble = Ensemble('ensemble/5143a51a37203f2cf7020351', api=api)
    ensemble.predict({"petal length": 3, "petal width": 1})

The local ensemble object can be used to manage the
three types of ensembles: ``Decision Forests`` (bagging or random) and
the ones using ``Boosted Trees``. Also, you can choose
the storage directory or even avoid storing at all. The ``àpi`` connection
object controls the storage strategy through the ``storage`` argument.

.. code-block:: python

    from bigml.api import BigML
    from bigml.ensemble import Ensemble

    # api connection using a user-selected storage
    api = BigML(storage='./my_storage')

    # creating ensemble
    ensemble = api.create_ensemble('dataset/5143a51a37203f2cf7000972')

    # Ensemble object to predict
    ensemble = Ensemble(ensemble, api)
    ensemble.predict({"petal length": 3, "petal width": 1},
                     operating_kind="votes")

In this example, we create
a new ensemble and store its information in the ``./my_storage``
folder. Then this information is used to predict locally using the number of
votes (one per model) backing each category.

The ``operating_kind`` argument overrides the legacy ``method`` argument, which
was previously used to define the combiner for the models predictions.

Similarly, local ensembles can also be created by giving a list of models to be
combined to issue the final prediction (note: only random decision forests and
bagging ensembles can be built using this method):

.. code-block:: python

    from bigml.ensemble import Ensemble
    ensemble = Ensemble(['model/50c0de043b563519830001c2', \
                         'model/50c0de043b5635198300031b')]
    ensemble.predict({"petal length": 3, "petal width": 1})

or even a JSON file that contains the ensemble resource:

.. code-block:: python

    from bigml.api import BigML
    api = BigML()
    api.export("ensemble/50c0de043b5635198300033c",
               "my_directory/my_ensemble.json")

    from bigml.ensemble import Ensemble
    local_ensemble = Ensemble("./my_directory/my_ensemble.json")

Note: the ensemble JSON structure is not self-contained, meaning that it
contains references to the models that the ensemble is build of, but not the
information of the models themselves.
To use an ensemble locally with no connection to
the internet, you must make sure that not only a local copy of the ensemble
JSON file is available in your computer, but also the JSON files corresponding
to the models in it. The ``export`` method takes care of storing the
information of every model in the ensemble and storing it in the same directory
as the ensemble JSON file. The ``Ensemble`` class will also look up for the
model files in the same directory when using a path to an ensemble file as
argument.

If you have no memory limitations you can create the ensemble
from a list of local model
objects. Then, local model objects will be always in memory and
will only be instantiated once. This will increase
performance for large ensembles:

.. code-block:: python

    from bigml.model import Model
    model_ids = ['model/50c0de043b563519830001c2', \
                 'model/50c0de043b5635198300031b']
    local_models = [Model(model_id) for model_id in model_ids]
    local_ensemble = Ensemble(local_models)

Local Ensemble caching
----------------------

Ensembles can become quite large objects and demand large memory resources.
If your usual scenario is using many of them
constantly in a disordered way, the best strategy is setting up a cache
system to store them. The local ensemble class provides helpers to
interact with that cache. Here's an example using ``Redis``.

.. code-block:: python

    from ensemble import Ensemble
    import redis
    r = redis.Redis()
    # First build as you would any core Ensemble object:
    local_ensemble = Ensemble('ensemble/5126965515526876630001b2')
    # Store a serialized version in Redis
    ensemble.dump(cache_set=r.set)
    # (retrieve the external rep from its convenient place)
    # Speedy Build from external rep
    local_ensemble = Ensemble('ensemble/5126965515526876630001b2', \
        cache_get=r.get)
    # Get scores same as always:
    local_ensemble.predict({"src_bytes": 350})


Local Ensemble's Predictions
----------------------------

As in the local model's case, you can use the local ensemble to create
new predictions for your test data, and set some arguments to configure
the final output of the ``predict`` method.

The predictions' structure will vary depending on the kind of
ensemble used. For ``Decision Forests`` local predictions will just contain
the ensemble's final prediction if no other argument is used.

.. code-block:: python

    from bigml.ensemble import Ensemble
    ensemble = Ensemble('ensemble/5143a51a37203f2cf7020351')
    ensemble.predict({"petal length": 3, "petal width": 1})
    u'Iris-versicolor'

The final prediction of an ensemble is determined
by aggregating or selecting the predictions of the individual models therein.
For classifications, the most probable class is returned if no especial
operating method is set. Using ``full=True`` you can see both the predicted
output and the associated probability:

.. code-block:: python

    from bigml.ensemble import Ensemble
    ensemble = Ensemble('ensemble/5143a51a37203f2cf7020351')
    ensemble.predict({"petal length": 3, "petal width": 1}, \
                     full=True)

    {'prediction': u'Iris-versicolor',
     'probability': 0.98566}

In general, the prediction in a classification
will be one amongst the list of categories in the objective
field. When each model in the ensemble
is used to predict, each category has a confidence, a
probability or a vote associated to this prediction.
Then, through the collection
of models in the
ensemble, each category gets an averaged confidence, probabiity and number of
votes. Thus you can decide whether to operate the ensemble using the
``confidence``, the ``probability`` or the ``votes`` so that the predicted
category is the one that scores higher in any of these quantities. The
criteria can be set using the `operating_kind` option (default is set to
``probability``):

.. code-block:: python

    ensemble.predict({"petal length": 3, "petal width": 1}, \
                     operating_kind="votes")

Regression will generate a predictiona and an associated error, however
``Boosted Trees`` don't have an associated confidence measure, so
only the prediction will be obtained in this case.

For consistency of interface with the ``Model`` class, as well as
between boosted and non-boosted ensembles, local Ensembles again have
a ``predict_probability`` method.  This takes the same optional
arguments as ``Model.predict``: ``missing_strategy`` and
``compact``. As with local Models, if ``compact`` is ``False`` (the default),
the output is a list of maps, each with the keys ``prediction`` and
``probability`` mapped to the class name and its associated
probability.

So, for example:

.. code-block:: python

    ensemble.predict_probability({"petal length": 3, "petal width": 1})

    [{'category': u'Iris-setosa', 'probability': 0.006733220044732548},
     {'category': u'Iris-versicolor', 'probability': 0.9824478534614787},
     {'category': u'Iris-virginica', 'probability': 0.0108189264937886}]

If ``compact`` is ``True``, only the probabilities themselves are
returned, as a list in class name order, again, as is the case with
local Models.

Operating point predictions are also available for local ensembles and an
example of it would be:

.. code-block:: python

    operating_point = {"kind": "probability",
                       "positive_class": "True",
                       "threshold": 0.8};
    prediction = local_ensemble.predict(inputData,
                                        operating_point=operating_point)

You can check the
`Operating point's predictions <#operating-point's-predictions>`_ section
to learn about
operating points. For ensembles, three kinds of operating points are available:
``votes``, ``probability`` and ``confidence``. ``Votes`` will use as threshold
the number of models in the ensemble that vote for the positive class.
The other two are already explained in the above mentioned section.

Local Ensemble Predictor
------------------------

Predictions can take longer when the ensemble is formed by a large number of
models or when its models have a high number of nodes. In these cases,
predictions' speed can be increased and memory usage minimized by using the
``EnsemblePredictor`` object. The basic example to build it is:

.. code-block:: python

    from bigml.ensemblepredictor import EnsemblePredictor
    ensemble = EnsemblePredictor('ensemble/5143a51a37203f2cf7020351',
                                 "./model_fns_directory")
    ensemble.predict({"petal length": 3, "petal width": 1}, full=True)
    {'prediction': u'Iris-versicolor', 'confidence': 0.91519}

This constructor has two compulsory attributes: then ensemble ID (or the
corresponding API response) and the path to a directory that contains a file
per each of the ensemble models. Each file stores the ``predict`` function
needed to obtain the model's predictions. As in the ``Ensemble`` object, you
can also add an ``api`` argument with the connection to be used to download
the ensemble's JSON information.

The functions stored in this directory are generated automatically the first
time you instantiate the ensemble. Once they are generated, the functions are
retrieved from the directory.

Note that only last prediction missings strategy is available for these
predictions and the combiners available are ``plurality``, ``confidence`` and
``distribution`` but no ``operating_kind`` or ``operating_point`` options
are provided at present.

Local Supervised Model
----------------------

There's a general class that will allow you to predict using any supervised
model resource, regardless of its particular type (model, ensemble,
logistic regression, linear regression or deepnet).

The ``SupervisedModel`` object will retrieve the resource information and
instantiate the corresponding local object, so that you can use its
``predict`` method to produce local predictions:

.. code-block:: python

    from bigml.supervised import SupervisedModel
    local_supervised_1 = SupervisedModel( \
        "logisticregression/5143a51a37203f2cf7020351")
    local_supervised_2 = SupervisedModel( \
        "model/5143a51a37203f2cf7020351")
    input_data = {"petal length": 3, "petal width": 1}
    logistic_regression_prediction = local_supervised_1.predict(input_data)
    model_prediction = local_supervised_2.predict(input_data)

Local predictions with shared models
------------------------------------

BigML's resources are private to the owner of the account where they were
created. However, owners can decide to share their resources with other
BigML users by creating
`Secret links <https://support.bigml.com/hc/en-us/articles/206616179-Can-I-share-my-model-with-other-users->`_
to them. The users that receive the link, will be able to inspect the
resource and can also download them. This is specially important in the case
of models, as they will be able to generate local predictions from them.

The ``Secret link`` URLs leading to shared resources end in a shared ID
(starting with the string ``shared/`` followed by the type of resource and
the particular sharing key). In order to use them locally, use this
string as first argument for the local model constructor. For instance, let's
say that someone shares with you the link to a shared ensemble
``https://bigml.com/shared/ensemble/qbXem5XoEiVKcq8MPmwjHnXunFj``.

You could use that in local predictions by instantiating the corresponding
``Ensemble`` object.

.. code-block:: python

    from bigml.ensemble import Ensemble
    local_ensemble = Ensemble("shared/ensemble/qbXem5XoEiVKcq8MPmwjHnXunFj")

And the new ``local_ensemble`` would be ready to predict using the ``.predict``
method, as discussed in the `Local Ensembles <#Local-Ensembles>`_ section.


Local caching
-------------

All local models can use an external cache system to manage memory storage and
recovery. The ``get`` and ``set`` functions of the cache manager should be
passed to the constructor or  ``dump`` function. Here's an example on how to
cache a linear regression:

.. code-block:: python

    from bigml.linear import LinearRegression
    lm = LinearRegression("linearregression/5e827ff85299630d22007198")
    lm.predict({"petal length": 4, "sepal length":4, "petal width": 4, \
        "sepal width": 4, "species": "Iris-setosa"}, full=True)
    import redis
    r = redis.Redis()
    # First build as you would any core LinearRegression object:
    # Store a serialized version in Redis
    lm.dump(cache_set=r.set)
    # (retrieve the external rep from its convenient place)
    # Speedy Build from external rep
    lm = LinearRegression("linearregression/5e827ff85299630d22007198", \
        cache_get=r.get)
    # Get predictions same as always:
    lm.predict({"petal length": 4, "sepal length":4, "petal width": 4, \
        "sepal width": 4, "species": "Iris-setosa"}, full=True)


Rule Generation
---------------

You can also use a local model to generate a IF-THEN rule set that can be very
helpful to understand how the model works internally.

.. code-block:: python

     local_model.rules()
     IF petal_length > 2.45 AND
         IF petal_width > 1.65 AND
             IF petal_length > 5.05 THEN
                 species = Iris-virginica
             IF petal_length <= 5.05 AND
                 IF sepal_width > 2.9 AND
                     IF sepal_length > 5.95 AND
                         IF petal_length > 4.95 THEN
                             species = Iris-versicolor
                         IF petal_length <= 4.95 THEN
                             species = Iris-virginica
                     IF sepal_length <= 5.95 THEN
                         species = Iris-versicolor
                 IF sepal_width <= 2.9 THEN
                     species = Iris-virginica
         IF petal_width <= 1.65 AND
             IF petal_length > 4.95 AND
                 IF sepal_length > 6.05 THEN
                     species = Iris-virginica
                 IF sepal_length <= 6.05 AND
                     IF sepal_width > 2.45 THEN
                         species = Iris-versicolor
                     IF sepal_width <= 2.45 THEN
                         species = Iris-virginica
             IF petal_length <= 4.95 THEN
                 species = Iris-versicolor
     IF petal_length <= 2.45 THEN
         species = Iris-setosa


Python, Tableau and Hadoop-ready Generation
-------------------------------------------

If you prefer, you can also generate a Python function that implements the model
and that can be useful to make the model actionable right away with ``local_model.python()``.

.. code-block:: python

    local_model.python()
    def predict_species(sepal_length=None,
                        sepal_width=None,
                        petal_length=None,
                        petal_width=None):
        """ Predictor for species from model/50a8e2d9eabcb404d2000293

            Predictive model by BigML - Machine Learning Made Easy
        """
        if (petal_length is None):
            return 'Iris-virginica'
        if (petal_length <= 2.45):
            return 'Iris-setosa'
        if (petal_length > 2.45):
            if (petal_width is None):
                return 'Iris-virginica'
            if (petal_width <= 1.65):
                if (petal_length <= 4.95):
                    return 'Iris-versicolor'
                if (petal_length > 4.95):
                    if (sepal_length is None):
                        return 'Iris-virginica'
                    if (sepal_length <= 6.05):
                        if (petal_width <= 1.55):
                            return 'Iris-virginica'
                        if (petal_width > 1.55):
                            return 'Iris-versicolor'
                    if (sepal_length > 6.05):
                        return 'Iris-virginica'
            if (petal_width > 1.65):
                if (petal_length <= 5.05):
                    if (sepal_width is None):
                        return 'Iris-virginica'
                    if (sepal_width <= 2.9):
                        return 'Iris-virginica'
                    if (sepal_width > 2.9):
                        if (sepal_length is None):
                            return 'Iris-virginica'
                        if (sepal_length <= 6.4):
                            if (sepal_length <= 5.95):
                                return 'Iris-versicolor'
                            if (sepal_length > 5.95):
                                return 'Iris-virginica'
                        if (sepal_length > 6.4):
                            return 'Iris-versicolor'
                if (petal_length > 5.05):
                    return 'Iris-virginica'

The ``local.python(hadoop=True)`` call will generate the code that you need
for the Hadoop map-reduce engine to produce batch predictions using `Hadoop
streaming <http://hadoop.apache.org/docs/r0.15.2/streaming.html>`_ .
Saving the mapper and reducer generated functions in their corresponding files
(let's say ``/home/hduser/hadoop_mapper.py`` and
``/home/hduser/hadoop_reducer.py``) you can start a Hadoop job
to generate predictions by issuing
the following Hadoop command in your system console:

.. code-block:: bash

    bin/hadoop jar contrib/streaming/hadoop-*streaming*.jar \
    -file /home/hduser/hadoop_mapper.py -mapper hadoop_mapper.py \
    -file /home/hduser/hadoop_reducer.py -reducer hadoop_reducer.py \
    -input /home/hduser/hadoop/input.csv \
    -output /home/hduser/hadoop/output_dir

assuming you are in the Hadoop home directory, your input file is in the
corresponding dfs directory
(``/home/hduser/hadoop/input.csv`` in this example) and the output will
be placed at ``/home/hduser/hadoop/output_dir`` (inside the dfs directory).

Tableau-ready rules are also available through ``local_model.tableau()`` for
all the models except those that use text predictors.

.. code-block:: python

    local_model.tableau()
    IF ISNULL([petal width]) THEN 'Iris-virginica'
    ELSEIF [petal width]>0.8 AND [petal width]>1.75 AND ISNULL([petal length]) THEN 'Iris-virginica'
    ELSEIF [petal width]>0.8 AND [petal width]>1.75 AND [petal length]>4.85 THEN 'Iris-virginica'
    ELSEIF [petal width]>0.8 AND [petal width]>1.75 AND [petal length]<=4.85 AND ISNULL([sepal width]) THEN 'Iris-virginica'
    ELSEIF [petal width]>0.8 AND [petal width]>1.75 AND [petal length]<=4.85 AND [sepal width]>3.1 THEN 'Iris-versicolor'
    ELSEIF [petal width]>0.8 AND [petal width]>1.75 AND [petal length]<=4.85 AND [sepal width]<=3.1 THEN 'Iris-virginica'
    ELSEIF [petal width]>0.8 AND [petal width]<=1.75 AND ISNULL([petal length]) THEN 'Iris-versicolor'
    ELSEIF [petal width]>0.8 AND [petal width]<=1.75 AND [petal length]>4.95 AND [petal width]>1.55 AND [petal length]>5.45 THEN 'Iris-virginica'
    ELSEIF [petal width]>0.8 AND [petal width]<=1.75 AND [petal length]>4.95 AND [petal width]>1.55 AND [petal length]<=5.45 THEN 'Iris-versicolor'
    ELSEIF [petal width]>0.8 AND [petal width]<=1.75 AND [petal length]>4.95 AND [petal width]<=1.55 THEN 'Iris-virginica'
    ELSEIF [petal width]>0.8 AND [petal width]<=1.75 AND [petal length]<=4.95 AND [petal width]>1.65 THEN 'Iris-virginica'
    ELSEIF [petal width]>0.8 AND [petal width]<=1.75 AND [petal length]<=4.95 AND [petal width]<=1.65 THEN 'Iris-versicolor'
    ELSEIF [petal width]<=0.8 THEN 'Iris-setosa'
    END


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


    Field importance:
        1. petal length: 53.16%
        2. petal width: 46.33%
        3. sepal length: 0.51%
        4. sepal width: 0.00%


    Iris-setosa : (data 33.33% / prediction 33.33%) petal length <= 2.45
        · 100.00%: petal length <= 2.45 [Confidence: 92.86%]


    Iris-versicolor : (data 33.33% / prediction 33.33%) petal length > 2.45
        · 94.00%: petal length > 2.45 and petal width <= 1.65 and petal length <= 4.95 [Confidence: 92.44%]
        · 2.00%: petal length > 2.45 and petal width <= 1.65 and petal length > 4.95 and sepal length <= 6.05 and petal width > 1.55 [Confidence: 20.65%]
        · 2.00%: petal length > 2.45 and petal width > 1.65 and petal length <= 5.05 and sepal width > 2.9 and sepal length > 6.4 [Confidence: 20.65%]
        · 2.00%: petal length > 2.45 and petal width > 1.65 and petal length <= 5.05 and sepal width > 2.9 and sepal length <= 6.4 and sepal length <= 5.95 [Confidence: 20.65%]


    Iris-virginica : (data 33.33% / prediction 33.33%) petal length > 2.45
        · 76.00%: petal length > 2.45 and petal width > 1.65 and petal length > 5.05 [Confidence: 90.82%]
        · 12.00%: petal length > 2.45 and petal width > 1.65 and petal length <= 5.05 and sepal width <= 2.9 [Confidence: 60.97%]
        · 6.00%: petal length > 2.45 and petal width <= 1.65 and petal length > 4.95 and sepal length > 6.05 [Confidence: 43.85%]
        · 4.00%: petal length > 2.45 and petal width > 1.65 and petal length <= 5.05 and sepal width > 2.9 and sepal length <= 6.4 and sepal length > 5.95 [Confidence: 34.24%]
        · 2.00%: petal length > 2.45 and petal width <= 1.65 and petal length > 4.95 and sepal length <= 6.05 and petal width <= 1.55 [Confidence: 20.65%]


You can also use ``local_model.get_data_distribution()`` and
``local_model.get_prediction_distribution()`` to obtain the training and
prediction basic distribution
information as a list (suitable to draw histograms or any further processing).
The tree nodes' information (prediction, confidence, impurity and distribution)
can also be retrieved in a CSV format using the method
``local_model.tree_CSV()``. The output can be sent to a file by providing a
``file_name`` argument or used as a list.

Local ensembles have a ``local_ensemble.summarize()`` method too, the output
in this case shows only the data distribution (only available in
``Decision Forests``) and field importance sections.

For local clusters, the ``local_cluster.summarize()`` method prints also the
data distribution, the training data statistics per cluster and the basic
intercentroid distance statistics. There's also a
``local_cluster.statistics_CSV(file_name)`` method that store in a CSV format
the values shown by the ``summarize()`` method. If no file name is provided,
the function returns the rows that would have been stored in the file as
a list.
