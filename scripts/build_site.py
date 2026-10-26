#!/usr/bin/env python3
"""Build the static, evidence-led GitHub Pages site for GEMSDOE33.

Generates responsive, evidence-bounded static research pages for GitHub Pages:
  - index.html: Current decision and research-only artifact status.
  - executive-summary.html: Safe workflow for a future slot-cleared submission.
  - results.html: Score provenance and holdout evidence boundaries.
  - hypotheses.html: Qualitative untested Round-4 planning slate and source limits.
  - data-sources.html: External data access and transfer limitations.
  - research.html: Archived historical experiments, diagnostics, and format records.
  - sources.html: Trusted-source discovery links, data provenance, and hash verification audit.
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
<p>DrivenData #306 · evidence-led research · repository audit 2026-10-26</p><nav class="nav" aria-label="Primary">{links}</nav></div></header>
<main class="wrap">{body}</main>
<footer><div class="wrap">Generated from repository evidence by <code>scripts/build_site.py</code>. No candidate is slot-approved and no DrivenData upload was made from this workspace. A local format audit is not scientific validation or organizer acceptance. Owner reports, measured diagnostics, model outputs and official sources are distinguished in the evidence.</div></footer>
</body></html>"""


def unique_submission_hero() -> str:
    """Compatibility alias for older callers; expose the current research TIFF."""
    return a33_r3_llc_hero()


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


def a33_r3_lchc_hero() -> str:
    tif = "downloads/gemsdoe33-a33-r3-lchc-connectivity-37654-20261026-77337fc0c6c7-zeros.tif"
    zip_ = "downloads/gemsdoe33-a33-r3-lchc-connectivity-37654-20261026-77337fc0c6c7-zeros.zip"
    nan_tif = "downloads/gemsdoe33-a33-r3-lchc-connectivity-37654-20261026-77337fc0c6c7-nan.tif"
    rcpt = "downloads/receipt-gemsdoe33-a33-r3-lchc-connectivity-37654-20261026-77337fc0c6c7.json"
    card = "data/a33_r3_lchc_run_card_20261026.json"
    sha = "a58219e1cc9f15f0ede99863b0e5a619dbfa6946c7fdd4fb61f7050ddd5070ac"
    sub_name = "gemsdoe33-a33-r3-lchc-connectivity-37654-20261026-77337fc0c6c7"
    sub_note = "GEMS33 A33-R3-LCHC: thermal/vent least-cost connectivity graph 37654d | gate NEGATIVE | 77337fc0c6c7"
    return f"""<div class=\"hero-download\" id=\"a33-r3-lchc\">
<h2>2026-10-26 A33-R3-LCHC GeoTIFF — OK TO DOWNLOAD: YES · OK TO SUBMIT: NO — HONEST NEGATIVE HOLDOUT RESULT (verdict: negative, not duplicate)</h2>
<p><span class=\"badge good\">OK TO DOWNLOAD: YES · STRICT [0, 1] FORMAT PASS</span> <span class=\"badge good\">FULLY UNIQUE: MAX SPEARMAN 0.0054, MAX 3-PX OVERLAP 18.6%/16.7%</span> <span class=\"badge bad\">HOLDOUT-DTI 0/8 FOLDS (0.043712 / 0.035199 vs 0.125441 / 0.128184)</span> <span class=\"badge bad\">OK TO SUBMIT: NO (verdict: negative)</span></p>
<p><b>Second independently preregistered 2026-10-26 hypothesis (Least-Cost Hydrothermal Connectivity):</b> a Dijkstra + minimum-spanning-tree graph threads <code>1,116</code> catalogue-free DOE GDR #1391 thermal/vent seeds through a label-free conductivity/gravity/geodetic-strain/basement-edge resistance surface, placed via the shared 300 m triangular-kernel <code>CELF</code> operator (<code>37,654</code> dots, strict <code>[0.0, 1.0]</code>, <code>EPSG:32611</code>, <code>3730 × 3292</code>, <code>0</code> catalogue overlap).</p>
<p><b>Why OK TO SUBMIT is NO (<code>verdict: negative</code>, <code>0</code> slots spent):</b> On buffered whole-segment holdout (<code>gems-segment-pooled-v1</code>), the candidate <b>lost</b> to regional control <code>B1_regional</code> in both the quadrant screen (<code>HOLDOUT-DTI = 0.043712</code> vs <code>0.125441</code>, <code>0/4</code> folds) and the frozen orthogonal diagonal-wedge confirmation (<code>HOLDOUT-DTI = 0.035199</code> vs <code>0.128184</code>, <code>0/4</code> folds). This is an honest negative result, reported as a required deliverable rather than withheld: a graph-connectivity surface is structurally too sparse to avoid the metric's <code>4×</code> false-negative penalty, even though — unlike the sibling <code>A33-R2-CSHT</code> artifact — it passes <b>both</b> uniqueness gates cleanly (surface and final dots each &lt; 19% 3-px overlap against all 21 pinned registry rasters).</p>
<p><a class=\"btn\" href=\"{tif}\">Download A33-R3-LCHC [0, 1] GeoTIFF (787 KB)</a> <a class=\"btn alt\" href=\"{zip_}\">Download Single-TIFF .zip</a> <a class=\"btn alt\" href=\"{nan_tif}\">NaN-outside Twin .tif</a> <a class=\"btn alt\" href=\"{rcpt}\">Validator Receipt JSON</a> <a class=\"btn alt\" href=\"{card}\">A33-R3 Run Card JSON</a></p>
<table><tbody>
<tr><th>Unique submission name</th><td><code>{sub_name}</code></td></tr>
<tr><th>Suggested note (100 / 140 chars)</th><td><code>{sub_note}</code></td></tr>
</tbody></table>
</div>"""


