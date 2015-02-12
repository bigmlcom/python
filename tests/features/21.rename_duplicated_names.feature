Feature: Rename duplicated names
    In order rename the duplicated field names
    I need to create a model first
    Then I need to create a local model

    Scenario: Successfully changing duplicated field names:
        Given I create a data source uploading a "<data>" file
        And I wait until the source is ready less than <time_1> secs
        And I create a dataset with "<options>"
        And I wait until the dataset is ready less than <time_2> secs
        And I create a model
        And I wait until the model is ready less than <time_3> secs
        And I create a local model
        Then "<field_id>" field's name is changed to "<new_name>"

Examples:
        | data             | time_1  | time_2 | time_3 | options | field_id | new_name                            
        | ../data/iris.csv | 20      | 20     | 30     | {"fields": {"000001": {"name": "species"}}} | 000001 | species1
        | ../data/iris.csv | 20      | 20     | 30     | {"fields": {"000001": {"name": "petal width"}}} | 000001 | petal width1
