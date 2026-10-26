"""Fail-closed duplicate guards against the pinned focus-site raster registry."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation
from scipy.stats import rankdata

from .paths import ROOT

REGISTRY_MANIFEST = ROOT / "registry" / "focus_rasters_20261025.json"
RANK_LIMIT = 0.90
OVERLAP_LIMIT = 0.70
OVERLAP_RADIUS_PX = 3


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _entries() -> list[dict]:
    return json.loads(REGISTRY_MANIFEST.read_text())["rasters"]


def _read_entry(entry: dict, footprint: np.ndarray) -> np.ndarray:
    path = ROOT / entry["cache_path"]
    if not path.is_file():
        raise FileNotFoundError(
            f"Missing registry raster {path}; run scripts/cache_focus_registry.py"
        )
    actual = _sha256(path)
    if actual != entry["sha256"]:
        raise ValueError(f"Registry SHA-256 mismatch for {entry['id']}: {actual}")
    with rasterio.open(path) as source:
        if source.count != 1 or source.shape != footprint.shape:
            raise ValueError(f"Registry grid/count mismatch for {entry['id']}")
        arr = source.read(1)
    return footprint & np.isfinite(arr) & (arr > 0)


def _correlation(left: np.ndarray, right: np.ndarray) -> float | None:
    a = np.asarray(left, dtype=np.float64)
    b = np.asarray(right, dtype=np.float64)
    if a.size != b.size or a.size < 2:
        raise ValueError("Correlation vectors must be equal and nontrivial")
    sa, sb = float(a.std()), float(b.std())
    if sa == 0.0 or sb == 0.0:
        return None
    return float(np.corrcoef(a, b)[0, 1])


def compare_surface(
    surface: np.ndarray,
    footprint: np.ndarray,
    *,
    sample_size: int = 200_000,
    seed: int = 20261025,
) -> dict:
    """Compare a continuous score surface before placement to every registry dot raster."""
    score = np.asarray(surface, dtype=np.float32)
    footprint = np.asarray(footprint, dtype=bool)
    if score.shape != footprint.shape or not np.isfinite(score[footprint]).all():
        raise ValueError("Surface must be finite and footprint-aligned")
    ids = np.flatnonzero(footprint)
    rng = np.random.default_rng(seed)
    sample = np.sort(rng.choice(ids, size=min(sample_size, ids.size), replace=False))
    score_ranks = rankdata(score.ravel()[sample], method="average")
    rows = []
    for entry in _entries():
        dots = _read_entry(entry, footprint)
        registry_ranks = rankdata(dots.ravel()[sample].astype(np.uint8), method="average")
        rho = _correlation(score_ranks, registry_ranks)
        duplicate = bool(rho is not None and rho > RANK_LIMIT)
        rows.append(
            {
                "registry_id": entry["id"],
                "registry_sha256": entry["sha256"],
                "registry_dots": int(dots.sum()),
                "spearman_rho": rho,
                "duplicate": duplicate,
            }
        )
    return {
        "stage": "surface_before_placement",
        "registry_count": len(rows),
        "sample_pixels": int(sample.size),
        "sample_seed": seed,
        "spearman_stop_gt": RANK_LIMIT,
        "passed": bool(rows) and not any(row["duplicate"] for row in rows),
        "max_spearman_rho": max(
            (row["spearman_rho"] for row in rows if row["spearman_rho"] is not None),
            default=None,
        ),
        "rows": rows,
    }


def compare_final_dots(dots: np.ndarray, footprint: np.ndarray) -> dict:
    """Compare exact final binary geometry to all registry rasters."""
    candidate = np.asarray(dots, dtype=bool)
    footprint = np.asarray(footprint, dtype=bool)
    if candidate.shape != footprint.shape or np.any(candidate & ~footprint) or not candidate.any():
        raise ValueError("Final dots must be nonempty and inside the footprint")
    cand_vec = candidate[footprint].astype(np.uint8)
    yy, xx = np.ogrid[-OVERLAP_RADIUS_PX : OVERLAP_RADIUS_PX + 1,
                      -OVERLAP_RADIUS_PX : OVERLAP_RADIUS_PX + 1]
    disk = (yy * yy + xx * xx) <= OVERLAP_RADIUS_PX * OVERLAP_RADIUS_PX
    rows = []
    for entry in _entries():
        registry = _read_entry(entry, footprint)
        rho = _correlation(cand_vec, registry[footprint].astype(np.uint8))
        near = binary_dilation(registry, structure=disk)
        overlap = float((candidate & near).sum() / candidate.sum())
        duplicate = bool(
            (rho is not None and rho > RANK_LIMIT) or overlap > OVERLAP_LIMIT
        )
        rows.append(
            {
                "registry_id": entry["id"],
                "registry_sha256": entry["sha256"],
                "registry_dots": int(registry.sum()),
                "spearman_rho": rho,
                "candidate_dots_within_3px": int((candidate & near).sum()),
                "candidate_dots": int(candidate.sum()),
                "candidate_fraction_within_3px": overlap,
                "duplicate": duplicate,
            }
        )
    return {
        "stage": "final_dots",
        "registry_count": len(rows),
        "spearman_stop_gt": RANK_LIMIT,
        "overlap_stop_gt": OVERLAP_LIMIT,
        "overlap_radius_px": OVERLAP_RADIUS_PX,
        "passed": bool(rows) and not any(row["duplicate"] for row in rows),
        "max_spearman_rho": max(
            (row["spearman_rho"] for row in rows if row["spearman_rho"] is not None),
            default=None,
        ),
        "max_candidate_fraction_within_3px": max(
            (row["candidate_fraction_within_3px"] for row in rows), default=None
        ),
        "rows": rows,
    }
