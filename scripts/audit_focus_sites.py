#!/usr/bin/env python3
"""Byte-level forensic audit of the 9 focus sites (GEMSDOE24..36) and 0.2778 lineage.

Reads the SHA-256 verified GeoTIFFs staged in ``.cache/registry_tifs`` and ``docs/downloads``
against the pinned ``labels.tif`` (``existing_faults.tif``), ``sample_submission.tif``, and
``derived_sgmc_faults_100m_u8.tif`` in ``.cache/data``.

All raster set-algebra results, pixel counts, distance-to-catalogue distributions, and
300 m kernel coverage integrals are labelled ``[MEASURED]``. Competition leaderboard scores
from the user brief are labelled ``[OWNER-REPORT]`` (no organizer receipt in this checkout).
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / ".cache" / "data"
REG_DIR = ROOT / ".cache" / "registry_tifs"
OUT_JSON = ROOT / "evidence" / "focus_sites_forensic_20261025.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    with rasterio.open(DATA_DIR / "sample_submission.tif") as src:
        foot = np.isfinite(src.read(1))
    with rasterio.open(DATA_DIR / "labels.tif") as src:
        cat = (src.read(1) > 0) & foot
    with rasterio.open(DATA_DIR / "derived_sgmc_faults_100m_u8.tif") as src:
        sgmc = (src.read(1) > 0) & foot

    d_cat = distance_transform_edt(~cat)
    sgmc_off = sgmc & (d_cat >= 3.0)

    entries = [
        {
            "site": "19GEMSDOE (upstream parent)",
            "submission_id": "h19-5-powerlaw-budget-multiline-corroborated-20260930-e27054cf-nan",
            "reported_score": 0.1922,
            "score_evidence_class": "OWNER-REPORT",
            "path": DATA_DIR / "h19_5_nan.tif",
            "repo_source": "buffedlizard55-lab/GEMSDOE24:inputs/gems19-h19-5-powerlaw-budget-multiline-corroborated-20260930-e27054cf-nan.tif",
        },
        {
            "site": "GEMSDOE24",
            "submission_id": "h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan",
            "reported_score": 0.2477,
            "score_evidence_class": "OWNER-REPORT",
            "path": REG_DIR / "GEMSDOE24_h25-1-d1-5-nan.tif",
            "repo_source": "buffedlizard55-lab/GEMSDOE24:docs/downloads/gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif",
        },
        {
            "site": "GEMSDOE25",
            "submission_id": "dotted-h19-5-d2-8-20261002-e56ea318af89-nan",
            "reported_score": 0.2600,
            "score_evidence_class": "OWNER-REPORT",
            "path": REG_DIR / "GEMSDOE25_d2-8-nan.tif",
            "repo_source": "buffedlizard55-lab/GEMSDOE25:docs/downloads/gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif",
        },
        {
            "site": "GEMSDOE27",
            "submission_id": "topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan",
            "reported_score": 0.2449,
            "score_evidence_class": "OWNER-REPORT",
            "path": REG_DIR / "GEMSDOE27_topo-gap-closure-d1-5-nan.tif",
            "repo_source": "buffedlizard55-lab/GEMSDOE27:docs/downloads/gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif",
        },
        {
            "site": "GEMSDOE28",
            "submission_id": "h27-4-r1-solo-d2-8-20261003-8acb75e1f2cc-nan",
            "reported_score": 0.2708,
            "score_evidence_class": "OWNER-REPORT (GEMSDOE28 site text marks H27-4 unscored/research-only; prompt lists 0.2708)",
            "path": REG_DIR / "GEMSDOE28_h27-4-r1-solo-d2-8-nan.tif",
            "repo_source": "buffedlizard55-lab/GEMSDOE28:docs/downloads/gems28-h27-4-r1-solo-d2-8-20261003-8acb75e1f2cc-nan.tif",
        },
        {
            "site": "GEMSDOE28",
            "submission_id": "h32-1-prethin-tip-euler-d2-8-20261003-31e35eee884e-nan",
            "reported_score": 0.2649,
            "score_evidence_class": "OWNER-REPORT",
            "path": REG_DIR / "GEMSDOE28_h32-1-prethin-tip-euler-d2-8-nan.tif",
            "repo_source": "buffedlizard55-lab/GEMSDOE28:docs/downloads/gems28-h32-1-prethin-tip-euler-d2-8-20261003-31e35eee884e-nan.tif",
        },
        {
            "site": "GEMSDOE28",
            "submission_id": "h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan",
            "reported_score": 0.2710,
            "score_evidence_class": "OWNER-REPORT",
            "path": REG_DIR / "GEMSDOE28_h36-1-rung30-blind-r1-nan.tif",
            "repo_source": "buffedlizard55-lab/GEMSDOE28:docs/downloads/gems28-h36-1-rung30-blind-r1-nan.tif",
        },
        {
            "site": "GEMSDOE28",
            "submission_id": "h38-1-hf-euler-r30-r1-20261003-56a9f473edc7-nan",
            "reported_score": 0.2707,
            "score_evidence_class": "OWNER-REPORT",
            "path": REG_DIR / "GEMSDOE28_h38-1-hf-euler-r30-r1-nan.tif",
            "repo_source": "buffedlizard55-lab/GEMSDOE28:docs/downloads/gems28-h38-1-hf-euler-r30-r1-nan.tif",
        },
        {
            "site": "GEMSDOE30",
            "submission_id": "d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca",
            "reported_score": 0.2600,
            "score_evidence_class": "OWNER-REPORT",
            "path": REG_DIR / "GEMSDOE30_d28-poisson300m-offcat-44090.tif",
            "repo_source": "buffedlizard55-lab/GEMSDOE30:docs/downloads/gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif",
        },
        {
            "site": "GEMSDOE31",
            "submission_id": "h27-4-solo-d28-20261004-8acb75e1-nan",
            "reported_score": 0.2708,
            "score_evidence_class": "OWNER-REPORT",
            "path": REG_DIR / "GEMSDOE31_h27-4-solo-d28-nan.tif",
            "repo_source": "buffedlizard55-lab/GEMSDOE31:docs/downloads/gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif",
        },
        {
            "site": "GEMSDOE32",
            "submission_id": "h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros",
            "reported_score": 0.2778,
            "score_evidence_class": "OWNER-REPORT",
            "path": REG_DIR / "GEMSDOE32_h33-2-b2-zeros.tif",
            "repo_source": "buffedlizard55-lab/GEMSDOE32:docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif",
        },
        {
            "site": "GEMSDOE33",
            "submission_id": "h33d-analog-tip-stepover-r30-20261004-cb490425926e",
            "reported_score": 0.2632,
            "score_evidence_class": "OWNER-REPORT",
            "path": ROOT / "docs/downloads/GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif",
            "repo_source": "buffedlizard55-lab/GEMSDOE33:docs/downloads/GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif",
        },
        {
            "site": "GEMSDOE36",
            "submission_id": "anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros",
            "reported_score": 0.2750,
            "score_evidence_class": "OWNER-REPORT",
            "path": REG_DIR / "GEMSDOE36_anderson-geothermal-pinn-38854-zeros.tif",
            "repo_source": "buffedlizard55-lab/GEMSDOE36:docs/downloads/gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif",
        },
    ]

    active_offcat = foot & ~cat
    masks = {}
    rows = []

    for item in entries:
        p = item["path"]
        with rasterio.open(p) as src:
            arr = src.read(1)
        m = np.isfinite(arr) & (arr > 0) & foot
        masks[item["submission_id"]] = m
        dc = d_cat[m]
        d_pred = distance_transform_edt(~m)
        kern = np.maximum(1.0 - d_pred / 3.0, 0.0)
        offcat_kernel_integral = float(kern[active_offcat].sum())
        sgmc_tpw = float(kern[sgmc_off].sum())
        sgmc_fpw = float((1.0 - np.maximum(1.0 - distance_transform_edt(~sgmc_off)[m] / 3.0, 0.0)).sum())
        sgmc_fnw = float(sgmc_off.sum()) - sgmc_tpw
        sgmc_dti = sgmc_tpw / (sgmc_tpw + 0.2 * sgmc_fpw + 0.8 * sgmc_fnw + 1e-7)

        rows.append({
            "site": item["site"],
            "submission_id": item["submission_id"],
            "repo_source": item["repo_source"],
            "sha256": sha256_file(p),
            "bytes": p.stat().st_size,
            "reported_score": item["reported_score"],
            "score_evidence_class": item["score_evidence_class"],
            "measured_positive_pixels": int(m.sum()),
            "measured_footprint_fraction": round(float(m.sum() / foot.sum()), 6),
            "outside_footprint_all_finite": bool(np.isfinite(arr).all()),
            "distance_to_catalogue_breakdown": {
                "d_eq_0_on_catalogue": int((dc == 0).sum()),
                "d_in_0_1px_100m": int(((dc > 0) & (dc <= 1.0)).sum()),
                "d_in_1_2px_200m": int(((dc > 1.0) & (dc <= 2.0)).sum()),
                "d_in_2_3px_300m": int(((dc > 2.0) & (dc <= 3.0)).sum()),
                "d_gt_3px_beyond_300m": int((dc > 3.0).sum()),
            },
            "offcat_300m_kernel_integral": round(offcat_kernel_integral, 2),
            "offcat_kernel_integral_per_dot": round(offcat_kernel_integral / max(int(m.sum()), 1), 4),
            "sgmc_offcat_proxy_dti": round(float(sgmc_dti), 6),
        })

    m_h19 = masks["h19-5-powerlaw-budget-multiline-corroborated-20260930-e27054cf-nan"]
    m_d28 = masks["dotted-h19-5-d2-8-20261002-e56ea318af89-nan"]
    m_h274 = masks["h27-4-r1-solo-d2-8-20261003-8acb75e1f2cc-nan"]
    m_b2 = masks["h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros"]
    m_36 = masks["anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros"]

    exact_identities = {
        "d28_is_strict_subset_of_h19_5": bool(np.all(m_h19[m_d28])),
        "gemsdoe30_d28_equals_gemsdoe25_d28": bool(
            np.array_equal(masks["d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca"], m_d28)
        ),
        "h27_4_equals_d28_and_d_cat_gt_1px": bool(np.array_equal(m_h274, m_d28 & (d_cat > 1.0))),
        "gemsdoe31_h27_4_equals_gemsdoe28_h27_4": bool(
            np.array_equal(masks["h27-4-solo-d28-20261004-8acb75e1-nan"], m_h274)
        ),
        "gemsdoe32_h33_2_b2_equals_d28_and_d_cat_gt_2px": bool(
            np.array_equal(m_b2, m_d28 & (d_cat > 2.0))
        ),
        "gemsdoe32_h33_2_b2_equals_h27_4_and_d_cat_gt_2px": bool(
            np.array_equal(m_b2, m_h274 & (d_cat > 2.0))
        ),
        "gemsdoe36_contains_gemsdoe32_h33_2_b2_as_exact_subset": bool(np.all(m_36[m_b2])),
        "gemsdoe36_extra_dots_over_gemsdoe32_h33_2_b2": int((m_36 & ~m_b2).sum()),
        "d28_dots_removed_at_b1_100m": int((m_d28 & (d_cat <= 1.0)).sum()),
        "d28_dots_removed_at_b2_100m_to_200m": int((m_d28 & (d_cat > 1.0) & (d_cat <= 2.0)).sum()),
        "d28_dots_remaining_at_b2": int(m_b2.sum()),
    }

    report = {
        "schema": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "evidence_note": (
            "Pixel counts, SHA-256 digests, distance-to-catalogue breakdowns, and exact boolean "
            "set identities are [MEASURED] directly from the staged repository GeoTIFFs. "
            "Competition scores are [OWNER-REPORT] from the user prompt and sibling repository "
            "pages (no organizer submission receipt is stored in this repository)."
        ),
        "exact_boolean_identities_measured": exact_identities,
        "focus_site_submissions": rows,
    }
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_JSON} with {len(rows)} focus submissions; all exact identities={exact_identities}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
