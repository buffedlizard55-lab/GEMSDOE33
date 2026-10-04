"""Grid, footprint and catalogue helpers for the GEMS GeoDAWN grid.

Canonical grid (verified against the official sample_submission mirror):
  EPSG:32611, 100 m pixels, 3292 x 3730, bounds
  (243350, 4135550) - (572550, 4508550), 5,167,373 finite-footprint cells.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, distance_transform_edt, label

DEFAULT_DATA_DIR = Path(os.environ.get("GEMS_DATA_DIR", Path(__file__).resolve().parents[2] / ".cache" / "gemsdata"))


def data_dir() -> Path:
    return DEFAULT_DATA_DIR


@dataclass(frozen=True)
class Grid:
    height: int
    width: int
    transform: tuple
    crs: str
    bounds: tuple

    @property
    def shape(self):
        return (self.height, self.width)


def load_grid(template_path: Path | None = None) -> Grid:
    template_path = Path(template_path or data_dir() / "core" / "sample_submission.tif")
    with rasterio.open(template_path) as ds:
        return Grid(
            height=ds.height,
            width=ds.width,
            transform=tuple(ds.transform)[:6],
            crs=ds.crs.to_string(),
            bounds=tuple(ds.bounds),
        )


def load_template(template_path: Path | None = None) -> tuple[np.ndarray, Grid]:
    """Return (finite-footprint mask, grid) from the sample submission template."""
    template_path = Path(template_path or data_dir() / "core" / "sample_submission.tif")
    with rasterio.open(template_path) as ds:
        sample = ds.read(1)
        grid = Grid(ds.height, ds.width, tuple(ds.transform)[:6], ds.crs.to_string(), tuple(ds.bounds))
    return np.isfinite(sample), grid


def load_catalogue(catalogue_path: Path | None = None) -> np.ndarray:
    """Boolean mask of the supplied USGS/INGENIOUS catalogue fault pixels."""
    catalogue_path = Path(catalogue_path or data_dir() / "core" / "labels.tif")
    with rasterio.open(catalogue_path) as ds:
        lab = ds.read(1)
    return (lab > 0)


def load_raster(path: Path) -> tuple[np.ndarray, Grid]:
    with rasterio.open(path) as ds:
        return ds.read(1), Grid(ds.height, ds.width, tuple(ds.transform)[:6], ds.crs.to_string(), tuple(ds.bounds))


def catalogue_systems(catalogue: np.ndarray, buffer_px: int = 6) -> np.ndarray:
    """Group catalogue pixels into fault systems (dilate, label, map back).

    Returns an int array with system id per catalogue pixel (0 = not catalogue).
    ``buffer_px=6`` is the 600 m LOSFO grouping buffer used by GEMSDOE28.
    """
    if buffer_px > 0:
        struct = np.ones((2 * buffer_px + 1, 2 * buffer_px + 1), bool)
        grown = binary_dilation(catalogue, structure=struct)
    else:
        grown = catalogue
    lab, n = label(grown)
    return np.where(catalogue, lab, 0)


def spatial_block_folds(centroids_rowcol: np.ndarray, n_folds: int = 4) -> np.ndarray:
    """Assign objects to folds by median-split spatial blocking (2x2 quadrants)."""
    rows, cols = centroids_rowcol[:, 0], centroids_rowcol[:, 1]
    rmed, cmed = np.median(rows), np.median(cols)
    q = ((rows > rmed).astype(int) * 2 + (cols > cmed).astype(int))
    if n_folds == 4:
        return q
    # fold merge for n_folds == 2
    return (q >= 2).astype(int)


def fold_masks(system_ids: np.ndarray, n_folds: int = 4) -> list[np.ndarray]:
    """Per-fold boolean masks of catalogue pixels via spatial blocking on system centroids."""
    systems = np.unique(system_ids[system_ids > 0])
    centroids = []
    for sid in systems:
        rc = np.argwhere(system_ids == sid)
        centroids.append(rc.mean(axis=0))
    centroids = np.asarray(centroids)
    folds_of_system = spatial_block_folds(centroids, n_folds)
    masks = []
    for f in range(n_folds):
        sel = set(systems[folds_of_system == f].tolist())
        masks.append(np.isin(system_ids, list(sel)))
    return masks


def distance_to_mask(mask: np.ndarray) -> np.ndarray:
    """Euclidean distance (px) from every cell to the nearest True pixel."""
    if mask.any():
        return distance_transform_edt(~mask)
    return np.full(mask.shape, np.inf, dtype=np.float64)


def footprint_stats() -> dict:
    footprint, grid = load_template()
    catalogue = load_catalogue()
    return {
        "grid": {"height": grid.height, "width": grid.width, "crs": grid.crs,
                 "transform": list(grid.transform), "bounds": list(grid.bounds)},
        "footprint_cells": int(footprint.sum()),
        "catalogue_pixels": int(catalogue.sum()),
        "catalogue_in_footprint": int((catalogue & footprint).sum()),
    }


if __name__ == "__main__":
    print(json.dumps(footprint_stats(), indent=1))
