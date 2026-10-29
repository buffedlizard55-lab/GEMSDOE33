#!/usr/bin/env python3
"""Build the static, evidence-led GitHub Pages site for GEMSDOE33.

Generates responsive, evidence-bounded static research pages for GitHub Pages:
  - index.html: Current decision and research-only artifact status.
  - executive-summary.html: Safe workflow for a future slot-cleared submission.
  - results.html: Score provenance and holdout evidence boundaries.
  - hypotheses.html: Current three-proposal source-gated slate plus historical prior art.
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
<p>DrivenData #306 · evidence-led research · review status 2026-10-29</p><nav class="nav" aria-label="Primary">{links}</nav></div></header>
<main class="wrap">{body}</main>
<footer><div class="wrap">Generated from repository evidence by <code>scripts/build_site.py</code>. No candidate is slot-approved and no DrivenData upload was made from this workspace. The selector checks declared evidence consistency, not the independent authenticity of measurements. A local format audit is not scientific validation or organizer acceptance. Owner reports, measured diagnostics, model outputs and official sources are distinguished in the evidence.</div></footer>
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
<h2>NEW UNIQUE TIF (2026-10-26, FSML2-CC) — ✅ OK TO DOWNLOAD: YES · 🛑 OK TO SUBMIT: NO (verdict: negative)</h2>
<p><span class="badge good">UNIQUE vs 22 registry rasters: surface max 3-px overlap {100*surf['max_preview_fraction_within_3px']:.1f}% ≤ 70%; final dots {100*u['final_dots_max_3px_overlap']:.1f}%, max |ρ| {u['final_dots_max_abs_spearman']:.3f} — comparisons are limited to the pinned registry</span>
<span class="badge good">FORMAT PASS: single-band float32, EPSG:32611, 3730×3292, whole array finite in [0,1] (values exactly {{0,1}})</span>
<span class="badge bad">HOLDOUT GATE FAILED vs CSHT (0/4 + 0/4 folds) — DO NOT SPEND A SLOT</span></p>
<p><b>What it is:</b> corroboration-count fusion — 4 fold-safe spy-PU physics experts + 2 label-free lines
(multiscale geopotential worms; strike-integrated LiDAR scarp lines); a pixel ranks by how many independent
lines place it in their top decile. CELF-300 m dotted emission, {bud:,} dots, 0 on catalogue. It is the fold-safe
re-derivation of the H19-5 multi-line idea that produced the 0.2778* B2 family (<a href="https://github.com/buffedlizard55-lab/GEMSDOE33/blob/main/knowledge/22_b2_forensics_and_fsml_slate_20261026.md">forensics + slate</a>).</p>
<div class="scroll"><table><thead><tr><th>File to download</th><th>HOLDOUT-DTI (gems-segment-pooled-v1, 60,988 withheld positives) — NOT a leaderboard estimate</th><th>Unique vs all 9 focus sites' registry?</th><th>OK to submit?</th></tr></thead><tbody>
<tr><td><code>{sub['file']}</code></td><td>screen {hs[sk]['dti']:.4f} [{hs[sk]['ci95'][0]:.4f}, {hs[sk]['ci95'][1]:.4f}] vs CSHT {hs[ck]['dti']:.4f} (paired Δ {ps['paired_delta_dti']:+.4f} [{ps['paired_delta_ci95'][0]:+.4f}, {ps['paired_delta_ci95'][1]:+.4f}], {ps['fold_wins']}/4); confirmation {hc[sk]['dti']:.4f} vs {hc[ck]['dti']:.4f} (Δ {pc['paired_delta_dti']:+.4f} [{pc['paired_delta_ci95'][0]:+.4f}, {pc['paired_delta_ci95'][1]:+.4f}], {pc['fold_wins']}/4). <b>Public score: not estimable</b> — the catalogue proxy anti-ranks the public B2 ladder on the emission axis (measured), so no numeric projection is defensible.</td><td><b>YES</b> — passes surface + final-dot guards vs all 22 registry rasters (B2-family included)</td><td><b>NO</b> — holdout gate failed; research only</td></tr>
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


def r7_pcsup_hero() -> str:
    card = read_json(ROOT / "evidence" / "a33_r7_pcsup_run_card_20261028.json")
    if not card:
        return ""
    sub = card["submission"]; hs = card["holdout_dti"]["screen"]; hc = card["holdout_dti"]["confirmation"]
    u = card["correlation_overlap_vs_registry"]
    return f"""<div class="hero-download" id="r7-pcsup">
<h2>A33-R7-PCSUP TIFF (2026-10-28) — 🛑 NOT UNIQUE UNDER LANE RULE · research artifact only · NOT OK TO SUBMIT</h2>
<p><span class="badge bad">PRE-PLACEMENT SURFACE DUPLICATE STOP: max 3-px overlap {100*u['surface_max_3px_overlap']:.2f}% &gt; 70% (21-raster registry); max |ρ| {u['surface_max_abs_spearman']:.4f}. Final dots passed (max overlap {100*u['final_dots_max_3px_overlap']:.2f}%) but cannot cure the failed surface guard.</span>
<span class="badge good">FORMAT PASS ONLY (not science/uniqueness): single-band float32, EPSG:32611, 3730×3292, whole array finite in [0,1], 37,654 dots</span>
<span class="badge bad">The saved holdout numbers are exploratory because the lane should have stopped at the failed surface guard. Separate matched-random screen also failed (Δ {hs['paired_delta_vs_matched_random']:+.4f}, CI spans 0). Estimated leaderboard score: NOT ESTIMABLE.</span></p>
<p><b>What it is:</b> supervised subsurface-only HGB on phase-congruency + potential-field channels (no topo/LiDAR), CELF-300 m emission. A post-run evidence audit found the pre-placement surface exceeded the hard overlap threshold; per protocol, log as duplicate/drift and stop. See <a href="https://github.com/buffedlizard55-lab/GEMSDOE33/blob/main/knowledge/31_r7_pcsup_lane_correction_20261028.md">correction and scope</a> and <a href="https://github.com/buffedlizard55-lab/GEMSDOE33/blob/main/knowledge/30_phcong_results_20261028.md">A33-R7 results</a>.</p>
<p><a class="btn alt" href="downloads/{sub['file']}">Download archived PCSUP TIFF (NOT unique under protocol; do not submit)</a> <a class="btn alt" href="downloads/{sub['zip']}">Single-TIFF .zip (research archive only)</a> <a class="btn alt" href="data/a33_r7_pcsup_run_card_20261028.json">Run card JSON</a></p><table><tbody>
<tr><th>Research artifact name (not approved for submission)</th><td><code>{sub['name']}</code></td></tr>
<tr><th>Note (≤140)</th><td><code>{esc(sub['note'])}</code></td></tr>
<tr><th>SHA-256</th><td><code>{card['raster_sha256']}</code></td></tr>
<tr><th>Exploratory HOLDOUT-DTI (not valid promotion evidence)</th><td>gems-segment-pooled-v1, 60,988 withheld positives; screen {hs['candidate']:.6f} [{hs['ci95'][0]:.6f}, {hs['ci95'][1]:.6f}], confirmation {hc['candidate']:.6f} [{hc['ci95'][0]:.6f}, {hc['ci95'][1]:.6f}]. NOT a leaderboard estimate; surface duplicate guard failed before placement.</td></tr>
<tr><th>Decision</th><td><b>✅ DOWNLOAD YES · 🛑 SUBMIT NO</b></td></tr>
</tbody></table></div>"""


def basestep_hero() -> str:
    """Newest unique research artifact banner (A33-R6-BASESTEP), built from its run card."""
    card = read_json(ROOT / "evidence" / "a33_r6_basestep_run_card_20261027.json")
    if not card:
        return ""
    sub = card["submission"]; hs = card["holdout_dti"]["screen"]; hc = card["holdout_dti"]["confirmation"]
    u = card["correlation_overlap_vs_registry"]
    note = sub["note"]
    return f"""<div class="hero-download" id="basestep">
