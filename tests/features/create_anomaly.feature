Feature: Create an anomaly detector from a dataset or dataset list
    In order to create an anomaly detector from a list of datasets
    I need to create some datasets first

    Scenario: Successfully creating an anomaly detector from a dataset and a dataset list:
        Given I create a data source uploading a "<data>" file
        And I wait until the source is ready less than <time_1> secs
        And I create a dataset
        And I wait until the dataset is ready less than <time_2> secs
        Then I create an anomaly detector from a dataset
        And I wait until the anomaly detector is ready less than <time_4> secs
        And I check the anomaly detector stems from the original dataset
        And I store the dataset id in a list
        And I create a dataset
        And I wait until the dataset is ready less than <time_3> secs
        And I store the dataset id in a list
        Then I create an anomaly detector from a dataset list
        And I wait until the anomaly detector is ready less than <time_4> secs
        And I check the anomaly detector stems from the original dataset list

        Examples:
        | data                 | time_1  | time_2 | time_3 |  time_4 | 
        | ../data/tiny_kdd.csv | 40      | 40     | 40     |  100
