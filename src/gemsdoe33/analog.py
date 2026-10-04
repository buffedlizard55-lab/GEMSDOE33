"""Named analog-field transfer on shared GeoDAWN layers.

Source domains are Dixie Valley, Brady Hot Springs and Desert Peak. Field masks are
built from unique INGENIOUS well/spring cells whose names match those fields
(owner-mirror of GDR 1391) unioned with a buffer around published plant/area
coordinates. Source labels remain the public USGS/INGENIOUS catalogue *inside*
those named fields — they are not independent BRIDGE GIS traces (GDR 1682 / 207
payloads could not be staged; TLS to gdr.openei.org failed).

This is covariate-shift adaptation from densely sampled geothermal fields onto
the rest of the GeoDAWN footprint. It is **not** a Ben-David et al. (2010)
target-error bound: lambda (joint-label error), a matched HΔH class, and
independent analog-only labels are unavailable. Exploratory domain-discriminator
AUC is recorded as a diagnostic only.

Official coordinate sources (fetched 2026-10-04):
- Dixie Valley geothermal area: OpenEI 39°58'3.59\" N, 117°51'18.27\" W
  https://openei.org/wiki/Dixie_Valley_Geothermal_Area (page was under
  maintenance when re-fetched; coordinates from the indexed OpenEI record).
- Brady Hot Springs: USGS MRDS 39.7866 N, 119.01319 W
  https://mrdata.usgs.gov/mrds/show-mrds.php?dep_id=10221999
- Desert Peak II facility: OpenEI 39.753855 N, 118.953781 W
  https://openei.org/wiki/Desert_Peak_II_Geothermal_Facility
"""
from __future__ import annotations

import csv
from dataclasses import dataclass

import numpy as np
from scipy.ndimage import binary_dilation, distance_transform_edt, label
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

from . import emission, grid

WELL_BUFFER_PX = 120  # 12 km at 100 m
CENTROID_BUFFER_PX = 150  # 15 km at 100 m
NEGATIVE_CLEARANCE_PX = 2.0
PRUNE_PX = 1.0
MIN_DIST_PX = 2.8
MAX_DOTS = 44090
FEATURE_KEYS = (
    "tmi_hg", "tmi_vg", "iso_grav_anom_hg", "iso_grav_anom_slope",
    "det_elev_slope", "det_elev", "depth_to_base_surf", "geod_dilaterate",
    "geod_shearrate", "geod_2ndinv", "cond_surf", "mag_anom", "rtp",
)
LIDAR_BANDS = ("ex_max", "step_max", "lapneg_max", "downface_max", "upface_max", "coh100")

FIELD_SPECS = (
    {
        "id": "dixie_valley",
        "name_substrings": ("dixie",),
        "lon": -117.855075,
        "lat": 39.967664,
        "source": "https://openei.org/wiki/Dixie_Valley_Geothermal_Area",
        "source_note": "OpenEI Dixie Valley Geothermal Area; 39°58'3.59\" N, 117°51'18.27\" W",
    },
    {
        "id": "brady",
        "name_substrings": ("brady",),
        "lon": -119.01319,
        "lat": 39.7866,
        "source": "https://mrdata.usgs.gov/mrds/show-mrds.php?dep_id=10221999",
        "source_note": "USGS MRDS Brady Hot Springs dep_id 10221999; 39.7866 N, 119.01319 W",
    },
    {
        "id": "desert_peak",
        "name_substrings": ("desert peak",),
        "lon": -118.953781,
        "lat": 39.753855,
        "source": "https://openei.org/wiki/Desert_Peak_II_Geothermal_Facility",
        "source_note": "OpenEI Desert Peak II Geothermal Facility; 39.753855 N, 118.953781 W",
    },
)


@dataclass(frozen=True)
class AnalogMasks:
    analog: np.ndarray
    per_field: dict
    well_cells: dict
    centroid_rowcol: dict


def _unique_well_cells(footprint: np.ndarray) -> dict[str, set[tuple[int, int]]]:
    h, w = footprint.shape
    cells = {spec["id"]: set() for spec in FIELD_SPECS}
    path = grid.DATA / "gdr_wellspring_in_footprint.csv"
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            name = (row.get("name") or "").lower()
            try:
                rr, cc = int(row["row"]), int(row["col"])
            except (KeyError, TypeError, ValueError):
                continue
            if not (0 <= rr < h and 0 <= cc < w and footprint[rr, cc]):
                continue
            for spec in FIELD_SPECS:
                if any(s in name for s in spec["name_substrings"]):
                    cells[spec["id"]].add((rr, cc))
    return cells


