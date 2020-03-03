ML Resources
============


External Connectors
-------------------

The ``Externalconnector`` object is  is an abstract resource that helps
you create ``Sources`` from several external data sources
like relational databases or ElasticSearch engines. This is not strictly
a Machine Learning resource, but a helper to connect your data repos to BigML.

.. code-block:: python

    >>> external_connector = api.get_external_connector( \
            "externalconnector/5e30b685e476845dd901df83")

You can check the external connector properties at the `API documentation
<https://bigml.com/api/externalconnectors#ec_external_connector_properties>`_.

Source
------

The ``Source`` is the first resource that you build in BigML when uploading
a file. BigML infers the structure of the file, whether it has headers or not,
the column separator or the field types and names and stores the results in
the ``Source`` information:

.. code-block:: python

    >>> source = api.get_source("source/5e30b685e476845dd901df83")
    >>> api.pprint(source["object"])
    {   u'category': 0,
        u'charset': u'UTF-8',
        u'code': 200,
        u'configuration': None,
        u'configuration_status': False,
        u'content_type': u'text/plain;UTF-8',
        u'created': u'2020-01-28T22:32:37.290000',
        u'creator': u'mmartin',
        u'credits': 0,
        u'description': u'',
        u'disable_datetime': False,
        u'field_types': {   u'categorical': 0,
                            u'datetime': 0,
                            u'items': 0,
                            u'numeric': 4,
                            u'text': 1,
                            u'total': 5},
        u'fields': {   u'000000': {   u'column_number': 0,
                                      u'name': u'sepal length',
                                      u'optype': u'numeric',
                                      u'order': 0},
                       u'000001': {   u'column_number': 1,
                                      u'name': u'sepal width',
                                      u'optype': u'numeric',
                                      u'order': 1},
                       u'000002': {   u'column_number': 2,
                                      u'name': u'petal length',
                                      u'optype': u'numeric',
                                      u'order': 2},
                       u'000003': {   u'column_number': 3,
                                      u'name': u'petal width',
                                      u'optype': u'numeric',
                                      u'order': 3},
                       u'000004': {   u'column_number': 4,
                                      u'name': u'species',
                                      u'optype': u'text',
                                      u'order': 4,
                                      u'term_analysis': {   u'enabled': True}}},
        u'fields_meta': {   u'count': 5,
                            u'image': 0,
                            u'limit': 1000,
                            u'offset': 0,
                            u'query_total': 5,
                            u'total': 5},
        ...
    }

You can check the source properties at the `API documentation
<https://bigml.com/api/sources#sr_source_properties>`_.

Dataset
-------

If you want to get some basic statistics for each field you can retrieve
the ``fields`` from the dataset as follows to get a dictionary keyed by
field id:

.. code-block:: python

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


The field filtering options are also available using a query string expression,
for instance:

.. code-block:: python

    >>> dataset = api.get_dataset(dataset, "limit=20")

limits the number of fields that will be included in ``dataset`` to 20.

You can check the dataset properties at the `API documentation
<https://bigml.com/api/datasets#ds_dataset_properties>`_.

Model
-----

One of the greatest things about BigML is that the models that it
generates for you are fully white-boxed. To get the explicit tree-like
predictive model for the example above:

.. code-block:: python

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

Again, filtering options are also available using a query string expression,
for instance:

.. code-block:: python

    >>> model = api.get_model(model, "limit=5")

limits the number of fields that will be included in ``model`` to 5.

You can check the model properties at the `API documentation
<https://bigml.com/api/models#md_model_properties>`_.

Evaluation
----------

The predictive performance of a model can be measured using many different
measures. In BigML these measures can be obtained by creating evaluations. To
create an evaluation you need the id of the model you are evaluating and the id
of the dataset that contains the data to be tested with. The result is shown
as:

.. code-block:: python

    >>> evaluation = api.get_evaluation(evaluation)
    >>> api.pprint(evaluation['object']['result'])
    {   'class_names': ['0', '1'],
        'mode': {   'accuracy': 0.9802,
                    'average_f_measure': 0.495,
                    'average_phi': 0,
                    'average_precision': 0.5,
                    'average_recall': 0.4901,
                    'confusion_matrix': [[99, 0], [2, 0]],
                    'per_class_statistics': [   {   'accuracy': 0.9801980198019802,
                                                    'class_name': '0',
                                                    'f_measure': 0.99,
                                                    'phi_coefficient': 0,
                                                    'precision': 1.0,
                                                    'present_in_test_data': True,
                                                    'recall': 0.9801980198019802},
                                                {   'accuracy': 0.9801980198019802,
                                                    'class_name': '1',
                                                    'f_measure': 0,
                                                    'phi_coefficient': 0,
                                                    'precision': 0.0,
                                                    'present_in_test_data': True,
                                                    'recall': 0}]},
        'model': {   'accuracy': 0.9901,
                     'average_f_measure': 0.89746,
                     'average_phi': 0.81236,
                     'average_precision': 0.99495,
                     'average_recall': 0.83333,
                     'confusion_matrix': [[98, 1], [0, 2]],
                     'per_class_statistics': [   {   'accuracy': 0.9900990099009901,
                                                     'class_name': '0',
                                                     'f_measure': 0.9949238578680203,
                                                     'phi_coefficient': 0.8123623944599232,
                                                     'precision': 0.98989898989899,
                                                     'present_in_test_data': True,
                                                     'recall': 1.0},
                                                 {   'accuracy': 0.9900990099009901,
                                                     'class_name': '1',
                                                     'f_measure': 0.8,
                                                     'phi_coefficient': 0.8123623944599232,
                                                     'precision': 1.0,
                                                     'present_in_test_data': True,
                                                     'recall': 0.6666666666666666}]},
        'random': {   'accuracy': 0.50495,
                      'average_f_measure': 0.36812,
                      'average_phi': 0.13797,
                      'average_precision': 0.74747,
                      'average_recall': 0.51923,
                      'confusion_matrix': [[49, 50], [0, 2]],
                      'per_class_statistics': [   {   'accuracy': 0.504950495049505,
                                                      'class_name': '0',
                                                      'f_measure': 0.6621621621621622,
                                                      'phi_coefficient': 0.1379728923974526,
                                                      'precision': 0.494949494949495,
                                                      'present_in_test_data': True,
                                                      'recall': 1.0},
                                                  {   'accuracy': 0.504950495049505,
                                                      'class_name': '1',
                                                      'f_measure': 0.07407407407407407,
                                                      'phi_coefficient': 0.1379728923974526,
                                                      'precision': 1.0,
                                                      'present_in_test_data': True,
                                                      'recall': 0.038461538461538464}]}}

where two levels of detail are easily identified. For classifications,
the first level shows these keys:

-  **class_names**: A list with the names of all the categories for the objective field (i.e., all the classes)
-  **mode**: A detailed result object. Measures of the performance of the classifier that predicts the mode class for all the instances in the dataset
-  **model**: A detailed result object.
-  **random**: A detailed result object.  Measures the performance of the classifier that predicts a random class for all the instances in the dataset.

and the detailed result objects include ``accuracy``, ``average_f_measure``, ``average_phi``,
``average_precision``, ``average_recall``, ``confusion_matrix``
and ``per_class_statistics``.

For regressions first level will contain these keys:

-  **mean**: A detailed result object. Measures the performance of the model that predicts the mean for all the instances in the dataset.
-  **model**: A detailed result object.
-  **random**: A detailed result object. Measures the performance of the model that predicts a random class for all the instances in the dataset.

where the detailed result objects include ``mean_absolute_error``,
``mean_squared_error`` and ``r_squared`` (refer to
`developers documentation <https://bigml.com/api/evaluations>`_ for
more info on the meaning of these measures.

You can check the evaluation properties at the `API documentation
<https://bigml.com/api/evaluations#ev_evaluation_properties>`_.

Cluster
-------

For unsupervised learning problems, the cluster is used to classify in a
limited number of groups your training data. The cluster structure is defined
by the centers of each group of data, named centroids, and the data enclosed
in the group. As for in the model's case, the cluster is a white-box resource
and can be retrieved as a JSON:

.. code-block:: python

    >>> cluster = api.get_cluster(cluster)
    >>> api.pprint(cluster['object'])
    {   'balance_fields': True,
        'category': 0,
        'cluster_datasets': {   '000000': '', '000001': '', '000002': ''},
        'cluster_datasets_ids': {   '000000': '53739b9ae4b0dad82b0a65e6',
                                    '000001': '53739b9ae4b0dad82b0a65e7',
                                    '000002': '53739b9ae4b0dad82b0a65e8'},
        'cluster_seed': '2c249dda00fbf54ab4cdd850532a584f286af5b6',
        'clusters': {   'clusters': [   {   'center': {   '000000': 58.5,
                                                          '000001': 26.8314,
                                                          '000002': 44.27907,
                                                          '000003': 14.37209},
                                            'count': 56,
                                            'distance': {   'bins': [   [   0.69602,
                                                                            2],
                                                                        [ ... ]
                                                                        [   3.77052,
                                                                            1]],
                                                            'maximum': 3.77052,
                                                            'mean': 1.61711,
                                                            'median': 1.52146,
                                                            'minimum': 0.69237,
                                                            'population': 56,
                                                            'standard_deviation': 0.6161,
                                                            'sum': 90.55805,
                                                            'sum_squares': 167.31926,
                                                            'variance': 0.37958},
                                            'id': '000000',
                                            'name': 'Cluster 0'},
                                        {   'center': {   '000000': 50.06,
                                                          '000001': 34.28,
                                                          '000002': 14.62,
                                                          '000003': 2.46},
                                            'count': 50,
                                            'distance': {   'bins': [   [   0.16917,
                                                                            1],
                                                                        [ ... ]
                                                                        [   4.94699,
                                                                            1]],
                                                            'maximum': 4.94699,
                                                            'mean': 1.50725,
                                                            'median': 1.3393,
                                                            'minimum': 0.16917,
                                                            'population': 50,
                                                            'standard_deviation': 1.00994,
                                                            'sum': 75.36252,
                                                            'sum_squares': 163.56918,
                                                            'variance': 1.01998},
                                            'id': '000001',
                                            'name': 'Cluster 1'},
                                        {   'center': {   '000000': 68.15625,
                                                          '000001': 31.25781,
                                                          '000002': 55.48438,
                                                          '000003': 19.96875},
                                            'count': 44,
                                            'distance': {   'bins': [   [   0.36825,
                                                                            1],
                                                                        [ ... ]
                                                                        [   3.87216,
                                                                            1]],
                                                            'maximum': 3.87216,
                                                            'mean': 1.67264,
                                                            'median': 1.63705,
                                                            'minimum': 0.36825,
                                                            'population': 44,
                                                            'standard_deviation': 0.78905,
                                                            'sum': 73.59627,
                                                            'sum_squares': 149.87194,
                                                            'variance': 0.6226},
                                            'id': '000002',
                                            'name': 'Cluster 2'}],
                        'fields': {   '000000': {   'column_number': 0,
                                                    'datatype': 'int8',
                                                    'name': 'sepal length',
                                                    'optype': 'numeric',
                                                    'order': 0,
                                                    'preferred': True,
                                                    'summary': {   'bins': [   [   43.75,
                                                                                   4],
                                                                               [ ... ]
                                                                               [   79,
                                                                                   1]],
                                                                   'maximum': 79,
                                                                   'mean': 58.43333,
                                                                   'median': 57.7889,
                                                                   'minimum': 43,
                                                                   'missing_count': 0,
                                                                   'population': 150,
                                                                   'splits': [   45.15258,
                                                                                 46.72525,
                                                                              72.04226,
                                                                                 76.47461],
                                                                   'standard_deviation': 8.28066,
                                                                   'sum': 8765,
                                                                   'sum_squares': 522385,
                                                                   'variance': 68.56935}},
                                                                    [ ... ]
                                                                                 [   25,
                                                                                     3]],
                                                                   'maximum': 25,
                                                                   'mean': 11.99333,
                                                                   'median': 13.28483,
                                                                   'minimum': 1,
                                                                   'missing_count': 0,
                                                                   'population': 150,
                                                                   'standard_deviation': 7.62238,
                                                                   'sum': 1799,
                                                                   'sum_squares': 30233,
                                                                   'variance': 58.10063}}}},
        'code': 202,
        'columns': 4,
        'created': '2014-05-14T16:36:40.993000',
        'credits': 0.017578125,
        'credits_per_prediction': 0.0,
        'dataset': 'dataset/53739b88c8db63122b000411',
        'dataset_field_types': {   'categorical': 1,
                                   'datetime': 0,
                                   'numeric': 4,
                                   'preferred': 5,
                                   'text': 0,
                                   'total': 5},
        'dataset_status': True,
        'dataset_type': 0,
        'description': '',
        'excluded_fields': ['000004'],
        'field_scales': None,
        'fields_meta': {   'count': 4,
                           'limit': 1000,
                           'offset': 0,
                           'query_total': 4,
                           'total': 4},
        'input_fields': ['000000', '000001', '000002', '000003'],
        'k': 3,
        'locale': 'es-ES',
        'max_columns': 5,
        'max_rows': 150,
        'name': 'my iris',
        'number_of_batchcentroids': 0,
        'number_of_centroids': 0,
        'number_of_public_centroids': 0,
        'out_of_bag': False,
        'price': 0.0,
        'private': True,
        'range': [1, 150],
        'replacement': False,
        'resource': 'cluster/53739b98d994972da7001de9',
        'rows': 150,
        'sample_rate': 1.0,
        'scales': {   '000000': 0.22445382597655375,
                      '000001': 0.4264213814821549,
                      '000002': 0.10528680248949522,
                      '000003': 0.2438379900517961},
        'shared': False,
        'size': 4608,
        'source': 'source/53739b24d994972da7001ddd',
        'source_status': True,
        'status': {   'code': 5,
                      'elapsed': 1009,
                      'message': 'The cluster has been created',
                      'progress': 1.0},
        'subscription': True,
        'tags': [],
        'updated': '2014-05-14T16:40:26.234728',
        'white_box': False}

