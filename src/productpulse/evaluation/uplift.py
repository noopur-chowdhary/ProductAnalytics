from __future__ import annotations

import numpy as np
import pandas as pd


def qini_curve(y, treatment, uplift_score, n_points: int = 200) -> pd.DataFrame:
    y = np.asarray(y, dtype=float)
    treatment = np.asarray(treatment, dtype=int)
    uplift_score = np.asarray(uplift_score, dtype=float)
    order = np.argsort(uplift_score)[::-1]
    y = y[order]
    treatment = treatment[order]
    treated = (treatment == 1).astype(float)
    control = (treatment == 0).astype(float)
    cum_treated_n = np.cumsum(treated)
    cum_control_n = np.cumsum(control)
    cum_treated_y = np.cumsum(y * treated)
    cum_control_y = np.cumsum(y * control)
    expected_control = np.divide(
        cum_control_y * cum_treated_n,
        cum_control_n,
        out=np.zeros_like(cum_control_y, dtype=float),
        where=cum_control_n > 0,
    )
    gain = cum_treated_y - expected_control
    n = len(y)
    positions = np.unique(np.linspace(1, n, min(n_points, n), dtype=int))
    idx = positions - 1
    return pd.DataFrame({"fraction_targeted": positions / n, "qini_gain": gain[idx]})


def qini_coefficient(y, treatment, uplift_score) -> float:
    curve = qini_curve(y, treatment, uplift_score, n_points=500)
    x = curve["fraction_targeted"].to_numpy()
    gain = curve["qini_gain"].to_numpy()
    if len(x) < 2:
        return float("nan")
    random_gain = x * gain[-1]
    return float(np.trapz(gain - random_gain, x))


def targeting_table(y, treatment, uplift_score, fractions=(0.01, 0.05, 0.10, 0.20, 1.00)) -> pd.DataFrame:
    y = np.asarray(y)
    treatment = np.asarray(treatment)
    uplift_score = np.asarray(uplift_score)
    order = np.argsort(uplift_score)[::-1]
    rows = []
    for fraction in fractions:
        n = max(1, int(np.ceil(len(y) * fraction)))
        idx = order[:n]
        y_top = y[idx]
        t_top = treatment[idx]
        treated_mask = t_top == 1
        control_mask = t_top == 0
        treated_rate = y_top[treated_mask].mean() if treated_mask.any() else np.nan
        control_rate = y_top[control_mask].mean() if control_mask.any() else np.nan
        uplift = treated_rate - control_rate
        rows.append({
            "target_fraction": fraction,
            "target_pct": 100 * fraction,
            "rows": n,
            "treated_rows": int(treated_mask.sum()),
            "control_rows": int(control_mask.sum()),
            "treated_conversion_rate": treated_rate,
            "control_conversion_rate": control_rate,
            "observed_uplift": uplift,
            "observed_uplift_pp": 100 * uplift,
        })
    return pd.DataFrame(rows)
