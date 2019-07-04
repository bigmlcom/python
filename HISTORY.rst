.. :changelog:

History
-------

4.24.1 (2019-07-05)
~~~~~~~~~~~~~~~~~~~

- Adding missing tokens handling to local models.

4.24.0 (2019-06-28)
~~~~~~~~~~~~~~~~~~~

- Refactoring for multipackage compatibility.
- Deprecating ``ensemble_id`` attribute in local ensembles.
- Extending the BigML class to export model's alternative output formats.

4.23.1 (2019-06-06)
~~~~~~~~~~~~~~~~~~~

- Fixing local predictions for models with unpreferred and datetime fields.

4.23.0 (2019-05-24)
~~~~~~~~~~~~~~~~~~~

- Adding access to tasks information in the API connection object.

4.22.1 (2019-05-23)
~~~~~~~~~~~~~~~~~~~

- Improving the local Ensemble and Fusion classes to use the component
  models when a local JSON file is used as argument.

4.22.0 (2019-05-11)
~~~~~~~~~~~~~~~~~~~

- Fixing bug in local linear regressions for non-invertible confidence bounds
  matrices.
- Adding the option of cloning model resources from shared clonable ones.
- Fixing Fields object for timeseries.

4.21.2 (2019-04-09)
~~~~~~~~~~~~~~~~~~~

- Fixing bug in local fusion regression predictions.

4.21.1 (2019-04-06)
~~~~~~~~~~~~~~~~~~~

- Fixing bug in local linear regression predictions.

4.21.0 (2019-03-22)
~~~~~~~~~~~~~~~~~~~

- Adding REST and local methods for linear regression.


4.20.2 (2019-02-02)
~~~~~~~~~~~~~~~~~~~

- Adding new format for the list of datasets to create a multidataset from.

4.20.1 (2019-02-01)
~~~~~~~~~~~~~~~~~~~

- Fixing bug in local ensemble when used with externally defined connection,
  as found by @KamalGalrani.

4.20.0 (2018-12-01)
~~~~~~~~~~~~~~~~~~~

- Adding PCA REST call methods.
- Adding local PCAs and Projections.

4.19.10 (2018-12-01)
~~~~~~~~~~~~~~~~~~~~

- Fixing local Deepnet predictions for regressions without numpy.

4.19.9 (2018-10-24)
~~~~~~~~~~~~~~~~~~~

- Fixing bug in create datasets for a list of one dataset only.

4.19.8 (2018-09-18)
~~~~~~~~~~~~~~~~~~~

- Fixing bug in create evaluation for timeseries.

4.19.7 (2018-09-13)
~~~~~~~~~~~~~~~~~~~

- Fixing bug when exporting fusions with weights.
- Local fusions now caching all models in the constructor.

4.19.6 (2018-09-12)
~~~~~~~~~~~~~~~~~~~

- Fixing bug when exporting fusions.

4.19.5 (2018-08-23)
~~~~~~~~~~~~~~~~~~~

- Changing source upload `async` parameter to ensure Python 3.7 compatibility.

4.19.4 (2018-07-18)
~~~~~~~~~~~~~~~~~~~

- Fixing local logistic regression predictions with weight field missing in
  input data.

4.19.3 (2018-06-26)
~~~~~~~~~~~~~~~~~~~

- Modifying local fusion object to adapt to logistic regressions with
  no missing numerics allowed.

4.19.2 (2018-06-25)
~~~~~~~~~~~~~~~~~~~

- Removing left over comment.

4.19.1 (2018-06-23)
~~~~~~~~~~~~~~~~~~~

- Refactoring the local classes that manage models information to create
  predictions. Now all of them allow a path, an ID or a dictionary to be
  the first argument in the constructor.

4.19.0 (2018-06-20)
~~~~~~~~~~~~~~~~~~~

- Adding local fusion object and predict methods.
- Fixing error handling in local objects.
- Fixing bug in local logistic regressions when using a local stored file.

4.18.3 (2018-06-03)
~~~~~~~~~~~~~~~~~~~

- Adding batch predictions for fusion resources.

4.18.2 (2018-05-28)
~~~~~~~~~~~~~~~~~~~

- Adding predictions and evaluations for fusion resources.

4.18.1 (2018-05-19)
~~~~~~~~~~~~~~~~~~~

- Fixing bug when unused field IDs are used in local prediction inputs.