<h2>NEW UNIQUE TIF (2026-10-27, A33-R6-BASESTEP) — ✅ OK TO DOWNLOAD: YES · 🛑 OK TO SUBMIT: NO (verdict: negative)</h2>
<p><span class="badge good">UNIQUE vs all 21 registry rasters (all 9 focus sites + local GEMSDOE33): surface max |ρ| {u['surface_max_abs_spearman']:.4f}, max 3-px overlap {100*u['surface_max_3px_overlap']:.2f}% ≤ 70%; final dots max |ρ| {u['final_dots_max_abs_spearman']:.4f}, max 3-px overlap {100*u['final_dots_max_3px_overlap']:.2f}% ≤ 70% — comparisons are limited to the pinned registry</span>
<span class="badge good">FORMAT PASS: single-band float32, EPSG:32611, 3730×3292, template 100 m geotransform, whole array finite in [0,1] (37,654 binary dots), 0 NaN inside footprint</span>
<span class="badge bad">HOLDOUT GATE FAILED — screen {hs['candidate']:.4f} [{hs['ci95'][0]:.4f}, {hs['ci95'][1]:.4f}] vs recorded regional baseline 0.112418 (CI spans the unpaired recorded baseline); confirmation {hc['candidate']:.4f} [{hc['ci95'][0]:.4f}, {hc['ci95'][1]:.4f}] vs 0.115122; vs matched-random control Δ {hs['paired_delta_vs_matched_random']:+.4f} [{hs['paired_delta_ci95'][0]:+.4f}, {hs['paired_delta_ci95'][1]:+.4f}], {hs['fold_wins']}/4 folds — DO NOT SPEND A SLOT</span></p>
<p><b>What it is:</b> label-free basement-depth-step × conductive-cover × gravity-margin-edge × magnetic-basement-fabric detector targeting blind listric fault soles under piedmont cover; thresholds were fit using the full catalogue before the split, a protocol violation; the holdout is not fold-safe; CELF-300 m placement of 37,654 dots, &gt;2 px off the USGS/INGENIOUS catalogue. Preregistered in <a href="https://github.com/buffedlizard55-lab/GEMSDOE33/blob/main/knowledge/26_thk_cond_slate_20261027.md">knowledge/26_thk_cond_slate_20261027.md</a> (Candidate 4).</p>
<div class="scroll"><table><thead><tr><th>File to download</th><th>HOLDOUT-DTI (gems-segment-pooled-v1, 60,988 withheld positives) — NOT a leaderboard estimate</th><th>Unique vs all 9 focus sites' registry?</th><th>OK to submit?</th></tr></thead><tbody>
<tr><td><code>{sub['file']}</code></td><td>screen {hs['candidate']:.4f} vs recorded B1 0.112418 (CI spans the unpaired recorded baseline); confirmation {hc['candidate']:.4f} vs 0.115122; vs matched-random Δ {hs['paired_delta_vs_matched_random']:+.4f} [{hs['paired_delta_ci95'][0]:+.4f}, {hs['paired_delta_ci95'][1]:+.4f}], {hs['fold_wins']}/4 folds. <b>Estimated leaderboard score: not estimable</b>.</td><td><b>YES</b> — surface max |ρ| {u['surface_max_abs_spearman']:.4f} ≤ 0.90; max 3-px {100*u['surface_max_3px_overlap']:.1f}% ≤ 70%; final dots max |ρ| {u['final_dots_max_abs_spearman']:.4f} ≤ 0.90; max 3-px {100*u['final_dots_max_3px_overlap']:.1f}% ≤ 70% (21 pinned registry rasters)</td><td><b>NO</b> — both holdout splits failed their gates; research only</td></tr>
</tbody></table></div>
<p><a class="btn" href="downloads/{sub['file']}">⬇ Download unique A33-R6-BASESTEP GeoTIFF (research only)</a> <a class="btn alt" href="downloads/{sub['zip']}">Single-TIFF .zip</a> <a class="btn alt" href="downloads/gemsdoe33-a33-r6-basestep-37654-20261027-4e0c37d1d539-nan.tif">NaN-outside twin</a> <a class="btn alt" href="downloads/receipt-gemsdoe33-a33-r6-basestep-37654-20261027-4e0c37d1d539.json">Validator receipt JSON</a> <a class="btn alt" href="data/a33_r6_basestep_run_card_20261027.json">Run card JSON</a></p>
<table><tbody>
<tr><th>Unique submission name</th><td><code>{sub['name']}</code></td></tr>
<tr><th>Note (≤140 characters)</th><td><code>{esc(note)}</code> ({len(note)}/140)</td></tr>
<tr><th>SHA-256 (.tif)</th><td><code>{card['raster_sha256']}</code></td></tr>
<tr><th>Decision</th><td><b>✅ DOWNLOAD YES · 🛑 SUBMIT NO.</b> Selector snapshot 2026-10-28: 0 eligible of 16 run cards. Slots spent: 0.</td></tr>
</tbody></table>
<p class="small"><b>Range-error note:</b> every cell of this <code>-zeros.tif</code> is finite and in [0,1] (re-opened and checked byte-wise), so its values cannot themselves violate a [0,1] range check. The <code>-nan.tif</code> twin follows the recorded null/NaN-outside wording. Portal acceptance remains unverified; do not upload this negative artifact.</p>
</div>"""


def pfrt_hero() -> str:
    """Newest unique research artifact banner (PFRT), built from its run card."""
    card = read_json(ROOT / "evidence" / "pfrt_run_card_20261027.json")
    if not card:
        return ""
    sub = card["submission"]; hs = card["holdout_dti"]["screen"]; hc = card["holdout_dti"]["confirmation"]
    ps, pc = hs["paired_vs_csht"], hc["paired_vs_csht"]; u = card["correlation_overlap_vs_registry"]
    sk, ck = "PFRT@37654", "A33_R2_CSHT@37654"
    return f"""<div class="hero-download" id="pfrt">
<h2>NEW UNIQUE TIF (2026-10-27, PFRT) — ✅ OK TO DOWNLOAD: YES · 🛑 OK TO SUBMIT: NO (verdict: negative)</h2>
<p><span class="badge good">UNIQUE vs 22 registry rasters: surface max 3-px overlap {100*u['surface_max_3px']:.1f}% ≤ 70%, max |ρ| {u['surface_max_abs_spearman']:.3f}; final dots {100*u['final_dots_max_3px']:.1f}% — comparisons are limited to the pinned registry</span>
<span class="badge good">FORMAT PASS: single-band float32, EPSG:32611, 3730×3292, whole array finite in [0,1] (values exactly {{0,1}}), 0 outside footprint</span>
<span class="badge bad">HOLDOUT GATE FAILED vs CSHT — DO NOT SPEND A SLOT</span></p>
<p><b>What it is:</b> PFRT listric dip-projection — basement-edge crests (depth-to-basement gradient × gravity HG) displaced updip by depth·cot(dip), dip 50°/60°, before CELF-300 m emission. Label-free, 37,654 dots, 0 on catalogue. The displacement is the tested mechanism; unshifted gradient classifiers are prior art.</p>
<div class="scroll"><table><thead><tr><th>File to download</th><th>HOLDOUT-DTI (gems-segment-pooled-v1, 60,988 withheld positives) — NOT a leaderboard estimate</th><th>Unique vs all 9 focus sites' registry?</th><th>OK to submit?</th></tr></thead><tbody>
<tr><td><code>{sub['file']}</code></td><td>screen {hs[sk]['dti']:.4f} [{hs[sk]['ci95'][0]:.4f}, {hs[sk]['ci95'][1]:.4f}] vs CSHT {hs[ck]['dti']:.4f} (paired Δ {ps['paired_delta_dti']:+.4f} [{ps['paired_delta_ci95'][0]:+.4f}, {ps['paired_delta_ci95'][1]:+.4f}], {ps['fold_wins']}/4); confirmation {hc[sk]['dti']:.4f} vs {hc[ck]['dti']:.4f} (Δ {pc['paired_delta_dti']:+.4f} [{pc['paired_delta_ci95'][0]:+.4f}, {pc['paired_delta_ci95'][1]:+.4f}], {pc['fold_wins']}/4). <b>Estimated leaderboard score: not estimable</b> — no validated transfer from catalogue-proxy HOLDOUT-DTI to the private score exists (knowledge/22 §3); the only labelled numbers are HOLDOUT-DTI and USER-REPORTED historical scores.</td><td><b>YES</b> — passes surface + final-dot guards vs all 22 registry rasters (all 9 focus sites included)</td><td><b>NO</b> — holdout gate failed on both splits; research only</td></tr>
</tbody></table></div>
<p><a class="btn" href="downloads/{sub['file']}">⬇ Download unique PFRT GeoTIFF (research only)</a> <a class="btn alt" href="downloads/{sub['zip']}">Single-TIFF .zip</a> <a class="btn alt" href="downloads/{sub['nan_twin']}">NaN-outside twin</a> <a class="btn alt" href="data/pfrt_run_card_20261027.json">Run card JSON</a></p>
<table><tbody>
<tr><th>Unique submission name</th><td><code>{sub['name']}</code></td></tr>
<tr><th>Note (≤140 characters)</th><td><code>{esc(sub['note'])}</code> ({sub['note_characters']}/140)</td></tr>
<tr><th>SHA-256 (.tif)</th><td><code>{card['raster_sha256']}</code></td></tr>
<tr><th>Decision</th><td><b>✅ DOWNLOAD YES · 🛑 SUBMIT NO.</b> Failed gates: screen_beats_current_best, independent_confirmation. Selector snapshot 2026-10-28: 0 eligible of 16 run cards. Slots spent: 0.</td></tr>
</tbody></table>
<p class="small"><b>Range-error note:</b> every cell of this <code>-zeros.tif</code> is finite and in [0,1] (independent re-audit: pass, min 0.0 / max 1.0, 0 NaN), so its values cannot themselves violate a [0,1] range check. Portal acceptance remains unverified; do not upload this negative artifact.</p>
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


