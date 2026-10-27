"""Automated verification tests for the 2026-10-25 Round-3 campaign, GeoTIFF, and Run Card."""

from __future__ import annotations

import hashlib
import json
import os
import zipfile
from pathlib import Path

import numpy as np
import rasterio

from gemsdoe33.round3_analog_vent import (
    CANDIDATE_CACHED_CHANNELS,
    FORBIDDEN_COLS,
    VENT_ALLOWED_COLS,
    WELLSPRING_ALLOWED_COLS,
    exact_choquet_self_credit,
)
from scripts import build_site
from vendor.gems57.grid import CRS_EPSG, SHAPE, TRANSFORM

ROOT = Path(__file__).resolve().parents[1]


def test_vendor_gems57_sha256_pins_match_registry():
    pins = json.loads((ROOT / "registry" / "vendor_pins.json").read_text())
    shas = pins["sha256"]
    assert len(shas) == 23
    for fname, expected_sha in shas.items():
        fpath = ROOT / "vendor" / "gems57" / fname
        assert fpath.is_file(), f"Missing vendored file: {fname}"
        actual_sha = hashlib.sha256(fpath.read_bytes()).hexdigest()
        assert actual_sha == expected_sha, f"SHA mismatch on {fname}"


def test_preregistration_hashes_intact():
    sha_file = ROOT / "evidence" / "hypothesis_slate_20261025_r3_preregistered.sha256"
    assert sha_file.is_file()
    lines = [ln.strip() for ln in sha_file.read_text().splitlines() if ln.strip()]
    assert len(lines) == 2
    for ln in lines:
        expected_sha, rel_path = ln.split(None, 1)
        actual_sha = hashlib.sha256((ROOT / rel_path.strip()).read_bytes()).hexdigest()
        assert actual_sha == expected_sha


def test_anti_leakage_feature_and_column_contracts():
    assert "dist_known_fault_px" in FORBIDDEN_COLS
    assert not (WELLSPRING_ALLOWED_COLS & FORBIDDEN_COLS)
    assert not (VENT_ALLOWED_COLS & FORBIDDEN_COLS)
    # Regional raw level channels that caused H33-F's 0.9169 domain shift must remain excluded
    forbidden_raw_levels = {
        "det_elev", "depth_to_base_surf", "iso_grav_anom", "rtp", "mag_anom",
        "tmi", "cond_surf", "ieq_n100a15", "deq_n100a15",
    }
    assert not (set(CANDIDATE_CACHED_CHANNELS) & forbidden_raw_levels)


def test_exact_choquet_self_credit_matches_monte_carlo_and_stays_in_unit_interval():
    from vendor.gems57.metric import OFF_DX, OFF_DY, OFF_K

    rng = np.random.default_rng(12345)
    patch = rng.uniform(0.0, 0.45, size=(11, 11)).astype(np.float32)
    sc = exact_choquet_self_credit(patch)
    assert sc.dtype == np.float32
    assert sc.shape == patch.shape
    assert np.isfinite(sc).all()
    assert float(sc.min()) >= 0.0 and float(sc.max()) <= 1.0

    # Along a 1-px strand with p=0.5, sum(p*k) > 1.5 (IR-78-EMIT-JENSEN), whereas Choquet stays <= 1
    strand = np.zeros((11, 11), dtype=np.float32)
    strand[5, :] = 0.5
    sc_strand = exact_choquet_self_credit(strand)
    assert float(sc_strand[5, 5]) < 0.99

    # Verify analytic value at center against 100k Bernoulli Monte Carlo trials
    draws = rng.random((100_000, 11, 11)) < patch[None, :, :]
    mc = np.zeros(100_000, dtype=np.float64)
    for dy, dx, kw in zip(OFF_DY, OFF_DX, OFF_K):
        mc = np.maximum(mc, draws[:, 5 - dy, 5 - dx] * kw)
    assert abs(float(sc[5, 5]) - float(mc.mean())) < 0.003


