import numpy as np

from gemsdoe33 import dpps


def _fp(shape=(40, 40)):
    return np.ones(shape, dtype=bool)


def test_rank_field_bounded_and_zero_outside():
    rng = np.random.default_rng(0)
    a = rng.normal(size=(40, 40)).astype(np.float32)
    fp = _fp()
    fp[:5, :] = False
    r = dpps.rank_field(a, fp)
    assert r.min() >= 0.0 and r.max() <= 1.0
    assert np.all(r[~fp] == 0.0)
    assert r[fp].max() == 1.0


def test_line_persistence_prefers_long_line_over_isolated_pixel():
    fp = _fp((41, 41))
    line = np.zeros((41, 41), dtype=np.float32)
    line[20, 5:36] = 1.0
    p_line = dpps.line_persistence(line, fp)
    iso = np.zeros((41, 41), dtype=np.float32)
    iso[20, 20] = 1.0
    p_iso = dpps.line_persistence(iso, fp)
    # centre of a 31-px line retains ~full line-mean; an isolated pixel is diluted ~1/n_steps
    assert p_line[20, 20] > 0.9
    assert p_iso[20, 20] < 0.2


def test_build_surfaces_finite_unit_range_and_void_fallback():
    rng = np.random.default_rng(1)
    shape = (60, 60)
    arrays = {}
    for name in dpps.INPUT_CHANNELS:
        arrays[name] = rng.normal(size=shape).astype(np.float32)
    arrays["lid_valid"] = np.full(shape, 255, dtype=np.float32)
    arrays["lid_valid"][:, :20] = 0  # LiDAR void strip -> DEM fallback must still produce values
    arrays["depth_to_base_surf"] = np.abs(arrays["depth_to_base_surf"]) * 500
    fp = _fp(shape)
    surface, ctrl, report = dpps.build_surfaces(arrays, fp)
    assert surface.shape == shape and ctrl.shape == shape
    assert np.isfinite(surface).all() and np.isfinite(ctrl).all()
    assert surface.min() >= 0.0 and surface.max() <= 1.0
    assert ctrl[:, :20].max() > 0.0
    assert report["catalogue_read_in_surface"] is False
    assert report["learned_weights"] is False


def test_dip_projection_shifts_crest_updip():
    # depth increases to the east (+x): buried crest at x=30 should support surface cells west of it.
    shape = (41, 41)
    arrays = {
        "iso_grav_anom_hg": np.zeros(shape, dtype=np.float32),
        "depth_to_base_surf": np.tile(np.linspace(0, 2000, shape[1]), (shape[0], 1)).astype(np.float32),
    }
    arrays["iso_grav_anom_hg"][:, 30] = 10.0
    fp = _fp(shape)
    g = dpps.dip_projected_gravity(arrays, fp)
    row = g[20]
    peak_x = int(np.argmax(row))
    assert peak_x < 30  # support moved updip (west) of the buried crest
    assert np.isfinite(g).all()