def review_warning() -> str:
    return """<div class="panel warn"><b>Historical 2026-10-28 safety review (superseded by the 2026-10-29 source/experiment status above).</b>
The BASESTEP and THKCOND historical holdouts used full-catalogue-fitted thresholds and composite-only canaries;
they are exploratory, not valid protocol evidence. Their runners are disabled. The selector now reassesses
hash-bound underlying evidence, but this cannot independently authenticate claimed measurements.
<a href="https://github.com/buffedlizard55-lab/GEMSDOE33/blob/main/knowledge/27_20261028_safety_review.md">Read the audit</a>.</div>"""


def build_index() -> str:
    body = f"""<div class="panel warn"><b>Latest review — 2026-10-29:</b> A33-R7 is exhausted at 3/3; no current method paragraph is identifiable. Three ranked proposals are recorded, but 0/3 pass source-payload/schema/license/coverage checks. No experiment, candidate TIFF, slot selection or upload occurred. See <a href="hypotheses.html">the proposal slate</a> and <a href="sources.html">official-source audit</a>.</div>{nine_site_index_panel()}{review_warning()}<h2>Historical artifact cards — none is a current submission recommendation</h2>{r7_pcsup_hero()}
{basestep_hero()}
{pfrt_hero()}
{fsml2_hero()}
{s33_seisdil_hero()}
{a33_r3_llc_hero()}
{dpps_hero()}
{a33_r3_lchc_hero()}
{a33_r2_csht_hero()}
{round3_da_hgcm_hero()}
<h2>Current decision (2026-10-29)</h2>
<div class="panel bad"><b>NO FILE IS OK TO SUBMIT.</b> The selector found 0 eligible files among 19 checked. A33-R7 is exhausted at 3/3; no current method paragraph is identifiable, and 0/3 new proposals pass the official-payload/source audit. No experiment, candidate TIFF, slot selection or upload occurred. Historical PCSUP also failed its pre-placement surface guard (86.08% within 3 px &gt; 70%); BASESTEP/THKCOND have separate protocol defects. Their old artifacts remain research/archive only.</div>
<p><b>Best reported focus-site artifact:</b> GEMSDOE32 B2, <code>h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros</code>, with <b>0.2778 USER/OWNER-REPORTED (NOT ORGANIZER-CONFIRMED)</b>. Raster forensics reproduced it as deletion-only pruning of GEMSDOE28 H27-4; it is prior art and must not be copied or lightly altered. No current candidate has demonstrated a valid basis to predict a higher competition score. HOLDOUT-DTI is a catalogue proxy, not a leaderboard score estimate. See the <a href="executive-summary.html">nine-site executive summary</a> and <a href="results.html">score provenance</a>.</p>
<h2>What can be concluded about the cited scores?</h2>
<p>Historical values in owner pages and the prompt are not organizer-confirmed without a submission receipt linked to the exact file. The prompt's current-leader values 0.3195 and 0.4413 conflict and are unverified here. The GEMSDOE28 owner page was recorded as labeling H27-4 unscored/research-only, so the premise that this raster earned 0.2708 is unresolved. These reports motivate forensic research; they are not independent validation or a score forecast.</p>
<p>Do not refresh or copy the official leaderboard without the permission/API described in the project's terms review. See <a href="irregularities.html">irregularities</a> for known conflicts.</p>
<h2>Hypothesis and experiment status</h2>
<p>The current three-item slate (aqueous-chemistry mixing fronts, depth-persistent MT conductance walls, and cross-catchment 3DEP channel profiles) is recorded in <a href="hypotheses.html">the hypotheses page</a>. It is proposal-only; no method lane is assigned and no experiment or fourth A33-R7 run is authorized. 0/3 hypotheses pass the official-payload/schema/license/coverage gate. See <a href="data/hypothesis_slate_20261029.json">slate JSON</a>, <a href="data/source_preflight_20261029.json">source preflight</a>, and the <a href="latest-review.html">latest review</a>. Historical PCSUP's pre-placement surface failed the duplicate guard (86.08% within 3 px &gt; 70%); see its <a href="https://github.com/buffedlizard55-lab/GEMSDOE33/blob/main/knowledge/31_r7_pcsup_lane_correction_20261028.md">correction</a>.</p>
<div class="panel warn"><b>Data/provenance status:</b> 17 SHA-256-pinned owner-mirror inputs were restored and the shared 121-channel research cache rebuilt locally; both remain git-ignored. Mirror hashes establish byte identity only, not organizer authentication. Direct GDR #1391/#1682 asset fetches returned HTTP 500; 3DEP was checked only at two finite-cell catalog windows, with no raw DEM bytes; MT conductance attachments were not obtained. No source-dependent candidate is viable on this evidence. See <a href="sources.html">official source registry</a>, <a href="data/source_preflight_20261029.json">preflight</a>, and <code>data/README.md</code>.</div>
<h2>Our operating values</h2>
<div class="grid-2"><div class="panel accent"><h3>Maximize P(Win)</h3><p>Prefer evidence that predicts useful hidden-fault detection, not a download or a hopeful score projection. No slot until a fresh, leakage-audited holdout improves over a matched baseline.</p></div><div class="panel accent"><h3>Own the Outcome</h3><p>Make failures visible, preserve provenance, correct misleading pages, and distinguish local format validation from scientific validity and organizer acceptance.</p></div></div>
<h2>Use artifacts safely</h2>
<p>All linked historical TIFFs are research/education artifacts or prior-site files, not approved new submissions. PCSUP is an audit artifact whose pre-placement surface failed the duplicate guard. Do not submit any file; the current selector has no eligible candidate. Use the current nine-site table and explicit per-file banner rather than historical hero cards. Read <a href="executive-summary.html">the executive summary</a> before downloading.</p>
"""
    return page("GEMSDOE33 · Evidence-led fault discovery", body, "index.html")

# ---------------------------------------------------------------------------
# 2026-10-29 nine-site audit section (generated from evidence/nine_site_audit_20261029.json)
# ---------------------------------------------------------------------------
NINE_SITES = ("GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
              "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36")
NINE_AUDIT_EVIDENCE = "evidence/nine_site_audit_20261029.json"
NINE_MANIFEST = "registry/nine_site_best_files_20261029.json"


def _short(name: str, width: int = 58) -> str:
    return name if len(name) <= width else name[: width - 1] + "…"


def _raw_link(entry: dict) -> str:
    head = entry.get("repo_head_at_pin") or "main"
    url = f"https://github.com/{entry['repo']}/raw/{head}/{entry['path']}"
    return (f'<a class="btn alt" href="{esc(url)}"><code>{esc(Path(entry["path"]).name)}</code></a>'
            f'<div class="small">{entry["bytes"]:,} bytes · git blob <code>{esc(entry["blob_sha1"][:12])}</code></div>')


def _unique_cell(v: dict) -> str:
    trig = v.get("duplicate_trigger_vs_other_submissions", [])
    m = v.get("max_frac_dots_within_3px_vs_other_submission") or {}
    value = m.get("value")
    near = f"; nearest {esc(_short(str(m.get('vs', '')), 46))}" if value is not None else ""
    pct = f"{value:.1%}" if value is not None else "n/a"
    border = " (borderline: limit 70%)" if value is not None and 0.65 <= value <= 0.70 else ""
    if v.get("unique_under_guard"):
        return f"<b>YES</b> — 0 guard triggers; max 3-px overlap {pct}{border}{near}"
    return f"<b>NO</b> — {len(trig)} guard trigger(s); max 3-px overlap {pct}{near}"