4.18.0 (2018-05-19)
~~~~~~~~~~~~~~~~~~~

- Adding methods for the REST calls to OptiMLs and Fusions.

4.17.1 (2018-05-15)
~~~~~~~~~~~~~~~~~~~

- Adding the option to export PMML models when available.
- Fixing bug in local deepnets for regressions.
- Adapting local Cluster and Anomaly detector to not include summary fields
  information.

4.17.0 (2018-05-02)
~~~~~~~~~~~~~~~~~~~

- Adding the local Supervised Model class to allow local predictions with
  any supervised model resource.

4.16.2 (2018-04-31)
~~~~~~~~~~~~~~~~~~~

- Adding the `export` and `export_last` methods to download and save the
  remote resources in the local file system.

4.16.1 (2018-04-24)
~~~~~~~~~~~~~~~~~~~

- Fixing bug in local deepnet predictions.

4.16.0 (2018-04-03)
~~~~~~~~~~~~~~~~~~~

- Deprecating local predictions formatting arguments. Formatting is available
  through the `cast_prediction` function.

4.15.2 (2018-02-24)
~~~~~~~~~~~~~~~~~~~

- Local predictions for regression ensembles corrected for strange models
  whose nodes lack the confidence attribute.

4.15.1 (2018-02-07)
~~~~~~~~~~~~~~~~~~~

- Removing logs left in local ensemble object.

4.15.0 (2018-02-07)
~~~~~~~~~~~~~~~~~~~

- Adding organizations support for all the API calls.

4.14.0 (2018-01-22)
~~~~~~~~~~~~~~~~~~~

- Deprecating `dev_mode` flag from BigML's API connection. The development
  environment has been deprecated.
- Fixing bug in local cluster output to CSV.
- Improving docs with local batch predictions examples.
- Adding operating kind support for local predictions in models and ensembles.
- Fixing bug in ensembles local predictions with probability.
- Fixing bug in logistic regression local predictions with operating points.

4.13.7 (2018-01-02)
~~~~~~~~~~~~~~~~~~~

- Changing local predictions with threshold to meet changes in backend.
- Adding support for configurations REST API calls.

4.13.6 (2017-12-05)
~~~~~~~~~~~~~~~~~~~

- Fixing predict confidence method in local ensembles.

4.13.5 (2017-11-23)
~~~~~~~~~~~~~~~~~~~

- Adding operating point local predictions to deepnets.

4.13.4 (2017-11-21)
~~~~~~~~~~~~~~~~~~~

- Fixing bug in local ensemble predictions with operating points.
- Fixing bug for local EnsemblePredictor class.

4.13.3 (2017-11-14)
~~~~~~~~~~~~~~~~~~~

- Fixing bug in local ensemble predictions for inputs that don't match the
  expected field types.

4.13.2 (2017-11-14)
~~~~~~~~~~~~~~~~~~~

- Adding left out static files for local ensemble predictor functions.

4.13.1 (2017-11-10)
~~~~~~~~~~~~~~~~~~~

- Refactoring local BoostedTrees and adding the EnsemblePredictor to
  use the local predict functions of each model to generate the ensemble
  prediction.

4.13.0 (2017-11-07)
~~~~~~~~~~~~~~~~~~~

- Adding operating point thresholds to local model, ensemble and logistic
  regression predictions.

4.12.1 (2017-10-12)
~~~~~~~~~~~~~~~~~~~

- Fixing bug in the local Deepnet predictions when numpy is not installed.

4.12.0 (2017-10-04)
~~~~~~~~~~~~~~~~~~~

- Adding support for Deepnets REST API calls and local predictions using
  the local Deepnet object.

4.11.3 (2017-09-29)
~~~~~~~~~~~~~~~~~~~

- Fixing bug in the local Ensemble object. Failed to use the
  stored ensemble object.

4.11.2 (2017-07-29)
~~~~~~~~~~~~~~~~~~~

- Fixing bug in source uploads using Python3 when reading data from stdin.

4.11.1 (2017-06-23)
~~~~~~~~~~~~~~~~~~~

- Fixing bug in source uploads using Python3 when a category is set.

4.11.0 (2017-06-23)
~~~~~~~~~~~~~~~~~~~

- Adding REST methods for managing time-series and local time-series object
  to create forecasts.

4.10.5 (2017-07-13)
~~~~~~~~~~~~~~~~~~~

