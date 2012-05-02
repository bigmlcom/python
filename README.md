# BigML.io Python bindings

In this directory you'll find an open source Python module that gives
you a simple binding to interact with [BigML](https://bigml.io). You
can use it to easily create, retrieve, list, update, and delete BigML
resources (i.e., sources, datasets, models and, predictions).

This module is licensed under the Apache Licence, Version 2.0
(http://www.apache.org/licenses/LICENSE-2.0.html).


## Requirements

The Python bindings use the
[requests](https://github.com/kennethreitz/requests) library.  This
library is automatically installed during the setup.

The bindings will also use `simplejson` if you happen to have it
installed, but that is optional: we fallback to Python's buit-in JSON
libraries by default.

## Installation

To install:

```bash
$ python setup.py install
```

You can also install the bindings directly from this git repository
with the command:

```bash
$ pip install -e git://github.com/bigmlcom/python.git#egg=bigml_python
```

## Importing the module

```python
import bigml.api
```

Alternatively you can just import the BigML class.

```python
from bigml.api import BigML
```
## Authentication

All the requests to BigML.io must be authenticated using your username
and [API key](https://bigml.com/account/apikey) and are always
transmitted over HTTPS.

This module will look for your username and API key in the environment
variables `BIGML_USERNAME` and `BIGML_API_KEY` respectively.  You can
add the following lines to your `.bashrc` or `.bash_profile` to set
those variables automatically when you log in:


```bash
export BIGML_USERNAME=myusername
export BIGML_API_KEY=ae579e7e53fb9abd646a6ff8aa99d4afe83ac291
```

If you do so, just with the following snippet you are connected to
BigML.

```python
from bigml.api import BigML
api = BigML()
```

Otherwise, you can can initialize directly when instantaiting the
BigML class as follows.


```python
api = BigML('myusername', 'ae579e7e53fb9abd646a6ff8aa99d4afe83ac291')
```

## Running the Tests

To run the tests you will need to get
[lettuce](http://packages.python.org/lettuce/tutorial/simple.html)
installed:

```bash
$ pip install lettuce
```

and set up your authentication first as explained above.  Then, you
can run the test suite simply by:

```bash
$ cd tests
$ lettuce
```

## Quick Start

Imagine that you want to use
[this csv file](https://static.bigml.com/csv/iris.csv ) containing the
[Iris flower dataset](http://en.wikipedia.org/wiki/Iris_flower_data_set)
to predict the species of a flower whose `sepal length` is `5` and
whose `sepal width` is `2.5`. A preview of the dataset is shown
below. It has 4 numeric fields: `sepal length`, `sepal width`, `petal
length`, `petal width` and a categorical field: `species`. By default,
BigML considers the last field in the dataset as the objective field
(i.e., the field that you want to generate predictions for).

```csv
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
```

You can easily generate a prediction following the next steps.

```python
from bigml.api import BigML

api = BigML()

source = api.create_source('../data/iris.csv')
dataset = api.create_dataset(source)
model = api.create_model(dataset)
prediction = api.create_prediction(model, {'sepal length': 5, 'sepal width': 2.5})
```

You can then print the prediction using the `pprint` method.

```python
api.pprint(prediction)
```

You'll see:

```python
species for {"sepal width": 2.5, "sepal length": 5} is Iris-virginica
```

## Fields

BigML automatically generates ids for each field. To see the fields
and their corresponding ids and types that that have been assigned to
a source you can use:

```python
source = api.get_source(source)
api.pprint(api.get_fields(source))
```

and you'll get:

```python
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
```

## Dataset

If you want to get some basic statistics for each field you can
retrieve the `fields` from the dataset as follows.

```python
dataset = api.get_dataset(dataset)
api.pprint(api.get_fields(dataset))
```

You will get a dictionary keyed by each field id.

```python
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
```

## Model

One of the greatest things of BigML is that the models that it generates for
you are fully white-boxed. To get the model for the example above you can retrieve it as follows:

```python
model = api.get_model(model)
api.pprint(model['object']['model']['root'])
```

You will get a explicit tree-like predictive model:

```python
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
```

(Note that we have abbreviated the output in the snippet above for
readability: the full predictive model you'll get i going to contain
much more nodes).

## Creating Resources

Newly-created resources are returned in a dictionary with the
following keys:

* **code**: If the request is successful you will get a
    `bigml.api.HTTP_CREATED` (201) status code. Otherwise, it will be
    one of the standard HTTP error codes. See
    [BigML documentation on status codes](https://bigml.com/developers/status_codes)
    for more info.
* **resource**: The id of the new resource.
* **location**: The location of the new resource.
* **object**: The resource itself as returned by BigML.
* **error**: If an error occurs and the resource cannot be created, it
    will contain an additional code and a description of the error. In
    this case, **location**, and **resource** will be `None`.

### Statuses

Please, bear in mind that resource creation is asynchronous except for
**predictions**. Therefore when you create a new source, a new dataset
or a new model even if you receive an immediate response from the
BigML servers, the fully creation of the resource can take from a few
seconds to a few days depending on the size of the resource and
BigML's load. A resource is not fully created until its status is
`bigml.api.FINISHED`. See
[BigML documentation on status codes](https://bigml.com/developers/status_codes)
for the listing of potential states and their semantics.  So depending
on your application you might need to import the following constants.

```python
bigml.api import WAITING
bigml.api import QUEUED
bigml.api import STARTED
bigml.api import IN_PROGRESS
bigml.api import SUMMARIZED
bigml.api import FINISHED
bigml.api import FAULTY
bigml.api import UNKNOWN
bigml.api import RUNNABLE
```

You can query the status of any resource with the `status` method.

```python
api.status(source)
api.status(dataset)
api.status(model)
api.status(prediction)
```

By default, before invoking the creation of a new resource the binding
checks that the status of resource that is passed as a parameter is
`FINISHED`. You can change how often the status will be checked with
the `wait_time` argument. By default it is setup to 3 seconds.

### Creating sources

To create a source from a local data file, you can use the
`create_source` method. The only required parameter is the path to the
data file. You can use a second optional parameter to specify any of
the options for source creation described in the
[BigML documentation](https://bigml.com/developers/sources).

Here's a sample invocation:

```python

from bigml.api import BigML
api = BigML()

source = api.create_source('../data/iris.csv',
    {'name': 'my source', 'source_parser': {'missing_tokens': ['?']}})
```

Souce creation is asynchronous: the initial resource status code will
be `WAITING` or `QUEUED`. You can retrieve the updated status at any
time using the corresponding get method. For example to get the status

```python
api.status(source)
```

### Creating datasets

Once you have created a source, you can create a dataset. The only
required argument to create a dataset is a source id. You can add all
the additional arguments accepted by BigML and documented
[here](https://bigml.com/developers/datasets).

For example, to create a dataset named "my dataset" with the first
1024 bytes of a source. You can do the following request.

```python
dataset = api.create_dataset(source, {"name": "my dataset", "size": 1024})
```

By default the

### Creating models

Once you have created a dataset, you can create a model. The only
required argument to create a model is a dataset id. You can also
include in the request all the additional arguments accepted by BigML
and documented [here](https://bigml.com/developers/models).


For example, to create a model only including the first to fields and
the first 10 instances you can perform the following invokation.

```python
model = api.create_model(dataset, {
    "name": "my model", "input_fields": ["000000", "000001"], "range": [1, 10]})
```

Again, the model is scheduled for creation, and you can retrieve its
status at any time by means of `api.status(model)` .

### Creating predictions

You can now use the model resource identifier together with some input
parameters to ask for predictions, using the `create_prediction`
method. You can also give the prediction a name.

```python
prediction = api.create_prediction(model,
                                   {"sepal length": 5,
                                    "sepal width": 2.5},
                                    {"name": "my prediction"})
```

To see the prediction you can use `pprint`:

```python
api.pprint(prediction)
```

## Reading Resources

When you retrieve an individual resource it is returned in a
dictionary exactly like the one you get when you create a new
resource. However the status code will be `bigml.api.HTTP_OK` if the
resource can be retrieved without problems or one of the HTTP standard
error codes otherwise.

## Listing Resources

You can list resources with the appropiate api method:

```python
api.list_sources()
api.list_datasets()
api.list_models()
api.list_predictions()
```

you will receive a dictionary with the following keys:

* **code**: If the request is successful you will get a
    `bigml.api.HTTP_OK` (200) status code. Otherwise, it will be one
    of the standard HTTP error codes. See
    [BigML documentation on status codes](https://bigml.com/developers/status_codes)
    for more info.
* **meta**: A dictionary including the following keys that can help
  you paginate listings:
    * **previous**: Path to get the previous page or None if there is
        no previous page.
    * **next**: Path to get the next page or None if there is no next
        page.
    * **offset**: How far off from the first resource in the resources
        is the first resource listed in the resources key.
    * **limit**: Maximum number of resources that you will get listed
      in the resources key.
    * **total_count**: The total number of resources in BigML.
* **objects**: A list of resources as returned by BigML.
* **error**: If an error occurs and the resource cannot be created, it
    will contain an additional code and a description of the error. In
    this case, **meta**, and **resources** will be `None`.

### Filtering Resources

You can filter resources in listings using the syntax and fields
labeled as *filterable* in the
[BigML documentation](https://bigml.com/developers) for each resource.

A few examples:

#### Ids of the first 5 sources created before April 1st, 2012

```python
[source['resource'] for source in
  api.list_sources("limit=5;created__lt=2012-04-1")['objects']]
```

#### Name of the first 10 datasets bigger than 1MB

```python
[dataset['name'] for dataset in
  api.list_datasets("limit=10;size__gt=1048576")['objects']]
```

#### Name of models with more than 5 fields (columns)

```python
[model['name'] for model in api.list_models("columns__gt=5")['objects']]
```

#### Ids of predictions whose model has not been deleted

```python
[prediction['resource'] for prediction in
  api.list_predictions("model_status=true")['objects']]
```


### Ordering Resources

You can order resources in listings using the syntax and fields
labeled as *sortable* in the
[BigML documentation](https://bigml.com/developers) for each resource.

A few examples:

#### Name of sources ordered by size

```python
[source['name'] for source in api.list_sources("order_by=size")['objects']]
```

#### Number of instances in datasets created before April 1st, 2012 ordered by size

```python
[dataset['rows'] for dataset in
  api.list_datasets("created__lt=2012-04-1;order_by=size")['objects']]
```

#### Model ids ordered by number of predictions (in descending order).

```python
[model['resource'] for model in
  api.list_models("order_by=-number_of_predictions")['objects']]
```

#### Name of predictions ordered by name.

```python
[prediction['name'] for prediction in
  api.list_predictions("order_by=name")['objects']]
```

## Updating Resources

When you update a resource it is returned in a dictionary exactly like
the one you get when you create a new resource. However the status
code will be `bigml.api.HTTP_ACCEPTED` if the resource can be updated
without problems or one of the HTTP standard error codes otherwise.

```python
api.update_source(source, {"name": "new name"})
api.update_dataset(detaset, {"name": "new name"})
api.update_model(model, {"name": "new name"})
api.update_prediction(prediction, {"name": "new name"})
```

## Deleting Resources

Resources can be deleted individually using the corresponding method
for each type of resource.

```python
api.delete_source(source)
api.delete_dataset(dataset)
api.delete_model(model)
api.delete_prediction(prediction)
```

Each of the delete method calls above will return a dictionary with
the following keys:

* **code** If the request is successful, the code will be a
  `bigml.api.HTTP_NO_CONTENT` (204) status code. Otherwise, it wil be
  one of the standard HTTP error codes. See
  [BigML documentation on status codes](https://bigml.com/developers/status_codes)
  for more info.
* **error** If the request does not succeed it will contain a
  dictionary with an error code and a message. It will be None
  otherwise.
