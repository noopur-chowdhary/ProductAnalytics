from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, mannwhitneyu, ttest_ind


def retention_test(df: pd.DataFrame, column: str) -> dict[str, float | str]:
    contingency = pd.crosstab(df["version"], df[column])
    chi2, p_value, _, _ = chi2_contingency(contingency)
    rates = df.groupby("version")[column].mean()
    g30 = float(rates.get("gate_30", np.nan))
    g40 = float(rates.get("gate_40", np.nan))
    return {
        "metric": column,
        "gate_30_rate": g30,
        "gate_40_rate": g40,
        "absolute_difference_gate40_minus_gate30": g40 - g30,
        "relative_lift_pct": 100 * (g40 - g30) / g30 if g30 else np.nan,
        "chi_square": float(chi2),
        "p_value": float(p_value),
    }


def rounds_test(df: pd.DataFrame) -> dict[str, float]:
    g30 = df.loc[df["version"] == "gate_30", "sum_gamerounds"]
    g40 = df.loc[df["version"] == "gate_40", "sum_gamerounds"]
    welch = ttest_ind(g30, g40, equal_var=False, nan_policy="omit")
    mw = mannwhitneyu(g30, g40, alternative="two-sided")
    return {
        "gate_30_mean": float(g30.mean()),
        "gate_40_mean": float(g40.mean()),
        "gate_30_median": float(g30.median()),
        "gate_40_median": float(g40.median()),
        "mean_difference_gate40_minus_gate30": float(g40.mean() - g30.mean()),
        "welch_t_stat": float(welch.statistic),
        "welch_t_p_value": float(welch.pvalue),
        "mann_whitney_u": float(mw.statistic),
        "mann_whitney_p_value": float(mw.pvalue),
    }


def choose_experiment_action(difference: float, p_value: float, alpha: float = 0.05) -> str:
    if p_value < alpha and difference > 0:
        return "prefer_treatment"
    if p_value < alpha and difference < 0:
        return "keep_control"
    return "no_clear_winner"