- Fixing bug in the sources upload using Python3. Server changes need the
  content-type of the file to be sent.

4.10.4 (2017-06-21)
~~~~~~~~~~~~~~~~~~~

- Fixing bug in the local model predicted distributions for weighted models.
- Fixing bug in predicted probability for local model predictions
  using weighted models.

4.10.3 (2017-06-07)
~~~~~~~~~~~~~~~~~~~

- Changing boosted local ensembles predictions to match the improvements in
  API.
- Fixing bug in association rules export to CSV and lisp for rules with numeric
  attributes.

4.10.2 (2017-05-23)
~~~~~~~~~~~~~~~~~~~

- Fixing bug: local Model object failed when retrieving old JSON models from
  local storage.

4.10.1 (2017-05-15)
~~~~~~~~~~~~~~~~~~~

- Internal refactoring preparing for extensions in BigMLer.

4.10.0 (2017-05-05)
~~~~~~~~~~~~~~~~~~~

- Adding predic_probability and predict_confidence methods to local model and
  ensemble.
- Internal refactoring of local model classes preparing for extensions
  in BigMLer.

4.9.2 (2017-03-26)
~~~~~~~~~~~~~~~~~~

- Fixing bug: local model slugifying fails when fields have empty names.

4.9.1 (2017-03-23)
~~~~~~~~~~~~~~~~~~

- Adding methods to local cluster: closest data points from a
  reference point and centroids ordered from a reference point.
- Modifying internal codes in MultiVote class.

4.9.0 (2017-03-21)
~~~~~~~~~~~~~~~~~~

- Adding boosted ensembles to the local Ensemble object.

4.8.3 (2017-03-01)
~~~~~~~~~~~~~~~~~~

- Fixing bug in local logistic regression predictions when a constant field is
  forced as input field.

4.8.2 (2017-02-09)
~~~~~~~~~~~~~~~~~~

- Fixing bug: Adapting to changes in Python 3.6 which cause the connection to
  the API using SSL to fail.

4.8.1 (2017-01-11)
~~~~~~~~~~~~~~~~~~

- Changing local association parameters to adapt to API docs specifications.

4.8.0 (2017-01-08)
~~~~~~~~~~~~~~~~~~

- Adapting to final format of local association sets and adding tests.

4.7.3 (2016-12-03)
~~~~~~~~~~~~~~~~~~

- Bug fixing: query string is allowed also for project get calls.

4.7.2 (2016-12-02)
~~~~~~~~~~~~~~~~~~

- Allowing a query string to be added to get calls for all the resource types.

4.7.1 (2016-12-01)
~~~~~~~~~~~~~~~~~~

- Improving the Fields object: extracting fields structure from topic models.
- Bug fixing: Local Topic Distributions failed when tokenizing inputs with
  sequences of separators.

4.7.0 (2016-11-30)
~~~~~~~~~~~~~~~~~~

- Adding REST methods for the new resource types: Topic Model,
  Topic Distribution, Batch Topic Distribution.
- Adding local Topic Model object.

4.6.10 (2016-10-26)
~~~~~~~~~~~~~~~~~~~

- Improving local cluster object to fill in missing numerics for clusters
  with default numeric values.

4.6.9 (2016-09-27)
~~~~~~~~~~~~~~~~~~

- Fixing bug in tests for anomaly detector and ill-formatted comments.
- Adapting tests to new logistic regression default value for balance_fields.

4.6.8 (2016-09-22)
~~~~~~~~~~~~~~~~~~

- Adding optional information to local predictions.
- Improving casting for booleans in local predictions.
- Improving the retrieval of stored or remote resources in local
  predictor objects.

4.6.7 (2016-09-15)
~~~~~~~~~~~~~~~~~~

- Changing the type for the bias attribute to create logistic regressions to
  boolean.

4.6.6 (2016-08-02)
~~~~~~~~~~~~~~~~~~

- Improving message for unauthorized API calls adding information about the
  current domain.

4.6.5 (2016-07-16)
~~~~~~~~~~~~~~~~~~

- Fixing bug in local model. Fixing predictions for weighted models.

4.6.4 (2016-07-06)
~~~~~~~~~~~~~~~~~~

- Fixing bug in delete_execution method. The delete call now has a
  query_string.

4.6.3 (2016-06-25)
~~~~~~~~~~~~~~~~~~

