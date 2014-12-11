Feature: REST calls for projects
    In order to CRU projects
    I need to create a project

    Scenario: Successfully creating, reading, updating and deleting a project:
        Given I create a project with name "<name>"
        And I wait until the project is ready less than <time_1> secs
        And I check that the project's name is "<name>"
        And I update the project name with "<name2>"
        Then I check that the project's name is "<name2>"

        Examples:
        | name       | time_1  | time_2 | name2             |
        | my_project | 10      | 10     | my_new_project    |
