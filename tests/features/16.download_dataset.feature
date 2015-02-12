Feature: Download Dataset to csv
    In order to export a dataset to csv
    I need to create a dataset first

    Scenario: Successfully exporting a dataset:
        Given I create a data source uploading a "<data>" file
        And I wait until the source is ready less than <time_1> secs
        And I create a dataset
        And I wait until the dataset is ready less than <time_2> secs
        And I download the dataset file to "<local_file>"
        Then file "<local_file>" is like file "<data>"

        Examples:
        | data             | time_1  | time_2 | local_file |
        | ../data/iris.csv | 30      | 30     | ./tmp/exported_iris.csv |
