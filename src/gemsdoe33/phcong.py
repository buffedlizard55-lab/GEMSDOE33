"""A33-R7-PHCONG: multiscale monogenic phase-congruency potential-field edges.

PC = |sum_s (even_s, oddx_s, oddy_s)| / (sum_s A_s + eps) per field, where
(even, odd) are log-Gabor bandpass quadrature (monogenic/Riesz) components at
wavelengths 4/8/16/32 px. Amplitude-invariant step-edge detector (Kovesi
local-energy principle). Orientation agreement compares the summed odd-vector
double-angle orientation between gravity and magnetics.
"""
from __future__ import annotations

import numpy as np

from . import features, grid
from .paths import CACHE

WAVELENGTHS = (4.0, 8.0, 16.0, 32.0)
SIGMA_ON_F = 0.55


def _fill(arr: np.ndarray, fp: np.ndarray) -> np.ndarray:
    a = np.asarray(arr, dtype=np.float64)
    a = np.where(np.isfinite(a), a, np.nan)
    return features._fill_nan(a.astype(np.float32), fp).astype(np.float64)


def phase_congruency(field: np.ndarray, fp: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (PC in [0,1], cos2theta, sin2theta) double-angle orientation."""
    x = _fill(field, fp)
    x = x - x[fp].mean()
    h, w = x.shape
    F = np.fft.fft2(x)
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    r = np.sqrt(fx * fx + fy * fy)
    r[0, 0] = 1.0
    ux, uy = fx / r, fy / r
    sum_e = np.zeros_like(x); sum_ox = np.zeros_like(x); sum_oy = np.zeros_like(x)
    sum_a = np.zeros_like(x)
    for lam in WAVELENGTHS:
        r0 = 1.0 / lam
        lg = np.exp(-(np.log(r / r0) ** 2) / (2 * np.log(SIGMA_ON_F) ** 2))
        lg[0, 0] = 0.0
        G = F * lg
        even = np.fft.ifft2(G).real
        ox = np.fft.ifft2(G * (-1j * ux)).real
        oy = np.fft.ifft2(G * (-1j * uy)).real
        sum_e += even; sum_ox += ox; sum_oy += oy
        sum_a += np.sqrt(even * even + ox * ox + oy * oy)
    vec = np.sqrt(sum_e**2 + sum_ox**2 + sum_oy**2)
    pc = vec / (sum_a + 1e-12)
    # odd-vector orientation (edge normal), undirected: double angle
    mag = np.sqrt(sum_ox**2 + sum_oy**2) + 1e-12
    cos_t, sin_t = sum_ox / mag, sum_oy / mag
    cos2 = cos_t**2 - sin_t**2
    sin2 = 2 * cos_t * sin_t
    return np.clip(pc, 0, 1).astype(np.float32), cos2.astype(np.float32), sin2.astype(np.float32)


def build_phcong_surface() -> tuple[np.ndarray, dict]:
    fp = grid.template_footprint()
    from .paths import CACHE_FEATURES
    fields = {}
    for key in ("tmi", "ext_TMI_up150", "iso_grav_anom"):
        fields[key] = np.asarray(np.load(CACHE_FEATURES / f"{key}.npy", mmap_mode="r"), dtype=np.float32)
    pcs, orients = {}, {}
    for key, arr in fields.items():
        cache_p = CACHE / f"phcong_{key}.npy"
        if cache_p.exists():
            pcs[key] = np.load(cache_p)
            orients[key] = np.load(CACHE / f"phcong_{key}_ori.npy")
        else:
            pc, c2, s2 = phase_congruency(arr, fp)
            ori = np.stack([c2, s2])
            np.save(cache_p, pc); np.save(CACHE / f"phcong_{key}_ori.npy", ori)
            pcs[key] = pc; orients[key] = ori
    # orientation agreement gravity vs magnetics: |cos(delta)| via double angle dot
    dc = orients["iso_grav_anom"][0] * orients["tmi"][0] + orients["iso_grav_anom"][1] * orients["tmi"][1]
    agree = np.clip(np.abs(dc), 0, 1).astype(np.float32)
    geo = np.cbrt(np.clip(pcs["tmi"], 0, None) * np.clip(pcs["ext_TMI_up150"], 0, None) * np.clip(pcs["iso_grav_anom"], 0, None))
    surface = (geo * (0.5 + 0.5 * agree)).astype(np.float32)
    surface[~fp] = 0.0
    parts = {f"pc_{k}": v for k, v in pcs.items()}
    parts["orientation_agreement"] = agree
    parts["phcong_surface"] = surface
    return surface, parts
