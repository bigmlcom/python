Feature: Obtain missing values and errors counters
    In order to get the missing values and errors
    I need to create a dataset first

    Scenario: Successfully obtaining missing values counts:
        Given I create a data source uploading a "<data>" file
        And I wait until the source is ready less than <time_1> secs
        And I update the source with params "<params>"
        And I create a dataset
        And I wait until the dataset is ready less than <time_2> secs
        When I ask for the missing values counts in the fields
        Then the missing values counts dict is "<missing_values>"

        Examples:
        | data                     | time_1  | params                                          | time_2 |missing_values       |
        | ../data/iris_missing.csv | 30      | {"fields": {"000000": {"optype": "numeric"}}}   |30      |{"000000": 1}      |

    Scenario: Successfully obtaining parsing error counts:
        Given I create a data source uploading a "<data>" file
        And I wait until the source is ready less than <time_1> secs
        And I update the source with params "<params>"
        And I create a dataset
        And I wait until the dataset is ready less than <time_2> secs
        When I ask for the error counts in the fields
        Then the error counts dict is "<error_values>"

        Examples:
        | data                     | time_1  | params                                          | time_2 |error_values       |
        | ../data/iris_missing.csv | 30      | {"fields": {"000000": {"optype": "numeric"}}}   |30      |{"000000": 1}      |