def _centroid_rowcol() -> dict[str, tuple[float, float]]:
    from rasterio.warp import transform as warp_transform

    out = {}
    with __import__("rasterio").open(grid.DATA / grid.SAMPLE_SUBMISSION) as src:
        for spec in FIELD_SPECS:
            xs, ys = warp_transform("EPSG:4326", src.crs, [spec["lon"]], [spec["lat"]])
            col, row = ~src.transform * (xs[0], ys[0])
            out[spec["id"]] = (float(row), float(col))
    return out


def build_analog_masks(footprint: np.ndarray | None = None) -> AnalogMasks:
    """Named-field source mask: well-name buffer ∪ official-centroid buffer."""
    footprint = grid.template_footprint() if footprint is None else np.asarray(footprint, bool)
    wells = _unique_well_cells(footprint)
    centroids = _centroid_rowcol()
    h, w = footprint.shape
    analog = np.zeros((h, w), dtype=bool)
    per_field = {}
    for spec in FIELD_SPECS:
        fid = spec["id"]
        seed = np.zeros((h, w), dtype=bool)
        for r, c in wells[fid]:
            seed[r, c] = True
        rr, cc = centroids[fid]
        r0, c0 = int(round(rr)), int(round(cc))
        if 0 <= r0 < h and 0 <= c0 < w:
            seed[r0, c0] = True
        field = np.zeros((h, w), dtype=bool)
        if seed.any():
            d_well = distance_transform_edt(~seed)
            # well seeds use WELL_BUFFER; the official centroid is always in `seed`
            # so the same distance field covers both. Apply the larger centroid
            # radius only near the centroid, well radius elsewhere.
            d_cent = np.full((h, w), np.inf, dtype=np.float64)
            if 0 <= r0 < h and 0 <= c0 < w:
                yy, xx = np.ogrid[:h, :w]
                d_cent = np.hypot(yy - rr, xx - cc)
            field = ((d_well <= WELL_BUFFER_PX) | (d_cent <= CENTROID_BUFFER_PX)) & footprint
        per_field[fid] = field
        analog |= field
    return AnalogMasks(analog=analog, per_field=per_field, well_cells=wells,
                       centroid_rowcol=centroids)


def analog_inventory(masks: AnalogMasks, catalogue: np.ndarray, footprint: np.ndarray) -> dict:
    rows = []
    for spec in FIELD_SPECS:
        fid = spec["id"]
        field = masks.per_field[fid]
        rr, cc = masks.centroid_rowcol[fid]
        rows.append({
            "id": fid,
            "n_named_well_cells": len(masks.well_cells[fid]),
            "centroid_row": rr,
            "centroid_col": cc,
            "centroid_in_footprint": bool(0 <= rr < footprint.shape[0] and 0 <= cc < footprint.shape[1]
                                          and footprint[int(round(rr)), int(round(cc))]),
            "field_cells": int(field.sum()),
            "catalogue_in_field": int((catalogue & field).sum()),
            "official_source": spec["source"],
            "official_note": spec["source_note"],
        })
    return {
        "union_cells": int(masks.analog.sum()),
        "union_catalogue": int((catalogue & masks.analog).sum()),
        "fields": rows,
        "well_buffer_px": WELL_BUFFER_PX,
        "centroid_buffer_px": CENTROID_BUFFER_PX,
        "label_policy": "public USGS/INGENIOUS catalogue inside named analog fields; not independent BRIDGE GIS",
    }


def load_feature_stack(footprint: np.ndarray) -> tuple[np.ndarray, list[str]]:
    """(n_feat, H, W) float32 stack; NaNs filled inside the footprint."""
    bands = []
    names = []
    for key in FEATURE_KEYS:
        arr = np.array(grid.load_band(key), dtype=np.float32, copy=True)
        arr[~footprint] = np.nan
        bands.append(_fill(arr, footprint))
        names.append(key)
    lidar_path = grid.DATA / "lidar_scarp_features_u8.tif"
    if lidar_path.is_file():
        import rasterio
        with rasterio.open(lidar_path) as src:
            desc = list(src.descriptions)
            for name in LIDAR_BANDS:
                if name in desc:
                    arr = src.read(desc.index(name) + 1).astype(np.float32)
                    arr[~footprint] = 0.0
                    bands.append(arr)
                    names.append(f"lidar_{name}")
    stack = np.stack(bands, axis=0)
    return stack, names


