Feature: Compare Predictions
    In order to compare a remote prediction with a local prediction
    I need to create a model first
    Then I need to create a local model

    Scenario: Successfully comparing predictions:
        Given I create a data source uploading a "<data>" file
        And I wait until the source is ready less than <time_1> secs
        And I create a dataset
        And I wait until the dataset is ready less than <time_2> secs
        And I create a model
        And I wait until the model is ready less than <time_3> secs
        And I create a local model
        When I create a prediction for "<data_input>"
        Then the prediction for "<objective>" is "<prediction>"
        And I create a local prediction for "<data_input>"
        Then the local prediction is "<prediction>"

        Examples:
        | data             | time_1  | time_2 | time_3 | data_input                             | objective | prediction  |
        | ../data/iris.csv | 10      | 10     | 10     | {"petal width": 0.5}                   | 000004    | Iris-setosa |
        | ../data/iris.csv | 10      | 10     | 10     | {"petal length": 6, "petal width": 2}  | 000004    | Iris-virginica |
        | ../data/iris.csv | 10      | 10     | 10     | {"petal length": 4, "petal width": 1.5}| 000004    | Iris-versicolor |
