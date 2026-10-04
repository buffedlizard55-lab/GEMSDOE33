"""GEMSDOE33 candidate builders and fold-aware source audits.

Candidates are {0,1} float32 arrays on the canonical grid. Constructors may
use the publicly supplied catalogue as a prediction mask; holdout callers must
pass a fold-visible ``catalogue_mask`` and exclude any source geometry within
the held-out buffer before evaluating spatial generalisation.

  C0  h27-4-r1-solo                owner-mirror research reference; score/file pairing unverified
  C1  C0 + H38-1 corroborated dots heat-flow-residual x SI-0 Euler clusters
  C2  C0 + stepover relay-bridge dots (distinct-FID tip pairs, gated)
  C3  rung-3.0 Poisson re-pack of the C0 dot set
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, distance_transform_edt

from .grid import data_dir, load_catalogue, load_raster, load_template
from .thinning import dot_thin

REPO_ROOT = Path(__file__).resolve().parents[2]


def load_dot_array(path: Path) -> np.ndarray:
    arr, _ = load_raster(path)
    out = np.where(np.isfinite(arr), arr, 0.0)
    return (out > 0.5).astype(np.float32)


def c0_control() -> np.ndarray:
    """H27-4 owner-mirror research reference. Score/file association is unverified."""
    local = REPO_ROOT / "data" / "artifacts" / "h27-4-r1-solo-d2-8-8acb75e1f2cc-nan.tif"
    mirror = data_dir() / "models" / "h27_4_r1_solo_nan.tif"
    return load_dot_array(local if local.is_file() else mirror)


def rebuild_c0_from_known(known: np.ndarray, raw_ridge: np.ndarray | None = None,
                          *, min_dist_px: float = 2.8, prune_px: float = 1.0) -> tuple[np.ndarray, dict]:
    """Rebuild the H27-4 control using only the catalogue mask visible in one fold.

    The legacy H27-4 raster is exactly ``dot_thin(H19-5, 2.8)`` with dots at
    distance <= 1 pixel from the known catalogue removed. Recomputing both
    steps from the fold-visible ``known`` mask prevents the precomputed final
    raster from carrying hidden-fold catalogue geometry into P1.
    """
    known = np.asarray(known, dtype=bool)
    if known.ndim != 2:
        raise ValueError("known must be a 2-D mask")
    raw = h19_5_ridge() if raw_ridge is None else np.asarray(raw_ridge, dtype=bool)
    if raw.shape != known.shape:
        raise ValueError("raw H19-5 ridge and known mask must have the same shape")
    base = dot_thin(raw & ~known, float(min_dist_px))
    d_known = distance_transform_edt(~known) if known.any() else np.full(known.shape, np.inf)
    result = base & (d_known > float(prune_px))
    return result.astype(np.float32), {
        "builder": "dot_thin(H19-5 & ~known, 2.8) & (distance_to_known > 1 px)",
        "min_dist_px": float(min_dist_px),
        "prune_px": float(prune_px),
        "known_pixels": int(known.sum()),
        "h19_5_pixels": int(raw.sum()),
        "dots_before_flank_prune": int(base.sum()),
        "dots_after_flank_prune": int(result.sum()),
        "pruned_dots": int((base & ~result).sum()),
    }


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
    # Use stable, collision-free integer IDs keyed by normalized NUM/NAME; blank
    # identifiers fall back to the stable shapefile record index.
    fid_by_identity: dict[tuple[str, str], int] = {}
    for record_index, sr in enumerate(sf.iterShapeRecords()):
        a = sr.record
        try:
            name = str(a["NAME"]).strip()
        except Exception:
            name = ""
        try:
            num = str(a["NUM"]).strip()
        except Exception:
            num = ""
        if num:
            identity = ("num", num.casefold())
        elif name:
            identity = ("name", name.casefold())
        else:
            # A blank NUM and NAME must not make unrelated unnamed records a
            # single fictitious fault system; retain a stable record identity.
            identity = ("record", str(record_index))
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


def exclude_source_fids_near_mask(segments: list[dict], target_mask: np.ndarray, transform,
                                  *, buffer_px: int = 6, guard_px: int = 1,
                                  sample_step_m: float = 50.0) -> tuple[set[int], dict]:
    """Find source fault systems that overlap a buffered target/holdout mask.

    Each source polyline is sampled at <= ``sample_step_m`` intervals in the
    projected CRS. Any segment entering the Chebyshev buffer is enough to
    exclude its entire fault-system ID from a fold's C2 candidate generation.
    ``guard_px`` adds a rasterization guard beyond the fold's label buffer.
    """
    target = np.asarray(target_mask, dtype=bool)
    if target.ndim != 2:
        raise ValueError("target_mask must be a 2-D array")
    if buffer_px < 0 or guard_px < 0 or not np.isfinite(sample_step_m) or sample_step_m <= 0:
        raise ValueError("buffer/guard must be non-negative and sample_step_m positive")
    if not target.any():
        return set(), {
            "applied": True,
            "target_pixels": 0,
            "buffer_px": int(buffer_px),
            "guard_px": int(guard_px),
            "source_exclusion_radius_px": int(buffer_px + guard_px),
            "sample_step_m": float(sample_step_m),
            "segments_checked": int(len(segments)),
            "source_fids_total": int(len({seg.get("fid") for seg in segments})),
            "source_fids_excluded": 0,
            "source_segments_excluded": 0,
            "excluded_fids_sha256": hashlib.sha256(b"").hexdigest(),
            "retained_min_sample_distance_px": None,
        }

    radius_px = int(buffer_px + guard_px)
    pad = radius_px + 2
    padded_target = np.pad(target, pad, mode="constant", constant_values=False)
    exclusion_zone = binary_dilation(
        padded_target,
        structure=np.ones((2 * radius_px + 1, 2 * radius_px + 1), dtype=bool),
    )
    distance_to_target = distance_transform_edt(~padded_target)

    a, e = float(transform.a), float(transform.e)
    c, f = float(transform.c), float(transform.f)
    if a <= 0 or e >= 0 or abs(float(transform.b)) > 1e-9 or abs(float(transform.d)) > 1e-9:
        raise ValueError("source exclusion expects a north-up projected grid")
    padded_height, padded_width = padded_target.shape

    excluded_fids: set[int] = set()
    min_distance_by_fid: dict[int, float] = {}
    checked_samples = 0
    for seg in segments:
        fid = int(seg["fid"])
        pts = np.asarray(seg.get("pts", []), dtype=float)
        if pts.ndim != 2 or pts.shape[1] != 2 or len(pts) < 2 or not np.isfinite(pts).all():
            continue
        min_distance = min_distance_by_fid.get(fid, float("inf"))
        enters_buffer = False
        for p0, p1 in zip(pts[:-1], pts[1:]):
            length_m = float(np.hypot(*(p1 - p0)))
            n_intervals = max(1, int(np.ceil(length_m / sample_step_m)))
            fractions = np.linspace(0.0, 1.0, n_intervals + 1)
            samples = p0[None, :] + fractions[:, None] * (p1 - p0)[None, :]
            cols = np.floor((samples[:, 0] - c) / a).astype(np.int64) + pad
            rows = np.floor((samples[:, 1] - f) / e).astype(np.int64) + pad
            in_grid = ((rows >= 0) & (rows < padded_height) &
                       (cols >= 0) & (cols < padded_width))
            if not in_grid.any():
                continue
            rows = rows[in_grid]
            cols = cols[in_grid]
            checked_samples += int(rows.size)
            min_distance = min(min_distance, float(distance_to_target[rows, cols].min()))
            if exclusion_zone[rows, cols].any():
                enters_buffer = True
                break
        if enters_buffer:
            excluded_fids.add(fid)
        min_distance_by_fid[fid] = min_distance

    unique_fids = {int(seg["fid"]) for seg in segments}
    excluded_payload = ",".join(str(fid) for fid in sorted(excluded_fids)).encode("ascii")
    retained_distances = [
        dist for fid, dist in min_distance_by_fid.items()
        if fid not in excluded_fids and np.isfinite(dist)
    ]
    excluded_segments = sum(int(seg["fid"]) in excluded_fids for seg in segments)
    return excluded_fids, {
        "applied": True,
        "target_pixels": int(target.sum()),
        "buffer_px": int(buffer_px),
        "guard_px": int(guard_px),
        "source_exclusion_radius_px": radius_px,
        "source_exclusion_shape": "square/Chebyshev",
        "sample_step_m": float(sample_step_m),
        "segments_checked": int(len(segments)),
        "sampled_points": int(checked_samples),
        "source_fids_total": int(len(unique_fids)),
        "source_fids_excluded": int(len(excluded_fids)),
        "source_segments_excluded": int(excluded_segments),
        "excluded_fids_sha256": hashlib.sha256(excluded_payload).hexdigest(),
        "retained_min_sample_distance_px": (
            float(min(retained_distances)) if retained_distances else None
        ),
    }


def c2_stepover_bridges(base: np.ndarray | None = None, d_min_m: float = 300.0, d_max_m: float = 2500.0,
                        strike_tol_deg: float = 30.0, dot_spacing_px: float = 2.83, *,
                        catalogue_mask: np.ndarray | None = None,
                        source_segments: list[dict] | None = None,
                        excluded_source_fids: set[int] | None = None,
                        source_exclusion_report: dict | None = None) -> tuple[np.ndarray, dict]:
    """Candidate relay-bridge dots between interacting tips of DISTINCT fault polylines.

    Faulds & Hinz (2015, OSTI 1724082) report step-overs/relay ramps among
    favorable regional geothermal settings; this motivates, but does not verify,
    the target-domain bridge hypothesis. This is deliberately different from
    GEMSDOE27's failed T-v2 rule, which filled gaps inside the same polyline
    (230/345 links were same-FID compiler artifacts). Here only distinct-FID
    tip pairs with near-parallel strikes and close tip approach qualify, and
    the bridge is gated by the potential-field edge layer
    (iso_grav_anom_hg >= in-footprint 80th percentile within 200 m). For a
    spatial holdout, pass the fold-visible catalogue mask and exclude every
    source FID intersecting the buffered held-out target before construction;
    the defaults below are for the full-data production map only.
    """
    import rasterio

    if base is None:
        base = c0_control()
    catalogue = load_catalogue() if catalogue_mask is None else np.asarray(catalogue_mask, dtype=bool)
    footprint, _ = load_template()
    base = np.asarray(base)
    if base.shape != footprint.shape or catalogue.shape != footprint.shape:
        raise ValueError("base, catalogue mask, and template must share the canonical grid")
    segs = _qfaults_tip_segments() if source_segments is None else source_segments
    excluded_source_fids = set(excluded_source_fids or ())
    active_segs = [seg for seg in segs if int(seg["fid"]) not in excluded_source_fids]

    # gravity horizontal gradient gate
    with rasterio.open(data_dir() / "core" / "training_features.tif") as ds:
        ghg = ds.read(18)  # band 18: iso_grav_anom_hg
    finite = np.isfinite(ghg) & footprint
    thr = np.quantile(ghg[finite], 0.80)
    grav_edge = (ghg >= thr) & footprint
    d_grav = distance_transform_edt(~grav_edge)

    # tip list: both ends of every retained segment, with local strike at the tip
    tips = []
    for seg in active_segs:
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
    report = {
        "candidate": "C2_stepover_bridges",
        "qualifying_tip_pairs": pairs,
        "added_dots": added,
        "source_segments_total": int(len(segs)),
        "source_segments_used": int(len(active_segs)),
        "source_fids_excluded": int(len(excluded_source_fids)),
        "catalogue_mask_pixels": int(catalogue.sum()),
        "source_exclusion": source_exclusion_report or {"applied": False},
        "parameters": {
            "d_min_m": float(d_min_m),
            "d_max_m": float(d_max_m),
            "strike_tol_deg": float(strike_tol_deg),
            "dot_spacing_px": float(dot_spacing_px),
            "catalogue_exclusion_px": 2.0,
            "existing_dot_exclusion_px": 2.5,
            "gravity_edge_distance_px": 2.0,
        },
    }
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
