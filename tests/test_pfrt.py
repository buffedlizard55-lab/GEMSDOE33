import numpy as np
from gemsdoe33 import pfrt


def _layers(shape=(60, 60)):
    y, x = np.mgrid[0:shape[0], 0:shape[1]]
    depth = (100 + 20 * x + 0 * y).astype(np.float32)  # deepens eastward; updip = west
    return {"depth": depth, "depth_gm": np.abs(np.gradient(depth)[1]).astype(np.float32) + (x == 30),
            "grav_hg": (x == 30).astype(np.float32) * 5}


def test_pfrt_surface_is_bounded_and_label_free():
    layers = _layers(); domain = np.ones((60, 60), bool)
    surf, rep = pfrt.pfrt_surface(layers, domain)
    assert surf.shape == domain.shape and np.isfinite(surf).all()
    assert (surf >= 0).all() and (surf <= 1).all() and rep["n_crest"] > 0


def test_pfrt_projects_west_of_east_deepening_crest():
    layers = _layers(); domain = np.ones((60, 60), bool)
    surf, _ = pfrt.pfrt_surface(layers, domain)
    # Crest is the x=30 line; updip (shallower) is -x, so mass must sit west of it.
    assert surf[:, 20:30].sum() > surf[:, 31:41].sum()
