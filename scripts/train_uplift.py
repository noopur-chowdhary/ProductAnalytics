from __future__ import annotations

import argparse

import joblib
import numpy as np
import pandas as pd

from productpulse.config import load_config
from productpulse.data.loaders import read_parquet_parts
from productpulse.evaluation.uplift import qini_coefficient, targeting_table
from productpulse.models.uplift import capped_arm_training_data, fit_t_learner, make_uplift_histgb, make_uplift_logistic, predict_uplift
from productpulse.paths import artifacts_dir, project_root, results_dir


def stratified_split_codes(df: pd.DataFrame, treatment_col: str, outcome_col: str, train_fraction=0.70, validation_fraction=0.15, random_state=42):
    rng = np.random.default_rng(random_state)
    code = np.empty(len(df), dtype=np.int8)
    for treatment_value in (0, 1):
        for outcome_value in (0, 1):
            idx = np.flatnonzero((df[treatment_col].to_numpy() == treatment_value) & (df[outcome_col].to_numpy() == outcome_value))
            rng.shuffle(idx)
            n_train = int(np.floor(train_fraction * len(idx)))
            n_val = int(np.floor(validation_fraction * len(idx)))
            code[idx[:n_train]] = 0
            code[idx[n_train:n_train + n_val]] = 1
            code[idx[n_train + n_val:]] = 2
    return code


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hgb-max-rows-per-arm", type=int, default=None)
    args = parser.parse_args()
    cfg = load_config("criteo")
    root = project_root()
    features = cfg["features"]
    treatment_col = cfg["treatment"]
    outcome_col = cfg["outcome"]
    criteo = read_parquet_parts(root / cfg["processed_parts"], columns=features + [treatment_col, outcome_col])
    codes = stratified_split_codes(criteo, treatment_col, outcome_col, cfg["train_fraction"], cfg["validation_fraction"], cfg["random_state"])
    train = codes == 0
    val = codes == 1
    test = codes == 2
    X_train, y_train, t_train = criteo.loc[train, features], criteo.loc[train, outcome_col].to_numpy(), criteo.loc[train, treatment_col].to_numpy()
    X_val, y_val, t_val = criteo.loc[val, features], criteo.loc[val, outcome_col].to_numpy(), criteo.loc[val, treatment_col].to_numpy()
    X_test, y_test, t_test = criteo.loc[test, features], criteo.loc[test, outcome_col].to_numpy(), criteo.loc[test, treatment_col].to_numpy()

    logit_t, logit_c = fit_t_learner(make_uplift_logistic, X_train, y_train, t_train)
    _, _, logit_val = predict_uplift(logit_t, logit_c, X_val)

    cap = args.hgb_max_rows_per_arm or int(cfg["hgb_max_rows_per_arm"])
    X_hgb, y_hgb, t_hgb = capped_arm_training_data(X_train, y_train, t_train, cap, cfg["random_state"])
    hgb_t, hgb_c = fit_t_learner(make_uplift_histgb, X_hgb, y_hgb, t_hgb)
    _, _, hgb_val = predict_uplift(hgb_t, hgb_c, X_val)

    val_metrics = pd.DataFrame([
        {"model": "LogisticRegression_TLearner", "qini_coefficient": qini_coefficient(y_val, t_val, logit_val)},
        {"model": "HistGradientBoosting_TLearner", "qini_coefficient": qini_coefficient(y_val, t_val, hgb_val)},
    ]).sort_values("qini_coefficient", ascending=False)
    selected = str(val_metrics.iloc[0]["model"])
    t_model, c_model = (hgb_t, hgb_c) if selected.startswith("Hist") else (logit_t, logit_c)
    _, _, test_uplift = predict_uplift(t_model, c_model, X_test)
    test_qini = qini_coefficient(y_test, t_test, test_uplift)
    targeting = targeting_table(y_test, t_test, test_uplift)

    out = results_dir() / "production_training" / "criteo"
    out.mkdir(parents=True, exist_ok=True)
    val_metrics.to_csv(out / "validation_model_metrics.csv", index=False)
    targeting.to_csv(out / "selected_test_targeting.csv", index=False)
    pd.DataFrame([{"selected_model": selected, "test_qini": test_qini}]).to_csv(out / "model_selection.csv", index=False)
    model_path = artifacts_dir() / "models" / "criteo_conversion_uplift_model.joblib"
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"treatment_model": t_model, "control_model": c_model, "features": features, "treatment": treatment_col, "outcome": outcome_col, "model_name": selected, "score_name": "uplift_score"}, model_path)
    print(val_metrics)
    print("Selected:", selected, "test Qini:", test_qini)


if __name__ == "__main__":
    main()