def a33_r3_llc_hero() -> str:
    base = "gemsdoe33-a33-r3-llc-37654-20261026-7f91f9f3ced9"
    tif, zip_, nan_tif = f"downloads/{base}-zeros.tif", f"downloads/{base}-zeros.zip", f"downloads/{base}-nan.tif"
    rcpt, card, sel = f"downloads/receipt-{base}.json", "data/a33_r3_run_card_20261026.json", "data/submission_selection.json"
    sha = "76f9e157d01bb9bec2d98c3c5941b6114e06e0f439272d5f140af6e3584c8825"
    note = "GEMS33 A33-R3-LLC V2_gamma05: scarp line-integral x CSHT prior, CELF300 37654d | NEGATIVE | 7f91f9f3ced9"
    return f"""<div class="hero-download" id="a33-r3-llc">
<h2>2026-10-26 A33-R3-LLC GeoTIFF: OK TO DOWNLOAD: YES · OK TO SUBMIT: NO (verdict: negative)</h2>
<p><span class="badge good">OK TO DOWNLOAD: YES · STRICT [0, 1], 0.0 OUTSIDE</span> <span class="badge good">UNIQUE VS 22 REGISTRY RASTERS (max 3-px 43.25%)</span> <span class="badge bad">OK TO SUBMIT: NO · ties the holdout best, does not beat it</span></p>
<p><b>Automated selector decision</b> (<code>scripts/select_submission.py</code>, <a href="{sel}">selection JSON</a>): <b>no raster in this project is OK to submit.</b>
A33-R3-LLC multiplies the fold-trained CSHT prior by a label-free score for strike-integrated LiDAR scarp lines. It produced HOLDOUT-DTI <code>0.137868</code> [0.1286, 0.1479] on the quadrant screen, against CSHT's <code>0.137555</code> (paired &Delta; <code>+0.0003</code> [&minus;0.0080, +0.0083], 2/4 folds). On the diagonal-wedge confirmation it scored <code>0.131506</code> against <code>0.132066</code> (&Delta; <code>&minus;0.0006</code> [&minus;0.0090, +0.0075], 2/4 folds). Each split withheld 60,988 positives (<code>gems-segment-pooled-v1</code>). The file is format-valid and unique, but it is a research artifact: <b>do not spend a weekly slot.</b></p>
<p><b>Uniqueness was checked at both stages against 22 pinned rasters.</b> Pre-placement V2 surface: max |&rho;| <code>0.011126</code>, max preview-dot 3-px coverage <code>67.79%</code> (passes the 70% threshold by 2.21 percentage points; close margin). Final dots: max |&rho;| <code>0.019359</code>, max 3-px coverage <code>43.25%</code>. See the linked run card; these checks concern only the pinned registry, not every possible submission.</p>
<p><a class="btn" href="{tif}">Download A33-R3-LLC GeoTIFF (827 KB)</a> <a class="btn alt" href="{zip_}">Single-TIFF .zip (184 KB)</a> <a class="btn alt" href="{nan_tif}">NaN-outside twin</a> <a class="btn alt" href="{rcpt}">Validator receipt</a> <a class="btn alt" href="{card}">Run card JSON</a></p>
<table><tbody>
<tr><th>Unique submission name</th><td><code>{base}-zeros</code></td></tr>
<tr><th>Note (104 / 140 chars)</th><td><code>{note}</code></td></tr>
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
<h2>Parallel-session unique TIF (2026-10-26, G33-DPPS) — ✅ OK TO DOWNLOAD: YES · 🛑 OK TO SUBMIT: NO — DO NOT SPEND A WEEKLY SLOT (verdict: negative)</h2>
<p><span class="badge good">✅ OK TO DOWNLOAD: YES</span> <span class="badge bad">🛑 OK TO SUBMIT: NO</span> <span class="badge good">STRICT [0, 1] WHOLE-ARRAY PASS · 0 NaN</span> <span class="badge good">UNIQUE VS 25 REGISTRY RASTERS (surface + final dots)</span> <span class="badge bad">HOLDOUT GATE FAILED vs B1 (1/4 + 0/4 folds)</span></p>
<p><b>What this file is:</b> a genuinely new, deterministic <b>dip-projected persistence-scarp</b> emission
(zero learned weights, zero catalogue/H19-5/B2 pixels in its surface): ≥1.5 km along-strike LiDAR-scarp
persistence fused with gravity support warped updip by <code>z·cot60°</code> along the depth-to-basement
gradient, placed by 300 m CELF. <code>37,654</code> binary dots, single-band <code>float32</code>,
<code>EPSG:32611</code>, <code>3730 × 3292</code>, values exactly <code>{{0.0, 1.0}}</code> with
<code>0.0</code> outside the footprint — the whole array is finite in <code>[0, 1]</code> and passes the local strict all-array audit. The earlier portal message's cause and live-portal acceptance are unverified. <code>0</code> dots on the catalogue; <code>9/9</code> leakage canaries pass
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


def submission_steps() -> str:
    return """<h3>Exact submission steps (for any future raster the automated selector marks OK TO SUBMIT)</h3>
