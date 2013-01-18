.. :changelog:

History
-------

0.5.0 (2012-01-16)
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
