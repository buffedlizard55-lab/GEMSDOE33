"""A33-L1 target-aligned, field-balanced analog-transfer model.

All transforms are label-free except the explicit classifier fits. Callers must
supply a fold-visible catalogue and a spatially purged training mask.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier

from . import analog
from .paths import CACHE_FEATURES

FEATURE_NAMES = (
    "tmi_hg",
    "tmi_vg",
    "iso_grav_anom_hg",
    "iso_grav_anom_slope",
    "det_elev_slope",
    "rtp_gms2",
    "iso_grav_anom_gms2",
    "depth_to_base_surf_gms2",
    "cond_surf_gms2",
    "rtp_coh",
    "iso_grav_anom_coh",
    "ext_TMI_up150_gm2",
)
QUANTILE_KNOTS = 257
SOURCE_DOMAIN_SAMPLE = 100_000
SOURCE_POSITIVE_CAP = 8_000
REGIONAL_POSITIVE_CAP = 40_000
NEGATIVE_CLEARANCE_PX = 3.0
FUSION_TARGET_WEIGHT = 0.80
FUSION_ANALOG_WEIGHT = 0.20

HGB_CONFIG = {
    "max_iter": 140,
    "learning_rate": 0.08,
    "max_leaf_nodes": 31,
    "l2_regularization": 1.0,
    "early_stopping": False,
}


@dataclass
class Expert:
    model: HistGradientBoostingClassifier
    report: dict


def load_feature_arrays() -> dict[str, np.ndarray]:
    arrays: dict[str, np.ndarray] = {}
    for name in FEATURE_NAMES:
        path = CACHE_FEATURES / f"{name}.npy"
        if not path.is_file():
            raise FileNotFoundError(
                f"Missing cached feature {path}; run scripts/prepare_data.py --skip-detector"
            )
        arr = np.load(path, mmap_mode="r")
        if arr.shape != (3730, 3292):
            raise ValueError(f"Feature grid mismatch: {name} {arr.shape}")
        arrays[name] = arr
    return arrays


def feature_source_hashes() -> dict[str, str]:
    rows = {}
    for name in FEATURE_NAMES:
        path = CACHE_FEATURES / f"{name}.npy"
        h = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1 << 20), b""):
                h.update(chunk)
        rows[name] = h.hexdigest()
    return rows


def _matrix(arrays: dict[str, np.ndarray], flat_ids: np.ndarray) -> np.ndarray:
    ids = np.asarray(flat_ids, dtype=np.int64)
    out = np.empty((ids.size, len(FEATURE_NAMES)), dtype=np.float32)
    for j, name in enumerate(FEATURE_NAMES):
        values = np.asarray(arrays[name]).ravel()[ids]
        out[:, j] = np.nan_to_num(values, nan=0.0, posinf=0.0, neginf=0.0)
    return out


def _sample_ids(mask: np.ndarray, cap: int, rng: np.random.Generator) -> np.ndarray:
    ids = np.flatnonzero(mask)
    if ids.size > cap:
        ids = np.sort(rng.choice(ids, size=cap, replace=False))
    return ids


def _quantiles(
    arrays: dict[str, np.ndarray],
    domain: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    ids = _sample_ids(domain, SOURCE_DOMAIN_SAMPLE, rng)
    if ids.size < 100:
        raise ValueError(f"Quantile domain too small: {ids.size}")
    x = _matrix(arrays, ids)
    q = np.linspace(0.0, 1.0, QUANTILE_KNOTS)
    return np.quantile(x, q, axis=0).astype(np.float32)


def _map_quantiles(x: np.ndarray, source_q: np.ndarray, target_q: np.ndarray) -> np.ndarray:
    mapped = np.empty_like(x, dtype=np.float32)
    for j in range(x.shape[1]):
        source, first = np.unique(source_q[:, j], return_index=True)
        target = target_q[first, j]
        if source.size == 1:
            mapped[:, j] = target[0]
        else:
            mapped[:, j] = np.interp(x[:, j], source, target).astype(np.float32)
    return mapped


def _new_model(seed: int) -> HistGradientBoostingClassifier:
    return HistGradientBoostingClassifier(**HGB_CONFIG, random_state=seed)


def fit_regional_expert(
    arrays: dict[str, np.ndarray],
    train: np.ndarray,
    visible: np.ndarray,
    distance_to_visible: np.ndarray,
    *,
    seed: int,
) -> Expert:
    rng = np.random.default_rng(seed)
    positives = train & visible
    negatives = train & ~visible & (distance_to_visible > NEGATIVE_CLEARANCE_PX)
    pos_ids = _sample_ids(positives, REGIONAL_POSITIVE_CAP, rng)
    neg_ids = _sample_ids(negatives, pos_ids.size, rng)
    if pos_ids.size < 100 or neg_ids.size < 100:
        raise RuntimeError(
            f"Insufficient regional samples: positives={pos_ids.size}, negatives={neg_ids.size}"
        )
    ids = np.concatenate([pos_ids, neg_ids])
    labels = np.concatenate(
        [np.ones(pos_ids.size, dtype=np.uint8), np.zeros(neg_ids.size, dtype=np.uint8)]
    )
    model = _new_model(seed)
    model.fit(_matrix(arrays, ids), labels)
    return Expert(
        model,
        {
            "kind": "regional_visible_fault_expert",
            "positive_samples": int(pos_ids.size),
            "negative_samples": int(neg_ids.size),
            "training_domain_cells": int(train.sum()),
            "seed": seed,
        },
    )


def fit_raw_analog_expert(
    arrays: dict[str, np.ndarray],
    train: np.ndarray,
    visible: np.ndarray,
    distance_to_visible: np.ndarray,
    masks: analog.AnalogMasks,
    *,
    seed: int,
) -> Expert:
    rng = np.random.default_rng(seed)
    source = masks.analog & train
    positives = source & visible
    negatives = source & ~visible & (distance_to_visible > NEGATIVE_CLEARANCE_PX)
    pos_ids = _sample_ids(positives, SOURCE_POSITIVE_CAP * len(masks.per_field), rng)
    neg_ids = _sample_ids(negatives, pos_ids.size, rng)
    if pos_ids.size < 100 or neg_ids.size < 100:
        raise RuntimeError(
            f"Insufficient raw analog samples: positives={pos_ids.size}, negatives={neg_ids.size}"
        )
    ids = np.concatenate([pos_ids, neg_ids])
    labels = np.concatenate(
        [np.ones(pos_ids.size, dtype=np.uint8), np.zeros(neg_ids.size, dtype=np.uint8)]
    )
    model = _new_model(seed)
    model.fit(_matrix(arrays, ids), labels)
    return Expert(
        model,
        {
            "kind": "raw_pooled_analog_expert_H33F_comparator",
            "positive_samples": int(pos_ids.size),
            "negative_samples": int(neg_ids.size),
            "source_domain_cells": int(source.sum()),
            "seed": seed,
        },
    )


def fit_adapted_analog_expert(
    arrays: dict[str, np.ndarray],
    train: np.ndarray,
    visible: np.ndarray,
    distance_to_visible: np.ndarray,
    masks: analog.AnalogMasks,
    *,
    seed: int,
) -> Expert:
    """Align each source field's feature marginals to the unlabeled target training domain."""
    rng = np.random.default_rng(seed)
    target_domain = train & ~masks.analog
    target_q = _quantiles(arrays, target_domain, rng)
    all_x: list[np.ndarray] = []
    all_y: list[np.ndarray] = []
    groups: list[int] = []
    field_rows = []
    for field_index, (field_id, field_mask) in enumerate(masks.per_field.items()):
        source_domain = train & field_mask
        positives = source_domain & visible
        negatives = source_domain & ~visible & (distance_to_visible > NEGATIVE_CLEARANCE_PX)
        pos_ids = _sample_ids(positives, SOURCE_POSITIVE_CAP, rng)
        neg_ids = _sample_ids(negatives, pos_ids.size, rng)
        if pos_ids.size < 50 or neg_ids.size < 50:
            field_rows.append(
                {
                    "field": field_id,
                    "used": False,
                    "reason": "fewer than 50 positive/negative fold-safe samples",
                    "positive_samples": int(pos_ids.size),
                    "negative_samples": int(neg_ids.size),
                }
            )
            continue
        source_q = _quantiles(arrays, source_domain, rng)
        ids = np.concatenate([pos_ids, neg_ids])
        x = _map_quantiles(_matrix(arrays, ids), source_q, target_q)
        y = np.concatenate(
            [np.ones(pos_ids.size, dtype=np.uint8), np.zeros(neg_ids.size, dtype=np.uint8)]
        )
        all_x.append(x)
        all_y.append(y)
        groups.extend([field_index] * len(y))
        field_rows.append(
            {
                "field": field_id,
                "used": True,
                "source_domain_cells": int(source_domain.sum()),
                "positive_samples": int(pos_ids.size),
                "negative_samples": int(neg_ids.size),
            }
        )
    if len(all_x) < 2:
        raise RuntimeError("A33-L1 requires at least two usable named source fields")
    x = np.vstack(all_x).astype(np.float32)
    y = np.concatenate(all_y)
    group = np.asarray(groups, dtype=np.int16)
    used_groups = np.unique(group)
    # Each source field contributes equal total loss, regardless of catalogue density.
    weights = np.zeros(len(group), dtype=np.float64)
    for value in used_groups:
        select = group == value
        weights[select] = len(group) / (len(used_groups) * int(select.sum()))
    model = _new_model(seed)
    model.fit(x, y, sample_weight=weights)
    return Expert(
        model,
        {
            "kind": "target_CDF_aligned_field_balanced_analog_expert",
            "fields": field_rows,
            "used_fields": int(len(used_groups)),
            "samples": int(len(y)),
            "target_quantile_domain_cells": int(target_domain.sum()),
            "quantile_knots": QUANTILE_KNOTS,
            "quantile_sample_cap": SOURCE_DOMAIN_SAMPLE,
            "field_total_weight_equalized": True,
            "seed": seed,
        },
    )