<ol>
<li>Run <code>python scripts/select_submission.py</code>. Upload only the file named in <code>docs/data/submission_selection.json</code>, and only if <code>"ok_to_submit": true</code>. Today it is <b>false</b>.</li>
<li>Confirm the file is unchanged: <code>sha256sum FILE</code> must equal the run card's <code>raster_sha256</code>. The selector checks this automatically.</li>
<li>Format (checked automatically by <code>scripts/validate_submission.py --strict-zero-outside</code>):
<ul>
<li>1 band, <code>float32</code>, <code>EPSG:32611</code>;</li>
<li>shape <code>3730 &times; 3292</code>, 100 m pixels, origin <code>(243350, 4508550)</code>, identical to <code>sample_submission.tif</code>;</li>
<li>every cell finite and in <code>[0, 1]</code>, with <code>0.0</code> outside the footprint. This passes the local strict all-array range check; it does not prove portal acceptance or diagnose the earlier reported message.</li>
</ul></li>
<li>On the DrivenData submission page for competition #306, while signed in as the owner, upload the <code>-zeros.tif</code>, or the <code>.zip</code> that contains exactly that one GeoTIFF.</li>
<li>Paste the unique submission name and the note (&le;140 characters) from the run card.</li>
<li>Check that a weekly slot is free before uploading. This project cannot observe the slot count.</li>
<li>Save the organizer's score receipt into <code>evidence/</code>. Only that receipt makes a score ORGANIZER-CONFIRMED.</li>
</ol>"""


def focus_site_summary_table() -> str:
    """Render the nine best-reported artifacts with byte-based uniqueness diagnostics."""
    audit = read_json(ROOT / "evidence" / "focus_registry_analysis_20261025.json")
    pairwise = audit.get("pairwise", [])
    rows = []
    for item in audit.get("artifacts", []):
        artifact_id = item.get("id", "")
        comparisons = []
        for comparison in pairwise:
            if comparison.get("left") == artifact_id:
                comparisons.append((
                    comparison.get("right", "other"),
                    float(comparison.get("spearman_rho_binary", 0.0)),
                    float(comparison.get("left_fraction_within_3px_of_right", 0.0)),
                ))
            elif comparison.get("right") == artifact_id:
                comparisons.append((
                    comparison.get("left", "other"),
                    float(comparison.get("spearman_rho_binary", 0.0)),
                    float(comparison.get("right_fraction_within_3px_of_left", 0.0)),
                ))
        worst_rho = max(comparisons, key=lambda value: abs(value[1])) if comparisons else ("—", 0.0, 0.0)
        worst_overlap = max(comparisons, key=lambda value: value[2]) if comparisons else ("—", 0.0, 0.0)
        passes_uniqueness = abs(worst_rho[1]) <= 0.90 and worst_overlap[2] <= 0.70
        repo = item.get("repository", "")
        ref = item.get("pinned_commit", "")
        path = item.get("path", "")
        url = f"https://github.com/{repo}/blob/{ref}/{path}" if repo and ref and path else "#"
        score = float(item.get("reported_dti_claim", 0.0))
        site = item.get("id", "").split("-", 1)[0]
        file_name = path.rsplit("/", 1)[-1]
        unique_text = (
            f"PASS (max |ρ| {abs(worst_rho[1]):.4f}; max 3-px coverage {worst_overlap[2]:.2%})"
            if passes_uniqueness else
            f"FAIL (max |ρ| {abs(worst_rho[1]):.4f} vs {esc(worst_rho[0])}; "
            f"max 3-px coverage {worst_overlap[2]:.2%} vs {esc(worst_overlap[0])})"
        )
        rows.append(
            f"<tr><td>{esc(site)}</td>"
            f"<td><a href=\"{esc(url)}\"><code>{esc(file_name)}</code></a></td>"
            f"<td>{score:.4f}<br><span class=\"muted\">owner/user reported, not organizer-confirmed</span></td>"
            f"<td>{unique_text}<br><span class=\"muted\">vs the other eight classic artifacts; ρ &gt; 0.90 or coverage &gt; 70% is a duplicate stop</span></td>"
            f"<td><b>Download:</b> source link available<br><b>Submit:</b> no; history/score is unverified and uniqueness fails</td></tr>"
        )
    return (
        '<div class="scroll"><table><thead><tr>'
        '<th>Site</th><th>Best reported artifact (pinned source)</th>'
        '<th>Reported score evidence</th><th>Measured uniqueness</th>'
        '<th>Download vs submit</th></tr></thead><tbody>'
        + "".join(rows)
        + "</tbody></table></div>"
    )


def ranked_hypothesis_table() -> str:
    """Return qualitative, explicitly untested Round-4 hypotheses and source limits."""
    hypotheses = [
        {
            "rank": "1",
            "id": "A33-R4-COULOMB",
            "mechanism": "Compute positive Coulomb failure-stress lobes from pinned Quaternary-fault slip rate, dip and sense (Okada elastic half-space), then place a matched-budget set of candidate splays.",
            "why": "Elastic stress transfer can load fault tips and conjugate or subparallel structures beyond simple distance-to-fault buffers; this is a distinct physical mechanism from the tested regional blends and geometric stepover grafts.",
            "mimic": "Catalogue endpoint/geometry artifacts, erroneous slip parameters, and basin-margin lithologic or hydrothermal boundaries can create apparently coherent lobes without a blind fault.",
            "upside": "Moderate–high, unproven",
            "cost": "Moderate; closed-form stress kernel plus sensitivity analysis",
            "data": "QFFD-derived CSV/JSON are present only as hash-pinned owner-mirror inputs. DOE GDR #1391 is the cited official source; its payload was not re-authenticated here.",
            "link": "https://gdr.openei.org/submissions/1391",
        },
        {
            "rank": "2",
            "id": "A33-R4-CURVTRACE (reframed)",
            "mechanism": "Test directional continuity of the available 12-channel LiDAR-derived scarp descriptors on the 100 m competition grid; do not describe this as a direct 1 m trace detector unless original DEM tiles are separately staged.",
            "why": "Persistent scarps may reveal fault traces at scales not expressed in regional gravity/magnetic favorability surfaces; a trace-continuity score is a different target than pixelwise regional classification.",
            "mimic": "Lake Lahontan beach ridges, fluvial/alluvial terrace risers, stream banks, roads, canals and levees can all be long, aligned non-fault scarps.",
            "upside": "Potentially high if coverage and mimic controls hold; not measured",
            "cost": "High; directional continuity and explicit non-fault rejection",
            "data": "Only a 100 m-grid derivative is pinned: its metadata says 2 m work resolution, 706/716 source tiles succeeded, and valid coverage is about 75.37%. The raw 1 m DEM tiles are not in the restored data directory; true 1 m processing is blocked.",
            "link": "https://www.usgs.gov/3d-elevation-program",
        },
        {
            "rank": "3",
            "id": "A33-R4-PFRT",
            "mechanism": "Project basement-relief highs updip by z·cot(dip) along −∇z to test a listric basement-to-piedmont offset geometry, with a matched dot budget.",
            "why": "An explicit geometric projection may locate blind listric faults rather than assigning favorability directly from gradient magnitude.",
            "mimic": "Igneous-body edges, sediment-thickness changes, basin-margin compaction and nontectonic basement lithologic contacts can mimic the projected gravity/relief alignment.",
            "upside": "Speculative/moderate",
            "cost": "Low–moderate; uses cached depth-to-basement and gravity features",
            "data": "The derived features are present in the local owner-mirror cache, not organizer-authenticated. It has high duplicate-convergence risk against G30-MSDB1/G24-gvc1/G25-h66.",
            "link": "https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and",
        },
        {
            "rank": "4",
            "id": "A33-R4-PALEOTEMP",
            "mechanism": "Transfer paleosinter/tufa and shallow temperature-probe anomalies as evidence of inactive or relict geothermal conduits, then test spatially blocked recovery of withheld fault segments.",
            "why": "Old hydrothermal conduits may preserve structure not represented by active-vent/wellspring inventories.",
            "mimic": "Seasonal groundwater flow, lithologic thermal conductivity, well depth, land-use disturbance and non-fault-controlled hydrothermal circulation can produce thermal anomalies or sinter-like deposits.",
            "upside": "Not assessable until the named product is obtained",
            "cost": "Blocked; specific probe/sinter inventory is not pinned locally",
            "data": "DOE GDR #1391 lists additional probe data, but the specific product is absent from the current pin set and its bytes/schema/coverage were not inspected.",
            "link": "https://gdr.openei.org/submissions/1391",
        },
    ]
    rows = []
    for hypothesis in hypotheses:
        rows.append(
            "<tr>"
            f"<td>{hypothesis['rank']}</td><td><b>{esc(hypothesis['id'])}</b><br>{esc(hypothesis['mechanism'])}</td>"
            f"<td>{esc(hypothesis['why'])}</td><td>{esc(hypothesis['mimic'])}</td>"
            f"<td>{esc(hypothesis['upside'])}</td><td>{esc(hypothesis['cost'])}</td>"
            f"<td>{esc(hypothesis['data'])}<br><a href=\"{esc(hypothesis['link'])}\">Official-source discovery link</a></td>"
            "</tr>"
        )
    return (
        '<div class="scroll"><table><thead><tr><th>Rank</th>'
        '<th>Untested hypothesis / mechanism</th><th>Geological rationale</th>'
        '<th>Named non-fault mimic</th><th>Qualitative upside</th><th>Cost</th>'
        '<th>Source / availability / limitation</th></tr></thead><tbody>'
        + "".join(rows)
        + "</tbody></table></div>"
    )


def build_index() -> str:
    body = f"""{a33_r3_llc_hero()}
