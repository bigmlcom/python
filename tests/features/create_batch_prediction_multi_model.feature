Feature: Create Batch Predictions from Multi Models
    In order to create a prediction from a multi model
    I need to create a multi model first

    Scenario: Successfully creating a batch prediction from a multi model:
        Given I create a data source uploading a "<data>" file
        And I wait until the source is ready less than <time_1> secs
        And I create a dataset
        And I wait until the dataset is ready less than <time_2> secs
        And I create a model with "<params>"
        And I wait until the model is ready less than <time_3> secs
        And I create a model with "<params>"
        And I wait until the model is ready less than <time_3> secs
        And I create a model with "<params>"
        And I wait until the model is ready less than <time_3> secs
        And I retrieve a list of remote models tagged with "<tag>"
        And I create a local multi model
        When I create a batch prediction for "<data_input>" and save it in "<path>"
        And I combine the votes in "<path>"
        Then the plurality combined predictions are "<predictions>"
        And the confidence weighted predictions are "<predictions>"

        Examples:
        | data             | time_1  | time_2 | time_3 | params                         |  tag  |  data_input    | path | predictions  |
        | ../data/iris.csv | 10      | 10     | 10     | {"tags":["mytag"]} | mytag |  [{"petal length": 1}, {"petal length": 6, "petal width": 2}, {"petal length": 4, "petal width": 1.5}]  | ./tmp | ["Iris-setosa", "Iris-virginica", "Iris-versicolor"] |
