from __future__ import annotations

from pathlib import Path
import pandas as pd

from productpulse.data.cleaning import (
    clean_cookie_cats,
    clean_online_retail,
)
from productpulse.experimentation.ab_testing import (
    retention_test,
    rounds_test,
    choose_experiment_action,
)
from productpulse.features.online_retail import (
    build_online_retail_splits,
)


def run_cookie_cats(
    path: str | Path = "data/raw/cookie_cats/cookie_cats.csv",
) -> dict:

    df = pd.read_csv(path)
    df = clean_cookie_cats(df)

    retention_1 = retention_test(
        df,
        "retention_1",
    )

    retention_7 = retention_test(
        df,
        "retention_7",
    )

    rounds = rounds_test(df)

    return {
        "rows": len(df),
        "retention_1": retention_1,
        "retention_7": retention_7,
        "rounds": rounds,
        "retention_1_action": choose_experiment_action(
            difference=retention_1[
                "absolute_difference_gate40_minus_gate30"
            ],
            p_value=retention_1["p_value"],
        ),
        "retention_7_action": choose_experiment_action(
            difference=retention_7[
                "absolute_difference_gate40_minus_gate30"
            ],
            p_value=retention_7["p_value"],
        ),
    }


def run_online_retail(
    path: str | Path = "data/raw/online_retail/online_retail_II.xlsx",
) -> dict:

    sheets = pd.read_excel(
        path,
        sheet_name=None,
    )

    raw = pd.concat(
        sheets.values(),
        ignore_index=True,
    )

    retail = clean_online_retail(raw)

    splits = build_online_retail_splits(
        retail
    )

    return {
        "clean_rows": len(retail),
        "customers": int(
            retail["CustomerID"].nunique()
        ),
        "total_revenue": float(
            retail["Revenue"].sum()
        ),
        "date_start": retail["InvoiceDate"].min(),
        "date_end": retail["InvoiceDate"].max(),
        "splits": splits,
        "split_summary": {
            name: {
                "rows": len(df),
                "customers": (
                    int(df["CustomerID"].nunique())
                    if not df.empty
                    else 0
                ),
            }
            for name, df in splits.items()
        },
    }


def run_criteo(
    path: str | Path = "data/raw/criteo/criteo-uplift-v2.1.csv.gz",
    rows_per_arm: int = 100_000,
) -> dict:
    from sklearn.model_selection import train_test_split

    from productpulse.data.cleaning import clean_criteo_chunk
    from productpulse.evaluation.uplift import (
        qini_coefficient,
        targeting_table,
    )
    from productpulse.models.uplift import (
        fit_t_learner,
        make_uplift_logistic,
        predict_uplift,
    )

    features = [f"f{i}" for i in range(12)]

    treated_parts = []
    control_parts = []

    treated_count = 0
    control_count = 0

    for chunk in pd.read_csv(path, chunksize=250_000):
        chunk = clean_criteo_chunk(chunk)

        treated = chunk.loc[chunk["treatment"] == 1]
        control = chunk.loc[chunk["treatment"] == 0]

        if treated_count < rows_per_arm:
            part = treated.head(
                rows_per_arm - treated_count
            )
            if not part.empty:
                treated_parts.append(part)
                treated_count += len(part)

        if control_count < rows_per_arm:
            part = control.head(
                rows_per_arm - control_count
            )
            if not part.empty:
                control_parts.append(part)
                control_count += len(part)

        if (
            treated_count >= rows_per_arm
            and control_count >= rows_per_arm
        ):
            break

    df = pd.concat(
        treated_parts + control_parts,
        ignore_index=True,
    )

    strata = (
        df["treatment"].astype(str)
        + "_"
        + df["conversion"].astype(str)
    )

    train, test = train_test_split(
        df,
        test_size=0.25,
        random_state=42,
        stratify=strata,
    )

    treatment_model, control_model = fit_t_learner(
        make_uplift_logistic,
        train[features],
        train["conversion"].to_numpy(),
        train["treatment"].to_numpy(),
    )

    treatment_score, control_score, uplift = predict_uplift(
        treatment_model,
        control_model,
        test[features],
    )

    qini = qini_coefficient(
        test["conversion"].to_numpy(),
        test["treatment"].to_numpy(),
        uplift,
    )

    targeting = targeting_table(
        test["conversion"].to_numpy(),
        test["treatment"].to_numpy(),
        uplift,
    )

    return {
        "rows": len(df),
        "train_rows": len(train),
        "test_rows": len(test),
        "mean_treatment_score": float(
            treatment_score.mean()
        ),
        "mean_control_score": float(
            control_score.mean()
        ),
        "mean_predicted_uplift": float(
            uplift.mean()
        ),
        "qini_coefficient": float(qini),
        "targeting_table": targeting,
    }


