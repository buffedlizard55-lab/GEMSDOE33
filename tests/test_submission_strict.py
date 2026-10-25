import numpy as np
import pytest
import rasterio
from affine import Affine

from gemsdoe33 import grid, submission


@pytest.fixture
def tiny_grid(monkeypatch):
    footprint = np.ones((4, 5), bool)
    footprint[0, 0] = False
    transform = Affine(100, 0, 243350, 0, -100, 4508550)
    crs = rasterio.crs.CRS.from_epsg(32611)
    profile = {"driver": "GTiff", "height": 4, "width": 5, "count": 1,
               "dtype": "float32", "crs": crs, "transform": transform}
    monkeypatch.setattr(grid, "template_footprint", lambda: footprint)
    monkeypatch.setattr(grid, "template_profile", lambda: profile.copy())
    monkeypatch.setattr(grid, "template_georef", lambda: (transform, 5, 4, crs))
    return footprint


@pytest.mark.parametrize("bad", [np.nan, np.inf, -np.inf, -1e-8, 1.00000001])
def test_writer_rejects_invalid_values_before_float32_rounding(tmp_path, tiny_grid, bad):
    values = np.zeros(tiny_grid.shape, dtype=np.float64)
    values[1, 1] = bad
    path = tmp_path / "bad.tif"
    with pytest.raises(ValueError, match="finite and in"):
        submission.write_tif(values, path)
    assert not path.exists()


def test_writer_checks_shape_and_infinite_outside(tmp_path, tiny_grid):
    with pytest.raises(ValueError, match="shape"):
        submission.write_tif(np.zeros((2, 2)), tmp_path / "bad.tif")
    with pytest.raises(ValueError, match="outside"):
        submission.write_tif(np.zeros(tiny_grid.shape), tmp_path / "bad.tif", outside=np.inf)


def test_full_shape_writer_does_not_consume_template_values(tmp_path, tiny_grid):
    values = np.zeros(tiny_grid.shape)
    values[1, 1] = .3
    values[0, 0] = np.nan  # ignored outside
    p = tmp_path / "good.tif"
    submission.write_tif(values, p, outside=0)
    with rasterio.open(p) as ds:
        arr = ds.read(1)
    assert np.isfinite(arr).all()
    assert arr[1, 1] == pytest.approx(.3)
    assert arr[0, 0] == 0


def test_package_rejects_invalid_weights_and_overlong_note_before_writing(tmp_path, tiny_grid):
    mask = np.zeros_like(tiny_grid)
    mask[1, 1] = True
    weights = np.zeros(mask.shape)
    weights[1, 1] = np.inf
    with pytest.raises(ValueError, match="no silent clipping"):
        submission.build_package(mask, weights, "bad", tmp_path, "note")
    with pytest.raises(ValueError, match="limit 140"):
        submission.build_package(mask, None, "bad", tmp_path, "x" * 141)
    assert list(tmp_path.iterdir()) == []


def test_package_validator_returns_failure_not_index_error_for_wrong_shape(tmp_path, tiny_grid):
    profile = grid.template_profile()
    profile["height"] = 2
    p = tmp_path / "shape.tif"
    with rasterio.open(p, "w", **profile) as ds:
        ds.write(np.zeros((2, 5), dtype=np.float32), 1)
    result = submission.validate(p)
    assert not result["pass"]
    assert "footprint_shape_matches" in result["errors"]


def test_soft_content_ids_and_actual_positive_counts(tmp_path, tiny_grid):
    mask = np.zeros_like(tiny_grid)
    mask[1, 1:3] = True
    a = np.zeros(mask.shape)
    a[1, 1] = .3
    r1 = submission.build_package(mask, a, "weighted", tmp_path, "test only")
    a[1, 1] = .7
    r2 = submission.build_package(mask, a, "weighted", tmp_path, "test only")
    assert r1["content_id"] != r2["content_id"]
    assert r1["emitted_pixels"] == r2["emitted_pixels"] == 1
    assert r1["zeros"]["sha256"] != r2["zeros"]["sha256"]


def test_numpy_nan_outside_has_nan_nodata(tmp_path, tiny_grid):
    p = tmp_path / "nan.tif"
    submission.write_tif(np.zeros(tiny_grid.shape), p, outside=np.float32(np.nan))
    with rasterio.open(p) as ds:
        assert np.isnan(ds.nodata)
