#!/usr/bin/env python3
"""Forensic re-verification (2026-10-26 session): why did B2 (0.2778*) win?

Reads only SHA-pinned local bytes: labels, H19-5 continuous surface, dotted
variants, and the 22-raster focus registry cache. Reports dot counts,
value alphabets, catalogue-distance distributions, set relations
(subset/pruning), and pairwise 3-px overlaps for the 9 focus sites' best.
Also measures, on the catalogue proxy only, how much weighted recall each
emission stage buys per emitted dot (DTI mechanics; NOT a leaderboard score).
"""
import json, sys
from pathlib import Path
import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt, binary_dilation

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

def load(p):
    with rasterio.open(p) as s:
        return s.read(1)

fp = np.load(ROOT / ".cache/footprint.npy")
labels = load(ROOT / "data/labels.tif") > 0
labels &= fp
dcat = distance_transform_edt(~labels)
print(f"footprint={fp.sum():,} catalogue={labels.sum():,}")

def stats(name, arr):
    a = np.nan_to_num(arr, nan=0.0)
    dots = (a > 0) & fp
    vals = np.unique(a[fp])
    d = dcat[dots]
    print(f"\n{name}: dots(>0)={dots.sum():,} on_cat={(dots & labels).sum()} "
          f"uniq_vals={len(vals)} max={a.max():.4f} "
          f"dcat: ==1:{(d<=1).sum():,} (1,2]:{((d>1)&(d<=2)).sum():,} (2,3]:{((d>2)&(d<=3)).sum():,} >3:{(d>3).sum():,}")
    return dots

h19 = load(ROOT / "data/h19_5_nan.tif")
h19d = stats("H19-5 continuous (0.1922*)", h19)
a = np.nan_to_num(h19, nan=0.0)
print("  H19-5 value deciles on footprint:", np.round(np.quantile(a[fp], [0,.5,.9,.99,.999,1]), 4))
print(f"  H19-5 mass sum={a[fp].sum():,.0f}; pixels>0.5: {((a>0.5)&fp).sum():,}; >0.1: {((a>0.1)&fp).sum():,}")

d15 = stats("dotted d1.5 (0.2477*)", load(ROOT / "data/dotted_h19_5_d1_5_nan.tif"))
d28 = stats("dotted d2.8 (0.2600*)", load(ROOT / "data/dotted_h19_5_d2_8_nan.tif"))

reg = json.loads((ROOT / "registry/focus_rasters_20261026_r3.json").read_text())
focus9 = ["G24-989f59505db1","G25-e56ea318af89","G27-5512495c6bd1","G28-8acb75e1f2cc",
          "G28-b531dae0a36f","G30-91eae1ca","G31-8acb75e1","G32-e5eb6e7e","G36-9b9ea4e6",
          "G27-h29-511898747886","G30-MSDB1-e7856ec3f14a"]
sets = {}
for r in reg["rasters"]:
    if r["id"] in focus9:
        arr = load(ROOT / (r.get("dest") or (".cache/focus_registry_20261026/" + r["id"] + ".tif")))
        sets[r["id"]] = stats(f"{r['id']} ({r.get('reported_dti')}*)", arr)

def near3(mask):
    return distance_transform_edt(~mask) <= 3.0

print("\n--- Set relations (exact pixel subsets) ---")
b2, h274 = sets["G32-e5eb6e7e"], sets["G28-8acb75e1f2cc"]
print(f"B2 subset of H27-4(G28)? {(b2 & ~h274).sum()} B2 dots outside H27-4; H27-4 dots not in B2: {(h274 & ~b2).sum():,}")
removed = h274 & ~b2
dr = dcat[removed]
print(f"  removed dots dcat: <=1:{(dr<=1).sum():,} (1,2]:{((dr>1)&(dr<=2)).sum():,} (2,3]:{((dr>2)&(dr<=3)).sum():,} >3:{(dr>3).sum():,}")
print(f"G31 == G28 H27-4? xor={(sets['G31-8acb75e1'] ^ h274).sum()}")
print(f"D2.8(local data) == G30? xor={(d28 ^ sets['G30-91eae1ca']).sum()}; == G25? xor={(d28 ^ sets['G25-e56ea318af89']).sum()}")
for k, v in sets.items():
    if k != "G32-e5eb6e7e":
        frac = (b2 & near3(v)).sum() / max(b2.sum(), 1)
        print(f"  B2 dots within 3px of {k}: {frac:.3f}")

print("\n--- G36 Anderson vs B2 family ---")
g36 = sets["G36-9b9ea4e6"]
print(f"G36 within 3px of B2: {(g36 & near3(b2)).sum()/g36.sum():.3f}; exact overlap {(g36&b2).sum():,}/{g36.sum():,}")

# DTI mechanics on catalogue proxy: score each emission against FULL catalogue
# with known-mask empty (illustrative only: measures catalogue recovery, the
# opposite of the hidden task, but shows kernel saturation economics).
sys.path.insert(0, str(ROOT / "src"))
from gems33.metric import dti_binary, dti_exact
print("\n--- Catalogue-proxy DTI (illustrative mechanics, NOT leaderboard) ---")
for name, m in [("d1.5", d15), ("d2.8", d28), ("H27-4", h274), ("B2", b2), ("G36", g36)]:
    r = dti_binary(m.astype(np.float32), labels, valid=fp, known=np.zeros_like(fp))
    print(f"{name}: DTI={r['dti']:.4f} TPw={r['TPw']:,.0f} FPw={r['FPw']:,.0f} recall_w={r['recall_w']:.3f} n={r['n_emitted']:,}")
r = dti_exact(np.nan_to_num(h19, nan=0.0).astype(np.float32), labels, valid=fp, known=np.zeros_like(fp))
print(f"H19-5 soft: DTI={r['dti']:.4f} TPw={r['TPw']:,.0f} FPw={r['FPw']:,.0f} recall_w={r['recall_w']:.3f}")
