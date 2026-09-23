from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def make_uplift_logistic(random_state: int = 42) -> Pipeline:
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(max_iter=1000, random_state=random_state)),
    ])


def make_uplift_histgb(random_state: int = 42) -> Pipeline:
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", HistGradientBoostingClassifier(
            learning_rate=0.08,
            max_iter=150,
            max_leaf_nodes=31,
            l2_regularization=1.0,
            random_state=random_state,
        )),
    ])


def fit_t_learner(model_factory, X: pd.DataFrame, y, treatment):
    treatment = np.asarray(treatment)
    y = np.asarray(y)
    treated = treatment == 1
    control = treatment == 0
    treatment_model = model_factory()
    control_model = model_factory()
    treatment_model.fit(X.loc[treated], y[treated])
    control_model.fit(X.loc[control], y[control])
    return treatment_model, control_model


def predict_uplift(treatment_model, control_model, X: pd.DataFrame):
    mu1 = treatment_model.predict_proba(X)[:, 1]
    mu0 = control_model.predict_proba(X)[:, 1]
    return mu1, mu0, mu1 - mu0


def capped_arm_training_data(X: pd.DataFrame, y, treatment, max_rows_per_arm: int | None = 2_000_000, random_state: int = 42):
    rng = np.random.default_rng(random_state)
    treatment = np.asarray(treatment)
    y = np.asarray(y)
    selected = []
    for arm in (0, 1):
        positions = np.flatnonzero(treatment == arm)
        if max_rows_per_arm is not None and len(positions) > max_rows_per_arm:
            positions = rng.choice(positions, size=max_rows_per_arm, replace=False)
        selected.append(positions)
    positions = np.concatenate(selected)
    rng.shuffle(positions)
    return X.iloc[positions], y[positions], treatment[positions]
