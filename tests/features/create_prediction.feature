Feature: Create Predictions
    In order to create a prediction
    I need to create a model first

    Scenario: Successfully creating a prediction:
        Given I create a data source uploading a "<data>" file
        And I wait until the source is ready less than <time_1> secs
        And I create a dataset
        And I wait until the dataset is ready less than <time_2> secs
        And I create a model
        And I wait until the model is ready less than <time_3> secs
        When I create a prediction for "<data_input>"
        Then the prediction for "<objective>" is "<prediction>"

        Examples:
        | data                | time_1  | time_2 | time_3 | data_input    | objective | prediction  |
        | ../data/iris.csv | 10      | 10     | 10     | {"petal width": 0.5} | 000004    | Iris-setosa |
    
    Scenario: Successfully creating a prediction from a source in a remote location:
        Given I create a data source using the url "<url>"
        And I wait until the source is ready less than <time_1> secs
        And I create a dataset
        And I wait until the dataset is ready less than <time_2> secs
        And I create a model
        And I wait until the model is ready less than <time_3> secs
        When I create a prediction for "<data_input>"
        Then the prediction for "<objective>" is "<prediction>"

        Examples:
        | url                | time_1  | time_2 | time_3 | data_input    | objective | prediction  |
        | s3://bigml-public/csv/iris.csv | 10      | 10     | 10     | {"petal width": 0.5} | 000004    | Iris-setosa |

    Scenario: Successfully creating a prediction from a asynchronous uploaded file:
        Given I create a data source uploading a "<data>" file in asynchronous mode
        And I wait until the source has been created less than <time_1> secs
        And I wait until the source is ready less than <time_2> secs
        And I create a dataset
        And I wait until the dataset is ready less than <time_3> secs
        And I create a model
        And I wait until the model is ready less than <time_4> secs
        When I create a prediction for "<data_input>"
        Then the prediction for "<objective>" is "<prediction>"

        Examples:
        | data                | time_1  | time_2 | time_3 | time_4 | data_input    | objective | prediction  |
        | ../data/iris.csv | 10      | 10     | 10     | 10     | {"petal width": 0.5} | 000004    | Iris-setosa |

    Scenario: Successfully creating a centroid and the associated dataset:
        Given I create a data source uploading a "<data>" file
        And I wait until the source is ready less than <time_1> secs
        And I create a dataset
        And I wait until the dataset is ready less than <time_2> secs
        And I create a cluster
        And I wait until the cluster is ready less than <time_3> secs
        When I create a centroid for "<data_input>"
        And I check the centroid is ok
        Then the centroid is "<centroid>"
        And I create a dataset from the cluster and the centroid
        And I wait until the dataset is ready less than <time_2> secs
        And I check that the dataset is created for the cluster and the centroid

        Examples:
        | data                | time_1  | time_2 | time_3 | data_input    | centroid  |
        | ../data/diabetes.csv | 10      | 10     | 10     | {"pregnancies": 0, "plasma glucose": 118, "blood pressure": 84, "triceps skin thickness": 47, "insulin": 230, "bmi": 45.8, "diabetes pedigree": 0.551, "age": 31, "diabetes": "true"} | Cluster 4 |