def test_round3_geotiff_zip_and_run_card_contracts():
    rc_path = ROOT / "evidence" / "round3_da_hgcm_run_card_20261025.json"
    assert rc_path.is_file()
    rc_raw = rc_path.read_text()
    assert "/home/user/" not in rc_raw, "Committed Run Card must not leak sandbox host paths"
    rc = json.loads(rc_raw)

    # Rule 5 & Rule 6 Run Card required fields
    assert rc["experiments_run"] <= 3
    assert rc["budget_cap_respected"] is True
    assert rc["submission_slots_spent"] == 0
    assert rc["verdict"] in {"promote", "negative"}
    assert 1 <= len(rc["submission_name"]) <= 140
    assert 1 <= len(rc["note"]) <= 140
    assert rc["note_chars"] == len(rc["note"])
    assert rc["leakage_canary"]["pass"] is True
    assert rc["leakage_canary"]["max_oriented_auc"] <= 0.90

    # Provenance labels on holdout DTI
    hd = rc["holdout_dti"]
    assert hd["evidence_class"] == "HOLDOUT-DTI"
    assert hd["evaluator_version"] == "gems57-pooled-hide-v2"
    conf = hd["independent_confirmation_seeds_33_34"]
    assert conf["withheld_positive_pixels"] > 20_000
    assert len(conf["ci95_20km_block_bootstrap"]) == 2
    assert conf["ci95_20km_block_bootstrap"][0] < conf["dti"] < conf["ci95_20km_block_bootstrap"][1]
    assert conf["delta_vs_ctrl_ridge_b2_ci95"][0] > 0.0
    assert conf["delta_vs_ctrl_gbdt_ci95"][0] > 0.0

    # On-disk GeoTIFF & single-TIFF ZIP programmatic verification without human inspection
    tif_path = ROOT / rc["artifact_path"]
    zip_path = tif_path.with_suffix(".zip")
    man_path = ROOT / "docs" / "downloads" / "round3" / "round3-manifest.json"
    assert tif_path.is_file() and zip_path.is_file() and man_path.is_file()
    assert "/home/user/" not in man_path.read_text()

    actual_tif_sha = hashlib.sha256(tif_path.read_bytes()).hexdigest()
    actual_zip_sha = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    assert actual_tif_sha == rc["raster_sha256"]
    assert actual_zip_sha == rc["zip_sha256"]

    with zipfile.ZipFile(zip_path) as zf:
        assert zf.namelist() == [tif_path.name]
        assert zf.read(tif_path.name) == tif_path.read_bytes()

    with rasterio.open(tif_path) as ds:
        assert ds.count == 1
        assert ds.dtypes[0] == "float32"
        assert (ds.height, ds.width) == SHAPE
        assert str(ds.crs) == CRS_EPSG
        assert tuple(ds.transform)[:6] == tuple(TRANSFORM)[:6]
        assert ds.nodata is None
        arr = ds.read(1)

    assert np.isfinite(arr).all(), "All 12,279,160 cells must be finite (no NaN/Inf)"
    assert float(arr.min()) >= 0.0 and float(arr.max()) <= 1.0
    assert int((arr > 0).sum()) == 37_654

    # Optional cross-check against restored sample_submission.tif & existing_faults.tif when cached locally
    cache_data = Path(os.environ.get("GEMS_DATA_DIR", ROOT / ".cache" / "gems_data"))
    if (cache_data / "sample_submission.tif").is_file() and (cache_data / "existing_faults.tif").is_file():
        with rasterio.open(cache_data / "sample_submission.tif") as sds:
            fp = np.isfinite(sds.read(1))
        with rasterio.open(cache_data / "existing_faults.tif") as cds:
            cat = cds.read(1) > 0
        assert not np.any((arr > 0) & (~fp)), "Zero positive predictions allowed outside footprint"
        assert np.all(arr[~fp] == 0.0), "Outside-footprint cells must be exact 0.0"
        assert not np.any((arr > 0) & cat), "Zero positive predictions allowed on mapped catalogue"


def test_site_surfaces_current_status_and_keeps_round3_archive_linked():
    index_page = build_site.build_index()
    exec_page = build_site.build_exec()
    current_file = "gemsdoe33-fsml2-cc-37654-20261026-6fd4410bbaee-zeros.tif"
    for page_html in (index_page, exec_page):
        assert current_file in page_html
        assert "Current decision" in page_html
        assert "NO RASTER IS OK TO SUBMIT" in page_html
    assert "gemsdoe33-r3-da-hgcm-submod-37654-20261025-a6a8552e-zeros.tif" in index_page
    assert "gemsdoe33-r3-da-hgcm-37654-a6a8552e" in index_page
    assert "verdict: negative" in index_page
    assert "DO NOT AUTO-SUBMIT" in index_page
