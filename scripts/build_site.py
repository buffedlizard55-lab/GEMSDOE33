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
<p>DrivenData #306 · evidence-led research · review status 2026-10-27</p><nav class="nav" aria-label="Primary">{links}</nav></div></header>
<main class="wrap">{body}</main>
<footer><div class="wrap">Generated from repository evidence by <code>scripts/build_site.py</code>. No candidate is slot-approved and no DrivenData upload was made from this workspace. A local format audit is not scientific validation or organizer acceptance. Owner reports, measured diagnostics, model outputs and official sources are distinguished in the evidence.</div></footer>
</body></html>"""


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
<p><a class="btn" href="{tif}">Download A33-R3-LLC GeoTIFF (827 KB)</a> <a class="btn alt" href="{zip_}">Single-TIFF .zip (184 KB)</a> <a class="btn alt" href="{nan_tif}">NaN-outside twin</a> <a class="btn alt" href="{rcpt}">Validator receipt</a> <a class="btn alt" href="{card}">Run card JSON</a></p>
<table><tbody>
<tr><th>Unique submission name</th><td><code>{base}-zeros</code></td></tr>
<tr><th>Note (104 / 140 chars)</th><td><code>{note}</code></td></tr>
<tr><th>GeoTIFF SHA-256</th><td><code>{sha}</code></td></tr>
</tbody></table>
</div>"""


def fsml2_hero() -> str:
    """Newest unique research artifact banner (FSML2-CC), built from its run card."""
    card = read_json(ROOT / "evidence" / "fsml2_run_card_20261026.json")
    if not card:
        return ""
    sub = card["submission"]
    sel = card["selected_variant"]
    bud = card["selected_budget"]
    sk = f"{sel}@{bud}"
    ck = f"A33_R2_CSHT@{bud}"
    hs, hc = card["holdout_dti"]["screen"], card["holdout_dti"]["confirmation"]
    ps, pc = hs["paired_vs_csht_matched_budget"], hc["paired_vs_csht_matched_budget"]
    u = card["correlation_overlap_vs_registry"]
    surf = u["surface_checks_all_variants"][sel]
    return f"""<div class="hero-download" id="fsml2-cc">
<h2>LATEST UNIQUE RESEARCH TIFF (generated 2026-10-26; not generated in this review) — ✅ OK TO DOWNLOAD: YES · 🛑 OK TO SUBMIT: NO (verdict: negative)</h2>
<p><span class="badge good">UNIQUE vs 22 registry rasters: surface max 3-px overlap {100*surf['max_preview_fraction_within_3px']:.1f}% ≤ 70%; final dots {100*u['final_dots_max_3px_overlap']:.1f}%, max |ρ| {u['final_dots_max_abs_spearman']:.3f} — passes the checked registry screen (not global uniqueness proof)</span>
<span class="badge good">FORMAT PASS: single-band float32, EPSG:32611, 3730×3292, whole array finite in [0,1] (values exactly {{0,1}})</span>
<span class="badge bad">HOLDOUT GATE FAILED vs CSHT (0/4 + 0/4 folds) — DO NOT SPEND A SLOT</span></p>
<p><b>What it is:</b> corroboration-count fusion — 4 fold-safe spy-PU physics experts + 2 label-free lines
(multiscale geopotential worms; strike-integrated LiDAR scarp lines); a pixel ranks by how many independent
lines place it in their top decile. CELF-300 m dotted emission, {bud:,} dots, 0 on catalogue. It is the fold-safe
re-derivation of the H19-5 multi-line idea that produced the 0.2778* B2 family (<a href="https://github.com/buffedlizard55-lab/GEMSDOE33/blob/main/knowledge/22_b2_forensics_and_fsml_slate_20261026.md">forensics + slate</a>).</p>
<div class="scroll"><table><thead><tr><th>File to download</th><th>HOLDOUT-DTI (α=0.2, β=0.8, 300 m triangular kernel; gems-segment-pooled-v1, 60,988 withheld positives; 10 km block-bootstrap 95% CI) — NOT a leaderboard estimate</th><th>Unique vs all 9 focus sites' registry?</th><th>OK to submit?</th></tr></thead><tbody>
<tr><td><code>{sub['file']}</code></td><td>screen {hs[sk]['dti']:.4f} [{hs[sk]['ci95'][0]:.4f}, {hs[sk]['ci95'][1]:.4f}] vs CSHT {hs[ck]['dti']:.4f} [{hs[ck]['ci95'][0]:.4f}, {hs[ck]['ci95'][1]:.4f}] (paired Δ {ps['paired_delta_dti']:+.4f} [{ps['paired_delta_ci95'][0]:+.4f}, {ps['paired_delta_ci95'][1]:+.4f}], {ps['fold_wins']}/4); confirmation {hc[sk]['dti']:.4f} [{hc[sk]['ci95'][0]:.4f}, {hc[sk]['ci95'][1]:.4f}] vs CSHT {hc[ck]['dti']:.4f} [{hc[ck]['ci95'][0]:.4f}, {hc[ck]['ci95'][1]:.4f}] (paired Δ {pc['paired_delta_dti']:+.4f} [{pc['paired_delta_ci95'][0]:+.4f}, {pc['paired_delta_ci95'][1]:+.4f}], {pc['fold_wins']}/4). <b>Public score: not estimable</b>; this proxy is not calibrated to the public leaderboard.</td><td><b>YES vs the checked 22-raster registry only</b></td><td><b>NO</b> — holdout gate failed; research only</td></tr>
</tbody></table></div>
<p><a class="btn" href="downloads/{sub['file']}">⬇ Download unique FSML2-CC GeoTIFF (research only)</a> <a class="btn alt" href="downloads/{sub['zip']}">Single-TIFF .zip</a> <a class="btn alt" href="downloads/{sub['nan_twin']}">NaN-outside twin</a> <a class="btn alt" href="data/fsml2_run_card_20261026.json">Run card JSON</a></p>
<table><tbody>
<tr><th>Unique submission name</th><td><code>{sub['name']}</code></td></tr>
<tr><th>Note (≤140 characters)</th><td><code>{esc(sub['note'])}</code> ({sub['note_characters']}/140)</td></tr>
<tr><th>SHA-256 (.tif)</th><td><code>{card['raster_sha256']}</code></td></tr>
<tr><th>Decision</th><td><b>✅ DOWNLOAD YES · 🛑 SUBMIT NO.</b> Failed gates: screen/confirmation beat-CSHT, CI, fold wins. Automated selector: 0 eligible of 13 run cards. Slots spent: 0.</td></tr>
</tbody></table>
<p class="small"><b>Range-error note:</b> every cell of this <code>-zeros.tif</code> is finite and in [0,1] (re-opened and checked byte-wise), so its values cannot themselves violate a [0,1] range check. Portal acceptance and the cause of the previously reported range error remain unverified; the <code>-nan.tif</code> twin follows the recorded null/NaN-outside wording. Do not upload this negative artifact either way.</p>
</div>"""


