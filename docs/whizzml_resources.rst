.. toctree::
   :hidden:

WhizzML Resources
=================

WhizzML is a Domain Specific Language that allows the definition and
execution of ML-centric workflows. Its objective is allowing BigML
users to define their own composite tasks, using as building blocks
the basic resources provided by BigML itself. Using Whizzml they can be
glued together using a higher order, functional, Turing-complete language.
The WhizzML code can be stored and executed in BigML using three kinds of
resources: ``Scripts``, ``Libraries`` and ``Executions``.

WhizzML ``Scripts`` can be executed in BigML's servers, that is,
in a controlled, fully-scalable environment which takes care of their
parallelization and fail-safe operation. Each execution uses an ``Execution``
resource to store the arguments and results of the process. WhizzML
``Libraries`` store generic code to be shared of reused in other WhizzML
``Scripts``.

Scripts
-------

In BigML a ``Script`` resource stores WhizzML source code, and the results of
its compilation. Once a WhizzML script is created, it's automatically compiled;
if compilation succeeds, the script can be run, that is,
used as the input for a WhizzML execution resource.

An example of a ``script`` that would create a ``source`` in BigML using the
contents of a remote file is:

.. code-block:: python

    >>> from bigml.api import BigML
    >>> api = BigML()
    # creating a script directly from the source code. This script creates
    # a source uploading data from an s3 repo. You could also create a
    # a script by using as first argument the path to a .whizzml file which
    # contains your source code.
    >>> script = api.create_script( \
            "(create-source {\"remote\" \"s3://bigml-public/csv/iris.csv\"})")
    >>> api.ok(script) # waiting for the script compilation to finish
    >>> api.pprint(script['object'])
    {   u'approval_status': 0,
        u'category': 0,
        u'code': 200,
        u'created': u'2016-05-18T16:54:05.666000',
        u'description': u'',
        u'imports': [],
        u'inputs': None,
        u'line_count': 1,
        u'locale': u'en-US',
        u'name': u'Script',
        u'number_of_executions': 0,
        u'outputs': None,
        u'price': 0.0,
        u'private': True,
        u'project': None,
        u'provider': None,
        u'resource': u'script/573c9e2db85eee23cd000489',
        u'shared': False,
        u'size': 59,
        u'source_code': u'(create-source {"remote" "s3://bigml-public/csv/iris.csv"})',
        u'status': {   u'code': 5,
                       u'elapsed': 4,
                       u'message': u'The script has been created',
                       u'progress': 1.0},
        u'subscription': True,
        u'tags': [],
        u'updated': u'2016-05-18T16:54:05.850000',
        u'white_box': False}

A ``script`` allows to define some variables as ``inputs``. In the previous
example, no input has been defined, but we could modify our code to
allow the user to set the remote file name as input:

.. code-block:: python

    >>> from bigml.api import BigML
    >>> api = BigML()
    >>> script = api.create_script( \
            "(create-source {\"remote\" my_remote_data})",
            {"inputs": [{"name": "my_remote_data",
                         "type": "string",
                         "default": "s3://bigml-public/csv/iris.csv",
                         "description": "Location of the remote data"}]})

The ``script`` can also use a ``library`` resource (please, see the
``Libraries`` section below for more details) by including its id in the
``imports`` attribute. Other attributes can be checked at the
`API Developers documentation for Scripts <https://bigml.com/api/scripts#ws_script_arguments>`_.

Executions
----------

To execute in BigML a compiled WhizzML ``script`` you need to create an
``execution`` resource. It's also possible to execute a pipeline of
many compiled scripts in one request.

Each ``execution`` is run under its associated user credentials and its
particular environment constrains. As ``scripts`` can be shared,
different users can execute the same ``script`` using different inputs.
Each particular execution will generate an ``execution`` resource in BigML.

As an example of an ``execution`` resource, let's create one for the first
script in the previous section. In this case, no inputs are required because
the ``script`` expects none:

.. code-block:: python

    >>> from bigml.api import BigML
    >>> api = BigML()
    >>> execution = api.create_execution('script/573c9e2db85eee23cd000489')
    >>> api.ok(execution) # waiting for the execution to finish
    >>> api.pprint(execution['object'])
    {   u'category': 0,
        u'code': 200,
        u'created': u'2016-05-18T16:58:01.613000',
        u'creation_defaults': {   },
        u'description': u'',
        u'execution': {   u'output_resources': [   {   u'code': 1,
                                                       u'id': u'source/573c9f19b85eee23c600024a',
                                                       u'last_update': 1463590681854,
                                                       u'progress': 0.0,
                                                       u'state': u'queued',
                                                       u'task': u'Queuing job',
                                                       u'variable': u''}],
                          u'outputs': [],
                          u'result': u'source/573c9f19b85eee23c600024a',
                          u'results': [u'source/573c9f19b85eee23c600024a'],
                          u'sources': [[   u'script/573c9e2db85eee23cd000489',
                                              u'']],
                          u'steps': 16},
        u'inputs': None,
        u'locale': u'en-US',
        u'name': u"Script's Execution",
        u'project': None,
        u'resource': u'execution/573c9f19b85eee23bd000125',
        u'script': u'script/573c9e2db85eee23cd000489',
        u'script_status': True,
        u'shared': False,
        u'status': {   u'code': 5,
                       u'elapsed': 249,
                       u'elapsed_times': {   u'in-progress': 247,
                                             u'queued': 62,
                                             u'started': 2},
                       u'message': u'The execution has been created',
                       u'progress': 1.0},
        u'subscription': True,
        u'tags': [],
        u'updated': u'2016-05-18T16:58:02.035000'}