def _fill(arr: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    out = arr.copy()
    bad = (~np.isfinite(out)) & footprint
    if bad.any():
        idx = distance_transform_edt(~np.isfinite(out), return_distances=False, return_indices=True)
        out[bad] = arr[tuple(idx[:, bad])]
    out[~np.isfinite(out)] = 0.0
    return out.astype(np.float32)


def _sample_xy(mask: np.ndarray, n: int, rng: np.random.Generator) -> np.ndarray:
    ys, xs = np.nonzero(mask)
    if ys.size == 0:
        return np.zeros((0, 2), dtype=int)
    if ys.size <= n:
        return np.stack([ys, xs], axis=1)
    pick = rng.choice(ys.size, size=n, replace=False)
    return np.stack([ys[pick], xs[pick]], axis=1)


def extract_xy(stack: np.ndarray, coords: np.ndarray) -> np.ndarray:
    if coords.size == 0:
        return np.zeros((0, stack.shape[0]), dtype=np.float32)
    return np.stack([stack[i][coords[:, 0], coords[:, 1]] for i in range(stack.shape[0])], axis=1)


def fit_analog_classifier(stack: np.ndarray, analog: np.ndarray, labels: np.ndarray,
                          footprint: np.ndarray, rng: np.random.Generator,
                          seed: int = 33) -> dict:
    """Train on analog-field catalogue vs analog background. labels must be fold-visible."""
    d_lab = distance_transform_edt(~labels) if labels.any() else np.full(labels.shape, np.inf)
    pos = analog & labels & footprint
    neg = analog & footprint & ~labels & (d_lab > NEGATIVE_CLEARANCE_PX)
    pos_xy = np.stack(np.nonzero(pos), axis=1)
    n_pos = int(len(pos_xy))
    neg_xy = _sample_xy(neg, max(n_pos, 1), rng)
    if n_pos < 50 or len(neg_xy) < 50:
        raise RuntimeError(f"insufficient analog training mass: pos={n_pos} neg={len(neg_xy)}")
    X = np.vstack([extract_xy(stack, pos_xy), extract_xy(stack, neg_xy)]).astype(np.float32)
    y = np.concatenate([np.ones(n_pos, np.uint8), np.zeros(len(neg_xy), np.uint8)])
    clf = HistGradientBoostingClassifier(
        max_iter=140, learning_rate=0.08, max_leaf_nodes=31,
        l2_regularization=1.0, random_state=seed,
    )
    clf.fit(X, y)
    p = clf.predict_proba(X)[:, 1]
    auc = float(roc_auc_score(y, p))
    return {"clf": clf, "n_pos": n_pos, "n_neg": int(len(neg_xy)), "train_auc_in_sample": auc}


def predict_chunks(clf, stack: np.ndarray, footprint: np.ndarray, chunk: int = 400_000) -> np.ndarray:
    h, w = footprint.shape
    out = np.zeros((h, w), dtype=np.float32)
    ys, xs = np.nonzero(footprint)
    n = ys.size
    for start in range(0, n, chunk):
        sl = slice(start, min(start + chunk, n))
        coords = np.stack([ys[sl], xs[sl]], axis=1)
        X = extract_xy(stack, coords)
        out[ys[sl], xs[sl]] = clf.predict_proba(X)[:, 1].astype(np.float32)
    return out


def emit_from_score(score: np.ndarray, footprint: np.ndarray, known: np.ndarray,
                    max_dots: int = MAX_DOTS, min_dist: float = MIN_DIST_PX,
                    prune_px: float = PRUNE_PX) -> np.ndarray:
    """Off-catalogue analog-score ridges, Poisson-thinned. Unique vs D2.8 geometry."""
    d_known = distance_transform_edt(~known) if known.any() else np.full(known.shape, np.inf)
    domain = footprint & (d_known > prune_px) & np.isfinite(score)
    # Keep the analog-score ridge AND a high-score tail so emission is not empty
    # if NMS is overly sparse.
    nms = emission.ridge_nms(np.where(domain, score, np.nan), width=1) & domain
    vals = score[domain]
    if vals.size == 0:
        return np.zeros(score.shape, dtype=bool)
    thr = float(np.quantile(vals, 0.985))
    high = domain & (score >= thr)
    cand = nms | high
    return emission.dot_thin(cand, min_dist, priority=score, max_dots=max_dots)


def domain_discriminator_proxy(stack: np.ndarray, analog: np.ndarray, footprint: np.ndarray,
                               rng: np.random.Generator, n_each: int = 40000, seed: int = 33) -> dict:
    """Exploratory spatial-block two-sample diagnostic. Not an HΔH bound."""
    source = analog & footprint
    target = footprint & ~analog
    src_xy = _sample_xy(source, n_each, rng)
    tgt_xy = _sample_xy(target, n_each, rng)
    X = np.vstack([extract_xy(stack, src_xy), extract_xy(stack, tgt_xy)]).astype(np.float32)
    y = np.concatenate([np.zeros(len(src_xy), np.uint8), np.ones(len(tgt_xy), np.uint8)])
    # 20 km spatial blocks; train even, test odd — avoids iid pixel split.
    block = ((src_xy[:, 0] // 200) + (src_xy[:, 1] // 200)).astype(int)
    block_t = ((tgt_xy[:, 0] // 200) + (tgt_xy[:, 1] // 200)).astype(int)
    blocks = np.concatenate([block, block_t])
    even = (blocks % 2) == 0
    if even.sum() < 100 or (~even).sum() < 100:
        return {"status": "BLOCKED_NOT_ESTIMATED", "reason": "spatial blocks too small"}
    clf = HistGradientBoostingClassifier(max_iter=80, max_leaf_nodes=15, random_state=seed)
    clf.fit(X[even], y[even])
    p = clf.predict_proba(X[~even])[:, 1]
    auc = float(roc_auc_score(y[~even], p))
    pred = (p >= 0.5).astype(np.uint8)
    err = float((pred != y[~even]).mean())
    return {
        "status": "EXPLORATORY_NOT_A_BOUND",
        "n_per_domain": n_each,
        "spatial_block_px": 200,
        "held_out_block_auc": auc,
        "held_out_block_error": err,
        "interpretation": (
            "Classifier two-sample AUC on 20 km even/odd blocks. This is not "
            "Ben-David d_HΔH, does not estimate lambda, and does not license transfer."
        ),
    }


def catalogue_systems(catalogue: np.ndarray, buffer_px: int = 6) -> np.ndarray:
    if buffer_px > 0:
        grown = binary_dilation(catalogue, structure=np.ones((2 * buffer_px + 1, 2 * buffer_px + 1), bool))
    else:
        grown = catalogue
    lab, _n = label(grown)
    return np.where(catalogue, lab, 0)


def fold_masks(system_ids: np.ndarray, n_folds: int = 4) -> list[np.ndarray]:
    systems = np.unique(system_ids[system_ids > 0])
    centroids = np.array([np.argwhere(system_ids == sid).mean(axis=0) for sid in systems])
    rows, cols = centroids[:, 0], centroids[:, 1]
    q = ((rows > np.median(rows)).astype(int) * 2 + (cols > np.median(cols)).astype(int))
    masks = []
    for f in range(n_folds):
        sel = set(systems[q == f].tolist())
        masks.append(np.isin(system_ids, list(sel)))
    return masks


def rebuild_c0(known: np.ndarray, ridge: np.ndarray) -> np.ndarray:
    """H27-4 reconstruction: Poisson d=2.8 of H19-5 off known, then 1-px catalogue-flank prune."""
    known = np.asarray(known, bool)
    ridge = np.asarray(ridge, bool)
    base = emission.dot_thin(ridge & ~known, MIN_DIST_PX)
    d_known = distance_transform_edt(~known) if known.any() else np.full(known.shape, np.inf)
    return base & (d_known > PRUNE_PX)


def h19_ridge() -> np.ndarray:
    arr, _ = grid.read_raster("h19_5_nan.tif")
    return np.where(np.isfinite(arr), arr, 0.0) > 0


def d28_mask(footprint: np.ndarray) -> np.ndarray:
    arr, _ = grid.read_raster("dotted_h19_5_d2_8_nan.tif")
    return (np.where(np.isfinite(arr), arr, 0.0) > 0) & footprint


def sgmc_off_catalogue(catalogue: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    arr, _ = grid.read_raster("derived_sgmc_faults_100m_u8.tif")
    sg = arr > 0
    d_cat = distance_transform_edt(~catalogue) if catalogue.any() else np.full(catalogue.shape, np.inf)
    return sg & footprint & (d_cat >= 3.0)