def s33_seisdil_hero() -> str:
    """Build the latest negative research-artifact banner from its retained run card."""
    card = read_json(ROOT / "evidence" / "s33_seisdil_run_card_20261026.json")
    if not card:
        return ""
    h = card["holdout_dti"]
    screen = h["screen_paired"]
    confirm = h["confirm_paired"]
    unique = card["correlation_overlap_vs_registry"]
    screen_ci = screen["paired_delta_ci95"]
    confirm_ci = confirm["paired_delta_ci95"]
    filename = f"{card['submission_name']}.tif"
    zipname = f"{card['submission_name']}.zip"
    card_link = "data/s33_seisdil_run_card_20261026.json"
    max_auc = max(x["max_fold_auc"] for x in card["feature_canaries"])
    return f"""<div class="hero-download" id="s33-seisdil">
<h2>S33-SEISDIL research GeoTIFF — ✅ OK TO DOWNLOAD: YES · 🛑 OK TO SUBMIT: NO</h2>
<p><span class="badge good">UNIQUE vs {unique['surface']['registry_count']} registry rasters: surface max |ρ| {unique['surface']['max_abs_spearman_rho']:.3f}; max 3-px overlap {100*unique['surface']['max_preview_fraction_within_3px']:.1f}%</span>
<span class="badge good">FINAL DOTS: max |ρ| {unique['final_dots']['max_abs_spearman_rho']:.3f}; max 3-px overlap {100*unique['final_dots']['max_candidate_fraction_within_3px']:.1f}%</span>
<span class="badge good">LOCAL FORMAT PASS · single-band float32, EPSG:32611, 3730×3292, [0,1] whole array</span>
<span class="badge bad">HOLDOUT GATE FAILED: 0/4 screen and 0/4 confirmation fold wins</span></p>
<p><b>Hypothesis:</b> geodetic dilatation/shear-rate gradients plus earthquake-intensity ridges might mark permeable fault corridors missing from USGS/INGENIOUS. Mechanism: a fold-trained B1 regional surface gated by the percentile mean of those three signals, then 300 m CELF emission at 37,654 dots. Named non-fault mimic: caldera/aquifer deformation and volcanic seismic swarms without a throughgoing fault.</p>
<p><b>HOLDOUT-DTI</b> (<code>{h['evaluator_version']}</code>, {h['withheld_positives']:,} withheld positives; not an organizer score): screen candidate <code>{h['screen_candidate']:.6f}</code> vs B1 <code>{h['screen_B1']:.6f}</code>; paired Δ <code>{screen['paired_delta_dti']:+.6f}</code>, 95% CI <code>[{screen_ci[0]:+.6f}, {screen_ci[1]:+.6f}]</code>, {screen['fold_wins']}/{screen['n_folds']} folds. Confirmation candidate <code>{h['confirm_candidate']:.6f}</code> vs B1 <code>{h['confirm_B1']:.6f}</code>; paired Δ <code>{confirm['paired_delta_dti']:+.6f}</code>, 95% CI <code>[{confirm_ci[0]:+.6f}, {confirm_ci[1]:+.6f}]</code>, {confirm['fold_wins']}/{confirm['n_folds']} folds. The run card has no standalone candidate-DTI CI; the paired-delta intervals are retained. Feature-alone canaries pass (maximum fold AUC <code>{max_auc:.3f} ≤ 0.90</code>). This negative proxy result is not a leaderboard-score projection.</p>
<p><a class="btn" href="downloads/{filename}">⬇ Download unique S33-SEISDIL GeoTIFF (research only)</a> <a class="btn alt" href="downloads/{zipname}">Single-TIFF .zip</a> <a class="btn alt" href="{card_link}">Run card JSON</a></p>
<table><tbody>
<tr><th>File to download</th><td><code>{filename}</code></td></tr>
<tr><th>Unique submission name</th><td><code>{card['submission_name']}</code></td></tr>
<tr><th>Submission note (≤140 characters)</th><td><code>{esc(card['submission_note'])}</code> ({len(card['submission_note'])}/140)</td></tr>
<tr><th>SHA-256</th><td><code>{card['raster_sha256']}</code></td></tr>
<tr><th>OK to submit?</th><td><b>NO</b>. The independent holdout gate failed. Do not upload or spend a slot.</td></tr>
</tbody></table>
<p class="small"><b>Format caveat:</b> the zeros-outside raster passes this repository's whole-array finite [0,1] audit. The recorded official-format wording calls for null/NaN outside the footprint, and the reported portal error has no retained rejected-file bytes or organizer diagnosis. This local audit does not establish portal acceptance or that zero encoding fixes the error; do not upload this negative artifact.</p>
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
<code>0.0</code> outside the footprint — the whole array is finite in <code>[0, 1]</code>, so this primary
<code>-zeros.tif</code> passes a local whole-array [0,1] range check; the reported portal error's cause and organizer acceptance of zero-outside encoding are unverified. <code>0</code> dots on the catalogue; <code>9/9</code> leakage canaries pass
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
<li>every cell finite and in <code>[0, 1]</code>, with <code>0.0</code> outside the footprint. This is a local range-format check only; organizer acceptance and the cause of the reported range error remain unverified.</li>
</ul></li>
<li>On the DrivenData submission page for competition #306, while signed in as the owner, upload the <code>-zeros.tif</code>, or the <code>.zip</code> that contains exactly that one GeoTIFF.</li>
<li>Paste the unique submission name and the note (&le;140 characters) from the run card.</li>
<li>Check that a weekly slot is free before uploading. This project cannot observe the slot count.</li>
<li>Save the organizer's score receipt into <code>evidence/</code>. Only that receipt makes a score ORGANIZER-CONFIRMED.</li>
</ol>"""