def _format_cell(v: dict, files: dict | None = None) -> str:
    if v.get("format_pass"):
        return "pass"
    checks = (files or {}).get(v["name"], {}).get("format_checks") or v.get("format_checks") or {}
    failed = [k for k, ok in checks.items() if not ok] or ["unknown"]
    return "<b>FAIL</b>: " + esc(", ".join(failed))


def nine_site_audit_section() -> str:
    audit = read_json(ROOT / NINE_AUDIT_EVIDENCE, None)
    manifest = read_json(ROOT / NINE_MANIFEST, None)
    if not audit or not manifest:
        return ("<div class='panel bad'><b>Nine-site audit evidence is missing.</b> "
                "Run <code>python scripts/nine_site_audit.py</code> after restoring the data.</div>")
    man = {f"{e['site']}/{e['user_reported_name']}": e for e in manifest["entries"]}
    files = {f["name"]: f for f in audit["nine_site_files"]}
    verdicts = audit["site_verdicts"]
    by_role = {r: [v for v in verdicts if v["role"] == r]
               for r in ("site_best", "site_listed", "local_research_zeros")}

    def score_key(v):
        s = v.get("reported_score_USER_REPORTED")
        return -1.0 if s is None else float(s)

    banner = (
        "<div class='panel bad'><b>OK TO SUBMIT: NO — for every file on this site.</b> "
        "The nine focus sites' best files are one H19-5 emission family, and no file that passes the duplicate guard "
        "has cleared the holdout gate. Selector result: <b>0 eligible</b> "
        "(<code>evidence/submission_selection_20261029.json</code>). "
        "The highest owner-reported value, GEMSDOE32 B2 at 0.2778, is a deletion-only copy of GEMSDOE28/31 H27-4 and "
        "is <b>not unique</b>. Reported scores are owner-reported, not organizer-confirmed, and no estimated score is given "
        "for any file here.</div>")

    # Table 1 — the nine site-best files
    site_best = sorted(by_role["site_best"], key=score_key, reverse=True)
    t1 = "\n".join(
        f"<tr><td><b>{esc(v['site'])}</b></td>"
        f"<td>{_raw_link(man[v['name']])}<div class='small'>{esc(_short(v['name'], 70))}</div></td>"
        f"<td>{v['reported_score_USER_REPORTED']:.4f} <span class='small'>owner-reported</span></td>"
        f"<td>Not estimable from evidence</td>"
        f"<td>{v['n_dots']:,}</td>"
        f"<td>{_unique_cell(v)}</td>"
        f"<td>{_format_cell(v, files)}</td>"
        f"<td><b>YES — learning/research only.</b> Not submission-approved.</td>"
        f"<td><b>NO</b></td></tr>"
        for v in site_best)

    # Table 2 — listed files that are unique under the guard
    listed_unique = sorted([v for v in by_role["site_listed"] if v["unique_under_guard"]],
                           key=score_key, reverse=True)
    listed_dup = sorted([v for v in by_role["site_listed"] if not v["unique_under_guard"]],
                        key=score_key, reverse=True)

    def listed_row(v):
        return (f"<tr><td>{esc(v['site'])}</td>"
                f"<td>{_raw_link(man[v['name']])}<div class='small'>{esc(_short(v['name'], 70))}</div></td>"
                f"<td>{v['reported_score_USER_REPORTED']:.4f} <span class='small'>owner-reported</span></td>"
                f"<td>{v['n_dots']:,}</td>"
                f"<td>{_unique_cell(v)}</td>"
                f"<td>{_format_cell(v, files)}</td>"
                f"<td><b>YES — research only.</b> Not submission-approved.</td>"
                f"<td><b>NO</b> — already scored by its owner; no holdout-validated gain recorded</td></tr>")

    t2 = "\n".join(listed_row(v) for v in listed_unique)
    t2b = "\n".join(listed_row(v) for v in listed_dup)

    # Table 3 — this repository's own research TIFFs
    research = sorted(by_role["local_research_zeros"], key=lambda v: (v["unique_under_guard"] is False, v["name"]))

    def research_row(v):
        notes = []
        if not v["format_pass"]:
            notes.append("format FAIL (see IR-33-20261029-HMDT-OUTSIDE-01)")
        if "lchc" in v["name"] or "thkcond" in v["name"] or "basestep" in v["name"]:
            notes.append("mutual family 90.7–94.0% overlap (IR-33-20261029-MUTUAL-DUP-01)")
        if "pcsup" in v["name"]:
            notes.append("final dots unique but pre-placement surface FAILED at 86.08% (IR-33-R7-PCSUP-SURFACE-01)")
        if "hmdt" in v["name"]:
            notes.append("no holdout run card (IR-33-HMDT-UNGATED-01)")
        good = v["unique_under_guard"] and v["format_pass"] and not any("MUTUAL" in n or "PCSUP" in n for n in notes)
        dl = "<b>YES — research/education only.</b> Not submission-approved." if good else "<b>NO</b> — do not use from this site"
        return (f"<tr><td>{esc(_short(Path(man[v['name']]['path']).name, 60))}</td>"
                f"<td>{_unique_cell(v)}</td><td>{_format_cell(v, files)}</td>"
                f"<td>{esc('; '.join(notes)) or 'no holdout run card; repo selector: not eligible'}</td>"
                f"<td>{dl}</td><td><b>NO</b></td></tr>")

    t3 = "\n".join(research_row(v) for v in research)

    irregularity_list = (
        "<ul>"
        "<li><b>IR-33-20261029-NINE-FAMILY-01</b> — all nine site-best files are one H19-5 family; two pairs are dot-identical copies.</li>"
        "<li><b>IR-33-20261029-B2-DELETION-01</b> — B2 = H27-4 minus 2,545 dots at 1–2 px from the catalogue; nothing added (independently recounted).</li>"
        "<li><b>IR-33-20261029-MUTUAL-DUP-01</b> — LCHC, THKCOND and BASESTEP overlap 90.7–94.0% with each other; their 'unique' labels were scoped to the pinned registry only.</li>"
        "<li><b>IR-33-20261029-HMDT-OUTSIDE-01</b> — the HMDT 'zeros' TIFF has 33,616 cells of 1.0 outside the template footprint.</li>"
        "<li><b>IR-33-20261029-PCSUP-SCOPE-01</b> — PCSUP passes the final-dot guard but failed the surface gate; dot-level uniqueness is not sufficient.</li>"
        "<li><b>IR-33-20261029-SCORE-CONFLICT-01</b> — the brief's 0.4413 leaderboard high, 0.3195 'current highest' and 0.2778 owner best cannot be reconciled without a receipt.</li>"
        "<li><b>IR-33-20261029-OFFICIAL-ACCESS-01</b> — GDR archive fetches failed HTTP 500; 3DEP coverage is catalog-spot-checked at two cells only; MT layer payload/grid/license/coverage remain unaudited, so no source-dependent hypothesis is viable.</li>"
        "<li><b>IR-33-20261029-HOLDOUT-COUNT-01</b> — the shared summary field <code>n_unique_withheld_components</code> is the total catalogue component count (3,199), not actual withheld components. Historical DTI arithmetic is unaffected; do not reuse this field as the holdout component count.</li>"
        "</ul>")

    return f"""
<h2>Nine-site audit (2026-10-29) — which file to submit?</h2>
{banner}
<p><b>Answer:</b> none. The owner-reported best (GEMSDOE32 B2, 0.2778) is a duplicate of GEMSDOE28/31 H27-4, and every listed site-best file triggers the duplicate guard. If you are looking for a reference point only, the highest owner-reported values are GEMSDOE32 B2 0.2778, GEMSDOE36 pinn 0.2750 and GEMSDOE28 h36-1 0.2710. None is a new submission.</p>
<p class="small">Method: each file is compared with every other pinned file in the audit (the 38-entry manifest plus 22 registry rasters; byte-identical copies excluded). A file is <b>duplicate</b> if Spearman/phi &gt; 0.90 or more than 70% of its dots lie within 3 px of another file's dots. Format is checked against the template (single-band float32, EPSG:32611, 3730 × 3292, template transform, values in [0, 1] in the footprint, zero or NaN outside). Estimated scores are <b>not</b> produced: the only scores here are owner/user-reported. Source: <a href="https://github.com/buffedlizard55-lab/GEMSDOE33/blob/main/{NINE_AUDIT_EVIDENCE}"><code>{NINE_AUDIT_EVIDENCE}</code></a>.</p>

<h3>Table 1 — best file per focus site (the nine owner-listed site-best files)</h3>
<div class="scroll"><table><thead><tr>
<th>Site</th><th>File to download (raw)</th><th>Reported score</th><th>Estimated score</th><th>Dots</th>
<th>Unique vs other GEMSDOE sites?</th><th>Format</th><th>OK to download?</th><th>OK to submit?</th>
</tr></thead><tbody>
{t1}
</tbody></table></div>

<h3>Table 2 — other owner-listed TIFFs on the nine focus sites</h3>
<p>Files that pass the duplicate guard against all other known files, sorted by reported score. None is OK to submit because each is already scored by its owner and no holdout-validated gain is recorded.</p>
<div class="scroll"><table><thead><tr>
<th>Site</th><th>File (raw)</th><th>Reported score</th><th>Dots</th><th>Unique vs other GEMSDOE sites?</th><th>Format</th><th>OK to download?</th><th>OK to submit?</th>
</tr></thead><tbody>
{t2}
{t2b}
</tbody></table></div>

<h3>Table 3 — this repository's own downloadable research TIFFs</h3>
<p>No owner score exists for these files. Uniqueness is measured against every other pinned file in the audit (38 manifest entries plus 22 registry rasters). A unique file still cannot be submitted without a passing holdout gate and a selector decision, and the selector returned 0 eligible.</p>
<div class="scroll"><table><thead><tr>
<th>File</th><th>Unique vs other pinned files?</th><th>Format</th><th>Notes / irregularity</th><th>OK to download?</th><th>OK to submit?</th>
</tr></thead><tbody>
{t3}
</tbody></table></div>

<h3>Irregularities found by this audit</h3>
{irregularity_list}
<p class="small">Full list and status: <a href="irregularities.html">irregularities page</a> (registry/irregularities.json).</p>
"""