- Fixing bug in local logistic regression predictions' format.

4.6.2 (2016-06-20)
~~~~~~~~~~~~~~~~~~

- Adding local logistic regression as argument for evaluations.

4.6.1 (2016-06-12)
~~~~~~~~~~~~~~~~~~

- Adapting local logistic regression object to new coefficients format and
  adding field_codings attribute.

4.6.0 (2016-05-19)
~~~~~~~~~~~~~~~~~~

- Adding REST methods to manage new types of whizzml resources: scripts,
  executions and libraries.
- Fixing bug in logistic regression predictions for datases with text fields.
  When input data has only one term and `all` token mode is used, local and
  remote predictions didn't match.

4.5.3 (2016-05-04)
~~~~~~~~~~~~~~~~~~

- Improving the cluster report information.
- Fixing bug in logistic regression predictions. Results differred from
  the backend predictions when date-time fields were present.

4.5.2 (2016-03-24)
~~~~~~~~~~~~~~~~~~

- Fixing bug in model's local predictions. When the model uses text fields and
  the field contents are missing in the input data, the prediction does
  not return the last prediction and stop. It now follows the
  "does not contain" branch.

4.5.1 (2016-03-12)
~~~~~~~~~~~~~~~~~~

- Adding method to Fields object to produce CSV summary files.
- Adding method to Fields object to import changes in updatable attributes
  from CSV files or strings.

4.5.0 (2016-02-08)
~~~~~~~~~~~~~~~~~~

- Adapting association object to the new syntax of missing values.
- Improving docs and comments for the proportional strategy in predictions.
- Fixing bug: centroid input data datetime fields are optional.

4.4.2 (2016-01-06)
~~~~~~~~~~~~~~~~~~

- Adapting logistic regression local object to the new missing_numeric
  parameter.

4.4.1 (2015-12-18)
~~~~~~~~~~~~~~~~~~

- Fixing bug: summarized path output failed when adding missing operators.

4.4.0 (2015-12-15)
~~~~~~~~~~~~~~~~~~

- Adding REST API calls for association rules and local Association object.
- Adapting local model, cluster, anomaly and logistic regression objects
  to new field type: items.
- Fixing bug: wrong value of giny impurity
- Fixing bug: local model summary failed occasionally when missings were used
  in a numeric predicate.
- Fixing bug: wrong syntax in flatline filter method of the tree object.

4.3.4 (2015-12-10)
~~~~~~~~~~~~~~~~~~

- Fixing bug: Logistic regression object failed to build when using input
  fields or non-preferred fields in dataset.

4.3.3 (2015-11-30)
~~~~~~~~~~~~~~~~~~

- Fixing bug: Anomaly object failed to generate the filter for new datasets
  when text empty values were found.

4.3.2 (2015-11-24)
~~~~~~~~~~~~~~~~~~

- Adding verify and protocol options to the existing Domain class constructor
  to handle special installs.

4.3.1 (2015-11-07)
~~~~~~~~~~~~~~~~~~

- Fixing bug: Local logistic regression predictions differ when input data
  has contents in a text field but the terms involved do not appear in the
  bag of words.

4.3.0 (2015-10-16)
~~~~~~~~~~~~~~~~~~

- Adding logistic regression as a new prediction model.

4.2.2 (2015-10-14)
~~~~~~~~~~~~~~~~~~

- Fixing bug: Fields object failed to store the correct objective id when the
  objective was in the first column.

4.2.1 (2015-10-14)
~~~~~~~~~~~~~~~~~~

- Fixing bug: Improving error handling in download_dataset method.

4.2.0 (2015-07-27)
~~~~~~~~~~~~~~~~~~

- Adding REST methods to manage new type of resource: correlations.
- Adding REST methods to manage new type of resource: tests.
- Adding min and max values predictions for regression models and ensembles.
- Fixing bug: Fields object was not retrieving objective id from the
  resource info.

4.1.7 (2015-08-15)
~~~~~~~~~~~~~~~~~~

- Fixing bug: console messages failed when used with Python3 on Windows.

4.1.6 (2015-06-25)
~~~~~~~~~~~~~~~~~~

- Fixing bug: Removing id fields from the filter to select the anomalies listed
  in the Anomaly object from the origin dataset.

4.1.5 (2015-06-06)
~~~~~~~~~~~~~~~~~~

- Fixing bug: create_source method failed when unicode literals were used in
  args.

