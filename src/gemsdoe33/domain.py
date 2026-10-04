"""Domain adaptation primitives — with an explicit warning about the present data.

The owner prompt proposes transferring faults from a better-mapped analog field. The official paper
is Ben-David et al. (2010), *A theory of learning from different domains*, Machine Learning 79,
151–175, https://doi.org/10.1007/s10994-009-5152-4. In their Theorem 2, under the stated i.i.d.
sample and finite-VC assumptions, one form of the bound is

    eps_T(h) <= eps_S(h) + 0.5 * d_hat_{HΔH}(U_S,U_T)
                + 4*sqrt((2*d*log(2*m') + log(2/delta))/m') + lambda,

where lambda is the combined error of the best joint hypothesis and d_hat is an empirical
HΔH-divergence. Their Lemma 2 relates d_hat to the error of an optimal domain discriminator in a
symmetric hypothesis class. An arbitrary classifier two-sample test, on spatially autocorrelated
cells with an unmeasured hypothesis-class complexity, is **not** a numerical Ben-David bound.

Current status: this repository has NOT completed the requested field-to-field transfer. The
first-pass code used top/bottom GDR well/spring point-density regions as a proxy for source/target,
not named geothermal fields; it counted multiple attribute rows at the same site; and it split
spatially autocorrelated cells at random. Those measurements are archived but withdrawn as a
formal divergence or transfer result (``IR-33-DA-01``). A promising official source is the public,
CC-BY 4.0 DOE/GDR BRIDGE GIS archive (submission 1682), whose README states that its LiDAR fault
picks have been field-verified in Dixie Valley and Gabbs Valley. The official page and file listing
were verified; the sandbox's direct HTTPS download failed with HTTP 000, so the vector payload is
not yet staged or inspected.
"""

from __future__ import annotations

import csv
import numpy as np
from scipy.ndimage import gaussian_filter
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

from . import grid


def documented_site_density(kernel_px: float = 30.0) -> np.ndarray:
    """Gaussian density of *unique* GDR 1391 well/spring map cells.

    This is documented geothermal sampling density, not a demonstrated fault-mapping effort
    surface. The CSV has 27,092 layer/attribute rows but only 12,570 distinct 100-m cells; count a
    cell once so repeated rows from chemistry/temperature/feature tables do not masquerade as
    independent field visits. The result is an exploratory covariate only.
    """
    H, W = grid.template_footprint().shape
    cells: set[tuple[int, int]] = set()
    with (grid.DATA / "gdr_wellspring_in_footprint.csv").open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            try:
                rr = int(row["row"])
                cc = int(row["col"])
            except (KeyError, TypeError, ValueError):
                continue
            if 0 <= rr < H and 0 <= cc < W:
                cells.add((rr, cc))
    counts = np.zeros((H, W), dtype=np.float32)
    if cells:
        rr, cc = zip(*cells)
        counts[np.asarray(rr, dtype=int), np.asarray(cc, dtype=int)] = 1.0
    return gaussian_filter(counts, kernel_px, mode="constant")


def source_target_split(intensity: np.ndarray, footprint: np.ndarray,
                        source_q: float = 0.97, target_q: float = 0.55):
    """Return exploratory upper/lower quantiles of a supplied covariate.

    This is **not** an analog-field definition and cannot alone justify transfer.
    """
    vals = np.asarray(intensity)[footprint]
    hi = np.quantile(vals, source_q)
    lo = np.quantile(vals, target_q)
    source = footprint & (intensity >= hi)
    target = footprint & (intensity <= lo)
    return source, target, float(hi), float(lo)


def classifier_two_sample_proxy(X_s: np.ndarray, X_t: np.ndarray, seed: int = 0,
                                max_iter: int = 120) -> dict:
    """Exploratory held-out domain-classification diagnostic, **not a formal bound**.

    Samples are balanced to equal n. The random train/test split below assumes exchangeable rows;
    that assumption is usually violated by raster pixels. Use grouped/spatial splits or independent
    field-level samples before interpreting this as an estimate of domain divergence. Also, the
    fitted domain-discriminator class need not equal the target model's HΔH class.
    """
    n = min(len(X_s), len(X_t))
    rng = np.random.default_rng(seed)
    si = rng.choice(len(X_s), n, replace=False)
    ti = rng.choice(len(X_t), n, replace=False)
    X = np.vstack([X_s[si], X_t[ti]]).astype(np.float32)
    y = np.concatenate([np.zeros(n, np.uint8), np.ones(n, np.uint8)])
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=seed, stratify=y)
    clf = HistGradientBoostingClassifier(max_iter=max_iter, learning_rate=0.1,
                                         max_leaf_nodes=31, l2_regularization=1.0,
                                         random_state=seed)
    clf.fit(Xtr, ytr)
    p = clf.predict_proba(Xte)[:, 1]
    auc = float(roc_auc_score(yte, p))
    pred = (p >= 0.5).astype(np.uint8)
    error = float((pred != yte).mean())
    d_proxy = 2.0 * (1.0 - 2.0 * min(error, 1.0 - error))
    return {"n_per_domain": int(n), "balanced_error": error, "roc_auc": auc,
            "d_proxy_not_formal_hdh": float(max(d_proxy, 0.0)),
            "interpretation": "exploratory only; iid rows and matched hypothesis class not established"}


def ben_david_theorem2_bound(eps_source: float, d_hat_hdh: float, lambda_joint: float,
                             vc_dim: int, n_unlabeled_per_domain: int,
                             delta: float = 0.05) -> dict:
    """Compute the paper's finite-sample Theorem-2 RHS for supplied valid inputs.

    This function does not estimate any input. In particular, a user must supply a defensible
    HΔH empirical divergence, a joint-error upper bound, a target/source error and the effective
    hypothesis-class VC dimension. With any of those unknown, this is not a usable numerical bound.
    """
    if not (0 <= eps_source <= 1 and 0 <= lambda_joint <= 2):
        raise ValueError("source error and joint error are outside their probability ranges")
    if not (0 <= d_hat_hdh <= 2):
        raise ValueError("empirical HΔH divergence must lie in [0,2]")
    if vc_dim <= 0 or n_unlabeled_per_domain <= 0 or not (0 < delta < 1):
        raise ValueError("vc_dim, sample size, and delta must be positive and in range")
    m = float(n_unlabeled_per_domain)
    complexity = 4.0 * np.sqrt((2.0 * vc_dim * np.log(2.0 * m) + np.log(2.0 / delta)) / m)
    rhs = float(eps_source + 0.5 * d_hat_hdh + complexity + lambda_joint)
    return {"epsilon_target_upper_bound": rhs, "epsilon_source": float(eps_source),
            "half_hdh": 0.5 * float(d_hat_hdh), "finite_sample_complexity": float(complexity),
            "lambda_joint": float(lambda_joint), "vc_dim": int(vc_dim),
            "n_unlabeled_per_domain": int(n_unlabeled_per_domain), "delta": float(delta)}


def catalogue_prevalence_report(source: np.ndarray, target: np.ndarray,
                                labels: np.ndarray) -> dict:
    """Descriptive label prevalence only; it is not a measure of catalogue completeness."""
    def rate(mask):
        return float((labels & mask).sum() / max(int(mask.sum()), 1))
    return {"source_cells": int(source.sum()), "target_cells": int(target.sum()),
            "source_fault_prevalence": rate(source), "target_fault_prevalence": rate(target),
            "warning": "labels are an incomplete catalogue; prevalence differences cannot by themselves measure completeness"}
