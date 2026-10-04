"""A holdout instrument whose *geometry* matches the live scoring, not just its formula.

Why the previous instruments could not choose a budget
------------------------------------------------------
GEMSDOE32 measured (and this repository reproduced the inputs for) the following: with the whole
visible catalogue used as truth, the proxy score is **anti-monotone** in emission size while the
live board is monotone:

    emission        dots     live [OWNER-REPORT]   catalogue-proxy DTI [MEASURED]
    parent H19-5    121,131  0.1922                0.1663512
    dotted d=1.5     60,069  0.2477                0.1719287
    dotted d=2.8     44,090  0.2600                0.1617720

The reason is a *geometry* mismatch, not a formula error.  Two properties of the live scoring are
missing from a whole-catalogue proxy:

1.  **Truth size.**  The organiser scores only newly-mapped faults; the inversion of three live
    returns puts |G| at ~12,226 px, while the visible catalogue is 60,988 px — 5.0x too large.
    Because the metric's optimum satisfies ``marginal credit per dot = alpha * DTI``, an inflated
    |G| depresses DTI, lowers the bar, and pushes the proxy's optimum to a far larger budget.

2.  **Catalogue blindness.**  Dots that land on an *already compiled* fault earn nothing live.
    A whole-catalogue proxy pays them full credit.

This module restores both.  A hidden set H is drawn from the catalogue with

*   size |H| = ``n_truth`` (default 12,226, the inverted live estimate) — geometry (1);
*   sampling weight increasing with *mapping-incompleteness*, proxied by low GDR exploration
    intensity, so the hidden set sits where the real hidden set must sit — not uniformly;
*   the **entire** catalogue removed from the emission domain, so catalogue dots earn nothing —
    geometry (2);
*   spatial blocking into four quadrants, so each fold's truth was never seen by that fold's model.

The instrument is then *calibrated against three live-scored emissions that are on disk*: it is
only trusted for budget/content decisions if it reproduces the live ordering
44,090 > 60,069 > 121,131.
"""

from __future__ import annotations

import numpy as np
from scipy.ndimage import binary_dilation, distance_transform_edt, label

from . import grid, metric

# Inverted from the three live returns (see evidence/live_inversion.json when generated).
K_HIDDEN_ESTIMATE = 12226


def quadrant_ids(footprint: np.ndarray) -> np.ndarray:
    """0=NW, 1=NE, 2=SW, 3=SE, split at the median row/col of the footprint."""
    yy, xx = np.nonzero(footprint)
    ym, xm = int(np.median(yy)), int(np.median(xx))
    H, W = footprint.shape
    gy, gx = np.ogrid[:H, :W]
    q = np.full((H, W), -1, np.int8)
    q[(gy < ym) & (gx < xm) & footprint] = 0
    q[(gy < ym) & (gx >= xm) & footprint] = 1
    q[(gy >= ym) & (gx < xm) & footprint] = 2
    q[(gy >= ym) & (gx >= xm) & footprint] = 3
    return q


def fault_system_components(labels: np.ndarray) -> tuple[np.ndarray, int]:
    """8-connected components of the catalogue raster = 'fault systems' for LOSFO splitting."""
    return label(labels, structure=np.ones((3, 3), dtype=int))


def make_hidden_set(labels: np.ndarray, footprint: np.ndarray, seed: int,
                    n_truth: int = K_HIDDEN_ESTIMATE,
                    incompleteness: np.ndarray | None = None,
                    folds: np.ndarray | None = None, fold: int | None = None,
                    buffer_px: int = 0) -> np.ndarray:
    """Draw a hidden truth set of ``n_truth`` catalogue pixels, exploration-weighted.

    ``incompleteness`` is a non-negative field, higher where the compilation is more likely to be
    incomplete (here: low GDR exploration intensity).  Sampling is without replacement with
    probability proportional to it, restricted to ``fold`` when spatial blocking is requested.
    """
    rng = np.random.default_rng(seed)
    cand = labels & footprint
    if folds is not None and fold is not None:
        cand = cand & (folds == fold)
        if buffer_px:
            outside = labels & footprint & (folds != fold)
            cand = cand & ~binary_dilation(outside, iterations=buffer_px,
                                           structure=np.ones((3, 3), bool))
    idx = np.flatnonzero(cand.ravel())
    if idx.size == 0:
        raise ValueError("no candidate truth pixels in the requested fold")
    if incompleteness is None:
        w = np.ones(idx.size)
    else:
        w = np.asarray(incompleteness, float).ravel()[idx]
        w = np.clip(w, 0, None)
        if w.sum() <= 0:
            w = np.ones(idx.size)
    w = w / w.sum()
    take = min(n_truth, idx.size)
    pick = rng.choice(idx, size=take, replace=False, p=w)
    hidden = np.zeros(labels.size, bool)
    hidden[pick] = True
    return hidden.reshape(labels.shape)


def emission_domain(footprint: np.ndarray, labels: np.ndarray, collar_px: int = 1) -> np.ndarray:
    """Where a submission may emit: the footprint with the whole catalogue (collared) removed."""
    dom = footprint.copy()
    if collar_px:
        dom &= ~binary_dilation(labels, iterations=collar_px, structure=np.ones((3, 3), bool))
    else:
        dom &= ~labels
    return dom