As you can see, the execution resource contains information about the result
of the execution, the resources that have been generated while executing and
users can define some variables in the code to be exported as outputs.

An ``execution`` receives inputs, the ones defined in the ``script`` chosen
to be executed, and generates a result. It can also generate outputs and
create resources. To
execute a ``script`` that expects some inputs, you will need to specify the
concrete values of those inputs, unless a default value has been assigned
for them in the script's inputs definition. Following the second example in
the previous section, we can execute the script that creates a source from a
URL pointing to a CSV file:

.. code-block:: python

    >>> from bigml.api import BigML
    >>> api = BigML()
    >>> execution = api.create_execution( \
            script,
            {"inputs": [["my_remote_data",
                         "https://static.bigml.com/csv/iris.csv"]]})

For more details on executions' structure, please refer to the
`Developers documentation for Executions <https://bigml.com/api/executions#we_execution_arguments>`_.


The results of an execution can be easily obtained by using the ``Execution``
class. This class can be used to instantiate a local object that will
expose the result, outputs and output resources generated in the execution
in its attributes.


.. code-block:: python

    from bigml.execution import Execution
    execution = Execution("execution/5cae5ad4b72c6609d9000468")
    print "The result of the execution is %s" % execution.result
    print " and the output for variable 'my_variable': %s" % \
        execution.outputs["my_variable"]
    print "The resources created in the execution are: %s" % \
        execution.output_resources

As an execution is in progress, the ``execution.result`` attribute will
contain the value of the last evaluated expression at that point.
Therefore, the value of the ``result`` attribute will change untill it
will contain the final result of the execution when finished.

Also, if the execution fails, the error information can be found in the
corresponding attributes:

.. code-block:: python

    from bigml.execution import Execution
    execution = Execution("execution/5cae5ad4b72c6609d9000468")
    print "The status of the execution is %s" % execution.status
    print "The execution failed at %s with error %s: %s" % ( \
        execution.error_location, execution.error, execution.error_message)


Libraries
---------

The ``library`` resource in BigML stores a special kind of compiled Whizzml
source code that only defines functions and constants. The ``library`` is
intended as an import for executable scripts.
Thus, a compiled library cannot be executed, just used as an
import in other ``libraries`` and ``scripts`` (which then have access
to all identifiers defined in the ``library``).

As an example, we build a ``library`` to store the definition of two functions:
``mu`` and ``g``. The first one adds one to the value set as argument and
the second one adds two variables and increments the result by one.


.. code-block:: python

    >>> from bigml.api import BigML
    >>> api = BigML()
    >>> library = api.create_library( \
            "(define (mu x) (+ x 1)) (define (g z y) (mu (+ y z)))")
    >>> api.ok(library) # waiting for the library compilation to finish
    >>> api.pprint(library['object'])
    {   u'approval_status': 0,
        u'category': 0,
        u'code': 200,
        u'created': u'2016-05-18T18:58:50.838000',
        u'description': u'',
        u'exports': [   {   u'name': u'mu', u'signature': [u'x']},
                        {   u'name': u'g', u'signature': [u'z', u'y']}],
        u'imports': [],
        u'line_count': 1,
        u'name': u'Library',
        u'price': 0.0,
        u'private': True,
        u'project': None,
        u'provider': None,
        u'resource': u'library/573cbb6ab85eee23c300018e',
        u'shared': False,
        u'size': 53,
        u'source_code': u'(define (mu x) (+ x 1)) (define (g z y) (mu (+ y z)))',
        u'status': {   u'code': 5,
                       u'elapsed': 2,
                       u'message': u'The library has been created',
                       u'progress': 1.0},
        u'subscription': True,
        u'tags': [],
        u'updated': u'2016-05-18T18:58:52.432000',
        u'white_box': False}

Libraries can be imported in scripts. The ``imports`` attribute of a ``script``
can contain a list of ``library`` IDs whose defined functions
and constants will be ready to be used throughout the ``script``. Please,
refer to the `API Developers documentation for Libraries <https://bigml.com/api/libraries#wl_library_arguments>`_
for more details.
