#!/usr/bin/env python3
"""Release-time A33-L1 guard against the canonical 12-reference focus registry.

This extends (never replaces) the frozen nine-raster experiment guard after the
concurrent canonical registry became available. It is a duplicate diagnostic,
not a new experiment, HOLDOUT-DTI, or organizer-score estimate.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gemsdoe33.novelty import binary_comparison  # noqa: E402

MANIFEST = ROOT / "registry/focus_rasters_20261025.json"
CANDIDATE = ROOT / "docs/downloads/gemsdoe33-a33-l1-analog-transfer-research-37654-20261025-85c94a805a34-zeros.tif"
SURFACE = ROOT / ".cache/a33_l1_full_surface.npy"
OUT = ROOT / "evidence/a33_l1_full_registry_guard_20261025.json"
EXPECTED_CANDIDATE_SHA256 = "2bbbf7e381720f2242959e3efd6f2437f273afe6e7c48540d769524d2b4e8759"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def rho(left: np.ndarray, right: np.ndarray) -> float | None:
    if left.std() == 0 or right.std() == 0:
        return None
    return float(np.corrcoef(left, right)[0, 1])


def main() -> int:
    specs = json.loads(MANIFEST.read_text())["rasters"]
    with rasterio.open(ROOT / "data/sample_submission.tif") as source:
        footprint = np.isfinite(source.read(1))
        grid = (source.shape, source.crs, source.transform)
    if sha256(CANDIDATE) != EXPECTED_CANDIDATE_SHA256:
        raise ValueError("A33-L1 candidate hash mismatch")
    with rasterio.open(CANDIDATE) as source:
        if (source.shape, source.crs, source.transform) != grid:
            raise ValueError("A33-L1 candidate grid mismatch")
        candidate = (source.read(1) > 0) & footprint
    surface = np.load(SURFACE, allow_pickle=False)
    if surface.shape != footprint.shape or not np.isfinite(surface[footprint]).all():
        raise ValueError("Missing/invalid recorded pre-placement surface")
    ids = np.flatnonzero(footprint)
    sample = np.sort(np.random.default_rng(20261025).choice(ids, 200_000, replace=False))
    surface_rank = rankdata(surface.ravel()[sample], method="average")

    rows = []
    for spec in specs:
        path = ROOT / spec.get("local_path", spec.get("dest", ""))
        if not path.is_file() or sha256(path) != spec["sha256"]:
            raise ValueError(f"Missing/hash-mismatched canonical reference: {spec['id']}")
        with rasterio.open(path) as source:
            if (source.shape, source.crs, source.transform) != grid:
                raise ValueError(f"Reference grid mismatch: {spec['id']}")
            values = source.read(1)
        if not np.isin(values[footprint], (0, 1)).all():
            raise ValueError(f"Non-binary canonical reference: {spec['id']}")
        registry = (values > 0) & footprint
        comparison = binary_comparison(candidate, registry, footprint)
        surface_rho = rho(
            surface_rank,
            rankdata(registry.ravel()[sample].astype(np.uint8), method="average"),
        )
        rows.append(
            {
                "registry_id": spec["id"],
                "registry_sha256": spec["sha256"],
                "preplacement_surface_spearman_rho": surface_rho,
                **comparison,
            }
        )
    maximum_surface = max(row["preplacement_surface_spearman_rho"] for row in rows)
    maximum_final = max(row["spearman_rho"] for row in rows)
    maximum_overlap = max(row["fraction_candidate_within_3px"] for row in rows)
    passed = bool(
        all(row["guard_pass"] for row in rows)
        and maximum_surface <= 0.90
    )
    payload = {
        "schema": 1,
        "date": "2026-10-25",
        "kind": "RELEASE_DUPLICATE_GUARD_NOT_HOLDOUT_DTI",
        "candidate": str(CANDIDATE.relative_to(ROOT)),
        "candidate_sha256": EXPECTED_CANDIDATE_SHA256,
        "canonical_registry_manifest": str(MANIFEST.relative_to(ROOT)),
        "canonical_registry_manifest_sha256": sha256(MANIFEST),
        "registry_count": len(rows),
        "preplacement_sample_pixels": int(sample.size),
        "preplacement_sample_seed": 20261025,
        "spearman_stop_gt": 0.90,
        "candidate_fraction_within_3px_stop_gt": 0.70,
        "max_preplacement_surface_spearman_rho": maximum_surface,
        "max_final_binary_spearman_rho": maximum_final,
        "max_candidate_fraction_within_3px": maximum_overlap,
        "passed": passed,
        "qualification": "Canonical focus subset, not a complete global registry or scientific performance test.",
        "rows": rows,
    }
    OUT.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
    print(json.dumps({key: payload[key] for key in (
        "registry_count", "max_preplacement_surface_spearman_rho",
        "max_final_binary_spearman_rho", "max_candidate_fraction_within_3px", "passed"
    )}, indent=2))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
