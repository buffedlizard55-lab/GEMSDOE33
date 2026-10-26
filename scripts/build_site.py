#!/usr/bin/env python3
"""Build the static, evidence-led GitHub Pages site for GEMSDOE33.

Generates responsive, evidence-bounded static research pages for GitHub Pages:
  - index.html: Current decision and research-only artifact status.
  - executive-summary.html: Safe workflow for a future slot-cleared submission.
  - results.html: Score provenance and holdout evidence boundaries.
  - hypotheses.html: Five-candidate preregistered hypothesis slate.
  - data-sources.html: External data access and transfer limitations.
  - research.html: Complete research registry, H33-6/H33-F diagnostics, and format check records.
  - sources.html: Official verified links, data provenance, and hash verification audit.
  - irregularities.html: Log of known irregularities and their resolutions (including IR-PORTAL-01 range check).
  - standing-prompt.html: Full verbatim standing brief and project instructions.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GITHUB = "https://github.com/buffedlizard55-lab/GEMSDOE33/blob/main"
DOCS = ROOT / "docs"
DOWNLOADS = DOCS / "downloads"
ASSETS = DOCS / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)
DOWNLOADS.mkdir(parents=True, exist_ok=True)


def read_json(path: Path, default=None):
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def reg(name: str):
    return read_json(ROOT / "registry" / name)


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def local_link(path: str, label: str | None = None, css: str = "") -> str:
    return f'<a class="{esc(css)}" href="{esc(path)}">{esc(label or path)}</a>'


CSS = """
:root{color-scheme:dark;--bg:#0c1118;--panel:#151d28;--line:#2b3948;--fg:#e8eef6;
--dim:#a4b1c0;--blue:#91c8ff;--green:#8fe0a0;--amber:#ffcf70;--red:#ff9a9a;--radius:14px}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--fg);
font:16px/1.65 system-ui,-apple-system,"Segoe UI",sans-serif}a{color:var(--blue);overflow-wrap:anywhere}
.wrap{width:min(1120px,calc(100% - 36px));margin:auto}header{padding:28px 0 22px;
background:radial-gradient(1000px 440px at 15% 0%,#173150 0%,transparent 70%),#101823;
border-bottom:1px solid var(--line)}header h1{margin:0;font-size:clamp(1.65rem,4vw,2.6rem);line-height:1.15}
header p{color:var(--dim);margin:8px 0 0}.nav{display:flex;flex-wrap:wrap;gap:9px;margin-top:20px}
.nav a{padding:6px 12px;border:1px solid var(--line);border-radius:999px;text-decoration:none;color:var(--fg);font-size:.9rem}
.nav a[aria-current=page]{border-color:var(--blue);color:var(--blue);font-weight:600}main{padding:22px 0 64px}
h2{font-size:1.45rem;margin:36px 0 12px;padding-bottom:8px;border-bottom:1px solid var(--line)}
h3{font-size:1.15rem;line-height:1.35;margin-top:24px}.panel{background:var(--panel);border:1px solid var(--line);
border-radius:var(--radius);padding:18px 20px;margin:16px 0}.panel.good{border-left:5px solid var(--green)}
.panel.warn{border-left:5px solid var(--amber)}.panel.bad{border-left:5px solid var(--red)}
.panel.accent{border-left:5px solid var(--blue);background:#132030}
.hero-download{background:linear-gradient(115deg,#352025,#12253a 65%);border:2px solid #a45d63;
border-radius:18px;padding:26px;margin:22px 0;box-shadow:0 8px 30px rgba(0,0,0,0.4)}
.hero-download h2{border:0;margin:0 0 10px;padding:0;color:#ffb4b4;font-size:1.6rem}
.btn{display:inline-block;margin:8px 10px 4px 0;padding:12px 20px;border-radius:10px;background:var(--green);
color:#072412;text-decoration:none;font-weight:750;font-size:1rem;transition:transform 0.1s}
.btn:hover{transform:translateY(-1px);background:#a3f4b5}
.btn.alt{background:var(--panel);color:var(--fg);border:1px solid var(--line)}
.btn.alt:hover{border-color:var(--blue);color:var(--blue)}
.badge{display:inline-block;padding:3px 10px;border-radius:999px;
border:1px solid var(--line);color:var(--dim);font-size:.78rem;white-space:nowrap}
.badge.good{color:var(--green);border-color:#397849;background:#102818}.badge.warn{color:var(--amber);border-color:#80632b;background:#2a2010}
.badge.bad{color:var(--red);border-color:#794545;background:#281010}.badge.blue{color:var(--blue);border-color:#386088;background:#122030}
code,pre{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}
code{background:#0a1017;border:1px solid var(--line);border-radius:5px;padding:2px 5px;overflow-wrap:anywhere}
pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#0a1017;border:1px solid var(--line);border-radius:9px;
padding:14px;font-size:.88rem}table{width:100%;border-collapse:collapse;margin:16px 0;font-size:.92rem}
th,td{border:1px solid var(--line);padding:10px 12px;text-align:left;vertical-align:top}
th{background:#1b2634;font-weight:650}tr:nth-child(even) td{background:#111822}
ul,ol{padding-left:1.35rem}li{margin:.45rem 0}.muted,.small{color:var(--dim)}
.small{font-size:.86rem}.scroll{overflow-x:auto}footer{padding:24px 0 36px;border-top:1px solid var(--line);color:var(--dim);
font-size:.88rem}blockquote{margin:16px 0;padding:12px 18px;border-left:4px solid var(--blue);background:#111a25;border-radius:0 8px 8px 0}
.grid-2{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px;margin:16px 0}
.stat-box{background:#111924;border:1px solid var(--line);border-radius:12px;padding:16px;text-align:center}
.stat-box .val{font-size:2rem;font-weight:800;color:var(--blue);margin:4px 0}
.stat-box .lbl{font-size:.82rem;color:var(--dim);text-transform:uppercase;letter-spacing:.05em}
"""

NAV = [
    ("index.html", "Overview"),
    ("executive-summary.html", "How to submit"),
    ("results.html", "Results & Score Provenance"),
    ("latest-review.html", "Latest audit & gates"),
    ("hypotheses.html", "Hypotheses"),
    ("data-sources.html", "Domain Adaptation"),
    ("research.html", "Research"),
    ("sources.html", "Sources"),
    ("irregularities.html", "Irregularities"),
    ("standing-prompt.html", "Standing brief"),
]


def page(title: str, body: str, active: str) -> str:
    links = "".join(
        f'<a href="{esc(url)}"'
        f'{" aria-current=page" if url == active else ""}>{esc(label)}</a>'
        for url, label in NAV
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="GEMSDOE33: Evidence-led geothermal fault discovery research, holdout results, provenance and submission guidance. No candidate is currently slot-approved.">
<title>{esc(title)}</title><link rel="stylesheet" href="assets/site.css"></head>
<body><header><div class="wrap"><h1>GEMSDOE33 · DOE GEMS fault discovery</h1>
<p>DrivenData #306 · evidence-led research · review status 2026-10-25</p><nav class="nav" aria-label="Primary">{links}</nav></div></header>
<main class="wrap">{body}</main>
<footer><div class="wrap">Generated from repository evidence by <code>scripts/build_site.py</code>. No candidate is slot-approved and no DrivenData upload was made from this workspace. A local format audit is not scientific validation or organizer acceptance. Owner reports, measured diagnostics, model outputs and official sources are distinguished in the evidence.</div></footer>
</body></html>"""


def unique_submission_hero() -> str:
    tif = "gemsdoe33-g33-tilt-gravity-lidar-coherence-20261026-171b8b87dbf7-nan.tif"
    zip_ = "gemsdoe33-g33-tilt-gravity-lidar-coherence-20261026-171b8b87dbf7-nan.zip"
    sha = "403e6925a5b32a1ad79084636336c60dd4a4ce56aacacb66910542ace6683d44"
    note = ("GEMSDOE33 G33 tilt-gravity-lidar coherence TIFF; proxy holdout FAILED "
            "dDTI -0.0907 0/4 folds; NOT cleared to submit. id 171b8b87dbf7")
    return f"""<div class="hero-download" id="unique-submission">
<h2>Unique submission-format GeoTIFF — OK to download · NOT cleared to submit</h2>
<p><span class="badge good">OK TO DOWNLOAD</span> <span class="badge bad">NOT OK TO SUBMIT</span></p>
<p>This is a freshly generated, <b>unique</b> competition-format GeoTIFF: single-band float32, EPSG:32611,\n3730 × 3292 cells, 100 m, exact template CRS/geotransform/bounds, finite probability values in [0,1]\ninside the footprint and NaN outside. It is <b>not a copy</b> of any focus-site submission: rank\ncorrelation vs all 12 pinned registry rasters is ρ ≤ 0.0046 and at most 29.9% of its dots fall within\n3 px of any one registry raster (duplicate limits: ρ ≤ 0.90, ≤ 70%). SHA-256 of the download:\n<code>{sha}</code>.</p>
<p><b>It must not be uploaded to the competition.</b> Its catalogue-proxy holdout gate failed (confirmation\npooled ΔDTI −0.0907, 0/4 folds positive; descriptive 95% CI [−0.1210, −0.0594]); it therefore has no\ndemonstrated leaderboard benefit and no organizer receipt. Download is for inspection and reproducibility only.</p>
<p><a class="btn" href="downloads/{tif}">Download GeoTIFF (NOT cleared for upload)</a> <a class="btn alt" href="downloads/{zip_}">Download ZIP package</a></p>
<table><tbody>
<tr><th>Artifact name</th><td><code>gemsdoe33-g33-tilt-gravity-lidar-coherence-20261026</code></td></tr>
<tr><th>Suggested portal note (≤ 140 characters)</th><td><pre>{note}</pre></td></tr>
<tr><th>Scientific status</th><td><span class="badge bad">HOLDOUT FAILED · NOT CLEARED FOR SUBMISSION</span>\nCatalogue-proxy pooled candidate DTI 0.0225 vs control DTI 0.1132 (confirmation ΔDTI −0.0907, CI [−0.1210, −0.0594]). Negative result; no score is projected.</td></tr>
<tr><th>Local format audit</th><td>10/10 checks pass: one band, float32, EPSG:32611, 3730 × 3292, exact template geotransform, finite [0,1] inside footprint, NaN outside, band description \"fault probability\". Local format check only; portal acceptance is not tested and no organizer receipt exists.</td></tr>
<tr><th>Uniqueness vs registry</th><td>Screened against all 12 pinned focus-site references (GEMSDOE 24/25/27/28/30/31/32/33/36): max Spearman ρ = 0.0046 (vs GEMSDOE32 B2); max dots within 3 px = 29.9% (vs GEMSDOE27). Both limits met with wide margin — not a lane duplicate.</td></tr>
<tr><th>SHA-256</th><td><code>{sha}</code></td></tr>
</tbody></table>
<p><b>Current audit:</b> all 17 owner-mirror inputs restored and hash-verified; 121 feature channels prepared;\n3 experiments run (holdout screen + matched-random control, production build, uniqueness + format audit).\n<a href="latest-review.html">Read the byte-level forensic review and automatic gate failures</a> ·\n<a href="research/current-run-card.json" download>Download current run card (JSON)</a> ·\n<a href="executive-summary.html">Per-site best submissions and how to submit</a>.</p>
<p>Historical score claims and leaderboard values are owner/user reports, not organizer receipts, and are\nunverified here. See <a href="results.html">score provenance</a> and <a href="irregularities.html">irregularities</a>.</p>
</div>"""

def package_box() -> str:
    man = download_manifest()
    recommended = artifact_by_name(man, man.get("recommended"))
    alternate = artifact_by_name(man, man.get("alternate"))
    if not recommended:
        return '<div class="panel bad">No recommended artifact is recorded in the manifest.</div>'
    primary = download_card(man, recommended, True)
    alt = download_card(man, alternate, False) if alternate else ""
    return f"""<div class="panel" id="download" style="border-top:3px solid var(--line);">
<h3>Historical D2.8 Reference Baseline (For Comparison & Education)</h3>
<p><b>D2.8 reference only.</b> This is an owner-mirror reference emission from GEMSDOE28, not a new model and is not demonstrated to beat the official
leaderboard. Its reported 0.2600 association is owner-reported; exact score-to-file identity is not
confirmed. The top card is the recommended, NaN-outside file.</p>{primary}{alt}</div>"""


def round3_da_hgcm_hero() -> str:
    tif = "downloads/round3/gemsdoe33-r3-da-hgcm-submod-37654-20261025-a6a8552e-zeros.tif"
    zip_ = "downloads/round3/gemsdoe33-r3-da-hgcm-submod-37654-20261025-a6a8552e-zeros.zip"
    rcpt = "downloads/round3/gemsdoe33-r3-da-hgcm-submod-37654-20261025-a6a8552e-zeros.json"
    card = "research/round3-da-hgcm-run-card.json"
    sha = "2c1b648364d976bb29a52ab9045f5e2233920870f7a9670533283f00a0b1e2a8"
    sub_name = "gemsdoe33-r3-da-hgcm-37654-a6a8552e"
    sub_note = "GEMSDOE33 H33-R3-3 37654d [0,1] zeros; unique vs 201 9-site dl; gated (r13-lattice-s5/proxy); id a6a8552e"
    return f"""<div class="hero-download" id="round3-da-hgcm">
<h2>Round-3 H33-R3-3 (DA-LinearVC-Submod) GeoTIFF — Format [0, 1] &amp; 9-Site Uniqueness PASS · Live Slot GATED (verdict: negative · DO NOT AUTO-SUBMIT)</h2>
<p><span class="badge good">OK TO DOWNLOAD · 15/15 FORMAT [0, 1] PASS</span> <span class="badge good">HOLDOUT-DTI 8/8 FOLDS PASS (0.114084)</span> <span class="badge good">UNIQUE VS ALL 204 9-SITE PUBLISHED TIFS</span> <span class="badge warn">LIVE SLOT GATED (verdict: negative)</span></p>
<p><b>Unique Round-3 artifact (zero NaNs anywhere, <code>0.0</code> outside footprint matching official reference Cell 19):</b>
<code>37,654</code> binary dots in <code>[0.0, 1.0]</code>, <code>EPSG:32611</code>, <code>3730 × 3292</code>, <code>0</code> on-catalogue pixels.
On fresh independent confirmation seeds (<code>33, 34</code>, <code>22,733</code> withheld positives, <code>gems57-pooled-hide-v2</code>), frozen <b>H33-R3-3</b> reached <b>HOLDOUT-DTI = 0.114084</b> (20 km spatial-block 95% CI <code>[0.096891, 0.132095]</code>), beating fold-rebuilt matched controls in <b>8/8 folds</b> (<code>+0.066412</code> vs <code>CTRL-RIDGE-B2</code>, <code>+0.027924</code> vs <code>CTRL-GBDT</code>) and improving independent off-catalogue USGS SGMC fault recovery by <b>+25.0%</b> (<code>0.120202</code> vs <code>0.096132</code>).</p>
<p><b>Why live competition slot promotion remains GATED (<code>verdict: negative</code>, <code>0</code> slots spent):</b> Although H33-R3-3 passes uniqueness across <b>all 204 published submission GeoTIFFs of GEMSDOE24..36</b> (max <code>|ρ| = 0.0650 ≤ 0.90</code>, max 3-px overlap = <code>0.5265 ≤ 0.70</code>), literal unexempted subdirectory scanning flags <code>GEMSDOE24/inputs/calibration/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif</code> (a 206,895-dot synthetic spacing-5 calibration lattice whose 3-px disks cover <b>99.87%</b> of the GeoDAWN footprint: <code>0.9997 &gt; 0.70</code>). Per Parallel-Run Protocol Rule 6, do not upload without explicit human selector clearance.</p>
<p><a class="btn" href="{tif}">Download H33-R3-3 [0, 1] GeoTIFF (148 KB)</a> <a class="btn alt" href="{zip_}">Download Single-TIFF .zip (117 KB)</a> <a class="btn alt" href="{rcpt}">Validator Receipt JSON</a> <a class="btn alt" href="{card}">Official Run Card JSON</a></p>
<table><tbody>
<tr><th>Unique submission name</th><td><code>{sub_name}</code></td></tr>
<tr><th>Suggested note (105 / 140 chars)</th><td><code>{sub_note}</code></td></tr>
<tr><th>GeoTIFF SHA-256</th><td><code>{sha}</code></td></tr>
</tbody></table>
</div>"""


def a33_r2_csht_hero() -> str:
    tif = "downloads/gemsdoe33-a33-r2-csht-transfer-37654-20261026-0b78c04d5fad-zeros.tif"
    zip_ = "downloads/gemsdoe33-a33-r2-csht-transfer-37654-20261026-0b78c04d5fad-zeros.zip"
    nan_tif = "downloads/gemsdoe33-a33-r2-csht-transfer-37654-20261026-0b78c04d5fad-nan.tif"
    rcpt = "downloads/receipt-gemsdoe33-a33-r2-csht-transfer-37654-20261026-0b78c04d5fad.json"
    card = "data/a33_r2_run_card_20261026.json"
    sha = "14ab452c22aaf07444cd02e589fce4627d682e99f44c63e78dc1383955e0c602"
    sub_name = "gemsdoe33-a33-r2-csht-transfer-37654-20261026-0b78c04d5fad"
    sub_note = "GEMS33 A33-R2-CSHT: cover+hydrothermal transfer + 300m CELF 37654d | gate DUPLICATE | 0b78c04d5fad"
    return f"""<div class="hero-download" id="a33-r2-csht">
<h2>2026-10-26 A33-R2-CSHT GeoTIFF — OK TO DOWNLOAD: YES · OK TO SUBMIT: NO — DO NOT SPEND A WEEKLY SLOT (verdict: duplicate)</h2>
<p><span class="badge good">OK TO DOWNLOAD: YES · STRICT [0, 1] FORMAT PASS</span> <span class="badge good">HOLDOUT-DTI 8/8 FOLDS PASS (0.136716 / 0.131169)</span> <span class="badge good">FINAL DOTS UNIQUE VS 24 RASTERS</span> <span class="badge bad">OK TO SUBMIT: NO (surface duplicate guard)</span></p>
<p><b>Unique 2026-10-26 A33-R2-CSHT submission-format GeoTIFF (strict <code>[0.0, 1.0]</code> range, <code>0.0</code> outside footprint, fixes <code>IR-33-LIDAR-VOID-01</code> <code>260,733</code> phantom void scarps):</b>
<code>37,654</code> binary dots in <code>[0.0, 1.0]</code>, <code>EPSG:32611</code>, <code>3730 × 3292</code>, <code>0</code> on-catalogue pixels, <code>50/50</code> feature leakage canaries passed (<code>max AUC = 0.7685 ≤ 0.90</code>).
On buffered whole-segment holdout (<code>60,988</code> withheld positives, <code>gems-segment-pooled-v1</code>), <b>A33-R2-CSHT</b> beat regional control <code>B1</code> in <b>8/8 folds</b> across both quadrant screen (<b>HOLDOUT-DTI = 0.136716</b> vs <code>0.112418</code>, paired <code>Δ = +0.024298 [+0.012427, +0.035833]</code>, <code>4/4</code> folds) and frozen orthogonal diagonal-wedge confirmation (<b>HOLDOUT-DTI = 0.131169</b> vs <code>0.115122</code>, paired <code>Δ = +0.016047 [+0.003817, +0.028030]</code>, <code>4/4</code> folds).</p>
<p><b>Why OK TO SUBMIT is NO (<code>verdict: duplicate</code>, <code>0</code> slots spent):</b> Final submodular <code>CELF-300m</code> dots pass uniqueness against <b>all 21 pinned focus+local rasters and all 3 Round-3 rasters</b> (max <code>|ρ| = 0.0416 ≤ 0.90</code>, max 3-px overlap = <code>69.34% ≤ 70%</code>; <code>35.86%</code> vs GEMSDOE32 B2). However, pre-placement continuous HGB surface peaks exceeded <code>70%</code> 3-px overlap vs 2026-10-25 sibling HGB <code>G30-MSDB1</code> (<code>91.11%</code> unthinned / <code>77.82%</code> matched-37k NMS; owner-reported <code>0.1462</code>). Per Parallel-Run Protocol Rule 1 &amp; Rule 6, this artifact is downloadable for research/reproducibility only and <b>must not be uploaded to a weekly competition slot</b>.</p>
<p><a class="btn" href="{tif}">Download A33-R2-CSHT [0, 1] GeoTIFF (808 KB)</a> <a class="btn alt" href="{zip_}">Download Single-TIFF .zip (168 KB)</a> <a class="btn alt" href="{nan_tif}">NaN-outside Twin .tif</a> <a class="btn alt" href="{rcpt}">Validator Receipt JSON</a> <a class="btn alt" href="{card}">A33-R2 Run Card JSON</a></p>
<table><tbody>
<tr><th>Unique submission name</th><td><code>{sub_name}</code></td></tr>
<tr><th>Suggested note (98 / 140 chars)</th><td><code>{sub_note}</code></td></tr>
<tr><th>GeoTIFF SHA-256</th><td><code>{sha}</code></td></tr>
</tbody></table>
</div>"""


def dpps_hero(*, include_b2_score: bool = False) -> str:
    card = read_json(ROOT / "evidence" / "dpps_run_card_20261026.json")
    if not card:
        return ""
    h = card["holdout_dti"]
    s, c = h["screen"], h["confirmation"]
    u = card["correlation_overlap_vs_registry"]
    tif = f"downloads/{card['file']}"
    zip_ = f"downloads/{card['zip']}"
    rcpt = "downloads/receipt-gemsdoe33-dpps-dipproj-persistence-37654-20261026-111ae96bb235.json"
    b2_line = (
        "<p><b>Context:</b> the highest owner-reported historical value (GEMSDOE32 B2, "
        "0.2778, not organizer-confirmed) is a deletion-only pruning of H27-4 reproduced "
        "pixel-exactly in this repo; it is not re-submittable under the duplicate gate. "
        "DPPS makes <b>no claim to beat it</b>.</p>"
        if include_b2_score else ""
    )
    return f"""<div class="hero-download" id="dpps">
<h2>★ NEWEST UNIQUE TIF (2026-10-26, G33-DPPS) — ✅ OK TO DOWNLOAD: YES · 🛑 OK TO SUBMIT: NO — DO NOT SPEND A WEEKLY SLOT (verdict: negative)</h2>
<p><span class="badge good">✅ OK TO DOWNLOAD: YES</span> <span class="badge bad">🛑 OK TO SUBMIT: NO</span> <span class="badge good">STRICT [0, 1] WHOLE-ARRAY PASS · 0 NaN</span> <span class="badge good">UNIQUE VS 25 REGISTRY RASTERS (surface + final dots)</span> <span class="badge bad">HOLDOUT GATE FAILED vs B1 (1/4 + 0/4 folds)</span></p>
<p><b>What this file is:</b> a genuinely new, deterministic <b>dip-projected persistence-scarp</b> emission
(zero learned weights, zero catalogue/H19-5/B2 pixels in its surface): ≥1.5 km along-strike LiDAR-scarp
persistence fused with gravity support warped updip by <code>z·cot60°</code> along the depth-to-basement
gradient, placed by 300 m CELF. <code>37,654</code> binary dots, single-band <code>float32</code>,
<code>EPSG:32611</code>, <code>3730 × 3292</code>, values exactly <code>{{0.0, 1.0}}</code> with
<code>0.0</code> outside the footprint — the whole array is finite in <code>[0, 1]</code>, so this primary
<code>-zeros.tif</code> cannot trigger the portal error <i>“Predicted values must be in range [0, 1]”</i>
from NaN handling. <code>0</code> dots on the catalogue; <code>9/9</code> leakage canaries pass
(max two-sided AUC <code>{card['leakage_canary']['max_two_sided_auc']:.4f} ≤ 0.90</code>).</p>
<p><b>Holdout evidence (HOLDOUT-DTI, <code>gems-segment-pooled-v1</code>, 60,988 withheld positives — not a competition score):</b>
screen <b>{s['candidate']:.6f}</b> [{s['candidate_95pct_ci'][0]:.6f}, {s['candidate_95pct_ci'][1]:.6f}] vs
B1_regional <code>{s['b1_regional']:.6f}</code> (paired Δ <code>{s['paired_delta_vs_b1']:+.6f} [{s['paired_delta_vs_b1_95pct_ci'][0]:+.6f}, {s['paired_delta_vs_b1_95pct_ci'][1]:+.6f}]</code>, {s['fold_wins_vs_b1']} folds);
confirmation <b>{c['candidate']:.6f}</b> vs B1 <code>{c['b1_regional']:.6f}</code>
(Δ <code>{c['paired_delta_vs_b1']:+.6f} [{c['paired_delta_vs_b1_95pct_ci'][0]:+.6f}, {c['paired_delta_vs_b1_95pct_ci'][1]:+.6f}]</code>, {c['fold_wins_vs_b1']}).
The mechanism itself is validated against its pixel-scarp ablation (screen Δ vs CTRL-PIXEL
<code>{s['paired_delta_vs_ctrl']:+.6f} [{s['paired_delta_vs_ctrl_95pct_ci'][0]:+.6f}, {s['paired_delta_vs_ctrl_95pct_ci'][1]:+.6f}]</code>, 4/4 folds),
but the system does <b>not</b> beat the supervised incumbent, so per the preregistered gate it must not spend a slot.</p>
<p><b>Uniqueness (Parallel-Run Protocol, both stages):</b> pre-placement surface max |ρ| =
<code>{u['surface_max_abs_spearman']:.4f}</code>, max preview dots within 3 px =
<code>{100*u['surface_max_3px_overlap']:.2f}%</code> (limit 70%; nearest is the local Round-3 raster — slim margin, flagged);
final dots max |ρ| = <code>{u['final_dots_max_abs_spearman']:.4f}</code>, max within 3 px =
<code>{100*u['final_dots_max_3px_overlap']:.2f}%</code>; only <code>{100*u['vs_G32_B2_final_3px']:.1f}%</code> of DPPS dots lie within 3 px of GEMSDOE32 B2 dots. Not a copy of any previous submission.</p>
{b2_line}
<p><a class="btn" href="{tif}">⬇ Download DPPS [0, 1] GeoTIFF ({card['file']})</a> <a class="btn alt" href="{zip_}">Single-TIFF .zip</a> <a class="btn alt" href="{rcpt}">Validator Receipt JSON</a> <a class="btn alt" href="data/dpps_run_card_20261026.json">DPPS Run Card JSON</a></p>
<table><tbody>
<tr><th>Unique submission name</th><td><code>{card['submission_name']}</code></td></tr>
<tr><th>Suggested note ({card['note_characters']} / 140 chars) — for provenance only; do not upload</th><td><code>{esc(card['note'])}</code></td></tr>
<tr><th>GeoTIFF SHA-256 (zeros primary)</th><td><code>{card['raster_sha256']}</code></td></tr>
<tr><th>Decision</th><td><b>✅ OK TO DOWNLOAD: YES (research/reproducibility) · 🛑 OK TO SUBMIT: NO</b> — failed gates: <code>{", ".join(card['failed_gates'])}</code>. No DrivenData upload was made from this workspace; slots spent: 0.</td></tr>
</tbody></table>
</div>"""


def build_index() -> str:
    body = f"""{dpps_hero()}
{a33_r2_csht_hero()}
{round3_da_hgcm_hero()}
{unique_submission_hero()}
<h2>Project decision</h2>
<div class="panel bad"><b>No real competition submission is approved.</b> The top-ranked candidate H33-6 failed the recorded spatial proxy gate (P1 mean ΔDTI −0.00273732; 2/4 folds positive). The evidence is conditional because the fixed H19-5 baseline surface was not regenerated per fold; private expert labels were not available. No upload was made and no score is predicted.</div>
<h2>What can be concluded about the cited scores?</h2>
<p>The values supplied in the project brief—including the claimed H27-4 0.2708 and the 0.3195 target—are not organizer-confirmed by a submission receipt in this checkout. The GEMSDOE28 owner page was previously recorded as calling H27-4 unscored/research-only. Therefore this repo cannot explain why H27-4 received that score as an established fact, pair a local raster with a score, or claim a new candidate beats it. Historical owner-site values are prior-art leads, not independent validation.</p>
<p>Do not refresh or copy the official leaderboard without the permission/API described in the project's terms review. See <a href="results.html">score provenance</a> for the evidence boundary and <a href="irregularities.html">irregularities</a> for known conflicts.</p>
<h2>Hypothesis and experiment status</h2>
<p>The five-item preregistered slate and prior-art review are documented in <a href="hypotheses.html">Ranked hypotheses</a>. H33-6 was tested as the top runnable candidate; it failed. Other candidate concepts are blocked or unvalidated and should not be treated as results. The run card and a negative result are recorded in the repository.</p>
<h2>Our operating values</h2>
<div class="grid-2"><div class="panel accent"><h3>Maximize P(Win)</h3><p>Prefer evidence that predicts useful hidden-fault detection, not a download or a hopeful score projection. No slot until a fresh, leakage-audited holdout improves over a matched baseline.</p></div><div class="panel accent"><h3>Own the Outcome</h3><p>Make failures visible, preserve provenance, correct misleading pages, and distinguish local format validation from scientific validity and organizer acceptance.</p></div></div>
<h2>Use the artifact safely</h2>
<p>The existing H33-6 TIFF is downloadable for inspection/reproducibility only. <b>It is not okay to upload.</b> The historical D2.8 mirror artifacts are educational references only and are not a new strategy or verified score-file pairing. Read <a href="executive-summary.html">the executive summary</a> before using any artifact.</p>
"""
    return page("GEMSDOE33 · Evidence-led fault discovery", body, "index.html")

def build_exec() -> str:
    tif = "gemsdoe33-g33-tilt-gravity-lidar-coherence-20261026-171b8b87dbf7-nan.tif"
    note = ("GEMSDOE33 G33 tilt-gravity-lidar coherence TIFF; proxy holdout FAILED "
            "dDTI -0.0907 0/4 folds; NOT cleared to submit. id 171b8b87dbf7")
    rows = "\n".join(
        f"<tr><td>{site}</td><td><code>{name}</code></td><td>{score}</td><td>{status}</td></tr>"
        for site, name, score, status in (
            ("GEMSDOE24", "h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan", "0.2477",
             "Owner-reported; no organizer score/file receipt in this repo"),
            ("GEMSDOE25", "dotted-h19-5-d2-8-20261002-e56ea318af89-nan", "0.2600",
             "Owner-reported; same 44,090-dot dotted-h19-5 family as GEMSDOE24/GEMSDOE30"),
            ("GEMSDOE27", "topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan", "0.2449",
             "Owner-reported; no organizer score/file receipt in this repo"),
            ("GEMSDOE28", "h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan", "0.2710",
             "Owner-reported; GEMSDOE28 page labels H27-4 unscored/research-only; H27-4 at 0.2708 is also listed"),
            ("GEMSDOE30", "d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca-nanoutside", "0.2600",
             "Owner-reported; shares the 44,090-dot dotted-h19-5 prediction with GEMSDOE24/GEMSDOE25"),
            ("GEMSDOE31", "h27-4-solo-d28-20261004-8acb75e1-nan", "0.2708",
             "Owner-reported; same 40,199-dot prediction family as GEMSDOE28 H27-4"),
            ("GEMSDOE32", "h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros", "0.2778",
             "HIGHEST owner-reported focus-site value; reproduced pixel-exactly as deletion-only pruning of GEMSDOE28 H27-4 (40,199 → 37,654 dots; Spearman 0.9676 vs H27-4, 100% dot overlap within 3 px) — copying it would trip the lane duplicate gate"),
            ("GEMSDOE33", "h33d-analog-tip-stepover-r30-20261004-cb490425926e", "0.2632",
             "Owner-reported; local research artifact, no organizer receipt in this repo"),
            ("GEMSDOE36", "anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros", "0.2750",
             "Owner-reported; filename references a PINN but no geothermal-discovery mechanism is established by local evidence"),
        )
    )
    body = f"""{dpps_hero(include_b2_score=True)}
{a33_r2_csht_hero()}
{round3_da_hgcm_hero()}
<h2>Executive summary — per-site best submissions and how to submit</h2>
<div class="panel bad"><b>Current status: no file in this project is approved for a competition slot, and no DrivenData upload was made from this workspace.</b> The newest unique file (G33-DPPS, above) is <b>✅ OK TO DOWNLOAD / 🛑 OK TO SUBMIT: NO</b>. Every historical file in the table below has already been spent as a submission (owner-reported) or is a duplicate of one — re-uploading any of them wastes a slot and cannot produce a new score. <b>There is currently no “submit this one” file; that is the honest, gate-driven answer.</b></div>

<h3>Exactly how a submission is made (when a future candidate passes every gate)</h3>
<ol>
<li><b>Check the banner at the top of this page.</b> Submit only if it says <code>OK TO SUBMIT: YES</code> for that exact filename. Today it says <b>NO</b> for every file on this site.</li>
<li><b>Download the primary <code>-zeros.tif</code></b> (or its single-TIFF <code>.zip</code>) and do not rename/edit/re-save it. The zeros variant is finite in [0, 1] over the <i>whole array</i> (0.0 outside the footprint, zero NaNs), which is the variant that cannot trip the portal message <i>“Predicted values must be in range [0, 1]”</i>. A <code>-nan.tif</code> twin (NaN outside, per the official-text wording) is kept only as an alternative if the live form rejects zeros.</li>
<li><b>Verify the bytes you downloaded</b> (optional, 10 seconds): SHA-256 must equal the hash in the banner table, and <code>python scripts/validate_submission.py --submission FILE.tif --template sample_submission.tif --strict-zero-outside</code> must print <code>"pass": true</code> (1 band, float32, EPSG:32611, 3730 × 3292, template transform, min 0.0 / max 1.0).</li>
<li><b>Open the DrivenData submission form</b> (competition 306 → <i>New submission</i>): choose the <code>.tif</code> file (single-band GeoTIFF, or a .zip containing exactly one GeoTIFF, matching the format CRS/shape/geotransform).</li>
<li><b>Paste the note exactly as given</b> in the banner table (≤ 140 characters) into the <i>Note</i> box, e.g. the DPPS provenance note above — the note is how you tell submissions apart later.</li>
<li><b>Confirm a weekly slot is available</b> on the submission page, then submit once. Do not submit the same dots twice under different names.</li>
<li><b>Save the organizer receipt/score screenshot</b> and add it to the repo: only an organizer receipt converts an owner-reported number into an ORGANIZER-CONFIRMED score. Until then every historical score on this page stays labelled owner-reported.</li>
</ol>
<div class="panel warn"><b>No human inspector is in this loop:</b> leakage canaries, spatially blocked holdout vs matched controls, surface+final-dots duplicate guards, and the saved-byte format audit all run automatically in-project (<code>scripts/run_dpps_campaign.py</code>, <code>scripts/validate_submission.py</code>). The only human step is the account-holder clicking upload in step 4–6, because this workspace has no DrivenData auth.</div>

<h3>Which focus-site submission is the best to submit?</h3>
<p>Among the nine focus sites (GEMSDOE 24, 25, 27, 28, 30, 31, 32, 33, 36), the highest owner-reported value is <b>GEMSDOE32 h33-h33-2-b2-...-zeros at 0.2778</b>, followed by GEMSDOE36 at 0.2750 and GEMSDOE28 h36-1 at 0.2710. <b>Every one of these values is an owner/user report: none is backed by an organizer submission-page receipt in this repository, and none is organizer-confirmed.</b> They are leads, not proven scores.</p>
<div class="scroll"><table><thead>
<tr><th>Site</th><th>Best owner-reported submission</th><th>Reported score (owner-reported, not organizer-confirmed)</th><th>Submit this now?</th><th>Status / caveat</th></tr>
</thead><tbody>
{rows}
</tbody></table></div>

<h3>Why did GEMSDOE32 B2 score 0.2778 — and can we beat it?</h3>
<p>We reproduced B2 pixel-exactly from the GEMSDOE28 H27-4 owner raster: it deletes 2,545 dots within 2 px of the catalogue and adds nothing (40,199 → 37,654 dots; Spearman ρ = 0.9676 vs H27-4; 100% of B2 dots within 3 px of H27-4 dots). Under the competition DTI (α=0.2 per false positive, β=0.8 per missed truth, 300 m kernel), every isolated prediction dot costs roughly 1 unit of weighted false-positive mass unless it lies within 300 m of a truth pixel, while dense clusters of dots share the same truth credit. Removing low-credit, catalogue-adjacent dots can therefore raise DTI even though no new fault is found: the most plausible mechanism is FP-mass reduction, not discovery. That is an inference from audited bytes, not proof, and no organizer receipt ties 0.2778 to B2's exact bytes.</p>
<p>Can we beat it? Not demonstrated here. Our new unique candidate G33-HA (tilt ≈ 0 × gravity edge × LiDAR coherence, sparse off-catalogue dots) failed the catalogue-proxy holdout (confirmation ΔDTI −0.0907, 0/4 folds; CI [−0.1210, −0.0594]) and is explicitly negative. No score above 0.2778 — or above any leaderboard value — is projected or claimed. Conflicting leader values (0.3195 / 0.4413) are unverified in this checkout; per the DrivenData Terms of Use this workspace does not scrape or refresh the leaderboard.</p>

<h3>Research GeoTIFF (do not upload)</h3>
<p><b>It must not be uploaded to the competition.</b> Its catalogue-proxy holdout gate failed (confirmation ΔDTI −0.0907, 0/4 folds) and no organizer receipt exists.</p>
<p><a class="btn alt" href="downloads/{tif}">Download unique GeoTIFF — NOT CLEARED FOR SUBMISSION</a></p>
<ul><li>Artifact: <code>gemsdoe33-g33-tilt-gravity-lidar-coherence-20261026-171b8b87dbf7</code></li><li>SHA-256: <code>403e6925a5b32a1ad79084636336c60dd4a4ce56aacacb66910542ace6683d44</code></li><li>Note (≤140 characters): <code>{note}</code></li><li>Verdict: <b>negative</b> — proxy holdout failed; format-valid and unique vs all 12 pinned registry rasters, but not cleared for a competition slot. No organizer receipt exists.</li></ul>

<h2>Steps for a future approved candidate</h2>
<ol><li>Require a passing automatic evidence gate <b>and</b> a separate selector decision within the verified weekly cap. A <b>promote</b> research verdict alone is not slot clearance; if either is missing, do not upload.</li><li>Download the exact named single-band GeoTIFF (or a ZIP with exactly one GeoTIFF) and keep it unchanged.</li><li>Run <code>python scripts/validate_submission.py --submission PATH --template PATH</code> against the official/sample template available in the local cache. Review CRS, shape, transform, dtype, footprint values, and outside-footprint handling against current official instructions.</li><li>In the authenticated DrivenData submission form, select the TIFF, enter a distinct name and concise note (portal limit: concise, e.g. ≤ 140 characters in this project), and submit only if a competition slot is available and the submission rules permit it.</li><li>Save the organizer receipt. Only that receipt can confirm a score/file association; report the organizer score separately from holdout diagnostics.</li></ol>
<div class="panel warn"><b>Outside-footprint values:</b> the official wording requires null/NaN outside the bounds. Our -nan.tif follows that wording; a -zeros.tif twin is kept only as a troubleshooting alternative because the previously reported portal range error ("Predicted values must be in range [0, 1]") was never confirmed by the organizer and its cause is unknown. Follow the live official format instructions rather than assuming either convention is accepted.</div>
<h3>What is required before the next competition submission</h3><ul><li>New spatially blocked holdout where every catalogue-derived feature, including baseline/pseudo-label surfaces, is rebuilt using fold-visible data only.</li><li>Feature-by-feature leakage canary; investigate AUC &gt; 0.90 before trusting a signal.</li><li>Predeclared experiment, matched budget/control, uncertainty interval, and uniqueness screen against accessible registry rasters.</li><li>Exact format check from source inputs plus saved-byte re-open; current validator requires installed rasterio/numpy.</li><li>All scientific/format inspections must be run automatically in-project. Only the final authorized account upload is outside this project; no human scientific inspector is required by the project gate. This workspace has no DrivenData auth and cannot upload or retrieve a receipt.</li></ul>
"""
    return page("Executive summary & submission guidance · GEMSDOE33", body, "executive-summary.html")
    return page("Executive summary & submission guidance · GEMSDOE33", body, "executive-summary.html")

def build_results() -> str:
    body = f"""<h2>Results, score claims, and evidence boundaries</h2>
<p><a href="latest-review.html">New: twelve-raster byte-level forensic review, GEMSDOE32 pruning recipe and automatic gate status</a> · <a href="{GITHUB}/knowledge/13_focus_forensics_g32_proof_and_a33_r2_results_20261026.md">2026-10-26 21-raster forensic proof &amp; A33-R2-CSHT report</a>.</p>
<div class="panel bad"><b>No organizer-confirmed submission result is available in this checkout.</b> The leaderboard values in the user's research brief and owner-maintained GEMSDOE pages are historical reports, not organizer receipts linking scores to raster bytes. Do not infer or present projected scores.</div>
<h3>2026-10-26 G33-DPPS local holdout (unique both stages; beats ablation, fails vs B1 — negative)</h3>
<p><b>HOLDOUT-DTI</b> (<code>gems-segment-pooled-v1</code>, <code>60,988</code> withheld catalogue pixels): quadrant screen DPPS <code>0.095407</code> (95% CI <code>[0.084971, 0.106370]</code>) vs <code>B1_regional = 0.111285</code>, paired <code>Δ = −0.015878 [−0.028932, −0.002121]</code>, <b>1/4 folds</b>; diagonal-wedge confirmation <code>0.096015</code> (<code>[0.085295, 0.106776]</code>) vs <code>B1_regional = 0.114619</code>, paired <code>Δ = −0.018604 [−0.031369, −0.005925]</code>, <b>0/4 folds</b>. Against its own pixel-scarp ablation at identical CELF emission, DPPS won <b>8/8 folds</b> (screen <code>Δ = +0.022590 [+0.016578, +0.028826]</code>; confirmation <code>Δ = +0.023079 [+0.016931, +0.029462]</code>), so persistence + dip-projection carry real signal, but the preregistered system gate (beat B1) failed on both splits. Surface and final dots are unique vs all 25 registry rasters (final max 3-px overlap <code>44.62%</code>; <code>24.0%</code> vs GEMSDOE32 B2). Verdict: <b>negative (✅ OK TO DOWNLOAD · 🛑 OK TO SUBMIT: NO)</b>. Evidence: <a href="{GITHUB}/evidence/dpps_experiment_20261026.json">experiment JSON</a> · <a href="data/dpps_run_card_20261026.json">run card</a> · <a href="{GITHUB}/knowledge/15_dpps_results_20261026.md">interpretation</a>.</p>
<h3>2026-10-26 A33-R2-CSHT local holdout (8/8 fold wins; surface duplicate-stopped)</h3>
<p><b>HOLDOUT-DTI</b> (<code>gems-segment-pooled-v1</code>, <code>60,988</code> withheld catalogue pixels): primary quadrant screen <code>0.136716</code> (95% CI <code>[0.119069, 0.154424]</code>) vs <code>B1_regional = 0.112418</code> (<code>0.113244</code> recorded), paired <code>Δ = +0.024298 [+0.012427, +0.035833]</code>, <b>4/4 folds positive</b>; frozen orthogonal diagonal-wedge confirmation <code>0.131169</code> (<code>[0.115241, 0.146693]</code>) vs <code>B1_regional = 0.115122</code>, paired <code>Δ = +0.016047 [+0.003817, +0.028030]</code>, <b>4/4 folds positive</b>. Among 2026-10-25 sibling focus uploads (owner/user-reported, not organizer-confirmed), <code>G27-h29</code> reported <code>0.2190</code>, <code>G30-MSDB1</code> <code>0.1462</code>, <code>G24-gvc1</code> <code>0.0859</code>, <code>G25-h66</code> <code>0.0742</code>, and <code>G28-s18</code> <code>0.0217</code>, while <code>GEMSDOE32</code> <code>H33-2-B2</code> (<code>37,654</code> dots = <code>H27-4</code> minus <code>2,545</code> <code>1 &lt; d_cat ≤ 2 px</code> boundary-halo dots) remains the highest owner-reported focus-site value at <code>0.2778</code>. Because <code>A33-R2-CSHT</code> pre-placement surface peaks converged with <code>G30-MSDB1-e7856ec3f14a</code> (<code>91.11%</code> unthinned / <code>77.82%</code> matched-37k NMS 3-px overlap &gt; <code>70%</code>), its promotion verdict is <code>duplicate</code> (<b>OK TO DOWNLOAD: YES · OK TO SUBMIT: NO</b>).</p>
<h3>H27-4 claim (0.2708)</h3><p>The repo records that the linked GEMSDOE28 owner page labels H27-4 unscored/research-only. No authenticated organizer receipt proves the quoted 0.2708 or associates it with the raster. Therefore the question “why did it score 0.2708?” has no verified premise here. At most, the owner report suggests a dotted H19-5 baseline with d=2.8; its mechanism is not confirmed as the cause of any official score.</p>
<h3>H33-6 local holdout</h3><p>HOLDOUT-DTI (four spatial folds; 60,988 withheld catalogue pixels total): pooled candidate DTI 0.112486 versus pooled control DTI 0.114669, pooled ΔDTI −0.002183. The unweighted mean of four fold deltas is −0.002737 (2/4 positive). A descriptive Student-t 95% interval across those fold deltas is [−0.015020, +0.009546], df=3; it is imprecise with n=4, conditional, and does not estimate uncertainty against private expert truth. P2 SGMC proxy ΔDTI is +0.00015900. These are local proxy diagnostics, not competition scores. The upstream H19-5 baseline was not re-derived per fold, and no independent confirmation was run.</p>
<p>Evaluator source: <code>src/gemsdoe33/metric.py</code>, function <code>dti_binary</code>; evidence does not record a semantic evaluator version. Record SHA-256 in the run card, rather than inventing a version label. See <a href="research.html">full run and caveats</a>.</p>
<h3>Historical context and provenance</h3><p>Prior owner-reported results are retained as historical context in <code>registry/score_ledger.json</code>; they are not a live feed and are not organizer-confirmed. The user's listed scores are not independently reproduced here. Official leaderboard access is not refreshed automatically. No result above can establish a higher-than-0.2778 or higher-than-0.3195 submission.</p>
"""
    return page("Results & score provenance · GEMSDOE33", body, "results.html")

def build_hypotheses() -> str:
    body = f"""<h2>Ranked geological hypothesis slate</h2>
<div class="panel warn"><b>Current planning slate:</b> four additional analog-transfer hypotheses are ranked in <a href="latest-review.html">the latest review</a>. All require independent official field labels and are blocked, not viable. The historical slate below is retained without rerunning failed arms.</div>
<p>The frozen 2026-10-04 slate in <a href="https://github.com/buffedlizard55-lab/GEMSDOE33/blob/main/knowledge/07_hypothesis_slate_20261004.md">knowledge/07_hypothesis_slate_20261004.md</a> contains five candidates ranked qualitatively by expected improvement and cost. It explicitly avoids numeric score projections. These ranks are prior beliefs, not scores.</p>
<table><thead><tr><th>Rank</th><th>Hypothesis / layers and signature</th><th>Why it might reveal omitted faults</th><th>Difference / cost / status</th></tr></thead><tbody>
<tr><td>1</td><td><b>H33-6 cross-physics edge-normal consensus.</b> GeoDAWN bands 14 TMI and 13 isostatic gravity gradients, corroborated by band 15 basement depth or band 17 conductivity edge; aligned normals at 2-pixel Gaussian scale.</td><td>Buried basin-bounding/intrabasin structures may create aligned magnetic/gravity transitions without a surface scarp; contacts can mimic this signal.</td><td>Joint normal agreement plus corroboration and matched-budget reallocation; not just single-layer gradients. Low–medium cost. Tested once; conditional P1 gate failed. Do not upload.</td></tr>
<tr><td>2</td><td><b>H33-7 field-verified BRIDGE transfer.</b> DOE GDR #1682 LiDAR fault picks plus common GeoDAWN features.</td><td>Independent field picks could test structures absent from the regional compilation, if overlaps and label policies are resolved.</td><td>Named-field transfer is not implemented. Medium–high cost; blocked until official bytes, schema, CRS, licence and coverage are audited.</td></tr>
<tr><td>3</td><td><b>H33-8 Gabbs Valley 3D fault-surface analogue.</b> USGS ScienceBase item 62b21845d34e74f0d80f17aa with shared geophysical layers.</td><td>Subsurface interpretation may expose buried structures beyond surface fault traces.</td><td>Tests shallow projection of mapped surfaces, not only line picks. Medium cost; blocked pending payload retrieval/schema audit.</td></tr>
<tr><td>4</td><td><b>H33-9 ComCat focal-mechanism orientation.</b> USGS event focal mechanisms (strike/dip/rake) with potential-field edges.</td><td>Mechanism-plane orientation can test active structure orientation, but nodal-plane ambiguity and sparse events matter.</td><td>Different from earthquake-density proximity; carried-forward from earlier H33-2, so not novel. Medium cost; no full extract staged.</td></tr>
<tr><td>5</td><td><b>H33-10 signed strain-lobe / conductor edge.</b> GeoDAWN bands 7/8 strain, 17 conductivity, 15 basement depth and 18 gravity gradient.</td><td>Asymmetric strain across conductive/basement edge may flag concealed deformation, but fluids/contact geometry can mimic it.</td><td>Signed edge formulation differs from raw/multiplicative strain screens; partly pre-empted. Low–medium cost; no validation.</td></tr></tbody></table>
<p>No untested candidate is promoted. H33-6's failure is a negative deliverable; remaining ideas require fresh preregistration and a valid holdout. Candidate details, official free-source availability checks and limitations are preserved in the linked slate.</p>
<p><b>New untried hypotheses (2026-10-26):</b> five further candidates are ranked in <a href="https://github.com/buffedlizard55-lab/GEMSDOE33/blob/main/knowledge/11_new_hypotheses_20261026.md">knowledge/11_new_hypotheses_20261026.md</a>: (H-N2) catalogue-flank frontier dots with H19-5 corroboration; (H-N3) signed strain-lobe across conductor–basement edge; (H-N4) 2 m probe proximity from DOE GDR #1391 (blocked — payload not retrievable here); (H-N5) ComCat focal-plane orientation vs potential-field lineaments (partially blocked). The top new candidate, H-N1 tilt-gravity-LiDAR coherence, was implemented and evaluated on the spatially blocked holdout: pooled confirmation ΔDTI −0.0907 (0/4 folds, CI [−0.1210, −0.0594]), no channel AUC > 0.90, unique vs all 12 pinned registry rasters — reported as a negative result; its format-valid unique TIFF is published as <code>gemsdoe33-g33-tilt-gravity-lidar-coherence-20261026-171b8b87dbf7-nan.tif</code> and is <b>not cleared to submit</b>.</p>
<p><b>2026-10-26 A33-R2-CSHT preregistered 5-hypothesis slate:</b> frozen prior to implementation in <a href="{GITHUB}/knowledge/12_preregistered_a33_r2_hypotheses_20261026.md">knowledge/12_preregistered_a33_r2_hypotheses_20261026.md</a> and <a href="{GITHUB}/evidence/a33_r2_preregistration_20261026.json">evidence/a33_r2_preregistration_20261026.json</a> (<code>SHA-256: f6144c2b6e0cd5bddb0966d9321697be3bb5a070808559a94f38eddcd2a70268</code>): (1) <b>A33-R2-H1 (`A33-R2-CSHT`)</b> cover-state + INGENIOUS <code>1,116</code>-seed hydrothermal conduit transfer + 300 m submodular <code>CELF</code> (tested: <code>8/8</code> fold wins across screen + orthogonal confirmation, stopped on pre-placement surface duplicate guard vs <code>G30-MSDB1</code>); (2) <b>A33-R2-H2</b> thermal-fluid strike-azimuth projection along MT/gravity walls; (3) <b>A33-R2-H3</b> cover-thickness normalized basement-relief edge ratio; (4) <b>A33-R2-H4</b> earthquake-swarm + strain-dilatation blind stepover transfer; (5) <b>A33-R2-H5</b> DOE GDR #1682 BRIDGE dense LiDAR transfer (blocked pending outbound host access).</p>
"""
    return page("Ranked hypotheses · GEMSDOE33", body, "hypotheses.html")

def build_data_sources() -> str:
    body = """<h2>External data and domain-transfer status</h2>
<p>Analogue geology is plausible context, but no domain-transfer bound or independent validation is established. The previous H33-F screen used available owner-mirror products and did not have independent BRIDGE field labels. Its P1 mean delta was −0.093072 and it failed; its exploratory discriminator AUC 0.917 is not a Ben-David HΔH bound.</p>
<div class="panel warn"><b>BRIDGE (DOE GDR #1682): listed, not locally audited.</b> Registry notes record a public listing and a CC BY 4.0 claim, but this workspace did not retrieve the GIS archive bytes. Geometry, CRS, field coverage, label independence, and overlap are therefore unverified. Do not use as viable transfer training/evaluation until retrieved and pinned.</div>
<div class="panel warn"><b>Gabbs Valley USGS source: metadata/bounds only.</b> USGS ScienceBase lists the fault dataset; the binary payload was not obtained. Bounding-box overlap is not proof of actual feature overlap or usable training labels.</div>
<h3>Conditions for any future Ben-David-style claim</h3><ol><li>Named, audited source and target domains with source label provenance.</li><li>Shared feature layers and common sampling support; account for spatial autocorrelation.</li><li>Spatial overlap/deduplication and a justified hypothesis class.</li><li>Source error, valid HΔH divergence estimate, finite-sample complexity term, and joint-label error λ. A discriminator AUC alone is not the bound.</li><li>Independent spatial confirmation; analog catalogue lines are not automatically independent truth.</li></ol>
<p>Official links are in the <a href="sources.html">source registry</a> and <a href="hypotheses.html">hypothesis slate</a>.</p>
"""
    return page("Data sources & transfer limits · GEMSDOE33", body, "data-sources.html")

def build_research() -> str:
    h336_audit = read_json(ROOT / "evidence/format_check_h33_6_6c888d2ce0f7.json")
    h33f_gate = read_json(ROOT / "evidence/holdout_analog.json")
    h33f_audit = read_json(ROOT / "evidence/format_check_h33f_d042874b26ef.json")

    body = f"""<h2>Research candidates and proxy holdout records</h2>
<div class="panel warn"><h3>2026-10-26 A33-R2-CSHT Cover-State + Hydrothermal Conduit Transfer (8/8 Fold Wins · Duplicate-Stopped)</h3>
<p><span class="badge good">OK TO DOWNLOAD: YES</span> <span class="badge bad">OK TO SUBMIT: NO (verdict: duplicate)</span></p>
<p>Screen <b>HOLDOUT-DTI = 0.136716</b> vs <code>B1_regional = 0.112418</code> (<code>Δ = +0.024298 [+0.012427, +0.035833]</code>, <code>4/4</code> folds); orthogonal confirmation <b>HOLDOUT-DTI = 0.131169</b> vs <code>B1_regional = 0.115122</code> (<code>Δ = +0.016047 [+0.003817, +0.028030]</code>, <code>4/4</code> folds); <code>50/50</code> feature leakage canaries passed (<code>max AUC = 0.7685 ≤ 0.90</code>); <code>final_dots</code> unique vs all 24 rasters (<code>max 3-px = 0.6934 ≤ 0.70</code>), stopped on pre-placement surface overlap vs <code>G30-MSDB1</code>.
<a href="downloads/gemsdoe33-a33-r2-csht-transfer-37654-20261026-0b78c04d5fad-zeros.tif">Download A33-R2-CSHT GeoTIFF</a> · <a href="downloads/gemsdoe33-a33-r2-csht-transfer-37654-20261026-0b78c04d5fad-zeros.zip">Download .zip</a> · <a href="data/a33_r2_run_card_20261026.json">Run Card JSON</a>.</p>
</div>
<div class="panel bad"><b>EXPLORATORY_NOT_LICENSED · BLOCKED_NOT_ESTIMATED</b>
<p>The first-round shortlist was retrospective and remains archived; H33-6 failed P1 and no candidate is slot-approved.
The score/file pairing unverified for historical baselines. H33-6 P1 mean ΔDTI was <b>−0.00273732</b> (2/4 folds positive);
A generic two-sample AUC is not itself that bound. The artifacts below are for research only.</p></div>

<div class="panel">
<h3>H33-6 Edge-Normal Consensus Research TIFF (Failed P1, Research Only)</h3>
<p><a class="btn alt" href="downloads/research/GEMSDOE33-H33-6-edge-consensus-research-20261004-6c888d2ce0f7-nan.tif">Download H33-6 research TIFF</a> ·
<a href="downloads/research/receipt-GEMSDOE33-H33-6-edge-consensus-research-20261004-6c888d2ce0f7.json">Audit JSON</a> ·
<span class="badge bad">RESEARCH ONLY</span></p>
<p>Independent local format audit: {esc(h336_audit.get('pass'))} · SHA-256: <code>{esc(h336_audit.get('sha256'))}</code></p>
</div>

<div class="panel">
<h3>Earlier H33-F analog-field screen</h3>
<p>Earlier H33-F analog-field screen failed local proxies (P1 mean <b>-0.093072</b>, 0/4 positive).
This was evaluated under Ben-David principles, but was <b>not</b> a Ben-David bound because independent BRIDGE labels were blocked.</p>
<p><a class="btn alt" href="downloads/gemsdoe33-h33f-analog-xfer-20261004-d042874b26ef-nan.tif">Download H33-F research TIFF</a> ·
<span class="badge bad">NOT SLOT-APPROVED</span></p>
<p>Format pass: {esc(h33f_audit.get('pass'))} · SHA-256: <code>{esc(h33f_audit.get('sha256'))}</code></p>
</div>

<div class="panel bad"><h3>2026-10-25 duplicate guard and run card</h3>
<p>H33-6 is not eligible for a slot. Its final raster crossed the duplicate threshold against 7 of 9 same-grid TIFFs available in this checkout. The external site rasters were not staged; the pre-placement edge surface was not screened in this audit; no new placement was run. The feature-alone leakage canary is also missing from retained evidence.</p>
<p>HOLDOUT-DTI (local <code>dti_binary</code>, four-fold conditional diagnostic; 60,988 withheld catalogue pixels): pooled DTI candidate <b>0.112486</b> vs control <b>0.114669</b>, pooled ΔDTI <b>−0.002183</b>; mean of fold deltas −0.002737 (2/4 positive). Descriptive fold-t 95% interval [−0.015020, +0.009546], df=3; not a private-label CI. The evaluator source has no semantic version field. See <a href="https://github.com/buffedlizard55-lab/GEMSDOE33/blob/main/evidence/duplicate_guard_run_card_20261025.json">machine-readable run card</a> and <a href="https://github.com/buffedlizard55-lab/GEMSDOE33/blob/main/evidence/holdout_h33_6.json">original holdout evidence</a>.</p>
</div>
"""
    return page("Research & Diagnostics · GEMSDOE33", body, "research.html")


def build_sources() -> str:
    sources = reg("sources.json")
    rows = "".join(
        f"<tr><td><b>{esc(s.get('id'))}</b></td><td><a href='{esc(s.get('url'))}'>{esc(s.get('title'))}</a></td>"
        f"<td>{esc(s.get('type') or s.get('evidence_class', 'SOURCE'))}</td>"
        f"<td>{esc(s.get('license') or s.get('verified_utc', '—'))}</td>"
        f"<td>{esc(s.get('note') or s.get('used_for', '—'))}</td></tr>"
        for s in sources.get("sources", [])
    )
    pins = reg("owner_mirror_input_pins.json")
    pin_rows = "".join(
        f"<tr><td><code>{esc(f.get('id'))}</code></td><td><code>{esc(f.get('dest'))}</code></td>"
        f"<td>{int(f.get('bytes', 0)):,} B</td><td><code>{esc(f.get('sha256')[:16])}...</code></td></tr>"
        for f in pins.get("files", [])
    )
    body = f"""<h2>Verified Sources & Data Provenance</h2>
<p>Sources are classified by provenance. A public listing or hash does not prove local binary availability, license suitability, exact geometry overlap, or organizer authenticity. See each source's recorded note and limitations.</p>

<h3>Official Competition & Geoscientific Sources</h3>
<div class="scroll">
<table><thead>
<tr><th>ID</th><th>Source Title / Link</th><th>Type</th><th>License</th><th>Verification Note</th></tr>
</thead><tbody>
{rows}
</tbody></table>
</div>

<h3>Historical input pin registry (not proof of current placement)</h3>
<p>The pin list records owner-mirror inputs from the prior run. The raw training/cache rasters are not present in this checkout; hashes identify claimed mirror bytes only and do not authenticate organizer provenance.</p>
<div class="scroll">
<table><thead>
<tr><th>Identifier</th><th>Local File</th><th>Bytes</th><th>SHA-256 Prefix</th></tr>
</thead><tbody>
{pin_rows}
</tbody></table>
</div>
"""
    return page("Sources & Audit · GEMSDOE33", body, "sources.html")


def build_irregularities() -> str:
    irreg = reg("irregularities.json")
    items = "".join(
        f"<div class='panel warn'><h3>[{esc(item.get('id'))}] {esc(item.get('finding', item.get('title', 'Finding')))}</h3>"
        f"<p><b>Severity:</b> {esc(item.get('severity', 'unspecified'))} · <b>Status:</b> <span class='badge warn'>{esc(item.get('status', 'unspecified'))}</span></p>"
        f"<p><b>Evidence:</b> {esc(item.get('evidence', 'not recorded'))}</p>"
        f"<p><b>Consequence / action:</b> {esc(item.get('consequence', item.get('resolution', 'review required')))}</p></div>"
        for item in irreg.get("irregularities", [])
    )
    body = f"""<h2>Irregularities & audit trail</h2>
<p>Known data-access, scientific, score-provenance and format issues are recorded below. Status labels preserve uncertainty; a repository note is not organizer verification.</p>

<div class="panel warn">
  <h3>Portal range error: reported, root cause unconfirmed</h3>
  <p>The owner reported a portal message, “Predicted values must be in range [0, 1]”. No organizer diagnostic or exact rejected file is preserved, so the cause is unknown. NaN outside the footprint may trigger an all-array range check, but this has not been verified against the organizer's validator.</p>
  <p>The retained H33-6 NaN-outside artifact passes the repository's footprint-only range audit; it fails an all-finite whole-array audit by design. A separate zero-outside file is not evidence of portal acceptance. Consult the current official format instructions and do not claim a local pass guarantees upload acceptance.</p>
</div>

{items}
"""
    return page("Irregularities & audit log · GEMSDOE33", body, "irregularities.html")


def build_focus_review() -> str:
    audit = read_json(ROOT / "evidence/focus_raster_audit_20261025.json")
    manifest = reg("focus_rasters_20261025.json")
    gate = read_json(ROOT / "evidence/promotion_gate_20261025.json")
    slate = reg("analog_hypotheses_20261025.json")
    rows = []
    for item in manifest.get("rasters", []):
        measured = next((r for r in audit.get("rasters", []) if r["id"] == item["id"]), {})
        url = (f"https://github.com/{item['repo']}/blob/{item['ref']}/{item['path']}"
               if "repo" in item else f"{GITHUB}/{item['local_path']}")
        rows.append(f"<tr><td>{esc(item['site'])}</td><td><a href='{esc(url)}'>{esc(item['id'])}</a></td>"
                    f"<td>{esc(measured.get('dots', 'not measured'))}</td>"
                    f"<td><code>{esc(item['sha256'])}</code></td></tr>")
    hypotheses = []
    for h in slate.get("candidates", []):
        sources = " · ".join(f'<a href="{esc(url)}">Official source</a>' for url in h["official_sources"])
        hypotheses.append(f"<div class='panel warn'><h3>{h['rank']}. {esc(h['id'])} — {esc(h['hypothesis'])}</h3>"
                          f"<p><b>Layers:</b> {esc(h['layers'])}</p><p><b>Signature:</b> {esc(h['signature'])}</p>"
                          f"<p><b>Missing-fault rationale:</b> {esc(h['missing_fault_rationale'])}</p>"
                          f"<p><b>Difference from local prior art:</b> {esc(h['difference_from_repo'])}</p>"
                          f"<p><b>Non-fault mimic:</b> {esc(h['non_fault_mimic'])}</p>"
                          f"<p><b>Qualitative priority / cost:</b> {esc(h['expected_improvement'])}; {esc(h['cost'])}</p>"
                          f"<p><b>{esc(h['availability'])}</b></p><p>{sources}</p></div>")
    gates = "".join(f"<tr><td>{esc(k)}</td><td>{'PASS' if v is True else 'BLOCKED'}</td></tr>"
                    for k, v in gate.get("gates", {}).items())
    body = f"""<h2>Latest audit: what the highest-scoring lineage actually contains</h2>
<div class="panel bad"><b>NOT OK TO SUBMIT. No new TIFF generated; zero new experiments and zero slots used.</b>
<p>The unique-submission goal remains incomplete. We will not rename a previous emission or fabricate validation to create a download.</p>
<p><a href="research/current-run-card.json" download>Download run card JSON</a> · <a href="research/current-promotion-gate.json" download>Automatic gate decision</a> · <a href="research/focus-raster-audit.json" download>Measured forensic audit</a></p></div>
<h3>GEMSDOE32 B2: reproducible construction, not a verified contest score</h3>
<p>The user-reported 0.2778 has no organizer receipt here. The pinned owner build record describes deletion of baseline dots at catalogue distance ≤2 pixels (200 m). We downloaded the named B2 raster and reproduced it pixel-exactly from GEMSDOE28 H27-4: <b>40,199 → 37,654 dots; 2,545 deletions, zero additions, zero mismatched cells.</b> This is prior-art forensics, not HOLDOUT-DTI.</p>
<p>B2 versus H27-4: Spearman <b>0.967587</b> and <b>100% candidate-dot overlap within 3 px</b>. It fails the lane thresholds if reused as a new candidate. GEMSDOE25/GEMSDOE30 share the same 44,090-dot prediction; GEMSDOE28 H27-4/GEMSDOE31 share the same 40,199-dot prediction. These pairs are not independent evidence of scientific improvement. GEMSDOE36 also has high overlap with B2; no PINN or geothermal-discovery claim is established by a filename.</p>
<h3>Why pruning might help — inference, not score attribution</h3>
<p>The local metric rewards a maximum nearby match, so redundant predictions can add false-positive cost without proportional new recovery. Deleting low-credit prediction mass can help; deleting near a real missing parallel fault can hurt. The exact net change requires held-out truth, which is unavailable for the reported organizer result. Neither the score list nor a source-code projection proves causation or predicts a higher competition score.</p>
<p><b>Irregularity:</b> the owner B2 audit's recorded aggregate means disagree with the average of its listed quadrant values; its note also contains an unverified score projection. We do not use that instrument as validation. The request's conflicting leader values 0.4413/0.3195 are not authenticated; no leaderboard was accessed.</p>
<h3>All nine requested sites covered</h3>
<p>Twelve precisely named historical rasters, pinned by SHA-256; 132 ordered comparisons on the shared template footprint. This is a focus subset, NOT a complete global uniqueness registry. Hashes authenticate mirror bytes only.</p>
<div class="scroll"><table><thead><tr><th>Site</th><th>Reference / pinned source</th><th>Positive cells</th><th>SHA-256</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
<h3>Data placement completed; scientific blockers remain</h3>
<p>All 17 owner-mirror inputs were restored and hash-audited. The existing preparer rebuilt 121 cached feature channels; no detector or stopped arm was retrained. Each feature still requires a leakage canary before being trusted. The sample mirror's finite values equal the catalogue, so only its grid and finiteness mask may be used.</p>
<p>Both archived H33-6 outside-mask variants were reopened and checked against the now-restored template. Local format passes do not repair its failed science or duplicate status. The writer now rejects invalid values rather than silently clipping them, rejects infinity outside, checks shape and enforces notes ≤140 characters. The organizer reference supports CPU training; a GPU is not mandatory.</p>
<h3>Automatic promotion evidence gates</h3>
<p>These are deterministic in-project checks, not a request for a human scientific inspector. <code>scripts/check_promotion.py</code> requires source-pinned shared tools, pooled paired improvement plus CI on screen and independent confirmation, complete feature canaries, both duplicate screens, exact saved-byte validation and budget compliance. It checks evidence completeness, not the truth of arbitrary supplied JSON. Even a pass is only eligibility for a separate weekly-cap-aware selector.</p>
<table><thead><tr><th>Gate</th><th>Current result</th></tr></thead><tbody>{gates}</tbody></table>
<h3>Four within-lane hypotheses, ranked BEFORE any new model implementation</h3>
<p>No identifiable new single-method lane paragraph or canonical template identity is supplied. The historical analog-transfer lane is retained only as planning scope. None of these source-dependent ideas is viable now: GDR/USGS payload hosts are outside this session's outbound allowlist. Historical public listings do not prove current obtainability, independence or licence. No hypothesis was trained or selected, and no performance estimate is reported.</p>
{''.join(hypotheses)}
<h3>Primary evidence and reviewable limitations</h3>
<p><a href="{GITHUB}/knowledge/10_focus_review_20261025.md">Full research/review note and next steps</a> · <a href="{GITHUB}/evidence/source_review_20261025.json">Pinned source inventory</a> · <a href="https://github.com/drivendataorg/gems-prize-reference-solution/blob/aebe92f7c8a990f0e3443451b7a825d9afd6336b/README.md">Organizer CPU/GPU reference</a>. Official competition rules, weekly cap, current leaderboard and score-to-file receipts were not freshly verified; no automated DrivenData contact was made.</p>
"""
    return page("Latest forensic review & automatic gates · GEMSDOE33", body, "latest-review.html")


def build_prompt() -> str:
    content = (ROOT / "standing_prompt.md").read_text(encoding="utf-8")
    body = f"""<h2>Standing Brief & Operational Prompt</h2>
<pre style="white-space:pre-wrap;background:#0d1520;padding:20px;border-radius:12px;">{esc(content)}</pre>"""
    return page("Standing Brief · GEMSDOE33", body, "standing-prompt.html")


def legacy_redirect(title: str, target: str, note: str) -> str:
    body = f"""<h2>{esc(title)}</h2>
<div class="panel warn"><p>{esc(note)}</p>
<p><a class="btn" href="{esc(target)}">Go to {esc(title)} &rarr;</a></p></div>"""
    return page(f"{title} · GEMSDOE33", body, target)


def retired_score_feed() -> str:
    review = reg("leaderboard_review.json")
    record = {
        "schema": 2,
        "as_of": "2026-10-04",
        "status": "RETIRED",
        "reason": "DrivenData Terms of Use prohibit automated or manual reproduction of row-level board data without consent.",
        "official_url": review.get("source_url"),
    }
    return json.dumps(record, indent=2, ensure_ascii=False) + chr(10)


def main() -> int:
    (ASSETS / "site.css").write_text(CSS, encoding="utf-8")
    pages = {
        "index.html": build_index(),
        "executive-summary.html": build_exec(),
        "results.html": build_results(),
        "latest-review.html": build_focus_review(),
        "hypotheses.html": build_hypotheses(),
        "data-sources.html": build_data_sources(),
        "research.html": build_research(),
        "sources.html": build_sources(),
        "irregularities.html": build_irregularities(),
        "standing-prompt.html": build_prompt(),
        "how-to-submit.html": build_exec(),  # Direct full page for how-to-submit
    }
    for filename, content in pages.items():
        (DOCS / filename).write_text(content, encoding="utf-8")
    research = DOCS / "research"
    research.mkdir(exist_ok=True)
    for source, name in (
        ("dpps_run_card_20261026.json", "dpps-run-card.json"),
        ("run_card_g33_20261026.json", "current-run-card.json"),
        ("round3_da_hgcm_run_card_20261025.json", "round3-da-hgcm-run-card.json"),
        ("promotion_gate_20261025.json", "current-promotion-gate.json"),
        ("focus_raster_audit_20261025.json", "focus-raster-audit.json"),
    ):
        payload = read_json(ROOT / "evidence" / source)
        (research / name).write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
    data_dir = DOCS / "data"
    data_dir.mkdir(exist_ok=True)
    r2_card = read_json(ROOT / "evidence" / "a33_r2_run_card_20261026.json")
    if r2_card:
        (data_dir / "a33_r2_run_card_20261026.json").write_text(
            json.dumps(r2_card, indent=2, allow_nan=False) + "\n", encoding="utf-8"
        )
    dpps_card = read_json(ROOT / "evidence" / "dpps_run_card_20261026.json")
    if dpps_card:
        (data_dir / "dpps_run_card_20261026.json").write_text(
            json.dumps(dpps_card, indent=2, allow_nan=False) + "\n", encoding="utf-8"
        )
    (DOCS / "score-feed.json").write_text(retired_score_feed(), encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    (ROOT / "index.html").write_text(
        '<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=docs/index.html">'
        '<title>GEMSDOE33</title><p>Redirecting to <a href="docs/index.html">the project site</a>.</p>',
        encoding="utf-8",
    )
    print("Built: " + ", ".join(f"docs/{name}" for name in pages))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