<h2>Current decision — no submission is approved</h2>
<div class="panel bad"><b>NO RASTER IS OK TO SUBMIT.</b> The available A33-R3-LLC TIFF is format-valid and passes its recorded uniqueness screen, but it did not beat the matched holdout baseline on screen and independent confirmation. No TIFF was generated in this review, no slot was selected, and no upload was made.</div>
<p><b>Competition-score estimate: not available.</b> HOLDOUT-DTI is an internal catalogue-proxy diagnostic, not a calibrated prediction of the organizer's score. The historical values shown elsewhere are owner/user-reported and have no organizer receipt in this repository.</p>
<h2>Navigate the evidence</h2>
<div class="grid-2">
<div class="panel accent"><h3>Executive summary</h3><p><a href="executive-summary.html">Nine-site best-reported artifact table</a> with evidence class, pinned source, measured pairwise duplication, and download-versus-submit status.</p></div>
<div class="panel accent"><h3>Latest review</h3><p><a href="latest-review.html">Repository and data-preparation review</a>, unresolved lane/template blockers, source limitations, and the next ranked geological hypotheses.</p></div>
<div class="panel accent"><h3>Research records</h3><p><a href="results.html">HOLDOUT-DTI results</a> · <a href="research.html">run cards and diagnostics</a> · <a href="irregularities.html">known conflicts and limitations</a>.</p></div>
<div class="panel accent"><h3>Sources</h3><p><a href="sources.html">Official source discovery links</a> and owner-mirror hash/provenance limitations. Source links are not equivalent to freshly authenticated payloads.</p></div>
</div>
<h2>Rules that govern this site</h2>
<ul><li>Do not infer an organizer score from holdout metrics or owner reports.</li><li>Do not upload unless the exact artifact is cleared by both the scientific gates and the separate selector/slot process.</li><li>Compare both the pre-placement score surface and final emitted dots against the registry; fail closed at |ρ| &gt; 0.90 or more than 70% of candidate dots within 3 px of one raster.</li><li>Do not run a new experiment until an explicit method lane and canonical shared-template identity are resolved.</li></ul>
"""
    return page("GEMSDOE33 · Evidence-led fault discovery", body, "index.html")


def build_exec() -> str:
    body = f"""<h2>Executive summary — best evidence, artifact, and submission status</h2>
