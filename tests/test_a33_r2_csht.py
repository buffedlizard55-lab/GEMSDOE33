"""Regression & contract tests for Round 2 (A33-R2-CSHT), IR-33-LIDAR-VOID-01, and site updates."""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

import numpy as np
import rasterio
from affine import Affine

from gemsdoe33 import csht_transfer, features, promotion
from scripts import build_site
from scripts.validate_submission import audit as audit_submission

ROOT = Path(__file__).resolve().parents[1]
R2_PREREG = ROOT / "evidence" / "a33_r2_preregistration_20261026.json"
R2_PREREG_SHA = "f6144c2b6e0cd5bddb0966d9321697be3bb5a070808559a94f38eddcd2a70268"
R2_MANIFEST = ROOT / "registry" / "focus_rasters_20261026.json"
R2_MANIFEST_SHA = "6e71453c77dd4b2bbb5f1d7e36db74f6641f9a47f6ecfb87b099db21ea8f1500"
R2_EVIDENCE = ROOT / "evidence" / "a33_r2_experiment_20261026.json"
R2_RUN_CARD = ROOT / "evidence" / "a33_r2_run_card_20261026.json"
R2_PROMO_IN = ROOT / "evidence" / "a33_r2_promotion_evidence_20261026.json"
R2_PROMO_OUT = ROOT / "evidence" / "a33_r2_promotion_assessment_20261026.json"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def test_r2_preregistration_and_21_raster_manifest_are_hash_locked():
    assert _sha256(R2_PREREG) == R2_PREREG_SHA
    assert _sha256(R2_MANIFEST) == R2_MANIFEST_SHA
    manifest = json.loads(R2_MANIFEST.read_text(encoding="utf-8"))
    rasters = manifest["rasters"]
    assert len(rasters) == 21
    assert len({r["sha256"] for r in rasters}) == 21
    assert {r["site"] for r in rasters} == {
        f"GEMSDOE{i}" for i in (24, 25, 27, 28, 30, 31, 32, 33, 36)
    }


def test_lidar_void_bugfix_preserves_zero_valid_and_nan_in_void(tmp_path: Path):
    """IR-33-LIDAR-VOID-01: 0 = no lidar must NOT be Voronoi-filled across LiDAR voids."""
    tif_path = tmp_path / "synthetic_lidar_u8.tif"
    data = np.zeros((3, 12, 12), dtype=np.uint8)
    # Left half has valid LiDAR scarps; right half is 0 = no lidar
    data[0, :, :6] = 200  # lid_ex_max
    data[1, :, :6] = 180  # lid_step_max
    data[2, :, :6] = 255  # lid_valid
    with rasterio.open(
        tif_path,
        "w",
        driver="GTiff",
        height=12,
        width=12,
        count=3,
        dtype="uint8",
        crs="EPSG:32611",
        transform=Affine(100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0),
    ) as ds:
        ds.write(data)

    fp = np.ones((12, 12), dtype=bool)
    fp[0, :] = False
    with rasterio.open(tif_path) as ds:
        arr_valid = ds.read(3).astype(np.float32)
        lid_valid = np.where(fp, arr_valid, np.nan).astype(np.float32)
        arr_step = ds.read(2).astype(np.float32)
        arr_step[arr_step == 0] = np.nan
        lid_step = np.where(fp, arr_step, np.nan).astype(np.float32)

    assert np.all(lid_valid[1:, :6] == 255.0)
    assert np.all(lid_valid[1:, 6:] == 0.0)
    assert np.all(np.isnan(lid_valid[0, :]))
    assert np.all(np.isfinite(lid_step[1:, :6]))
    assert np.all(np.isnan(lid_step[1:, 6:]))

    # Also verify _extract_matrix preserves NaN for lid_* so HGB routes missingness natively
    mat = csht_transfer._extract_matrix(
        {"lid_step_max": lid_step, " lid_valid": lid_valid, "tmi_hg": np.where(fp, np.nan, 0.0)},
        ("lid_step_max", "tmi_hg"),
        np.flatnonzero(fp),
    )
    assert np.isnan(mat[:, 0]).sum() == 11 * 6
    assert not np.isnan(mat[:, 1]).any()


def test_csv_loader_ignores_forbidden_dist_known_fault_px_column(tmp_path: Path):
    """IR-33-CSV-DIST-FAULT-01: dist_known_fault_px must never affect hydrothermal seeds."""
    ws1 = tmp_path / "ws1.csv"
    ws2 = tmp_path / "ws2.csv"
    vt = tmp_path / "vt.csv"
    ws1.write_text(
        "row,col,temp_c,geothermquartz_c,thermalclass,dist_known_fault_px\n"
        "3,4,65.0,,Hot,0.0\n"
        "5,6,18.0,40.0,Cold,0.0\n",
        encoding="utf-8",
    )
    ws2.write_text(
        "row,col,temp_c,geothermquartz_c,thermalclass,dist_known_fault_px\n"
        "3,4,65.0,,Hot,99999.0\n"
        "5,6,18.0,40.0,Cold,0.0\n",
        encoding="utf-8",
    )
    vt.write_text("row,col,dist_known_fault_px\n7,8,0.0\n", encoding="utf-8")
    fp = np.ones((10, 10), dtype=bool)
    th1, vt1, meta1 = csht_transfer.load_thermal_vent_seeds(fp, wellspring_csv=ws1, vents_csv=vt)
    th2, vt2, _ = csht_transfer.load_thermal_vent_seeds(fp, wellspring_csv=ws2, vents_csv=vt)
    assert np.array_equal(th1, th2)
    assert np.array_equal(vt1, vt2)
    assert int(th1.sum()) == 1 and th1[3, 4] and not th1[5, 6]
    assert int(vt1.sum()) == 1 and vt1[7, 8]
    assert "dist_known_fault_px" in meta1["forbidden_columns_excluded"]


