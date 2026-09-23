from __future__ import annotations

import pandas as pd

from .common import generate_cutoffs, make_time_split_boundaries, safe_divide


DEFAULTS = {
    "lookback_days": 180,
    "recent_days": 30,
    "horizon_days": 60,
    "step_days": 30,
    "train_fraction": 0.70,
    "validation_fraction": 0.15,
}

ADMIN_CODES = {"POST", "DOT", "M", "D", "BANK CHARGES", "AMAZONFEE", "CRUK", "S", "C2", "PADS"}


def filter_modeling_sales(retail: pd.DataFrame) -> pd.DataFrame:
    description_upper = retail["Description"].fillna("").astype(str).str.upper()
    admin_mask = (
        retail["StockCode"].astype(str).str.upper().isin(ADMIN_CODES)
        | description_upper.str.contains("POSTAGE|BANK CHARGES|AMAZON FEE|CRUK COMMISSION|MANUAL", regex=True)
    )
    out = retail.loc[retail["CustomerID"].notna() & ~admin_mask].copy()
    out["CustomerID"] = out["CustomerID"].astype("int64")
    return out


def build_online_retail_snapshot(
    retail_df: pd.DataFrame,
    cutoff,
    split_name: str,
    lookback_days: int = 180,
    recent_days: int = 30,
    horizon_days: int = 60,
) -> pd.DataFrame:
    cutoff = pd.Timestamp(cutoff)
    history_start = cutoff - pd.Timedelta(days=lookback_days)
    recent_start = cutoff - pd.Timedelta(days=recent_days)
    label_end = cutoff + pd.Timedelta(days=horizon_days)

    history = retail_df.loc[(retail_df["InvoiceDate"] >= history_start) & (retail_df["InvoiceDate"] < cutoff)].copy()
    future = retail_df.loc[(retail_df["InvoiceDate"] >= cutoff) & (retail_df["InvoiceDate"] < label_end)].copy()

    customer = history.groupby("CustomerID").agg(
        orders_180d=("Invoice", "nunique"),
        revenue_180d=("Revenue", "sum"),
        units_180d=("Quantity", "sum"),
        unique_products_180d=("StockCode", "nunique"),
        first_purchase_180d=("InvoiceDate", "min"),
        last_purchase_180d=("InvoiceDate", "max"),
    ).reset_index()
    customer["avg_order_value_180d"] = safe_divide(customer["revenue_180d"], customer["orders_180d"])
    customer["recency_days"] = (cutoff - customer["last_purchase_180d"]).dt.days
    customer["active_span_days_180d"] = (customer["last_purchase_180d"] - customer["first_purchase_180d"]).dt.days

    recent = history.loc[history["InvoiceDate"] >= recent_start]
    recent_metrics = recent.groupby("CustomerID").agg(
        orders_30d=("Invoice", "nunique"),
        revenue_30d=("Revenue", "sum"),
        units_30d=("Quantity", "sum"),
        unique_products_30d=("StockCode", "nunique"),
    ).reset_index()
    customer = customer.merge(recent_metrics, on="CustomerID", how="left")
    recent_cols = ["orders_30d", "revenue_30d", "units_30d", "unique_products_30d"]
    customer[recent_cols] = customer[recent_cols].fillna(0)

    future_customer = future.groupby("CustomerID").agg(
        future_orders_60d=("Invoice", "nunique"),
        future_revenue_60d=("Revenue", "sum"),
    ).reset_index()
    customer = customer.merge(future_customer, on="CustomerID", how="left")
    customer[["future_orders_60d", "future_revenue_60d"]] = customer[["future_orders_60d", "future_revenue_60d"]].fillna(0)
    customer["target_future_purchase"] = (customer["future_orders_60d"] > 0).astype("int8")
    customer["prediction_cutoff"] = cutoff
    customer["label_end"] = label_end
    customer["split"] = split_name
    return customer


def build_online_retail_splits(retail: pd.DataFrame, **overrides) -> dict[str, pd.DataFrame]:
    cfg = {**DEFAULTS, **overrides}
    retail = filter_modeling_sales(retail)
    retail = retail.sort_values("InvoiceDate").reset_index(drop=True)
    data_start = retail["InvoiceDate"].min().floor("D")
    data_end = retail["InvoiceDate"].max().ceil("D")
    boundaries = make_time_split_boundaries(data_start, data_end, cfg["train_fraction"], cfg["validation_fraction"])
    outputs: dict[str, pd.DataFrame] = {}
    for split_name, (start, end) in boundaries.items():
        cutoffs = generate_cutoffs(start, end, data_start, cfg["lookback_days"], cfg["horizon_days"], cfg["step_days"])
        frames = [build_online_retail_snapshot(retail, cutoff, split_name, cfg["lookback_days"], cfg["recent_days"], cfg["horizon_days"]) for cutoff in cutoffs]
        outputs[split_name] = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    return outputs