def build_index() -> str:
    body = f"""<div class="panel bad"><b>Current decision · 2026-10-27:</b> NO RASTER IS OK TO SUBMIT. The selector reports <b>0 eligible of 13</b>. This review ran no experiment, generated no new TIFF, selected no slot, and made no upload. The required single method lane is not identifiable in the current task; no hypothesis was self-selected. See <a href="{GITHUB}/knowledge/24_repository_review_20261027.md">the complete three-pass review</a> and <a href="data/20261027_review_card.json">the no-experiment card</a>.</div>
{fsml2_hero()}
{s33_seisdil_hero()}
{a33_r3_llc_hero()}
{dpps_hero()}
{a33_r3_lchc_hero()}
{a33_r2_csht_hero()}
{round3_da_hgcm_hero()}
<h2>What the evidence supports</h2>
<p><b>GEMSDOE32 B2's 0.2778 is USER/OWNER-REPORTED, not ORGANIZER-CONFIRMED.</b> Byte forensics show that B2 is a 37,654-dot exact subset of the 40,199-dot H27-4 emission. Removing low-credit catalogue-flank detections is a plausible metric explanation for the reported increase, not a causal proof against private labels. B2-family rasters are prior art and must not be copied or lightly perturbed. See the <a href="executive-summary.html">nine-site executive comparison</a> and <a href="results.html">score provenance</a>.</p>
<p>No public-score estimate is made. The supplied leader claims 0.3195 and 0.4413 conflict and remain unverified. No DrivenData page or leaderboard was accessed for this review; automatic or manual monitoring is not permitted without recorded written consent or an authorized API.</p>
<h2>Hypothesis and experiment status</h2>
<p>The three ranked 2026-10-27 candidates are qualitative proposals, not a lane assignment or numerical forecast. Cached channels are available locally from hash-pinned owner mirrors; the raw 1 m USGS 3DEP tiles required by the third idea are absent and blocked. See <a href="hypotheses.html">Ranked hypotheses</a> and <a href="latest-review.html">the latest audit</a>.</p>
<div class="panel warn"><b>Provenance:</b> 17 SHA-256-pinned owner-mirror inputs matched their registered pins; the shared 121-channel cache was prepared locally and is git-ignored. Mirror-byte identity does not authenticate organizer origin, licensing, or completeness. The sample template exactly copies catalogue labels on the footprint, so it is grid/footprint metadata only—not truth.</div>
<h2>Operating values</h2>
<div class="grid-2"><div class="panel accent"><h3>Maximize P(Win)</h3><p>Prefer evidence over hopeful score projections. No slot until a fresh, leakage-audited holdout beats a matched baseline and all uniqueness, confirmation, format, and selector gates pass.</p></div><div class="panel accent"><h3>Own the Outcome</h3><p>Make failures visible, preserve provenance, correct misleading pages, and distinguish local format validation from scientific validity and organizer acceptance.</p></div></div>
<p>See <a href="standing-prompt.html">the full operating brief</a> before using any artifact. The only existing current research download is FSML2-CC above; it is explicitly NOT OK TO SUBMIT.</p>
"""
    return page("GEMSDOE33 · Evidence-led fault discovery", body, "index.html")