(Note that we have abbreviated the output in the snippet above for
readability: the full predictive cluster you'll get is going to contain
much more details).

You can check the cluster properties at the `API documentation
<https://bigml.com/api/clusters#cl_cluster_properties>`_.

Anomaly detector
----------------

For anomaly detection problems, BigML anomaly detector uses iforest as an
unsupervised kind of model that detects anomalous data in a dataset. The
information it returns encloses a `top_anomalies` block
that contains a list of the most anomalous
points. For each, we capture a `score` from 0 to 1.  The closer to 1,
the more anomalous. We also capture the `row` which gives values for
each field in the order defined by `input_fields`.  Similarly we give
a list of `importances` which match the `row` values.  These
importances tell us which values contributed most to the anomaly
score. Thus, the structure of an anomaly detector is similar to:

.. code-block:: python

    {   'category': 0,
        'code': 200,
        'columns': 14,
        'constraints': False,
        'created': '2014-09-08T18:51:11.893000',
        'credits': 0.11653518676757812,
        'credits_per_prediction': 0.0,
        'dataset': 'dataset/540dfa9d9841fa5c88000765',
        'dataset_field_types': {   'categorical': 21,
                                   'datetime': 0,
                                   'numeric': 21,
                                   'preferred': 14,
                                   'text': 0,
                                   'total': 42},
        'dataset_status': True,
        'dataset_type': 0,
        'description': '',
        'excluded_fields': [],
        'fields_meta': {   'count': 14,
                           'limit': 1000,
                           'offset': 0,
                           'query_total': 14,
                           'total': 14},
        'forest_size': 128,
        'input_fields': [   '000004',
                            '000005',
                            '000009',
                            '000016',
                            '000017',
                            '000018',
                            '000019',
                            '00001e',
                            '00001f',
                            '000020',
                            '000023',
                            '000024',
                            '000025',
                            '000026'],
        'locale': 'en_US',
        'max_columns': 42,
        'max_rows': 200,
        'model': {   'fields': {   '000004': {   'column_number': 4,
                                                 'datatype': 'int16',
                                                 'name': 'src_bytes',
                                                 'optype': 'numeric',
                                                 'order': 0,
                                                 'preferred': True,
                                                 'summary': {   'bins': [   [   143,
                                                                                2],
                                                                            ...
                                                                            [   370,
                                                                                2]],
                                                                'maximum': 370,
                                                                'mean': 248.235,
                                                                'median': 234.57157,
                                                                'minimum': 141,
                                                                'missing_count': 0,
                                                                'population': 200,
                                                                'splits': [   159.92462,
                                                                              173.73312,
                                                                              188,
                                                                              ...
                                                                              339.55228],
                                                                'standard_deviation': 49.39869,
                                                                'sum': 49647,
                                                                'sum_squares': 12809729,
                                                                'variance': 2440.23093}},
                                   '000005': {   'column_number': 5,
                                                 'datatype': 'int32',
                                                 'name': 'dst_bytes',
                                                 'optype': 'numeric',
                                                 'order': 1,
                                                 'preferred': True,
                                                  ...
                                                                'sum': 1030851,
                                                                'sum_squares': 22764504759,
                                                                'variance': 87694652.45224}},
                                   '000009': {   'column_number': 9,
                                                 'datatype': 'string',
                                                 'name': 'hot',
                                                 'optype': 'categorical',
                                                 'order': 2,
                                                 'preferred': True,
                                                 'summary': {   'categories': [   [   '0',
                                                                                      199],
                                                                                  [   '1',
                                                                                      1]],
                                                                'missing_count': 0},
                                                 'term_analysis': {   'enabled': True}},
                                   '000016': {   'column_number': 22,
                                                 'datatype': 'int8',
                                                 'name': 'count',
                                                 'optype': 'numeric',
                                                 'order': 3,
                                                 'preferred': True,
                                                                ...
                                                                'population': 200,
                                                                'standard_deviation': 5.42421,
                                                                'sum': 1351,
                                                                'sum_squares': 14981,
                                                                'variance': 29.42209}},
                                   '000017': { ... }}},
                     'kind': 'iforest',
                     'mean_depth': 12.314174107142858,
                     'top_anomalies': [   {   'importance': [   0.06768,
                                                                0.01667,
                                                                0.00081,
                                                                0.02437,
                                                                0.04773,
                                                                0.22197,
                                                                0.18208,
                                                                0.01868,
                                                                0.11855,
                                                                0.01983,
                                                                0.01898,
                                                                0.05306,
                                                                0.20398,
                                                                0.00562],
                                              'row': [   183.0,
                                                         8654.0,
                                                         '0',
                                                         4.0,
                                                         4.0,
                                                         0.25,
                                                         0.25,
                                                         0.0,
                                                         123.0,
                                                         255.0,
                                                         0.01,
                                                         0.04,
                                                         0.01,
                                                         0.0],
                                              'score': 0.68782},
                                          {   'importance': [   0.05645,
                                                                0.02285,
                                                                0.0015,
                                                                0.05196,
                                                                0.04435,
                                                                0.0005,
                                                                0.00056,
                                                                0.18979,
                                                                0.12402,
                                                                0.23671,
                                                                0.20723,
                                                                0.05651,
                                                                0.00144,
                                                                0.00612],
                                              'row': [   212.0,
                                                         1940.0,
                                                         '0',
                                                         1.0,
                                                         2.0,
                                                         0.0,
                                                         0.0,
                                                         1.0,
                                                         1.0,
                                                         69.0,
                                                         1.0,
                                                         0.04,
                                                         0.0,
                                                         0.0],
                                              'score': 0.6239},
                                              ...],
                     'trees': [   {   'root': {   'children': [   {   'children': [   {   'children': [   {   'children': [   {   'children':
     [   {   'population': 1,
                                                                                                                                  'predicates': [   {   'field': '00001f',
                                                                                                                                                        'op': '>',
                                                                                                                                                        'value': 35.54357}]},

    ...
                                                                                                                              {   'population': 1,
                                                                                                                                  'predicates': [   {   'field': '00001f',
                                                                                                                                                        'op': '<=',
                                                                                                                                                        'value': 35.54357}]}],
                                                                                                              'population': 2,
                                                                                                              'predicates': [   {   'field': '000005',
                                                                                                                                    'op': '<=',
                                                                                                                                    'value': 1385.5166}]}],
                                                                                          'population': 3,
                                                                                          'predicates': [   {   'field': '000020',
                                                                                                                'op': '<=',
                                                                                                                'value': 65.14308},
                                                                                                            {   'field': '000019',
                                                                                                                'op': '=',
                                                                                                                'value': 0}]}],
                                                                      'population': 105,
                                                                      'predicates': [   {   'field': '000017',
                                                                                            'op': '<=',
                                                                                            'value': 13.21754},
                                                                                        {   'field': '000009',
                                                                                            'op': 'in',
                                                                                            'value': [   '0']}]}],
                                                  'population': 126,
                                                  'predicates': [   True,
                                                                    {   'field': '000018',
                                                                        'op': '=',
                                                                        'value': 0}]},
                                      'training_mean_depth': 11.071428571428571}]},
        'name': "tiny_kdd's dataset anomaly detector",
        'number_of_batchscores': 0,
        'number_of_public_predictions': 0,
        'number_of_scores': 0,
        'out_of_bag': False,
        'price': 0.0,
        'private': True,
        'project': None,
        'range': [1, 200],
        'replacement': False,
        'resource': 'anomaly/540dfa9f9841fa5c8800076a',
        'rows': 200,
        'sample_rate': 1.0,
        'sample_size': 126,
        'seed': 'BigML',
        'shared': False,
        'size': 30549,
        'source': 'source/540dfa979841fa5c7f000363',
        'source_status': True,
        'status': {   'code': 5,
                      'elapsed': 32397,
                      'message': 'The anomaly detector has been created',
                      'progress': 1.0},
        'subscription': False,
        'tags': [],
        'updated': '2014-09-08T23:54:28.647000',
        'white_box': False}

Note that we have abbreviated the output in the snippet above for
readability: the full anomaly detector you'll get is going to contain
much more details).

The `trees` list contains the actual isolation forest, and it can be quite
large usually. That's why, this part of the resource should only be included
in downloads when needed. If you are only interested in other properties, such
as `top_anomalies`, you'll improve performance by excluding it, using the
`excluded=trees` query string in the API call:

.. code-block:: python

    anomaly = api.get_anomaly('anomaly/540dfa9f9841fa5c8800076a', \
                              query_string='excluded=trees')

Each node in an isolation tree can have multiple predicates.
For the node to be a valid branch when evaluated with a data point, all of its
predicates must be true.

You can check the anomaly detector properties at the `API documentation
<https://bigml.com/api/anomalies#an_anomaly_detector_properties>`_.

Samples
-------

To provide quick access to your row data you can create a ``sample``. Samples
are in-memory objects that can be queried for subsets of data by limiting
their size, the fields or the rows returned. The structure of a sample would
be::

Samples are not permanent objects. Once they are created, they will be
available as long as GETs are requested within periods smaller than
a pre-established TTL (Time to Live). The expiration timer of a sample is
reset every time a new GET is received.

If requested, a sample can also perform linear regression and compute
Pearson's and Spearman's correlations for either one numeric field
against all other numeric fields or between two specific numeric fields.

You can check the sample properties at the `API documentation
<https://bigml.com/api/samples#sp_sample_properties>`_.

Correlations
------------

A ``correlation`` resource contains a series of computations that reflect the
degree of dependence between the field set as objective for your predictions
and the rest of fields in your dataset. The dependence degree is obtained by
comparing the distributions in every objective and non-objective field pair,
as independent fields should have probabilistic
independent distributions. Depending on the types of the fields to compare,
the metrics used to compute the correlation degree will be:

- for numeric to numeric pairs:
  `Pearson's <https://en.wikipedia.org/wiki/Pearson_product-moment_correlation_coefficient>`_
  and `Spearman's correlation <https://en.wikipedia.org/wiki/Spearman%27s_rank_correlation_coefficient>`_
  coefficients.
- for numeric to categorical pairs:
  `One-way Analysis of Variance <https://en.wikipedia.org/wiki/One-way_analysis_of_variance>`_, with the
  categorical field as the predictor variable.
- for categorical to categorical pairs:
  `contingency table (or two-way table) <https://en.wikipedia.org/wiki/Contingency_table>`_,
  `Chi-square test of independence <https://en.wikipedia.org/wiki/Pearson%27s_chi-squared_test>`_
  , and `Cramer's V <https://en.wikipedia.org/wiki/Cram%C3%A9r%27s_V>`_
  and `Tschuprow's T <https://en.wikipedia.org/wiki/Tschuprow%27s_T>`_ coefficients.