<div class="panel bad"><b>Decision: no TIFF is currently OK to submit.</b> This review generated no new raster and spent no competition slot. The download below is an existing research artifact—not a recommended competition entry.</div>

<h3>Current research TIFF: A33-R3-LLC</h3>
<p>The exact TIFF is easy to download from the card below. Its recorded validator passed and its final dots pass the recorded 22-raster uniqueness checks, but its matched HOLDOUT-DTI results do not show an improvement over CSHT. <b>OK to download: yes. OK to submit: no.</b></p>
{a33_r3_llc_hero()}

<h3>What is the best-reported historical artifact at each requested focus site?</h3>
<p>Every score below is a <b>USER/OWNER-REPORTED claim</b>, not ORGANIZER-CONFIRMED. The pinned source links identify owner-mirror bytes and the measured comparison covers only the nine classic top artifacts—not every raster ever submitted; it is not a complete global registry. The 3-px statistic is directional: the share of this row's candidate dots that lie within 3 pixels of another row's raster. Since each row breaches at least one duplicate threshold, none should be reused as a new unique submission. The reported value is not a competition-score estimate.</p>
{focus_site_summary_table()}
<p>Download the clean audit table: <a href="data/focus_best_artifact_summary_20261026.csv">CSV</a> · <a href="data/focus_best_artifact_summary_20261026.json">JSON</a>. Source evidence: <a href="{GITHUB}/evidence/focus_registry_analysis_20261025.json">pinned nine-artifact byte/geometry analysis</a> and <a href="{GITHUB}/registry/focus_rasters_20261026.json">expanded focus raster inventory</a>. The 3-px/rank-correlation checks establish similarity only among the compared rasters; they do not prove score provenance or scientific quality.</p>
<h3>GEMSDOE32 B2: byte lineage and plausible mechanism, not verified score causation</h3>
<p>The byte audit reproduces B2 as a deletion-only subset of GEMSDOE28 H27-4: 40,199 dots become 37,654 by removing 2,545 dots at 1–2 pixels from the visible catalogue; no dots are added. Under the metric's α=0.2 false-positive and β=0.8 false-negative weights, removing redundant low-credit catalogue-halo predictions could reduce false-positive cost. This is a plausible mechanism, not proof that the change caused the reported 0.2778: no organizer receipt links that claim to these bytes. B2 is itself part of a duplicate family and must not be reused as a new submission.</p>

<h3>Current holdout evidence (not a competition score)</h3>
<p>A33-R3-LLC screen: HOLDOUT-DTI <code>0.137868</code> [95% CI <code>0.128559, 0.147913</code>] vs CSHT <code>0.137555</code>; paired delta <code>+0.000313</code> [<code>−0.008009, +0.008288</code>], <code>2/4</code> folds. Independent confirmation: <code>0.131506</code> [<code>0.1208, 0.1414</code>] vs <code>0.132066</code>; paired delta <code>−0.000560</code> [<code>−0.009035, +0.007547</code>], <code>2/4</code> folds. Evaluator: <code>gems-segment-pooled-v1</code>; <code>60,988</code> withheld positives per split. Both paired confidence intervals include zero or negative values, so promotion failed. Do not translate these internal metrics to a competition score.</p>

<h3>Ranked hypotheses for a future, authorized experiment</h3>
<p>These are qualitative research priorities, <b>not</b> score projections. Rank 1–4 reflect expected information/value relative to implementation cost, not a numeric expected DTI gain. No hypothesis was selected or run: there is no identifiable single-method lane paragraph and no unambiguous canonical shared-template identity in the current task.</p>
{ranked_hypothesis_table()}