4.1.4 (2015-05-27)
~~~~~~~~~~~~~~~~~~

- Ensuring unique ordering in MultiVote categorical combinations (only
  needed in Python 3).

4.1.3 (2015-05-19)
~~~~~~~~~~~~~~~~~~

- Adapting code to handle uploading from String objects.
- Adding models creation new origin resources: clusters and centroids.

4.1.2 (2015-04-28)
~~~~~~~~~~~~~~~~~~

- Fixing bug in summarize method for local models. Ensuring unicode use and
  adding tests for generated outputs.

4.1.1 (2015-04-26)
~~~~~~~~~~~~~~~~~~

- Fixing bug in method to print the fields in the anomaly trees.
- Fixing bug in the create_source method for Python3. Creation failed when
  the `tags` argument was used.

4.1.0 (2015-04-14)
~~~~~~~~~~~~~~~~~~

- Adding median based predictions to ensembles.

4.0.2 (2015-04-12)
~~~~~~~~~~~~~~~~~~

- Fixing bug: multimodels median predictions failed.

4.0.1 (2015-04-10)
~~~~~~~~~~~~~~~~~~

- Adding support for median-based predictions in MultiModels.

4.0.0 (2015-04-10)
~~~~~~~~~~~~~~~~~~

- Python 3 added to supported Python versions.
- Test suite migrated to nose.


3.0.3 (2015-04-08)
~~~~~~~~~~~~~~~~~~

- Changing setup to ensure compatible Python and requests versions.
- Hiding warnings when SSL verification is disabled.

3.0.2 (2015-03-26)
~~~~~~~~~~~~~~~~~~

- Adding samples as Fields generator resources

3.0.1 (2015-03-17)
~~~~~~~~~~~~~~~~~~

- Changing the Ensemble object init method to use the max_models argument
  also when loading the ensemble fields to trigger garbage collection.

3.0.0 (2015-03-04)
~~~~~~~~~~~~~~~~~~

- Adding Google App Engine support for remote REST calls.
- Adding cache_get argument to Ensemble constructor to allow getting
  local model objects from cache.

2.2.0 (2015-02-26)
~~~~~~~~~~~~~~~~~~

- Adding lists of local models as argument for the local ensemble
  constructor.

2.1.0 (2015-02-22)
~~~~~~~~~~~~~~~~~~

- Adding distribution and median to ensembles' predictions output.

2.0.0 (2015-02-12)
~~~~~~~~~~~~~~~~~~

- Adding REST API calls for samples.

1.10.8 (2015-02-10)
~~~~~~~~~~~~~~~~~~~

- Adding distribution units to the predict method output of the local model.

1.10.7 (2015-02-07)
~~~~~~~~~~~~~~~~~~~

- Extending the predict method in local models to get multiple predictions.
- Changing the local model object to add the units used in the distribution
  and the add_median argument in the predict method.

1.10.6 (2015-02-06)
~~~~~~~~~~~~~~~~~~~

- Adding the median as prediction for the local model object.

1.10.5 (2014-01-29)
~~~~~~~~~~~~~~~~~~~

- Fixing bug: centroids failed when predicted from local clusters with
  summary fields.

1.10.4 (2014-01-17)
~~~~~~~~~~~~~~~~~~~

- Improvements in docs presentation and content.
- Adding tree_CSV method to local model to output the nodes information
  in CSV format.

1.10.3 (2014-01-16)
~~~~~~~~~~~~~~~~~~~

- Fixing bug: local ensembles were not retrieved from the stored JSON file.
- Adding the ability to construct local ensembles from any existing JSON file
  describing an ensemble structure.

1.10.2 (2014-01-15)
~~~~~~~~~~~~~~~~~~~

- Source creation from inline data.

1.10.1 (2014-12-29)
~~~~~~~~~~~~~~~~~~~

- Fixing bug: source upload failed in old Python versions.

1.10.0 (2014-12-29)
~~~~~~~~~~~~~~~~~~~

- Refactoring the BigML class before adding the new project resource.
- Changing the ok and check_resource methods to download lighter resources.
- Fixing bug: cluster summarize for 1-centroid clusters.
- Fixing bug: adapting to new SSL verification in Python 2.7.9.

1.9.8 (2014-12-01)
~~~~~~~~~~~~~~~~~~

