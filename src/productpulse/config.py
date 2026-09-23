from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .paths import project_root


def load_config(name_or_path: str | Path) -> dict[str, Any]:
    path = Path(name_or_path)
    if not path.exists():
        candidate = project_root() / "configs" / str(name_or_path)
        if candidate.suffix == "":
            candidate = candidate.with_suffix(".yaml")
        path = candidate
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}
