from __future__ import annotations

import math

import pandas as pd


def ranking_policy_table(ranking_row: pd.Series | dict, test_rows: int, entity_name: str) -> pd.DataFrame:
    row = dict(ranking_row)
    rows = []
    for pct in (1, 5, 10):
        fraction = pct / 100
        precision = float(row[f"precision_at_{pct}pct"])
        recall = float(row[f"recall_at_{pct}pct"])
        lift = float(row[f"lift_at_{pct}pct"])
        audience_rows = int(math.ceil(test_rows * fraction))
        rows.append({
            "target_pct": pct,
            "target_fraction": fraction,
            "audience_rows": audience_rows,
            "observed_positive_rate": precision,
            "observed_positive_rate_pct": 100 * precision,
            "captured_positive_share": recall,
            "captured_positive_share_pct": 100 * recall,
            "lift_vs_population": lift,
            "estimated_positive_rows_in_audience": audience_rows * precision,
            "entity": entity_name,
        })
    return pd.DataFrame(rows)


def causal_targeting_policy(targeting: pd.DataFrame) -> pd.DataFrame:
    out = targeting.copy()
    out["incremental_conversions_per_10k"] = out["observed_uplift"] * 10_000
    out["estimated_incremental_conversions_in_audience"] = out["observed_uplift"] * out["rows"]
    full = out.loc[out["target_fraction"] == 1.0, "observed_uplift"]
    if len(full):
        out["conversion_uplift_relative_to_population"] = out["observed_uplift"] / float(full.iloc[0])
    return out
