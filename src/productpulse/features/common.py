from __future__ import annotations

import numpy as np
import pandas as pd


def safe_divide(a, b):
    return np.where(b != 0, a / b, np.nan)


def make_time_split_boundaries(start_time, end_time_exclusive, train_fraction: float, validation_fraction: float):
    start_time = pd.Timestamp(start_time)
    end_time_exclusive = pd.Timestamp(end_time_exclusive)
    total = end_time_exclusive - start_time
    train_end = start_time + total * train_fraction
    validation_end = start_time + total * (train_fraction + validation_fraction)
    return {
        "train": (start_time, train_end),
        "validation": (train_end, validation_end),
        "test": (validation_end, end_time_exclusive),
    }


def generate_cutoffs(split_start, split_end, data_start, lookback_days: int, horizon_days: int, step_days: int):
    first_possible = max(
        pd.Timestamp(split_start),
        pd.Timestamp(data_start) + pd.Timedelta(days=lookback_days),
    )
    latest_possible = pd.Timestamp(split_end) - pd.Timedelta(days=horizon_days)
    if first_possible > latest_possible:
        return []
    return list(pd.date_range(start=first_possible, end=latest_possible, freq=f"{step_days}D"))