def build_exec() -> str:
    site_rows = [
        ("GEMSDOE24", "H25-1 · 60,069 dots · 0.2477*", "GVC1 · 0.0859*", "The recent GVC1 result is lower; both values are owner-reported."),
        ("GEMSDOE25", "H19-5 d2.8 · 44,090 dots · 0.2600*", "H66 · 0.0742*", "H66 is a lower gravity-flank attempt; d2.8 belongs to the shared H19-5 emission family."),
        ("GEMSDOE27", "topo-gap · 61,328 dots · 0.2449*", "H29 · 0.2190*; H31 · 0.2250*", "H29 is the strongest supplied independent non-H19-5 comparator; reports are not organizer-confirmed."),
        ("GEMSDOE28", "H36-1 · 37,660 dots · 0.2710*; H27-4 · 0.2708*", "S18 · 0.0217*; S21 · 0.0206*", "The high-score files are in the H19-5 pruning family; the recent sparse results are much lower."),
        ("GEMSDOE30", "d2.8 baseline · 44,090 dots · 0.2600*", "MSDB1 · 0.1462*", "The classic d2.8 raster is shared with GEMSDOE25; MSDB1 is a catalogue-supervised HGB reference."),
        ("GEMSDOE31", "H27-4 solo d2.8 · 40,199 dots · 0.2708*", "H31R-1 · unscored; failed holdout gate", "H27-4 is a prior-art subset in the B2 pruning sequence; do not re-emit it."),
        ("GEMSDOE32", "B2 · 37,654 dots · 0.2778*", "SBIR1 · unscored; failed holdout gate", "Highest supplied focus-site report; exact subset of H27-4, not a verified independent discovery."),
        ("GEMSDOE33", "H33-D analog tip/stepover · 41,865 dots · 0.2632* (retired)", "S33-SEISDIL · 0.0963*", "Local research candidates are negative or duplicate-blocked; no GEMSDOE33 raster is submission-approved."),
        ("GEMSDOE36", "Anderson · 38,854 dots · 0.2750*", "KPL36 · 0.1647*", "Anderson contains B2 plus 1,200 dots; not an independent high-scoring surface."),
    ]
    rows = "\n".join(
        f"<tr><th>{esc(site)}</th><td>{esc(best)}</td><td>{esc(recent)}</td>"
        f"<td>Not estimable</td><td>{esc(reading)}</td><td>NO</td></tr>"
        for site,best,recent,reading in site_rows
    )
    body = f"""{fsml2_hero()}
<h2>Executive comparison · GEMSDOE24, 25, 27, 28, 30, 31, 32, 33, 36</h2>
<div class="panel bad"><b>Current decision: NO RASTER IS OK TO SUBMIT.</b> The selector reports <b>0 eligible of 13</b>. No experiment or TIFF was produced in this 2026-10-27 review because the single assigned method lane is not specified. The existing FSML2-CC file above is downloadable for research only; its holdout is negative. No slot was selected and no upload was made.</div>
<p>All public values below are <b>USER/OWNER-REPORTED, NOT ORGANIZER-CONFIRMED</b>. “Not estimable” means the available catalogue holdout does not provide a calibrated leaderboard-score estimate. No user-supplied leaderboard score is represented as current or verified.</p>
<div class="scroll"><table><thead><tr><th>Focus site</th><th>Highest supplied report</th><th>Other recent report in supplied brief</th><th>Public-score estimate</th><th>Executive read</th><th>Submit?</th></tr></thead><tbody>{rows}</tbody></table></div>
<p>Full 130-row USER-REPORTED score ledger (blank values preserved): <a href="{GITHUB}/registry/user_reported_scores_20261026.csv">CSV</a>. The pinned raster inventory contains 21 files and is not the complete set of all historical site submissions; hash pins verify mirror bytes only.</p>
<h3>Why GEMSDOE32 B2 is reported at 0.2778</h3>
<p>Byte-level forensics show a 37,654-dot B2 raster that is an exact subset of the 40,199-dot H27-4 raster: <b>2,545 deletions, zero additions</b>. H27-4 is itself a thinning of the 44,090-dot d2.8 H19-5 emission. The reported score sequence is 0.2600* → 0.2708* → 0.2778*. With DTI α=0.2 for weighted false positives, β=0.8 for weighted false negatives, and a 300 m triangular kernel, pruning detections near already mapped traces may reduce redundant false-positive cost while losing little weighted recall. This is a <b>plausible mechanism, not a causal demonstration</b>: the organizer's private truth and score-to-file receipt are unavailable. Do not copy or perturb B2-family rasters.</p>
<h3>HOLDOUT-DTI is not a public-score estimate</h3>
<p>The FSML2-CC candidate failed its matched CSHT comparisons on screen and independent confirmation; both use <code>gems-segment-pooled-v1</code>, 60,988 withheld positives, and 10 km spatial block-bootstrap 95% CIs. Details are in <a href="{GITHUB}/knowledge/23_fsml_results_20261026.md">the saved report</a> and <a href="{GITHUB}/evidence/fsml2_run_card_20261026.json">run card</a>. The informational fixed H19-5 surface is not fold-safe; do not treat it or any HOLDOUT-DTI value as a contest score.</p>
<h3>Safe workflow for any future candidate</h3>
<ol><li>Work only inside one explicit, assigned method lane; if none is identifiable, stop before experiments.</li><li>Freeze a preregistered hypothesis, mechanism, named non-fault mimic, source/availability check, and matched evaluation design.</li><li>Use whole-segment buffered hide-and-recover folds; derive all catalogue features from fold-visible faults and mask them pixel-exactly. Use the shared evaluator/writer, pooled DTI α=0.2, β=0.8, 300 m triangular kernel, and report evaluator version, withheld positives, and 95% CI.</li><li>Run each feature-alone leakage canary; AUC &gt;0.90 is leakage-suspect. Check continuous-surface uniqueness before placement and final dots. Stop if rank-correlation &gt;0.90 or more than 70% of candidate dots lie within 3 px of a registry raster.</li><li>Reopen saved bytes for CRS, shape, transform, dtype and value validation. Require screen, independent confirmation, uniqueness and selector gates before any submission decision. This workspace does not choose a weekly slot or upload.</li></ol>
<div class="panel warn"><b>Outside-footprint convention remains unresolved.</b> The repository records null/NaN-outside wording, but no organizer receipt settles the reported range error or confirms zero-outside files. Local format success is not portal acceptance. Check the current official contract before any future approved upload.</div>
<p>Official competition, USGS and DOE links are listed on the <a href="sources.html">sources page</a>; none was freshly authenticated in this review. See <a href="hypotheses.html">the ranked proposal slate</a> and <a href="latest-review.html">the full three-pass audit</a>.</p>
"""
    return page("Executive comparison & submission guidance · GEMSDOE33", body, "executive-summary.html")