- Adding impurity to Model leaves, and a new method to select impure leaves.
- Fixing bug: the Model, Cluster and Anomaly objects had no resource_id
  attribute when built from a local resource JSON structure.

1.9.7 (2014-11-24)
~~~~~~~~~~~~~~~~~~

- Adding method in Anomaly object to build the filter to exclude anomalies
  from the original dataset.
- Basic code refactorization for initial resources structure.

1.9.6 (2014-11-09)
~~~~~~~~~~~~~~~~~~

- Adding BIGML_PROTOCOL, BIGML_SSL_VERIFY and BIGML_PREDICTION_SSL_VERIFY
  environment variables to change the default corresponding values in
  customized private environments.

1.9.5 (2014-11-03)
~~~~~~~~~~~~~~~~~~

- Fixing bug: summarize method breaks for clusters with text fields.

1.9.4 (2014-10-27)
~~~~~~~~~~~~~~~~~~

- Changing MultiModel class to return in-memory list of predictions.

1.9.3 (2014-10-23)
~~~~~~~~~~~~~~~~~~

- Improving Fields and including the new Cluster and
  Anomalies fields structures as fields resources.
- Improving ModelFields to filter missing values from input data.
- Forcing garbage collection in local ensemble to lower memory usage.

1.9.2 (2014-10-13)
~~~~~~~~~~~~~~~~~~

- Changing some Fields exceptions handling.
- Refactoring api code to handle create, update and delete methods dynamically.
- Adding connection info string for printing.
- Improving tests information.

1.9.1 (2014-10-10)
~~~~~~~~~~~~~~~~~~

- Adding the summarize and statistics_CSV methods to local cluster object.

1.9.0 (2014-10-02)
~~~~~~~~~~~~~~~~~~

- Adding the batch anomaly score REST API calls.

1.8.0 (2014-09-09)
~~~~~~~~~~~~~~~~~~

- Adding the anomaly detector and anomaly score REST API calls.
- Adding the local anomaly detector.

1.7.0 (2014-08-29)
~~~~~~~~~~~~~~~~~~

- Adding to local model predictions the ability to use the new
  missing-combined operators.

1.6.7 (2014-08-05)
~~~~~~~~~~~~~~~~~~

- Fixing bug in corner case of model predictions using proportional missing
  strategy.
- Adding the unique path to the first missing split to the predictions using
  proportional missing strategy.

1.6.6 (2014-07-31)
~~~~~~~~~~~~~~~~~~

- Improving the locale handling to avoid problems when logging to console under
  Windows.

1.6.5 (2014-07-26)
~~~~~~~~~~~~~~~~~~

- Adding stats method to Fields to show fields statistics.
- Adding api method to create a source from a batch prediction.

1.6.4 (2014-07-25)
~~~~~~~~~~~~~~~~~~

- Changing the create methods to check if origin resources are finished
  by downloading no fields information.

1.6.3 (2014-07-24)
~~~~~~~~~~~~~~~~~~

- Changing some variable names in the predict method (add_count, add_path) and
  the prediction structure to follow other bindigns naming.

1.6.2 (2014-07-19)
~~~~~~~~~~~~~~~~~~

- Building local model from a JSON model file.
- Predictions output can contain confidence, distribution, instances and/or
  rules.

1.6.1 (2014-07-09)
~~~~~~~~~~~~~~~~~~

- Fixing bug: download_dataset method did not return content when no filename
  was provided.

1.6.0 (2014-07-03)
~~~~~~~~~~~~~~~~~~

- Fixing bug: check valid parameter in distribution merge function.
- Adding downlod_dataset method to api to export datasets to CSV.

1.5.1 (2014-06-13)
~~~~~~~~~~~~~~~~~~

- Fixing bug: local clusters' centroid method crashes when text or categorical
  fields are not present in input data.

1.5.0 (2014-06-05)
~~~~~~~~~~~~~~~~~~

- Adding local cluster to produce centroid predictions locally.

1.4.4 (2014-05-23)
~~~~~~~~~~~~~~~~~~

- Adding shared urls to datasets.
- Fixing bug: error renaming variables.

1.4.3 (2014-05-22)
~~~~~~~~~~~~~~~~~~

- Adding the ability to change the remote server domain in the API
  connection constructor (for VPCs).
- Adding the ability to generate datasets from clusters.

1.4.2 (2014-05-20)
~~~~~~~~~~~~~~~~~~

