Feature: Create Predictions locally from Ensembles
    In order to create a local prediction from an ensemble
    I need to create an Ensemble first

    Scenario: Successfully creating a local prediction from an Ensemble:
        Given I create a data source uploading a "<data>" file
        And I wait until the source is ready less than <time_1> secs
        And I create a dataset
        And I wait until the dataset is ready less than <time_2> secs
        And I create an ensemble of <number_of_models> models and <tlp> tlp
        And I wait until the ensemble is ready less than <time_3> secs
        And I create a local Ensemble
        When I create a local ensemble prediction for "<data_input>"
        Then the local prediction is "<prediction>"

        Examples:
        | data             | time_1  | time_2 | time_3 | time_4 | number_of_models | tlp   |  data_input    |prediction  |
        | ../data/iris.csv | 10      | 10     | 50     | 20     | 5                | 1     | {"petal width": 0.5} | Iris-setosa |
