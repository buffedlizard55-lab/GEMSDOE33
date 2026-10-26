"""Submission GeoTIFF writer and a local format validator.

The package writer emits two variants from the same in-footprint values: ``-nan.tif`` with NaN
outside (recommended because it follows the official null/NaN-outside wording) and ``-zeros.tif``
with 0.0 outside (troubleshooting alternative only). The validator checks the saved bytes for the
registered grid, dtype, band count, in-footprint range and outside values. These are local checks,
not an organizer portal acceptance test.

Grid geometry is read from the owner-mirrored sample file, not an authenticated organizer download.
The measured in-footprint training-band nodata counts and source provenance are recorded in
``registry/irregularities.json``.
"""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

import numpy as np
import rasterio

from . import grid

MAX_NOTE = 140


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def content_id(mask: np.ndarray) -> str:
    """12-hex content identifier over the emitted pixel set (grid-independent of file encoding)."""
    return hashlib.sha256(np.packbits(np.asarray(mask, bool), axis=None).tobytes()).hexdigest()[:12]


def write_tif(values: np.ndarray, dest: Path, outside: float | None = np.nan) -> dict:
    """Write a single-band float32 submission raster on the exact template grid.

    ``values`` is the in-footprint prediction in [0, 1]; cells outside the footprint get
    ``outside`` (NaN for the recommended spec-aligned variant, 0.0 for the troubleshooting twin).
    """
    profile = grid.template_profile()
    footprint = grid.template_footprint()
    # Reject bad predictions before conversion/writing; never silently clip a scientific result.
    v = np.asarray(values)
    if v.shape == footprint.shape:
        v = v[footprint]
    elif v.shape != (int(footprint.sum()),):
        raise ValueError("values must match template shape or the in-footprint cell count")
    if not np.isfinite(v).all() or np.any((v < 0) | (v > 1)):
        raise ValueError("in-footprint predictions must be finite and in [0,1]")
    if outside is not None and not (np.isscalar(outside) and (np.isnan(outside) or outside == 0)):
        raise ValueError("outside must be NaN/None or zero; infinity is not null")
    out = np.full(footprint.shape, np.nan if outside is None else outside, dtype=np.float32)
    out[footprint] = v.astype(np.float32)
    if outside is None or np.isnan(outside):
        profile["nodata"] = np.nan
    else:
        profile["nodata"] = None
    dest.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(dest, "w", **profile) as dst:
        dst.write(out, 1)
        dst.set_band_description(1, "fault probability")
    return {"path": str(dest), "bytes": dest.stat().st_size, "sha256": _sha256(dest)}


def write_zip(tif_path: Path, dest: Path) -> dict:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.write(tif_path, arcname=tif_path.name)
    return {"path": str(dest), "bytes": dest.stat().st_size, "sha256": _sha256(dest),
            "members": 1}


def validate(path: Path) -> dict:
    """Re-read saved bytes for the local format contract; not portal acceptance."""
    errors, checks = [], []
    with rasterio.open(path) as src:
        arr = src.read(1)
        checks.append(("count_is_1", src.count == 1))
        checks.append(("dtype_is_float32", src.dtypes[0] == "float32"))
        checks.append(("crs_is_epsg_32611", src.crs is not None and src.crs.to_epsg() == 32611))
        checks.append(("shape_is_3730x3292", (src.height, src.width) == (3730, 3292)))
        tpl_tr, tpl_w, tpl_h, tpl_crs = grid.template_georef()
        checks.append(("georef_matches_template",
                       tuple(src.transform)[:6] == tuple(tpl_tr)[:6]
                       and (src.width, src.height) == (tpl_w, tpl_h)
                       and src.crs == tpl_crs))
        tmpl = grid.template_footprint()
        if arr.shape != tmpl.shape:
            checks.append(("footprint_shape_matches", False))
            return {"file": str(path), "checks": dict(checks),
                    "errors": [name for name, ok in checks if not ok],
                    "n_checks": len(checks), "pass": False}
        finite = np.isfinite(arr)
        checks.append(("no_nan_inside_footprint", bool(finite[tmpl].all())))
        inside = arr[tmpl]
        checks.append(("min_ge_0", bool((inside >= 0).all())))
        checks.append(("max_le_1", bool((inside <= 1).all())))
        checks.append(("outside_is_null_or_zero", bool((np.isnan(arr) | (arr == 0))[~tmpl].all())))
        checks.append(("single_band_description", src.descriptions[0] == "fault probability"))
    for name, ok in checks:
        if not ok:
            errors.append(name)
    return {"file": str(path), "checks": dict(checks), "errors": errors,
            "n_checks": len(checks), "pass": not errors}


def build_package(mask: np.ndarray, weights: np.ndarray | None, name: str,
                  outdir: Path, note: str) -> dict:
    """Emit the -zeros primary, the -nan twin, one .zip each and a receipt."""
    footprint = grid.template_footprint()
    mask = np.asarray(mask)
    if mask.shape != footprint.shape or not np.isin(mask, (0, 1)).all():
        raise ValueError("mask must be binary and match the template shape")
    mask = mask.astype(bool) & footprint
    vals = np.zeros(mask.shape, dtype=np.float32)
    if weights is not None:
        w = np.asarray(weights)
        if w.shape != mask.shape:
            raise ValueError("weights must match the template shape")
        if not np.isfinite(w[mask]).all() or np.any((w[mask] < 0) | (w[mask] > 1)):
            raise ValueError("selected weights must be finite and in [0,1]; no silent clipping")
        vals[mask] = w[mask].astype(np.float32)
    else:
        vals[mask] = 1.0
    emitted_mask = vals > 0
    binary_values = np.all((vals == 0) | (vals == 1))
    cid = content_id(emitted_mask) if binary_values else hashlib.sha256(
        np.asarray(vals.shape, dtype="<i8").tobytes() + vals.astype("<f4").tobytes()
    ).hexdigest()[:12]
    note = note.replace("{cid}", cid).replace("PENDING", cid)
    if len(note) > MAX_NOTE:
        raise ValueError(f"note is {len(note)} chars, limit {MAX_NOTE}")

    zeros = outdir / f"{name}-{cid}-zeros.tif"
    nant = outdir / f"{name}-{cid}-nan.tif"
    r_zero = write_tif(vals[footprint], zeros, outside=0.0)
    r_nan = write_tif(vals[footprint], nant, outside=np.nan)
    r_zip0 = write_zip(zeros, outdir / f"{zeros.stem}.zip")
    r_zipn = write_zip(nant, outdir / f"{nant.stem}.zip")
    v_zero = validate(zeros)
    v_nan = validate(nant)
    receipt = {
        "name": name, "content_id": cid, "note": note, "note_chars": len(note),
        "emitted_pixels": int(emitted_mask.sum()),
        "emitted_fraction_of_footprint": float(emitted_mask.sum() / footprint.sum()),
        "value_range_inside": [float(vals[footprint].min()), float(vals[footprint].max())],
        "zeros": {**r_zero, **v_zero}, "nan": {**r_nan, **v_nan},
        "zip_zeros": r_zip0, "zip_nan": r_zipn,
        "all_checks_pass": bool(v_zero["pass"] and v_nan["pass"]),
    }
    (outdir / f"receipt-{name}-{cid}.json").write_text(json.dumps(receipt, indent=2))
    (outdir / f"note-{name}-{cid}.txt").write_text(note + "\n")
    return receipt
