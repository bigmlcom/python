.. toctree::
   :hidden:

101 - OptiML usage
==================

Following the schema described in the `prediction workflow <api_sketch.html>`_,
document, this is the code snippet that shows the minimal workflow to
create an OptiML.

.. code-block:: python

    from bigml.api import BigML
    # step 0: creating a connection to the service (default credentials)
    api = BigML()
    # step 1: creating a source from the data in your local "data/iris.csv" file
    source = api.create_source("data/iris.csv")
    # waiting for the source to be finished. Results will be stored in `source`
    api.ok(source)
    # step 3: creating a dataset from the previously created `source`
    dataset = api.create_dataset(source)
    # waiting for the dataset to be finished
    api.ok(dataset)
    # step 5: creating an optiml
    optiml = api.create_optiml(dataset)
    # waiting for the optiml to be finished
    api.ok(optiml)

In the previous code, the `api.ok <creating_resources.html>`_
method is used to wait for the resource
to be finished before calling the next create method
or accessing the resource properties.
In the first case, we could skip that `api.ok`call because the next
`create` method would internally do the waiting when needed.

If you want to configure some of the attributes of your optiml, like the
maximum training time, you can use the second argument in the create call.

    # step 5: creating an optiml with a maximum training time of 3600 seconds
    optiml = api.create_optiml(dataset, {"max_training_time": 3600})
    # waiting for the optiml to be finished
    api.ok(optiml)

You can check all the available creation arguments in the `API documentation
<https://bigml.com/api/optimls#op_optiml_arguments>`_.