<h3>Trusted-source links and limitations</h3>
<ul>
<li><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">DrivenData competition problem and metric</a>; <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/rules/">competition rules</a>; <a href="https://github.com/drivendataorg/gems-prize-reference-solution">organizer reference solution</a>. These links were not freshly authenticated in this review; no leaderboard was monitored or scraped.</li>
<li><a href="https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and">USGS GeoDAWN</a>; <a href="https://www.usgs.gov/3d-elevation-program">USGS 3DEP</a>; <a href="https://gdr.openei.org/submissions/1391">DOE Geothermal Data Repository #1391</a>. Data restored locally came from pinned owner mirrors, not directly from these official sites.</li>
<li>See <a href="sources.html">source registry</a>, <a href="data-sources.html">data transfer limits</a>, and <a href="latest-review.html">audit notes</a> for evidence classes, licensing/provenance caveats, and payload availability.</li>
</ul>

<h3>Submission procedure (future candidate only)</h3>
<div class="panel warn">Do not submit the current research TIFF. A future candidate would need a preregistered, fold-safe holdout with feature-by-feature leakage canaries, independent confirmation, pre-placement and final-dot uniqueness checks, saved-byte validation, a complete JSON run card, and a separate selector decision within a verified slot limit. An organizer receipt is required before labeling any score ORGANIZER-CONFIRMED.</div>
"""
    return page("Executive summary · GEMSDOE33", body, "executive-summary.html")

def build_results() -> str:
    body = f"""<h2>Results, score claims, and evidence boundaries</h2>
<p><a href="latest-review.html">Current: repository review, nine-site score-evidence table, current gates and ranked untested hypotheses</a> · <a href="{GITHUB}/knowledge/13_focus_forensics_g32_proof_and_a33_r2_results_20261026.md">2026-10-26 21-raster forensic proof &amp; A33-R2-CSHT report</a> · <a href="{GITHUB}/knowledge/16_a33_r3_llc_preregistration_and_result_20261026.md">A33-R3-LLC preregistration &amp; negative result</a> · <a href="{GITHUB}/registry/user_reported_scores_20261026.csv">full user-reported score list</a>.</p>
<h3>2026-10-26 A33-R3-LLC (negative: ties CSHT)</h3>
<p><b>HOLDOUT-DTI</b> (<code>gems-segment-pooled-v1</code>, 60,988 withheld): screen <code>0.137868</code> [0.1286, 0.1479] vs in-run CSHT <code>0.137555</code>, &Delta; +0.000313 [&minus;0.008009, +0.008288], 2/4 folds; confirmation <code>0.131506</code> [0.1208, 0.1414] vs <code>0.132066</code>, &Delta; &minus;0.000560 [&minus;0.009035, +0.007547], 2/4 folds. Informational H19-5 reference (not fold-safe): screen <code>0.162036</code>. Verdict <b>negative</b>; OK TO DOWNLOAD: YES · OK TO SUBMIT: NO.</p>
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
    body = f"""<h2>Ranked geological hypotheses — planning only</h2>
<div class="panel warn"><b>No new hypothesis was selected or tested.</b> The current task has no identifiable standalone method-lane paragraph, and the canonical shared-template identity is unresolved. Historical analog-transfer text is not authority to infer a lane. The rankings below are qualitative prior beliefs about information gain relative to cost—not DTI predictions or competition-score estimates.</div>
<p>The slate draws on the prior Round-4 notes in <a href="{GITHUB}/knowledge/17_a33_r3_lchc_result_and_round4_hypothesis_slate_20261026.md">knowledge/17</a>, with a review correction for LiDAR resolution and current owner-mirror availability. Every experiment, if authorized later, must reuse the agreed shared evaluator/writer and pass the standing holdout, leakage, uniqueness, validator and run-card protocol.</p>
{ranked_hypothesis_table()}
<h3>Separate unfinished audit item (not a novel hypothesis)</h3>
<p><b>A33-R2-HMDT:</b> a prior artifact exists but has no HOLDOUT-DTI run card/evaluation. Finishing that missing evaluation would be a gated audit of an existing mechanism, not a new hypothesis and not evidence of improvement. It remains ineligible to submit. Do not run it until the lane and canonical template are resolved.</p>
<h3>Historical slates and prior results</h3>
<p>Earlier H33-6, A33-R2, and A33-R3 records are retained as historical experiments. H33-6 failed its recorded conditional proxy gate; A33-R2-CSHT was duplicate-stopped; A33-R3-LLC tied CSHT within uncertainty; A33-R3-LCHC failed both screen and confirmation. Their run cards and caveats are linked from <a href="results.html">Results</a>, <a href="research.html">Research</a>, and the corresponding <code>evidence/</code> files. None yields a competition-score estimate.</p>
<h3>Source limitations relevant to the slate</h3>
<ul><li>DOE GDR #1391 and USGS 3DEP/GeoDAWN links are discovery references; this session did not freshly authenticate their pages or retrieve the specific raw payloads.</li><li>Restored QFFD/thermal/GeoDAWN/LiDAR derivative files were hash-verified against owner-mirror pins, not organizer-authenticated source downloads.</li><li>The saved LiDAR descriptor product is on the 100 m competition grid, with reported 2 m work resolution and partial coverage. The original 1 m DEM tile stack is absent; do not claim a direct 1 m continuity analysis from the derivative.</li></ul>
"""
    return page("Ranked geological hypotheses · GEMSDOE33", body, "hypotheses.html")


