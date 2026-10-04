"""Grid, footprint and band handling for the owner-mirrored 100 m EPSG:32611 rasters.

The hash-pinned owner mirror of ``training_features.tif`` is a 19-band float32 GeoTIFF, 3292 ×
3730 cells, with a registered geotransform and nodata sentinel. It is not an organizer-authenticated
download. ``read_grid_meta`` exposes actual descriptions from the local bytes; ``BANDS`` below uses
short working keys and descriptions that must not be mistaken for independent provenance.
"""

from __future__ import annotations

import json
import numpy as np
import rasterio

from .paths import CACHE, CACHE_BANDS, DATA, band_path

SENTINEL = -3.4028234663852886e38
SAMPLE_SUBMISSION = "sample_submission.tif"
TRAINING = "training_features.tif"
LABELS = "labels.tif"

# Short keys used across the stack.  Index is the 1-based band number in training_features.tif.
BANDS = [
    (1, "mag_anom", "Magnetic anomaly - deviation from expected Earth's magnetic field"),
    (2, "rtp", "Reduced to pole magnetic data - magnetic anomaly corrected for latitude effects"),
    (3, "tmi_hg", "Total magnetic intensity horizontal gradient - rate of change in horizontal direction"),
    (4, "geod_2ndinv", "Geodetic second invariant - measure of strain rate tensor magnitude"),
    (5, "iso_grav_anom_slope", "Isostatic gravity anomaly slope - gradient of gravity after isostatic correction"),
    (6, "tc", "Tilt angle or total curvature - magnetic field derivative for edge detection"),
    (7, "geod_shearrate", "Geodetic shear rate - rate of angular deformation from GPS/InSAR"),
    (8, "geod_dilaterate", "Geodetic dilatation rate - rate of volumetric strain (expansion/contraction)"),
    (9, "tmi_vg", "Total magnetic intensity vertical gradient - rate of change in vertical direction"),
    (10, "deq_n100a15", "Distance to earthquake (n=100km radius, a=15 deg azimuth parameters)"),
    (11, "iso_grav_anom_vg", "Isostatic gravity anomaly vertical gradient - vertical rate of change"),
    (12, "det_elev", "Detrended elevation - topography with regional trends removed"),
    (13, "iso_grav_anom", "Isostatic gravity anomaly - gravity after compensating for topographic mass"),
    (14, "tmi", "Total magnetic intensity - total strength of magnetic field"),
    (15, "depth_to_base_surf", "Depth to basement surface - thickness of sedimentary cover"),
    (16, "ieq_n100a15", "Earthquake intensity or density (n=100km radius, a=15 deg parameters)"),
    (17, "cond_surf", "Conductivity surface - electrical conductivity of subsurface"),
    (18, "iso_grav_anom_hg", "Isostatic gravity anomaly horizontal gradient - horizontal rate of change"),
    (19, "det_elev_slope", "Detrended elevation slope - gradient of elevation after detrending"),
]

BAND_KEYS = [k for _, k, _ in BANDS]


def read_grid_meta() -> dict:
    """Grid metadata read back from the pinned bytes on disk (never hard-coded)."""
    with rasterio.open(DATA / TRAINING) as src:
        return {
            "width": src.width,
            "height": src.height,
            "count": src.count,
            "crs": str(src.crs),
            "transform": list(src.transform)[:6],
            "dtype": src.dtypes[0],
            "nodata": src.nodata,
            "descriptions": list(src.descriptions),
        }


def read_band(index: int) -> np.ndarray:
    """Read one 1-based band with the nodata sentinel converted to NaN."""
    with rasterio.open(DATA / TRAINING) as src:
        arr = src.read(index).astype(np.float32)
    arr[arr <= SENTINEL * 0.999] = np.nan
    return arr


def read_raster(name: str, band: int | None = 1):
    """Read an arbitrary raster in ``data/``; returns (array, profile).

    ``band=None`` reads every band (shape ``(n_bands, H, W)``); an integer reads one band
    (shape ``(H, W)``).  Multi-band external layers must be read with ``band=None`` — reading
    them one band at a time and then indexing the result silently yields grid *rows*.
    """
    with rasterio.open(DATA / name) as src:
        arr = src.read() if band is None else src.read(band)
        return arr, src.profile.copy()


