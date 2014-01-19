Feature: Create Batch Predictions
    In order to create a batch prediction
    I need to create a model and a dataset first

    Scenario: Successfully creating a batch prediction:
        Given I create a data source uploading a "<data>" file
        And I wait until the source is ready less than <time_1> secs
        And I create a dataset
        And I wait until the dataset is ready less than <time_2> secs
        And I create a model
        And I wait until the model is ready less than <time_3> secs
        When I create a batch prediction for the dataset with the model
        And I wait until the batch prediction is ready less than <time_4> secs
        And I download the created predictions file to "<local_file>"
        Then the batch prediction file is like "<predictions_file>"

        Examples:
        | data             | time_1  | time_2 | time_3 | time_4 | local_file | predictions_file       |
        | ../data/iris.csv | 30      | 30     | 30     | 30     | ./tmp/batch_predictions.csv |./check_files/batch_predictions.csv |

    Scenario: Successfully creating a batch prediction for an ensemble:
        Given I create a data source uploading a "<data>" file
        And I wait until the source is ready less than <time_1> secs
        And I create a dataset
        And I wait until the dataset is ready less than <time_2> secs
        And I create an ensemble of <number_of_models> models and <tlp> tlp
        And I wait until the ensemble is ready less than <time_3> secs
        When I create a batch prediction for the dataset with the ensemble
        And I wait until the batch prediction is ready less than <time_4> secs
        And I download the created predictions file to "<local_file>"
        Then the batch prediction file is like "<predictions_file>"

        Examples:
        | data             | time_1  | time_2 | number_of_models | tlp | time_3 | time_4 | local_file | predictions_file       |
        | ../data/iris.csv | 30      | 30     | 5                | 1   | 50     | 30     | ./tmp/batch_predictions.csv | ./check_files/batch_predictions_e.csv |