def build_data_sources() -> str:
    body = """<h2>External data, provenance, and transfer limits</h2>
<p>Official links are provided for manual review. Their presence in the registry is not proof that a page or payload was freshly checked, downloaded, licensed for this use, independent, or spatially suitable during this session.</p>
<div class="panel warn"><b>Restored-data status:</b> 17 inputs were restored and matched to SHA-256 values from pinned owner mirrors, then the existing preparer built 121 feature channels with detector training skipped. This verifies integrity against the owner pins only. It does not authenticate organizer provenance, licensing, coverage or scientific validity. See <a href="data/data_preparation_20261026.json">the session evidence record</a>.</div>
<h3>Key official / trusted-source discovery links</h3>
<ul>
<li><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">DrivenData #306 problem description and metric</a> · <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/rules/">contest rules</a> · <a href="https://github.com/drivendataorg/gems-prize-reference-solution">organizer reference solution</a>. Current slot rules and portal acceptance require manual confirmation by the account holder.</li>
<li><a href="https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and">USGS GeoDAWN data record</a> and <a href="https://www.usgs.gov/3d-elevation-program">USGS 3DEP</a>. The feature bytes used locally were restored from owner mirrors; the original sources were not downloaded in this review.</li>
<li><a href="https://gdr.openei.org/submissions/1391">DOE Geothermal Data Repository #1391 / INGENIOUS compilation</a>. The QFFD and thermal derivative inputs are owner-mirror copies; the specific paleotemperature/sinter product proposed for A33-R4-PALEOTEMP is not in the pin set.</li>
<li><a href="https://pubs.usgs.gov/publication/sim3498">USGS Gabbs Valley geologic map</a> and its <a href="https://www.usgs.gov/data/stratigraphic-and-fault-surfaces-three-dimensional-geologic-map-southeastern-gabbs-valley">data-release page</a> are analog-source references, not independent local truth.</li>
</ul>
<h3>Limits on analog transfer</h3>
<ol><li>Define source and target domains and labels from audited, independent data.</li><li>Confirm spatial overlap at feature level, not just bounding-box overlap.</li><li>Account for spatial autocorrelation, label policy, coverage and source-specific error.</li><li>A domain-discriminator AUC alone is not a Ben-David bound; a bound also requires source error, a justified HΔH divergence, complexity terms and joint-label error.</li><li>Use a spatially blocked, leakage-safe holdout and independent confirmation before considering a submission.</li></ol>
<p>No analog-source transfer performance estimate is reported here.</p>
"""
    return page("Data sources & transfer limits · GEMSDOE33", body, "data-sources.html")

def build_research() -> str:
    h336_audit = read_json(ROOT / "evidence/format_check_h33_6_6c888d2ce0f7.json")
    h33f_gate = read_json(ROOT / "evidence/holdout_analog.json")
    h33f_audit = read_json(ROOT / "evidence/format_check_h33f_d042874b26ef.json")

    body = f"""<h2>Research candidates and proxy holdout records</h2>
<div class="panel bad"><b>Current decision: no raster is slot-approved.</b> This page preserves prior experiments and should be read as an archive. The latest artifact is A33-R3-LLC, whose matched holdout result was negative for promotion; see <a href="latest-review.html">the current review</a> and <a href="results.html">score provenance</a>. Historical values below do not estimate organizer scores.</div>
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
        f"<tr><td><b>{esc(item.get('id'))}</b></td><td><a href='{esc(item.get('url'))}'>{esc(item.get('title'))}</a></td>"
        f"<td>{esc(item.get('type') or item.get('evidence_class', 'SOURCE'))}</td>"
        f"<td>{esc(item.get('license') or item.get('verified_utc', '—'))}</td>"
        f"<td>{esc(item.get('note') or item.get('used_for', '—'))}</td></tr>"
        for item in sources.get("sources", [])
    )
    pins = reg("owner_mirror_input_pins.json")
    pin_rows = "".join(
        f"<tr><td><code>{esc(file.get('id'))}</code></td><td><code>{esc(file.get('dest'))}</code></td>"
        f"<td>{int(file.get('bytes', 0)):,} B</td><td><code>{esc(file.get('sha256', '')[:16])}...</code></td></tr>"
        for file in pins.get("files", [])
    )
    prep = read_json(ROOT / "evidence" / "data_preparation_20261026.json")
    restore = prep.get("restore", {})
    feature = prep.get("feature_preparation", {})
    body = f"""<h2>Source links & provenance registry</h2>