def build_band_cache(force: bool = False) -> dict:
    """Sanitise all 19 bands to float32 .npy in .cache/bands and derive the footprint."""
    report = {"bands": [], "grid": read_grid_meta()}
    valid_stack = []
    for index, key, desc in BANDS:
        dest = band_path(key)
        if force or not dest.exists():
            arr = read_band(index)
            np.save(dest, arr)
        else:
            arr = np.load(dest, mmap_mode="r")
        finite = np.isfinite(np.asarray(arr))
        valid_stack.append(finite)
        report["bands"].append({
            "index": index, "key": key, "description": desc,
            "n_valid": int(finite.sum()),
            "min": float(np.nanmin(np.asarray(arr, dtype=np.float32))),
            "max": float(np.nanmax(np.asarray(arr, dtype=np.float32))),
        })
    # The working submission-footprint mask comes from the owner-mirrored sample file, not from
    # intersection of training bands. Several training bands carry nodata inside that mask, and
    # some layers have valid values beyond it. Save the mask used by this project and preserve
    # per-band coverage separately; this does not authenticate the organizer's scoring mask.
    core = [i for i, (_, k, _) in enumerate(BANDS) if k not in ("depth_to_base_surf", "cond_surf")]
    stack = np.stack([valid_stack[i] for i in core])
    coverage = stack.sum(axis=0)
    footprint = template_footprint()
    np.save(CACHE / "footprint.npy", footprint)
    np.save(CACHE / "core_coverage.npy", coverage.astype(np.uint8))
    report["n_core_bands"] = len(core)
    report["n_footprint"] = int(footprint.sum())
    report["n_grid"] = int(footprint.size)
    report["n_template_cells_missing_any_core_band"] = int((footprint & (coverage < len(core))).sum())
    report["n_template_cells_all_core_bands_valid"] = int((footprint & (coverage == len(core))).sum())
    report["footprint_fraction"] = float(footprint.mean())
    (CACHE / "band_report.json").write_text(json.dumps(report, indent=2))
    return report


def load_footprint() -> np.ndarray:
    p = CACHE / "footprint.npy"
    if not p.exists():
        build_band_cache()
    return np.load(p)


def load_band(key: str) -> np.ndarray:
    p = band_path(key)
    if not p.exists():
        build_band_cache()
    return np.load(p, mmap_mode="r")


def load_labels() -> np.ndarray:
    """Catalogue raster (USGS Quaternary faults + INGENIOUS), bool on the template grid."""
    with rasterio.open(DATA / LABELS) as src:
        arr = src.read(1)
    return arr > 0


def template_profile() -> dict:
    with rasterio.open(DATA / SAMPLE_SUBMISSION) as src:
        prof = src.profile.copy()
    prof.update(count=1, dtype="float32", nodata=np.nan, compress="deflate", predictor=3)
    return prof


def template_georef() -> tuple:
    """The owner-mirror template's ``(transform, width, height, crs)`` tuple.

    Values are read from local bytes rather than repeated as hard-coded constants. This checks
    internal consistency with the registered mirror, not organizer provenance.
    """
    with rasterio.open(DATA / SAMPLE_SUBMISSION) as src:
        return src.transform, src.width, src.height, src.crs


def template_footprint() -> np.ndarray:
    """Working footprint mask from the owner-mirrored sample (5,167,373 finite cells).

    The count is measured locally; it is not authenticated as the organizer scoring mask.
    IRREGULARITY (``IR-33-TEMPLATE-01``): the owner-mirrored ``sample_submission.tif`` is **not**
    the organiser's "total fault absence" template.  Inside its finite footprint it carries the
    value 1.0 on exactly the 60,988 catalogue pixels — it is bit-identical to ``labels.tif`` in
    its positive set — and 0.0 elsewhere.  It is therefore used here **only** for its finite
    mask (grid, CRS, transform), never as truth and never as a prediction target.
    """
    with rasterio.open(DATA / SAMPLE_SUBMISSION) as src:
        arr = src.read(1)
    return np.isfinite(arr)


def template_positive() -> np.ndarray:
    """The 60,988 cells the mirrored sample submission marks 1.0 (identical to ``labels.tif``)."""
    with rasterio.open(DATA / SAMPLE_SUBMISSION) as src:
        arr = src.read(1)
    return np.isfinite(arr) & (arr != 0)


def rowcol_to_xy(rows, cols) -> tuple[np.ndarray, np.ndarray]:
    with rasterio.open(DATA / TRAINING) as src:
        t = src.transform
    return t * (np.asarray(cols) + 0.5, np.asarray(rows) + 0.5)


def xy_to_rowcol(xs, ys) -> tuple[np.ndarray, np.ndarray]:
    with rasterio.open(DATA / TRAINING) as src:
        t = src.transform
    inv = ~t
    cols_f, rows_f = inv * (np.asarray(xs, float), np.asarray(ys, float))
    return np.floor(rows_f).astype(int), np.floor(cols_f).astype(int)


def ll_bounds() -> dict:
    """WGS84 lon/lat bounding box of the template grid, read from the pinned bytes."""
    import rasterio.warp as rw
    with rasterio.open(DATA / TRAINING) as src:
        b = src.bounds
        xs = [b.left, b.right]
        ys = [b.bottom, b.top]
        lons, lats = rw.transform(src.crs, "EPSG:4326", xs, ys)
    return {"west": min(lons), "east": max(lons), "south": min(lats), "north": max(lats)}