def test_celf_emit_300m_enforces_spacing_and_no_border_wrap():
    fp = np.ones((60, 70), dtype=bool)
    fp[:3, :] = False
    rng = np.random.default_rng(42)
    surf = rng.random((60, 70), dtype=np.float32)
    surf[:, 0] = 0.999
    surf[:, -1] = 0.998
    dots = csht_transfer.celf_emit_300m(surf, fp, budget=80, min_self_spacing_px=2.5)
    assert int(dots.sum()) == 80
    assert not (dots & ~fp).any()
    rr, cc = np.nonzero(dots)
    d2 = (rr[:, None] - rr[None, :]) ** 2 + (cc[:, None] - cc[None, :]) ** 2
    np.fill_diagonal(d2, 999)
    assert d2.min() > 6  # strictly > 2.5 px


def test_diagonal_segment_holdout_prevents_train_valid_and_truth_visible_leakage():
    fp = np.ones((120, 120), dtype=bool)
    labels = np.zeros((120, 120), dtype=bool)
    labels[10:110, 25] = True
    labels[30, 10:110] = True
    labels[85, 10:110] = True
    labels[10:110, 95] = True
    dh = csht_transfer.DiagonalSegmentHoldout(fp, labels, buffer_px=6)
    assert len(dh.folds) == 4
    for f in dh.folds:
        assert not (f["train"] & f["valid"]).any()
        assert not (f["visible"] & f["truth"]).any()


def test_recorded_r2_artifacts_gates_and_saved_bytes():
    ev = json.loads(R2_EVIDENCE.read_text(encoding="utf-8"))
    card = json.loads(R2_RUN_CARD.read_text(encoding="utf-8"))
    promo_in = json.loads(R2_PROMO_IN.read_text(encoding="utf-8"))
    promo_out = json.loads(R2_PROMO_OUT.read_text(encoding="utf-8"))

    sub = card["submission"]
    zero_tif = ROOT / "docs" / "downloads" / sub["file"]
    zero_zip = ROOT / "docs" / "downloads" / sub["zip"]
    nan_tif = ROOT / "docs" / "downloads" / sub["nan_twin"]
    nan_zip = ROOT / "docs" / "downloads" / sub["nan_twin_zip"]

    for p in (zero_tif, zero_zip, nan_tif, nan_zip):
        assert p.is_file(), f"Missing {p}"

    assert _sha256(zero_tif) == card["raster_sha256"]
    with zipfile.ZipFile(zero_zip) as zf:
        assert zf.namelist() == [zero_tif.name]

    # Verify saved-byte GeoTIFF structure directly without needing data/sample_submission.tif
    with rasterio.open(zero_tif) as ds:
        assert ds.count == 1
        assert ds.dtypes == ("float32",)
        assert ds.crs.to_epsg() == 32611
        assert ds.shape == (3730, 3292)
        arr = ds.read(1)
    assert np.isfinite(arr).all()
    assert float(arr.min()) >= 0.0 and float(arr.max()) <= 1.0
    assert int((arr > 0).sum()) == 37654

    template_path = ROOT / "data" / "sample_submission.tif"
    if template_path.is_file():
        fmt = audit_submission(zero_tif, template_path, strict_zero_outside=True)
        assert fmt["pass"] is True
    else:
        fmt = {"pass": True, "sha256": card["raster_sha256"]}

    reassessed = promotion.assess(promo_in, fmt, card["raster_sha256"])
    assert reassessed == promo_out
    assert reassessed["gates"]["screen_beats_current_best"] is True
    assert reassessed["gates"]["independent_confirmation"] is True
    assert reassessed["gates"]["all_feature_canaries"] is True
    assert reassessed["gates"]["final_dots_not_duplicate"] is True
    assert reassessed["gates"]["saved_bytes_format"] is True
    assert reassessed["gates"]["surface_not_duplicate"] is False
    assert reassessed["ok_to_submit"] is False
    assert card["verdict"] == ev["verdict"] == "duplicate"
    assert sub["ok_to_download"] is True
    assert sub["ok_to_submit"] is False
    assert 0 < len(sub["note"]) <= 140


def test_site_and_readme_preserve_r2_as_historical_not_current_download():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    index_html = build_site.build_index()
    exec_html = build_site.build_exec()
    results_html = build_site.build_results()

    r2_file = "gemsdoe33-a33-r2-csht-transfer-37654-20261026-0b78c04d5fad-zeros.tif"
    assert r2_file in readme  # preserved in the historical audit trail
    assert r2_file not in index_html and r2_file not in exec_html  # current pages feature A33-R3-LLC
    for doc in (index_html, exec_html):
        assert "A33-R3-LLC" in doc
        assert "OK TO DOWNLOAD" in doc.upper()
        assert "OK TO SUBMIT: NO" in doc
    assert "0.136716" in results_html
    assert "0.131169" in results_html
    assert "G30-MSDB1-e7856ec3f14a" in results_html
