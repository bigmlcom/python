Feature: Compute MultiVote predictions
    In order compute combined predictions
    I need to create a MultiVote object

    Scenario: Successfully computing predictions combinations:
        Given I create a MultiVote for the set of predictions in file <predictions>
        When I compute the prediction with confidence using method "<method>"
        Then the combined prediction is "<prediction>"
        And the confidence for the combined prediction is <confidence>

        Examples:
        | predictions               | method       | prediction    | confidence            |
        | ../data/predictions_c.json| 0            | a             | 0.450471270879        |
        | ../data/predictions_c.json| 1            | a             | 0.552021302649        |
        | ../data/predictions_c.json| 2            | a             | 0.403632421178        |
        | ../data/predictions_r.json| 0            | 1.55555556667 | 0.400079152063        |
        | ../data/predictions_r.json| 1            | 1.59376845074 | 0.248366474212        |
        | ../data/predictions_r.json| 2            | 1.55555556667 | 0.400079152063        |
