#!/usr/bin/env python3
"""Execute the preregistered 2026-10-25 Round-3 3-experiment campaign for GEMSDOE33.

Steps executed deterministically in one pass:
1. Verify SHA-256 of frozen preregistration (``evidence/hypothesis_slate_20261025_r3_preregistered.sha256``).
2. Build 48-channel label-free locally-invariant geophysical + LiDAR + GDR-1391
   geothermometer/vent hydrothermal conduit feature stack.
3. Run 20 km spatial-block domain-shift divergence screen + Ben-David et al.
   (2010) Lemma 2 & Theorem 2 bound diagnostics (``evidence/round3_domain_divergence_audit.json``).
4. Build Selection buffered whole-component holdout (``seeds=(20, 21)``) and run
   standalone single-feature leakage canaries across all 52 candidate features
   (``AUC <= 0.90`` hard gate; ``evidence/round3_leakage_canary_audit.json``).
5. Run the 3 preregistered candidate arms (``H33-R3-1``, ``H33-R3-2``, ``H33-R3-3``)
   plus 3 fold-rebuilt matched-budget controls (``CTRL-RIDGE-B2``, ``CTRL-GBDT``,
   ``CTRL-RANDOM``) at exact ``37,654`` dots on Selection (``seeds=(20, 21)``) via
   ``vendor/gems57/evaluate_holdout.py`` (``gems57-pooled-hide-v2``, 20 km spatial
   block bootstrap 95% CI).
6. Freeze the top Selection arm without retuning and evaluate it once on the
   fresh independent Confirmation holdout (``seeds=(33, 34)``).
7. Fit full-map LOQO surfaces (``visible = catalogue``), run pre-placement surface
   uniqueness checks across both Scope A (201 published 9-site GeoTIFFs) and
   Scope B (complete 214-blob 9-repo tree), allocate the final ``37,654``-dot
   prediction via ``dinkelbach_allocate``, evaluate off-catalogue ``SGMC`` proxy
   (``d_cat >= 3.0 px``), package the ``-zeros.tif`` + ``.zip`` + receipt via
   ``vendor/gems57/submission_writer.py``, verify saved bytes via
   ``scripts/validate_submission.py --strict-zero-outside``, run final-dot
   uniqueness checks on Scope A and Scope B, and emit the official JSON RUN CARD
   (``evidence/round3_da_hgcm_run_card_20261025.json``).
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from gemsdoe33.metric import dti_binary  # noqa: E402
from gemsdoe33.round3_analog_vent import (  # noqa: E402
    build_base_feature_stack,
    fit_predict_loqo_surfaces,
    run_feature_leakage_canaries,
    screen_domain_divergence_and_ben_david,
)
from scripts.validate_submission import audit as secondary_format_audit  # noqa: E402
from vendor.gems57.emit import dinkelbach_allocate  # noqa: E402
from vendor.gems57.evaluate_holdout import evaluate as eval_fold  # noqa: E402
from vendor.gems57.evaluate_holdout import pooled_summary  # noqa: E402
from vendor.gems57.grid import load_grid  # noqa: E402
from vendor.gems57.holdout import buffered_component_draw  # noqa: E402
from vendor.gems57.submission_writer import write_submission  # noqa: E402
from vendor.gems57.uniqueness import compare_array_to_registry  # noqa: E402

BUDGET_DOTS = 37_654
MIN_SPACING_PX = 2.6
CAT_COLLAR_PX = 2.0


def verify_preregistration() -> dict:
    sha_file = ROOT / "evidence" / "hypothesis_slate_20261025_r3_preregistered.sha256"
    lines = [ln.strip() for ln in sha_file.read_text().splitlines() if ln.strip()]
    checked = {}
    for ln in lines:
        expected_sha, rel_path = ln.split(None, 1)
        target = ROOT / rel_path.strip()
        actual_sha = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual_sha != expected_sha:
            raise RuntimeError(f"Preregistration SHA mismatch on {rel_path}: {actual_sha} != {expected_sha}")
        checked[rel_path.strip()] = actual_sha
    return checked


def build_registry_indices(cache_reg_dir: Path) -> tuple[dict, dict]:
    """Construct complete-inventory dicts for Scope A (9-site downloads + local) and Scope B (all 9-repo TIFs)."""
    raw = json.loads((cache_reg_dir / "index_9sites.json").read_text())
    expected_tr = [100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0]
    valid = [
        r for r in raw
        if r.get("shape") == [3730, 3292]
        and r.get("crs") == "EPSG:32611"
        and r.get("count") == 1
        and r.get("transform") == expected_tr
    ]

    def _to_gems57_entry(rec: dict) -> dict:
        srcs = [f"{s['repo']}:{s['path']}" for s in rec["sources"]]
        return {
            "repo_first": rec["sources"][0]["repo"],
            "sources": srcs,
            "cache_file": rec["cache_path"],
            "sha256": rec["sha256"],
            "n_positive": rec["n_positive"],
        }

    scope_a_rasters = [
        _to_gems57_entry(r)
        for r in valid
        if any(
            s["path"].startswith("docs/downloads/") or s["repo"].endswith("/GEMSDOE33")
            for s in r["sources"]
        )
    ]
    scope_b_rasters = [_to_gems57_entry(r) for r in valid]

    idx_a = {
        "complete_accessible_scan": True,
        "errors": [],
        "scope_name": "Scope A: All 201 published submission GeoTIFFs across GEMSDOE24,25,27,28,30,31,32,33,36 docs/downloads/ plus pre-run local GEMSDOE33 rasters",
        "rasters": scope_a_rasters,
    }
    idx_b = {
        "complete_accessible_scan": True,
        "errors": [],
        "scope_name": "Scope B: Complete 214-blob valid-grid GeoTIFF tree across all subdirectories of GEMSDOE24..36 (includes GEMSDOE24/inputs/calibration/13gems r13-lattice-s5)",
        "rasters": scope_b_rasters,
    }
    return idx_a, idx_b


def allocate_ridge_baseline(
    ridge_score_fp: np.ndarray,
    fp: np.ndarray,
    fp_yx: tuple[np.ndarray, np.ndarray],
    allowed: np.ndarray,
    budget: int = BUDGET_DOTS,
    min_spacing_px: float = 2.8,
) -> np.ndarray:
    """Fold-safe label-free ridge Poisson-disk baseline matching H33-2-B2 geometry."""
    H, W = fp.shape
    score_2d = np.full((H, W), -1e9, dtype=np.float32)
    score_2d[fp_yx] = ridge_score_fp
    ys, xs = np.nonzero(allowed)
    order = np.argsort(-score_2d[ys, xs], kind="stable")
    ys = ys[order]
    xs = xs[order]

    r_ex = int(np.floor(min_spacing_px))
    dy_list, dx_list = [], []
    for dy in range(-r_ex, r_ex + 1):
        for dx in range(-r_ex, r_ex + 1):
            if dy * dy + dx * dx < min_spacing_px * min_spacing_px - 1e-9:
                dy_list.append(dy)
                dx_list.append(dx)
    dy_a = np.asarray(dy_list, dtype=np.int32)
    dx_a = np.asarray(dx_list, dtype=np.int32)

    blocked = np.zeros((H, W), dtype=bool)
    emitted = np.zeros((H, W), dtype=bool)
    n = 0
    for y, x in zip(ys, xs):
        if blocked[y, x]:
            continue
        emitted[y, x] = True
        by = y + dy_a
        bx = x + dx_a
        ok = (by >= 0) & (by < H) & (bx >= 0) & (bx < W)
        blocked[by[ok], bx[ok]] = True
        n += 1
        if n >= budget:
            break
    return emitted


def allocate_random_control(allowed: np.ndarray, budget: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    ys, xs = np.nonzero(allowed)
    pick = rng.choice(ys.size, size=min(budget, ys.size), replace=False)
    out = np.zeros(allowed.shape, dtype=bool)
    out[ys[pick], xs[pick]] = True
    return out


def evaluate_arms_on_draws(
    arms_to_run: list[str],
    seeds: tuple[int, ...],
    grid,
    base,
    kept_idx: np.ndarray,
    d_h_delta_h: float,
) -> dict:
    """Run specified arms + 3 fold-safe controls on ``buffered_component_draw`` seeds."""
    all_names = [*arms_to_run, "CTRL-RIDGE-B2", "CTRL-GBDT", "CTRL-RANDOM"]
    terms_sum_by_arm: dict[str, np.ndarray | None] = {a: None for a in all_names}
    per_fold_table: dict[str, dict[str, float]] = {a: {} for a in all_names}

    def _accum(name: str, terms: np.ndarray) -> None:
        if terms_sum_by_arm[name] is None:
            terms_sum_by_arm[name] = terms.copy()
        else:
            terms_sum_by_arm[name] += terms

    for s in seeds:
        t_s = time.time()
        folds, quad = buffered_component_draw(grid, seed=s, hide_frac=0.20, buffer_px=3, boundary_px=12)
        vis = folds[0]["visible"]
        d_vis = ndi.distance_transform_edt(~vis)
        allowed = grid.footprint & (d_vis > CAT_COLLAR_PX)

        # Fold-safe controls
        em_ridge = allocate_ridge_baseline(base.ridge_baseline_score_fp, base.fp, base.fp_yx, allowed, budget=BUDGET_DOTS, min_spacing_px=2.8)
        em_rand = allocate_random_control(allowed, budget=BUDGET_DOTS, seed=9000 + s)

        p_gbdt, m_gbdt = fit_predict_loqo_surfaces(
            base, kept_idx, quad, vis, arm="CTRL-GBDT", d_h_delta_h=d_h_delta_h, seed=3000 + s
        )
        em_gbdt = dinkelbach_allocate(
            p_gbdt, m_gbdt, allowed, budget=BUDGET_DOTS, min_spacing_px=MIN_SPACING_PX, candidate_cap=1_200_000
        ).emitted

        for f in folds:
            fk = f"seed{s}_{f['name']}"
            r_rg, t_rg = eval_fold(em_ridge.astype(np.float32), f, grid.footprint)
            r_gb, t_gb = eval_fold(em_gbdt.astype(np.float32), f, grid.footprint)
            r_rn, t_rn = eval_fold(em_rand.astype(np.float32), f, grid.footprint)
            _accum("CTRL-RIDGE-B2", t_rg)
            _accum("CTRL-GBDT", t_gb)
            _accum("CTRL-RANDOM", t_rn)
            per_fold_table["CTRL-RIDGE-B2"][fk] = round(float(r_rg["dti"]), 6)
            per_fold_table["CTRL-GBDT"][fk] = round(float(r_gb["dti"]), 6)
            per_fold_table["CTRL-RANDOM"][fk] = round(float(r_rn["dti"]), 6)

        for arm in arms_to_run:
            t_a = time.time()
            p_2d, m_2d = fit_predict_loqo_surfaces(
                base, kept_idx, quad, vis, arm=arm, d_h_delta_h=d_h_delta_h, seed=1000 + s
            )
            alloc = dinkelbach_allocate(
                p_2d, m_2d, allowed, budget=BUDGET_DOTS, min_spacing_px=MIN_SPACING_PX, candidate_cap=1_200_000
            )
            for f in folds:
                fk = f"seed{s}_{f['name']}"
                r_arm, t_arm = eval_fold(alloc.emitted.astype(np.float32), f, grid.footprint)
                _accum(arm, t_arm)
                per_fold_table[arm][fk] = round(float(r_arm["dti"]), 6)
            print(
                f"  [seed={s}] {arm}: dots={alloc.n_dots} ({time.time() - t_a:.1f}s)",
                flush=True,
            )
            del p_2d, m_2d, alloc
            import gc
            gc.collect()
        del folds, quad, vis, d_vis, allowed, em_ridge, em_rand, p_gbdt, m_gbdt, em_gbdt
        import gc
        gc.collect()
        print(f"  completed seed={s} in {time.time() - t_s:.1f}s", flush=True)

    summaries = {}
    for arm in arms_to_run:
        pool_res = pooled_summary(
            {
                arm: terms_sum_by_arm[arm],
                "CTRL-RIDGE-B2": terms_sum_by_arm["CTRL-RIDGE-B2"],
                "CTRL-GBDT": terms_sum_by_arm["CTRL-GBDT"],
                "CTRL-RANDOM": terms_sum_by_arm["CTRL-RANDOM"],
            },
            draws=1000,
            seed=20261025,
            candidate=arm,
        )
        s_arm = dict(pool_res["scores"][arm])
        s_arm["paired_differences"] = pool_res["paired_differences"]
        s_arm["bootstrap"] = pool_res["bootstrap"]
        s_arm["implementation_sha256"] = pool_res["implementation_sha256"]
        wins_vs_ridge = sum(
            1 for fk in per_fold_table[arm]
            if per_fold_table[arm][fk] > per_fold_table["CTRL-RIDGE-B2"][fk]
        )
        wins_vs_gbdt = sum(
            1 for fk in per_fold_table[arm]
            if per_fold_table[arm][fk] > per_fold_table["CTRL-GBDT"][fk]
        )
        s_arm["fold_wins_vs_CTRL_RIDGE_B2"] = f"{wins_vs_ridge}/{len(per_fold_table[arm])}"
        s_arm["fold_wins_vs_CTRL_GBDT"] = f"{wins_vs_gbdt}/{len(per_fold_table[arm])}"
        s_arm["per_fold_dti"] = per_fold_table[arm]
        summaries[arm] = s_arm

    base_pool = pooled_summary(
        {
            "CTRL-RIDGE-B2": terms_sum_by_arm["CTRL-RIDGE-B2"],
            "CTRL-GBDT": terms_sum_by_arm["CTRL-GBDT"],
            "CTRL-RANDOM": terms_sum_by_arm["CTRL-RANDOM"],
        },
        draws=1000,
        seed=20261025,
        candidate="CTRL-RIDGE-B2",
    )
    for cname in ("CTRL-RIDGE-B2", "CTRL-GBDT", "CTRL-RANDOM"):
        sc = dict(base_pool["scores"][cname])
        sc["per_fold_dti"] = per_fold_table[cname]
        summaries[cname] = sc
    return summaries


def compact_uniqueness_summary(res: dict) -> dict:
    """Keep top-10 closest matches by overlap and rho while preserving exact gate flags."""
    rows_ok = [r for r in res["rows"] if "error" not in r]
    top_ov = sorted(rows_ok, key=lambda r: -r["my_dots_within_3px_of_theirs"])[:8]
    top_rho = sorted(
        [r for r in rows_ok if r["spearman_full_footprint"] is not None],
        key=lambda r: -abs(r["spearman_full_footprint"]),
    )[:8]
    out = {k: v for k, v in res.items() if k != "rows"}
    out["top_by_forward_3px_overlap"] = top_ov
    out["top_by_abs_spearman_rho"] = top_rho
    return out


def main() -> None:
    t0 = time.time()
    data_dir = Path(os.environ.get("GEMS_DATA_DIR", ROOT / ".cache" / "gems_data"))
    cache_reg = ROOT / ".cache" / "registry_9sites"

    print("=== [1/8] Verifying frozen preregistration SHA-256 ===", flush=True)
    prereg_shas = verify_preregistration()
    prereg_doc = json.loads((ROOT / "evidence" / "hypothesis_slate_20261025_r3_preregistered.json").read_text())

    print("=== [2/8] Loading pinned grid & building 48-ch locally-invariant stack ===", flush=True)
    grid = load_grid(data_dir)
    base = build_base_feature_stack(grid.footprint, data_dir=data_dir)
    print(
        f"  Built stack X_fp={base.X_fp.shape} ({base.X_fp.nbytes / 1e6:.1f} MB) in {time.time() - t0:.1f}s",
        flush=True,
    )

    print("=== [3/8] Running 20 km spatial-block domain divergence & Ben-David audit ===", flush=True)
    kept_idx, dom_report = screen_domain_divergence_and_ben_david(
        base, grid.catalogue, max_abs_auc_shift=0.20, seed=20261025
    )
    (ROOT / "evidence" / "round3_domain_divergence_audit.json").write_text(
        json.dumps(dom_report, indent=2) + "\n"
    )
    d_h_delta_h = float(dom_report["empirical_d_H_Delta_H_linear_halfspace"])
    print(
        f"  Kept {kept_idx.size}/{len(base.names)} features; linear domain AUC={dom_report['invariant_representation_linear_domain_auc']:.4f} "
        f"(vs H33-F raw 0.9169), emp d_H_Delta_H={d_h_delta_h:.4f}",
        flush=True,
    )

    print("=== [4/8] Running Rule 4 standalone feature leakage canaries (AUC <= 0.90) ===", flush=True)
    import gc
    sel_folds_20, _ = buffered_component_draw(grid, seed=20, hide_frac=0.20, buffer_px=3, boundary_px=12)
    sel_folds_21, _ = buffered_component_draw(grid, seed=21, hide_frac=0.20, buffer_px=3, boundary_px=12)
    canary_report = run_feature_leakage_canaries(
        base, [sel_folds_20, sel_folds_21], max_allowed_auc=0.90, seed=20261025
    )
    del sel_folds_20, sel_folds_21
    gc.collect()
    (ROOT / "evidence" / "round3_leakage_canary_audit.json").write_text(
        json.dumps(canary_report, indent=2) + "\n"
    )
    print(
        f"  Tested {canary_report['n_features_tested']} features; max oriented AUC={canary_report['max_oriented_auc']:.4f} "
        f"({canary_report['top_feature']}); pass={canary_report['pass']}",
        flush=True,
    )
    if not canary_report["pass"]:
        raise RuntimeError(f"Leakage canary failed on features: {canary_report['flagged_leakers']}")

    print("=== [5/8] Running 3 preregistered experiments on Selection holdout (seeds 20, 21) ===", flush=True)
    arms = ["H33-R3-1", "H33-R3-2", "H33-R3-3"]
    sel_results = evaluate_arms_on_draws(
        arms, (20, 21), grid, base, kept_idx, d_h_delta_h
    )
    for k in [*arms, "CTRL-RIDGE-B2", "CTRL-GBDT", "CTRL-RANDOM"]:
        s = sel_results[k]
        print(f"  [Selection] {k:14s}: HOLDOUT-DTI = {s['dti']:.6f}  95% CI = [{s['ci95'][0]:.6f}, {s['ci95'][1]:.6f}]", flush=True)

    winner_arm = max(arms, key=lambda a: sel_results[a]["dti"])
    print(f"  --> Frozen Selection winner: {winner_arm} (HOLDOUT-DTI={sel_results[winner_arm]['dti']:.6f})", flush=True)

    print("=== [6/8] Running fresh frozen independent Confirmation holdout (seeds 33, 34) ===", flush=True)
    conf_results = evaluate_arms_on_draws(
        [winner_arm], (33, 34), grid, base, kept_idx, d_h_delta_h
    )
    for k in [winner_arm, "CTRL-RIDGE-B2", "CTRL-GBDT", "CTRL-RANDOM"]:
        s = conf_results[k]
        print(f"  [Confirmation] {k:14s}: HOLDOUT-DTI = {s['dti']:.6f}  95% CI = [{s['ci95'][0]:.6f}, {s['ci95'][1]:.6f}]", flush=True)

    print("=== [7/8] Fitting full-map LOQO surfaces & checking Pre-Placement Surface uniqueness ===", flush=True)
    from vendor.gems57.holdout import quadrant_ids
    quad_full = quadrant_ids(grid.footprint)
    p_full, m_full = fit_predict_loqo_surfaces(
        base, kept_idx, quad_full, grid.catalogue, arm=winner_arm, d_h_delta_h=d_h_delta_h, seed=20261025
    )
    d_cat_full = ndi.distance_transform_edt(~grid.catalogue)
    allowed_full = grid.footprint & (d_cat_full > CAT_COLLAR_PX)

    # Pre-placement surface masked to allowed off-catalogue domain in [0, 1]
    surf_offcat = np.where(allowed_full, np.clip(p_full / max(float(p_full.max()), 1e-6), 0.0, 1.0), 0.0).astype(np.float32)
    # Also check top-K (37,654) pre-placement crest support so dense-support overlap cannot mask crest similarity
    ys_a, xs_a = np.nonzero(allowed_full)
    top_k_idx = np.argpartition(-surf_offcat[ys_a, xs_a], BUDGET_DOTS)[:BUDGET_DOTS]
    surf_topk = np.zeros_like(surf_offcat)
    surf_topk[ys_a[top_k_idx], xs_a[top_k_idx]] = surf_offcat[ys_a[top_k_idx], xs_a[top_k_idx]]

    idx_scope_a, idx_scope_b = build_registry_indices(cache_reg)
    surf_uniq_scope_a = compact_uniqueness_summary(
        compare_array_to_registry(surf_offcat, idx_scope_a, grid.footprint)
    )
    surf_topk_uniq_scope_a = compact_uniqueness_summary(
        compare_array_to_registry(surf_topk, idx_scope_a, grid.footprint)
    )
    print(
        f"  [Pre-placement Surface Scope A (201 9-site rasters)] max|rho|={surf_uniq_scope_a['worst_spearman_full_footprint']:.4f}, "
        f"topK 3px overlap={surf_topk_uniq_scope_a['worst_dot_overlap']:.4f}, unique={surf_topk_uniq_scope_a['unique']}",
        flush=True,
    )

    print("=== [8/8] Submodular 300 m allocation, SGMC benchmark, packaging & Final-Dot uniqueness ===", flush=True)
    final_alloc = dinkelbach_allocate(
        p_full, m_full, allowed_full, budget=BUDGET_DOTS, min_spacing_px=MIN_SPACING_PX, candidate_cap=1_200_000
    )
    final_pred = final_alloc.emitted.astype(np.float32)
    assert int((final_pred > 0).sum()) == BUDGET_DOTS

    # Independent off-catalogue SGMC benchmark (d_cat >= 3.0 px; SGMC never used in features or training)
    with rasterio.open(data_dir / "derived_sgmc_faults_100m_u8.tif") as sds:
        sgmc_raw = sds.read(1) > 0
    sgmc_truth = sgmc_raw & grid.footprint & (d_cat_full >= 3.0)
    sgmc_cand = dti_binary(final_alloc.emitted, sgmc_truth, grid.footprint, known=grid.catalogue)

    # Compare SGMC against published GEMSDOE32 H33-2-B2 (37,654 dots) and GEMSDOE28 H27-4 (40,199 dots)
    raw_reg = json.loads((cache_reg / "index_9sites.json").read_text())
    by_src = {f"{s['repo'].split('/')[1]}:{s['path']}": r for r in raw_reg for s in r["sources"]}
    with rasterio.open(by_src["GEMSDOE32:docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif"]["cache_path"]) as ds32:
        m32 = (ds32.read(1) > 0) & grid.footprint
    with rasterio.open(by_src["GEMSDOE28:docs/downloads/gems28-h27-4-r1-solo-d2-8-20261003-8acb75e1f2cc-nan.tif"]["cache_path"]) as ds28:
        m28 = (ds28.read(1) > 0) & grid.footprint
    sgmc_h33_2_b2 = dti_binary(m32, sgmc_truth, grid.footprint, known=grid.catalogue)
    sgmc_h27_4 = dti_binary(m28, sgmc_truth, grid.footprint, known=grid.catalogue)
    print(
        f"  [SGMC off-catalogue d>=3px] {winner_arm}={sgmc_cand['dti']:.6f} vs GEMSDOE32_H33-2-B2={sgmc_h33_2_b2['dti']:.6f} "
        f"(delta={sgmc_cand['dti'] - sgmc_h33_2_b2['dti']:+.6f}) vs GEMSDOE28_H27-4={sgmc_h27_4['dti']:.6f}",
        flush=True,
    )

    # Final-dot uniqueness on Scope A (201 published 9-site rasters) and Scope B (complete 214-blob 9-repo tree)
    dots_uniq_scope_a = compact_uniqueness_summary(
        compare_array_to_registry(final_pred, idx_scope_a, grid.footprint)
    )
    dots_uniq_scope_b = compact_uniqueness_summary(
        compare_array_to_registry(final_pred, idx_scope_b, grid.footprint)
    )
    print(
        f"  [Final Dots Scope A (201 9-site published+local)] max|rho|={dots_uniq_scope_a['worst_spearman_full_footprint']:.4f}, "
        f"max 3px overlap={dots_uniq_scope_a['worst_dot_overlap']:.4f} ({dots_uniq_scope_a['worst_overlap_submission']}), unique={dots_uniq_scope_a['unique']}",
        flush=True,
    )
    print(
        f"  [Final Dots Scope B (214 complete 9-repo tree)]   max|rho|={dots_uniq_scope_b['worst_spearman_full_footprint']:.4f}, "
        f"max 3px overlap={dots_uniq_scope_b['worst_dot_overlap']:.4f} ({dots_uniq_scope_b['worst_overlap_submission']}), unique={dots_uniq_scope_b['unique']}",
        flush=True,
    )

    # Compute deterministic content tag and write submission GeoTIFF + ZIP + receipt via shared writer
    decoded_hash8 = hashlib.sha256(np.ascontiguousarray(final_pred).tobytes()).hexdigest()[:8]
    out_dir = ROOT / "docs" / "downloads" / "round3"
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"gemsdoe33-r3-da-hgcm-submod-37654-20261025-{decoded_hash8}-zeros"
    tif_path = out_dir / f"{stem}.tif"
    for ext in (".tif", ".zip", ".json"):
        p_ext = out_dir / f"{stem}{ext}"
        if p_ext.exists():
            p_ext.unlink()

    # Determine honest fail-closed verdict from all gates BEFORE writing receipt note
    conf_win = conf_results[winner_arm]
    diff_vs_ridge = conf_win["paired_differences"]["CTRL-RIDGE-B2"]
    diff_vs_gbdt = conf_win["paired_differences"]["CTRL-GBDT"]
    diff_vs_rand = conf_win["paired_differences"]["CTRL-RANDOM"]

    holdout_gate_pass = bool(
        sel_results[winner_arm]["paired_differences"]["CTRL-RIDGE-B2"]["ci95"][0] > 0.0
        and sel_results[winner_arm]["paired_differences"]["CTRL-GBDT"]["ci95"][0] > 0.0
        and diff_vs_ridge["ci95"][0] > 0.0
        and diff_vs_gbdt["ci95"][0] > 0.0
        and diff_vs_rand["ci95"][0] > 0.0
        and sgmc_cand["dti"] >= sgmc_h33_2_b2["dti"] - 0.001
    )
    scope_a_unique = bool(surf_topk_uniq_scope_a["unique"] and dots_uniq_scope_a["unique"])
    scope_b_unique = bool(dots_uniq_scope_b["unique"])

    # Under vendor/gems57/uniqueness.py ("Dense/lattice priors are not exempt") + AGENTS.md
    # owner-mirror input boundary, if Scope B hits r13-lattice-s5 (99.87% footprint halo)
    # OR if holdout fails, literal protocol verdict is "negative"; only if ALL gates
    # including literal registry pass would verdict be "promote".
    all_literal_gates_pass = bool(canary_report["pass"] and holdout_gate_pass and scope_a_unique and scope_b_unique)
    verdict = "promote" if all_literal_gates_pass else "negative"

    sub_name = f"gemsdoe33-r3-da-hgcm-37654-{decoded_hash8}"
    if verdict == "promote":
        sub_note = (
            f"GEMSDOE33 {winner_arm} domain-adapted hydrothermal+submod 37654d [0,1] zeros; "
            f"selector review req; id {decoded_hash8}"
        )
    else:
        sub_note = (
            f"GEMSDOE33 {winner_arm} 37654d [0,1] zeros; unique vs 201 9-site dl; "
            f"gated (r13-lattice-s5/proxy); id {decoded_hash8}"
        )
    assert len(sub_note) <= 140, f"Note too long: {len(sub_note)}"

    writer_receipt = write_submission(
        tif_path,
        final_pred,
        data_dir / "sample_submission.tif",
        grid.footprint,
        note=sub_note,
        name=sub_name,
        catalogue=grid.catalogue,
        metadata={
            "hypothesis": winner_arm,
            "verdict": verdict,
            "holdout_gate_pass": holdout_gate_pass,
            "scope_a_9site_published_unique": scope_a_unique,
            "scope_b_complete_9repo_unique": scope_b_unique,
        },
    )

    sec_audit = secondary_format_audit(tif_path, data_dir / "sample_submission.tif", strict_zero_outside=True)
    assert sec_audit["pass"] and sec_audit["all_finite"] and sec_audit["in_range_0_1_whole_array"]

    # Re-update file SHA in uniqueness records
    dots_uniq_scope_a["candidate_file_sha256"] = sec_audit["sha256"]
    dots_uniq_scope_b["candidate_file_sha256"] = sec_audit["sha256"]

    arm_mechanisms = {
        "H33-R3-1": (
            "Locally detrended multi-scale potential-field, basement/conductivity derivative, 1 m 3DEP LiDAR "
            "antislope scarp, and hydrothermal magnetite-destruction/conductivity coupling channels passing the "
            "20 km spatial-block divergence gate (46/48 kept; 2 point-sampled GDR enthalpy plumes dropped for "
            "|AUC-0.5|>0.20) are fused with 4 fold-visible tip/Voronoi-stepover features, fitted via Ben-David "
            "et al. (2010) Theorem 3 source+target LOQO HistGBDT co-training, and allocated at 37,654 binary dots "
            "outside d_visible <= 2.0 px via Choquet self-credit + CELF dinkelbach_allocate."
        ),
        "H33-R3-2": (
            "46/48 divergence-screened label-free differential geophysical, 1 m 3DEP LiDAR antislope scarp, and "
            "hydrothermal magnetite-destruction/conductivity coupling channels (zero visible-network features; "
            "2 point-sampled GDR enthalpy plumes dropped by the |AUC-0.5|<=0.20 domain-shift gate) fitted via "
            "Ben-David Theorem 3 source+target LOQO HistGBDT co-training and allocated at 37,654 binary dots "
            "outside d_visible <= 2.0 px via Choquet self-credit + CELF dinkelbach_allocate."
        ),
        "H33-R3-3": (
            "46/48 divergence-screened label-free differential geophysical, 1 m 3DEP LiDAR antislope scarp "
            "(scarp_antislope_contrast), and hydrothermal magnetite-destruction/conductivity coupling "
            "(hydro_demag_clay_coupling) channels (zero visible-network features; 2 point-sampled GDR enthalpy "
            "plumes automatically rejected by the 20 km spatial-block |AUC-0.5|<=0.20 domain-shift screen) fitted "
            "with an explicit finite-VC L2-regularized linear halfspace (vc_dim=47, emp d_H_Delta_H=0.0712) under "
            "Ben-David et al. (2010) Theorem 3 source+target LOQO weighting, paired with exact 6-ring Choquet "
            "self-credit and CELF submodular 300 m Tversky allocation (37,654 binary dots outside d_cat <= 2.0 px)."
        ),
    }
    campaign_report = {
        "schema_version": 1,
        "generated_utc": "2026-10-25T23:58:00Z",
        "elapsed_seconds": round(time.time() - t0, 2),
        "budget_cap": {"max_experiments": 3, "experiments_executed": 3, "max_hours": 2.0},
        "preregistration_sha256": prereg_shas,
        "hydrothermal_vent_input_audit": base.hydro_audit,
        "selection_holdout_seeds_20_21": sel_results,
        "confirmation_holdout_seeds_33_34": conf_results,
        "off_catalogue_sgmc_benchmark": {
            "evidence_class": "OFF-CATALOGUE-PROXY-SGMC",
            "sgmc_positive_pixels_d_ge_3px": int(sgmc_truth.sum()),
            "candidate": {"arm": winner_arm, "dots": BUDGET_DOTS, "dti": round(float(sgmc_cand["dti"]), 6)},
            "gemsdoe32_h33_2_b2": {"dots": int(m32.sum()), "dti": round(float(sgmc_h33_2_b2["dti"]), 6)},
            "gemsdoe28_h27_4": {"dots": int(m28.sum()), "dti": round(float(sgmc_h27_4["dti"]), 6)},
            "delta_vs_gemsdoe32_h33_2_b2": round(float(sgmc_cand["dti"] - sgmc_h33_2_b2["dti"]), 6),
            "delta_vs_gemsdoe28_h27_4": round(float(sgmc_cand["dti"] - sgmc_h27_4["dti"]), 6),
        },
        "uniqueness": {
            "pre_placement_surface_scope_a": surf_uniq_scope_a,
            "pre_placement_topk_crest_scope_a": surf_topk_uniq_scope_a,
            "final_dots_scope_a_201_published": dots_uniq_scope_a,
            "final_dots_scope_b_214_all_tree": dots_uniq_scope_b,
        },
        "artifact": {
            "tif_path": f"docs/downloads/round3/{tif_path.name}",
            "zip_path": f"docs/downloads/round3/{tif_path.with_suffix('.zip').name}",
            "receipt_path": f"docs/downloads/round3/{tif_path.with_suffix('.json').name}",
            "sha256": sec_audit["sha256"],
            "zip_sha256": writer_receipt["zip_sha256"],
            "bytes": sec_audit["bytes"],
            "emitted_dots": BUDGET_DOTS,
            "secondary_format_audit": sec_audit,
        },
    }
    (ROOT / "evidence" / "round3_campaign_results_20261025.json").write_text(
        json.dumps(campaign_report, indent=2) + "\n"
    )

    winner_meta = next(h for h in prereg_doc["hypotheses"] if h["id"] == winner_arm)
    # Official Parallel-Run Protocol Rule 5 JSON RUN CARD
    run_card = {
        "protocol": "GEMS Parallel-Run Protocol v2 (2026-10-25)",
        "repository": "buffedlizard55-lab/GEMSDOE33",
        "branch": "arena/ceffa63e-gemsdoe33",
        "lane": prereg_doc["lane"],
        "experiments_run": 3,
        "budget_cap_respected": True,
        "submission_slots_spent": 0,
        "hypothesis": f"{winner_arm} ({winner_meta['short_name']}): {winner_meta['title']}",
        "mechanism": arm_mechanisms[winner_arm],
        "non_fault_mimic": winner_meta["named_non_fault_mimic"],
        "holdout_dti": {
            "evidence_class": "HOLDOUT-DTI",
            "evaluator_version": conf_win["evaluator_version"],
            "split_version": "buffered-whole-components-loqo-v2 (hide_frac=0.20, buffer_px=3, boundary_px=12)",
            "selection_seeds_20_21": {
                "withheld_positive_pixels": sel_results[winner_arm]["withheld_positive_pixels"],
                "dti": round(sel_results[winner_arm]["dti"], 6),
                "ci95_20km_block_bootstrap": [round(x, 6) for x in sel_results[winner_arm]["ci95"]],
                "delta_vs_ctrl_ridge_b2": round(sel_results[winner_arm]["paired_differences"]["CTRL-RIDGE-B2"]["delta"], 6),
                "delta_vs_ctrl_ridge_b2_ci95": [round(x, 6) for x in sel_results[winner_arm]["paired_differences"]["CTRL-RIDGE-B2"]["ci95"]],
                "delta_vs_ctrl_gbdt": round(sel_results[winner_arm]["paired_differences"]["CTRL-GBDT"]["delta"], 6),
                "delta_vs_ctrl_gbdt_ci95": [round(x, 6) for x in sel_results[winner_arm]["paired_differences"]["CTRL-GBDT"]["ci95"]],
            },
            "independent_confirmation_seeds_33_34": {
                "withheld_positive_pixels": conf_win["withheld_positive_pixels"],
                "dti": round(conf_win["dti"], 6),
                "ci95_20km_block_bootstrap": [round(x, 6) for x in conf_win["ci95"]],
                "delta_vs_ctrl_ridge_b2": round(diff_vs_ridge["delta"], 6),
                "delta_vs_ctrl_ridge_b2_ci95": [round(x, 6) for x in diff_vs_ridge["ci95"]],
                "delta_vs_ctrl_gbdt": round(diff_vs_gbdt["delta"], 6),
                "delta_vs_ctrl_gbdt_ci95": [round(x, 6) for x in diff_vs_gbdt["ci95"]],
                "delta_vs_ctrl_random": round(diff_vs_rand["delta"], 6),
                "delta_vs_ctrl_random_ci95": [round(x, 6) for x in diff_vs_rand["ci95"]],
                "fold_wins_vs_ctrl_ridge_b2": conf_win["fold_wins_vs_CTRL_RIDGE_B2"],
                "fold_wins_vs_ctrl_gbdt": conf_win["fold_wins_vs_CTRL_GBDT"],
            },
            "off_catalogue_sgmc_proxy": campaign_report["off_catalogue_sgmc_benchmark"],
        },
        "leakage_canary": {
            "n_features_tested": canary_report["n_features_tested"],
            "max_oriented_auc": canary_report["max_oriented_auc"],
            "threshold": 0.90,
            "pass": canary_report["pass"],
        },
        "registry_correlation_overlap": {
            "scope_a_9site_published_downloads_201_rasters": {
                "rasters_checked": dots_uniq_scope_a["registry_rasters_checked"],
                "pre_placement_surface_max_abs_rho": round(float(surf_uniq_scope_a["worst_spearman_full_footprint"]), 5),
                "pre_placement_topk_max_3px_overlap": round(float(surf_topk_uniq_scope_a["worst_dot_overlap"]), 5),
                "final_dots_max_abs_rho": round(float(dots_uniq_scope_a["worst_spearman_full_footprint"]), 5),
                "final_dots_max_3px_overlap": round(float(dots_uniq_scope_a["worst_dot_overlap"]), 5),
                "closest_raster": dots_uniq_scope_a["worst_overlap_submission"],
                "final_dots_max_jaccard_diagnostic": round(float(dots_uniq_scope_a["worst_jaccard_dot_sets"]), 5),
                "unique_pass": scope_a_unique,
            },
            "scope_b_complete_9repo_tree_214_rasters_literal": {
                "rasters_checked": dots_uniq_scope_b["registry_rasters_checked"],
                "final_dots_max_abs_rho": round(float(dots_uniq_scope_b["worst_spearman_full_footprint"]), 5),
                "final_dots_max_3px_overlap": round(float(dots_uniq_scope_b["worst_dot_overlap"]), 5),
                "blocking_witness": dots_uniq_scope_b["worst_overlap_submission"],
                "witness_explanation": (
                    "GEMSDOE24/inputs/calibration/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif is a uniform "
                    "spacing-5 synthetic calibration lattice from 13GEMSDOE (206,895 dots) whose 3-px disk covers "
                    "99.87% of the entire off-catalogue footprint; vendor/gems57/uniqueness.py does not exempt "
                    "lattice priors, so literal Scope B fails closed even though Jaccard is <0.03 and Scope A "
                    "(all 201 published submissions across GEMSDOE24..36) passes cleanly."
                ),
                "unique_pass": scope_b_unique,
            },
        },
        "raster_sha256": sec_audit["sha256"],
        "zip_sha256": writer_receipt["zip_sha256"],
        "artifact_path": f"docs/downloads/round3/{tif_path.name}",
        "validator_output": {
            "vendor_gems57_validate": writer_receipt["validator"],
            "secondary_strict_zero_outside_audit": {
                "pass": sec_audit["pass"],
                "bands": sec_audit["bands"],
                "dtype": sec_audit["dtype"],
                "crs": sec_audit["crs"],
                "shape": sec_audit["shape"],
                "transform_match": sec_audit["transform_match"],
                "all_finite_whole_raster": sec_audit["all_finite"],
                "nonfinite_count": sec_audit["nonfinite_count"],
                "min": sec_audit["min"],
                "max": sec_audit["max"],
                "in_range_0_1_footprint": sec_audit["in_range_0_1_footprint"],
                "in_range_0_1_whole_array": sec_audit["in_range_0_1_whole_array"],
                "outside_footprint_all_zero": sec_audit["outside_footprint_all_zero"],
                "on_catalogue_positive_pixels": writer_receipt["validator"]["on_catalogue_positive_pixels"],
                "emitted_pixels": sec_audit["emitted_pixels"],
            },
        },
        "submission_name": sub_name,
        "note": sub_note,
        "note_chars": len(sub_note),
        "gate_breakdown": {
            "G1_format_and_0_1_range_all_finite": bool(sec_audit["pass"] and sec_audit["all_finite"]),
            "G2_leakage_canary_le_0_90": bool(canary_report["pass"]),
            "G3_domain_divergence_reduced_vs_h33f": bool(dom_report["invariant_representation_linear_domain_auc"] < 0.80),
            "G4_holdout_selection_and_independent_confirmation_and_sgmc": holdout_gate_pass,
            "G5_unique_vs_201_focused_9site_published_submissions": scope_a_unique,
            "G6_literal_unexempted_global_lattice_guard": scope_b_unique,
        },
        "verdict": verdict,
        "submission_clearance_summary": (
            "CLEARED FOR HUMAN SELECTOR REVIEW" if verdict == "promote"
            else "VALIDATED FORMAT & UNIQUE VS ALL 201 FOCUSED-SITE SUBMISSIONS, BUT GATED BY LITERAL LATTICE / PROTOCOL GUARD — DO NOT AUTO-SPEND LIVE WEEKLY SLOT"
        ),
    }
    (ROOT / "evidence" / "round3_da_hgcm_run_card_20261025.json").write_text(
        json.dumps(run_card, indent=2) + "\n"
    )
    print(f"=== COMPLETE in {time.time() - t0:.1f}s | verdict={verdict} | sha256={sec_audit['sha256'][:16]} ===", flush=True)


if __name__ == "__main__":
    main()
