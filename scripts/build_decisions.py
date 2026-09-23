from __future__ import annotations

import pandas as pd

from productpulse.decisions.policies import causal_targeting_policy, ranking_policy_table
from productpulse.experimentation.ab_testing import choose_experiment_action
from productpulse.paths import results_dir


def main():
    results = results_dir()
    out = results / "production_decisions"
    out.mkdir(parents=True, exist_ok=True)

    exp = pd.read_csv(results / "05_cookie_cats_experiment_analysis/tables/experiment_conclusion.csv")
    ret7 = exp.loc[exp["metric"] == "retention_7"].iloc[0]
    action = choose_experiment_action(float(ret7["absolute_difference_gate40_minus_gate30"]), float(ret7["p_value"]))
    pd.DataFrame([{"decision": action, "metric": "retention_7", "difference": ret7["absolute_difference_gate40_minus_gate30"], "p_value": ret7["p_value"]}]).to_csv(out / "experiment_decision.csv", index=False)

    rr_rank = pd.read_csv(results / "08_behavior_and_customer_prediction/tables/retailrocket_selected_ranking.csv").iloc[0]
    rr_split = pd.read_csv(results / "08_behavior_and_customer_prediction/tables/retailrocket_split_summary.csv")
    rr_n = int(rr_split.loc[rr_split["split"] == "test", "rows"].iloc[0])
    ranking_policy_table(rr_rank, rr_n, "visitor prediction rows").to_csv(out / "retailrocket_targeting_policy.csv", index=False)

    or_rank = pd.read_csv(results / "08_behavior_and_customer_prediction/tables/online_retail_selected_ranking.csv").iloc[0]
    or_split = pd.read_csv(results / "08_behavior_and_customer_prediction/tables/online_retail_split_summary.csv")
    or_n = int(or_split.loc[or_split["split"] == "test", "rows"].iloc[0])
    ranking_policy_table(or_rank, or_n, "customer prediction rows").to_csv(out / "online_retail_targeting_policy.csv", index=False)

    uplift = pd.read_csv(results / "09_criteo_uplift_modeling/tables/selected_test_targeting.csv")
    causal_targeting_policy(uplift).to_csv(out / "criteo_targeting_policy.csv", index=False)
    print("Saved production decisions to", out)


if __name__ == "__main__":
    main()
