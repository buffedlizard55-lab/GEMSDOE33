"""A33-R3-LCHC: Least-Cost Hydrothermal Connectivity (graph/circuit-theory transfer).

Lane (single method paragraph): target faults missing from the USGS/INGENIOUS
catalogue by modelling the SUBSURFACE PLUMBING that must connect independently
documented, non-fault thermal manifestation points (INGENIOUS DOE GDR #1391
"Hot"-class springs/wells and Quaternary volcanic vents) through a resistance
("cost") surface built only from GeoDAWN potential-field, radiometric-adjacent
and basement-structure geophysics (conductivity, basement-depth gradient,
gravity horizontal gradient, geodetic shear/dilatation rate). A minimum-cost
Steiner-like tree (seed-pairwise Dijkstra + minimum spanning tree over the
pairwise cost-distance matrix) threading these points reveals the buried
conduit segments -- a graph/least-cost-path construction that is NEVER used
anywhere else in this repository (H19-5 is curvilinear per-pixel trace
detection; CSHT/A33-L1/H33-6/H33-D are pixel-wise classifiers, gradient-vector
consensus fields, or geometric catalogue-tip grafts). The candidate surface
reads `labels.tif`/`existing_faults.tif` NOWHERE in its construction: the
thermal/vent seed points and every cost-surface channel come from
catalogue-independent sources, so the method is immune by construction to the
catalogue-visibility leakage that every other local hypothesis must guard
against with a fold-restricted classifier fit. The physical justification is
the published Great Basin structural-control model for fault-hosted
geothermal upflow (e.g. Faulds & Hinz, 2015 Great Basin play-fairway fault
architecture; Blackwell & Richards, 2004 Geothermal Map of North America):
surface thermal manifestations and young volcanic vents mark the two visible
ends of deep, often blind, normal-fault plumbing, and the path of least
hydraulic/structural resistance between them is a reasonable, non-arbitrary
proxy for the unmapped connecting fault trace -- including segments the
catalogue never recorded. Non-fault mimics are explicitly named in the run
card (buried intrusive margins, paleo-lake-shoreline benches, and conductive
sedimentary basin fill can all produce a low-cost corridor between two
hydrologically connected but non-tectonic points).

All transforms below are label-free. The only catalogue contact anywhere in
this module is the standard, shared, pixel-exact visible-catalogue exclusion
mask applied by the caller before emission -- identical in spirit to every
other lane in this repository.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass

import numpy as np
from scipy.ndimage import distance_transform_edt, label as ndi_label
from scipy.sparse import coo_matrix, csr_matrix
from scipy.sparse.csgraph import dijkstra, minimum_spanning_tree

from .csht_transfer import load_thermal_vent_seeds, percentile_rank_surface  # reuse, no fork
from .paths import CACHE_FEATURES

# ---------------------------------------------------------------------------
# Cost-surface channels: ALL label-free GeoDAWN geophysics, never the catalogue.
# ---------------------------------------------------------------------------
COST_CHANNEL_NAMES: tuple[str, ...] = (
    "cond_surf",
    "cond_surf_gms2",
    "iso_grav_anom_hg",
    "iso_grav_anom_slope",
    "geod_shearrate",
    "geod_dilaterate",
)
BASEMENT_DEPTH_CHANNEL = "depth_to_base_surf"
CORROBORATION_CHANNEL_NAMES: tuple[str, ...] = ("lid_coh100", "lid_relief", "tmi_hg")

DOWNSAMPLE_FACTOR = 3          # 100 m -> 300 m, matched to the DTI triangular-kernel radius
MST_EDGE_KEEP_QUANTILE = 0.85  # drop the longest 15% of MST cost-distance edges (de-noising)
SEED_MERGE_RADIUS_PX = 3       # ~300 m: merge adjacent GDR records into one plumbing endpoint
MAX_SEED_CLUSTERS = 90         # computational ceiling; clusters are ranked by member count
EPS = 1e-6


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_channel(name: str) -> np.ndarray:
    path = CACHE_FEATURES / f"{name}.npy"
    if not path.is_file():
        raise FileNotFoundError(f"Missing cached channel {path}")
    return np.asarray(np.load(path, mmap_mode="r"), dtype=np.float32)


def basement_structure_edge(depth: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    """Horizontal gradient magnitude of the basement-depth surface (buried structural steps)."""
    d = np.asarray(depth, dtype=np.float64)
    fill = float(np.nanmedian(d[footprint & np.isfinite(d)]))
    d = np.where(np.isfinite(d), d, fill)
    gy, gx = np.gradient(d)
    mag = np.hypot(gy, gx).astype(np.float32)
    return np.where(footprint, mag, 0.0).astype(np.float32)


def _percentile_map(values: np.ndarray, fit_mask: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    """Rank-map every footprint pixel against the empirical CDF fit ONLY on ``fit_mask``."""
    v = np.asarray(values, dtype=np.float64)
    fill = float(np.nanmedian(v[fit_mask & np.isfinite(v)]))
    v = np.where(np.isfinite(v), v, fill)
    fit_vals = np.sort(v[fit_mask])
    if fit_vals.size < 2:
        raise ValueError("Degenerate fit mask for percentile transform")
    quantile_x = fit_vals
    quantile_y = np.linspace(0.0, 1.0, fit_vals.size, dtype=np.float64)
    out = np.interp(v, quantile_x, quantile_y)
    return np.where(footprint, out, 0.0).astype(np.float32)


@dataclass
class CostSurfaceReport:
    channels: tuple[str, ...]
    fit_domain_cells: int
    favorability_mean: float
    favorability_std: float


def build_cost_surface(
    footprint: np.ndarray, fit_mask: np.ndarray
) -> tuple[np.ndarray, np.ndarray, CostSurfaceReport]:
    """Average-percentile favorability across cost channels, fit ONLY on ``fit_mask``.

    ``fit_mask`` is the caller's spatially purged TRAIN region (never touches which catalogue
    pixels are withheld; it exists purely so the percentile-CDF statistics are never fit using a
    pixel population informed by the held-out quadrant, mirroring every other lane's discipline
    even though no catalogue value is read here at all).
    """
    fp = np.asarray(footprint, dtype=bool)
    fit = np.asarray(fit_mask, dtype=bool) & fp
    ranks = []
    for name in COST_CHANNEL_NAMES:
        arr = _load_channel(name)
        ranks.append(_percentile_map(arr, fit, fp))
    edge = basement_structure_edge(_load_channel(BASEMENT_DEPTH_CHANNEL), fp)
    ranks.append(_percentile_map(edge, fit, fp))
    favorability = np.mean(np.stack(ranks, axis=0), axis=0).astype(np.float32)
    favorability = np.where(fp, favorability, 0.0).astype(np.float32)
    cost = np.where(fp, np.clip(1.0 - favorability, 0.02, 1.0), 1.0).astype(np.float32)
    report = CostSurfaceReport(
        channels=COST_CHANNEL_NAMES + (f"{BASEMENT_DEPTH_CHANNEL}_hg",),
        fit_domain_cells=int(fit.sum()),
        favorability_mean=float(favorability[fp].mean()),
        favorability_std=float(favorability[fp].std()),
    )
    return cost, favorability, report


def downsample_mean(arr: np.ndarray, weight: np.ndarray, factor: int) -> tuple[np.ndarray, np.ndarray]:
    """Weighted block-mean downsample; returns (small_values, small_valid_fraction)."""
    h, w = arr.shape
    pad_h, pad_w = (-h) % factor, (-w) % factor
    a = np.pad(np.asarray(arr, dtype=np.float64), ((0, pad_h), (0, pad_w)), mode="edge")
    m = np.pad(np.asarray(weight, dtype=np.float64), ((0, pad_h), (0, pad_w)), mode="constant")
    hp, wp = a.shape
    a4 = a.reshape(hp // factor, factor, wp // factor, factor)
    m4 = m.reshape(hp // factor, factor, wp // factor, factor)
    num = (a4 * m4).sum(axis=(1, 3))
    den = m4.sum(axis=(1, 3))
    out = np.divide(num, den, out=np.zeros_like(num), where=den > 0)
    return out.astype(np.float32), den.astype(np.float32)


def cluster_seed_cells(seed_mask: np.ndarray, merge_radius_px: int = SEED_MERGE_RADIUS_PX
                        ) -> list[tuple[int, int, int]]:
    """Merge adjacent/duplicate GDR seed cells into discrete plumbing-endpoint clusters.

    Returns a list of (row, col, member_count) cluster centroids (member_count = number of raw
    1.0-weight pixels folded into the cluster; row/col snapped to the nearest actual seed pixel).
    """
    from scipy.ndimage import binary_dilation

    mask = np.asarray(seed_mask, dtype=bool)
    if not mask.any():
        return []
    structure = np.ones((2 * merge_radius_px + 1, 2 * merge_radius_px + 1), dtype=bool)
    dilated = binary_dilation(mask, structure=structure)
    labels, n = ndi_label(dilated, structure=np.ones((3, 3), dtype=int))
    clusters = []
    for cid in range(1, n + 1):
        comp = labels == cid
        comp_seed = comp & mask
        if not comp_seed.any():
            continue
        ys, xs = np.nonzero(comp_seed)
        cy, cx = float(ys.mean()), float(xs.mean())
        dist = (ys - cy) ** 2 + (xs - cx) ** 2
        best = int(np.argmin(dist))
        clusters.append((int(ys[best]), int(xs[best]), int(comp_seed.sum())))
    clusters.sort(key=lambda t: -t[2])
    return clusters


def build_small_graph(cost_small: np.ndarray, valid_small: np.ndarray) -> tuple[csr_matrix, np.ndarray]:
    """8-connected resistance graph over the downsampled grid; edge weight = step * mean(cost)."""
    h, w = cost_small.shape
    node_id = np.full((h, w), -1, dtype=np.int64)
    node_id[valid_small] = np.arange(int(valid_small.sum()))
    n_nodes = int(valid_small.sum())
    rows, cols, data = [], [], []
    offsets = [(-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),
               (-1, -1, np.sqrt(2.0)), (-1, 1, np.sqrt(2.0)), (1, -1, np.sqrt(2.0)), (1, 1, np.sqrt(2.0))]
    yy, xx = np.nonzero(valid_small)
    for dy, dx, step in offsets:
        ny, nx = yy + dy, xx + dx
        ok = (ny >= 0) & (ny < h) & (nx >= 0) & (nx < w)
        ok_idx = np.flatnonzero(ok)
        ny_ok, nx_ok = ny[ok_idx], nx[ok_idx]
        valid_nbr = valid_small[ny_ok, nx_ok]
        src_y, src_x = yy[ok_idx][valid_nbr], xx[ok_idx][valid_nbr]
        dst_y, dst_x = ny_ok[valid_nbr], nx_ok[valid_nbr]
        w_edge = step * 0.5 * (cost_small[src_y, src_x] + cost_small[dst_y, dst_x])
        rows.append(node_id[src_y, src_x])
        cols.append(node_id[dst_y, dst_x])
        data.append(w_edge)
    rows = np.concatenate(rows)
    cols = np.concatenate(cols)
    data = np.concatenate(data).astype(np.float64)
    graph = coo_matrix((data, (rows, cols)), shape=(n_nodes, n_nodes)).tocsr()
    return graph, node_id


def connect_seed_clusters(
    graph: csr_matrix,
    node_id: np.ndarray,
    clusters_small: list[tuple[int, int]],
    shape_small: tuple[int, int],
    *,
    keep_quantile: float = MST_EDGE_KEEP_QUANTILE,
) -> tuple[np.ndarray, dict]:
    """Seed-pairwise Dijkstra + minimum-spanning-tree over the cost-distance matrix.

    Returns a float32 confidence surface (0..1, 0 outside any retained path) on the SMALL grid
    plus a diagnostic report. Confidence per retained MST edge = directness ratio = (straight-line
    pixel distance) / (cost-weighted graph distance), clipped to [0, 1]; a value near 1 means the
    least-cost route is almost straight (strong, continuous structural control), while a low value
    means the route meanders through favourable terrain with little direct alignment.
    """
    seed_node_ids = np.array([node_id[r, c] for r, c in clusters_small], dtype=np.int64)
    keep = seed_node_ids >= 0
    seed_node_ids = seed_node_ids[keep]
    clusters_kept = [c for c, k in zip(clusters_small, keep) if k]
    if seed_node_ids.size < 2:
        return np.zeros(shape_small, dtype=np.float32), {"n_seed_clusters": int(seed_node_ids.size),
                                                           "n_mst_edges_total": 0, "n_mst_edges_kept": 0}

    dist_matrix, predecessors = dijkstra(
        graph, directed=False, indices=seed_node_ids, return_predecessors=True
    )
    n_seeds = seed_node_ids.size
    pairwise = dist_matrix[:, seed_node_ids]
    pairwise = np.where(np.isfinite(pairwise), pairwise, np.inf)
    mst = minimum_spanning_tree(csr_matrix(pairwise)).tocoo()

    yy_all, xx_all = np.nonzero(node_id >= 0)
    inv_rows = np.full(graph.shape[0], -1, dtype=np.int64)
    inv_cols = np.full(graph.shape[0], -1, dtype=np.int64)
    inv_rows[node_id[yy_all, xx_all]] = yy_all
    inv_cols[node_id[yy_all, xx_all]] = xx_all

    edge_weights = mst.data
    threshold = float(np.quantile(edge_weights, keep_quantile)) if edge_weights.size else 0.0
    surface = np.zeros(shape_small, dtype=np.float32)
    edges_report = []
    for i, j, w_cost in zip(mst.row, mst.col, mst.data):
        if not np.isfinite(w_cost) or w_cost <= 0:
            continue
        ry, rx = clusters_kept[i]
        cy, cx = clusters_kept[j]
        straight = float(np.hypot(ry - cy, rx - cx))
        directness = float(np.clip(straight / max(w_cost, EPS), 0.0, 1.0))
        kept = bool(w_cost <= threshold or edge_weights.size <= 2)
        edges_report.append({
            "i": int(i), "j": int(j), "cost_distance": float(w_cost),
            "straight_px": straight, "directness": directness, "kept": kept,
        })
        if not kept:
            continue
        node_j = seed_node_ids[j]
        pred_row = predecessors[i]
        current = node_j
        target = seed_node_ids[i]
        steps = 0
        max_steps = predecessors.shape[1] + 1
        while current != target and current != -9999 and steps < max_steps:
            yy_n, xx_n = int(inv_rows[current]), int(inv_cols[current])
            surface[yy_n, xx_n] = max(surface[yy_n, xx_n], directness)
            current = int(pred_row[current])
            steps += 1
        if current == target:
            surface[clusters_kept[i][0], clusters_kept[i][1]] = max(
                surface[clusters_kept[i][0], clusters_kept[i][1]], directness
            )
    report = {
        "n_seed_clusters": int(n_seeds),
        "n_mst_edges_total": int(len(edges_report)),
        "n_mst_edges_kept": int(sum(e["kept"] for e in edges_report)),
        "keep_quantile": keep_quantile,
        "edge_cost_threshold": threshold,
        "edges": edges_report,
    }
    return surface, report


def upsample_nearest(small: np.ndarray, factor: int, shape_full: tuple[int, int]) -> np.ndarray:
    out = np.repeat(np.repeat(small, factor, axis=0), factor, axis=1)
    return out[: shape_full[0], : shape_full[1]]


@dataclass
class LCHCBundle:
    seed_report: dict
    cost_report: CostSurfaceReport
    graph_report: dict
    connect_report: dict


def fit_lchc_surface(
    footprint: np.ndarray,
    fit_mask: np.ndarray,
    *,
    seed_mask: np.ndarray | None = None,
) -> tuple[np.ndarray, LCHCBundle]:
    """End-to-end: cost surface -> 300 m graph -> seed MST connectivity -> full-res [0,1] surface.

    ``seed_mask`` lets the caller pass a precomputed thermal+vent union mask (built once, since it
    never depends on the catalogue or on ``fit_mask``); if omitted it is (re)loaded here.
    """
    fp = np.asarray(footprint, dtype=bool)
    if seed_mask is None:
        thermal, vent, seed_meta = load_thermal_vent_seeds(fp)
        seed_mask = thermal | vent
    else:
        seed_meta = {"union_seed_cells": int(np.asarray(seed_mask).sum())}

    cost, favorability, cost_report = build_cost_surface(fp, fit_mask)
    cost_small, valid_frac = downsample_mean(cost, fp.astype(np.float32), DOWNSAMPLE_FACTOR)
    valid_small = valid_frac > 0.0

    clusters = cluster_seed_cells(seed_mask)
    clusters = clusters[:MAX_SEED_CLUSTERS]
    clusters_small = [(r // DOWNSAMPLE_FACTOR, c // DOWNSAMPLE_FACTOR) for r, c, _n in clusters]
    # Snap any cluster landing on an invalid small cell to its nearest valid small cell.
    if not valid_small.any():
        raise ValueError("No valid downsampled cells; cannot build connectivity graph")
    _, (ny, nx) = distance_transform_edt(~valid_small, return_distances=True, return_indices=True)
    snapped = []
    for r, c in clusters_small:
        r = int(np.clip(r, 0, valid_small.shape[0] - 1))
        c = int(np.clip(c, 0, valid_small.shape[1] - 1))
        if not valid_small[r, c]:
            r, c = int(ny[r, c]), int(nx[r, c])
        snapped.append((r, c))

    graph, node_id = build_small_graph(cost_small, valid_small)
    graph_report = {"n_nodes": int(valid_small.sum()), "n_edges": int(graph.nnz),
                     "shape_small": list(valid_small.shape)}
    path_small, connect_report = connect_seed_clusters(graph, node_id, snapped, valid_small.shape)

    path_full = upsample_nearest(path_small, DOWNSAMPLE_FACTOR, fp.shape)
    path_full = np.where(fp, path_full, 0.0).astype(np.float32)

    corroboration = []
    for name in CORROBORATION_CHANNEL_NAMES:
        arr = _load_channel(name)
        finite = np.isfinite(arr)
        rank = _percentile_map(np.where(finite, arr, 0.0), fit_mask & fp & finite, fp)
        rank = np.where(finite, rank, 0.5)  # neutral multiplier inside LiDAR/geophysics voids
        corroboration.append(rank)
    corrob = np.mean(np.stack(corroboration, axis=0), axis=0).astype(np.float32)
    blended = path_full * (0.5 + 0.5 * corrob)
    surface = percentile_rank_surface(blended.astype(np.float32), fp)

    bundle = LCHCBundle(
        seed_report=seed_meta, cost_report=cost_report.__dict__, graph_report=graph_report,
        connect_report=connect_report,
    )
    return surface, bundle
