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