def nine_site_index_panel() -> str:
    return ("<div class='panel bad'><b>Nine-site audit (2026-10-29): OK TO SUBMIT — NO for every file.</b> "
            "Every focus-site best file is a duplicate of the same H19-5 family, and no unique file has cleared the holdout gate. "
            "Highest owner-reported value: GEMSDOE32 B2 0.2778 (not unique, not an organizer score). "
            "See the <a href=\"executive-summary.html\">nine-site table and download guidance</a>.</div>")


def build_exec() -> str:
    tif = "gemsdoe33-g33-tilt-gravity-lidar-coherence-20261026-171b8b87dbf7-nan.tif"
    note = ("GEMSDOE33 G33 tilt-gravity-lidar coherence TIFF; proxy holdout FAILED "
            "dDTI -0.0907 0/4 folds; NOT cleared to submit. id 171b8b87dbf7")
    body = f"""<h2>Current decision — 2026-10-29</h2>
<div class="panel bad"><b>NO FILE IS OK TO SUBMIT. No candidate was implemented or evaluated in this continuation.</b> The A33-R7 budget is exhausted at 3/3 and no identifiable current method paragraph authorizes a new lane. The ranked slate is proposals only: 0/3 hypotheses pass the official-payload/schema/license/coverage gate. The selector previously found 0 eligible files of 19 checked. No slot was selected and no DrivenData upload occurred. Public leaderboard score is <b>not estimable</b>.</div>
<p><b>Shared evaluator/writer contract review:</b> the four vendored GEMSDOE24 source hashes match their pinned manifest; 45 targeted holdout/metric/writer tests pass. The evaluator uses 8-connected raster components as a proxy, not expert geological segment IDs. Its <code>n_unique_withheld_components</code> field also reports the full-catalogue count (3,199), not actually withheld components; historical records do not retain hidden IDs. This metadata bug does not alter DTI arithmetic; see <code>IR-33-20261029-HOLDOUT-COUNT-01</code> and the <a href="data/shared_pipeline_contract_review_20261029.json">contract review JSON</a>.</p>
<p><b>Current per-site inventory:</b> see the single 2026-10-29 nine-site table immediately below. It gives one row per site, raw file link, owner-reported score evidence, not-estimable score, novelty against the pinned registry, format, and explicit learning-download/submission status. Historical artifact cards farther down are archival context, not recommendations.</p>
{nine_site_audit_section()}
<div class="panel warn"><b>Data/source status:</b> restored 17/17 hash-pinned owner-mirror inputs and rebuilt the ignored 121-channel cache. Mirror hashes do not authenticate organizer provenance. Official page/catalog checks are documented in <a href="sources.html">the source registry</a> and <a href="data/source_preflight_20261029.json">source preflight JSON</a>; no candidate-required official payload is fully staged and verified.</div>
{review_warning()}<h2>Historical artifact cards — none is a current submission recommendation</h2>{r7_pcsup_hero()}{basestep_hero()}
{pfrt_hero()}
{fsml2_hero()}
{s33_seisdil_hero()}
{a33_r3_llc_hero()}
{dpps_hero(include_b2_score=True)}
{a33_r3_lchc_hero()}
{a33_r2_csht_hero()}
{round3_da_hgcm_hero()}
<h2>Executive summary — per-site best submissions and how to submit</h2>
<div class="panel bad"><b>Current status: no file in this project is approved for a competition slot, and no DrivenData upload was made from this workspace.</b> The newest file is A33-R7-PCSUP (above), <b>archive download only / 🛑 NOT OK TO SUBMIT</b>; it failed the pre-placement surface uniqueness guard and the same-operator matched-random gate. Its estimated leaderboard score is not estimable. The A33-R7 budget is exhausted. Older BASESTEP/THKCOND results are also invalid as confirmatory evidence because of full-catalogue threshold fitting and composite-only canaries. Historical site scores remain owner-reported unless an organizer receipt is linked to exact bytes. <b>There is currently no “submit this one” file; do not upload any file until its banner says OK TO SUBMIT: YES.</b></div>

<h3>Exactly how a submission is made (when a future candidate passes every gate)</h3>
<ol>
<li><b>Check the banner at the top of this page.</b> Submit only if it says <code>OK TO SUBMIT: YES</code> for that exact filename. Today it says <b>NO</b> for every file on this site.</li>
<li><b>Download the exact file only after the selector says OK TO SUBMIT: YES.</b> The <code>-zeros.tif</code> variant is finite in [0,1] across the whole array and passes the local range check, but the official instructions' outside-footprint null/NaN wording and the previously reported portal error are unresolved. No claim is made that zeros or NaN encoding is accepted by the live form; follow the current official format contract and do not upload while the selector says NO.</li>
<li><b>Verify the bytes you downloaded</b> (optional, 10 seconds): SHA-256 must equal the hash in the banner table, and <code>python scripts/validate_submission.py --submission FILE.tif --template sample_submission.tif --strict-zero-outside</code> must print <code>"pass": true</code> (1 band, float32, EPSG:32611, 3730 × 3292, template transform, min 0.0 / max 1.0).</li>
<li><b>Open the DrivenData submission form</b> (competition 306 → <i>New submission</i>): choose the <code>.tif</code> file (single-band GeoTIFF, or a .zip containing exactly one GeoTIFF, matching the format CRS/shape/geotransform).</li>
<li><b>Paste the note exactly as given</b> in the banner table (≤ 140 characters) into the <i>Note</i> box, e.g. the DPPS provenance note above — the note is how you tell submissions apart later.</li>
<li><b>Confirm a weekly slot is available</b> on the submission page, then submit once. Do not submit the same dots twice under different names.</li>
<li><b>Save the organizer receipt/score screenshot</b> and add it to the repo: only an organizer receipt converts an owner-reported number into an ORGANIZER-CONFIRMED score. Until then every historical score on this page stays labelled owner-reported.</li>
</ol>
<div class="panel warn"><b>No human inspector is in this loop:</b> leakage canaries, spatially blocked holdout vs matched controls, surface+final-dots duplicate guards, and the saved-byte format audit all run automatically in-project (<code>scripts/run_dpps_campaign.py</code>, <code>scripts/validate_submission.py</code>). The only human step is the account-holder clicking upload in step 4–6, because this workspace has no DrivenData auth.</div>

<h3>Per-site file, score evidence and uniqueness</h3>
<p>The preceding 2026-10-29 nine-site audit table is the single current per-site inventory. It deliberately reports user/owner scores as unconfirmed, gives no leaderboard score estimate, and marks the site-best files as non-unique and not approved to submit. Do not use a stale historical table or an artifact card below as a selector recommendation.</p>

<h3>Current ranked hypotheses and source preflight (proposal only)</h3>
<p>Three proposals—aqueous-geochemistry mixing fronts, depth-persistent MT conductance walls, and cross-catchment 3DEP channel-profile discontinuities—are ranked in <a href="hypotheses.html">the hypothesis page</a> and recorded in <a href="data/hypothesis_slate_20261029.json">the slate JSON</a>. The pinned shared holdout/writer contract review is <a href="data/shared_pipeline_contract_review_20261029.json">here</a>. The official source checks are in <a href="data/source_preflight_20261029.json">the preflight record</a>. No source-dependent candidate passes the official-payload/schema/license/coverage gate; no method lane was assigned, so no holdout experiment or TIFF was created. “Priority 1” is proposal order only, not expected contest rank or a score.</p>

<h3>Why did GEMSDOE32 B2 score 0.2778 — and can we beat it?</h3>
<p>We reproduced B2 pixel-exactly from the GEMSDOE28 H27-4 owner raster: it deletes 2,545 dots within 2 px of the catalogue and adds nothing (40,199 → 37,654 dots; Spearman ρ = 0.9676 vs H27-4; 100% of B2 dots within 3 px of H27-4 dots). Under the competition DTI (α=0.2 per false positive, β=0.8 per missed truth, 300 m kernel), every isolated prediction dot costs roughly 1 unit of weighted false-positive mass unless it lies within 300 m of a truth pixel, while dense clusters of dots share the same truth credit. Removing low-credit, catalogue-adjacent dots can therefore raise DTI even though no new fault is found: the most plausible mechanism is FP-mass reduction, not discovery. That is an inference from audited bytes, not proof, and no organizer receipt ties 0.2778 to B2's exact bytes.</p>
<p>Can we beat it? Not demonstrated here. Every fold-safe surface in this repository reaches HOLDOUT-DTI 0.13&ndash;0.14. The newest, A33-R3-LLC, tied CSHT: &Delta; +0.0003 on the screen and &minus;0.0006 on confirmation, with both CIs spanning 0. The fixed H19-5 surface that B2 descends from is not fold-safe, and on the same withheld segments it reaches 0.162. That gap of +0.0242 [+0.0150, +0.0328] (4/4 folds) is either real signal or leakage. That experiment has now run (FSML/FSML2-CC, 2026-10-26): the fold-safe re-derivation with the cached channel stack did <b>not</b> reproduce the gap — the plain PU blend duplicated CSHT at the surface guard (87.5% 3-px overlap), and the unique corroboration-count variant scored HOLDOUT-DTI 0.1104/0.1031 vs CSHT 0.1357/0.1321. So H19-5’s advantage either uses information outside the cached stack (1 m DEM tiles, full-catalogue geometry) or is not fold-safe; it is not reproducible as a unique fold-safe lane here. The full public ladder (121,131-px mask 0.1922* → thinned 0.2477* → 0.2600* → flank-pruned 0.2708* → B2 0.2778*) is byte-verified in knowledge/22: every step is emission pruning of one mask, and uniform budget cuts were separately rejected on holdout (25,000 dots scored worse for both FSML2 and CSHT). An older candidate, G33-HA (tilt &asymp; 0 &times; gravity edge &times; LiDAR coherence), failed the catalogue-proxy holdout (confirmation &Delta;DTI &minus;0.0907, 0/4 folds; CI [&minus;0.1210, &minus;0.0594]). No score above 0.2778, or above any leaderboard value, is projected or claimed. The two leader values in the brief (0.3195 and 0.4413) conflict and are unverified in this checkout. Under the DrivenData Terms of Use, this workspace does not scrape or refresh the leaderboard.</p>

<h3>Older H-N1 research GeoTIFF (archived; do not upload)</h3>
<p><b>This is not the newest artifact and is not cleared for the competition.</b> Its catalogue-proxy holdout failed (confirmation ΔDTI −0.0907, 0/4 folds). The historical uniqueness audit covered only the then-pinned 12-raster registry; it is not a current uniqueness certificate.</p>
<p><a class="btn alt" href="downloads/{tif}">Download archived H-N1 research GeoTIFF — NOT CLEARED FOR SUBMISSION</a></p>
<ul><li>Artifact: <code>gemsdoe33-g33-tilt-gravity-lidar-coherence-20261026-171b8b87dbf7</code></li><li>SHA-256: <code>403e6925a5b32a1ad79084636336c60dd4a4ce56aacacb66910542ace6683d44</code></li><li>Note (≤140 characters): <code>{note}</code></li><li>Verdict: <b>negative</b> — preserved as an older research result; format-valid but not slot-cleared. No organizer receipt exists.</li></ul>

{submission_steps()}
<h2>Steps for a future approved candidate (policy summary)</h2>
<ol><li>Require a passing automatic evidence gate <b>and</b> a separate selector decision within the verified weekly cap. A <b>promote</b> research verdict alone is not slot clearance; if either is missing, do not upload.</li><li>Download the exact named single-band GeoTIFF (or a ZIP with exactly one GeoTIFF) and keep it unchanged.</li><li>Run <code>python scripts/validate_submission.py --submission PATH --template PATH</code> against the official/sample template available in the local cache. Review CRS, shape, transform, dtype, footprint values, and outside-footprint handling against current official instructions.</li><li>In the authenticated DrivenData submission form, select the TIFF, enter a distinct name and concise note (portal limit: concise, e.g. ≤ 140 characters in this project), and submit only if a competition slot is available and the submission rules permit it.</li><li>Save the organizer receipt. Only that receipt can confirm a score/file association; report the organizer score separately from holdout diagnostics.</li></ol>
<div class="panel warn"><b>Outside-footprint semantics unresolved:</b> the repository's recorded official-format wording says null/NaN outside, while the owner separately reported a portal range error for a NaN-containing file; the exact rejected bytes and organizer diagnosis are not retained. A <code>-zeros.tif</code> passes the local all-array finite [0,1] check but may not match the null/NaN wording. Neither encoding has organizer acceptance evidence here. Do not upload while the selector says NO; for any future approved file, check the current official contract first.</div>
<h3>What is required before the next competition submission</h3><ul><li>New spatially blocked holdout where every catalogue-derived feature, including baseline/pseudo-label surfaces, is rebuilt using fold-visible data only.</li><li>Feature-by-feature leakage canary; investigate AUC &gt; 0.90 before trusting a signal.</li><li>Predeclared experiment, matched budget/control, uncertainty interval, and uniqueness screen against accessible registry rasters.</li><li>Exact format check from source inputs plus saved-byte re-open; current validator requires installed rasterio/numpy.</li><li>All scientific/format inspections must be run automatically in-project. Only the final authorized account upload is outside this project; no human scientific inspector is required by the project gate. This workspace has no DrivenData auth and cannot upload or retrieve a receipt.</li></ul>
<h2>Previous research artifacts (OK to download, DO NOT submit)</h2>
{a33_r2_csht_hero()}
{round3_da_hgcm_hero()}
"""
    return page("Executive summary & submission guidance · GEMSDOE33", body, "executive-summary.html")