def predict(
    expert: Expert,
    arrays: dict[str, np.ndarray],
    domain: np.ndarray,
    *,
    chunk: int = 300_000,
) -> np.ndarray:
    out = np.zeros(domain.shape, dtype=np.float32)
    ids = np.flatnonzero(domain)
    for start in range(0, ids.size, chunk):
        batch = ids[start : start + chunk]
        out.ravel()[batch] = expert.model.predict_proba(_matrix(arrays, batch))[:, 1].astype(
            np.float32
        )
    return out


def percentile_surface(score: np.ndarray, domain: np.ndarray) -> np.ndarray:
    """Deterministic 257-knot approximate empirical rank on one prediction domain."""
    values = np.asarray(score, dtype=np.float32)[domain]
    if values.size < 100 or not np.isfinite(values).all():
        raise ValueError("Percentile surface requires >=100 finite domain values")
    q = np.linspace(0.0, 1.0, QUANTILE_KNOTS)
    knots = np.quantile(values, q)
    unique, first = np.unique(knots, return_index=True)
    ranks = q[first]
    out = np.zeros(score.shape, dtype=np.float32)
    if unique.size == 1:
        out[domain] = 0.5
    else:
        out[domain] = np.interp(values, unique, ranks).astype(np.float32)
    return out


def fuse(regional_score: np.ndarray, adapted_score: np.ndarray, domain: np.ndarray) -> np.ndarray:
    regional_rank = percentile_surface(regional_score, domain)
    adapted_rank = percentile_surface(adapted_score, domain)
    out = np.zeros(domain.shape, dtype=np.float32)
    out[domain] = (
        FUSION_TARGET_WEIGHT * regional_rank[domain]
        + FUSION_ANALOG_WEIGHT * adapted_rank[domain]
    )
    return out
