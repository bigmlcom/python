Feature: Create Predictions in DEV mode
    In order to create a prediction in DEV mode
    I need to change to an API instance in DEV mode
    And I need to create a model first

    Scenario: Successfully creating a prediction in DEV mode:
        Given I want to use api in DEV mode
        When I create a data source uploading a "<data>" file
        And I wait until the source is ready less than <time_1> secs
        And the source has DEV True 
        And I create a dataset
        And I wait until the dataset is ready less than <time_2> secs
        And I create a model
        And I wait until the model is ready less than <time_3> secs
        When I create a prediction for "<data_input>"
        Then the prediction for "<objective>" is "<prediction>"

        Examples:
        | data                | time_1  | time_2 | time_3 | data_input    | objective | prediction  |
        | ../data/iris.csv | 10      | 10     | 10     | {"petal width": 0.5} | 000004    | Iris-setosa |
