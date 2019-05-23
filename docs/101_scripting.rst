BigML Bindings: 101 - Creating and executing scripts
====================================================

The bindings offer methods to create and execute `WhizzML
<https://bigml.com/whizzml>_` scripts in the platform.
WhizzML is the DSL that allows you to automate tasks in BigML.

These code snippets show examples to illustrate how to create and execute
simple scripts:

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

In this example. the `url` used is always the same, so no inputs are provided
to the script. This is not a realistic situation, because usually scripts
need user-provided inputs. The next example shows how to
add two variables, whose values will be provided as inputs:

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

In a full-fledged script, you will also produce some outputs that can be used
in other scripts. This is an example of a script creating a dataset from a
source that was generated from a remote URL. Both the URL and the source
name are provided by the user:

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
