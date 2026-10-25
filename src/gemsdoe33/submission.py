"""Submission GeoTIFF writer and a local format validator.

The package writer emits two variants from the same in-footprint values: ``-nan.tif`` with NaN
outside and ``-zeros.tif`` with 0.0 outside. Choose outside semantics only after checking the
current official instructions; neither encoding is a submission recommendation by itself. The
validator checks saved bytes for the registered grid, dtype, band count, in-footprint range and
outside values. These are local checks, not an organizer portal acceptance test.

Grid geometry is read from the owner-mirrored sample file, not an authenticated organizer download.
The measured in-footprint training-band nodata counts and source provenance are recorded in
``registry/irregularities.json``.
"""

from __future__ import annotations

import hashlib
import json
import re
import zipfile
from pathlib import Path

import numpy as np
import rasterio

from . import grid

# The session's stricter run-card protocol caps paste-ready comments at 140 characters,
# even though historical artifacts may retain the portal's older 200-character convention.
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
    """Write a single-band float32 GeoTIFF after fail-closed probability checks.

    ``values`` may be either a full-grid array or a 1-D array containing exactly the
    in-footprint predictions. Every written in-footprint value must be finite and in
    ``[0, 1]``. Outside cells may only be NaN/null or 0.0 (the latter is a troubleshooting
    variant, not a claim of organizer acceptance).
    """
    profile = grid.template_profile()
    footprint = np.asarray(grid.template_footprint(), dtype=bool)
    if footprint.ndim != 2 or not footprint.any():
        raise ValueError("template footprint must be a non-empty 2-D mask")

    raw = np.asarray(values)
    if np.iscomplexobj(raw):
        raise ValueError("in-footprint predictions must be real-valued probabilities")
    if raw.shape == footprint.shape:
        selected = raw[footprint]
    elif raw.ndim == 1 and raw.size == int(footprint.sum()):
        selected = raw
    else:
        raise ValueError(
            "values must match the template grid or contain exactly one value per footprint cell"
        )
    try:
        selected64 = np.asarray(selected, dtype=np.float64)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("in-footprint predictions must be numeric probabilities") from exc
    if not np.isfinite(selected64).all():
        raise ValueError("in-footprint predictions must all be finite; NaN/Inf is not allowed")
    if np.any((selected64 < 0.0) | (selected64 > 1.0)):
        raise ValueError("in-footprint predictions must lie in [0, 1]; refusing to clip")
    selected32 = selected64.astype(np.float32)
    if not np.isfinite(selected32).all():
        raise ValueError("in-footprint probabilities overflow float32")

    if outside is None:
        outside_value = np.nan
    else:
        try:
            outside_value = float(outside)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("outside must be NaN/null or 0.0") from exc
    if not (np.isnan(outside_value) or outside_value == 0.0):
        raise ValueError("outside must be NaN/null or 0.0")

    out = np.full(footprint.shape, outside_value, dtype=np.float32)
    out[footprint] = selected32
    if np.isnan(outside_value):
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
    """Re-read saved bytes and apply the local grid, probability, and outside-mask checks.

    NaN outside is allowed by the recorded null/NaN wording, so ``whole_array_finite`` is
    reported separately from finite-value range. This is a local audit, not portal acceptance.
    """
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
        tmpl = np.asarray(grid.template_footprint(), dtype=bool)
        same_shape = tmpl.shape == arr.shape
        checks.append(("template_footprint_shape_matches", same_shape))
        finite = np.isfinite(arr)
        finite_values = arr[finite]
        checks.append(("whole_array_finite", bool(finite.all())))
        checks.append(("all_finite_values_in_range_0_1",
                       bool(finite_values.size > 0
                            and (finite_values >= 0.0).all()
                            and (finite_values <= 1.0).all())))
        checks.append(("whole_array_finite_and_in_range_0_1",
                       bool(finite.all() and finite_values.size > 0
                            and (finite_values >= 0.0).all()
                            and (finite_values <= 1.0).all())))
        if same_shape and tmpl.any():
            inside = arr[tmpl]
            outside = arr[~tmpl]
            checks.append(("footprint_non_empty", True))
            checks.append(("no_nan_or_inf_inside_footprint", bool(np.isfinite(inside).all())))
            checks.append(("inside_values_in_range_0_1",
                           bool(np.isfinite(inside).all()
                                and (inside >= 0.0).all()
                                and (inside <= 1.0).all())))
            checks.append(("outside_is_null_or_zero",
                           bool((np.isnan(outside) | (outside == 0.0)).all())))
        else:
            checks.extend([
                ("footprint_non_empty", False),
                ("no_nan_or_inf_inside_footprint", False),
                ("inside_values_in_range_0_1", False),
                ("outside_is_null_or_zero", False),
            ])
        checks.append(("single_band_description", src.descriptions[0] == "fault probability"))
    diagnostic_only = {"whole_array_finite", "whole_array_finite_and_in_range_0_1"}
    for name, ok in checks:
        if not ok and name not in diagnostic_only:
            errors.append(name)
    return {"file": str(path), "checks": dict(checks), "errors": errors,
            "n_checks": len(checks), "pass": not errors}


