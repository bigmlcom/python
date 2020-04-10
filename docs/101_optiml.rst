BigML Bindings: 101 - Using an OptiML
=====================================

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

If you want to configure some of the attributes of your optiml, like the
maximum training time, you can use the second argument in the create call.

    # step 5: creating an optiml with a maximum training time of 3600 seconds
    optiml = api.create_optiml(dataset, {"max_training_time": 3600})
    # waiting for the optiml to be finished
    api.ok(optiml)

You can check all the available creation arguments in the `API documentation
<https://bigml.com/api/optimls#op_optiml_arguments>`_.
