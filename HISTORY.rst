.. :changelog:

History
-------

1.0.3 (2014-01-21)
~~~~~~~~~~~~~~~~~~

- Fixes bug in regressions predictions with ensembles and plurality without
  confidence information. Predictions values were not normalized.
- Updating copyright information

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

- Fixes bug in local ensembles with more than 200 fields

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
