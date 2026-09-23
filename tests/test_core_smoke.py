import numpy as np
import pandas as pd

from productpulse.data.validation import (
    require_columns,
    assert_binary,
    summarize_nulls,
)

from productpulse.features.common import safe_divide

from productpulse.evaluation.classification import (
    best_f1_threshold,
    evaluate_scores,
    precision_at_fraction,
    recall_at_fraction,
    lift_at_fraction,
    ranking_metrics,
)

from productpulse.evaluation.uplift import (
    qini_curve,
    qini_coefficient,
    targeting_table,
)

from productpulse.experimentation.ab_testing import (
    retention_test,
    rounds_test,
    choose_experiment_action,
)

from productpulse.models.propensity import (
    make_logistic_model,
    make_histgb_model,
    save_model_bundle,
    load_model_bundle,
)

from productpulse.models.uplift import (
    make_uplift_logistic,
    fit_t_learner,
    predict_uplift,
)


# -------------------------------------------------------------------
# Validation
# -------------------------------------------------------------------

def test_validation_helpers():
    df = pd.DataFrame(
        {
            "feature": [1.0, np.nan, 3.0],
            "target": [0, 1, 0],
        }
    )

    require_columns(df, ["feature", "target"], dataset_name="test")

    assert_binary(df["target"], "target")

    summary = summarize_nulls(df)

    assert isinstance(summary, pd.DataFrame)
    assert len(summary) > 0


# -------------------------------------------------------------------
# Common feature utilities
# -------------------------------------------------------------------

def test_safe_divide():
    numerator = pd.Series([10.0, 20.0, 30.0])
    denominator = pd.Series([2.0, 4.0, 5.0])

    result = safe_divide(numerator, denominator)

    assert len(result) == 3
    assert np.isclose(result[0], 5.0)
    assert np.isclose(result[1], 5.0)
    assert np.isclose(result
                      [2], 6.0)


# -------------------------------------------------------------------
# Classification evaluation
# -------------------------------------------------------------------

def test_classification_evaluation():
    y_true = np.array(
        [0, 1, 0, 1, 1, 0, 1, 0, 1, 0]
    )

    scores = np.array(
        [0.05, 0.90, 0.20, 0.80, 0.75,
         0.10, 0.65, 0.30, 0.70, 0.15]
    )

    threshold = best_f1_threshold(y_true, scores)

    assert 0 <= threshold <= 1

    metrics = evaluate_scores(
        y_true,
        scores,
        threshold=threshold,
        model_name="test_model",
        split_name="test",
    )

    assert isinstance(metrics, dict)
    assert len(metrics) > 0

    ranking = ranking_metrics(y_true, scores)

    assert isinstance(ranking, dict)
    assert len(ranking) > 0

    precision = precision_at_fraction(y_true, scores, 0.2)
    recall = recall_at_fraction(y_true, scores, 0.2)
    lift = lift_at_fraction(y_true, scores, 0.2)

    assert np.isfinite(precision)
    assert np.isfinite(recall)
    assert np.isfinite(lift)


# -------------------------------------------------------------------
# Uplift evaluation
# -------------------------------------------------------------------

