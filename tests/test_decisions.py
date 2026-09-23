import pandas as pd

from productpulse.decisions.policies import ranking_policy_table


def test_ranking_policy_has_three_targeting_depths():
    row = pd.Series({
        "precision_at_1pct": 0.2, "recall_at_1pct": 0.4, "lift_at_1pct": 20,
        "precision_at_5pct": 0.1, "recall_at_5pct": 0.6, "lift_at_5pct": 10,
        "precision_at_10pct": 0.05, "recall_at_10pct": 0.7, "lift_at_10pct": 5,
    })
    table = ranking_policy_table(row, 1000, "users")
    assert table["target_pct"].tolist() == [1, 5, 10]
    assert table["audience_rows"].tolist() == [10, 50, 100]
