from __future__ import annotations

import numpy as np
from sklearn.metrics import average_precision_score, brier_score_loss, f1_score, precision_recall_curve, roc_auc_score


def best_f1_threshold(y_true, score) -> float:
    precision, recall, thresholds = precision_recall_curve(y_true, score)
    if len(thresholds) == 0:
        return 0.5
    f1_values = 2 * precision[:-1] * recall[:-1] / (precision[:-1] + recall[:-1] + 1e-12)
    return float(thresholds[int(np.nanargmax(f1_values))])


def precision_at_fraction(y_true, score, fraction: float) -> float:
    y_true = np.asarray(y_true)
    score = np.asarray(score)
    n = max(1, int(np.ceil(len(score) * fraction)))
    idx = np.argsort(score)[::-1][:n]
    return float(y_true[idx].mean())


def recall_at_fraction(y_true, score, fraction: float) -> float:
    y_true = np.asarray(y_true)
    score = np.asarray(score)
    positives = y_true.sum()
    if positives == 0:
        return float("nan")
    n = max(1, int(np.ceil(len(score) * fraction)))
    idx = np.argsort(score)[::-1][:n]
    return float(y_true[idx].sum() / positives)


def lift_at_fraction(y_true, score, fraction: float) -> float:
    base = float(np.mean(y_true))
    return float(precision_at_fraction(y_true, score, fraction) / base) if base else float("nan")


def ranking_metrics(y_true, score) -> dict[str, float]:
    out: dict[str, float] = {}
    for pct in (1, 5, 10):
        f = pct / 100
        out[f"precision_at_{pct}pct"] = precision_at_fraction(y_true, score, f)
        out[f"recall_at_{pct}pct"] = recall_at_fraction(y_true, score, f)
        out[f"lift_at_{pct}pct"] = lift_at_fraction(y_true, score, f)
    return out


def evaluate_scores(y_true, score, threshold: float, model_name: str, split_name: str) -> dict[str, float | str]:
    pred = (np.asarray(score) >= threshold).astype(int)
    result: dict[str, float | str] = {
        "model": model_name,
        "split": split_name,
        "roc_auc": float(roc_auc_score(y_true, score)),
        "pr_auc": float(average_precision_score(y_true, score)),
        "f1": float(f1_score(y_true, pred, zero_division=0)),
        "brier_score": float(brier_score_loss(y_true, score)),
        "threshold": float(threshold),
        "positive_rate": float(np.mean(y_true)),
    }
    result.update(ranking_metrics(y_true, score))
    return result
