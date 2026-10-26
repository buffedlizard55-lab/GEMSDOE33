"""The current run card must record a stop, not an upload recommendation."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_duplicate_guard_card_is_negative_and_byte_pinned():
    card = json.loads((ROOT / "evidence/duplicate_guard_run_card_20261025.json").read_text())
    assert card["verdict"] == "negative"
    assert "H33-6" in card["hypothesis"]
    assert "Lithologic contact" in card["named_non_fault_mimic"]
    assert card["status"] == "DUPLICATE_GUARD_TRIGGERED_STOP_NO_SLOT"
    assert card["surface_preplacement_screen"].startswith("NOT RUN")
    assert card["holdout_recap"]["withheld_positives"] == 60988
    assert card["holdout_recap"]["mean_delta_dti"] < 0
    assert card["holdout_recap"]["pooled_p1_delta_dti"] < 0
    assert card["holdout_recap"]["pooled_p1_candidate_dti"] < card["holdout_recap"]["pooled_p1_control_dti"]
    assert card["leakage_canary"]["status"].startswith("UNRESOLVED")
    assert card["submission"]["status"].startswith("RESEARCH ONLY")
    assert card["submission"]["note_characters"] <= 140
    # The artifact path is explicit in the validator record; pin that exact saved file.
    candidate = ROOT / card["validator"]["artifact"]
    assert hashlib.sha256(candidate.read_bytes()).hexdigest() == card["submission"]["tif_sha256"]
    assert sum(row["duplicate_trigger"] for row in card["final_dot_duplicate_screen"]["comparisons"]) == 7


def test_saved_byte_audit_discloses_missing_template_and_nan_outside():
    audit = json.loads((ROOT / "evidence/saved_bytes_audit_20261025.json").read_text())
    assert audit["reopened_saved_bytes"] is True
    assert audit["finite_cells"] == 5167373
    assert audit["nan_cells"] == 7111787
    assert "Not repeated against sample_submission.tif" in audit["footprint_grid_comparison"]
    assert "all-array finite check fails" in audit["portal_acceptance"]


def test_round3_run_card_matches_parallel_run_protocol():
    card = json.loads((ROOT / "evidence/round3_run_card_20261025.json").read_text())
    assert card["verdict"] == "negative"
    assert card["experiment_budget_used"] == 3
    assert card["experiment_budget_limit"] == 3
    assert "H33-R3-1" in card["hypothesis"]
    assert len(card["named_non_fault_mimic"]) > 20

    hd = card["holdout_dti"]
    assert hd["label"] == "HOLDOUT-DTI"
    assert hd["evaluator_version"] == "GEMSDOE33-HIDE-AND-RECOVER-v1.0"
    assert hd["withheld_positives"] == 60988
    exp1 = hd["experiments"]["H33-R3-1_invariant_analog_cotrain"]
    assert 0.06 < exp1["pooled_dti"] < 0.09
    assert exp1["delta_vs_fold_safe_physical_baseline"] > 0.02
    assert exp1["positive_folds_vs_physical_baseline"] == 3
    assert exp1["delta_vs_matched_random_control"] > 0.02

    lc = card["leakage_canary"]
    assert lc["features_tested"] == 32
    assert lc["max_feature_canary_auc"] <= 0.90
    assert lc["any_leakage_flagged"] is False

    dup = card["correlation_and_overlap_vs_registry"]
    assert dup["n_registry_rasters_checked"] >= 20
    assert dup["max_abs_surface_spearman_rho"] <= 0.90
    assert dup["max_dots_spearman_rho"] <= 0.90
    assert dup["max_fraction_within_3px"] <= 0.70
    assert dup["duplicate_triggered"] is False

    val = card["validator_output"]
    assert val["no_nan_inside_footprint"] is True
    assert val["values_in_0_1_footprint"] is True
    assert val["values_in_0_1_whole_array_zeros_variant"] is True
    assert val["crs_shape_transform_match"] is True
    assert val["all_checks_pass"] is True

    sub = card["submission"]
    assert sub["note_chars"] <= 140
    assert sub["emitted_positive_pixels"] == 37654
    assert sub["on_catalogue_positive_pixels"] == 0
    assert sub["within_200m_of_catalogue_pixels"] == 0

    zeros_p = ROOT / val["zeros_file"]
    nan_p = ROOT / val["nan_file"]
    assert zeros_p.is_file() and nan_p.is_file()
    assert hashlib.sha256(zeros_p.read_bytes()).hexdigest() == card["raster_sha256"]["zeros_tif"]
    assert hashlib.sha256(nan_p.read_bytes()).hexdigest() == card["raster_sha256"]["nan_tif"]


def test_focus_sites_forensic_set_identities():
    forensic = json.loads((ROOT / "evidence/focus_sites_forensic_20261025.json").read_text())
    assert len(forensic["focus_site_submissions"]) == 13
    ident = forensic["exact_boolean_identities_measured"]
    assert ident["d28_is_strict_subset_of_h19_5"] is True
    assert ident["gemsdoe30_d28_equals_gemsdoe25_d28"] is True
    assert ident["h27_4_equals_d28_and_d_cat_gt_1px"] is True
    assert ident["gemsdoe31_h27_4_equals_gemsdoe28_h27_4"] is True
    assert ident["gemsdoe32_h33_2_b2_equals_d28_and_d_cat_gt_2px"] is True
    assert ident["gemsdoe32_h33_2_b2_equals_h27_4_and_d_cat_gt_2px"] is True
    assert ident["gemsdoe36_contains_gemsdoe32_h33_2_b2_as_exact_subset"] is True


def test_shared_evaluate_holdout_and_submission_writer_guards(tmp_path):
    import importlib.util
    import numpy as np
    import pytest

    def _load(name: str, path: Path):
        import sys
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
        return mod

    eh = _load("root_evaluate_holdout", ROOT / "evaluate_holdout.py")
    sw = _load("root_submission_writer", ROOT / "submission_writer.py")

    # 1. Hide-and-recover folds enforce zero overlap between visible_faults and withheld_pos
    fp = np.ones((80, 80), dtype=bool)
    cat = np.zeros((80, 80), dtype=bool)
    cat[10:25, 15] = True
    cat[55:70, 60] = True
    folds = eh.build_hide_and_recover_folds(cat, fp, system_buffer_px=3, collar_px=3, n_folds=2)
    assert len(folds) == 2
    for f in folds:
        assert not np.any(f.visible_faults & f.withheld_pos)
        assert not np.any(f.visible_faults & f.collar_mask)
        assert not np.any(f.train_eligible_mask & f.withheld_pos)

    # 2. Leakage canary flags a feature that leaks held-out positives (AUC > 0.90)
    leaky_feat = cat.astype(np.float32)
    res_leak = eh.leakage_canary_auc(leaky_feat, folds, max_neg_per_fold=500, seed=1)
    assert res_leak["canary_auc"] > 0.90
    assert res_leak["leakage_flag"] is True

    # 3. Submission writer refuses notes > 140 chars or out-of-range values
    bad_note = "x" * 145
    with pytest.raises(ValueError):
        sw.write_submission_bundle(
            np.zeros((3730, 3292), dtype=np.float32),
            name_prefix="test",
            note_template=bad_note,
            outdir=tmp_path,
        )
