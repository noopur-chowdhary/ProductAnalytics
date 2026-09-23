from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from productpulse.config import load_config
from productpulse.features.online_retail import build_online_retail_splits
from productpulse.features.retailrocket import build_retailrocket_splits
from productpulse.paths import project_root


def save_splits(splits, folder: Path):
    folder.mkdir(parents=True, exist_ok=True)
    for split, df in splits.items():
        path = folder / f"{split}.parquet"
        df.to_parquet(path, index=False)
        print(f"{split:10s} {len(df):>10,} rows -> {path}")


def build_retailrocket():
    root = project_root()
    cfg = load_config("retailrocket")
    events = pd.read_parquet(root / cfg["processed_events"])
    splits = build_retailrocket_splits(events, **{k: cfg[k] for k in ["lookback_days", "recent_days", "horizon_days", "step_days", "train_fraction", "validation_fraction"]})
    save_splits(splits, root / cfg["modeling_output"])


def build_online_retail():
    root = project_root()
    cfg = load_config("online_retail")
    retail = pd.read_parquet(root / cfg["processed_sales"])
    splits = build_online_retail_splits(retail, **{k: cfg[k] for k in ["lookback_days", "recent_days", "horizon_days", "step_days", "train_fraction", "validation_fraction"]})
    save_splits(splits, root / cfg["modeling_output"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=["retailrocket", "online_retail", "all"], default="all")
    args = parser.parse_args()
    if args.dataset in {"retailrocket", "all"}:
        build_retailrocket()
    if args.dataset in {"online_retail", "all"}:
        build_online_retail()


if __name__ == "__main__":
    main()
