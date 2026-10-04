"""Distance-weighted Tversky index (DTI), reimplemented from the official metric page.

Source: DrivenData GEMS #306, "Performance metric":
https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/

For pixel size 100 m and support radius R=300 m=3 pixels, the triangular kernel is
``k(d)=max(1-d/R,0)``. The official page defines distance-weighted TP, FP and FN and uses
alpha=0.2, beta=0.8:

    TP = sum_{g in G} max_x p(x) k(d(x,g))
    FP = sum_x p(x) [1 - max_{g in G} k(d(x,g))]
    FN = sum_{g in G} [1 - max_x p(x) k(d(x,g))]
    DTI = TP / (TP + alpha*FP + beta*FN + eps)

Since ``FN=|G|-TP`` identically, the denominator also equals
``alpha*(TP+FP)+beta*|G|`` (because alpha+beta=1).

Important marginal-value distinction
------------------------------------
For a proposed addition, let ``dTP`` be its *incremental* true-positive credit after the max over
existing predictions, and ``dFP`` its incremental distance-weighted false-positive mass. Then

    DTI increases  iff  dTP/dFP > alpha*DTI / (1-alpha*DTI).

This ratio threshold is the exact general rule. In the special case of an isolated unit-probability
dot whose full kernel weight ``k`` is not already covered by another prediction, ``dTP=k`` and
``dFP=1-k``; the same condition simplifies to ``k > alpha*DTI``. That simplified pointwise rule
is **not** exact for overlapping dots or soft fields, because the TP term is a maximum and the
increment ``dTP`` can be smaller than ``k``. This subtlety matters when thinning a dense line.
"""

from __future__ import annotations

import numpy as np
from scipy.ndimage import distance_transform_edt

ALPHA = 0.2
BETA = 0.8
RADIUS_PX = 3.0
EPS = 1e-7


def kernel_from_distance(d: np.ndarray | float) -> np.ndarray:
    """Triangular kernel k(d) = max(1 - d/3 px, 0)."""
    return np.maximum(1.0 - np.asarray(d) / RADIUS_PX, 0.0)


def isolated_dot_bar(dti: float) -> float:
    """Pointwise ``k`` threshold for an *isolated* unit-mass dot: ``k > alpha*DTI``."""
    return ALPHA * float(dti)


def ratio_bar(dti: float) -> float:
    """Exact required incremental ``dTP/dFP`` ratio for any candidate addition."""
    s = float(dti)
    if s < 0 or s >= 1:
        raise ValueError("dti must lie in [0, 1)")
    return ALPHA * s / (1.0 - ALPHA * s)


def _prep(pred, truth, valid, known):
    pred = np.asarray(pred, dtype=np.float64)
    truth = np.asarray(truth, dtype=bool)
    if pred.shape != truth.shape or pred.ndim != 2:
        raise ValueError("pred/truth must be equal-shaped 2-D grids")
    valid = np.ones(pred.shape, bool) if valid is None else np.asarray(valid, bool)
    known = np.zeros(pred.shape, bool) if known is None else np.asarray(known, bool)
    if valid.shape != pred.shape or known.shape != pred.shape:
        raise ValueError("valid/known masks must match pred shape")
    active = valid & ~known
    vals = pred[active]
    if not np.isfinite(vals).all():
        raise ValueError("evaluated predictions must be finite")
    if np.any((vals < 0) | (vals > 1)):
        raise ValueError("evaluated predictions must lie in [0, 1]")
    p = np.where(active, pred, 0.0)
    g = truth & active
    return p, g, active


def dti_binary(pred, truth, valid=None, known=None) -> dict:
    """Exact DTI for a {0,1} prediction, using Euclidean distance transforms.

    ``known`` masks catalogue pixels that the scorer removes from both prediction and truth. The
    returned distances are over the supplied truth after masking.
    """
    p, g, _ = _prep(pred, truth, valid, known)
    if np.any((p != 0) & (p != 1)):
        raise ValueError("dti_binary needs a {0,1} prediction; use dti_exact for soft values")
    pb = p > 0.5
    n_truth = int(g.sum())
    n_emit = int(pb.sum())
    if n_truth == 0:
        return {"TPw": 0.0, "FPw": float(n_emit), "FNw": 0.0, "n_truth": 0,
                "n_emitted": n_emit, "dti": 0.0, "recall_w": 0.0}
    if not pb.any():
        return {"TPw": 0.0, "FPw": 0.0, "FNw": float(n_truth), "n_truth": n_truth,
                "n_emitted": 0, "dti": 0.0, "recall_w": 0.0}
    d_to_p = distance_transform_edt(~pb)
    tp = float(kernel_from_distance(d_to_p[g]).sum())
    d_to_g = distance_transform_edt(~g)
    fp = float((1.0 - kernel_from_distance(d_to_g[pb])).sum())
    fn = n_truth - tp
    dti = tp / (tp + ALPHA * fp + BETA * fn + EPS)
    return {"TPw": tp, "FPw": fp, "FNw": fn, "n_truth": n_truth,
            "n_emitted": n_emit, "dti": dti, "recall_w": tp / n_truth}


def dti_exact(pred, truth, valid=None, known=None) -> dict:
    """Exact DTI for soft predictions p in [0,1], by scanning the 3-px kernel footprint."""
    p, g, _ = _prep(pred, truth, valid, known)
    n_truth = int(g.sum())
    H, W = p.shape
    yy, xx = np.nonzero(g)
    credit = np.zeros(n_truth, dtype=np.float64)
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
    dti = tp / (tp + ALPHA * fp + BETA * fn + EPS) if n_truth else 0.0
    return {"TPw": tp, "FPw": fp, "FNw": fn, "n_truth": n_truth,
            "n_emitted": int((p > 0).sum()), "dti": dti,
            "recall_w": tp / n_truth if n_truth else 0.0}


def marginal_gain(base, add, truth, valid=None, known=None) -> dict:
    """Exact ``dTP``, ``dFP`` and DTI change from unioning binary masks ``base`` and ``add``."""
    b = np.asarray(base, bool)
    a = np.asarray(add, bool)
    if b.shape != a.shape:
        raise ValueError("base/add shapes must match")
    active_pred, g, active = _prep(b.astype(float), truth, valid, known)
    b = (active_pred > 0.5)
    a = a & active & ~b
    base_result = dti_binary(b.astype(float), g, valid=active)
    union_result = dti_binary((b | a).astype(float), g, valid=active)
    n_added = int(a.sum())
    d_tp = float(union_result["TPw"] - base_result["TPw"])
    d_fp = float(union_result["FPw"] - base_result["FPw"])
    return {"dTP": d_tp, "dFP": d_fp,
            "dTP_dFP": d_tp / d_fp if d_fp > 0 else float("inf"),
            "n_added": n_added, "dti_base": float(base_result["dti"]),
            "dti_union": float(union_result["dti"]),
            "n_truth": int(base_result["n_truth"]),
            "TP0": float(base_result["TPw"]), "TP1": float(union_result["TPw"]),
            "FP0": float(base_result["FPw"]), "FP1": float(union_result["FPw"])}


def required_credit(target_dti: float, n_dots: int, n_truth: int, rho: float = 1.0) -> float:
    """Solve the conditional inversion for TP ``T`` at specified score, budget and rho.

    This is only a model inversion: the caller must define ``rho = matched_mass / T`` and provide
    a defensible ``n_truth``. It is not an independent observation of the competition labels.
    """
    s = float(target_dti)
    denom = 1.0 - ALPHA * s * (1.0 - rho)
    return s * (ALPHA * n_dots + BETA * n_truth) / denom