def build_results() -> str:
    body = f"""<h2>Results, score claims, and evidence boundaries</h2>
<div class="panel bad"><b>Current summary (2026-10-29): no file is OK TO SUBMIT; no new candidate or experiment was run.</b> No organizer-confirmed score or leaderboard estimate is available. The current nine-site inventory is on the <a href="executive-summary.html">executive summary</a>; source blockers are on the <a href="hypotheses.html">proposal slate</a> and <a href="sources.html">source registry</a>.</div>
<p>Historical evidence: <a href="latest-review.html">nine-site byte-level forensics and automatic gate status</a> · <a href="{GITHUB}/knowledge/13_focus_forensics_g32_proof_and_a33_r2_results_20261026.md">2026-10-26 21-raster forensic proof &amp; A33-R2-CSHT report</a> · <a href="{GITHUB}/knowledge/16_a33_r3_llc_preregistration_and_result_20261026.md">A33-R3-LLC preregistration &amp; negative result</a> · <a href="{GITHUB}/registry/user_reported_scores_20261026.csv">historical user-reported score list</a>.</p>
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

def current_hypothesis_slate_section() -> str:
    slate = read_json(ROOT / "evidence/hypothesis_slate_20261029.json", {})
    hypotheses = slate.get("hypotheses", [])
    rows = []
    for item in hypotheses:
        layers = "<ul>" + "".join(f"<li>{esc(v)}</li>" for v in item.get("layers", [])) + "</ul>"
        source_links = []
        source_status = []
        for source in item.get("required_official_sources", []):
            url = source.get("url")
            if url:
                source_links.append(f'<a href="{esc(url)}">{esc(source.get("id", "official source"))}</a>')
            if source.get("asset_url"):
                source_links.append(f'<a href="{esc(source["asset_url"])}">listed asset URL (not downloaded)</a>')
            if source.get("api_url"):
                source_links.append(f'<a href="{esc(source["api_url"])}">official catalog API</a>')
            if source.get("doi"):
                source_links.append(f'<a href="{esc(source["doi"])}">DOI</a>')
            source_status.append(esc(source.get("availability", "Availability not recorded")))
        status = "<b>NOT VIABLE NOW</b> — " + esc(item.get("block_reason", "source gate incomplete"))
        rows.append(
            "<tr>"
            f"<td><b>{item.get('rank')}</b><br><code>{esc(item.get('id'))}</code><br>{esc(item.get('title'))}</td>"
            f"<td>{layers}</td>"
            f"<td>{esc(item.get('physical_signature'))}</td>"
            f"<td><b>Missing-catalogue rationale:</b> {esc(item.get('why_it_targets_catalogue_missing_faults'))}"
            f"<br><b>Prior-art difference:</b> {esc(item.get('difference_from_repo_prior_art'))}"
            f"<br><b>Named non-fault mimic:</b> {esc(item.get('named_non_fault_mimic'))}</td>"
            f"<td><b>{esc(item.get('expected_rank'))}</b><br>{esc(item.get('expected_qualitative_holdout_potential'))}"
            f"<br><b>Cost:</b> {esc(item.get('implementation_cost'))}</td>"
            f"<td>{' · '.join(source_links)}<br>{'<br>'.join(source_status)}<br>{status}</td>"
            "</tr>"
        )
    excluded = slate.get("excluded_prior_art", [])
    exclusions = "<ul>" + "".join(
        f"<li><b>{esc(v.get('id'))} — {esc(v.get('concept'))}:</b> {esc(v.get('reason'))}</li>"
        for v in excluded
    ) + "</ul>"
    return f"""
