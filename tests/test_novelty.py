import numpy as np
import pytest
from scipy.stats import spearmanr

from gemsdoe33.novelty import binary_comparison


def test_binary_phi_is_exact_tied_spearman():
    rng = np.random.default_rng(8)
    a, b = rng.random((31, 35)) < .2, rng.random((31, 35)) < .25
    foot = rng.random(a.shape) > .1
    result = binary_comparison(a, b, foot)
    assert result["spearman_rho"] == pytest.approx(spearmanr(a[foot], b[foot]).statistic)


def test_directional_overlap_and_euclidean_disk():
    a, b = np.zeros((20, 20), bool), np.zeros((20, 20), bool)
    b[5, 5] = True
    a[5, 8] = True   # exactly 3: included
    a[8, 8] = True   # sqrt(18): excluded
    result = binary_comparison(a, b, np.ones_like(a))
    assert result["candidate_dots_within_3px"] == 1
    assert result["fraction_candidate_within_3px"] == .5


def test_constant_raster_never_passes_guard():
    a = np.zeros((10, 10), bool)
    result = binary_comparison(a, a, ~a)
    assert result["spearman_rho"] is None
    assert result["fraction_candidate_within_3px"] is None
    assert result["guard_pass"] is False


def test_reencoding_binary_content_is_duplicate():
    a = np.eye(20, dtype=bool)
    result = binary_comparison(a, a.astype(float), np.ones_like(a))
    assert result["duplicate_trigger"] is True
    assert result["spearman_rho"] == 1


def test_soft_or_invalid_inputs_not_silently_binarized():
    a = np.eye(5, dtype=float)
    a[0, 0] = .3
    with pytest.raises(ValueError):
        binary_comparison(a, a, np.ones_like(a, bool))
