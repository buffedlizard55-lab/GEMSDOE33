"""Proxy validation protocols (catalogue is the only local truth substitute).

IMPORTANT: the competition is scored against *new expert-labelled faults that
are not in the public catalogue*. The catalogue itself is therefore a proxy
truth, not the scoring truth. These proxy metrics are not competition scores.
The catalogue-hidden evaluator below scores a pre-built prediction; it does not
rebuild candidates or exclude source geometries per fold, so it is invalid for
promotion when candidate construction can depend on catalogue-derived inputs.
Use the source-audit runner for conditional C2 diagnostics. Candidate-specific
threshold preregistration must be established separately; see evidence/holdout33.json.

P1 ``catalogue_hidden``  — spatially blocked leave-fold-out over catalogue fault
   systems (600 m grouping buffer, 2x2 quadrant folds). Each fold hides one
   quadrant's catalogue systems; DTI is measured on hidden pixels only.
   This is the catalogue-gap proxy used by GEMSDOE28/GEMSDOE29.

P2 ``sgmc_off_catalogue`` — DTI against faults rasterised from the USGS State
   Geologic Map Compilation (SGMC) that lie >= 300 m from the supplied
   catalogue. Independent compilation, different vintage and scope; the best
   local stand-in for "faults the catalogue does not list".

A candidate passes the slot gate when its paired mean DeltaDTI vs the control
is positive on P1 (majority of folds) AND it does not lose on P2.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .grid import catalogue_systems, data_dir, fold_masks, load_catalogue, load_raster, load_template
from .metric import dti_binary

SGMC_MIN_CATALOGUE_DIST_PX = 3.0


def sgmc_off_catalogue_truth(sgmc_path: Path | None = None, catalogue=None, footprint=None) -> np.ndarray:
    """SGMC-derived fault pixels at least 300 m from the supplied catalogue."""
    from scipy.ndimage import distance_transform_edt

    sgmc_path = Path(sgmc_path or data_dir() / "external" / "derived_sgmc_faults_100m_u8.tif")
    sgmc, _ = load_raster(sgmc_path)
    sgmc = sgmc > 0
    if catalogue is None:
        catalogue = load_catalogue()
    if footprint is None:
        footprint, _ = load_template()
    if catalogue.any():
        d_cat = distance_transform_edt(~catalogue)
    else:
        d_cat = np.full(sgmc.shape, np.inf)
    return sgmc & footprint & (d_cat >= SGMC_MIN_CATALOGUE_DIST_PX)


def catalogue_hidden_folds(buffer_px: int = 6, n_folds: int = 4) -> list[np.ndarray]:
    catalogue = load_catalogue()
    systems = catalogue_systems(catalogue, buffer_px=buffer_px)
    return fold_masks(systems, n_folds=n_folds)


def evaluate_proxy(pred: np.ndarray, control: np.ndarray, *, buffer_px: int = 6,
                   n_folds: int = 4, use_sgmc: bool = True) -> dict:
    """Legacy paired evaluation of pre-built ``pred`` vs ``control`` arrays.

    Returns fold-wise and mean DeltaDTI for P1 plus absolute DTI on P2. This
    function masks labels only during scoring; it does not rebuild either
    array per fold or exclude catalogue-derived source geometry. Do not use it
    as a promotion gate for source-dependent candidates.
    """
    footprint, _ = load_template()
    catalogue = load_catalogue()
    valid = footprint
    known = catalogue

    out = {"p1_folds": [], "p1_mean_d_dti": None, "p2": None}
    masks = catalogue_hidden_folds(buffer_px=buffer_px, n_folds=n_folds)
    diffs = []
    for i, m in enumerate(masks):
        truth = m & footprint
        if truth.sum() == 0:
            continue
        # LOSFO rule: the hidden fold's systems (dilated by the grouping
        # buffer) are removed from the known mask so they stay scorable;
        # every other catalogue pixel remains masked exactly as in live play.
        from scipy.ndimage import binary_dilation

        grown = binary_dilation(m, structure=np.ones((2 * buffer_px + 1, 2 * buffer_px + 1), bool))
        known_fold = known & ~grown
        rp = dti_binary(pred, truth, valid=valid, known=known_fold)
        rc = dti_binary(control, truth, valid=valid, known=known_fold)
        diffs.append(rp["dti"] - rc["dti"])
        out["p1_folds"].append({
            "fold": i,
            "n_truth": rp["n_truth"],
            "pred_dti": rp["dti"],
            "control_dti": rc["dti"],
            "d_dti": rp["dti"] - rc["dti"],
            "pred_tp": rp["TPw"], "pred_fp": rp["FPw"],
            "control_tp": rc["TPw"], "control_fp": rc["FPw"],
        })
    out["p1_mean_d_dti"] = float(np.mean(diffs)) if diffs else None
    out["p1_positive_folds"] = int(sum(1 for d in diffs if d > 0))
    out["p1_n_folds"] = len(diffs)

    if use_sgmc:
        truth2 = sgmc_off_catalogue_truth(catalogue=catalogue, footprint=footprint)
        rp2 = dti_binary(pred, truth2, valid=valid, known=known)
        rc2 = dti_binary(control, truth2, valid=valid, known=known)
        out["p2"] = {
            "n_truth": rp2["n_truth"],
            "pred_dti": rp2["dti"], "control_dti": rc2["dti"],
            "d_dti": rp2["dti"] - rc2["dti"],
            "pred_recall_w": rp2["recall_w"], "control_recall_w": rc2["recall_w"],
        }
    return out


def gate_summary(report: dict, bar_mean_d_dti: float = 0.0) -> dict:
    """Fail-closed numeric P1/P2 threshold check; not a protocol-validity check.

    A numeric pass requires a positive paired P1 mean, strictly more than half
    of the nonempty folds positive, and a measured P2 delta no worse than
    -0.001. Missing folds or a missing P2 measurement never count as a pass.
    The caller must independently establish that candidate construction and
    source features were fold-safe before any slot decision.
    """
    p1 = report.get("p1_mean_d_dti")
    p2 = (report.get("p2") or {}).get("d_dti")
    try:
        n_folds = int(report.get("p1_n_folds", 0))
        positive_folds = int(report.get("p1_positive_folds", 0))
        p1_value = float(p1)
        p2_value = float(p2)
        bar_value = float(bar_mean_d_dti)
    except (TypeError, ValueError):
        n_folds = positive_folds = 0
        p1_value = p2_value = float("nan")
        bar_value = float(bar_mean_d_dti)

    folds_ok = n_folds > 0 and 0 <= positive_folds <= n_folds and 2 * positive_folds > n_folds
    verdict = {
        "p1_above_bar": bool(np.isfinite(p1_value) and p1_value > bar_value),
        "p1_majority_folds_positive": bool(folds_ok),
        "p2_not_worse": bool(np.isfinite(p2_value) and p2_value >= -0.001),
    }
    verdict["pass"] = all(verdict.values())
    return verdict
