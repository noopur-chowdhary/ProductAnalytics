from __future__ import annotations

import os
from pathlib import Path


def project_root() -> Path:
    """Return the Product Pulse project root.

    Set PRODUCTPULSE_ROOT in Docker/production when the repository root is not
    discoverable from the installed package location.
    """
    env = os.getenv("PRODUCTPULSE_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    return Path(__file__).resolve().parents[2]


def data_dir() -> Path:
    return project_root() / "data"


def results_dir() -> Path:
    return project_root() / "results"


def artifacts_dir() -> Path:
    return project_root() / "artifacts"