def test_uplift_evaluation():
    y = np.array(
        [0, 1, 0, 1, 0, 1, 1, 0, 1, 0,
         0, 1, 0, 1, 1, 0, 1, 0, 0, 1]
    )

    treatment = np.array(
        [0, 0, 1, 1, 0, 1, 0, 1, 0, 1,
         0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
    )

    uplift_score = np.linspace(-0.2, 0.4, len(y))

    curve = qini_curve(
        y,
        treatment,
        uplift_score,
        n_points=10,
    )

    assert isinstance(curve, pd.DataFrame)
    assert len(curve) > 0

    qini = qini_coefficient(
        y,
        treatment,
        uplift_score,
    )

    assert np.isfinite(qini)

    table = targeting_table(
        y,
        treatment,
        uplift_score,
    )

    assert isinstance(table, pd.DataFrame)
    assert len(table) > 0


# -------------------------------------------------------------------
# Cookie Cats A/B testing
# -------------------------------------------------------------------

def test_ab_testing():
    rng = np.random.default_rng(42)

    n = 200

    df = pd.DataFrame(
        {
            "userid": np.arange(n),

            "version": (
                ["gate_30"] * 100
                + ["gate_40"] * 100
            ),

            "sum_gamerounds": np.concatenate(
                [
                    rng.poisson(50, 100),
                    rng.poisson(55, 100),
                ]
            ),

            "retention_1": np.concatenate(
                [
                    rng.binomial(1, 0.45, 100),
                    rng.binomial(1, 0.50, 100),
                ]
            ).astype(bool),

            "retention_7": np.concatenate(
                [
                    rng.binomial(1, 0.20, 100),
                    rng.binomial(1, 0.25, 100),
                ]
            ).astype(bool),
        }
    )

    retention = retention_test(
        df,
        "retention_1",
    )

    assert isinstance(retention, dict)
    assert len(retention) > 0

    rounds = rounds_test(df)

    assert isinstance(rounds, dict)
    assert len(rounds) > 0

    action = choose_experiment_action(
        difference=0.05,
        p_value=0.01,
    )

    assert isinstance(action, str)
    assert len(action) > 0


# -------------------------------------------------------------------
# Propensity models
# -------------------------------------------------------------------

def test_propensity_models():
    rng = np.random.default_rng(42)

    X = pd.DataFrame(
        {
            "events_21d": rng.poisson(5, 200),
            "views_21d": rng.poisson(10, 200),
            "carts_21d": rng.poisson(2, 200),
            "recency_hours": rng.uniform(0, 100, 200),
        }
    )

    y = (
        0.1 * X["views_21d"]
        + 0.5 * X["carts_21d"]
        + rng.normal(0, 1, 200)
        > 2.0
    ).astype(int)

    logistic = make_logistic_model()
    logistic.fit(X, y)

    logistic_scores = logistic.predict_proba(X)[:, 1]

    assert len(logistic_scores) == len(X)
    assert np.all(logistic_scores >= 0)
    assert np.all(logistic_scores <= 1)

    histgb = make_histgb_model()
    histgb.fit(X, y)

    histgb_scores = histgb.predict_proba(X)[:, 1]

    assert len(histgb_scores) == len(X)
    assert np.all(histgb_scores >= 0)
    assert np.all(histgb_scores <= 1)


# -------------------------------------------------------------------
# Model persistence
# -------------------------------------------------------------------

def test_model_save_and_load(tmp_path):
    model = make_logistic_model()

    bundle_path = tmp_path / "test_model.joblib"

    saved_path = save_model_bundle(
        bundle_path,
        model=model,
        features=["x1", "x2"],
        threshold=0.5,
    )

    assert saved_path.exists()

    loaded = load_model_bundle(saved_path)

    assert loaded is not None


# -------------------------------------------------------------------
# T-learner uplift model
# -------------------------------------------------------------------

def test_t_learner():
    rng = np.random.default_rng(42)

    n = 400

    X = pd.DataFrame(
        {
            "x1": rng.normal(size=n),
            "x2": rng.normal(size=n),
            "x3": rng.normal(size=n),
        }
    )

    treatment = rng.binomial(1, 0.5, n)

    base_probability = (
        1 / (
            1
            + np.exp(
                -(
                    -1.0
                    + 0.5 * X["x1"]
                    - 0.3 * X["x2"]
                )
            )
        )
    )

    treatment_effect = (
        0.10 * treatment
    )

    probability = np.clip(
        base_probability + treatment_effect,
        0.01,
        0.99,
    )

    y = rng.binomial(
        1,
        probability,
    )

    treatment_model, control_model = fit_t_learner(
        make_uplift_logistic,
        X,
        y,
        treatment,
    )

    treatment_pred, control_pred, uplift = predict_uplift(
        treatment_model,
        control_model,
        X,
    )

    assert len(treatment_pred) == n
    assert len(control_pred) == n
    assert len(uplift) == n

    assert np.all(np.isfinite(treatment_pred))
    assert np.all(np.isfinite(control_pred))
    assert np.all(np.isfinite(uplift))

    assert np.allclose(
        uplift,
        treatment_pred - control_pred,
    )