def calibrated_domain(footprint: np.ndarray, labels: np.ndarray, hidden: np.ndarray,
                      collar_px: int = 1) -> np.ndarray:
    """Emission domain for one hidden draw: remove the *visible* catalogue, keep the hidden part.

    This is the step that makes the proxy geometrically faithful.  Live, a dot on an already
    compiled fault earns nothing, so the visible catalogue must be removed from the domain; but
    the hidden draw must stay inside it, otherwise the truth set itself is masked out of the
    scoring region and every score collapses to zero.

    A residual, *common* bias remains: the shipped emissions were zeroed on the whole catalogue,
    hidden part included, so they own no dot exactly on a hidden pixel and collect only the
    kernel's off-crest credit.  Because all three calibration emissions are masked identically the
    bias is shared and relative orderings stay informative; the absolute proxy DTI is therefore
    reported but never compared with a live number.
    """
    visible = labels & ~hidden
    dom = footprint.copy()
    if collar_px:
        dom &= ~binary_dilation(visible, iterations=collar_px, structure=np.ones((3, 3), bool))
    else:
        dom &= ~visible
    # The collar must never eat the truth itself: a hidden pixel that touches a visible catalogue
    # pixel is still part of the hidden fault and must stay inside the scored region.
    dom |= (np.asarray(hidden, bool) & footprint)
    return dom


def score(emission: np.ndarray, hidden: np.ndarray, domain: np.ndarray) -> dict:
    """Official DTI of a binary emission against a hidden set, on the emission domain."""
    r = metric.dti_binary(emission.astype(np.float32), hidden, valid=domain, known=None)
    r["dti"] = float(r["dti"])
    return r


def mask_to_domain(emission: np.ndarray, domain: np.ndarray) -> np.ndarray:
    return np.asarray(emission, bool) & domain


def reconstruct_shadow(emission: np.ndarray, hidden: np.ndarray, radius_px: int = 2) -> np.ndarray:
    """Undo the catalogue mask on the hidden draw.

    Every shipped emission was zeroed on *all* catalogue pixels, so none of them owns a dot on a
    hidden pixel — they collect only off-crest kernel credit there.  Live, a hidden fault is not
    in the catalogue and the emitter is free to place a dot on its crest.  This helper restores
    that: a hidden pixel gets a dot iff the emission already has a dot within ``radius_px``, i.e.
    iff the emitter's own ridge passes through it.  It is a reconstruction of what the *same*
    emitter would have produced had the hidden fault been absent from the catalogue, and it is
    applied identically to every arm so the comparison stays matched.
    """
    em = np.asarray(emission, bool)
    near = binary_dilation(em, iterations=radius_px, structure=np.ones((3, 3), bool))
    return em | (np.asarray(hidden, bool) & near)


# -----------------------------------------------------------------------------------------
# the calibration ladder
# -----------------------------------------------------------------------------------------
def calibration_ladder(emissions: dict[str, np.ndarray], labels: np.ndarray,
                       footprint: np.ndarray, seeds=(0, 1, 2),
                       n_truth: int = K_HIDDEN_ESTIMATE,
                       incompleteness: np.ndarray | None = None,
                       quadrant: bool = False,
                       reconstruct: bool = False,
                       buffer_px: int = 0) -> dict:
    """Score several emissions against repeated draws of the calibrated hidden set.

    ``emissions`` maps a name to a boolean grid.  Every emission is masked to the same emission
    domain, so the comparison is exactly matched in emitted mass support.
    """
    folds = quadrant_ids(footprint) if quadrant else None
    fold_list = [None] if not quadrant else [0, 1, 2, 3]
    rows = []
    for seed in seeds:
        for fold in fold_list:
            hidden = make_hidden_set(labels, footprint, seed, n_truth=n_truth,
                                     incompleteness=incompleteness,
                                     folds=folds, fold=fold, buffer_px=buffer_px)
            domain = calibrated_domain(footprint, labels, hidden, collar_px=1)
            for name, em in emissions.items():
                e = mask_to_domain(em, domain)
                if reconstruct:
                    e = reconstruct_shadow(e, hidden)
                r = score(e, hidden, domain)
                rows.append({"emission": name, "seed": int(seed), "fold": fold,
                             "dti": r["dti"], "TPw": r["TPw"], "FPw": r["FPw"],
                             "n_emitted": r["n_emitted"], "n_truth": r["n_truth"]})
    out = {}
    for name in emissions:
        rs = [r for r in rows if r["emission"] == name]
        d = np.array([r["dti"] for r in rs])
        out[name] = {
            "mean_dti": float(d.mean()), "std_dti": float(d.std(ddof=1)) if len(d) > 1 else 0.0,
            "n_cells": len(d), "mean_emitted": float(np.mean([r["n_emitted"] for r in rs])),
            "mean_TPw": float(np.mean([r["TPw"] for r in rs])),
            "mean_FPw": float(np.mean([r["FPw"] for r in rs])),
            "per_cell": rs,
        }
    out["_settings"] = dict(n_truth=n_truth, seeds=list(seeds), quadrant=quadrant,
                            n_cells=len(seeds) * len(fold_list),
                            incompleteness=incompleteness is not None)
    return out


def monotone_check(ladder: dict, order: list[str]) -> dict:
    """Does the instrument reproduce a known live ordering of emissions?"""
    means = [ladder[k]["mean_dti"] for k in order if k in ladder]
    ok = all(a > b for a, b in zip(means, means[1:]))
    return {"order": order, "means": [round(m, 6) for m in means],
            "reproduces_live_ordering": bool(ok and len(means) == len(order))}
