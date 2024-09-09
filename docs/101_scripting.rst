.. toctree::
   :hidden:

101 - Creating and executing scripts
====================================

The bindings offer methods to create and execute `WhizzML <https://bigml.com/whizzml>`_
scripts in the platform.
WhizzML is the DSL that allows you to automate tasks in BigML.

These code snippets show examples to illustrate how to create and execute
simple scripts:

Basic script, no inputs
-----------------------

This is the code to create a simple script that creates a source from an
existing CSV file that is available in a remote URL:

.. code-block:: python

    from bigml.api import BigML
    # step 0: creating a connection to the service (default credentials)
    api = BigML()
    # step 1: creating a script that uploads a remote file and creates a source
    script = api.create_script( \
        "(create-source {\"remote\" \"https://static.bigml.com/csv/iris.csv\"})")
    # waiting for the script to be finished.
    api.ok(script)
    # step 2: executing the script with some particular inputs: a=1, b=2
    execution = api.create_execution(script)
    # waiting for the execution to be finished
    api.ok(execution)
    # step 3: retrieving the result (e.g. "source/5ce6a55dc984177cf7000891")
    result = execution['object']['execution']['result']

In the previous code, the `api.ok <creating_resources.html>`_
method is used to wait for the resource
to be finished before calling the next create method
or accessing the resource properties.
In the first case, we could skip that `api.ok`call because the next
`create` method would internally do the waiting when needed.

In this example. the `url` used is always the same, so no inputs are provided
to the script. This is not a realistic situation, because usually scripts
need user-provided inputs. The next example shows how to
add two variables, whose values will be provided as inputs.

Basic script with inputs
------------------------

Scripts usually need some inputs to work. When defining the script, you need
to provide booth the code and the description of the inputs that it will
accept.

.. code-block:: python

    from bigml.api import BigML
    # step 0: creating a connection to the service (default credentials)
    api = BigML()
    # step 1: creating a script that adds two numbers
    script = api.create_script( \
        "(+ a b)",
        {"inputs": [{"name": "a",
                     "type": "number"},
                     {"name": "b",
                      "type": "number"}]})
    # waiting for the script to be finished.
    api.ok(script)
    # step 2: executing the script with some particular inputs: a=1, b=2
    execution = api.create_execution( \
        script,
        {"inputs": [["a", 1],
                    ["b", 2]]})
    # waiting for the execution to be finished
    api.ok(execution)
    # step 3: retrieving the result (e.g. 3)
    result = execution['object']['execution']['result']

And of course, you will usually store your code, inputs and outputs in files.
The ``create_script`` method can receive as first argument the path to a file
that contains the source code and the rest of arguments can be retrieved from
a JSON file using the standard tools available in Python. The previous
example could also be created from a file that contains the WhizzML code
and a metadata file that contains the inputs and outputs description as a
JSON.

.. code-block:: python

    import json
    from bigml.api import BigML
    # step 0: creating a connection to the service (default credentials)
    api = BigML()
    # step 1: creating a script from the code stored in `my_script.whizzml`
    #         and the inputs and outputs metadata stored in `metadata.json`

    with open('./metadata.json') as json_file:
        metadata = json.load(json_file)
    script = api.create_script("./my_script.whizzml", metadata)
    # waiting for the script to be finished.
    api.ok(script)

Or load the files from a gist url:

.. code-block:: python

    import json
    from bigml.api import BigML
    # step 0: creating a connection to the service (default credentials)
    api = BigML()
    # step 1: creating a script from a gist

    gist_url = "https://gist.github.com/mmerce/49e0a69cab117b6a11fb490140326020"
    script = api.create_script(gist_url)
    # waiting for the script to be finished.
    api.ok(script)

Basic Execution
---------------

In a full-fledged script, you will also produce some outputs that can be used
in other scripts. This is an example of a script creating a dataset from a
source that was generated from a remote URL. Both the URL and the source
name are provided by the user. Once the script has been created, we
run it by creating an execution from it and placing the particular input values
that we want to apply it to.

.. code-block:: python

    from bigml.api import BigML
    # step 0: creating a connection to the service (default credentials)
    api = BigML()
    # step 1: creating a script that creates a `source` and a dataset from
    #         a user-given remote file
    script = api.create_script( \
        "(define my-dataset (create-dataset (create-source {\"remote\" url \"name\" source-name})))",
        {"inputs": [{"name": "url",
                     "type": "string"},
                     {"name": "source-name",
                      "type": "string"}],
         "outputs": [{"name": "my-dataset",
                      "type": "dataset"}]})
    # waiting for the script to be finished.
    api.ok(script)

    # step 2: executing the script with some particular inputs
    execution = api.create_execution( \
        script,
        {"inputs": [["url", "https://static.bigml.com/csv/iris.csv"],
                    ["source-name", "my source"]]})
    # waiting for the dataset to be finished
    api.ok(execution)
    # step 3: retrieving the result (e.g. "dataset/5cae5ad4b72c6609d9000356")
    result = execution['object']['execution']['result']


You can also use the ``Execution`` class to easily access the results,
outputs and output resources of an existing execution.
Just instantiate the  class with the execution resource or ID:

.. code-block:: python

    from bigml.execution import Execution
    execution = Execution("execution/5cae5ad4b72c6609d9000468")
    print "The result of the execution is %s" % execution.result
    print " and the output for variable 'my_variable': %s" % \
        execution.outputs["my_variable"]

Local and remote scripting
--------------------------

Any operation in BigML can be scripted by using the bindings locally
to call the API. However, the highest
efficiency, scalability and reproducibility will come only by using
WhizzML scripts in the platform to handle the Machine Learning workflow that
you need. Thus, in most situations, the bindings are used merely to
upload the data to the platform and create an execution that uses that data to
reproduce the same operations. Let's say that you have a WhizzML script that
generates a batch prediction based on an existing model. The only input
for the script will be the source ID that will be used to predict, and the
rest of steps will be handled by the WhizzML script. Therefore, in order to
use that on new data you'll need to upload that data to the platform and use
the resulting ID as input.


.. code-block:: python

    from bigml.api import BigML
    # step 0: creating a connection to the service (default credentials)
    api = BigML()
    # step 1: creating a script that uploads local data to create a `source`
    source = api.create_source("my_local_file")
    # waiting for the source to be finished.
    api.ok(source)

    # step 2: executing the script to do a batch prediction with the new
    # source as input
    script = "script/5cae5ad4b72c6609d9000235"
    execution = api.create_execution( \
        script,
        {"inputs": [["source", source["resource"]]]})
    # waiting for the workflow to be finished
    api.ok(execution)
    # step 3: retrieving the result (e.g. "dataset/5cae5ad4b72c6609d9000356")
    result = execution['object']['execution']['result']
    # step 4: maybe storing the result as a CSV
    api.download_dataset(result, "my_predictions.csv")
