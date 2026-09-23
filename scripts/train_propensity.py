from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.utils.class_weight import compute_sample_weight

from productpulse.config import load_config
from productpulse.data.loaders import load_parquet_split
from productpulse.evaluation.classification import best_f1_threshold, evaluate_scores
from productpulse.models.propensity import make_histgb_model, make_logistic_model, save_model_bundle
from productpulse.paths import artifacts_dir, project_root, results_dir


def numeric(df, cols):
    return df[cols].replace([np.inf, -np.inf], np.nan)


def train(dataset: str):
    root = project_root()
    cfg = load_config(dataset)
    splits = load_parquet_split(root / cfg["modeling_output"])
    features = cfg["features"]
    target = cfg["target"]
    balanced = bool(cfg.get("class_balancing", False))

    X_train = numeric(splits["train"], features)
    y_train = splits["train"][target].to_numpy()
    X_val = numeric(splits["validation"], features)
    y_val = splits["validation"][target].to_numpy()
    X_test = numeric(splits["test"], features)
    y_test = splits["test"][target].to_numpy()

    logistic = make_logistic_model(balanced=balanced)
    histgb = make_histgb_model()
    logistic.fit(X_train, y_train)
    if balanced:
        weights = compute_sample_weight(class_weight="balanced", y=y_train)
        histgb.fit(X_train, y_train, model__sample_weight=weights)
    else:
        histgb.fit(X_train, y_train)

    val_scores = {
        "LogisticRegression": logistic.predict_proba(X_val)[:, 1],
        "HistGradientBoosting": histgb.predict_proba(X_val)[:, 1],
    }
    thresholds = {name: best_f1_threshold(y_val, score) for name, score in val_scores.items()}
    val_metrics = pd.DataFrame([evaluate_scores(y_val, score, thresholds[name], name, "validation") for name, score in val_scores.items()])
    selected_name = str(val_metrics.sort_values("pr_auc", ascending=False).iloc[0]["model"])
    selected_model = histgb if selected_name == "HistGradientBoosting" else logistic

    test_scores = {
        "LogisticRegression": logistic.predict_proba(X_test)[:, 1],
        "HistGradientBoosting": histgb.predict_proba(X_test)[:, 1],
    }
    test_metrics = pd.DataFrame([evaluate_scores(y_test, score, thresholds[name], name, "test") for name, score in test_scores.items()])

    out = results_dir() / "production_training" / dataset
    out.mkdir(parents=True, exist_ok=True)
    pd.concat([val_metrics, test_metrics], ignore_index=True).to_csv(out / "model_metrics.csv", index=False)
    pd.DataFrame([{"dataset": dataset, "selected_model": selected_name, "selection_metric": "validation_pr_auc", "threshold": thresholds[selected_name]}]).to_csv(out / "model_selection.csv", index=False)

    artifact_name = "retailrocket_7d_transaction_model.joblib" if dataset == "retailrocket" else "online_retail_60d_repeat_purchase_model.joblib"
    save_model_bundle(
        artifacts_dir() / "models" / artifact_name,
        task=dataset,
        model=selected_model,
        features=features,
        target=target,
        threshold=thresholds[selected_name],
        model_name=selected_name,
        class_balancing=balanced,
    )
    print(val_metrics)
    print(test_metrics)
    print("Selected:", selected_name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=["retailrocket", "online_retail"], required=True)
    args = parser.parse_args()
    train(args.dataset)


if __name__ == "__main__":
    main()