def run_retailrocket(
    path: str | Path = "data/raw/retailrocket/events.csv",
) -> dict:
    from sklearn.utils.class_weight import compute_sample_weight

    from productpulse.data.cleaning import (
        clean_retailrocket_events,
    )
    from productpulse.evaluation.classification import (
        best_f1_threshold,
        evaluate_scores,
    )
    from productpulse.features.retailrocket import (
        build_retailrocket_splits,
    )
    from productpulse.models.propensity import (
        make_histgb_model,
        make_logistic_model,
    )

    features = [
        "events_21d",
        "unique_items_21d",
        "views_21d",
        "carts_21d",
        "transactions_21d",
        "views_7d",
        "carts_7d",
        "transactions_7d",
        "recency_hours",
        "active_span_days_21d",
        "cart_per_view_21d",
        "transaction_per_view_21d",
    ]

    target = "target_future_transaction"

    raw = pd.read_csv(path)
    events = clean_retailrocket_events(raw)

    splits = build_retailrocket_splits(events)

    train = splits["train"]
    validation = splits["validation"]
    test = splits["test"]

    X_train = train[features]
    y_train = train[target].to_numpy()

    X_val = validation[features]
    y_val = validation[target].to_numpy()

    X_test = test[features]
    y_test = test[target].to_numpy()

    logistic = make_logistic_model(
        balanced=True,
    )

    logistic.fit(
        X_train,
        y_train,
    )

    val_lr = logistic.predict_proba(
        X_val
    )[:, 1]

    threshold_lr = best_f1_threshold(
        y_val,
        val_lr,
    )

    metrics_lr = evaluate_scores(
        y_val,
        val_lr,
        threshold_lr,
        "LogisticRegression",
        "validation",
    )

    histgb = make_histgb_model()

    weights = compute_sample_weight(
        class_weight="balanced",
        y=y_train,
    )

    histgb.fit(
        X_train,
        y_train,
        model__sample_weight=weights,
    )

    val_hgb = histgb.predict_proba(
        X_val
    )[:, 1]

    threshold_hgb = best_f1_threshold(
        y_val,
        val_hgb,
    )

    metrics_hgb = evaluate_scores(
        y_val,
        val_hgb,
        threshold_hgb,
        "HistGradientBoosting",
        "validation",
    )

    validation_metrics = pd.DataFrame(
        [metrics_lr, metrics_hgb]
    )

    selected_model = (
        validation_metrics
        .sort_values(
            "pr_auc",
            ascending=False,
        )
        .iloc[0]["model"]
    )

    test_metrics = []

    for name, model, threshold in [
        (
            "LogisticRegression",
            logistic,
            threshold_lr,
        ),
        (
            "HistGradientBoosting",
            histgb,
            threshold_hgb,
        ),
    ]:
        score = model.predict_proba(
            X_test
        )[:, 1]

        test_metrics.append(
            evaluate_scores(
                y_test,
                score,
                threshold,
                name,
                "test",
            )
        )

    return {
        "selected_model": selected_model,
        "validation_metrics": validation_metrics,
        "test_metrics": pd.DataFrame(test_metrics),
        "split_rows": {
            "train": len(train),
            "validation": len(validation),
            "test": len(test),
        },
    }
