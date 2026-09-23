from __future__ import annotations

import pandas as pd

from .common import generate_cutoffs, make_time_split_boundaries, safe_divide


DEFAULTS = {
    "lookback_days": 21,
    "recent_days": 7,
    "horizon_days": 7,
    "step_days": 7,
    "train_fraction": 0.60,
    "validation_fraction": 0.20,
}


def build_retailrocket_snapshot(
    events: pd.DataFrame,
    cutoff,
    split_name: str,
    lookback_days: int = 21,
    recent_days: int = 7,
    horizon_days: int = 7,
) -> pd.DataFrame:
    cutoff = pd.Timestamp(cutoff)
    history_start = cutoff - pd.Timedelta(days=lookback_days)
    recent_start = cutoff - pd.Timedelta(days=recent_days)
    label_end = cutoff + pd.Timedelta(days=horizon_days)

    history = events.loc[(events["event_time"] >= history_start) & (events["event_time"] < cutoff)].copy()
    future = events.loc[(events["event_time"] >= cutoff) & (events["event_time"] < label_end)].copy()

    features = history.groupby("visitorid").agg(
        events_21d=("event", "size"),
        unique_items_21d=("itemid", "nunique"),
        first_event_21d=("event_time", "min"),
        last_event_21d=("event_time", "max"),
    ).reset_index()

    event_counts = history.groupby(["visitorid", "event"]).size().unstack(fill_value=0).reset_index().rename(
        columns={"view": "views_21d", "addtocart": "carts_21d", "transaction": "transactions_21d"}
    )
    for col in ["views_21d", "carts_21d", "transactions_21d"]:
        if col not in event_counts.columns:
            event_counts[col] = 0
    features = features.merge(event_counts[["visitorid", "views_21d", "carts_21d", "transactions_21d"]], on="visitorid", how="left")

    recent = history.loc[history["event_time"] >= recent_start]
    recent_counts = recent.groupby(["visitorid", "event"]).size().unstack(fill_value=0).reset_index().rename(
        columns={"view": "views_7d", "addtocart": "carts_7d", "transaction": "transactions_7d"}
    )
    for col in ["views_7d", "carts_7d", "transactions_7d"]:
        if col not in recent_counts.columns:
            recent_counts[col] = 0
    features = features.merge(recent_counts[["visitorid", "views_7d", "carts_7d", "transactions_7d"]], on="visitorid", how="left")
    features[["views_7d", "carts_7d", "transactions_7d"]] = features[["views_7d", "carts_7d", "transactions_7d"]].fillna(0)

    features["recency_hours"] = (cutoff - features["last_event_21d"]).dt.total_seconds() / 3600
    features["active_span_days_21d"] = (features["last_event_21d"] - features["first_event_21d"]).dt.total_seconds() / 86400
    features["cart_per_view_21d"] = safe_divide(features["carts_21d"], features["views_21d"])
    features["transaction_per_view_21d"] = safe_divide(features["transactions_21d"], features["views_21d"])

    future_transactions = future.loc[future["event"] == "transaction"].groupby("visitorid").size().rename("future_transactions_7d").reset_index()
    features = features.merge(future_transactions, on="visitorid", how="left")
    features["future_transactions_7d"] = features["future_transactions_7d"].fillna(0).astype("int32")
    features["target_future_transaction"] = (features["future_transactions_7d"] > 0).astype("int8")
    features["prediction_cutoff"] = cutoff
    features["label_end"] = label_end
    features["split"] = split_name
    return features


def build_retailrocket_splits(events: pd.DataFrame, **overrides) -> dict[str, pd.DataFrame]:
    cfg = {**DEFAULTS, **overrides}
    events = events.sort_values("event_time").reset_index(drop=True)
    data_start = events["event_time"].min().floor("D")
    data_end = events["event_time"].max().ceil("D")
    boundaries = make_time_split_boundaries(data_start, data_end, cfg["train_fraction"], cfg["validation_fraction"])
    outputs: dict[str, pd.DataFrame] = {}
    for split_name, (start, end) in boundaries.items():
        cutoffs = generate_cutoffs(start, end, data_start, cfg["lookback_days"], cfg["horizon_days"], cfg["step_days"])
        frames = [build_retailrocket_snapshot(events, cutoff, split_name, cfg["lookback_days"], cfg["recent_days"], cfg["horizon_days"]) for cutoff in cutoffs]
        outputs[split_name] = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    return outputs
