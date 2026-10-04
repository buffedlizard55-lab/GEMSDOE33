"""Spatial grouping helper tests; quadrant groups are not candidate-validation evidence."""
import numpy as np
import pytest

from gemsdoe33.holdout import quadrant_ids


def test_quadrant_ids_assigns_only_footprint_and_four_ids():
    footprint = np.ones((10, 10), dtype=bool)
    footprint[0, 0] = False
    ids = quadrant_ids(footprint)
    assert ids.shape == footprint.shape
    assert ids[0, 0] == -1
    assert set(np.unique(ids[footprint])) == {0, 1, 2, 3}


def test_quadrant_ids_rejects_empty_and_non_2d_masks():
    with pytest.raises(ValueError):
        quadrant_ids(np.zeros((2, 2), dtype=bool))
    with pytest.raises(ValueError):
        quadrant_ids(np.ones(5, dtype=bool))
