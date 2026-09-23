from __future__ import annotations

from pathlib import Path

import json
import pandas as pd

from productpulse.paths import results_dir


class ResultStore:

    def __init__(self, root: str | Path | None = None):
        self.root = Path(root) if root else results_dir()

    # ---------------------------------------------------------
    # Paths
    # ---------------------------------------------------------

    def path(self, relative_path: str) -> Path:
        return self.root / relative_path

    # ---------------------------------------------------------
    # Read
    # ---------------------------------------------------------

    def csv(self, relative_path: str) -> pd.DataFrame:
        path = self.path(relative_path)

        if not path.exists():
            raise FileNotFoundError(path)

        return pd.read_csv(path)

    def records(self, relative_path: str) -> list[dict]:
        df = self.csv(relative_path)

        return json.loads(
            df.to_json(orient="records")
        )

    # ---------------------------------------------------------
    # Write
    # ---------------------------------------------------------

    def save_csv(
        self,
        relative_path: str,
        df: pd.DataFrame,
        *,
        index: bool = False,
    ) -> Path:

        path = self.path(relative_path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        df.to_csv(
            path,
            index=index,
        )

        return path

    def save_json(
        self,
        relative_path: str,
        data,
    ) -> Path:

        path = self.path(relative_path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with path.open(
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                data,
                f,
                indent=2,
                default=str,
            )

        return path

    # ---------------------------------------------------------
    # ProductPulse decision outputs
    # ---------------------------------------------------------

    def decision_cards(self) -> list[dict]:
        return self.records(
            "10_product_pulse_decision_engine/"
            "tables/decision_cards.csv"
        )

    def decision_registry(self) -> list[dict]:
        return self.records(
            "10_product_pulse_decision_engine/"
            "tables/decision_registry.csv"
        )
