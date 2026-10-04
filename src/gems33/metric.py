"""Distance-weighted Tversky index (DTI), official definition.

Official definition (DrivenData #306 problem page, "Performance metric",
https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/):

    k(d)  = max(1 - d / 300 m, 0)                       (3 px at 100 m resolution)
    TPw   = sum_g max_x p(x) k(d(x, g))
    FPw   = sum_x p(x) (1 - max_g k(d(x, g)))
    FNw   = sum_g (1 - max_x p(x) k(d(x, g)))
    DTI   = TPw / (TPw + 0.2 FPw + 0.8 FNw + eps)

alpha = 0.2 (false positives), beta = 0.8 (false negatives).

Known-catalogue pixels are masked: predictions on them neither earn credit nor
cost false-positive mass, and truth never includes them (the competition scores
against *new* expert-labelled faults, not the existing catalogue). This
implementation is adapted from the campaign-validated GEMSDOE28
``src/gems27/metric.py`` (itself validated against a brute-force reference),
kept byte-for-byte equivalent in the quantities it reports.
"""

from __future__ import annotations

import numpy as np
from scipy.ndimage import distance_transform_edt

ALPHA = 0.2
BETA = 0.8
RADIUS_PX = 3.0
EPS = 1e-7


def kernel_from_distance(d: np.ndarray) -> np.ndarray:
    """Triangular tolerance kernel k(d) = (1 - d/R)+ in pixel units."""
    return np.maximum(1.0 - d / RADIUS_PX, 0.0)


def _prep(pred, truth, valid, known):
    pred = np.asarray(pred)
    truth = np.asarray(truth, bool)
    if pred.shape != truth.shape or pred.ndim != 2:
        raise ValueError("pred/truth must be equal-shaped 2-D grids")
    valid = np.ones(pred.shape, bool) if valid is None else np.asarray(valid, bool)
    known = np.zeros(pred.shape, bool) if known is None else np.asarray(known, bool)
    active = valid & ~known
    vals = pred[active]
    if not np.isfinite(vals).all() or np.any((vals < 0) | (vals > 1)):
        raise ValueError("evaluated predictions must be finite probabilities in [0,1]")
    p = np.where(active & np.isfinite(pred), pred, 0.0)
    g = truth & active
    return p, g, active


def dti_binary(pred, truth, valid=None, known=None) -> dict[str, float]:
    """Exact DTI for a {0,1} prediction using Euclidean distance transforms."""
    p, g, active = _prep(pred, truth, valid, known)
    if np.any((p != 0) & (p != 1)):
        raise ValueError("dti_binary needs a {0,1} prediction; use dti_exact for soft values")
    pb = p > 0.5
    n_truth = int(g.sum())
    if n_truth == 0:
        return {"TPw": 0.0, "FPw": float(pb.sum()), "FNw": 0.0, "n_truth": 0,
                "n_emitted": int(pb.sum()), "dti": 0.0, "recall_w": 0.0}
    if not pb.any():
        return {"TPw": 0.0, "FPw": 0.0, "FNw": float(n_truth), "n_truth": n_truth,
                "n_emitted": 0, "dti": 0.0, "recall_w": 0.0}
    d_to_p = distance_transform_edt(~pb)
    tp = float(kernel_from_distance(d_to_p[g]).sum())
    d_to_g = distance_transform_edt(~g)
    fp = float((1.0 - kernel_from_distance(d_to_g[pb])).sum())
    fn = n_truth - tp
    return {"TPw": tp, "FPw": fp, "FNw": fn, "n_truth": n_truth, "n_emitted": int(pb.sum()),
            "dti": tp / (tp + ALPHA * fp + BETA * fn + EPS), "recall_w": tp / n_truth}


def dti_exact(pred, truth, valid=None, known=None) -> dict[str, float]:
    """Exact DTI for soft predictions p in [0,1] (loops over the 3-px kernel footprint)."""
    p, g, _ = _prep(pred, truth, valid, known)
    n_truth = int(g.sum())
    H, W = p.shape
    yy, xx = np.nonzero(g)
    credit = np.zeros(n_truth)
    r = int(np.ceil(RADIUS_PX))
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            k = max(1.0 - float(np.hypot(dy, dx)) / RADIUS_PX, 0.0)
            if k <= 0:
                continue
            ny, nx = yy + dy, xx + dx
            ok = (ny >= 0) & (nx >= 0) & (ny < H) & (nx < W)
            credit[ok] = np.maximum(credit[ok], p[ny[ok], nx[ok]] * k)
    tp = float(credit.sum())
    d_to_g = distance_transform_edt(~g) if n_truth else np.full(p.shape, np.inf)
    fp = float((p * (1.0 - kernel_from_distance(d_to_g))).sum())
    fn = n_truth - tp
    return {"TPw": tp, "FPw": fp, "FNw": fn, "n_truth": n_truth, "n_emitted": int((p > 0).sum()),
            "dti": tp / (tp + ALPHA * fp + BETA * fn + EPS) if n_truth else 0.0,
            "recall_w": tp / n_truth if n_truth else 0.0}


def inclusion_threshold(dti: float) -> float:
    """Marginal credit per FP unit needed for an added pixel set to raise DTI.

    Adding pixels raises DTI iff  dTP / dFP  >  0.2*DTI / (1 - 0.2*DTI).
    Derivation: DTI = TP / D with D = 0.2(TP + FP) + 0.8|G|;
    DTI' > DTI  <=>  dTP*D > 0.2*TP*(dTP + dFP)
                 <=>  dTP/dFP > 0.2*DTI / (1 - 0.2*DTI).
    At DTI = 0.2708 this is 0.0573.
    """
    return (ALPHA * dti) / (1.0 - ALPHA * dti)
