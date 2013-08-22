Feature: Create Predictions from Multi Models
    In order to create a prediction from a multi model
    I need to create a multi model first

    Scenario: Successfully creating a prediction from a multi model:
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
        When I create a prediction for "<data_input>"
        Then the prediction for "<objective>" is "<prediction>"

        Examples:
        | data             | time_1  | time_2 | time_3 | params                         |  tag  |  data_input    | objective | prediction  |
        | ../data/iris.csv | 10      | 10     | 10     | {"tags":["mytag"]} | mytag |  {"petal width": 0.5} | 000004    | Iris-setosa |
