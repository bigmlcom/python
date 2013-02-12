Feature: Create Predictions from public Model
    In order to create a prediction from a public model
    I need to create a public model

    Scenario: Successfully creating a prediction using a public model:
        Given I create a data source uploading a "<data>" file
        And I wait until the source is ready less than <time_1> secs
        And I create a dataset
        And I wait until the dataset is ready less than <time_2> secs
        And I create a model
        And I wait until the model is ready less than <time_3> secs
        And I make the model public
        And I wait until the model is ready less than <time_3> secs
        And I check the model status using the model's public url
        When I create a prediction for "<data_input>"
        Then the prediction for "<objective>" is "<prediction>"

        Examples:
        | data                | time_1  | time_2 | time_3 | data_input    | objective | prediction  |
        | ../data/iris.csv | 10      | 10     | 10     | {"petal length": 1} | 000004    | Iris-setosa |
