"""GEMSDOE33 candidate builders (all label-free at construction time).

Candidates are {0,1} float32 arrays on the canonical grid:
  C0  h27-4-r1-solo                scored 0.2708 (control)
  C1  C0 + H38-1 corroborated dots heat-flow-residual x SI-0 Euler clusters
  C2  C0 + stepover relay-bridge dots (distinct-FID tip pairs, gated)
  C3  rung-3.0 Poisson re-pack of the C0 dot set
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

from .grid import data_dir, load_catalogue, load_raster, load_template

REPO_ROOT = Path(__file__).resolve().parents[2]


def load_dot_array(path: Path) -> np.ndarray:
    arr, _ = load_raster(path)
    out = np.where(np.isfinite(arr), arr, 0.0)
    return (out > 0.5).astype(np.float32)


def c0_control() -> np.ndarray:
    """Scored 0.2708 control. Local artifact first; fall back to the restored mirror."""
    local = REPO_ROOT / "data" / "artifacts" / "h27-4-r1-solo-d2-8-8acb75e1f2cc-nan.tif"
    mirror = data_dir() / "models" / "h27_4_r1_solo_nan.tif"
    return load_dot_array(local if local.is_file() else mirror)


def h19_5_ridge() -> np.ndarray:
    """H19-5 ridge emission mask. The emission is defined on value > 0
    (121,131 px per the GEMSDOE28 inversion), not > 0.5."""
    arr, _ = load_raster(data_dir() / "models" / "h19_5_nan.tif")
    return (np.where(np.isfinite(arr), arr, 0.0) > 0).astype(np.float32)


def c1_h38_corroborated(base: np.ndarray | None = None, max_ridge_dist_px: float = 3.0,
                        min_existing_dist_px: float = 1.5) -> tuple[np.ndarray, dict]:
    """Add H38-1 corroborated Euler-cluster dots (GEMSDOE28 evidence file).

    Corroboration per GEMSDOE28 H38-1: SI=0 Euler depth-coherent cluster
    aligned within 300 m of the 1-px detector ridge and co-located with a
    conductive heat-flow residual >= 50 mW/m^2 (DeAngelo et al. 2022). The
    cluster list was published in GEMSDOE28 ``evidence/h38_1_candidate_clusters.csv``;
    we snap each cluster to the grid, require <= 300 m to the H19-5 ridge
    (value > 0 emission), and enforce >= 150 m from any existing dot and
    not on the catalogue.
    """
    import csv

    if base is None:
        base = c0_control()
    catalogue = load_catalogue()  # noqa: F841 (used below via d_cat)
    ridge = h19_5_ridge() > 0
    d_ridge = distance_transform_edt(~ridge)
    existing = base > 0
    d_existing = distance_transform_edt(~existing) if existing.any() else np.full(base.shape, np.inf)
    d_cat = distance_transform_edt(~catalogue) if catalogue.any() else np.full(base.shape, np.inf)

    out = base.copy()
    csv_path = REPO_ROOT / "reference" / "gems28" / "h38_1_candidate_clusters.csv"
    added, skipped = [], {"off_grid": 0, "far_from_ridge": 0, "too_close": 0, "on_catalogue": 0}
    with open(csv_path) as fh:
        for row in csv.DictReader(fh):
            r, c = int(round(float(row["row"]))), int(round(float(row["col"])))
            if not (0 <= r < out.shape[0] and 0 <= c < out.shape[1]):
                skipped["off_grid"] += 1
                continue
            if d_ridge[r, c] > max_ridge_dist_px:
                skipped["far_from_ridge"] += 1
                continue
            if d_existing[r, c] < min_existing_dist_px or d_cat[r, c] < 1.0:
                skipped["too_close" if d_existing[r, c] < min_existing_dist_px else "on_catalogue"] += 1
                continue
            out[r, c] = 1.0
            added.append({"cluster_id": int(row["cluster_id"]), "row": r, "col": c,
                          "median_depth_m": float(row["median_depth_m"])})
    report = {"candidate": "C1_h38_corroborated", "added": len(added), "skipped": skipped,
              "added_clusters": added}
    return out, report


def _qfaults_tip_segments() -> list[dict]:
    """INGENIOUS Quaternary fault polylines from a pinned community mirror of
    the GDR #1391 compilation, NAD83 lon/lat -> EPSG:32611, clipped to the
    competition footprint with a 3 km margin.

    Note IR-QFAULTS-01: the GEMSDOE24 mirror ``qfaults_v2_in_footprint.json``
    carries geometry in a non-invertible shifted frame and is NOT used; the
    shapefile's .prj is parsed as GCS_North_American_1983. A 42.5% sample-vertex
    proximity check against the supplied catalogue is only a geometry
    diagnostic, not validation of every trace or of target-label equivalence.
    The mirror hashes authenticate fetched bytes, not the source provenance.
    """
    import shapefile
    from rasterio.warp import transform as warp_transform

    shp_path = (data_dir() / "external" / "faults_quaternary_INGENIOUS_regional_data" /
                "faults_quaternary_regional.shp")
    with rasterio.open(data_dir() / "core" / "sample_submission.tif") as ds:
        b = ds.bounds
        transform = ds.transform
    margin = 3000.0
    lonlat_corners = warp_transform(
        "EPSG:32611", "EPSG:4326",
        [b.left - margin, b.right + margin, b.left - margin, b.right + margin],
        [b.bottom - margin, b.bottom - margin, b.top + margin, b.top + margin])
    lon_min = min(lonlat_corners[0]); lon_max = max(lonlat_corners[0])
    lat_min = min(lonlat_corners[1]); lat_max = max(lonlat_corners[1])

    sf = shapefile.Reader(str(shp_path))
    segs = []
    # The source NUM field is often alphanumeric (e.g. "829a"), so casting
    # it to int and falling back to Python's randomized hash(name) made the
    # feature IDs unstable and allowed hash collisions to merge fault systems.
    # Use stable, collision-free integer IDs keyed by the original identity.
    fid_by_identity: dict[tuple[str, str], int] = {}
    for sr in sf.iterShapeRecords():
        a = sr.record
        try:
            name = str(a["NAME"]).strip()
        except Exception:
            name = ""
        try:
            num = str(a["NUM"]).strip()
        except Exception:
            num = ""
        identity = ("num", num) if num else ("name", name)
        if identity not in fid_by_identity:
            fid_by_identity[identity] = len(fid_by_identity)
        fid = fid_by_identity[identity]
        bbox = sr.shape.bbox  # [xmin, ymin, xmax, ymax] in lon/lat
        if bbox[2] < lon_min or bbox[0] > lon_max or bbox[3] < lat_min or bbox[1] > lat_max:
            continue
        for part_idx in range(len(sr.shape.parts)):
            start = sr.shape.parts[part_idx]
            end = sr.shape.parts[part_idx + 1] if part_idx + 1 < len(sr.shape.parts) else len(sr.shape.points)
            pts_ll = np.asarray(sr.shape.points[start:end], dtype=float)
            if len(pts_ll) < 2:
                continue
            E, N = warp_transform("EPSG:4326", "EPSG:32611", pts_ll[:, 0].tolist(), pts_ll[:, 1].tolist())
            pts = np.column_stack([E, N])
            segs.append({"fid": fid, "name": name, "pts": pts})
    return segs


def c2_stepover_bridges(base: np.ndarray | None = None, d_min_m: float = 300.0, d_max_m: float = 2500.0,
                        strike_tol_deg: float = 30.0, dot_spacing_px: float = 2.83) -> tuple[np.ndarray, dict]:
    """Candidate relay-bridge dots between interacting tips of DISTINCT fault polylines.

    Faulds & Hinz (2015, OSTI 1724082) report step-overs/relay ramps among
    favorable regional geothermal settings; this motivates, but does not verify,
    the target-domain bridge hypothesis. This is deliberately different from
    GEMSDOE27's failed T-v2 rule, which filled gaps inside the same polyline
    (230/345 links were same-FID compiler artifacts). Here only distinct-FID
    tip pairs with near-parallel strikes and close tip approach qualify, and
    the bridge is gated by the potential-field edge layer
    (iso_grav_anom_hg >= in-footprint 80th percentile within 200 m).
    """
    import rasterio

    if base is None:
        base = c0_control()
    catalogue = load_catalogue()
    footprint, _ = load_template()
    segs = _qfaults_tip_segments()

    # gravity horizontal gradient gate
    with rasterio.open(data_dir() / "core" / "training_features.tif") as ds:
        ghg = ds.read(18)  # band 18: iso_grav_anom_hg
    finite = np.isfinite(ghg) & footprint
    thr = np.quantile(ghg[finite], 0.80)
    grav_edge = (ghg >= thr) & footprint
    d_grav = distance_transform_edt(~grav_edge)

    # tip list: both ends of every segment, with local strike at the tip
    tips = []
    for seg in segs:
        pts = seg["pts"]
        for which in ("start", "end"):
            i = 0 if which == "start" else len(pts) - 1
            j = 1 if which == "start" else len(pts) - 2
            v = pts[j] - pts[i]
            n = np.hypot(*v)
            if n < 1e-6:
                continue
            ang = (np.degrees(np.arctan2(v[1], v[0])) + 180.0) % 180.0
            tips.append({"fid": seg["fid"], "xy": pts[i], "ang": ang})

    existing = base > 0
    d_existing = distance_transform_edt(~existing) if existing.any() else np.full(base.shape, np.inf)
    d_cat = distance_transform_edt(~catalogue) if catalogue.any() else np.full(base.shape, np.inf)

    with rasterio.open(data_dir() / "core" / "sample_submission.tif") as ds:
        transform = ds.transform
    out = base.copy()
    added, pairs = 0, 0

    from scipy.spatial import cKDTree

    if tips:
        xy = np.array([t["xy"] for t in tips])
        ang = np.array([t["ang"] for t in tips])
        fid = np.array([t["fid"] for t in tips])
        tree = cKDTree(xy)
        seen_pairs = set()
        for i, idx_list in enumerate(tree.query_ball_point(xy, r=d_max_m)):
            for j in idx_list:
                if j <= i or fid[i] == fid[j]:
                    continue  # distinct structures only (T-v2 lesson)
                key = (min(i, j), max(i, j))
                if key in seen_pairs:
                    continue
                seen_pairs.add(key)
                gap = float(np.hypot(*(xy[j] - xy[i])))
                if gap < d_min_m:
                    continue
                d_ang = abs(ang[i] - ang[j])
                d_ang = min(d_ang, 180.0 - d_ang)
                if d_ang > strike_tol_deg:
                    continue
                n_dots = max(1, int(gap / (dot_spacing_px * 100.0)) - 1)
                for k in range(1, n_dots + 1):
                    p = xy[i] + (xy[j] - xy[i]) * (k / (n_dots + 1))
                    col = int(round((p[0] - transform.c) / transform.a))
                    row = int(round((transform.f - p[1]) / -transform.e))
                    if not (0 <= row < out.shape[0] and 0 <= col < out.shape[1]):
                        continue
                    if not footprint[row, col]:
                        continue
                    if d_cat[row, col] < 2.0 or d_existing[row, col] < 2.5:
                        continue  # >=200 m off catalogue, >=250 m from existing dots
                    if d_grav[row, col] > 2.0:
                        continue  # must sit within 200 m of a strong gravity edge
                    if out[row, col] == 0:
                        out[row, col] = 1.0
                        added += 1
                pairs += 1
    report = {"candidate": "C2_stepover_bridges", "qualifying_tip_pairs": pairs, "added_dots": added}
    return out, report


def c3_rung30_repack(base: np.ndarray | None = None, rung_px: float = 3.0) -> tuple[np.ndarray, dict]:
    """Greedy Poisson-disk re-pack of the base dot set at a coarser rung.

    Raster-scan order (content-blind, same convention as the GEMSDOE28 H36-1
    re-pack of the H19-5 surface); keeps dots whose nearest kept neighbour is
    >= rung_px. This reduces dot count while preserving 1-D crest coverage
    under the 300 m kernel.
    """
    if base is None:
        base = c0_control()
    ys, xs = np.nonzero(base > 0)
    kept = np.zeros_like(base, bool)
    kept_idx = []
    min_d2 = rung_px * rung_px
    for y, x in zip(ys, xs):
        y0, y1 = max(0, y - 3), min(base.shape[0], y + 4)
        x0, x1 = max(0, x - 3), min(base.shape[1], x + 4)
        patch = kept[y0:y1, x0:x1]
        if patch.any():
            yy, xx = np.nonzero(patch)
            d2 = ((yy + y0 - y) ** 2 + (xx + x0 - x) ** 2).min()
            if d2 < min_d2:
                continue
        kept[y, x] = True
        kept_idx.append((int(y), int(x)))
    report = {"candidate": "C3_rung30_repack", "input_dots": int(len(ys)), "kept_dots": int(kept.sum())}
    return kept.astype(np.float32), report
