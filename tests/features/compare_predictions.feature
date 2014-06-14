Feature: Compare Predictions
    In order to compare a remote prediction with a local prediction
    I need to create a model first
    Then I need to create a local model

    Scenario: Successfully comparing predictions:
        Given I create a data source uploading a "<data>" file
        And I wait until the source is ready less than <time_1> secs
        And I create a dataset
        And I wait until the dataset is ready less than <time_2> secs
        And I create a model
        And I wait until the model is ready less than <time_3> secs
        And I create a local model
        When I create a prediction for "<data_input>"
        Then the prediction for "<objective>" is "<prediction>"
        And I create a local prediction for "<data_input>"
        Then the local prediction is "<prediction>"

        Examples:
        | data             | time_1  | time_2 | time_3 | data_input                             | objective | prediction  |
        | ../data/iris.csv | 10      | 10     | 10     | {"petal width": 0.5}                   | 000004    | Iris-setosa |
        | ../data/iris.csv | 10      | 10     | 10     | {"petal length": 6, "petal width": 2}  | 000004    | Iris-virginica |
        | ../data/iris.csv | 10      | 10     | 10     | {"petal length": 4, "petal width": 1.5}| 000004    | Iris-versicolor |

    Scenario: Successfully comparing predictions with text options:
        Given I create a data source uploading a "<data>" file
        And I wait until the source is ready less than <time_1> secs
        And I update the source with params "<options>"
        And I create a dataset
        And I wait until the dataset is ready less than <time_2> secs
        And I create a model
        And I wait until the model is ready less than <time_3> secs
        And I create a local model
        When I create a prediction for "<data_input>"
        Then the prediction for "<objective>" is "<prediction>"
        And I create a local prediction for "<data_input>"
        Then the local prediction is "<prediction>"

        Examples:
        | data             | time_1  | time_2 | time_3 | options | data_input                             | objective | prediction  |
        | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false}}}} |{"Message": "Mobile call"}             | 000000    | spam    |
        | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false}}}} |{"Message": "A normal message"}        | 000000    | ham     |
        | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": false, "use_stopwords": false}}}} |{"Message": "Mobile calls"}          | 000000    | spam   |
        | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": false, "use_stopwords": false}}}} |{"Message": "A normal message"}       | 000000    | ham     |
        | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": true, "use_stopwords": true}}}} |{"Message": "Mobile call"}            | 000000    | spam    |
        | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": true, "use_stopwords": true}}}} |{"Message": "A normal message"}       | 000000    | ham     |
        | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"token_mode": "full_terms_only"}}}} |{"Message": "FREE for 1st week! No1 Nokia tone 4 ur mob every week just txt NOKIA to 87077 Get txting and tell ur mates. zed POBox 36504 W45WQ norm150p/tone 16+"}       | 000000    | spam     |
        | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"token_mode": "full_terms_only"}}}} |{"Message": "Ok"}       | 000000    | ham     |

    Scenario: Successfully comparing predictions with proportional missing strategy:
        Given I create a data source uploading a "<data>" file
        And I wait until the source is ready less than <time_1> secs
        And I create a dataset
        And I wait until the dataset is ready less than <time_2> secs
        And I create a model
        And I wait until the model is ready less than <time_3> secs
        And I create a local model
        When I create a proportional missing strategy prediction for "<data_input>"
        Then the prediction for "<objective>" is "<prediction>"
        And the confidence for the prediction is "<confidence>"
        And I create a proportional missing strategy local prediction for "<data_input>"
        Then the local prediction is "<prediction>"
        And the confidence for the local prediction is "<confidence>"

        Examples:
        | data               | time_1  | time_2 | time_3 | data_input           | objective | prediction     | confidence |
        | ../data/iris.csv   | 10      | 10     | 10     | {}                   | 000004    | Iris-setosa    | 0.2629     |
        | ../data/grades.csv | 10      | 10     | 10     | {}                   | 000005    | 68.62224       | 27.5358    |

    Scenario: Successfully comparing centroids with or without text options:
        Given I create a data source uploading a "<data>" file
        And I wait until the source is ready less than <time_1> secs
        And I update the source with params "<options>"
        And I create a dataset
        And I wait until the dataset is ready less than <time_2> secs
        And I create a cluster
        And I wait until the cluster is ready less than <time_3> secs
        And I create a local cluster
        When I create a centroid for "<data_input>"
        Then the centroid is "<centroid>" with distance "<distance>"
        And I create a local centroid for "<data_input>"
        Then the local centroid is "<centroid>" with distance "<distance>"

        Examples:
        | data             | time_1  | time_2 | time_3 | options | data_input                            | centroid  | distance |
        | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false}}}} |{"Type": "ham", "Message": "Mobile call"}             | Cluster 0   | 0.5   |
        | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false}}}} |{"Type": "ham", "Message": "A normal message"}        | Cluster 1   | 0.393399641822     |
        | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": false, "use_stopwords": false}}}} |{"Type": "ham", "Message": "Mobile calls"}            | Cluster 0     | 0.5    |
        | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": false, "use_stopwords": false}}}} |{"Type": "ham", "Message": "A normal message"}       | Cluster 1     | 0.393399641822     |
        | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": true, "use_stopwords": true}}}} |{"Type": "ham", "Message": "Mobile call"}               | Cluster 0      | 0.5   |
        | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": false, "stem_words": true, "use_stopwords": true}}}} |{"Type": "ham", "Message": "A normal message"}       | Cluster 1     | 0.393399641822    |
        | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"token_mode": "full_terms_only"}}}} |{"Type": "ham", "Message": "FREE for 1st week! No1 Nokia tone 4 ur mob every week just txt NOKIA to 87077 Get txting and tell ur mates. zed POBox 36504 W45WQ norm150p/tone 16+"}       | Cluster 0      | 0.5     |
        | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"token_mode": "full_terms_only"}}}} |{"Type": "ham", "Message": "Ok"}       | Cluster 0    | 0.478833312167     |
        | ../data/spam.csv | 20      | 20     | 30     | {"fields": {"000001": {"optype": "text", "term_analysis": {"case_sensitive": true, "stem_words": true, "use_stopwords": false}}}} |{"Type": "", "Message": ""}             | Cluster 0   | 0.707106781187   |
        | ../data/iris.csv | 20      | 20     | 30     | {"fields": {}} |{"petal length": 1, "petal width": 1, "sepal length": 1, "sepal width": 1, "species": "Iris-setosa"}       | Cluster 0    | 1.04496638843     |