- Fixing bug when using api.ok method for centroids and batch centroids.

1.4.1 (2014-05-19)
~~~~~~~~~~~~~~~~~~

- Docs and test updates.

1.4.0 (2014-05-14)
~~~~~~~~~~~~~~~~~~

- Adding REST methods to manage clusters, centroids and batch centroids.

1.3.1 (2014-05-06)
~~~~~~~~~~~~~~~~~~

- Adding the average_confidence method to local models.
- Fixing bug in pprint for predictions with input data keyed by field names.

1.3.0 (2014-04-07)
~~~~~~~~~~~~~~~~~~

- Changing Fields object constructor to accept also source, dataset or model
  resources.

1.2.2 (2014-04-01)
~~~~~~~~~~~~~~~~~~

- Changing error message when create_source calls result in http errors
  to standarize them.
- Simplifying create_prediction calls because now API accepts field names
  as input_data keys.
- Adding missing_counts and error_counts to report the missing values and
  error counts per field in the dataset.

1.2.1 (2014-03-19)
~~~~~~~~~~~~~~~~~~

- Adding error to regression local predictions using proportional missing
  strategy.

1.2.0 (2014-03-07)
~~~~~~~~~~~~~~~~~~

- Adding proportional missing strategy to MultiModel and solving tie breaks
  in remote predictions.
- Adding new output options to model's python, rules and tableau outputs:
  ability to extract the branch of the model leading to a certain node with
  or without the hanging subtree.
- Adding HTTP_TOO_MANY_REQUESTS error handling in REST API calls.

1.1.0 (2014-02-10)
~~~~~~~~~~~~~~~~~~

- Adding Tableau-ready ouput to local model code generators.

1.0.6 (2014-02-03)
~~~~~~~~~~~~~~~~~~

- Fixing getters: getter for batch predictions was missing.

1.0.5 (2014-01-22)
~~~~~~~~~~~~~~~~~~

- Improving BaseModel and Model. If they receive a partial model
  structure with a correct model id, the needed model resource is downloaded
  and stored (if storage is enabled in the given api connection).
- Improving local ensemble. Adding a new `fields` attribute that
  contains all the fields used in its models.

1.0.4 (2014-01-21)
~~~~~~~~~~~~~~~~~~

- Adding a summarize method to local ensembles with data distribution
  and field importance information.

1.0.3 (2014-01-21)
~~~~~~~~~~~~~~~~~~

- Fixes bug in regressions predictions with ensembles and plurality without
  confidence information. Predictions values were not normalized.
- Updating copyright information.

1.0.2 (2014-01-20)
~~~~~~~~~~~~~~~~~~

- Fixes bug in create calls: the user provided args dictionaries were
  updated inside the calls.

1.0.1 (2014-01-05)
~~~~~~~~~~~~~~~~~~

- Changing the source for ensemble field importance computations.
- Fixes bug in http_ok adding the valid state for updates.

1.0.0 (2013-12-09)
~~~~~~~~~~~~~~~~~~

- Adding more info to error messages in REST methods.
- Adding new missing fields strategy in predict method.
- Fixes bug in shared models: credentials where not properly set.
- Adding batch predictions REST methods.

0.10.3 (2013-12-19)
~~~~~~~~~~~~~~~~~~~

- Fixes bug in local ensembles with more than 200 fields.

0.10.2 (2013-12-02)
~~~~~~~~~~~~~~~~~~~

- Fixes bug in summarize method of local models: field importance report
  crashed.
- Fixes bug in status method of the BigML connection object: status for
  async uploads of source files crashed while uploading.

0.10.1 (2013-11-25)
~~~~~~~~~~~~~~~~~~~

- Adding threshold combiner to MultiModel objects.

0.10.0 (2013-11-21)
~~~~~~~~~~~~~~~~~~~

- Adding a function printing field importance to ensembles.
- Changing Model to add a lightweight BaseModel class with no Tree
  information.
- Adding function to get resource type from resource id or structure.
- Adding resource type checks to REST functions.
- Adding threshold as new combination method for local ensembles.

0.9.1 (2013-10-17)
~~~~~~~~~~~~~~~~~~

- Fixes duplication changing field names in local model if they are not unique.

0.9.0 (2013-10-08)
~~~~~~~~~~~~~~~~~~

- Adds the environment variables and adapts the create_prediction method
  to create predictions using a different prediction server.