def build_package(mask: np.ndarray, weights: np.ndarray | None, name: str,
                  outdir: Path, note: str) -> dict:
    """Emit checked -zeros/-nan variants, one-TIFF ZIPs and a local audit receipt.

    Invalid probabilities are rejected rather than silently clipped or replaced with zero, and
    existing package outputs are never overwritten. A successful local receipt still does not mean
    the artifact passed a scientific promotion gate or was accepted by the organizer.
    """
    if not isinstance(name, str) or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,95}", name) is None:
        raise ValueError("name must be a 1–96 character filename-safe identifier")
    if not isinstance(note, str):
        raise ValueError("note must be plain text")
    footprint = np.asarray(grid.template_footprint(), dtype=bool)
    raw_mask = np.asarray(mask)
    if footprint.ndim != 2 or not footprint.any() or raw_mask.shape != footprint.shape:
        raise ValueError("mask and template footprint must be equal-shaped 2-D arrays")
    if np.iscomplexobj(raw_mask):
        raise ValueError("emission mask must contain only boolean/0/1 values")
    if raw_mask.dtype != np.bool_:
        try:
            numeric_mask = np.asarray(raw_mask, dtype=np.float64)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("emission mask must contain only boolean/0/1 values") from exc
        if (not np.isfinite(numeric_mask).all()
                or np.any((numeric_mask != 0.0) & (numeric_mask != 1.0))):
            raise ValueError("emission mask must contain only boolean/0/1 values")
    mask = raw_mask.astype(bool, copy=False) & footprint
    vals = np.zeros(mask.shape, dtype=np.float32)
    if weights is not None:
        raw_weights = np.asarray(weights)
        if raw_weights.shape != mask.shape:
            raise ValueError("weights must match the template grid")
        if np.iscomplexobj(raw_weights):
            raise ValueError("weights must be real-valued probabilities")
        try:
            w = np.asarray(raw_weights, dtype=np.float64)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("weights must be numeric probabilities") from exc
        selected = w[mask]
        if not np.isfinite(selected).all():
            raise ValueError("emitted weights must all be finite; refusing to replace NaN/Inf")
        if np.any((selected < 0.0) | (selected > 1.0)):
            raise ValueError("emitted weights must lie in [0, 1]; refusing to clip")
        vals[mask] = selected.astype(np.float32)
    else:
        vals[mask] = 1.0
    cid = content_id(mask)
    note = note.replace("{cid}", cid).replace("PENDING", cid)
    if len(note) > MAX_NOTE:
        raise ValueError(f"note is {len(note)} chars, limit {MAX_NOTE}")

    zeros = outdir / f"{name}-{cid}-zeros.tif"
    nant = outdir / f"{name}-{cid}-nan.tif"
    zip_zero = outdir / f"{zeros.stem}.zip"
    zip_nan = outdir / f"{nant.stem}.zip"
    receipt_path = outdir / f"receipt-{name}-{cid}.json"
    note_path = outdir / f"note-{name}-{cid}.txt"
    targets = [zeros, nant, zip_zero, zip_nan, receipt_path, note_path]
    collisions = [str(path) for path in targets if path.exists() or path.is_symlink()]
    if collisions:
        raise FileExistsError(f"refusing to overwrite existing package outputs: {collisions}")
    r_zero = write_tif(vals[footprint], zeros, outside=0.0)
    r_nan = write_tif(vals[footprint], nant, outside=np.nan)
    r_zip0 = write_zip(zeros, zip_zero)
    r_zipn = write_zip(nant, zip_nan)
    v_zero = validate(zeros)
    v_nan = validate(nant)
    receipt = {
        "name": name, "content_id": cid, "note": note, "note_chars": len(note),
        "emitted_pixels": int(mask.sum()),
        "emitted_fraction_of_footprint": float(mask.sum() / footprint.sum()),
        "value_range_inside": [float(vals[footprint].min()), float(vals[footprint].max())],
        "zeros": {**r_zero, **v_zero}, "nan": {**r_nan, **v_nan},
        "zip_zeros": r_zip0, "zip_nan": r_zipn,
        "all_checks_pass": bool(v_zero["pass"] and v_nan["pass"]),
    }
    receipt_path.write_text(json.dumps(receipt, indent=2))
    note_path.write_text(note + "\n")
    return receipt
