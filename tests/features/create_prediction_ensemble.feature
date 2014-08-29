Feature: Create Predictions from Ensembles
    In order to create a prediction from an ensemble
    I need to create an ensemble first

    Scenario: Successfully creating a prediction from an ensemble:
        Given I create a data source uploading a "<data>" file
        And I wait until the source is ready less than <time_1> secs
        And I create a dataset
        And I wait until the dataset is ready less than <time_2> secs
        And I create an ensemble of <number_of_models> models and <tlp> tlp
        And I wait until the ensemble is ready less than <time_3> secs
        When I create an ensemble prediction for "<data_input>"
        And I wait until the prediction is ready less than <time_4> secs
        Then the prediction for "<objective>" is "<prediction>"

        Examples:
        | data               | time_1  | time_2 | time_3 | time_4 | number_of_models | tlp   |  data_input    | objective | prediction  |
        | ../data/iris.csv   | 10      | 10     | 50     | 20     | 5                | 1     | {"petal width": 0.5} | 000004    | Iris-versicolor |
        | ../data/grades.csv | 10      | 10     | 150     | 20     | 10               | 1     | {"Assignment": 81.22, "Tutorial": 91.95, "Midterm": 79.38, "TakeHome": 105.93} | 000005    | 88.205575 | 
        | ../data/grades.csv | 10      | 10     | 150     | 20     | 10               | 1     | {"Assignment": 97.33, "Tutorial": 106.74, "Midterm": 76.88, "TakeHome": 108.89} | 000005    | 84.29401 |
