Feature: Create and update a sample from a dataset
    In order to create a sample from a dataset
    I need to create an origin dataset

    Scenario: Successfully creating a sample from a dataset:
        Given I create a data source uploading a "<data>" file
        And I wait until the source is ready less than <time_1> secs
        And I create a dataset
        And I wait until the dataset is ready less than <time_2> secs
        And I create a sample from a dataset
        And I wait until the sample is ready less than <time_3> secs
        And I update the sample name to "<sample_name>"
        When I wait until the sample is ready less than <time_4> secs
        Then the sample name is "<sample_name>"

        Examples:
        | data                | time_1  | time_2 | time_3 | time_4 | sample_name |
        | ../data/iris.csv | 10      | 10     | 10     | 10 | my new sample name |
