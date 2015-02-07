Feature: Create Predictions
    In order to create a prediction
    I need to create a model first

    Scenario: Successfully creating a prediction from a local model in a json file:
        Given I create a local model from a "<model>" file
        When I create a local prediction for "<data_input>" with confidence
        Then the local prediction is "<prediction>"
        And the confidence for the local prediction is "<confidence>"

        Examples:
        | model                | data_input    | objective | prediction  | confidence
        | ../data/iris_model.json | {"petal length": 0.5} | 000004    | Iris-setosa | 0.90594

    Scenario: Successfully creating a multiple prediction from a local model in a json file:
        Given I create a local model from a "<model>" file
        When I create a multiple local prediction for "<data_input>"
        Then the multiple local prediction is "<prediction>"

        Examples:
        | model                | data_input    | prediction
        | ../data/iris_model.json | {"petal length": 3} |  [{"count": 42, "confidence": 0.4006020980792863, "prediction": "Iris-versicolor", "probability": 0.5060240963855421}, {"count": 41, "confidence": 0.3890868795664999, "prediction": "Iris-virginica", "probability": 0.4939759036144578}]