An example of the correlation resource JSON structure is:

.. code-block:: python

    >>> from bigml.api import BigML
    >>> api = BigML()
    >>> correlation = api.create_correlation('dataset/55b7a6749841fa2500000d41')
    >>> api.ok(correlation)
    >>> api.pprint(correlation['object'])
    {   u'category': 0,
        u'clones': 0,
        u'code': 200,
        u'columns': 5,
        u'correlations': {   u'correlations': [   {   u'name': u'one_way_anova',
                                                      u'result': {   u'000000': {   u'eta_square': 0.61871,
                                                                                    u'f_ratio': 119.2645,
                                                                                    u'p_value': 0,
                                                                                    u'significant': [   True,
                                                                                                        True,
                                                                                                        True]},
                                                                     u'000001': {   u'eta_square': 0.40078,
                                                                                    u'f_ratio': 49.16004,
                                                                                    u'p_value': 0,
                                                                                    u'significant': [   True,
                                                                                                        True,
                                                                                                        True]},
                                                                     u'000002': {   u'eta_square': 0.94137,
                                                                                    u'f_ratio': 1180.16118,
                                                                                    u'p_value': 0,
                                                                                    u'significant': [   True,
                                                                                                        True,
                                                                                                        True]},
                                                                     u'000003': {   u'eta_square': 0.92888,
                                                                                    u'f_ratio': 960.00715,
                                                                                    u'p_value': 0,
                                                                                    u'significant': [   True,
                                                                                                        True,
                                                                                                        True]}}}],
                             u'fields': {   u'000000': {   u'column_number': 0,
                                                           u'datatype': u'double',
                                                           u'idx': 0,
                                                           u'name': u'sepal length',
                                                           u'optype': u'numeric',
                                                           u'order': 0,
                                                           u'preferred': True,
                                                           u'summary': {   u'bins': [   [   4.3,
                                                                                            1],
                                                                                        [   4.425,
                                                                                            4],
    ...
                                                                                        [   7.9,
                                                                                            1]],
                                                                           u'kurtosis': -0.57357,
                                                                           u'maximum': 7.9,
                                                                           u'mean': 5.84333,
                                                                           u'median': 5.8,
                                                                           u'minimum': 4.3,
                                                                           u'missing_count': 0,
                                                                           u'population': 150,
                                                                           u'skewness': 0.31175,
                                                                           u'splits': [   4.51526,
                                                                                          4.67252,
                                                                                          4.81113,
                                                                                          4.89582,
                                                                                          4.96139,
                                                                                          5.01131,
    ...
                                                                                          6.92597,
                                                                                          7.20423,
                                                                                          7.64746],
                                                                           u'standard_deviation': 0.82807,
                                                                           u'sum': 876.5,
                                                                           u'sum_squares': 5223.85,
                                                                           u'variance': 0.68569}},
                                            u'000001': {   u'column_number': 1,
                                                           u'datatype': u'double',
                                                           u'idx': 1,
                                                           u'name': u'sepal width',
                                                           u'optype': u'numeric',
                                                           u'order': 1,
                                                           u'preferred': True,
                                                           u'summary': {   u'counts': [   [   2,
                                                                                              1],
                                                                                          [   2.2,
    ...
                                            u'000004': {   u'column_number': 4,
                                                           u'datatype': u'string',
                                                           u'idx': 4,
                                                           u'name': u'species',
                                                           u'optype': u'categorical',
                                                           u'order': 4,
                                                           u'preferred': True,
                                                           u'summary': {   u'categories': [   [   u'Iris-setosa',
                                                                                                  50],
                                                                                              [   u'Iris-versicolor',
                                                                                                  50],
                                                                                              [   u'Iris-virginica',
                                                                                                  50]],
                                                                           u'missing_count': 0},
                                                           u'term_analysis': {   u'enabled': True}}},
                             u'significance_levels': [0.01, 0.05, 0.1]},
        u'created': u'2015-07-28T18:07:37.010000',
        u'credits': 0.017581939697265625,
        u'dataset': u'dataset/55b7a6749841fa2500000d41',
        u'dataset_status': True,
        u'dataset_type': 0,
        u'description': u'',
        u'excluded_fields': [],
        u'fields_meta': {   u'count': 5,
                            u'limit': 1000,
                            u'offset': 0,
                            u'query_total': 5,
                            u'total': 5},
        u'input_fields': [u'000000', u'000001', u'000002', u'000003'],
        u'locale': u'en_US',
        u'max_columns': 5,
        u'max_rows': 150,
        u'name': u"iris' dataset correlation",
        u'objective_field_details': {   u'column_number': 4,
                                        u'datatype': u'string',
                                        u'name': u'species',
                                        u'optype': u'categorical',
                                        u'order': 4},
        u'out_of_bag': False,
        u'price': 0.0,
        u'private': True,
        u'project': None,
        u'range': [1, 150],
        u'replacement': False,
        u'resource': u'correlation/55b7c4e99841fa24f20009bf',
        u'rows': 150,
        u'sample_rate': 1.0,
        u'shared': False,
        u'size': 4609,
        u'source': u'source/55b7a6729841fa24f100036a',
        u'source_status': True,
        u'status': {   u'code': 5,
                       u'elapsed': 274,
                       u'message': u'The correlation has been created',
                       u'progress': 1.0},
        u'subscription': True,
        u'tags': [],
        u'updated': u'2015-07-28T18:07:49.057000',
        u'white_box': False}

Note that the output in the snippet above has been abbreviated. As you see, the
``correlations`` attribute contains the information about each field
correlation to the objective field.

You can check the correlations properties at the `API documentation
<https://bigml.com/api/correlations#cr_correlation_properties>`_.


Statistical Tests
-----------------

A ``statisticaltest`` resource contains a series of tests
that compare the
distribution of data in each numeric field of a dataset
to certain canonical distributions,
such as the
`normal distribution <https://en.wikipedia.org/wiki/Normal_distribution>`_
or `Benford's law <https://en.wikipedia.org/wiki/Benford%27s_law>`_
distribution. Statistical test are useful in tasks such as fraud, normality,
or outlier detection.

- Fraud Detection Tests:
Benford: This statistical test performs a comparison of the distribution of
first significant digits (FSDs) of each value of the field to the Benford's
law distribution. Benford's law applies to numerical distributions spanning
several orders of magnitude, such as the values found on financial balance
sheets. It states that the frequency distribution of leading, or first
significant digits (FSD) in such distributions is not uniform.
On the contrary, lower digits like 1 and 2 occur disproportionately
often as leading significant digits. The test compares the distribution
in the field to Bendford's distribution using a Chi-square goodness-of-fit
test, and Cho-Gaines d test. If a field has a dissimilar distribution,
it may contain anomalous or fraudulent values.

- Normality tests:
These tests can be used to confirm the assumption that the data in each field
of a dataset is distributed according to a normal distribution. The results
are relevant because many statistical and machine learning techniques rely on
this assumption.
Anderson-Darling: The Anderson-Darling test computes a test statistic based on
the difference between the observed cumulative distribution function (CDF) to
that of a normal distribution. A significant result indicates that the
assumption of normality is rejected.
Jarque-Bera: The Jarque-Bera test computes a test statistic based on the third
and fourth central moments (skewness and kurtosis) of the data. Again, a
significant result indicates that the normality assumption is rejected.
Z-score: For a given sample size, the maximum deviation from the mean that
would expected in a sampling of a normal distribution can be computed based
on the 68-95-99.7 rule. This test simply reports this expected deviation and
the actual deviation observed in the data, as a sort of sanity check.

- Outlier tests:
Grubbs: When the values of a field are normally distributed, a few values may
still deviate from the mean distribution. The outlier tests reports whether
at least one value in each numeric field differs significantly from the mean
using Grubb's test for outliers. If an outlier is found, then its value will
be returned.

The JSON structure for ``statisticaltest`` resources is similar to this one:

.. code-block:: python

    >>> statistical_test = api.create_statistical_test('dataset/55b7a6749841fa2500000d41')
    >>> api.ok(statistical_test)
    True
    >>> api.pprint(statistical_test['object'])
    {   u'category': 0,
        u'clones': 0,
        u'code': 200,
        u'columns': 5,
        u'created': u'2015-07-28T18:16:40.582000',
        u'credits': 0.017581939697265625,
        u'dataset': u'dataset/55b7a6749841fa2500000d41',
        u'dataset_status': True,
        u'dataset_type': 0,
        u'description': u'',
        u'excluded_fields': [],
        u'fields_meta': {   u'count': 5,
                            u'limit': 1000,
                            u'offset': 0,
                            u'query_total': 5,
                            u'total': 5},
        u'input_fields': [u'000000', u'000001', u'000002', u'000003'],
        u'locale': u'en_US',
        u'max_columns': 5,
        u'max_rows': 150,
        u'name': u"iris' dataset test",
        u'out_of_bag': False,
        u'price': 0.0,
        u'private': True,
        u'project': None,
        u'range': [1, 150],
        u'replacement': False,
        u'resource': u'statisticaltest/55b7c7089841fa25000010ad',
        u'rows': 150,
        u'sample_rate': 1.0,
        u'shared': False,
        u'size': 4609,
        u'source': u'source/55b7a6729841fa24f100036a',
        u'source_status': True,
        u'status': {   u'code': 5,
                       u'elapsed': 302,
                       u'message': u'The test has been created',
                       u'progress': 1.0},
        u'subscription': True,
        u'tags': [],
        u'statistical_tests': {   u'ad_sample_size': 1024,
                      u'fields': {   u'000000': {   u'column_number': 0,
                                                    u'datatype': u'double',
                                                    u'idx': 0,
                                                    u'name': u'sepal length',
                                                    u'optype': u'numeric',
                                                    u'order': 0,
                                                    u'preferred': True,
                                                    u'summary': {   u'bins': [   [   4.3,
                                                                                     1],
                                                                                 [   4.425,
                                                                                     4],
    ...
                                                                                 [   7.9,
                                                                                     1]],
                                                                    u'kurtosis': -0.57357,
                                                                    u'maximum': 7.9,
                                                                    u'mean': 5.84333,
                                                                    u'median': 5.8,
                                                                    u'minimum': 4.3,
                                                                    u'missing_count': 0,
                                                                    u'population': 150,
                                                                    u'skewness': 0.31175,
                                                                    u'splits': [   4.51526,
                                                                                   4.67252,
                                                                                   4.81113,
                                                                                   4.89582,
    ...
                                                                                   7.20423,
                                                                                   7.64746],
                                                                    u'standard_deviation': 0.82807,
                                                                    u'sum': 876.5,
                                                                    u'sum_squares': 5223.85,
                                                                    u'variance': 0.68569}},
    ...
                                     u'000004': {   u'column_number': 4,
                                                    u'datatype': u'string',
                                                    u'idx': 4,
                                                    u'name': u'species',
                                                    u'optype': u'categorical',
                                                    u'order': 4,
                                                    u'preferred': True,
                                                    u'summary': {   u'categories': [   [   u'Iris-setosa',
                                                                                           50],
                                                                                       [   u'Iris-versicolor',
                                                                                           50],
                                                                                       [   u'Iris-virginica',
                                                                                           50]],
                                                                    u'missing_count': 0},
                                                    u'term_analysis': {   u'enabled': True}}},
                      u'fraud': [   {   u'name': u'benford',
                                        u'result': {   u'000000': {   u'chi_square': {   u'chi_square_value': 506.39302,
                                                                                         u'p_value': 0,
                                                                                         u'significant': [   True,
                                                                                                             True,
                                                                                                             True]},
                                                                      u'cho_gaines': {   u'd_statistic': 7.124311073683573,
                                                                                         u'significant': [   True,
                                                                                                             True,
                                                                                                             True]},
                                                                      u'distribution': [   0,
                                                                                           0,
                                                                                           0,
                                                                                           22,
                                                                                           61,
                                                                                           54,
                                                                                           13,
                                                                                           0,
                                                                                           0],
                                                                      u'negatives': 0,
                                                                      u'zeros': 0},
                                                       u'000001': {   u'chi_square': {   u'chi_square_value': 396.76556,
                                                                                         u'p_value': 0,
                                                                                         u'significant': [   True,
                                                                                                             True,
                                                                                                             True]},
                                                                      u'cho_gaines': {   u'd_statistic': 7.503503138331123,
                                                                                         u'significant': [   True,
                                                                                                             True,
                                                                                                             True]},
                                                                      u'distribution': [   0,
                                                                                           57,
                                                                                           89,
                                                                                           4,
                                                                                           0,
                                                                                           0,
                                                                                           0,
                                                                                           0,
                                                                                           0],
                                                                      u'negatives': 0,
                                                                      u'zeros': 0},
                                                       u'000002': {   u'chi_square': {   u'chi_square_value': 154.20728,
                                                                                         u'p_value': 0,
                                                                                         u'significant': [   True,
                                                                                                             True,
                                                                                                             True]},
                                                                      u'cho_gaines': {   u'd_statistic': 3.9229974017266054,
                                                                                         u'significant': [   True,
                                                                                                             True,
                                                                                                             True]},
                                                                      u'distribution': [   50,
                                                                                           0,
                                                                                           11,
                                                                                           43,
                                                                                           35,
                                                                                           11,
                                                                                           0,
                                                                                           0,
                                                                                           0],
                                                                      u'negatives': 0,
                                                                      u'zeros': 0},
                                                       u'000003': {   u'chi_square': {   u'chi_square_value': 111.4438,
                                                                                         u'p_value': 0,
                                                                                         u'significant': [   True,
                                                                                                             True,
                                                                                                             True]},
                                                                      u'cho_gaines': {   u'd_statistic': 4.103257341299901,
                                                                                         u'significant': [   True,
                                                                                                             True,
                                                                                                             True]},
                                                                      u'distribution': [   76,
                                                                                           58,
                                                                                           7,
                                                                                           7,
                                                                                           1,
                                                                                           1,
                                                                                           0,
                                                                                           0,
                                                                                           0],
                                                                      u'negatives': 0,
                                                                      u'zeros': 0}}}],
                      u'normality': [   {   u'name': u'anderson_darling',
                                            u'result': {   u'000000': {   u'p_value': 0.02252,
                                                                          u'significant': [   False,
                                                                                              True,
                                                                                              True]},
                                                           u'000001': {   u'p_value': 0.02023,
                                                                          u'significant': [   False,
                                                                                              True,
                                                                                              True]},
                                                           u'000002': {   u'p_value': 0,
                                                                          u'significant': [   True,
                                                                                              True,
                                                                                              True]},
                                                           u'000003': {   u'p_value': 0,
                                                                          u'significant': [   True,
                                                                                              True,
                                                                                              True]}}},
                                        {   u'name': u'jarque_bera',
                                            u'result': {   u'000000': {   u'p_value': 0.10615,
                                                                          u'significant': [   False,
                                                                                              False,
                                                                                              False]},
                                                           u'000001': {   u'p_value': 0.25957,
                                                                          u'significant': [   False,
                                                                                              False,
                                                                                              False]},
                                                           u'000002': {   u'p_value': 0.0009,
                                                                          u'significant': [   True,
                                                                                              True,
                                                                                              True]},
                                                           u'000003': {   u'p_value': 0.00332,
                                                                          u'significant': [   True,
                                                                                              True,
                                                                                              True]}}},
                                        {   u'name': u'z_score',
                                            u'result': {   u'000000': {   u'expected_max_z': 2.71305,
                                                                          u'max_z': 2.48369},
                                                           u'000001': {   u'expected_max_z': 2.71305,
                                                                          u'max_z': 3.08044},
                                                           u'000002': {   u'expected_max_z': 2.71305,
                                                                          u'max_z': 1.77987},
                                                           u'000003': {   u'expected_max_z': 2.71305,
                                                                          u'max_z': 1.70638}}}],
                      u'outliers': [   {   u'name': u'grubbs',
                                           u'result': {   u'000000': {   u'p_value': 1,
                                                                         u'significant': [   False,
                                                                                             False,
                                                                                             False]},
                                                          u'000001': {   u'p_value': 0.26555,
                                                                         u'significant': [   False,
                                                                                             False,
                                                                                             False]},
                                                          u'000002': {   u'p_value': 1,
                                                                         u'significant': [   False,
                                                                                             False,
                                                                                             False]},
                                                          u'000003': {   u'p_value': 1,
                                                                         u'significant': [   False,
                                                                                             False,
                                                                                             False]}}}],
                      u'significance_levels': [0.01, 0.05, 0.1]},
        u'updated': u'2015-07-28T18:17:11.829000',
        u'white_box': False}

Note that the output in the snippet above has been abbreviated. As you see, the
``statistical_tests`` attribute contains the ``fraud`, ``normality``
and ``outliers``
sections where the information for each field's distribution is stored.

You can check the statistical tests properties at the `API documentation
<https://bigml.com/api/statisticaltests#st_statistical_test_properties>`_.

Logistic Regressions
--------------------

A logistic regression is a supervised machine learning method for
solving classification problems. Each of the classes in the field
you want to predict, the objective field, is assigned a probability depending
on the values of the input fields. The probability is computed
as the value of a logistic function,
whose argument is a linear combination of the predictors' values.
You can create a logistic regression selecting which fields from your
dataset you want to use as input fields (or predictors) and which
categorical field you want to predict, the objective field. Then the
created logistic regression is defined by the set of coefficients in the
linear combination of the values. Categorical
and text fields need some prior work to be modelled using this method. They
are expanded as a set of new fields, one per category or term (respectively)
where the number of occurrences of the category or term is store. Thus,
the linear combination is made on the frequency of the categories or terms.

The JSON structure for a logistic regression is:

.. code-block:: python

    >>> api.pprint(logistic_regression['object'])
    {   u'balance_objective': False,
        u'category': 0,
        u'code': 200,
        u'columns': 5,
        u'created': u'2015-10-09T16:11:08.444000',
        u'credits': 0.017581939697265625,
        u'credits_per_prediction': 0.0,
        u'dataset': u'dataset/561304f537203f4c930001ca',
        u'dataset_field_types': {   u'categorical': 1,
                                    u'datetime': 0,
                                    u'effective_fields': 5,
                                    u'numeric': 4,
                                    u'preferred': 5,
                                    u'text': 0,
                                    u'total': 5},
        u'dataset_status': True,
        u'description': u'',
        u'excluded_fields': [],
        u'fields_meta': {   u'count': 5,
                            u'limit': 1000,
                            u'offset': 0,
                            u'query_total': 5,
                            u'total': 5},
        u'input_fields': [u'000000', u'000001', u'000002', u'000003'],
        u'locale': u'en_US',
        u'logistic_regression': {   u'bias': 1,
                                    u'c': 1,
                                    u'coefficients': [   [   u'Iris-virginica',
                                                             [   -1.7074433493289376,
                                                                 -1.533662474502423,
                                                                 2.47026986670851,
                                                                 2.5567582221085563,
                                                                 -1.2158200612711925]],
                                                         [   u'Iris-setosa',
                                                             [   0.41021712519841674,
                                                                 1.464162165246765,
                                                                 -2.26003266131107,
                                                                 -1.0210350909174153,
                                                                 0.26421852991732514]],
                                                         [   u'Iris-versicolor',
                                                             [   0.42702327817072505,
                                                                 -1.611817241669904,
                                                                 0.5763832839459982,
                                                                 -1.4069842681625884,
                                                                 1.0946877732663143]]],
                                    u'eps': 1e-05,
                                    u'fields': {   u'000000': {   u'column_number': 0,
                                                                  u'datatype': u'double',
                                                                  u'name': u'sepal length',
                                                                  u'optype': u'numeric',
                                                                  u'order': 0,
                                                                  u'preferred': True,
                                                                  u'summary': {   u'bins': [   [   4.3,
                                                                                                   1],
                                                                                               [   4.425,
                                                                                                   4],
                                                                                               [   4.6,
                                                                                                   4],
    ...
                                                                                               [   7.9,
                                                                                                   1]],
                                                                                  u'kurtosis': -0.57357,
                                                                                  u'maximum': 7.9,
                                                                                  u'mean': 5.84333,
                                                                                  u'median': 5.8,
                                                                                  u'minimum': 4.3,
                                                                                  u'missing_count': 0,
                                                                                  u'population': 150,
                                                                                  u'skewness': 0.31175,
                                                                                  u'splits': [   4.51526,
                                                                                                 4.67252,
                                                                                                 4.81113,
    ...
                                                                                                 6.92597,
                                                                                                 7.20423,
                                                                                                 7.64746],
                                                                                  u'standard_deviation': 0.82807,
                                                                                  u'sum': 876.5,
                                                                                  u'sum_squares': 5223.85,
                                                                                  u'variance': 0.68569}},
                                                   u'000001': {   u'column_number': 1,
                                                                  u'datatype': u'double',
                                                                  u'name': u'sepal width',
                                                                  u'optype': u'numeric',
                                                                  u'order': 1,
                                                                  u'preferred': True,
                                                                  u'summary': {   u'counts': [   [   2,
                                                                                                     1],
                                                                                                 [   2.2,
                                                                                                     3],
    ...
                                                                                                 [   4.2,
                                                                                                     1],
                                                                                                 [   4.4,
                                                                                                     1]],
                                                                                  u'kurtosis': 0.18098,
                                                                                  u'maximum': 4.4,
                                                                                  u'mean': 3.05733,
                                                                                  u'median': 3,
                                                                                  u'minimum': 2,
                                                                                  u'missing_count': 0,
                                                                                  u'population': 150,
                                                                                  u'skewness': 0.31577,
                                                                                  u'standard_deviation': 0.43587,
                                                                                  u'sum': 458.6,
                                                                                  u'sum_squares': 1430.4,
                                                                                  u'variance': 0.18998}},
                                                   u'000002': {   u'column_number': 2,
                                                                  u'datatype': u'double',
                                                                  u'name': u'petal length',
                                                                  u'optype': u'numeric',
                                                                  u'order': 2,
                                                                  u'preferred': True,
                                                                  u'summary': {   u'bins': [   [   1,
                                                                                                   1],
                                                                                               [   1.16667,
                                                                                                   3],
    ...
                                                                                               [   6.6,
                                                                                                   1],
                                                                                               [   6.7,
                                                                                                   2],
                                                                                               [   6.9,
                                                                                                   1]],
                                                                                  u'kurtosis': -1.39554,
                                                                                  u'maximum': 6.9,
                                                                                  u'mean': 3.758,
                                                                                  u'median': 4.35,
                                                                                  u'minimum': 1,
                                                                                  u'missing_count': 0,
                                                                                  u'population': 150,
                                                                                  u'skewness': -0.27213,
                                                                                  u'splits': [   1.25138,
                                                                                                 1.32426,
                                                                                                 1.37171,
    ...
                                                                                                 6.02913,
                                                                                                 6.38125],
                                                                                  u'standard_deviation': 1.7653,
                                                                                  u'sum': 563.7,
                                                                                  u'sum_squares': 2582.71,
                                                                                  u'variance': 3.11628}},
                                                   u'000003': {   u'column_number': 3,
                                                                  u'datatype': u'double',
                                                                  u'name': u'petal width',
                                                                  u'optype': u'numeric',
                                                                  u'order': 3,
                                                                  u'preferred': True,
                                                                  u'summary': {   u'counts': [   [   0.1,
                                                                                                     5],
                                                                                                 [   0.2,
                                                                                                     29],
    ...
                                                                                                 [   2.4,
                                                                                                     3],
                                                                                                 [   2.5,
                                                                                                     3]],
                                                                                  u'kurtosis': -1.33607,
                                                                                  u'maximum': 2.5,
                                                                                  u'mean': 1.19933,
                                                                                  u'median': 1.3,
                                                                                  u'minimum': 0.1,
                                                                                  u'missing_count': 0,
                                                                                  u'population': 150,
                                                                                  u'skewness': -0.10193,
                                                                                  u'standard_deviation': 0.76224,
                                                                                  u'sum': 179.9,
                                                                                  u'sum_squares': 302.33,
                                                                                  u'variance': 0.58101}},
                                                   u'000004': {   u'column_number': 4,
                                                                  u'datatype': u'string',
                                                                  u'name': u'species',
                                                                  u'optype': u'categorical',
                                                                  u'order': 4,
                                                                  u'preferred': True,
                                                                  u'summary': {   u'categories': [   [   u'Iris-setosa',
                                                                                                         50],
                                                                                                     [   u'Iris-versicolor',
                                                                                                         50],
                                                                                                     [   u'Iris-virginica',
                                                                                                         50]],
                                                                                  u'missing_count': 0},
                                                                  u'term_analysis': {   u'enabled': True}}},
                                    u'normalize': False,
                                    u'regularization': u'l2'},
        u'max_columns': 5,
        u'max_rows': 150,
        u'name': u"iris' dataset's logistic regression",
        u'number_of_batchpredictions': 0,
        u'number_of_evaluations': 0,
        u'number_of_predictions': 1,
        u'objective_field': u'000004',
        u'objective_field_name': u'species',
        u'objective_field_type': u'categorical',
        u'objective_fields': [u'000004'],
        u'out_of_bag': False,
        u'private': True,
        u'project': u'project/561304c137203f4c9300016c',
        u'range': [1, 150],
        u'replacement': False,
        u'resource': u'logisticregression/5617e71c37203f506a000001',
        u'rows': 150,
        u'sample_rate': 1.0,
        u'shared': False,
        u'size': 4609,
        u'source': u'source/561304f437203f4c930001c3',
        u'source_status': True,
        u'status': {   u'code': 5,
                       u'elapsed': 86,
                       u'message': u'The logistic regression has been created',
                       u'progress': 1.0},
        u'subscription': False,
        u'tags': [u'species'],
        u'updated': u'2015-10-09T16:14:02.336000',
        u'white_box': False}

Note that the output in the snippet above has been abbreviated. As you see,
the ``logistic_regression`` attribute stores the coefficients used in the
logistic function as well as the configuration parameters described in
the `developers section
<https://bigml.com/api/logisticregressions#lr_logistic_regression_properties>`_ .


Linear Regressions
------------------

A linear regression is a supervised machine learning method for
solving regression problems by computing the objective as a linear
combination of factors. The implementation is a multiple linear regression
that models the output as a linear combination of the predictors.
The coefficients are estimated doing a least-squares fit on the training data.

As a linear combination can only be done using numeric values, non-numeric
fields need to be transformed to numeric ones following some rules:

- Categorical fields will be encoded and each class appearance in input data
  will convey a different contribution to the input vector.
- Text and items fields will be expanded to several numeric predictors,
  each one indicating the number of occurences for a specific term.
  Text fields without term analysis are excluded from the model.

Therefore, the initial input data is transformed into an input vector with one
or may components per field. Also, if a field in the training data contains
missing data, the components corresponding to that field will include an
additional 1 or 0 value depending on whether the field is missing in the
input data or not.

The JSON structure for a linear regression is:

.. code-block:: python

    >>> api.pprint(linear_regression["object"])
    {   u'category': 0,
        u'code': 200,
        u'columns': 4,
        u'composites': None,
        u'configuration': None,
        u'configuration_status': False,
        u'created': u'2019-02-20T21:02:40.027000',
        u'creator': u'merce',
        u'credits': 0.0,
        u'credits_per_prediction': 0.0,
        u'dataset': u'dataset/5c6dc06a983efc18e2000084',
        u'dataset_field_types': {   u'categorical': 0,
                                    u'datetime': 0,
                                    u'items': 0,
                                    u'numeric': 6,
                                    u'preferred': 6,
                                    u'text': 0,
                                    u'total': 6},
        u'dataset_status': True,
        u'datasets': [],
        u'default_numeric_value': None,
        u'description': u'',
        u'excluded_fields': [],
        u'execution_id': None,
        u'execution_status': None,
        u'fields_maps': None,
        u'fields_meta': {   u'count': 4,
                            u'limit': 1000,
                            u'offset': 0,
                            u'query_total': 4,
                            u'total': 4},
        u'fusions': None,
        u'input_fields': [u'000000', u'000001', u'000002'],
        u'linear_regression': {   u'bias': True,
                                  u'coefficients': [   [-1.88196],
                                                       [0.475633],
                                                       [0.122468],
                                                       [30.9141]],
                                  u'fields': {   u'000000': {   u'column_number': 0,
                                                                u'datatype': u'int8',
                                                                u'name': u'Prefix',
                                                                u'optype': u'numeric',
                                                                u'order': 0,
                                                                u'preferred': True,
                                                                u'summary': {   u'counts': [   [   4,
                                                                                                   1],

                                    ...
                                  u'stats': {   u'confidence_intervals': [   [   5.63628],
                                                                             [   0.375062],
                                                                             [   0.348577],
                                                                             [   44.4112]],
                                                u'mean_squared_error': 342.206,
                                                u'number_of_parameters': 4,
                                                u'number_of_samples': 77,
                                                u'p_values': [   [0.512831],
                                                                 [0.0129362],
                                                                 [0.491069],
                                                                 [0.172471]],
                                                u'r_squared': 0.136672,
                                                u'standard_errors': [   [   2.87571],
                                                                        [   0.191361],
                                                                        [   0.177849],
                                                                        [   22.6592]],
                                                u'sum_squared_errors': 24981,
                                                u'xtx': [   [   4242,
                                                                48396.9,
                                                                51273.97,
                                                                568],
                                                            [   48396.9,
                                                                570177.6584,
                                                                594274.3274,
                                                                6550.52],
                                                            [   51273.97,
                                                                594274.3274,
                                                                635452.7068,
                                                                6894.24],
                                                            [   568,
                                                                6550.52,
                                                                6894.24,
                                                                77]],
                                                u'z_scores': [   [-0.654436],
                                                                 [2.48552],
                                                                 [0.688609],
                                                                 [1.36431]]}},
        u'locale': u'en_US',
        u'max_columns': 6,
        u'max_rows': 80,
        u'name': u'grades',
        u'name_options': u'bias',
        u'number_of_batchpredictions': 0,
        u'number_of_evaluations': 0,
        u'number_of_predictions': 2,
        u'number_of_public_predictions': 0,
        u'objective_field': u'000005',
        u'objective_field_name': u'Final',
        u'objective_field_type': u'numeric',
        u'objective_fields': [u'000005'],
        u'operating_point': {   },
        u'optiml': None,
        u'optiml_status': False,
        u'ordering': 0,
        u'out_of_bag': False,
        u'out_of_bags': None,
        u'price': 0.0,
        u'private': True,
        u'project': u'project/5c6dc062983efc18d5000129',
        u'range': None,
        u'ranges': None,
        u'replacement': False,
        u'replacements': None,
        u'resource': u'linearregression/5c6dc070983efc18e00001f1',
        u'rows': 80,
        u'sample_rate': 1.0,
        u'sample_rates': None,
        u'seed': None,
        u'seeds': None,
        u'shared': False,
        u'size': 2691,
        u'source': u'source/5c6dc064983efc18e00001ed',
        u'source_status': True,
        u'status': {   u'code': 5,
                       u'elapsed': 62086,
                       u'message': u'The linear regression has been created',
                       u'progress': 1},
        u'subscription': True,
        u'tags': [],
        u'type': 0,
        u'updated': u'2019-02-27T18:01:18.539000',
        u'user_metadata': {   },
        u'webhook': None,
        u'weight_field': None,
        u'white_box': False}

Note that the output in the snippet above has been abbreviated. As you see,
the ``linear_regression`` attribute stores the coefficients used in the
linear function as well as the configuration parameters described in
the `developers section <https://bigml.com/api/linearregressions>`_ .


Associations
------------

Association Discovery is a popular method to find out relations among values
in high-dimensional datasets.

A common case where association discovery is often used is
market basket analysis. This analysis seeks for customer shopping
patterns across large transactional
datasets. For instance, do customers who buy hamburgers and ketchup also
consume bread?

Businesses use those insights to make decisions on promotions and product
placements.
Association Discovery can also be used for other purposes such as early
incident detection, web usage analysis, or software intrusion detection.

In BigML, the Association resource object can be built from any dataset, and
its results are a list of association rules between the items in the dataset.
In the example case, the corresponding
association rule would have hamburguers and ketchup as the items at the
left hand side of the association rule and bread would be the item at the
right hand side. Both sides in this association rule are related,
in the sense that observing
the items in the left hand side implies observing the items in the right hand
side. There are some metrics to ponder the quality of these association rules:

- Support: the proportion of instances which contain an itemset.

For an association rule, it means the number of instances in the dataset which
contain the rule's antecedent and rule's consequent together
over the total number of instances (N) in the dataset.

It gives a measure of the importance of the rule. Association rules have
to satisfy a minimum support constraint (i.e., min_support).

- Coverage: the support of the antedecent of an association rule.
It measures how often a rule can be applied.

- Confidence or (strength): The probability of seeing the rule's consequent
under the condition that the instances also contain the rule's antecedent.
Confidence is computed using the support of the association rule over the
coverage. That is, the percentage of instances which contain the consequent
and antecedent together over the number of instances which only contain
the antecedent.

Confidence is directed and gives different values for the association
rules Antecedent → Consequent and Consequent → Antecedent. Association
rules also need to satisfy a minimum confidence constraint
(i.e., min_confidence).

- Leverage: the difference of the support of the association
rule (i.e., the antecedent and consequent appearing together) and what would
be expected if antecedent and consequent where statistically independent.
This is a value between -1 and 1. A positive value suggests a positive
relationship and a negative value suggests a negative relationship.
0 indicates independence.

Lift: how many times more often antecedent and consequent occur together
than expected if they where statistically independent.
A value of 1 suggests that there is no relationship between the antecedent
and the consequent. Higher values suggest stronger positive relationships.
Lower values suggest stronger negative relationships (the presence of the
antecedent reduces the likelihood of the consequent)

As to the items used in association rules, each type of field is parsed to
extract items for the rules as follows:

- Categorical: each different value (class) will be considered a separate item.
- Text: each unique term will be considered a separate item.
- Items: each different item in the items summary will be considered.
- Numeric: Values will be converted into categorical by making a
segmentation of the values.
For example, a numeric field with values ranging from 0 to 600 split
into 3 segments:
segment 1 → [0, 200), segment 2 → [200, 400), segment 3 → [400, 600].
You can refine the behavior of the transformation using
`discretization <https://bigml.com/api/associations#ad_create_discretization>`_
and `field_discretizations <https://bigml.com/api/associations#ad_create_field_discretizations>`_.

The JSON structure for an association resource is:

.. code-block:: python


    >>> api.pprint(association['object'])
    {
        "associations":{
            "complement":false,
            "discretization":{
                "pretty":true,
                "size":5,
                "trim":0,
                "type":"width"
            },
            "items":[
                {
                    "complement":false,
                    "count":32,
                    "field_id":"000000",
                    "name":"Segment 1",
                    "bin_end":5,
                    "bin_start":null
                },
                {
                    "complement":false,
                    "count":49,
                    "field_id":"000000",
                    "name":"Segment 3",
                    "bin_end":7,
                    "bin_start":6
                },
                {
                    "complement":false,
                    "count":12,
                    "field_id":"000000",
                    "name":"Segment 4",
                    "bin_end":null,
                    "bin_start":7
                },
                {
                    "complement":false,
                    "count":19,
                    "field_id":"000001",
                    "name":"Segment 1",
                    "bin_end":2.5,
                    "bin_start":null
                },
                ...
                {
                    "complement":false,
                    "count":50,
                    "field_id":"000004",
                    "name":"Iris-versicolor"
                },
                {
                    "complement":false,
                    "count":50,
                    "field_id":"000004",
                    "name":"Iris-virginica"
                }
            ],
            "max_k": 100,
            "min_confidence":0,
            "min_leverage":0,
            "min_lift":1,
            "min_support":0,
            "rules":[
                {
                    "confidence":1,
                    "id":"000000",
                    "leverage":0.22222,
                    "lhs":[
                        13
                    ],
                    "lhs_cover":[
                        0.33333,
                        50
                    ],
                    "lift":3,
                    "p_value":0.000000000,
                    "rhs":[
                        6
                    ],
                    "rhs_cover":[
                        0.33333,
                        50
                    ],
                    "support":[
                        0.33333,
                        50
                    ]
                },
                {
                    "confidence":1,
                    "id":"000001",
                    "leverage":0.22222,
                    "lhs":[
                        6
                    ],
                    "lhs_cover":[
                        0.33333,
                        50
                    ],
                    "lift":3,
                    "p_value":0.000000000,
                    "rhs":[
                        13
                    ],
                    "rhs_cover":[
                        0.33333,
                        50
                    ],
                    "support":[
                        0.33333,
                        50
                    ]
                },
                ...
                {
                    "confidence":0.26,
                    "id":"000029",
                    "leverage":0.05111,
                    "lhs":[
                        13
                    ],
                    "lhs_cover":[
                        0.33333,
                        50
                    ],
                    "lift":2.4375,
                    "p_value":0.0000454342,
                    "rhs":[
                        5
                    ],
                    "rhs_cover":[
                        0.10667,
                        16
                    ],
                    "support":[
                        0.08667,
                        13
                    ]
                },
                {
                    "confidence":0.18,
                    "id":"00002a",
                    "leverage":0.04,
                    "lhs":[
                        15
                    ],
                    "lhs_cover":[
                        0.33333,
                        50
                    ],
                    "lift":3,
                    "p_value":0.0000302052,
                    "rhs":[
                        9
                    ],
                    "rhs_cover":[
                        0.06,
                        9
                    ],
                    "support":[
                        0.06,
                        9
                    ]
                },
                {
                    "confidence":1,
                    "id":"00002b",
                    "leverage":0.04,
                    "lhs":[
                        9
                    ],
                    "lhs_cover":[
                        0.06,
                        9
                    ],
                    "lift":3,
                    "p_value":0.0000302052,
                    "rhs":[
                        15
                    ],
                    "rhs_cover":[
                        0.33333,
                        50
                    ],
                    "support":[
                        0.06,
                        9
                    ]
                }
            ],
            "rules_summary":{
                "confidence":{
                    "counts":[
                        [
                            0.18,
                            1
                        ],
                        [
                            0.24,
                            1
                        ],
                        [
                            0.26,
                            2
                        ],
                        ...
                        [
                            0.97959,
                            1
                        ],
                        [
                            1,
                            9
                        ]
                    ],
                    "maximum":1,
                    "mean":0.70986,
                    "median":0.72864,
                    "minimum":0.18,
                    "population":44,
                    "standard_deviation":0.24324,
                    "sum":31.23367,
                    "sum_squares":24.71548,
                    "variance":0.05916
                },
                "k":44,
                "leverage":{
                    "counts":[
                        [
                            0.04,
                            2
                        ],
                        [
                            0.05111,
                            4
                        ],
                        [
                            0.05316,
                            2
                        ],
                        ...
                        [
                            0.22222,
                            2
                        ]
                    ],
                    "maximum":0.22222,
                    "mean":0.10603,
                    "median":0.10156,
                    "minimum":0.04,
                    "population":44,
                    "standard_deviation":0.0536,
                    "sum":4.6651,
                    "sum_squares":0.61815,
                    "variance":0.00287
                },
                "lhs_cover":{
                    "counts":[
                        [
                            0.06,
                            2
                        ],
                        [
                            0.08,
                            2
                        ],
                        [
                            0.10667,
                            4
                        ],
                        [
                            0.12667,
                            1
                        ],
                        ...
                        [
                            0.5,
                            4
                        ]
                    ],
                    "maximum":0.5,
                    "mean":0.29894,
                    "median":0.33213,
                    "minimum":0.06,
                    "population":44,
                    "standard_deviation":0.13386,
                    "sum":13.15331,
                    "sum_squares":4.70252,
                    "variance":0.01792
                },
                "lift":{
                    "counts":[
                        [
                            1.40625,
                            2
                        ],
                        [
                            1.5067,
                            2
                        ],
                        ...
                        [
                            2.63158,
                            4
                        ],
                        [
                            3,
                            10
                        ],
                        [
                            4.93421,
                            2
                        ],
                        [
                            12.5,
                            2
                        ]
                    ],
                    "maximum":12.5,
                    "mean":2.91963,
                    "median":2.58068,
                    "minimum":1.40625,
                    "population":44,
                    "standard_deviation":2.24641,
                    "sum":128.46352,
                    "sum_squares":592.05855,
                    "variance":5.04635
                },
                "p_value":{
                    "counts":[
                        [
                            0.000000000,
                            2
                        ],
                        [
                            0.000000000,
                            4
                        ],
                        [
                            0.000000000,
                            2
                        ],
                        ...
                        [
                            0.0000910873,
                            2
                        ]
                    ],
                    "maximum":0.0000910873,
                    "mean":0.0000106114,
                    "median":0.00000000,
                    "minimum":0.000000000,
                    "population":44,
                    "standard_deviation":0.0000227364,
                    "sum":0.000466903,
                    "sum_squares":0.0000000,
                    "variance":0.000000001
                },
                "rhs_cover":{
                    "counts":[
                        [
                            0.06,
                            2
                        ],
                        [
                            0.08,
                            2
                        ],
                        ...
                        [
                            0.42667,
                            2
                        ],
                        [
                            0.46667,
                            3
                        ],
                        [
                            0.5,
                            4
                        ]
                    ],
                    "maximum":0.5,
                    "mean":0.29894,
                    "median":0.33213,
                    "minimum":0.06,
                    "population":44,
                    "standard_deviation":0.13386,
                    "sum":13.15331,
                    "sum_squares":4.70252,
                    "variance":0.01792
                },
                "support":{
                    "counts":[
                        [
                            0.06,
                            4
                        ],
                        [
                            0.06667,
                            2
                        ],
                        [
                            0.08,
                            2
                        ],
                        [
                            0.08667,
                            4
                        ],
                        [
                            0.10667,
                            4
                        ],
                        [
                            0.15333,
                            2
                        ],
                        [
                            0.18667,
                            4
                        ],
                        [
                            0.19333,
                            2
                        ],
                        [
                            0.20667,
                            2
                        ],
                        [
                            0.27333,
                            2
                        ],
                        [
                            0.28667,
                            2
                        ],
                        [
                            0.3,
                            4
                        ],
                        [
                            0.32,
                            2
                        ],
                        [
                            0.33333,
                            6
                        ],
                        [
                            0.37333,
                            2
                        ]
                    ],
                    "maximum":0.37333,
                    "mean":0.20152,
                    "median":0.19057,
                    "minimum":0.06,
                    "population":44,
                    "standard_deviation":0.10734,
                    "sum":8.86668,
                    "sum_squares":2.28221,
                    "variance":0.01152
                }
            },
            "search_strategy":"leverage",
            "significance_level":0.05
        },
        "category":0,
        "clones":0,
        "code":200,
        "columns":5,
        "created":"2015-11-05T08:06:08.184000",
        "credits":0.017581939697265625,
        "dataset":"dataset/562fae3f4e1727141d00004e",
        "dataset_status":true,
        "dataset_type":0,
        "description":"",
        "excluded_fields":[ ],
        "fields_meta":{
            "count":5,
            "limit":1000,
            "offset":0,
            "query_total":5,
            "total":5
        },
        "input_fields":[
            "000000",
            "000001",
            "000002",
            "000003",
            "000004"
        ],
        "locale":"en_US",
        "max_columns":5,
        "max_rows":150,
        "name":"iris' dataset's association",
        "out_of_bag":false,
        "price":0,
        "private":true,
        "project":null,
        "range":[
            1,
            150
        ],
        "replacement":false,
        "resource":"association/5621b70910cb86ae4c000000",
        "rows":150,
        "sample_rate":1,
        "shared":false,
        "size":4609,
        "source":"source/562fae3a4e1727141d000048",
        "source_status":true,
        "status":{
            "code":5,
            "elapsed":1072,
            "message":"The association has been created",
            "progress":1
        },
        "subscription":false,
        "tags":[ ],
        "updated":"2015-11-05T08:06:20.403000",
        "white_box":false
    }
Note that the output in the snippet above has been abbreviated. As you see,
the ``associations`` attribute stores items, rules and metrics extracted
from the datasets as well as the configuration parameters described in
the `developers section <https://bigml.com/api/associations>`_ .


Topic Models
------------

A topic model is an unsupervised machine learning method
for unveiling all the different topics
underlying a collection of documents.
BigML uses Latent Dirichlet Allocation (LDA), one of the most popular
probabilistic methods for topic modeling.
In BigML, each instance (i.e. each row in your dataset) will
be considered a document and the contents of all the text fields
given as inputs will be automatically concatenated and considered the
document bag of words.

Topic model is based on the assumption that any document
exhibits a mixture of topics. Each topic is composed of a set of words
which are thematically related. The words from a given topic have different
probabilities for that topic. At the same time, each word can be attributable
to one or several topics. So for example the word "sea" may be found in
a topic related with sea transport but also in a topic related to holidays.
Topic model automatically discards stop words and high
frequency words.

Topic model's main applications include browsing, organizing and understanding
large archives of documents. It can been applied for information retrieval,
collaborative filtering, assessing document similarity among others.
The topics found in the dataset can also be very useful new features
before applying other models like classification, clustering, or
anomaly detection.

The JSON structure for a topic model is:

.. code-block:: python

    >>> api.pprint(topic['object'])
    {   u'category': 0,
        u'code': 200,
        u'columns': 1,
        u'configuration': None,
        u'configuration_status': False,
        u'created': u'2016-11-23T23:47:54.703000',
        u'credits': 0.0,
        u'credits_per_prediction': 0.0,
        u'dataset': u'dataset/58362aa0983efc45a0000005',
        u'dataset_field_types': {   u'categorical': 1,
                                    u'datetime': 0,
                                    u'effective_fields': 672,
                                    u'items': 0,
                                    u'numeric': 0,
                                    u'preferred': 2,
                                    u'text': 1,
                                    u'total': 2},
        u'dataset_status': True,
        u'dataset_type': 0,
        u'description': u'',
        u'excluded_fields': [],
        u'fields_meta': {   u'count': 1,
                            u'limit': 1000,
                            u'offset': 0,
                            u'query_total': 1,
                            u'total': 1},
        u'input_fields': [u'000001'],
        u'locale': u'en_US',
        u'max_columns': 2,
        u'max_rows': 656,
        u'name': u"spam dataset's Topic Model ",
        u'number_of_batchtopicdistributions': 0,
        u'number_of_public_topicdistributions': 0,
        u'number_of_topicdistributions': 0,
        u'ordering': 0,
        u'out_of_bag': False,
        u'price': 0.0,
        u'private': True,
        u'project': None,
        u'range': [1, 656],
        u'replacement': False,
        u'resource': u'topicmodel/58362aaa983efc45a1000007',
        u'rows': 656,
        u'sample_rate': 1.0,
        u'shared': False,
        u'size': 54740,
        u'source': u'source/58362a69983efc459f000001',
        u'source_status': True,
        u'status': {   u'code': 5,
                       u'elapsed': 3222,
                       u'message': u'The topic model has been created',
                       u'progress': 1.0},
        u'subscription': True,
        u'tags': [],
        u'topic_model': {   u'alpha': 4.166666666666667,
                            u'beta': 0.1,
                            u'bigrams': False,
                            u'case_sensitive': False,
                            u'fields': {   u'000001': {   u'column_number': 1,
                                                          u'datatype': u'string',
                                                          u'name': u'Message',
                                                          u'optype': u'text',
                                                          u'order': 0,
                                                          u'preferred': True,
                                                          u'summary': {   u'average_length': 78.14787,
                                                                          u'missing_count': 0,
                                                                          u'tag_cloud': [   [   u'call',
                                                                                                72],
                                                                                            [   u'ok',
                                                                                                36],
                                                                                            [   u'gt',
                                                                                                34],
    ...
                                                                                            [   u'worse',
                                                                                                2],
                                                                                            [   u'worth',
                                                                                                2],
                                                                                            [   u'write',
                                                                                                2],
                                                                                            [   u'yest',
                                                                                                2],
                                                                                            [   u'yijue',
                                                                                                2]],
                                                                          u'term_forms': {   }},
                                                          u'term_analysis': {   u'case_sensitive': False,
                                                                                u'enabled': True,
                                                                                u'language': u'en',
                                                                                u'stem_words': False,
                                                                                u'token_mode': u'all',
                                                                                u'use_stopwords': False}}},
                            u'hashed_seed': 62146850,
                            u'language': u'en',
                            u'number_of_topics': 12,
                            u'term_limit': 4096,
                            u'term_topic_assignments': [   [   0,
                                                               5,
                                                               0,
                                                               1,
                                                               0,
                                                               19,
                                                               0,
                                                               0,
                                                               19,
                                                               0,
                                                               1,
                                                               0],
                                                           [   0,
                                                               0,
                                                               0,
                                                               13,
                                                               0,
                                                               0,
                                                               0,
                                                               0,
                                                               5,
                                                               0,
                                                               0,
                                                               0],
    ...
                                                           [   0,
                                                               7,
                                                               27,
                                                               0,
                                                               112,
                                                               0,
                                                               0,
                                                               0,
                                                               0,
                                                               0,
                                                               14,
                                                               2]],
                            u'termset': [   u'000',
                                            u'03',
                                            u'04',
                                            u'06',
                                            u'08000839402',
                                            u'08712460324',
    ...

                                            u'yes',
                                            u'yest',
                                            u'yesterday',
                                            u'yijue',
                                            u'yo',
                                            u'yr',
                                            u'yup',
                                            u'\xfc'],
                            u'top_n_terms': 10,
                            u'topicmodel_seed': u'26c386d781963ca1ea5c90dab8a6b023b5e1d180',
                            u'topics': [   {   u'id': u'000000',
                                               u'name': u'Topic 00',
                                               u'probability': 0.09375,
                                               u'top_terms': [   [   u'im',
                                                                     0.04849],
                                                                 [   u'hi',
                                                                     0.04717],
                                                                 [   u'love',
                                                                     0.04585],
                                                                 [   u'please',
                                                                     0.02867],
                                                                 [   u'tomorrow',
                                                                     0.02867],
                                                                 [   u'cos',
                                                                     0.02823],
                                                                 [   u'sent',
                                                                     0.02647],
                                                                 [   u'da',
                                                                     0.02383],
                                                                 [   u'meet',
                                                                     0.02207],
                                                                 [   u'dinner',
                                                                     0.01898]]},
                                           {   u'id': u'000001',
                                               u'name': u'Topic 01',
                                               u'probability': 0.08215,
                                               u'top_terms': [   [   u'lt',
                                                                     0.1015],
                                                                 [   u'gt',
                                                                     0.1007],
                                                                 [   u'wish',
                                                                     0.03958],
                                                                 [   u'feel',
                                                                     0.0272],
                                                                 [   u'shit',
                                                                     0.02361],
                                                                 [   u'waiting',
                                                                     0.02281],
                                                                 [   u'stuff',
                                                                     0.02001],
                                                                 [   u'name',
                                                                     0.01921],
                                                                 [   u'comp',
                                                                     0.01522],
                                                                 [   u'forgot',
                                                                     0.01482]]},
    ...
                                           {   u'id': u'00000b',
                                               u'name': u'Topic 11',
                                               u'probability': 0.0826,
                                               u'top_terms': [   [   u'call',
                                                                     0.15084],
                                                                 [   u'min',
                                                                     0.05003],
                                                                 [   u'msg',
                                                                     0.03185],
                                                                 [   u'home',
                                                                     0.02648],
                                                                 [   u'mind',
                                                                     0.02152],
                                                                 [   u'lt',
                                                                     0.01987],
                                                                 [   u'bring',
                                                                     0.01946],
                                                                 [   u'camera',
                                                                     0.01905],
                                                                 [   u'set',
                                                                     0.01905],
                                                                 [   u'contact',
                                                                     0.01781]]}],
                            u'use_stopwords': False},
        u'updated': u'2016-11-23T23:48:03.336000',
        u'white_box': False}

Note that the output in the snippet above has been abbreviated.


The topic model returns a list of top terms for each topic found in the data.
Note that topics are not labeled, so you have to infer their meaning according
to the words they are composed of.

Once you build the topic model you can calculate each topic probability
for a given document by using Topic Distribution.
This information can be useful to find documents similarities based
on their thematic.

As you see,
the ``topic_model`` attribute stores the topics and termset and term to
topic assignment,
as well as the configuration parameters described in
the `developers section <https://bigml.com/api/topicmodels>`_ .


Time Series
-----------

A time series model is a supervised learning method to forecast the future
values of a field based on its previously observed values.
It is used to analyze time based data when historical patterns can explain
the future behavior such as stock prices, sales forecasting,
website traffic, production and inventory analysis, weather forecasting, etc.
A time series model needs to be trained with time series data,
i.e., a field containing a sequence of equally distributed data points in time.

BigML implements exponential smoothing to train time series models.
Time series data is modeled as a level component and it can optionally
include a trend (damped or not damped) and a seasonality
components. You can learn more about how to include these components and their
use in the `API documentation page <https://bigml.io/api/>`_.

You can create a time series model selecting one or several fields from
your dataset, that will be the ojective fields. The forecast will compute
their future values.


The JSON structure for a time series is:

.. code-block:: python

    >>> api.pprint(time_series['object'])
    {   u'category': 0,
        u'clones': 0,
        u'code': 200,
        u'columns': 1,
        u'configuration': None,
        u'configuration_status': False,
        u'created': u'2017-07-15T12:49:42.601000',
        u'credits': 0.0,
        u'dataset': u'dataset/5968ec42983efc21b0000016',
        u'dataset_field_types': {   u'categorical': 0,
                                    u'datetime': 0,
                                    u'effective_fields': 6,
                                    u'items': 0,
                                    u'numeric': 6,
                                    u'preferred': 6,
                                    u'text': 0,
                                    u'total': 6},
        u'dataset_status': True,
        u'dataset_type': 0,
        u'description': u'',
        u'fields_meta': {   u'count': 1,
                            u'limit': 1000,
                            u'offset': 0,
                            u'query_total': 1,
                            u'total': 1},
        u'forecast': {   u'000005': [   {   u'lower_bound': [   30.14111,
                                                                30.14111,
                                                                ...
                                                                30.14111],
                                            u'model': u'A,N,N',
                                            u'point_forecast': [   68.53181,
                                                                   68.53181,
                                                                   ...
                                                                   68.53181,
                                                                   68.53181],
                                            u'time_range': {   u'end': 129,
                                                               u'interval': 1,
                                                               u'interval_unit': u'milliseconds',
                                                               u'start': 80},
                                            u'upper_bound': [   106.92251,
                                                                106.92251,
                                                                ...
                                                                106.92251,
                                                                106.92251]},
                                        {   u'lower_bound': [   35.44118,
                                                                35.5032,
                                                                ...
                                                                35.28083],
                                            u'model': u'A,Ad,N',
                            ...
                                                                   66.83537,
                                                                   66.9465],
                                            u'time_range': {   u'end': 129,
                                                               u'interval': 1,
                                                               u'interval_unit': u'milliseconds',
                                                               u'start': 80}}]},
        u'horizon': 50,
        u'locale': u'en_US',
        u'max_columns': 6,
        u'max_rows': 80,
        u'name': u'my_ts_data',
        u'name_options': u'period=1, range=[1, 80]',
        u'number_of_evaluations': 0,
        u'number_of_forecasts': 0,
        u'number_of_public_forecasts': 0,
        u'objective_field': u'000005',
        u'objective_field_name': u'Final',
        u'objective_field_type': u'numeric',
        u'objective_fields': [u'000005'],
        u'objective_fields_names': [u'Final'],
        u'price': 0.0,
        u'private': True,
        u'project': None,
        u'range': [1, 80],
        u'resource': u'timeseries/596a0f66983efc53f3000000',
        u'rows': 80,
        u'shared': False,
        u'short_url': u'',
        u'size': 2691,
        u'source': u'source/5968ec3c983efc218c000006',
        u'source_status': True,
        u'status': {   u'code': 5,
                       u'elapsed': 8358,
                       u'message': u'The time series has been created',
                       u'progress': 1.0},
        u'subscription': True,
        u'tags': [],
        u'time_series': {   u'all_numeric_objectives': False,
                            u'datasets': {   u'000005': u'dataset/596a0f70983efc53f3000003'},
                            u'ets_models': {   u'000005': [   {   u'aic': 831.30903,
                                                                  u'aicc': 831.84236,
                                                                  u'alpha': 0.00012,
                                                                  u'beta': 0,
                                                                  u'bic': 840.83713,
                                                                  u'final_state': {   u'b': 0,
                                                                                      u'l': 68.53181,
                                                                                      u's': [   0]},
                                                                  u'gamma': 0,
                                                                  u'initial_state': {   u'b': 0,
                                                                                        u'l': 68.53217,
                                                                                        u's': [   0]},
                                                                  u'name': u'A,N,N',
                                                                  u'period': 1,
                                                                  u'phi': 1,
                                                                  u'r_squared': -0.0187,
                                                                  u'sigma': 19.19535},
                                                              {   u'aic': 834.43049,
                                                                  ...
                                                                  u'slope': 0.11113,
                                                                  u'value': 61.39}]},
                            u'fields': {   u'000005': {   u'column_number': 5,
                                                          u'datatype': u'double',
                                                          u'name': u'Final',
                                                          u'optype': u'numeric',
                                                          u'order': 0,
                                                          u'preferred': True,
                                                          u'summary': {   u'bins': [   [   28.06,
                                                                                           1],
                                                                                       [   34.44,
                                                                                        ...
                                                                                       [   108.335,
                                                                                           2]],
                                                                          ...
                                                                          u'sum_squares': 389814.3944,
                                                                          u'variance': 380.73315}}},
                            u'period': 1,
                            u'time_range': {   u'end': 79,
                                               u'interval': 1,
                                               u'interval_unit': u'milliseconds',
                                               u'start': 0}},
        u'type': 0,
        u'updated': u'2017-07-15T12:49:52.549000',
        u'white_box': False}


You can check the time series properties at the `API documentation
<https://bigml.com/api/timeseries#ts_time_series_properties>`_.



OptiMLs
-------

An OptiML is the result of an automated optimization process to find the
best model (type and configuration) to solve a particular
classification or regression problem.

The selection process automates the usual time-consuming task of trying
different models and parameters and evaluating their results to find the
best one. Using the OptiML, non-experts can build top-performing models.

You can create an OptiML selecting the ojective field to be predicted, the
evaluation metric to be used to rank the models tested in the process and
a maximum time for the task to be run.

The JSON structure for an OptiML is:

.. code-block:: python

    >>> api.pprint(optiml["object"])
    {   u'category': 0,
        u'code': 200,
        u'configuration': None,
        u'configuration_status': False,
        u'created': u'2018-05-17T20:23:00.060000',
        u'creator': u'mmartin',
        u'dataset': u'dataset/5afdb7009252732d930009e8',
        u'dataset_status': True,
        u'datasets': [   u'dataset/5afde6488bf7d551ee00081c',
                         u'dataset/5afde6488bf7d551fd00511f',
                         u'dataset/5afde6488bf7d551fe002e0f',
                            ...
                         u'dataset/5afde64d8bf7d551fd00512e'],
        u'description': u'',
        u'evaluations': [   u'evaluation/5afde65c8bf7d551fd00514c',
                            u'evaluation/5afde65c8bf7d551fd00514f',
                            ...
                            u'evaluation/5afde6628bf7d551fd005161'],
        u'excluded_fields': [],
        u'fields_meta': {   u'count': 5,
                            u'limit': 1000,
                            u'offset': 0,
                            u'query_total': 5,
                            u'total': 5},
        u'input_fields': [u'000000', u'000001', u'000002', u'000003'],
        u'model_count': {   u'logisticregression': 1, u'model': 8, u'total': 9},
        u'models': [   u'model/5afde64e8bf7d551fd005131',
                       u'model/5afde64f8bf7d551fd005134',
                       u'model/5afde6518bf7d551fd005137',
                       u'model/5afde6538bf7d551fd00513a',
                       u'logisticregression/5afde6558bf7d551fd00513d',
                       ...
                       u'model/5afde65a8bf7d551fd005149'],
        u'models_meta': {   u'count': 9, u'limit': 1000, u'offset': 0, u'total': 9},
        u'name': u'iris',
        u'name_options': u'9 total models (logisticregression: 1, model: 8), metric=max_phi, model candidates=18, max. training time=300',
        u'objective_field': u'000004',
        u'objective_field_details': {   u'column_number': 4,
                                        u'datatype': u'string',
                                        u'name': u'species',
                                        u'optype': u'categorical',
                                        u'order': 4},
        u'objective_field_name': u'species',
        u'objective_field_type': u'categorical',
        u'objective_fields': [u'000004'],
        u'optiml': {   u'created_resources': {   u'dataset': 10,
                                                 u'logisticregression': 11,
                                                 u'logisticregression_evaluation': 11,
                                                 u'model': 29,
                                                 u'model_evaluation': 29},
                       u'datasets': [   {   u'id': u'dataset/5afde6488bf7d551ee00081c',
                                            u'name': u'iris',
                                            u'name_options': u'120 instances, 5 fields (1 categorical, 4 numeric), sample rate=0.8'},
                                        {   u'id': u'dataset/5afde6488bf7d551fd00511f',
                                            u'name': u'iris',
                                            u'name_options': u'30 instances, 5 fields (1 categorical, 4 numeric), sample rate=0.2, out of bag'},
                                        {   u'id': u'dataset/5afde6488bf7d551fe002e0f',
                                            u'name': u'iris',
                                            u'name_options': u'120 instances, 5 fields (1 categorical, 4 numeric), sample rate=0.8'},
                                        ...
                                        {   u'id': u'dataset/5afde64d8bf7d551fd00512e',
                                            u'name': u'iris',
                                            u'name_options': u'120 instances, 5 fields (1 categorical, 4 numeric), sample rate=0.8'}],
                       u'fields': {   u'000000': {   u'column_number': 0,
                                                     u'datatype': u'double',
                                                     u'name': u'sepal length',
                                                     u'optype': u'numeric',
                                                     u'order': 0,
                                                     u'preferred': True,
                                                     u'summary': {   u'bins': [   [   4.3,
                                                                                      1],
                                                                                    ...
                                                                                  [   7.9,
                                                                                      1]],
                                                                     ...
                                                                     u'sum': 179.9,
                                                                     u'sum_squares': 302.33,
                                                                     u'variance': 0.58101}},
                                      u'000004': {   u'column_number': 4,
                                                     u'datatype': u'string',
                                                     u'name': u'species',
                                                     u'optype': u'categorical',
                                                     u'order': 4,
                                                     u'preferred': True,
                                                     u'summary': {   u'categories': [   [   u'Iris-setosa',
                                                                                            50],
                                                                                        [   u'Iris-versicolor',
                                                                                            50],
                                                                                        [   u'Iris-virginica',
                                                                                            50]],
                                                                     u'missing_count': 0},
                                                     u'term_analysis': {   u'enabled': True}}},
                       u'max_training_time': 300,
                       u'metric': u'max_phi',
                       u'model_types': [u'model', u'logisticregression'],
                       u'models': [   {   u'evaluation': {   u'id': u'evaluation/5afde65c8bf7d551fd00514c',
                                                             u'info': {   u'accuracy': 0.96667,
                                                                          u'average_area_under_pr_curve': 0.97867,
                                                                          ...
                                                                          u'per_class_statistics': [   {   u'accuracy': 1,
                                                                                                           u'area_under_pr_curve': 1,
                                                                                                           ...
                                                                                                           u'spearmans_rho': 0.82005}]},
                                                             u'metric_value': 0.95356,
                                                             u'metric_variance': 0.00079,
                                                             u'name': u'iris vs. iris',
                                                             u'name_options': u'279-node, deterministic order, operating kind=probability'},
                                          u'evaluation_count': 3,
                                          u'id': u'model/5afde64e8bf7d551fd005131',
                                          u'importance': [   [   u'000002',
                                                                 0.70997],
                                                             [   u'000003',
                                                                 0.27289],
                                                             [   u'000000',
                                                                 0.0106],
                                                             [   u'000001',
                                                                 0.00654]],
                                          u'kind': u'model',
                                          u'name': u'iris',
                                          u'name_options': u'279-node, deterministic order'},
                                      {   u'evaluation': {   u'id': u'evaluation/5afde65c8bf7d551fd00514f',
                                                             u'info': {   u'accuracy': 0.93333,

                                                            ...
                                                             [   u'000001',
                                                                 0.02133]],
                                          u'kind': u'model',
                                          u'name': u'iris',
                                          u'name_options': u'12-node, randomize, deterministic order, balanced'}],
                       u'number_of_model_candidates': 18,
                       u'recent_evaluations': [   0.90764,
                                                  0.94952,
                                                  ...
                                                  0.90427],
                       u'search_complete': True,
                       u'summary': {   u'logisticregression': {   u'best': u'logisticregression/5afde6558bf7d551fd00513d',
                                                                  u'count': 1},
                                       u'model': {   u'best': u'model/5afde64e8bf7d551fd005131',
                                                     u'count': 8}}},
        u'private': True,
        u'project': None,
        u'resource': u'optiml/5afde4a42a83475c1b0008a2',
        u'shared': False,
        u'size': 3686,
        u'source': u'source/5afdb6fb9252732d930009e5',
        u'source_status': True,
        u'status': {   u'code': 5,
                       u'elapsed': 448878.0,
                       u'message': u'The optiml has been created',
                       u'progress': 1},
        u'subscription': False,
        u'tags': [],
        u'test_dataset': None,
        u'type': 0,
        u'updated': u'2018-05-17T20:30:29.063000'}


You can check the optiml properties at the `API documentation
<https://bigml.com/api/optimls#op_optiml_properties>`_.


Fusions
-------

A Fusion is a special type of composed resource for which all
submodels satisfy the following constraints: they're all either
classifications or regressions over the same kind of data or
compatible fields, with the same objective field. Given those
properties, a fusion can be considered a supervised model,
and therefore one can predict with fusions and evaluate them.
Ensembles can be viewed as a kind of fusion subject to the additional
constraints that all its submodels are tree models that, moreover,
have been built from the same base input data, but sampled in particular ways.

The model types allowed to be a submodel of a fusion are:
deepnet, ensemble, fusion, model, logistic regression and linear regression.

The JSON structure for an Fusion is:

.. code-block:: python

    >>> api.pprint(fusion["object"])
    {
        "category": 0,
        "code": 200,
        "configuration": null,
        "configuration_status": false,
        "created": "2018-05-09T20:11:05.821000",
        "credits_per_prediction": 0,
        "description": "",
        "fields_meta": {
            "count": 5,
            "limit": 1000,
            "offset": 0,
            "query_total": 5,
            "total": 5
        },
        "fusion": {
            "models": [
                {
                    "id": "ensemble/5af272eb4e1727d378000050",
                    "kind": "ensemble",
                    "name": "Iris ensemble",
                    "name_options": "boosted trees, 1999-node, 16-iteration, deterministic order, balanced"
                },
                {
                    "id": "model/5af272fe4e1727d3780000d6",
                    "kind": "model",
                    "name": "Iris model",
                    "name_options": "1999-node, pruned, deterministic order, balanced"
                },
                {
                    "id": "logisticregression/5af272ff4e1727d3780000d9",
                    "kind": "logisticregression",
                    "name": "Iris LR",
                    "name_options": "L2 regularized (c=1), bias, auto-scaled, missing values, eps=0.001"
                }
            ]
        },
        "importance": {
            "000000": 0.05847,
            "000001": 0.03028,
            "000002": 0.13582,
            "000003": 0.4421
        },
        "model_count": {
            "ensemble": 1,
            "logisticregression": 1,
            "model": 1,
            "total": 3
        },
        "models": [
            "ensemble/5af272eb4e1727d378000050",
            "model/5af272fe4e1727d3780000d6",
            "logisticregression/5af272ff4e1727d3780000d9"
        ],
        "models_meta": {
            "count": 3,
            "limit": 1000,
            "offset": 0,
            "total": 3
        },
        "name": "iris",
        "name_options": "3 total models (ensemble: 1, logisticregression: 1, model: 1)",
        "number_of_batchpredictions": 0,
        "number_of_evaluations": 0,
        "number_of_predictions": 0,
        "number_of_public_predictions": 0,
        "objective_field": "000004",
        "objective_field_details": {
            "column_number": 4,
            "datatype": "string",
            "name": "species",
            "optype": "categorical",
            "order": 4
        },
        "objective_field_name": "species",
        "objective_field_type": "categorical",
        "objective_fields": [
            "000004"
        ],
        "private": true,
        "project": null,
        "resource":"fusion/59af8107b8aa0965d5b61138",
        "shared": false,
        "status": {
            "code": 5,
            "elapsed": 8420,
            "message": "The fusion has been created",
            "progress": 1
        },
        "subscription": false,
        "tags": [],
        "type": 0,
        "updated": "2018-05-09T20:11:14.258000"
    }

You can check the fusion properties at the `API documentation
<https://bigml.com/api/fusion#fu_fusion_properties>`_.


PCAs
----

A PCA (Principal Component Analysis) resource fits a number of orthogonal
projections (components) to maximally capture the variance in a dataset. This
is a dimensional reduction technique, as it can be used to reduce
the number of inputs for the modeling step. PCA models belong to the
unsupervised class of models (there is no objective field).

The JSON structure for an PCA is:

.. code-block:: python


    {'code': 200,
     'error': None,
     'location': 'https://strato.dev.bigml.io/andromeda/pca/5c002572983efc0ac5000003',
     'object': {u'category': 0,
                u'code': 200,
                u'columns': 2,
                u'configuration': None,
                u'configuration_status': False,
                u'created': u'2018-11-29T17:44:18.359000',
                u'creator': u'merce',
                u'credits': 0.0,
                u'credits_per_prediction': 0.0,
                u'dataset': u'dataset/5c00256a983efc0acf000000',
                u'dataset_field_types': {u'categorical': 1,
                                         u'datetime': 0,
                                         u'items': 0,
                                         u'numeric': 0,
                                         u'preferred': 2,
                                         u'text': 1,
                                         u'total': 2},
                u'dataset_status': True,
                u'description': u'',
                u'excluded_fields': [],
                u'fields_meta': {u'count': 2,
                                 u'limit': 1000,
                                 u'offset': 0,
                                 u'query_total': 2,
                                 u'total': 2},
                u'input_fields': [u'000000', u'000001'],
                u'locale': u'en-us',
                u'max_columns': 2,
                u'max_rows': 7,
                u'name': u'spam 4 words',
                u'name_options': u'standardized',
                u'number_of_batchprojections': 2,
                u'number_of_projections': 0,
                u'number_of_public_projections': 0,
                u'ordering': 0,
                u'out_of_bag': False,
                u'pca': {u'components': [[-0.64757,
                                          0.83392,
                                          0.1158,
                                          0.83481,
                                          ...
                                          -0.09426,
                                          -0.08544,
                                          -0.03457]],
                         u'cumulative_variance': [0.43667,
                                                  0.74066,
                                                  0.87902,
                                                  0.98488,
                                                  0.99561,
                                                  1],
                         u'eigenvectors': [[-0.3894,
                                            0.50146,
                                            0.06963,
                                            ...
                                            -0.56542,
                                            -0.5125,
                                            -0.20734]],
                         u'fields': {u'000000': {u'column_number': 0,
                                                 u'datatype': u'string',
                                                 u'name': u'Type',
                                                 ...
                                                                    u'token_mode': u'all',
                                                                    u'use_stopwords': False}}},
                         u'pca_seed': u'2c249dda00fbf54ab4cdd850532a584f286af5b6',
                         u'standardized': True,
                         u'text_stats': {u'000001': {u'means': [0.71429,
                                                                0.71429,
                                                                0.42857,
                                                                0.28571],
                                                     u'standard_deviations': [0.75593,
                                                                              0.75593,
                                                                              0.53452,
                                                                              0.48795]}},
                         u'variance': [0.43667,
                                       0.30399,
                                       0.13837,
                                       0.10585,
                                       0.01073,
                                       0.00439]},
                u'price': 0.0,
                u'private': True,
                u'project': None,
                u'range': None,
                u'replacement': False,
                u'resource': u'pca/5c002572983efc0ac5000003',
                u'rows': 7,
                u'sample_rate': 1.0,
                u'shared': False,
                u'size': 127,
                u'source': u'source/5c00255e983efc0acd00001b',
                u'source_status': True,
                u'status': {u'code': 5,
                            u'elapsed': 1571,
                            u'message': u'The pca has been created',
                            u'progress': 1},
                u'subscription': True,
                u'tags': [],
                u'type': 0,
                u'updated': u'2018-11-29T18:13:19.714000',
                u'white_box': False},
     'resource': u'pca/5c002572983efc0ac5000003'}

You can check the PCA properties at the `API documentation
<https://bigml.com/api/pca#pc_pca_properties>`_.