def build_results() -> str:
    body = f"""<h2>Results and score provenance</h2>
<div class="panel bad"><b>No organizer-confirmed score or exact submission-page receipt is retained here.</b> Historical values marked * are USER/OWNER-REPORTED. No leaderboard was accessed or refreshed in this review. No numeric leaderboard-score projection is made.</div>
<p>See the <a href="{GITHUB}/registry/user_reported_scores_20261026.csv">130-row user-reported score ledger</a>, <a href="{GITHUB}/registry/leaderboard_review.json">dated score-source review</a>, and <a href="{GITHUB}/registry/irregularities.json">irregularity register</a>. The latest current selector snapshot is <a href="{GITHUB}/evidence/submission_selection_20261027.json">0 eligible of 13</a>.</p>
<h3>GEMSDOE32 B2 byte forensics</h3>
<p>The 37,654-dot B2 raster is an exact subset of H27-4: 2,545 cells were deleted and none added. That is a measured set relation. The 0.2778* public report is not organizer-confirmed, and no exact bytes/receipt association is available. Pruning low-credit detections near known traces may explain the metric gain, but private truth is not available to establish causation. Full analysis: <a href="{GITHUB}/knowledge/22_b2_forensics_and_fsml_slate_20261026.md">B2 forensics</a>.</p>
<h3>FSML2-CC — negative research result</h3>
<p><b>HOLDOUT-DTI</b> (α=0.2, β=0.8, 300 m triangular kernel; `gems-segment-pooled-v1`; 60,988 withheld positives; 10 km spatial block-bootstrap 95% CI): screen candidate 0.110427 [0.1009, 0.1203] vs CSHT 0.135672 [0.1241, 0.1477], paired difference −0.025246 [−0.0355, −0.0151], 0/4 folds; independent confirmation candidate 0.103077 [0.0941, 0.1129] vs CSHT 0.132066 [0.1201, 0.1440], paired difference −0.028989 [−0.0410, −0.0174], 0/4 folds. The candidate is unique against the checked registry but fails the holdout promotion gate. No public score is estimated. See <a href="{GITHUB}/knowledge/23_fsml_results_20261026.md">full report</a> and <a href="{GITHUB}/evidence/fsml2_run_card_20261026.json">run card</a>.</p>
<h3>Historical leaderboard context</h3>
<p>The supplied leader claims 0.3195 and 0.4413 conflict and remain unverified. In the nine focus sites, B2's 0.2778* is the highest supplied historical value. No file in this repository has an organizer receipt binding score, account, timestamp and exact raster bytes. Do not convert a local holdout result to a public score.</p>
"""
    return page("Results & score provenance · GEMSDOE33", body, "results.html")