<div class="panel warn"><b>Evidence boundary:</b> this table is a curated source register, not a claim that every external URL was freshly fetched in this review. Public listings, owner-mirror commits, and matching hashes do not by themselves authenticate organizer origin, a license grant for a specific use, schema, spatial coverage, or scientific independence. The DrivenData leaderboard was not monitored or copied.</div>
<h3>Official and trusted-source discovery links</h3>
<div class="scroll"><table><thead><tr><th>ID</th><th>Title / link</th><th>Class</th><th>License / date note</th><th>Recorded scope and limitations</th></tr></thead><tbody>{rows}</tbody></table></div>
<h3>Owner-mirror input pins and this session's preparation</h3>
<p><b>{restore.get('input_count', 0)} inputs</b> ({int(restore.get('total_bytes', 0)):,} bytes) restored and SHA-256-verified against pinned owner mirrors; all hash checks reported {str(restore.get('all_hashes_verified', False)).lower()}. The existing data preparer built <b>{feature.get('channel_count', 0)} channels</b> under <code>{esc(feature.get('cache_location', '.cache/feature_stack'))}</code>; detector training and model training were skipped. This is preparation—not an experiment. Raw data and the feature cache are gitignored and are not distributed with this site. The compact auditable record is <a href="data/data_preparation_20261026.json">data/data_preparation_20261026.json</a>.</p>
<div class="scroll"><table><thead><tr><th>Identifier</th><th>Destination</th><th>Bytes</th><th>SHA-256 prefix</th></tr></thead><tbody>{pin_rows}</tbody></table></div>
<p>Every mirror file's full hash and source pin is recorded in <code>registry/owner_mirror_input_pins.json</code>. The cache is not evidence of feature validity: each feature needs a leakage canary before being trusted.</p>
"""
    return page("Sources & provenance · GEMSDOE33", body, "sources.html")


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
    review = read_json(ROOT / "evidence/repository_review_20261026.json")
    prep = read_json(ROOT / "evidence/data_preparation_20261026.json")
    artifact = review.get("current_research_artifact", {})
    prep_restore = prep.get("restore", {})
    prep_features = prep.get("feature_preparation", {})
    site_table = focus_site_summary_table()
    hypothesis_table = ranked_hypothesis_table()
    body = f"""<h2>Latest repository review — status, scores, and next gates</h2>
<div class="panel bad"><b>Current decision: NO RASTER IS OK TO SUBMIT.</b> The existing A33-R3-LLC file is OK TO DOWNLOAD for research and reproducibility, but its selector verdict is negative. No TIFF was generated in this review; no holdout was rerun; no slot was used; no DrivenData upload or organizer score receipt exists.</div>
<p><b>Current artifact SHA-256:</b> <code>{esc(artifact.get('sha256'))}</code> · <b>HOLDOUT-DTI:</b> see <a href="data/a33_r3_run_card_20261026.json">run card</a> (<code>gems-segment-pooled-v1</code>, 60,988 withheld positives, screen and confirmation paired CIs include no improvement over CSHT) · <b>format:</b> saved-byte validator passed · <b>uniqueness:</b> recorded surface/final-dot gates pass vs 22 pinned registry rasters. The format and novelty gates cannot compensate for the negative holdout.</p>
<h3>Scope and blockers</h3>
<ul><li>The current request has no identifiable standalone single-method lane paragraph. Do not infer one from the README's historical analog-field paragraph.</li><li>No canonical shared-template identity (commit/path) is explicitly authorized for this task. A repository pin or same-named script elsewhere does not by itself resolve that instruction.</li><li>Historical site scores are user/owner claims without organizer receipts in this checkout. No scientifically defensible competition-score estimate can be constructed from HOLDOUT-DTI.</li></ul>
<h3>Nine-site executive table: best reported artifact, evidence class, and duplication</h3>
<p>The source set is the nine classic best-reported artifacts. All nine fail at least one uniqueness threshold when compared with the other eight in this set. This is not a complete global registry check or an organizer-score audit. Download the full table: <a href="data/focus_best_artifact_summary_20261026.csv">CSV</a> · <a href="data/focus_best_artifact_summary_20261026.json">JSON</a>.</p>
{site_table}
<h3>Data restoration and feature preparation — not an experiment</h3>
<p>{prep_restore.get('input_count', 0)} pinned owner-mirror inputs ({int(prep_restore.get('total_bytes', 0)):,} bytes) restored and hash-verified; {prep_features.get('channel_count', 0)} feature channels prepared under the gitignored <code>.cache/feature_stack</code>; detector training skipped. These bytes are not organizer-authenticated. No training, spatial holdout, score evaluation, or raster emission occurred during this review. Full hashes and provenance class: <a href="data/data_preparation_20261026.json">data preparation evidence</a>.</p>
<h3>Ranked, untested geological hypotheses</h3>
<p>Qualitative expected value/cost ordering only—no numeric score estimates. No experiment may begin until the lane and shared-template identity are resolved.</p>
{hypothesis_table}
<h3>Trusted-source links and limitations</h3>
<p>Manual review links are collected in <a href="sources.html">the source registry</a>. Relevant references include the <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">official problem statement</a>, <a href="https://www.usgs.gov/3d-elevation-program">USGS 3DEP</a>, <a href="https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and">USGS GeoDAWN</a>, and <a href="https://gdr.openei.org/submissions/1391">DOE GDR #1391</a>. No external page was freshly authenticated here; owner-mirror hashes establish integrity against the pins only.</p>
<p>Review ledger: <a href="data/repository_review_20261026.json">data/repository_review_20261026.json</a>. Historical run cards and score claims remain preserved; this page does not overwrite or relabel them.</p>
"""
    return page("Latest repository review · GEMSDOE33", body, "latest-review.html")


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
    for source_name in (
        "a33_r3_run_card_20261026.json",
        "data_preparation_20261026.json",
        "repository_review_20261026.json",
    ):
        payload = read_json(ROOT / "evidence" / source_name)
        if payload:
            (data_dir / source_name).write_text(
                json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8"
            )
    for source_name in (
        "focus_best_artifact_summary_20261026.json",
        "focus_best_artifact_summary_20261026.csv",
    ):
        source_path = ROOT / "registry" / source_name
        if source_path.is_file():
            (data_dir / source_name).write_bytes(source_path.read_bytes())
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
