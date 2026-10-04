"""Filesystem layout for the GEMSDOE33 checkout.

All competition rasters live in ``data/`` (SHA-256 pinned, git-ignored) and all derived arrays in
``.cache/`` (git-ignored).  Nothing large is ever committed.
"""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = Path(os.environ.get("GEMS_DATA_DIR", ROOT / "data"))
CACHE = Path(os.environ.get("GEMS_CACHE_DIR", ROOT / ".cache"))
CACHE_BANDS = CACHE / "bands"
CACHE_FEATURES = CACHE / "features"
DOCS = ROOT / "docs"
DOWNLOADS = DOCS / "downloads"
REGISTRY = ROOT / "registry"
EVIDENCE = ROOT / "evidence"
KNOWLEDGE = ROOT / "knowledge"

for _d in (DATA, CACHE, CACHE_BANDS, CACHE_FEATURES, DOWNLOADS, EVIDENCE, KNOWLEDGE):
    _d.mkdir(parents=True, exist_ok=True)


def band_path(name: str) -> Path:
    return CACHE_BANDS / f"{name}.npy"


def feature_path(name: str) -> Path:
    return CACHE_FEATURES / f"{name}.npy"


def data_path(name: str) -> Path:
    return DATA / name