<h2>Current ranked hypotheses — proposal slate only (2026-10-29)</h2>
<div class="panel bad"><b>No candidate is viable; no experiment is authorized.</b> This slate contains three ranked geological proposals, not a preregistration or assigned method lane. A33-R7 is exhausted at 3/3, and no current method paragraph is identifiable. Source records were checked before any viability claim: <b>0/3 pass</b> the required official-payload, hash, schema, CRS, license, target-coverage and spatial-support audit. No DTI, contest rank or leaderboard score is projected. Priority numbers below mean research order only.</div>
<p>Machine-readable slate: <a href="data/hypothesis_slate_20261029.json"><code>evidence/hypothesis_slate_20261029.json</code></a> · source preflight: <a href="data/source_preflight_20261029.json"><code>evidence/source_preflight_20261029.json</code></a> · review: <a href="https://github.com/buffedlizard55-lab/GEMSDOE33/blob/main/knowledge/33_hypothesis_slate_and_source_audit_20261029.md">knowledge/33_hypothesis_slate_and_source_audit_20261029.md</a>.</p>
<div class="scroll"><table><thead><tr><th>Priority / candidate</th><th>Layers</th><th>Physical signature</th><th>Why missing faults / prior-art difference / named mimic</th><th>Expected priority, potential &amp; cost</th><th>Official source and availability / viability</th></tr></thead><tbody>
{''.join(rows)}
</tbody></table></div>
<h3>Excluded as repository prior art</h3>{exclusions}
<p><b>Experiment decision:</b> zero holdout experiments, zero candidate TIFFs and zero run cards were created from this slate. First obtain and hash the required official bytes, audit their schemas, CRS, license and full target coverage, then use an explicitly assigned single method paragraph and the shared evaluator/writer if a future run is authorized.</p>
"""


def build_hypotheses() -> str:
    current_slate = current_hypothesis_slate_section()
    body = f"""{current_slate}
<h2>Historical ranked geological hypothesis slates</h2>
<div class="panel warn"><b>Historical planning slates, not the current status.</b> The 2026-10-26 Round-4 and earlier slates below are retained as prior art; they are not authorizations to implement or run a candidate. The current 2026-10-29 slate above is the controlling proposal slate.</div>
<div class="panel warn"><b>Historical Round-4 feasibility audit (2026-10-26).</b> No new experiment or TIFF was produced in that review. The assigned lane was not specified as one single method; candidate availability also failed source/geometry checks for the first two ideas. Full audit: <a href="https://github.com/buffedlizard55-lab/GEMSDOE33/blob/main/knowledge/18_round4_feasibility_audit_20261026.md">Round-4 feasibility audit</a>; machine-readable card: <a href="research/round4-run-card.json">run card</a>.</div>
<p>Qualitative priority is not a numerical DTI estimate. A candidate becomes viable only after its inputs are locally available, correctly georeferenced, independent of withheld labels, and feature-canary/uniqueness checks pass. All numerical contest scores remain user/owner-reported unless an organizer receipt is retained.</p>
<div class="scroll"><table><thead><tr><th>Rank</th><th>Candidate; layers and physical signature</th><th>Why it could find missing faults; distinction from prior art</th><th>Official source / availability, mimic, cost, status</th></tr></thead><tbody>
<tr><td>1</td><td><b>A33-R4-COULOMB</b>; mapped Quaternary-fault trace geometry, slip rate, slip sense, dip, plus elastic half-space ΔCFS lobes.</td><td>Stress-transfer lobes could indicate blind synthetic/antithetic splays away from mapped traces. Distinct from geometric stepover halos and the earlier Mohr-slip surface because it requires a full spatial dislocation model.</td><td>Official source listing: <a href="https://gdr.openei.org/submissions/1391">DOE GDR #1391</a>. Local CSV contains centroids/attributes but no trace vertices; the companion vector mirror's coordinates lack an identified CRS and do not fall on the EPSG:32611 grid or match CSV UTM extents. Static stress/rake assumptions add uncertainty. Intrusive/caldera margins and frictional heterogeneity mimic. Moderate cost; <b>blocked pending auditable, correctly georeferenced trace geometry</b>.</td></tr>
<tr><td>2</td><td><b>A33-R4-CURVTRACE</b>; raw 1 m USGS 3DEP DEM, multi-azimuth hillshade/curvature and ≥1.5 km orientation-tracked scarp continuity.</td><td>Trace-scale morphology could reveal low-relief fault scarps unresolved by the 100 m feature grid; distinct from pixel-HGB, but overlaps conceptually with the earlier 100 m line-localized R3 work.</td><td>Official source: <a href="https://www.usgs.gov/3d-elevation-program">USGS 3DEP</a>. Cached LiDAR product is 12-band, 100 m aggregated features from 2 m processing; raw 1 m tiles are not in the pinned input set. Tile host is outside this session's network allowlist. Shoreline benches, terrace risers, roads, canals mimic. Higher cost; <b>blocked until official raw tiles are staged and hashed</b>.</td></tr>
<tr><td>3</td><td><b>A33-R4-PFRT</b>; cached <code>depth_to_base_surf</code>, gravity horizontal-gradient and directional updip projection.</td><td>Could transfer basement offsets basinward into subtle piedmont flexures, where the exposed trace is absent. Different from unshifted gradient-favorability models, but shares gravity layers with prior regional detectors.</td><td>Cached stack available; official upstream GeoDAWN page: <a href="https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and">USGS GeoDAWN</a>. Coalescent fan toes and buried pediments mimic; medium cost and high duplicate risk. <b>Potentially testable only after explicit lane/preregistration and early surface uniqueness screen; not run.</b></td></tr>
<tr><td>4</td><td><b>A33-R4-HMDT</b>; cached conductivity, upward-continued TMI, gravity gradient and dilatation; signed cross-gradient doublet.</td><td>Hydrothermal alteration may create asymmetric magnetic/conductive anomalies around concealed faults; distinct from unsigned CSHT rank averaging.</td><td>Official layers reference: <a href="https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and">USGS GeoDAWN</a> and <a href="https://gdr.openei.org/submissions/1391">DOE GDR #1391</a>. Saline playa / nonmagnetic lacustrine tuff mimic. Low–medium cost. An HMDT TIFF exists but has no retained reproducible fold-safe runner/card; <b>not a fresh untried hypothesis; do not score static bytes as fold-safe evidence</b>.</td></tr>
<tr><td>5</td><td><b>A33-R4-PALEOTEMP</b>; DOE 2 m temperature probes and paleosinter/tufa inventory with cached conductivity and geophysical edges.</td><td>Relict, inactive hydrothermal conduits could mark buried faults missed by active-vent-only approaches; distinct from current well/spring seeds.</td><td>Official source: <a href="https://gdr.openei.org/submissions/1391">DOE GDR #1391</a> (CC BY 4.0 as recorded in source registry). The specific probe/sinter payload is not among pinned 17 files and GDR host is not reachable from the workspace. Paleochannel thermal outflow mimic. Blocked; <b>not viable until exact payload/coverage/license is staged and audited</b>.</td></tr>
</tbody></table></div>
<p><b>Historical result:</b> Round-4 rank 1 (COULOMB) lacked usable staged geometry, rank 2 needed raw external 3DEP tiles, and no standalone lane was identified in that review. PFRT was not run. This archived feasibility result is not an instruction to select PFRT or to start a new lane now; the current 2026-10-29 proposal slate and source gate above control.</p>
<p>The frozen 2026-10-04 slate below is historical prior art, retained without rerunning failed arms.</p>
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
    body = """<h2>External data and source-preflight status (2026-10-29)</h2>
<div class="panel bad"><b>No new data-dependent hypothesis is viable yet.</b> The official source review verified pages/catalog entries, not local binary payloads. GDR #1391 wellspring GDB and GDR #1682 BRIDGE ZIP direct fetches returned HTTP 500; TNM offered 1 m DEM product URLs at two finite-template sample cells but no DEM bytes were downloaded or full coverage checked; MT conductance layers remain metadata-only with grid, license and coverage unchecked. See <a href="data/source_preflight_20261029.json">auditable source preflight</a> and <a href="hypotheses.html">ranked proposal slate</a>.</div>
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
    body = f"""<h2>Official Sources & Data Provenance</h2>