- Support for shared models.

0.8.0 (2013-08-10)
~~~~~~~~~~~~~~~~~~

- Adds text analysis local predict function
- Modifies outputs for text analysis: rules, summary, python, hadoop

0.7.5 (2013-08-22)
~~~~~~~~~~~~~~~~~~

- Fixes temporarily problems in predictions for regression models and
  ensembles
- Adds en-gb to the list of available locales, avoiding spurious warnings

0.7.4 (2013-08-17)
~~~~~~~~~~~~~~~~~~

- Changes warning logger level to info

0.7.3 (2013-08-09)
~~~~~~~~~~~~~~~~~~

- Adds fields method to retrieve only preferred fields
- Fixes error message when no valid resource id is provided in check_resource

0.7.2 (2013-07-04)
~~~~~~~~~~~~~~~~~~

- Fixes check_resource method that was not using query-string data
- Add list of models as argument in Ensemble constructor
- MultiModel has BigML connection as a new optional argument

0.7.1 (2013-06-19)
~~~~~~~~~~~~~~~~~~

- Fixes Multimodel list_models method
- Fixes check_resource method for predictions
- Adds local configuration environment variable BIGML_DOMAIN replacing
  BIGML_URL and BIGML_DEV_URL
- Refactors Ensemble and Model's predict method

0.7.0 (2013-05-01)
~~~~~~~~~~~~~~~~~~

- Adds splits in datasets to generate new datasets
- Adds evaluations for ensembles

0.6.0 (2013-04-27)
~~~~~~~~~~~~~~~~~~

- REST API methods for model ensembles
- New method returning the leaves of tree models
- Improved error handling in GET methods

0.5.2 (2013-03-03)
~~~~~~~~~~~~~~~~~~

- Adds combined confidence to combined predictions
- Fixes get_status for resources that have no status info
- Fixes bug: public datasets, that should be downloadable, weren't

0.5.1 (2013-02-12)
~~~~~~~~~~~~~~~~~~

- Fixes bug: no status info in public models, now shows FINISHED status code
- Adds more file-like objects (e.g. stdin) support in create_source input
- Refactoring Fields pair method and Model predict method to increase
- Adds some more locale aliases

0.5.0 (2013-01-16)
~~~~~~~~~~~~~~~~~~

- Adds evaluation api functions
- New prediction combination method: probability weighted
- Refactors MultiModels lists of predictions into MultiVote
- Multimodels partial predictions: new format

0.4.8 (2012-12-21)
~~~~~~~~~~~~~~~~~~

- Improved locale management
- Adds new features to MultiModel to allow local batch predictions
- Improved combined predictions
- Adds local predictions options: plurality, confidence weighted

0.4.7 (2012-12-06)
~~~~~~~~~~~~~~~~~~

- Warning message to inform of locale default if verbose mode

0.4.6 (2012-12-06)
~~~~~~~~~~~~~~~~~~

- Fix locale code for windows

0.4.5 (2012-12-05)
~~~~~~~~~~~~~~~~~~

- Fix remote predictions for input data containing fields not included in rules

0.4.4 (2012-12-02)
~~~~~~~~~~~~~~~~~~

- Tiny fixes
- Fix local predictions for input data containing fields not included in rules
- Overall clean up

0.4.3 (2012-11-07)
~~~~~~~~~~~~~~~~~~

- A few tiny fixes
- Multi models to generate predictions from multiple local models
- Adds hadoop-python code generation to create local predictions

0.4.2 (2012-09-19)
~~~~~~~~~~~~~~~~~~

- Fix Python generation
- Add a debug flag to log https requests and responses
- Type conversion in fields pairing

0.4.1 (2012-09-17)
~~~~~~~~~~~~~~~~~~

- Fix missing distribution field in new models
- Add new Field class to deal with BigML auto-generated ids
- Add by_name flag to predict methods to avoid reverse name lookups
- Add summarize method in models to generate class grouped printed output

0.4.0 (2012-08-20)
~~~~~~~~~~~~~~~~~~

- Development Mode
- Remote Sources
- Bigger files streamed with Poster
- Asynchronous Uploading
- Local Models
- Local Predictions
- Rule Generation
- Python Generation
- Overall clean up


0.3.1 (2012-07-05)
~~~~~~~~~~~~~~~~~~

- Initial release for the "andromeda" version of BigML.io.
