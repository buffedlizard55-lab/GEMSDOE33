#!/usr/bin/env python3
"""Nine-site best-file audit (2026-10-29): byte identity, format, dot overlap and uniqueness.

Reads ``registry/nine_site_best_files_20261029.json`` (the best-reported file for each of the nine
focus GEMSDOE sites), fetches each file by its git blob SHA-1 from the owner GitHub repository,
verifies the blob hash and byte count, and then measures:

* byte identity (SHA-256) and pixel identity of the dot set (value > 0 inside the template footprint);
* strict format against the template grid (single band, float32, EPSG:32611, same shape and
  transform, finite and in [0, 1] inside the footprint; outside cells zero or NaN);
* exact subset relations between dot sets;
* the repository's duplicate guard (``gemsdoe33.novelty.binary_comparison``): Spearman/phi over the
  footprint and the fraction of each candidate's dots within 3 px of a registry raster's dots;
* the same guard against the 22-raster pinned focus registry (``registry/focus_rasters_20261026_r3.json``).

Outputs ``evidence/nine_site_audit_20261029.json`` and the identical ``docs/data/nine_site_audit.json``
used by the static site. Comparison only: none of these files is used as a feature, label or score.

Nothing here logs in to DrivenData, uploads, polls a leaderboard or writes a score. Scores are copied
from the manifest as USER-REPORTED values and are never estimated.

Usage::

    python scripts/nine_site_audit.py            # fetch if needed, audit, write outputs
    python scripts/nine_site_audit.py --offline  # require already-cached bytes (no network)
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gemsdoe33.novelty import binary_comparison  # noqa: E402

MANIFEST = ROOT / "registry" / "nine_site_best_files_20261029.json"
REGISTRY = ROOT / "registry" / "focus_rasters_20261026_r3.json"
TEMPLATE = ROOT / "data" / "sample_submission.tif"
LABELS = ROOT / "data" / "labels.tif"
CACHE = ROOT / "data" / "nine_site"
EVIDENCE = ROOT / "evidence" / "nine_site_audit_20261029.json"
SITE_JSON = ROOT / "docs" / "data" / "nine_site_audit.json"
RADIUS_PX = 3.0
OVERLAP_TRIGGER = 0.70
RHO_TRIGGER = 0.90
EXPECTED_CRS = "EPSG:32611"


def git_blob_sha1(data: bytes) -> str:
    """Git's object id for a blob: sha1(b"blob <len>\\0" + content)."""
    return hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_blob(repo: str, blob_sha1: str, expected_bytes: int, *, offline: bool) -> bytes:
    """Return the git blob bytes, verifying size and blob SHA-1. Caches under data/nine_site/."""
    CACHE.mkdir(parents=True, exist_ok=True)
    cached = CACHE / f"{blob_sha1}.bin"
    if cached.is_file():
        data = cached.read_bytes()
    else:
        if offline:
            raise FileNotFoundError(f"offline: {cached} is not cached")
        out = subprocess.run(
            ["gh", "api", f"repos/{repo}/git/blobs/{blob_sha1}", "--jq", ".content"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        data = base64.b64decode(out)
        cached.write_bytes(data)
    if len(data) != expected_bytes:
        raise ValueError(f"{repo} {blob_sha1}: {len(data)} bytes, expected {expected_bytes}")
    if git_blob_sha1(data) != blob_sha1:
        raise ValueError(f"{repo} {blob_sha1}: git blob SHA-1 mismatch")
    return data


def load_array(data_or_path) -> np.ndarray:
    """Read band 1 as float64 from a path or in-memory bytes (via a GDAL /vsimem/ file)."""
    if isinstance(data_or_path, (bytes, bytearray)):
        from rasterio.io import MemoryFile

        with MemoryFile(bytes(data_or_path)) as memfile, memfile.open() as src:
            return src.read(1).astype(np.float64)
    with rasterio.open(data_or_path) as src:
        return src.read(1).astype(np.float64)


def raster_meta(data_or_path) -> dict:
    if isinstance(data_or_path, (bytes, bytearray)):
        from rasterio.io import MemoryFile

        with MemoryFile(bytes(data_or_path)) as memfile, memfile.open() as src:
            return _meta_from(src)
    with rasterio.open(data_or_path) as src:
        return _meta_from(src)


def _meta_from(src) -> dict:
    epsg = src.crs.to_epsg() if src.crs else None
    return {
        "driver": src.driver,
        "count": int(src.count),
        "dtype": src.dtypes[0],
        "width": int(src.width),
        "height": int(src.height),
        "crs_epsg": epsg,
        "transform": [float(v) for v in src.transform][:6],
    }


def analyse(name: str, arr: np.ndarray, meta: dict, template: dict, footprint: np.ndarray,
            catalogue: np.ndarray) -> dict:
    """Format + dot statistics for one raster. ``arr`` is band 1 as float64."""
    inside = arr[footprint]
    finite_in = np.isfinite(inside)
    outside = arr[~footprint]
    vals_in = inside[finite_in]
    dots = np.zeros(arr.shape, dtype=bool)
    dots[footprint] = np.nan_to_num(arr[footprint], nan=0.0) > 0.0
    uniq = np.unique(vals_in)
    format_checks = {
        "single_band": meta["count"] == 1,
        "float32": meta["dtype"] == "float32",
        "crs_is_EPSG_32611": meta["crs_epsg"] == 32611,
        "shape_matches_template": (meta["height"], meta["width"]) == (template["height"], template["width"]),
        "transform_matches_template": meta["transform"] == template["transform"],
        "footprint_all_finite": bool(finite_in.all()),
        "footprint_in_0_1": bool(vals_in.size and vals_in.min() >= 0.0 and vals_in.max() <= 1.0),
        "outside_footprint_zero_or_nan": bool(np.all((outside == 0) | np.isnan(outside))),
    }
    return {
        "name": name,
        "meta": meta,
        "format_checks": format_checks,
        "format_pass": all(format_checks.values()),
        "footprint_cells": int(footprint.sum()),
        "footprint_nan_cells": int((~finite_in).sum()),
        "footprint_min": float(vals_in.min()) if vals_in.size else None,
        "footprint_max": float(vals_in.max()) if vals_in.size else None,
        "is_binary_0_1": bool(np.isin(uniq, (0.0, 1.0)).all()) if uniq.size else False,
        "distinct_values_footprint": int(uniq.size),
        "n_dots": int(dots.sum()),
        "dots_on_catalogue": int((dots & catalogue).sum()),
        "dots_off_catalogue": int((dots & ~catalogue).sum()),
    }


def dots_of(arr: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    """Boolean dot mask: value > 0 inside the footprint (NaN treated as 0), False outside."""
    m = np.zeros(arr.shape, dtype=bool)
    m[footprint] = np.nan_to_num(arr[footprint], nan=0.0) > 0.0
    return m


def near3(mask: np.ndarray) -> np.ndarray:
    """Cells within 3 px (Euclidean) of any True cell in ``mask``."""
    if not mask.any():
        return np.zeros_like(mask, dtype=bool)
    return distance_transform_edt(~mask) <= RADIUS_PX


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--offline", action="store_true", help="use only cached bytes; no network")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text())
    registry = json.loads(REGISTRY.read_text())

    template_meta = raster_meta(TEMPLATE)
    template_arr = load_array(TEMPLATE)
    footprint = np.isfinite(template_arr)
    catalogue = (load_array(LABELS) > 0) & footprint
    template = dict(template_meta)

    # --- 1. The nine pinned site files (fetched by git blob) ---------------------------------
    nine = []
    for entry in manifest["entries"]:
        data = fetch_blob(entry["repo"], entry["blob_sha1"], entry["bytes"], offline=args.offline)
        arr = load_array(data)
        meta = raster_meta(data)
        rec = analyse(f"{entry['site']}/{entry['user_reported_name']}", arr, meta, template, footprint, catalogue)
        dot_mask = dots_of(arr, footprint)
        rec.update({
            "site": entry["site"],
            "role": entry.get("role", "site_listed"),
            "user_reported_name": entry["user_reported_name"],
            "reported_score_USER_REPORTED": entry["reported_score"],
            "repo": entry["repo"],
            "path": entry["path"],
            "blob_sha1": entry["blob_sha1"],
            "bytes": entry["bytes"],
            "sha256": sha256_bytes(data),
            "site_url": entry["site_url"],
        })
        nine.append((rec, dot_mask, data))
        del arr

    # --- 2. The 22-raster pinned focus registry (comparison only) ----------------------------
    registry_rows = []
    for r in registry["rasters"]:
        rel = r.get("dest") or r.get("local_path")
        path = ROOT / rel
        if not path.is_file():
            raise FileNotFoundError(f"registry raster missing: {rel} (run scripts/restore_focus_registry_r3.py)")
        data = path.read_bytes()
        digest = sha256_bytes(data)
        if digest != r["sha256"]:
            raise ValueError(f"registry SHA-256 mismatch for {r['id']}")
        arr = load_array(data)
        meta = raster_meta(data)
        rec = analyse(r["id"], arr, meta, template, footprint, catalogue)
        rec.update({"site": r.get("site"), "sha256": digest, "path": rel,
                    "reported_dti_USER_REPORTED": r.get("reported_dti")})
        registry_rows.append((rec, dots_of(arr, footprint), data))
        del arr

    # --- 3. Byte / pixel identity ------------------------------------------------------------
    everything = nine + registry_rows
    if len({rec["name"] for rec, _, _ in everything}) != len(everything):
        raise ValueError("duplicate raster names in audit set")
    byte_groups: dict[str, list[str]] = {}
    for rec, _, _ in everything:
        byte_groups.setdefault(rec["sha256"], []).append(rec["name"])
    dot_masks = {rec["name"]: m for rec, m, _ in everything}
    dot_groups: dict[str, list[str]] = {}
    for name, m in dot_masks.items():
        dot_groups.setdefault(hashlib.sha256(np.packbits(m).tobytes()).hexdigest(), []).append(name)
    identical_byte_groups = [v for v in byte_groups.values() if len(v) > 1]
    identical_dot_groups = [v for v in dot_groups.values() if len(v) > 1]

    # --- 4. Duplicate guard: the nine vs everything (excluding self and byte-identical copies) --
    near = {name: near3(m) for name, m in dot_masks.items()}
    names = [rec["name"] for rec, _, _ in everything]
    site_names = [rec["name"] for rec, _, _ in nine]
    pairs = {}
    for a in site_names:
        for b in names:
            if a == b:
                continue
            ca, cb = dot_masks[a], dot_masks[b]
            res = binary_comparison(
                ca.astype(np.uint8), cb.astype(np.uint8), footprint, near_other=near[b]
            )
            pairs.setdefault(a, {})[b] = {
                "spearman_phi": None if res["spearman_rho"] is None else round(res["spearman_rho"], 6),
                "frac_dots_within_3px": None if res["fraction_candidate_within_3px"] is None
                else round(res["fraction_candidate_within_3px"], 6),
                "pixel_identical_dots": bool(np.array_equal(ca, cb)),
                "a_dots_exactly_in_b": int((ca & cb).sum()),
                "a_subset_of_b": bool(not (ca & ~cb).any()) and bool(ca.any()),
                "duplicate_trigger": bool(res["duplicate_trigger"]),
            }

    # Duplicate verdict per site file. "Self" = the same bytes (its own registry copy) and is not a
    # duplicate. Everything else (different bytes) is another submission and is compared.
    sha_of = {rec["name"]: rec["sha256"] for rec, _, _ in everything}
    site_verdicts = []
    for rec, _, _ in nine:
        name = rec["name"]
        self_copies = [k for k in names if k != name and sha_of[k] == sha_of[name]]
        others = {k: v for k, v in pairs[name].items() if sha_of[k] != sha_of[name]}
        identical = sorted(k for k, v in others.items() if v["pixel_identical_dots"])
        triggers = sorted(k for k, v in others.items() if v["duplicate_trigger"])
        worst_overlap = max(others.items(), key=lambda kv: kv[1]["frac_dots_within_3px"] or 0.0, default=(None, None))
        worst_rho = max(others.items(), key=lambda kv: kv[1]["spearman_phi"] or -1.0, default=(None, None))
        site_verdicts.append({
            "site": rec["site"],
            "role": rec["role"],
            "name": name,
            "reported_score_USER_REPORTED": rec["reported_score_USER_REPORTED"],
            "sha256": rec["sha256"],
            "n_dots": rec["n_dots"],
            "format_pass": rec["format_pass"],
            "same_bytes_registry_copies": self_copies,
            "pixel_identical_dots_to_other_submission": identical,
            "duplicate_trigger_vs_other_submissions": triggers,
            "max_frac_dots_within_3px_vs_other_submission": None if worst_overlap[0] is None else {
                "vs": worst_overlap[0], "value": worst_overlap[1]["frac_dots_within_3px"]},
            "max_spearman_phi_vs_other_submission": None if worst_rho[0] is None else {
                "vs": worst_rho[0], "value": worst_rho[1]["spearman_phi"]},
            "unique_under_guard": not triggers and not identical,
        })

    # --- 5. Forensic recount of the B2 deletion step (independent of the registry note) -------
    dcat = distance_transform_edt(~catalogue)

    def bins(mask: np.ndarray) -> dict:
        d = dcat[mask]
        return {"d_le_1px": int((d <= 1).sum()), "d_1_to_2px": int(((d > 1) & (d <= 2)).sum()),
                "d_2_to_3px": int(((d > 2) & (d <= 3)).sum()), "d_gt_3px": int((d > 3).sum())}

    def named(prefix: str):
        hits = [k for k in dot_masks if k.startswith(prefix)]
        if len(hits) != 1:
            raise ValueError(f"expected one raster for {prefix!r}, found {hits}")
        return hits[0]

    b2 = named("GEMSDOE32/h33-h33-2-b2")
    h274_solo = named("GEMSDOE31/h27-4-solo-d28")
    forensic = []
    for parent_key in (h274_solo, named("GEMSDOE28/h27-4-r1-solo-d2-8")):
        parent, child = dot_masks[parent_key], dot_masks[b2]
        removed = parent & ~child
        added = child & ~parent
        forensic.append({
            "parent": parent_key, "child": b2,
            "parent_dots": int(parent.sum()), "child_dots": int(child.sum()),
            "child_is_exact_subset_of_parent": bool(not added.any()),
            "removed_dots": int(removed.sum()), "added_dots": int(added.sum()),
            "removed_by_catalogue_distance": bins(removed),
            "child_by_catalogue_distance": bins(child),
            "child_dots_on_catalogue": int((child & catalogue).sum()),
        })

    result = {
        "schema": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "script": "scripts/nine_site_audit.py",
        "manifest": "registry/nine_site_best_files_20261029.json",
        "registry": "registry/focus_rasters_20261026_r3.json",
        "provenance_warning": manifest["provenance_warning"],
        "evidence_class": "MEASURED from owner-repo git blobs (byte/pixel) and local raster arithmetic; scores are USER-REPORTED and are NOT estimated",
        "guard": {
            "rule": "duplicate if Spearman/phi > 0.90 OR > 70% of candidate dots within 3 px of a registry raster's dots (repo duplicate guard)",
            "overlap_trigger": OVERLAP_TRIGGER, "rho_trigger": RHO_TRIGGER,
            "note": "Dot-level guard; for binary rasters the surface and dot sets coincide.",
        },
        "template": {"path": "data/sample_submission.tif", "crs_epsg": template_meta["crs_epsg"],
                     "shape": [template_meta["height"], template_meta["width"]],
                     "transform": template_meta["transform"], "footprint_cells": int(footprint.sum()),
                     "warning": "template values equal the catalogue labels (IR-SAMPLE-LABEL-01); used only for grid/footprint"},
        "catalogue_cells": int(catalogue.sum()),
        "nine_site_files": [rec for rec, _, _ in nine],
        "registry_files": [rec for rec, _, _ in registry_rows],
        "identical_bytes_groups": identical_byte_groups,
        "identical_dot_set_groups": identical_dot_groups,
        "site_verdicts": site_verdicts,
        "pairwise_nine_vs_all": pairs,
        "b2_forensic_recount": forensic,
    }
    text = json.dumps(result, indent=2, allow_nan=False) + "\n"
    EVIDENCE.write_text(text)
    SITE_JSON.parent.mkdir(parents=True, exist_ok=True)
    SITE_JSON.write_text(text)
    print(f"wrote {EVIDENCE.relative_to(ROOT)} and {SITE_JSON.relative_to(ROOT)}")
    for v in site_verdicts:
        score = "  n/a " if v["reported_score_USER_REPORTED"] is None else f"{v['reported_score_USER_REPORTED']:.4f}"
        print(f"  {v['site']:9s} {score}  {v['name'][:44]:44s} dots={v['n_dots']:>7,}  "
              f"format={v['format_pass']}  unique_under_guard={v['unique_under_guard']}  "
              f"triggers={len(v['duplicate_trigger_vs_other_submissions'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