<div class="panel bad"><b>Source preflight (2026-10-29): no candidate-required official binary is fully verified.</b> The source pages/API below are linked for manual review. GDR #1391/#1682 archive fetches returned HTTP 500; 3DEP catalog coverage is verified at only two finite-footprint sample cells, with no raw tile bytes; MT conductance is metadata-only pending payload, grid, license and coverage checks. Full record: <a href="data/source_preflight_20261029.json"><code>evidence/source_preflight_20261029.json</code></a>; evaluator/writer contract: <a href="data/shared_pipeline_contract_review_20261029.json">pinned API and limitations</a>; source blocker: <code>IR-33-20261029-OFFICIAL-ACCESS-01</code>.</div>
<p>Sources are classified by provenance. A public listing or hash does not prove local binary availability, license suitability, exact geometry overlap, or organizer authenticity. See each source's recorded note and limitations.</p>

<h3>Official Competition & Geoscientific Sources</h3>
<div class="scroll">
<table><thead>
<tr><th>ID</th><th>Source Title / Link</th><th>Type</th><th>License</th><th>Verification Note</th></tr>
</thead><tbody>
{rows}
</tbody></table>
</div>

<h3>Owner-mirror input pins (verified 2026-10-29; not organizer authentication)</h3>
<p>All 17 registered owner-mirror inputs were restored and hash-verified; <code>scripts/prepare_data.py</code> rebuilt the shared 121-channel research cache. The receipts are <a href="{GITHUB}/evidence/input_grid_audit.json"><code>evidence/input_grid_audit.json</code></a> and <a href="data/data_preparation_20261029.json"><code>evidence/data_preparation_20261029.json</code></a>. These large rasters and the derived cache are git-ignored and not published with this static site. Hashes identify mirror bytes only and do not authenticate organizer provenance.
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
<div class="panel bad"><b>NOT OK TO SUBMIT. The restoration/claims audit itself ran zero experiments; the subsequent, separately preregistered S33-SEISDIL artifact from parallel PR #30 is unique and downloadable, but failed both holdout comparisons and is not slot-approved.</b>
<p>Do not relabel a negative raster as a winner. The S33 result and run card are linked from the overview and executive summary; this repository review did not rerun or retune that candidate.</p>
<p><a href="research/round4-run-card.json" download>Download this review's run card JSON</a> · <a href="research/current-promotion-gate.json" download>Automatic gate decision</a> · <a href="research/focus-raster-audit.json" download>Measured forensic audit</a></p></div>
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
<h3>Prior 2025 promotion-gate snapshot (not a current candidate result)</h3>
<p>These are deterministic in-project checks, not a request for a human scientific inspector. <code>scripts/check_promotion.py</code> requires source-pinned shared tools, pooled paired improvement plus CI on screen and independent confirmation, complete feature canaries, both duplicate screens, exact saved-byte validation and budget compliance. It checks evidence completeness, not the truth of arbitrary supplied JSON. Even a pass is only eligibility for a separate weekly-cap-aware selector. The table below is the archived 2025 focus-review gate record; the current selector separately reports 0 eligible of 12 run cards (including S33-SEISDIL).</p>
<table><thead><tr><th>Archived gate</th><th>Prior snapshot</th></tr></thead><tbody>{gates}</tbody></table>
<h3>Round-4 feasibility decision</h3>
<p>The ranked five-candidate Round-4 slate and input-by-input feasibility audit are <a href="hypotheses.html">on the hypotheses page</a> and in <a href="https://github.com/buffedlizard55-lab/GEMSDOE33/blob/main/knowledge/18_round4_feasibility_audit_20261026.md">the full audit note</a>. The conceptual top candidate (Coulomb stress transfer) lacked usable local trace geometry; 1 m CURVTRACE needed unstaged raw 3DEP tiles. PFRT was not run in that restoration review because no single lane was specified there. A subsequent, separate S33-SEISDIL lane was preregistered and evaluated in PR #30; see its run card and the top-level banner. It failed both holdout comparisons, so no submission is promoted. No additional candidate was run in this repository review.</p>
<div class="panel warn"><b>Current-checkout verification (2026-10-26):</b> all 17 registered owner-mirror inputs were restored and hash-verified; the shared 121-channel cache was rebuilt without training in the restoration audit. A separate preregistered S33-SEISDIL candidate was later evaluated and generated on parallel PR #30; it is unique/format-valid but negative and NOT OK TO SUBMIT. No additional candidate or slot was created by this review. Data/cache remain ignored and are not included in Git snapshots. See <a href="https://github.com/buffedlizard55-lab/GEMSDOE33/blob/main/knowledge/21_post_merge_review_20261026.md">the latest repository review</a>.</div>
<p><a href="research/round4-run-card.json" download>Round-4 feasibility run card</a> · <a href="{GITHUB}/evidence/round4_input_feasibility_20261026.json">machine-readable input feasibility audit</a> · <a href="{GITHUB}/evidence/input_grid_audit.json">17-input hash/grid audit</a>.</p>
<h3>Primary evidence and reviewable limitations</h3>
<p><a href="{GITHUB}/knowledge/21_post_merge_review_20261026.md">Latest post-merge review</a> · <a href="{GITHUB}/knowledge/20_restoration_and_claims_audit_20261026.md">Restoration and claims audit</a> · <a href="{GITHUB}/knowledge/18_round4_feasibility_audit_20261026.md">Previous Round-4 feasibility report</a> · <a href="{GITHUB}/evidence/source_review_20261025.json">Pinned source inventory</a> · <a href="https://github.com/drivendataorg/gems-prize-reference-solution/blob/aebe92f7c8a990f0e3443451b7a825d9afd6336b/README.md">Organizer CPU/GPU reference</a>. Official competition rules, weekly cap, current leaderboard and score-to-file receipts were not freshly verified; no automated DrivenData contact was made.</p>
"""
    current = """<div class="panel bad"><b>Current status (2026-10-29): NO FILE IS OK TO SUBMIT; no candidate was run.</b> A33-R7 is exhausted at 3/3 and no current method paragraph is identifiable. The new slate contains three proposals, but 0/3 pass the official-payload/schema/license/coverage gate; no experiment, TIFF, slot selection or upload occurred. Source details: <a href="data/source_preflight_20261029.json">preflight JSON</a>; full record: <a href="https://github.com/buffedlizard55-lab/GEMSDOE33/blob/main/knowledge/33_hypothesis_slate_and_source_audit_20261029.md">2026-10-29 review</a>. All content below this notice is historical audit material, including the 2026-10-28 PCSUP surface-duplicate correction.</div>"""
    return page("Latest forensic review & automatic gates · GEMSDOE33", current + body, "latest-review.html")


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
    for evidence_name in (
        "hypothesis_slate_20261029.json",
        "source_preflight_20261029.json",
        "data_preparation_20261029.json",
        "shared_pipeline_contract_review_20261029.json",
    ):
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
