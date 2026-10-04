"""Unit tests for the DTI implementation (adapted from GEMSDOE28 tests)."""

import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gems33.metric import ALPHA, BETA, dti_binary, dti_exact, inclusion_threshold


def test_perfect_prediction_scores_one():
    g = np.zeros((20, 20), bool)
    g[10, 5:15] = True
    r = dti_binary(g.astype(float), g)
    assert abs(r["dti"] - 1.0) < 1e-6
    assert r["FPw"] == 0.0


def test_empty_prediction_scores_zero():
    g = np.zeros((20, 20), bool)
    g[10, 5:15] = True
    r = dti_binary(np.zeros((20, 20)), g)
    assert r["dti"] == 0.0
    assert r["FNw"] == g.sum()


def test_far_prediction_is_pure_false_positive():
    g = np.zeros((40, 40), bool)
    g[5, 5] = True
    p = np.zeros((40, 40))
    p[35, 35] = 1.0
    r = dti_binary(p, g)
    # TP=0, FP=1, FN=1 -> DTI = 0 / (0.2 + 0.8) = 0
    assert r["TPw"] == 0.0
    assert abs(r["FPw"] - 1.0) < 1e-9
    assert r["dti"] == 0.0


def test_kernel_credit_at_one_pixel():
    g = np.zeros((20, 20), bool)
    g[10, 10] = True
    p = np.zeros((20, 20))
    p[10, 11] = 1.0  # d=1 -> k=1-1/3=2/3
    r = dti_binary(p, g)
    assert abs(r["TPw"] - (1.0 - 1.0 / 3.0)) < 1e-9


def test_binary_and_exact_agree():
    rng = np.random.default_rng(7)
    g = rng.random((30, 30)) < 0.02
    p = (rng.random((30, 30)) < 0.02).astype(float)
    rb = dti_binary(p, g)
    re = dti_exact(p, g)
    assert abs(rb["TPw"] - re["TPw"]) < 1e-6
    assert abs(rb["FPw"] - re["FPw"]) < 1e-6
    assert abs(rb["dti"] - re["dti"]) < 1e-6


def test_known_mask_neutralises_catalogue_overlap():
    g = np.zeros((20, 20), bool)
    g[10, 10] = True
    p = np.zeros((20, 20))
    p[10, 10] = 1.0
    known = np.zeros((20, 20), bool)
    known[10, 10] = True
    r = dti_binary(p, g, known=known)
    # truth and prediction both masked -> nothing scored
    assert r["n_truth"] == 0


def test_inclusion_threshold_values():
    assert abs(inclusion_threshold(0.25) - 0.0526315789) < 1e-6
    t = inclusion_threshold(0.2708)
    assert 0.057 < t < 0.058
    assert inclusion_threshold(0.0) == 0.0


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print("PASS", fn.__name__)
    print(f"{len(fns)} metric tests passed")
