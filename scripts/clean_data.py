from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from productpulse.data.cleaning import clean_cookie_cats, clean_criteo_chunk, clean_online_retail, clean_retailrocket_category_tree, clean_retailrocket_events
from productpulse.paths import project_root


def main():
    parser = argparse.ArgumentParser(description="Clean Product Pulse raw datasets into Parquet.")
    parser.add_argument("--dataset", choices=["cookie_cats", "online_retail", "retailrocket", "criteo", "all"], default="all")
    parser.add_argument("--chunk-size", type=int, default=500_000)
    args = parser.parse_args()
    root = project_root()
    raw = root / "data/raw"
    out = root / "data/processed/02_cleaned"
    out.mkdir(parents=True, exist_ok=True)

    if args.dataset in {"cookie_cats", "all"}:
        df = pd.read_csv(raw / "cookie_cats/cookie_cats.csv")
        clean_cookie_cats(df).to_parquet(out / "cookie_cats_clean.parquet", index=False)

    if args.dataset in {"online_retail", "all"}:
        book = pd.read_excel(raw / "online_retail/online_retail_II.xlsx", sheet_name=None, engine="openpyxl")
        frames = []
        for sheet, frame in book.items():
            frame = frame.copy(); frame["source_sheet"] = sheet; frames.append(frame)
        clean_online_retail(pd.concat(frames, ignore_index=True)).to_parquet(out / "online_retail_sales_clean.parquet", index=False)

    if args.dataset in {"retailrocket", "all"}:
        clean_retailrocket_events(pd.read_csv(raw / "retailrocket/events.csv")).to_parquet(out / "retailrocket_events_clean.parquet", index=False)
        clean_retailrocket_category_tree(pd.read_csv(raw / "retailrocket/category_tree.csv")).to_parquet(out / "retailrocket_category_tree_clean.parquet", index=False)

    if args.dataset in {"criteo", "all"}:
        target = out / "criteo_uplift"
        target.mkdir(parents=True, exist_ok=True)
        for i, chunk in enumerate(pd.read_csv(raw / "criteo/criteo-uplift-v2.1.csv.gz", compression="gzip", chunksize=args.chunk_size)):
            clean_criteo_chunk(chunk).to_parquet(target / f"part_{i:04d}.parquet", index=False)

    print("Cleaning complete:", out)


if __name__ == "__main__":
    main()