def build_hypotheses() -> str:
    slate = reg("hypotheses_20261027.json")
    cards = []
    for h in slate.get("hypotheses", []):
        layers = "; ".join(h.get("layers", []))
        source = h.get("official_source_and_availability", {})
        url = source.get("url", "")
        source_link = f'<a href="{esc(url)}">{esc(source.get("source_name", "official source"))}</a>' if url else "No additional official source listed"
        cards.append(f"""<div class="panel warn"><h3>Rank {h['rank']}: {esc(h['title'])} <code>{esc(h['id'])}</code></h3>
<p><b>Layers:</b> {esc(layers)}</p><p><b>Physical signature:</b> {esc(h['physical_signature'])}</p>
<p><b>Missing-fault mechanism:</b> {esc(h['why_it_may_find_catalogue_missing_faults'])}</p>
<p><b>Difference / prior art:</b> {esc(h['difference_from_repository_prior_art'])}</p>
<p><b>Named non-fault mimic:</b> {esc(h['named_non_fault_mimic'])}</p>
<p><b>Qualitative rank:</b> {esc(h['qualitative_expected_improvement'])} · <b>Cost:</b> {esc(h['implementation_cost'])}</p>
<p><b>Official source:</b> {source_link}. <b>Availability:</b> {esc(source.get('status', 'not checked'))} {esc(source.get('local_check', ''))}</p>
<p><b>Holdout status:</b> {esc(h['holdout_status'])}</p></div>""")
    shared = slate.get("shared_validation_requirements", {})
    body = f"""<h2>Ranked geological hypotheses — proposals only</h2>
<div class="panel bad"><b>No lane assigned; no hypothesis implemented or scored.</b> The task refers to a “single method paragraph below” but no identifiable assigned method paragraph is present. The ranking below is qualitative planning, not a lane assignment, not permission to experiment, not a novelty guarantee, and not a numeric DTI forecast. Full machine-readable slate: <a href="data/hypotheses_20261027.json">registry/hypotheses_20261027.json</a>.</div>
<p>Ranking balances plausible geology, implementation cost, repository prior art, and local availability. The 17 local inputs are SHA-pinned owner mirrors, not organizer-authenticated payloads. Official URLs are retained for manual review and were not re-fetched on 2026-10-27.</p>
{''.join(cards)}
<h3>Shared gates before any future experiment</h3>
<ul><li><b>Evaluator:</b> {esc(shared.get('evaluator', ''))}</li><li><b>Fold design:</b> {esc(shared.get('split', ''))}</li><li><b>Metric:</b> {esc(shared.get('metric', ''))}</li><li><b>Leakage:</b> {esc(shared.get('leakage', ''))}</li><li><b>Uniqueness:</b> {esc(shared.get('uniqueness', ''))}</li><li><b>Promotion:</b> {esc(shared.get('promotion', ''))}</li></ul>
<p>Tracked-code prior-art search found no exact implementation of these specific formulations. H27-BIFURCATION is explicitly adjacent to existing ridge/network work; H27-CATCHMENT-PROFILE is blocked until official raw 1 m tiles are locally obtainable and audited.</p>
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
    body = f"""<h2>Registered Primary Sources & Data Provenance</h2>
