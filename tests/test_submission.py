"""Local GeoTIFF writer/validator contract on a synthetic official-sized grid."""
from __future__ import annotations

import numpy as np
import pytest
import rasterio
from affine import Affine
from rasterio.crs import CRS

from gemsdoe33 import grid, submission


HEIGHT, WIDTH = 3730, 3292
TRANSFORM = Affine(100, 0, 243350, 0, -100, 4508550)
CRS_UTM11 = CRS.from_epsg(32611)


def test_package_writes_both_outside_variants_and_note(tmp_path, monkeypatch):
    footprint = np.ones((HEIGHT, WIDTH), dtype=bool)
    footprint[-1, -1] = False
    profile = {
        "driver": "GTiff", "height": HEIGHT, "width": WIDTH, "count": 1,
        "dtype": "float32", "crs": CRS_UTM11, "transform": TRANSFORM,
        "nodata": np.nan, "compress": "deflate", "predictor": 3,
    }
    monkeypatch.setattr(grid, "template_footprint", lambda: footprint)
    monkeypatch.setattr(grid, "template_profile", lambda: profile.copy())
    monkeypatch.setattr(grid, "template_georef", lambda: (TRANSFORM, WIDTH, HEIGHT, CRS_UTM11))

    mask = np.zeros_like(footprint)
    mask[100, 100] = True
    mask[100, 101] = True
    mask[100, 102] = True
    receipt = submission.build_package(
        mask, None, "synthetic-test", tmp_path,
        "test note {cid}",
    )

    assert receipt["all_checks_pass"]
    assert receipt["note_chars"] <= submission.MAX_NOTE
    assert receipt["emitted_pixels"] == 3
    assert receipt["nan"]["checks"]["outside_is_null_or_zero"]
    assert receipt["zeros"]["checks"]["outside_is_null_or_zero"]
    assert receipt["nan"]["sha256"] != receipt["zeros"]["sha256"]
    assert receipt["zip_nan"]["members"] == 1
    assert receipt["zip_zeros"]["members"] == 1
    assert receipt["note_chars"] <= 140
    assert receipt["nan"]["checks"]["all_finite_values_in_range_0_1"]
    assert not receipt["nan"]["checks"]["whole_array_finite"]
    assert receipt["zeros"]["checks"]["whole_array_finite_and_in_range_0_1"]


def _small_template(monkeypatch, *, footprint=None):
    footprint = np.ones((4, 5), dtype=bool) if footprint is None else footprint
    profile = {
        "driver": "GTiff", "height": footprint.shape[0], "width": footprint.shape[1],
        "count": 1, "dtype": "float32", "crs": CRS_UTM11,
        "transform": Affine(100, 0, 1000, 0, -100, 4000), "nodata": np.nan,
    }
    monkeypatch.setattr(grid, "template_footprint", lambda: footprint)
    monkeypatch.setattr(grid, "template_profile", lambda: profile.copy())
    monkeypatch.setattr(
        grid, "template_georef",
        lambda: (profile["transform"], profile["width"], profile["height"], profile["crs"]),
    )
    return footprint, profile


def test_writer_rejects_out_of_range_weights_instead_of_clipping(tmp_path, monkeypatch):
    footprint, _ = _small_template(monkeypatch)
    mask = np.zeros_like(footprint)
    mask[1, 2] = True
    weights = np.zeros(footprint.shape, dtype=np.float32)
    weights[1, 2] = 1.01

    with pytest.raises(ValueError, match=r"lie in \[0, 1\].*refusing to clip"):
        submission.build_package(mask, weights, "bad-range", tmp_path, "invalid output")
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("bad", [np.nan, np.inf, -np.inf])
def test_writer_rejects_nonfinite_emitted_weights(tmp_path, monkeypatch, bad):
    footprint, _ = _small_template(monkeypatch)
    mask = np.zeros_like(footprint)
    mask[1, 2] = True
    weights = np.zeros(footprint.shape, dtype=np.float64)
    weights[1, 2] = bad
    with pytest.raises(ValueError, match="must all be finite"):
        submission.build_package(mask, weights, "bad-nonfinite", tmp_path, "invalid output")
    assert list(tmp_path.iterdir()) == []


def test_writer_rejects_nan_inside_and_invalid_outside_value(tmp_path, monkeypatch):
    footprint, _ = _small_template(monkeypatch)
    with pytest.raises(ValueError, match="must all be finite"):
        submission.write_tif(np.full(int(footprint.sum()), np.nan), tmp_path / "nan-inside.tif")
    with pytest.raises(ValueError, match="outside must be NaN/null or 0.0"):
        submission.write_tif(np.zeros(int(footprint.sum())), tmp_path / "bad-outside.tif", outside=0.5)
    assert list(tmp_path.iterdir()) == []


def test_writer_rejects_complex_predictions_and_empty_footprint(tmp_path, monkeypatch):
    footprint, _ = _small_template(monkeypatch)
    with pytest.raises(ValueError, match="real-valued probabilities"):
        submission.write_tif(np.ones(int(footprint.sum()), dtype=np.complex64), tmp_path / "complex.tif")

    empty = np.zeros_like(footprint)
    _small_template(monkeypatch, footprint=empty)
    with pytest.raises(ValueError, match="non-empty 2-D mask"):
        submission.write_tif(np.array([], dtype=np.float32), tmp_path / "empty.tif")
    with pytest.raises(ValueError, match="equal-shaped 2-D arrays"):
        submission.build_package(empty, None, "empty-grid", tmp_path, "invalid")
    assert list(tmp_path.iterdir()) == []


def test_validator_rejects_infinity_outside_footprint(tmp_path, monkeypatch):
    footprint = np.ones((4, 5), dtype=bool)
    footprint[0, 0] = False
    _, profile = _small_template(monkeypatch, footprint=footprint)
    artifact = tmp_path / "outside-inf.tif"
    arr = np.zeros(footprint.shape, dtype=np.float32)
    arr[0, 0] = np.inf
    profile["nodata"] = None
    with rasterio.open(artifact, "w", **profile) as dst:
        dst.write(arr, 1)
        dst.set_band_description(1, "fault probability")

    report = submission.validate(artifact)
    assert not report["checks"]["outside_is_null_or_zero"]
    assert "outside_is_null_or_zero" in report["errors"]
    assert not report["checks"]["whole_array_finite"]


def test_package_refuses_to_overwrite_existing_outputs(tmp_path, monkeypatch):
    footprint, _ = _small_template(monkeypatch)
    mask = np.zeros_like(footprint)
    mask[1, 2] = True
    first = submission.build_package(mask, None, "same-name", tmp_path, "first output")
    originals = {path.name: path.read_bytes() for path in tmp_path.iterdir()}

    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        submission.build_package(mask, None, "same-name", tmp_path, "changed note")
    assert {path.name: path.read_bytes() for path in tmp_path.iterdir()} == originals
    assert first["zeros"]["bytes"] > 0
    assert first["nan"]["bytes"] > 0


def test_package_enforces_short_note_and_filename_safe_name(tmp_path, monkeypatch):
    footprint, _ = _small_template(monkeypatch)
    mask = np.zeros_like(footprint)
    with pytest.raises(ValueError, match="filename-safe identifier"):
        submission.build_package(mask, None, "../escape", tmp_path, "note")
    with pytest.raises(ValueError, match="limit 140"):
        submission.build_package(mask, None, "long-note", tmp_path, "n" * 141)
    assert list(tmp_path.iterdir()) == []
