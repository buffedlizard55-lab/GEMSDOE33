#!/usr/bin/env python3
"""Byte-level forensic analysis of the nine pinned focus rasters.

The rasters are prior-art comparators only. Reported DTI values are copied as
owner/user claims and are never upgraded to organizer-confirmed evidence.
"""
from __future__ import annotations

import hashlib
import json
from itertools import combinations
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "focus_rasters_20261025.json"
OUT = ROOT / "evidence" / "focus_registry_analysis_20261025.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def phi(a: np.ndarray, b: np.ndarray, domain: np.ndarray) -> float:
    """Pearson phi, equal to Spearman rho for binary arrays with ties."""
    av = a[domain]
    bv = b[domain]
    n11 = int((av & bv).sum())
    n10 = int((av & ~bv).sum())
    n01 = int((~av & bv).sum())
    n00 = int((~av & ~bv).sum())
    den = ((n11 + n10) * (n01 + n00) * (n11 + n01) * (n10 + n00)) ** 0.5
    return float((n11 * n00 - n10 * n01) / den) if den else 0.0


def main() -> int:
    registry = json.loads(REGISTRY.read_text())
    with rasterio.open(ROOT / "data" / "sample_submission.tif") as source:
        template_profile = source.profile
        footprint = np.isfinite(source.read(1))
    with rasterio.open(ROOT / "data" / "labels.tif") as source:
        catalogue = (source.read(1) > 0) & footprint
    distance = distance_transform_edt(~catalogue)

    masks: dict[str, np.ndarray] = {}
    artifacts = []
    for record in registry["rasters"]:
        path = ROOT / record["cache_path"]
        digest = sha256(path)
        if digest != record["sha256"]:
            raise RuntimeError(f"Hash mismatch for {record['id']}")
        with rasterio.open(path) as source:
            if source.shape != (template_profile["height"], template_profile["width"]):
                raise RuntimeError(f"Shape mismatch for {record['id']}")
            if source.crs != template_profile["crs"] or source.transform != template_profile["transform"]:
                raise RuntimeError(f"Grid mismatch for {record['id']}")
            mask = (source.read(1) > 0) & footprint
        masks[record["id"]] = mask
        dots = int(mask.sum())
        artifacts.append(
            {
                "id": record["id"],
                "repository": record["repo"],
                "pinned_commit": record["commit"],
                "path": record["path"],
                "sha256": digest,
                "reported_dti_claim": record["reported_dti"],
                "reported_dti_evidence_class": "OWNER_OR_USER_REPORTED_NOT_ORGANIZER_CONFIRMED",
                "dots": dots,
                "dots_on_catalogue": int((mask & catalogue).sum()),
                "distance_to_catalogue_pixels": {
                    "equal_1": int((mask & (distance == 1)).sum()),
                    "gt_1_le_2": int((mask & (distance > 1) & (distance <= 2)).sum()),
                    "gt_2_le_3": int((mask & (distance > 2) & (distance <= 3)).sum()),
                    "gt_3": int((mask & (distance > 3)).sum()),
                },
            }
        )

    pairwise = []
    for left, right in combinations(registry["rasters"], 2):
        a = masks[left["id"]]
        b = masks[right["id"]]
        intersection = int((a & b).sum())
        union = int((a | b).sum())
        d_to_b = distance_transform_edt(~b)
        d_to_a = distance_transform_edt(~a)
        pairwise.append(
            {
                "left": left["id"],
                "right": right["id"],
                "intersection_dots": intersection,
                "union_dots": union,
                "jaccard": intersection / union,
                "spearman_rho_binary": phi(a, b, footprint),
                "left_subset_of_right": bool(np.all(~a | b)),
                "right_subset_of_left": bool(np.all(~b | a)),
                "left_fraction_within_3px_of_right": float((a & (d_to_b <= 3)).sum() / a.sum()),
                "right_fraction_within_3px_of_left": float((b & (d_to_a <= 3)).sum() / b.sum()),
            }
        )

    d28 = masks["GEMSDOE25-d2p8"]
    d30 = masks["GEMSDOE30-d28"]
    solo = masks["GEMSDOE31-h27-4"]
    champion = masks["GEMSDOE32-h33-2-b2"]
    anderson = masks["GEMSDOE36-anderson"]
    d_to_champion = distance_transform_edt(~champion)
    lineage = {
        "gems25_and_gems30_pixel_identical": bool(np.array_equal(d28, d30)),
        "solo_is_exact_subset_of_d2p8": bool(np.all(~solo | d28)),
        "d2p8_minus_solo_dots": int((d28 & ~solo).sum()),
        "d2p8_minus_solo_all_exactly_1px_from_catalogue": bool(
            np.all(distance[d28 & ~solo] == 1)
        ),
        "b2_is_exact_subset_of_solo": bool(np.all(~champion | solo)),
        "solo_minus_b2_dots": int((solo & ~champion).sum()),
        "solo_minus_b2_all_gt1_le2px_from_catalogue": bool(
            np.all((distance[solo & ~champion] > 1) & (distance[solo & ~champion] <= 2))
        ),
        "b2_is_exact_subset_of_anderson": bool(np.all(~champion | anderson)),
        "anderson_minus_b2_dots": int((anderson & ~champion).sum()),
        "anderson_fraction_within_3px_of_b2": float(
            (anderson & (d_to_champion <= 3)).sum() / anderson.sum()
        ),
    }
    payload = {
        "schema": 1,
        "date": "2026-10-25",
        "scope": "Nine SHA-256-pinned focus rasters; bytes and geometry only",
        "score_evidence_boundary": (
            "No organizer submission receipt was retained or authenticated here. Every reported DTI "
            "value is OWNER_OR_USER_REPORTED_NOT_ORGANIZER_CONFIRMED and is not used as truth."
        ),
        "grid": {
            "shape": list(footprint.shape),
            "epsg": template_profile["crs"].to_epsg(),
            "pixel_size_m": 100,
            "footprint_pixels": int(footprint.sum()),
            "catalogue_pixels": int(catalogue.sum()),
        },
        "artifacts": artifacts,
        "lineage": lineage,
        "pairwise": pairwise,
        "interpretation_limits": [
            "Nested geometry plus reported score ordering is an observational controlled contrast, not authenticated portal evidence.",
            "Artifact dependence prevents treating GEMSDOE31, GEMSDOE32 and GEMSDOE36 as independent replications.",
            "The mapped catalogue is not hidden truth; proximity economics do not prove that every near-catalogue prediction is geologically false.",
            "Spearman/overlap describe raster similarity, not expected competition performance.",
        ],
    }
    OUT.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"output": str(OUT.relative_to(ROOT)), "artifacts": 9, "pairs": len(pairwise)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