<div class="panel warn"><b>Not freshly authenticated in this 2026-10-27 review.</b> The links below are preserved official/primary-source references for manual review. No DrivenData page or leaderboard was accessed; external-source availability and licence must be checked before future use.</div>
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
<p>The pin list records 17 owner-mirror inputs restored and hash-verified in the 2026-10-27 working session; the receipt is <code>evidence/input_grid_audit.json</code>. These large rasters and derived cache are git-ignored and are not published with this static site. Hashes identify mirror bytes only and do not authenticate organizer provenance.</p>
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
    selection = read_json(ROOT / "evidence/submission_selection_20261027.json")
    inputs = read_json(ROOT / "evidence/input_grid_audit.json")
    card = read_json(ROOT / "evidence/20261027_review_card.json")
    n_cards = len(selection.get("candidates", []))
    candidates = "".join(
        f"<tr><td>{esc(item.get('campaign') or '—')}</td><td><code>{esc(item.get('submission_name') or item.get('file') or '—')}</code></td>"
        f"<td>{esc(item.get('verdict') or '—')}</td><td>{'ELIGIBLE' if item.get('eligible') is True else 'BLOCKED'}</td></tr>"
        for item in selection.get("candidates", [])
    )
    body = f"""<h2>2026-10-27 repository review — three passes</h2>
<div class="panel bad"><b>{esc(selection.get('decision', 'NO RASTER IS OK TO SUBMIT'))}</b> No experiment was run in this review; no new TIFF was generated, no competition slot was chosen, and no upload was made. The assigned single method lane remains unidentified. Review card status: <code>{esc(card.get('status', 'missing'))}</code>.</div>
<p><a href="{GITHUB}/knowledge/24_repository_review_20261027.md">Full review report</a> · <a href="data/20261027_review_card.json">No-experiment JSON card</a> · <a href="data/submission_selection_20261027.json">Selector evidence</a>.</p>
<h3>Pass 1 — input and baseline inspection</h3>
<p>Restored and SHA-256 checked {inputs.get('registered_inputs', {}).get('verified', 17)} of {inputs.get('registered_inputs', {}).get('expected', 17)} registered SHA-256-pinned owner-mirror inputs. The common preparer built 121 cached channels; the cache is ignored. The sample-template positive set exactly matches catalogue labels on the finite footprint, so it is not used as truth.</p>
<h3>Pass 2 — adversarial review</h3>
<ul><li>Corrected the README's stale A33-R2-HMDT lane claim and the misleading “generated this session” language.</li><li>Replaced the stale 0-of-12 selector description with 0 eligible of {n_cards} current cards.</li><li>Updated the score ledger with four user-supplied lower-scoring focus-site reports; they remain USER-REPORTED.</li><li>Marked the H19-5 re-derivation recommendation as already tested on the cached stack; no same-stack retuning is proposed.</li><li>Prior-art search found no exact implementation of the three current formulations, but ridge/network overlap is material; novelty beyond this repository is not claimed.</li></ul>
<h3>Pass 3 — final reconciliation</h3>
<p>Updated README, standing brief, machine-readable slate, irregularity register, result pages and this site page. Candidate hypotheses remain untested because the lane is absent. Raw 1 m USGS 3DEP tiles are not in the local inputs; the third candidate is blocked. No current contest-score estimate is made.</p>
<h3>Selector audit ({n_cards} saved run cards)</h3>
<div class="scroll"><table><thead><tr><th>Campaign</th><th>Saved candidate</th><th>Verdict</th><th>Selector result</th></tr></thead><tbody>{candidates}</tbody></table></div>
<p><b>Current decision:</b> {esc(selection.get('decision', 'NO RASTER IS OK TO SUBMIT'))}.</p>
<h3>Automated verification</h3>
<p>Final post-restoration command <code>PYTHON=.venv/bin/python GEMS_DATA_DIR=$PWD/.cache/gemsdata bash scripts/run_checks.sh</code> completed with <b>177 passed</b>. It rebuilt the site, verified 17/17 owner-mirror input pins, reran the sample-template diagnostic, confirmed the selector's 0/13 result, compiled Python files and passed <code>git diff --check</code>. This is repository/test evidence, not a new scientific experiment or organizer validation.</p>
<h3>Input provenance and limits</h3>
<div class="panel warn"><b>{esc(inputs.get('evidence_class', 'MEASURED from local owner-mirror bytes'))}.</b> Pins establish identity with recorded mirror bytes only, not organizer origin, completeness or licensing. Data/cache are not published by GitHub Pages. No DrivenData page or leaderboard was contacted.</div>
<p>Existing FSML2-CC is an older, negative research artifact. It passed the checked-registry uniqueness and local-format audits but failed holdout promotion; it is OK TO DOWNLOAD FOR RESEARCH, NOT OK TO SUBMIT. Its run card and candidate binary are linked on the overview.</p>
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
        ("round4_run_card_20261026.json", "round4-run-card.json"),
        ("run_card_g33_20261026.json", "current-run-card.json"),
        ("round3_da_hgcm_run_card_20261025.json", "round3-da-hgcm-run-card.json"),
        ("promotion_gate_20261025.json", "current-promotion-gate.json"),
        ("focus_raster_audit_20261025.json", "focus-raster-audit.json"),
    ):
        payload = read_json(ROOT / "evidence" / source)
        (research / name).write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
    data_dir = DOCS / "data"
    data_dir.mkdir(exist_ok=True)
    for source, destination in (
        (ROOT / "evidence" / "20261027_review_card.json", data_dir / "20261027_review_card.json"),
        (ROOT / "evidence" / "submission_selection_20261027.json", data_dir / "submission_selection_20261027.json"),
        (ROOT / "registry" / "hypotheses_20261027.json", data_dir / "hypotheses_20261027.json"),
    ):
        if source.exists():
            payload = json.loads(source.read_text(encoding="utf-8"))
            destination.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8")
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
    for evidence_name in ("round4_run_card_20261026.json", "round4_input_feasibility_20261026.json"):
        payload = read_json(ROOT / "evidence" / evidence_name)
        if payload:
            (data_dir / evidence_name).write_text(
                json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8"
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
