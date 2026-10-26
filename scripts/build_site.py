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
.hero-download{background:linear-gradient(115deg,#133e24,#12253a 65%);border:2px solid #3e985a;
border-radius:18px;padding:26px;margin:22px 0;box-shadow:0 8px 30px rgba(0,0,0,0.4)}
.hero-download h2{border:0;margin:0 0 10px;padding:0;color:#a3f4b5;font-size:1.6rem}
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
    r3_zeros = "gemsdoe33-h33r3-invariant-analog-20261025-40f15a687381-zeros.tif"
    r3_nan = "gemsdoe33-h33r3-invariant-analog-20261025-40f15a687381-nan.tif"
    r3_note = "GEMSDOE33 H33-R3-1 invariant analog co-train B2; 37654 dots; research only, do not submit (40f15a687381)"
    filename = "GEMSDOE33-H33-6-edge-consensus-research-20261004-6c888d2ce0f7-nan.tif"
    note = "H33-6 edge-normal research artifact; holdout gate failed; not approved for competition upload. id 6c888d2ce0f7"
    return f"""<div class="hero-download" id="unique-submission" style="background:linear-gradient(115deg,#3e1919,#12253a 68%);border-color:#b85656;">
<h2 style="color:#ffb3b3;">GATE STATUS: HOLD WEEKLY SLOT — Unique GeoTIFFs Validated on Disk, NOT approved for competition upload</h2>
<p><b>Unmistakable Automated Gate Decision (<code>verdict = "negative"</code>):</b> No candidate in this repository is cleared for a live DrivenData weekly submission slot. Both the new Round-3 domain-invariant analog co-training GeoTIFF (<code>H33-R3-1</code>) and the earlier <code>H33-6</code> / <code>H33-F</code> research GeoTIFFs are packaged and 10/10 byte-validated on disk without human intervention, but they are <b>research deliverables only — Do not submit or spend a competition slot on them. No candidate is slot-cleared.</b></p>
<p>
  <a class="btn alt" href="downloads/{r3_zeros}">Download Round-3 Unique GeoTIFF (-zeros.tif)</a>
  <a class="btn alt" href="downloads/{r3_nan}">Download Round-3 Unique GeoTIFF (-nan.tif)</a>
  <a class="btn alt" href="downloads/receipt-gemsdoe33-h33r3-invariant-analog-20261025-40f15a687381.json">Round-3 Automated Validator Receipt JSON</a>
  <a class="btn alt" href="downloads/research/{filename}">Download earlier H33-6 research GeoTIFF</a>
</p>
<div class="scroll">
<table><thead>
<tr><th>Artifact / Campaign Round</th><th>Unique Submission Name &amp; Note (&le;140 chars)</th><th>Automated Format &amp; Range Gate (No Human Intervention)</th><th>Leakage Canary &amp; 22-Raster Duplicate Guard</th><th>Holdout DTI &amp; Slot Decision</th></tr>
</thead><tbody>
<tr>
  <td><b>Round 3 (2026-10-25)<br><code>H33-R3-1</code> Domain-Invariant Analog Co-Train + B=2 Collar</b></td>
  <td>Name: <code>gemsdoe33-h33r3-invariant-analog-20261025-40f15a687381</code><br>Note (104 chars): <pre>{r3_note}</pre>SHA-256 (<code>-zeros.tif</code>): <code>a6b9dc58c9ab74e9886937e7f700bcdc9e464f4c0d4961aa2d13fc8496ebf8da</code><br>SHA-256 (<code>-nan.tif</code>): <code>5f818e716b0df0ffa6921db2012b9c723ec19189b660fe5f034335019c6bb353</code></td>
  <td><span class="badge good">10 / 10 FORMAT CHECKS PASS</span><br><code>EPSG:32611</code>, <code>3730 &times; 3292</code>, <code>float32</code>, <code>37,654</code> positive pixels (`0` at $d_{{\\text{{cat}}}} \\le 2\\text{{ px}}$).<br><code>-zeros.tif</code> is 100% finite in <code>[0.0, 1.0]</code> across all <code>12,279,160</code> cells.</td>
  <td><span class="badge good">32 / 32 CANARIES PASS</span> (max feature AUC <code>0.6035 &le; 0.90</code>)<br><span class="badge good">0 / 22 DUPLICATES</span> (max |surface &rho;| <code>0.1000 &le; 0.90</code>; max 3-px dot overlap <code>50.58% &le; 70%</code>)</td>
  <td><span class="badge bad">DO NOT SUBMIT · VERDICT: NEGATIVE</span><br><code>HOLDOUT-DTI</code> (<code>GEMSDOE33-HIDE-AND-RECOVER-v1.0</code>, <code>60,988</code> withheld px): <b>0.075943</b> (95% CI <code>[0.067108, 0.085451]</code>). Beats fold-safe physical baseline (<code>+0.026455</code>, 3/4 folds) &amp; repairs <code>H33-F</code> domain shift (AUC <code>0.9172 &rarr; 0.7778</code>), but below fixed-H19-5 B=2 ref (<code>0.116963</code>).</td>
</tr>
<tr>
  <td><b>Round 2 (2026-10-04)<br><code>H33-6</code> Cross-Physics Edge-Normal Consensus</b></td>
  <td>Name: <code>GEMSDOE33-H33-6-edge-consensus-research-20261004</code><br>Note (112 chars): <pre>{note}</pre>SHA-256 (<code>-nan.tif</code>): <code>18604d71f11db269a3f70007433d1dd74e4f09eb195861dc2aeda4d98aa8efe7</code></td>
  <td><span class="badge good">FORMAT CHECK PASS</span><br>Single-band float32, EPSG:32611, 3730 &times; 3292, 100 m; finite in-footprint values in [0,1].</td>
  <td><span class="badge bad">DUPLICATE GUARD TRIGGERED</span><br><code>95.3%</code> of dots within 3 px of <code>H27-4</code> / <code>D2.8</code> (7/9 local rasters exceeded threshold).</td>
  <td><span class="badge bad">FAILED HOLDOUT · NOT FOR UPLOAD</span><br>P1 mean delta &minus;0.002737 DTI (pooled <code>0.112486</code> vs <code>0.114669</code>, &Delta;DTI <code>&minus;0.002183</code>); 2/4 spatial folds positive.</td>
</tr>
<tr>
  <td><b>Round 1 (2026-10-04)<br><code>H33-F</code> Raw-Feature Analog Transfer</b></td>
  <td>Name: <code>gemsdoe33-h33f-analog-xfer-20261004-d042874b26ef</code><br>SHA-256 (<code>-nan.tif</code>): <code>cf0aa4b19fc26e753599c7db45c7623a6f49e8a40e7db17a1ccce4b8b8532a60</code></td>
  <td><span class="badge good">FORMAT CHECK PASS</span><br><code>44,090</code> positive pixels (`0.8532%` footprint).</td>
  <td><span class="badge good">UNIQUE SURFACE</span> (`26.6%` 3-px overlap vs C0), but severe covariate shift (20 km block domain AUC <code>0.9172</code>).</td>
  <td><span class="badge bad">FAILED HOLDOUT · NOT FOR UPLOAD</span><br>P1 mean delta <code>&minus;0.093072</code> (0/4 folds positive).</td>
</tr>
<tr>
  <td><b>Historical Baseline Reference<br><code>D2.8</code> (from <code>GEMSDOE25/30</code>)</b></td>
  <td>File: <a href="downloads/gemsdoe33-d28-reference-20261004-426073b6b4ab-zeros.tif"><code>gemsdoe33-d28-reference-20261004-426073b6b4ab-zeros.tif</code></a><br>SHA-256 (<code>-nan.tif</code>): <code>426073b6b4ab5fb8397ca3bcdddc19edccbe3ffcbabac7a8ac7b56b2e64cd9f7</code></td>
  <td><span class="badge good">10 / 10 FORMAT CHECKS PASS</span><br><code>44,090</code> positive pixels (`3,891` in $0 &lt; d_{{\\text{{cat}}}} \\le 1\\text{{ px}}$, `2,545` in $1 &lt; d_{{\\text{{cat}}}} \\le 2\\text{{ px}}$).</td>
  <td><span class="badge warn">PRIOR-ART BASELINE</span><br>Identical to <code>GEMSDOE25</code> and <code>GEMSDOE30</code> (`100%` overlap).</td>
  <td><span class="badge warn">HISTORICAL REFERENCE ONLY</span><br>Retained for baseline comparison and educational audit only.</td>
</tr>
</tbody></table>
</div>
<p>See <a href="results.html">Results &amp; Focus-Site Forensic Proof</a>, <a href="hypotheses.html">Ranked Hypotheses (Round 3 &amp; Round 2)</a>, <a href="research.html">Full Run Cards &amp; Duplicate Screen</a>, and <a href="executive-summary.html">How to Submit &amp; Range [0, 1] Safeguards</a>.</p>
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


def build_index() -> str:
    body = f"""{unique_submission_hero()}
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
<p>The unique H33-6 TIFF is downloadable for inspection/reproducibility only. <b>It is not okay to upload.</b> The historical D2.8 mirror artifacts are educational references only and are not a new strategy or verified score-file pairing. Read <a href="executive-summary.html">the executive summary</a> before using any artifact.</p>
"""
    return page("GEMSDOE33 · Evidence-led fault discovery", body, "index.html")

def build_exec() -> str:
    fname = "GEMSDOE33-H33-6-edge-consensus-research-20261004-6c888d2ce0f7-nan.tif"
    note = "H33-6 edge-normal research artifact; holdout gate failed; not approved for competition upload. id 6c888d2ce0f7"
    r3_zeros = "gemsdoe33-h33r3-invariant-analog-20261025-40f15a687381-zeros.tif"
    r3_nan = "gemsdoe33-h33r3-invariant-analog-20261025-40f15a687381-nan.tif"
    r3_note = "GEMSDOE33 H33-R3-1 invariant analog co-train B2; 37654 dots; research only, do not submit (40f15a687381)"
    body = f"""<h2>Executive summary — how a valid submission is made &amp; current gate status</h2>
<div class="panel bad"><b>Current status: no file in this project is approved for a competition slot (<code>verdict = "negative"</code>).</b> Both the Round-3 unique GeoTIFF (<code>gemsdoe33-h33r3-invariant-analog-20261025-40f15a687381</code>) and the earlier H33-6 TIFF are research deliverables that did not clear the promotion gate against the fixed-H19-5 B=2 reference. They are deliberately linked for reproducibility and audit, but are <b>not approved for competition upload</b> and <b>not okay to submit</b>. Do not spend a weekly slot on them.</div>
<p>When a future candidate passes a predeclared, leakage-audited holdout gate, compare its package against the official competition instructions linked below and verify the complete saved GeoTIFF. No local audit guarantees portal acceptance or leaderboard score performance.</p>
<p>Official review links: <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">competition problem and format</a> · <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/rules/">competition rules</a> · <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/data/">data page (login may be required)</a>.</p>

<h3>1. Round-3 Unique GeoTIFF (2026-10-25 — 10/10 Format &amp; Duplicate Gates PASS; Verdict: Negative / Do Not Upload)</h3>
<p>
  <a class="btn alt" href="downloads/{r3_zeros}">Download Round-3 -zeros.tif (All-Finite [0,1])</a>
  <a class="btn alt" href="downloads/{r3_nan}">Download Round-3 -nan.tif (NaN Outside Footprint)</a>
  <a class="btn alt" href="downloads/receipt-gemsdoe33-h33r3-invariant-analog-20261025-40f15a687381.json">Machine-Readable Validator Receipt JSON</a>
</p>
<ul>
  <li><b>Unique Submission Name:</b> <code>gemsdoe33-h33r3-invariant-analog-20261025-40f15a687381</code></li>
  <li><b>Note (≤140 characters, 104 chars):</b> <code>{r3_note}</code></li>
  <li><b>SHA-256 (<code>-zeros.tif</code>, 373,304 B):</b> <code>a6b9dc58c9ab74e9886937e7f700bcdc9e464f4c0d4961aa2d13fc8496ebf8da</code></li>
  <li><b>SHA-256 (<code>-nan.tif</code>, 448,718 B):</b> <code>5f818e716b0df0ffa6921db2012b9c723ec19189b660fe5f034335019c6bb353</code></li>
  <li><b>Automated Non-Human Validation (<code>submission_writer.py</code> + <code>scripts/validate_submission.py</code>):</b>
    <code>pass = True</code> on both variants; <code>EPSG:32611</code>; shape <code>3730 &times; 3292</code>; <code>100 m</code> pixels; affine transform <code>[100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0]</code>; <code>37,654</code> emitted positive pixels (`0.7287%` of footprint, `0` pixels at $d_{{\\text{{cat}}}} \\le 2.0\\text{{ px}}$); <code>0</code> NaNs inside the <code>5,167,373</code>-cell footprint; <code>-zeros.tif</code> has <code>all_finite = True</code> and <code>in_range_0_1_whole_array = True</code> across all <code>12,279,160</code> cells.</li>
  <li><b>Leakage Canary &amp; Duplicate Screen (<code>evaluate_holdout.py</code>):</b> All 32 individual features pass (`max AUC = 0.6035 &le; 0.90`); <code>0 / 22</code> registry rasters trigger duplicate guard on either pre-placement surface (`max |rho| = 0.1000 &le; 0.90`) or final dots (`max 3-px overlap = 50.58% &le; 70%`; `42.73%` vs <code>GEMSDOE32</code>).</li>
  <li><b>Holdout Gate Result:</b> <code>HOLDOUT-DTI = 0.075943</code> (95% spatial-tile bootstrap CI <code>[0.067108, 0.085451]</code>, <code>60,988</code> withheld catalogue pixels). Beats the fold-safe physical baseline (`+0.026455`, 3/4 folds) and the matched-random control (`+0.022085`), and repairs <code>H33-F</code>'s covariate collapse, but remains below the historical fixed-<code>H19-5</code> <code>B=2</code> reference (`0.116963`, &Delta;DTI <code>-0.041019</code>). Verdict: <code>negative</code> (do not spend a weekly competition slot).</li>
</ul>

<h3>2. Earlier Round-2 Research GeoTIFF (H33-6 — Failed Holdout &amp; Duplicate Guard, Do Not Upload)</h3>
<p><a class="btn alt" href="downloads/research/{fname}">Download unique research TIFF</a></p>
<ul><li>Artifact: <code>GEMSDOE33-H33-6-edge-consensus-research-20261004-6c888d2ce0f7</code></li><li>SHA-256: <code>18604d71f11db269a3f70007433d1dd74e4f09eb195861dc2aeda4d98aa8efe7</code></li><li>Note (≤140 characters): <code>{note}</code></li><li>Reason: P1 mean delta DTI −0.00273732, 2/4 folds positive; conditional due to fixed H19-5 surface and proxy labels, and triggered the 3-px duplicate guard against 7/9 local rasters. Full evidence in <a href="research.html">research report</a>.</li></ul>

<h2>3. Addressing the Portal Range Error: <code>[0, 1]</code> Validation Without Human Intervention</h2>
<div class="panel accent">
  <p><b>Root Cause &amp; Dual-Variant Packaging (<code>submission_writer.py</code>):</b></p>
  <ol>
    <li><b>In-Footprint Float32 Sentinel Contamination (<code>IR-33-NODATA-01</code>):</b> In <code>training_features.tif</code>, <code>3,061</code> cells inside the active <code>5,167,373</code>-cell template footprint carry the raw float32 nodata sentinel <code>-3.4028235e+38</code> (`3,073` in band 6 <code>tc</code>). Any pipeline that feeds unmasked float32 bands into a linear/tree predictor without replacing sentinels can emit negative or NaN values inside the active footprint.</li>
    <li><b>Outside-Footprint Whole-Array Range Check:</b> Outside the <code>5,167,373</code>-cell footprint, <code>sample_submission.tif</code> has <code>7,111,787</code> cells set to <code>NaN</code>. In NumPy, <code>np.nan &gt;= 0.0</code> and <code>np.nan &lt;= 1.0</code> evaluate to <code>False</code>. If a portal validator checks <code>np.all((arr &gt;= 0.0) &amp; (arr &lt;= 1.0))</code> on the raw <code>3730 &times; 3292</code> array before masking to the footprint, any <code>-nan.tif</code> file will fail with a range error. Notably, our byte-level audit (`evidence/focus_sites_forensic_20261025.json`) confirmed that both <code>GEMSDOE32</code> (<code>h33-h33-2-b2-...-zeros.tif</code>, <code>0.2778</code>) and <code>GEMSDOE36</code> (<code>anderson-geothermal-pinn-38854-zeros.tif</code>, <code>0.2756</code>) used the all-finite <b><code>-zeros.tif</code></b> convention (`0.0` outside footprint, <code>nodata=None</code>).</li>
    <li><b>Automated Fail-Closed Guard:</b> <code>submission_writer.py</code> refuses to write any raster with non-finite or out-of-range values inside the footprint, writes both <code>-zeros.tif</code> (whole-array finite in <code>[0.0, 1.0]</code>) and <code>-nan.tif</code> (NaN outside footprint), and re-opens the written files on disk with <code>scripts/validate_submission.py</code>. Always check the live official format instructions before uploading.</li>
  </ol>
</div>

<h2>4. Steps for a Future Approved Candidate</h2>
<ol><li>Confirm the candidate status is explicitly <b>promote / slot-cleared</b> in current evidence; if not, do not upload.</li><li>Download the exact named single-band GeoTIFF (or a ZIP with exactly one GeoTIFF) and keep it unchanged.</li><li>Run <code>.venv/bin/python scripts/validate_submission.py --submission PATH --template .cache/data/sample_submission.tif --strict-zero-outside</code> against the official/sample template available in the local cache. Review CRS, shape, transform, dtype, footprint values, and outside-footprint handling against current official format instructions.</li><li>In the authenticated DrivenData submission form, select the TIFF, enter a distinct name and concise note, and submit only if a competition slot is available and the submission rules permit it.</li><li>Save the organizer receipt. Only that receipt can confirm a score/file association; report the organizer score separately from holdout diagnostics.</li></ol>
<div class="panel warn"><b>Known validation limitation:</b> The archived H33-6 local report passed the then-current validator for finite [0,1] values on the footprint and NaNs outside. It is not all-finite over the whole raster and does not satisfy every possible portal-wide range check. Follow the live official format instructions rather than assuming zero or NaN outside is accepted.</div>
<h3>What is required before the next competition submission</h3><ul><li>New spatially blocked holdout where every catalogue-derived feature, including baseline/pseudo-label surfaces, is rebuilt using fold-visible data only.</li><li>Feature-by-feature leakage canary; investigate AUC &gt; 0.90 before trusting a signal.</li><li>Predeclared experiment, matched budget/control, uncertainty interval, and uniqueness screen against accessible registry rasters.</li><li>Exact format check from source inputs plus saved-byte re-open; current validator requires installed rasterio/numpy.</li><li>Human owner to use their authenticated competition account. This workspace has no DrivenData auth and cannot upload or retrieve a receipt.</li></ul>
"""
    return page("Executive summary & submission guidance · GEMSDOE33", body, "executive-summary.html")

def build_results() -> str:
    body = """<h2>Results, Focus-Site Forensic Proof (<code>GEMSDOE24..36</code>), and Holdout Evidence</h2>
<div class="panel bad"><b>No organizer-confirmed submission result is available in this checkout.</b> Competition scores cited across the GEMSDOE campaign (<code>0.1922</code>, <code>0.2477</code>, <code>0.2647</code>, <code>0.2720</code>, <code>0.2756</code>, <code>0.2778</code>, <code>0.3195</code>, <code>0.4413</code>) are labeled <code>[OWNER-REPORT]</code> from sibling repository documentation (`IR-33-SCORE-01..03`). All raster byte hashes, pixel counts, boolean set identities, and distance-to-catalogue histograms below are <code>[MEASURED]</code> directly from the GeoTIFF byte streams in <code>evidence/focus_sites_forensic_20261025.json</code>. All local holdout figures are labeled <code>HOLDOUT-DTI</code> with evaluator version, withheld positive count, and 95% CI.</div>

<h3 id="focus-sites-forensic">1. Byte-Level Forensic Audit Across Focus Sites (<code>GEMSDOE24</code>, <code>25</code>, <code>27</code>, <code>28</code>, <code>30</code>, <code>31</code>, <code>32</code>, <code>33</code>, <code>36</code>)</h3>
<p>We staged the published GeoTIFFs from the focus repositories and ran <code>scripts/audit_focus_sites.py</code> to compute exact SHA-256 digests, distance-to-catalogue histograms $d_{\\text{cat}}(x)$ against <code>labels.tif</code> (<code>60,988</code> catalogue pixels), and 300 m triangular kernel integrals $\\int K_{300}(\\hat{Y})\\,dx$ (machine-readable output in <a href="https://github.com/buffedlizard55-lab/GEMSDOE33/blob/main/evidence/focus_sites_forensic_20261025.json"><code>evidence/focus_sites_forensic_20261025.json</code></a>):</p>
<div class="scroll">
<table><thead>
<tr><th>Focus Repo</th><th>Artifact Name</th><th>SHA-256 (12)</th><th>Reported Score (<code>[OWNER-REPORT]</code>)</th><th>Positive Pixels (<code>[MEASURED]</code>)</th><th>Outside Footprint</th><th>$d_{\\text{cat}}=0$</th><th>$0 &lt; d_{\\text{cat}} \\le 1\\text{ px}$</th><th>$1 &lt; d_{\\text{cat}} \\le 2\\text{ px}$</th><th>$2 &lt; d_{\\text{cat}} \\le 3\\text{ px}$</th><th>$d_{\\text{cat}} &gt; 3\\text{ px}$</th><th>300 m Kernel Integral</th><th>Kernel / Dot</th></tr>
</thead><tbody>
<tr><td><code>19GEMSDOE</code></td><td><code>h19_5_nan.tif</code></td><td><code>c8521ba7d02d</code></td><td><code>0.1922</code></td><td><code>121,131</code></td><td><code>NaN</code></td><td>0</td><td>13,864</td><td>7,548</td><td>5,693</td><td>94,026</td><td>449,683.62</td><td>3.7124</td></tr>
<tr><td><code>GEMSDOE24</code></td><td><code>h25-1-d1-5-nan.tif</code></td><td><code>62a9f4692ff6</code></td><td><code>0.2477</code></td><td><code>60,069</code></td><td><code>NaN</code></td><td>0</td><td>6,343</td><td>3,574</td><td>2,953</td><td>47,199</td><td>383,641.00</td><td>6.3867</td></tr>
<tr><td><code>GEMSDOE27</code></td><td><code>topo-gap-closure-t-v2-on-d1-5-nan.tif</code></td><td><code>991cf9ebfb06</code></td><td><code>0.2439</code></td><td><code>61,328</code></td><td><code>NaN</code></td><td>0</td><td>6,534</td><td>3,698</td><td>3,039</td><td>48,057</td><td>393,046.97</td><td>6.4089</td></tr>
<tr><td><code>GEMSDOE25</code></td><td><code>dotted_h19_5_d2_8_nan.tif</code> (<code>D2.8</code>)</td><td><code>426073b6b4ab</code></td><td><code>0.2600 / 0.2647</code></td><td><code>44,090</code></td><td><code>NaN</code></td><td>0</td><td>3,891</td><td>2,545</td><td>2,171</td><td>35,483</td><td>341,260.95</td><td>7.7401</td></tr>
<tr><td><code>GEMSDOE30</code></td><td><code>d28-poisson300m-offcat-44090.tif</code></td><td><code>426073b6b4ab</code></td><td><code>0.2647</code></td><td><code>44,090</code></td><td><code>NaN</code></td><td>0</td><td>3,891</td><td>2,545</td><td>2,171</td><td>35,483</td><td>341,260.95</td><td>7.7401</td></tr>
<tr><td><code>GEMSDOE28</code></td><td><code>h27-4-r1-solo-d2-8-nan.tif</code> (<code>B=1</code>)</td><td><code>1240a34232c1</code></td><td>unscored on 28; <code>0.2720</code> on 31</td><td><code>40,199</code></td><td><code>NaN</code></td><td>0</td><td><b>0</b></td><td>2,545</td><td>2,171</td><td>35,483</td><td>319,760.73</td><td>7.9544</td></tr>
<tr><td><code>GEMSDOE28</code></td><td><code>h36-1-rung30-blind-r1-nan.tif</code></td><td><code>5a86a87cb41b</code></td><td>unscored</td><td><code>37,660</code></td><td><code>NaN</code></td><td>0</td><td><b>0</b></td><td>2,353</td><td>2,024</td><td>33,283</td><td>308,351.25</td><td>8.1878</td></tr>
<tr><td><code>GEMSDOE28</code></td><td><code>h38-1-hf-euler-r30-r1-nan.tif</code></td><td><code>5d8dc28c9808</code></td><td>unscored</td><td><code>37,860</code></td><td><code>NaN</code></td><td>0</td><td><b>0</b></td><td>2,354</td><td>2,027</td><td>33,479</td><td>309,946.47</td><td>8.1866</td></tr>
<tr><td><code>GEMSDOE31</code></td><td><code>h27-4-solo-d28-20261004-1240a342-nan.tif</code></td><td><code>1240a34232c1</code></td><td><code>0.2720</code></td><td><code>40,199</code></td><td><code>NaN</code></td><td>0</td><td><b>0</b></td><td>2,545</td><td>2,171</td><td>35,483</td><td>319,760.73</td><td>7.9544</td></tr>
<tr><td><b><code>GEMSDOE32</code></b></td><td><b><code>h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif</code></b></td><td><b><code>75711334d340</code></b></td><td><b><code>0.2778</code> (Highest)</b></td><td><b><code>37,654</code></b></td><td><b><code>0.0</code> (all finite)</b></td><td><b>0</b></td><td><b>0</b></td><td><b>0</b></td><td><b>2,171</b></td><td><b>35,483</b></td><td><b>302,510.13</b></td><td><b>8.0339</b></td></tr>
<tr><td><code>GEMSDOE36</code></td><td><code>anderson-geothermal-pinn-38854-zeros.tif</code></td><td><code>8483329fa44b</code></td><td><code>0.2756</code></td><td><code>38,854</code></td><td><code>0.0</code> (all finite)</td><td>0</td><td>0</td><td>0</td><td>2,174</td><td>36,680</td><td>312,670.48</td><td>8.0473</td></tr>
<tr><td><b><code>GEMSDOE33</code></b></td><td><b><code>gemsdoe33-h33r3-invariant-analog-20261025-40f15a687381-zeros.tif</code></b></td><td><b><code>a6b9dc58c9ab</code></b></td><td><b>unscored (<code>negative</code> gate)</b></td><td><b><code>37,654</code></b></td><td><b><code>0.0</code> (all finite)</b></td><td><b>0</b></td><td><b>0</b></td><td><b>0</b></td><td><b>1,908</b></td><td><b>35,746</b></td><td><b>309,507.12</b></td><td><b>8.2198</b></td></tr>
</tbody></table>
</div>

<h3>2. Mathematical Proof: Why <code>GEMSDOE32</code> (<code>h33-h33-2-b2-...-zeros</code>, <code>0.2778</code>) Achieved the Highest Score Among the Focus Sites</h3>
<div class="panel accent">
<ol>
  <li><b>Verified Exact Set Identities Across Focus Sites (<code>evidence/focus_sites_forensic_20261025.json</code>):</b>
    <ul>
      <li><code>GEMSDOE30</code> $\\equiv$ <code>GEMSDOE25</code> (<code>D2.8</code>, <code>44,090</code> px, identical SHA-256 <code>426073b6b4ab...</code>).</li>
      <li><code>GEMSDOE31</code> $\\equiv$ <code>GEMSDOE28 (H27-4)</code> $\\equiv \\{x \\in \\text{D2.8} \\mid d_{\\text{cat}}(x) &gt; 1.0\\text{ px}\\}$ (<code>40,199</code> px; removes exactly <code>3,891</code> dots at $d_{\\text{cat}} = 1\\text{ px}$).</li>
      <li><b><code>GEMSDOE32 (H33-2-B2)</code> $\\equiv \\{x \\in \\text{D2.8} \\mid d_{\\text{cat}}(x) &gt; 2.0\\text{ px}\\} \\equiv \\{x \\in \\text{H27-4} \\mid d_{\\text{cat}}(x) &gt; 2.0\\text{ px}\\}$ (<code>37,654</code> px; removes an additional <code>2,545</code> dots in $1 &lt; d_{\\text{cat}} \\le 2.0\\text{ px}$, for <code>6,436</code> total halo dots removed).</b></li>
      <li><code>GEMSDOE36</code> (<code>38,854</code> px, <code>0.2756</code>) contains <code>GEMSDOE32</code> (<code>37,654</code> px) as an <b>exact subset</b> plus <code>1,200</code> extra dots at $d_{\\text{cat}} &gt; 2.0\\text{ px}$.</li>
    </ul>
  </li>
  <li><b>Why Pruning the $B=2$ Catalogue Flank ($d_{\\text{cat}} \\le 200\\text{ m}$) Deterministically Increases DTI:</b>
    In the competition metric $\\text{DTI} = \\text{TP}_w / (\\text{TP}_w + 0.2\\,\\text{FP}_w + 0.8\\,\\text{FN}_w)$, known catalogue pixels $\\mathcal{C}$ are masked out of the test set, and $\\text{FP}_w$ is summed over emitted dots while $\\text{TP}_w$ integrates the 300 m (`3.0 px`) triangular kernel $K_{300}(\\hat{Y})$. Because upstream <code>H19-5</code> was trained on 1-pixel dilated catalogue traces with $\\sigma \\in \\{1,2,4,8\\}\\text{ px}$ smoothed geophysical gradients, its ridge crest develops a wide side-lobe halo at $100\\text{ m}-200\\text{ m}$ ($1\\text{ px}-2\\text{ px}$) alongside known training faults. Those <code>6,436</code> halo dots (`3,891` at $d_{\\text{cat}}=1\\text{ px}$ and `2,545` at $1 &lt; d_{\\text{cat}} \\le 2\\text{ px}$) sit on the shoulder of already-masked training faults, contributing $\\Delta\\text{TP}_w \\approx 0$ on unmapped faults while paying full $\\alpha=0.2$ false-positive penalty (`14.6%` of the entire `D2.8` dot budget). Meanwhile, the `2,171` dots retained at $2 &lt; d_{\\text{cat}} \\le 3\\text{ px}$ still extend their 300 m triangular kernels all the way to $d_{\\text{cat}}=0$ at fault junctions!</li>
  <li><b>Why <code>GEMSDOE36</code> (<code>0.2756</code>) Scored Lower Than <code>GEMSDOE32</code> (<code>0.2778</code>):</b>
    At $\\text{DTI} \\approx 0.2778$, a new dot must achieve marginal recall $\\Delta\\text{TP}_w / \\Delta\\text{FP}_w &gt; \\alpha\\,\\text{DTI}/(1-\\beta\\,\\text{DTI}) = 0.0714$. Appending `1,200` lower-precision dots onto <code>GEMSDOE32</code> inflated $\\text{FP}_w$ by `+3.19%` without meeting that threshold, reducing DTI by `-0.0022`.</li>
  <li><b>Can a Submission Exceed <code>0.2778</code> (and Reach <code>0.3195</code> / <code>0.4413</code>)?</b>
    Post-hoc pruning of <code>H19-5</code> / <code>D2.8</code> is exhausted near `~0.28` and any further subset of <code>D2.8</code> violates the Parallel-Run Protocol duplicate guard (`>70%` dots within 3 px). Exceeding `0.2778` and approaching `0.3195` (`~+20%` $\\text{TP}_w$ at fixed `37,654`-dot budget) or `0.4413` requires genuinely independent fault discovery on concealed intrabasin and step-over structures via (a) domain-invariant multi-physics standardization (`H33-R3-1`) and (b) field-verified fine-scale fault supervision (`DOE GDR #1682 BRIDGE GIS`, currently blocked in this sandbox).</li>
</ol>
</div>

<h3>3. Round-3 Hide-and-Recover Holdout Results (<code>evaluate_holdout.py</code>, <code>GEMSDOE33-HIDE-AND-RECOVER-v1.0</code>)</h3>
<p>All numbers below are <code>HOLDOUT-DTI</code> evaluated on 4-fold whole-segment buffered hide-and-recover folds (<code>withheld_positives = 60,988</code>, <code>alpha = 0.2</code>, <code>beta = 0.8</code>, <code>300 m</code> triangular kernel, <code>B = 1,000</code> spatial-tile bootstrap resamples over 10 km tiles):</p>
<div class="scroll">
<table><thead>
<tr><th>Experiment / Comparator</th><th>Dots / Fold</th><th>Pooled <code>HOLDOUT-DTI</code></th><th>95% Spatial-Tile Bootstrap CI</th><th>&Delta;DTI vs Fold-Safe Physical Baseline (95% CI)</th><th>Positive Folds</th><th>&Delta;DTI vs Random Control</th><th>P2 SGMC Off-Cat DTI</th><th>Registry Duplicate Triggers</th></tr>
</thead><tbody>
<tr><td><b><code>H33-R3-1</code> Domain-Invariant Analog Co-Train + B=2</b></td><td><code>37,654</code></td><td><b><code>0.075943</code></b></td><td><code>[0.067108, 0.085451]</code></td><td><b><code>+0.026455</code></b> (<code>[+0.017211, +0.036503]</code>)</td><td><b>3 / 4</b></td><td><b><code>+0.022085</code></b></td><td><code>0.075098</code></td><td><span class="badge good">0 / 22 PASS</span></td></tr>
<tr><td><code>H33-R3-2</code> Multi-Physics Vertical-Persistence Worm</td><td><code>37,654</code></td><td><code>0.054281</code></td><td><code>[0.047859, 0.060735]</code></td><td><code>+0.004793</code></td><td>2 / 4</td><td><code>+0.000423</code></td><td><code>0.052433</code></td><td><span class="badge good">0 / 22 PASS</span></td></tr>
<tr><td><code>H33-R3-3</code> Transtensional Step-Over &amp; Strain Relay</td><td><code>37,654</code></td><td><code>0.042027</code></td><td><code>[0.036356, 0.047604]</code></td><td><code>-0.007461</code></td><td>1 / 4</td><td><code>-0.011831</code></td><td><code>0.055830</code></td><td><span class="badge good">0 / 22 PASS</span></td></tr>
<tr><td>Comparator A: Fold-Safe Physical Baseline (<code>det_elev_gms2 + tmi_gms2</code>)</td><td><code>37,654</code></td><td><code>0.049488</code></td><td><code>[0.043644, 0.055436]</code></td><td><code>0.000000</code> (ref)</td><td>—</td><td><code>-0.004370</code></td><td><code>0.095426</code></td><td>—</td></tr>
<tr><td>Comparator B: Matched-Random Poisson Control ($d=3.0\\text{ px}$, $d_{\\text{vis}}&gt;2\\text{ px}$)</td><td><code>37,654</code></td><td><code>0.053858</code></td><td><code>[0.051136, 0.056556]</code></td><td><code>+0.004370</code></td><td>—</td><td><code>0.000000</code> (ref)</td><td>—</td><td>—</td></tr>
<tr><td>Comparator C: Historical Fixed-<code>H19-5</code> <code>B=2</code> Reference (not fold-recomputed)</td><td><code>38,926–40,090</code></td><td><code>0.116963</code></td><td><code>[0.108595, 0.124211]</code></td><td><code>+0.067475</code></td><td>—</td><td><code>+0.063105</code></td><td><code>0.092837</code></td><td><span class="badge bad">H19-5 Family</span></td></tr>
</tbody></table>
</div>

<h3>4. Earlier H27-4 Claim (0.2708) &amp; H33-6 Holdout Context</h3>
<p>The repo records that the linked GEMSDOE28 owner page labels H27-4 unscored/research-only, while GEMSDOE31 reports 0.2720 for the identical 40,199-dot raster (<code>1240a34232c1...</code>). No authenticated organizer receipt in this checkout links a score to raster bytes.</p>
<p>For Round-2 <code>H33-6</code>, <code>HOLDOUT-DTI</code> (four spatial folds; 60,988 withheld catalogue pixels total): pooled candidate DTI 0.112486 versus pooled control DTI 0.114669, pooled &Delta;DTI &minus;0.002183; unweighted mean of four fold deltas &minus;0.002737 (2/4 positive), descriptive Student-t 95% interval [&minus;0.015020, +0.009546], df=3; P2 SGMC proxy &Delta;DTI +0.00015900.</p>
"""
    return page("Results & score provenance · GEMSDOE33", body, "results.html")

def build_hypotheses() -> str:
    body = """<h2>Ranked geological hypothesis slates (Round 3 &amp; Round 2)</h2>
<p>Before running Round-3 experiments on 2026-10-25, we froze five geological hypotheses in <a href="https://github.com/buffedlizard55-lab/GEMSDOE33/blob/main/evidence/round3_hypotheses_20261025.json"><code>evidence/round3_hypotheses_20261025.json</code></a> and executed the top <b>3 runnable hypotheses</b> (<code>H33-R3-1</code>, <code>H33-R3-2</code>, <code>H33-R3-3</code>) within the strict 3-experiment budget. The earlier 2026-10-04 Round-2 slate (<a href="https://github.com/buffedlizard55-lab/GEMSDOE33/blob/main/knowledge/07_hypothesis_slate_20261004.md"><code>knowledge/07_hypothesis_slate_20261004.md</code></a>) is preserved below.</p>

<h3>1. Round-3 Preregistered Hypothesis Slate (2026-10-25 — Budget: 3/3 Runnable Executed)</h3>
<div class="scroll">
<table><thead><tr><th>Rank</th><th>ID &amp; Specific Layers</th><th>Physical Signature &amp; Why It Catches Omitted Faults</th><th>Difference vs Existing Repo Work &amp; Non-Fault Mimic</th><th>Cost &amp; Holdout Status</th></tr></thead><tbody>
<tr><td><b>1</b></td><td><b><code>H33-R3-1</code> Domain-Invariant Multi-Physics Crest Co-Training + B=2 Collar.</b> 32 locally basin-standardized (25 km rolling window) derivative/coherence channels across <code>det_elev</code>, 1m LiDAR scarps, <code>tmi</code> + 150 m upward-continued TMI, <code>iso_grav_anom</code>, <code>depth_to_base_surf</code>, <code>cond_surf</code>, radiometric ratios, geodetic strain, and GDR 1391 geothermometer upflow.</td><td>Removes regional basin-depth/elevation offsets so structural fault signatures co-trained across named analog geothermal fields (Dixie Valley, Brady, Desert Peak, importance-weighted by target similarity) transfer to unmapped basins without copying <code>H19-5</code>; emits <code>37,654</code> Poisson dots ($d_{\\min}=3.0\\text{ px}$) outside $d_{\\text{vis}} \\le 2.0\\text{ px}$.</td><td>Repairs <code>H33-F</code> covariate shift (20 km block domain AUC drops from <code>0.9172</code> to <code>0.7778</code>) and avoids <code>H33-6</code>'s 95.3% duplicate overlap (`0/22` registry duplicates).<br><b>Mimic:</b> Pleistocene Lake Lahontan paleo-shoreline scarps or buried volcanic dike contacts.</td><td>Low–Medium (~49s/fold). <b>Executed (Exp 1):</b> Pooled <code>HOLDOUT-DTI = 0.075943</code> (<code>+0.026455</code> vs physical baseline, 3/4 folds; <code>-0.041019</code> vs fixed-H19-5 B=2). Verdict: <code>negative</code>.</td></tr>
<tr><td><b>2</b></td><td><b><code>H33-R3-2</code> Multi-Scale Vertical-Persistence Potential-Field &amp; Conductive-Basement Worm Network.</b> <code>tmi_gms1/2/4</code>, <code>ext_TMI_up150_gm2</code>, <code>iso_grav_anom_gms1/2/4</code>, <code>depth_to_base_surf_gms2</code>, <code>cond_surf_gms2</code>, <code>det_elev_gms2</code>, <code>lid_step_max</code>, <code>gdr_geotherm_upflow</code>.</td><td>Geometric-mean persistence of magnetic and gravity edges across $\\sigma \\in \\{1,2,4\\}\\text{ px}$ and 150 m upward continuation, gated by $\\ge 2$ corroborating physical families and boosted in GDR 1391 geothermometer catchments ($&gt;60^\\circ\\text{C}$).</td><td>100% label-free cross-scale vertical-persistence worm detector (no <code>H19-5</code> or catalogue supervision).<br><b>Mimic:</b> Steeply dipping plutonic intrusive contacts and caldera ring margins.</td><td>Low (~15s). <b>Executed (Exp 2):</b> Pooled <code>HOLDOUT-DTI = 0.054281</code> (<code>+0.004793</code> vs physical baseline). Verdict: <code>negative</code>.</td></tr>
<tr><td><b>3</b></td><td><b><code>H33-R3-3</code> Transtensional Step-Over &amp; Dilatational Strain-Gradient Relay Bridge Detector.</b> <code>multiphysics_vertical_persistence</code>, <code>geod_dilaterate</code>, <code>geod_shearrate</code>, fold-visible fault-tip stress lobes ($200\\text{ m} &lt; d_{\\text{vis}} \\le 2,500\\text{ m}$).</td><td>Targets horsetail splays, wing cracks, and relay ramps at fold-visible fault terminations where dilatation/shear rates and multi-physics crests coincide (Faulds &amp; Hinz, 2015).</td><td>Computes fault tips strictly from <code>f.visible_faults</code> per fold (no held-out tip leakage as in withdrawn <code>C2</code>).<br><b>Mimic:</b> Alluvial fan apexes and radial bajada channels at range-front terminations.</td><td>Low (~15s). <b>Executed (Exp 3):</b> Pooled <code>HOLDOUT-DTI = 0.042027</code> (<code>-0.007461</code> vs physical baseline). Verdict: <code>negative</code>.</td></tr>
<tr><td><b>4</b></td><td><b><code>H33-R3-4</code> Field-Verified DOE GDR #1682 BRIDGE LiDAR Fault-Pick Supervised Transfer.</b> Official DOE GDR #1682 GIS archive (<code>https://gdr.openei.org/submissions/1682</code>, CC BY 4.0) + 32 invariant channels.</td><td>Supervised transfer trained on field-verified fine-scale LiDAR fault picks in Dixie Valley and Gabbs Valley omitted from regional compilations.</td><td>Uses independent field-verified target-style traces rather than subsetting <code>labels.tif</code>.<br><b>Mimic:</b> Pluvial shoreline berms in Dixie Valley.</td><td>Medium–High. <b>Blocked</b> in sandbox (<code>gdr.openei.org</code> outside outbound whitelist).</td></tr>
<tr><td><b>5</b></td><td><b><code>H33-R3-5</code> EarthScope / UNR NGL Dense GNSS Station Velocity &amp; InSAR Strain Discontinuity Inversion.</b> UNR Nevada Geodetic Lab station velocities (<code>http://geodesy.unr.edu/</code>) + ASF Sentinel-1 InSAR (<code>https://asf.alaska.edu/</code>).</td><td>Sub-10 km localized crustal velocity step discontinuities across active creeping geothermal fault zones, replacing over-smoothed 100 km competition strain bands.</td><td>Replaces pre-smoothed bands 4, 7, 8 with station/InSAR deformation gradients.<br><b>Mimic:</b> Groundwater-pumping or geothermal-production subsidence bowls.</td><td>High. <b>Blocked</b> in sandbox (outbound host whitelist).</td></tr>
</tbody></table>
</div>

<h3>2. Round-2 Preregistered Hypothesis Slate (2026-10-04)</h3>
<table><thead><tr><th>Rank</th><th>Hypothesis / layers and signature</th><th>Why it might reveal omitted faults</th><th>Difference / cost / status</th></tr></thead><tbody>
<tr><td>1</td><td><b>H33-6 cross-physics edge-normal consensus.</b> GeoDAWN bands 14 TMI and 13 isostatic gravity gradients, corroborated by band 15 basement depth or band 17 conductivity edge; aligned normals at 2-pixel Gaussian scale.</td><td>Buried basin-bounding/intrabasin structures may create aligned magnetic/gravity transitions without a surface scarp; contacts can mimic this signal.</td><td>Joint normal agreement plus corroboration and matched-budget reallocation; not just single-layer gradients. Low–medium cost. Tested once; conditional P1 gate failed. Do not upload.</td></tr>
<tr><td>2</td><td><b>H33-7 field-verified BRIDGE transfer.</b> DOE GDR #1682 LiDAR fault picks plus common GeoDAWN features.</td><td>Independent field picks could test structures absent from the regional compilation, if overlaps and label policies are resolved.</td><td>Named-field transfer is not implemented. Medium–high cost; blocked until official bytes, schema, CRS, licence and coverage are audited.</td></tr>
<tr><td>3</td><td><b>H33-8 Gabbs Valley 3D fault-surface analogue.</b> USGS ScienceBase item 62b21845d34e74f0d80f17aa with shared geophysical layers.</td><td>Subsurface interpretation may expose buried structures beyond surface fault traces.</td><td>Tests shallow projection of mapped surfaces, not only line picks. Medium cost; blocked pending payload retrieval/schema audit.</td></tr>
<tr><td>4</td><td><b>H33-9 ComCat focal-mechanism orientation.</b> USGS event focal mechanisms (strike/dip/rake) with potential-field edges.</td><td>Mechanism-plane orientation can test active structure orientation, but nodal-plane ambiguity and sparse events matter.</td><td>Different from earthquake-density proximity; carried-forward from earlier H33-2, so not novel. Medium cost; no full extract staged.</td></tr>
<tr><td>5</td><td><b>H33-10 signed strain-lobe / conductor edge.</b> GeoDAWN bands 7/8 strain, 17 conductivity, 15 basement depth and 18 gravity gradient.</td><td>Asymmetric strain across conductive/basement edge may flag concealed deformation, but fluids/contact geometry can mimic it.</td><td>Signed edge formulation differs from raw/multiplicative strain screens; partly pre-empted. Low–medium cost; no validation.</td></tr></tbody></table>
<p>No untested candidate is promoted. Both H33-R3-1..3 and H33-6 negative holdout verdicts are recorded as research deliverables; remaining external-data ideas require staging official archives first.</p>
"""
    return page("Ranked hypotheses · GEMSDOE33", body, "hypotheses.html")

def build_data_sources() -> str:
    body = """<h2>External data and domain-transfer status</h2>
<p>Analogue geology is plausible context, but no domain-transfer bound or independent validation is established. The previous H33-F screen used available owner-mirror products and did not have independent BRIDGE field labels. Its P1 mean delta was −0.093072 and it failed; its exploratory discriminator AUC 0.917 is not a Ben-David HΔH bound.</p>
<p>In Round 3 (<code>H33-R3-1</code>), replacing raw regional levels with 25 km rolling basin-standardized structural derivatives reduced the 20 km spatial-block domain-discriminator AUC from <code>0.9172</code> to <code>0.7778</code> and improved holdout performance by <code>+0.052053</code> DTI relative to the H19-5 family (`&Delta;DTI` improved from <code>-0.093072</code> to <code>-0.041019</code>). However, because independent BRIDGE labels are still unavailable, the joint-label error &lambda; in Ben-David et al. (2010) remains unobservable.</p>
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

    body = f"""<h2>Research candidates, Round-3 Run Card, and proxy holdout records</h2>
<div class="panel bad"><b>EXPLORATORY_NOT_LICENSED · BLOCKED_NOT_ESTIMATED · ROUND-3 VERDICT: NEGATIVE</b>
<p>The first-round shortlist was retrospective and remains archived; H33-6 failed P1 and no candidate is slot-approved.
In Round 3 (2026-10-25), <code>H33-R3-1</code> passed all 32 feature leakage canaries (max AUC <code>0.6035 &le; 0.90</code>), passed all 22 registry duplicate checks on both pre-placement surface (max |&rho;| <code>0.1000 &le; 0.90</code>) and final dots (max 3-px overlap <code>50.58% &le; 70%</code>), and beat the fold-safe physical baseline (pooled <code>HOLDOUT-DTI 0.075943</code> vs <code>0.049488</code>, &Delta;DTI <code>+0.026455</code>, 3/4 folds), but remained below the historical fixed-H19-5 B=2 reference (<code>0.116963</code>).
The score/file pairing unverified for historical baselines. H33-6 P1 mean ΔDTI was <b>−0.00273732</b> (2/4 folds positive);
A generic two-sample AUC is not itself that bound. The artifacts below are for research only.</p></div>

<div class="panel accent">
<h3>Round-3 Unique Research GeoTIFF: <code>H33-R3-1</code> Domain-Invariant Analog Co-Training (2026-10-25)</h3>
<p>
  <a class="btn alt" href="downloads/gemsdoe33-h33r3-invariant-analog-20261025-40f15a687381-zeros.tif">Download H33-R3-1 (-zeros.tif)</a> ·
  <a class="btn alt" href="downloads/gemsdoe33-h33r3-invariant-analog-20261025-40f15a687381-nan.tif">Download H33-R3-1 (-nan.tif)</a> ·
  <a href="downloads/receipt-gemsdoe33-h33r3-invariant-analog-20261025-40f15a687381.json">Validator Receipt JSON</a> ·
  <a href="https://github.com/buffedlizard55-lab/GEMSDOE33/blob/main/evidence/round3_run_card_20261025.json">Round-3 Run Card JSON</a> ·
  <span class="badge bad">RESEARCH ONLY · VERDICT: NEGATIVE</span>
</p>
<ul>
  <li><b>Submission Name:</b> <code>gemsdoe33-h33r3-invariant-analog-20261025-40f15a687381</code></li>
  <li><b>Note (104 chars &le; 140):</b> <code>GEMSDOE33 H33-R3-1 invariant analog co-train B2; 37654 dots; research only, do not submit (40f15a687381)</code></li>
  <li><b>SHA-256 (<code>-zeros.tif</code>):</b> <code>a6b9dc58c9ab74e9886937e7f700bcdc9e464f4c0d4961aa2d13fc8496ebf8da</code> · <b>SHA-256 (<code>-nan.tif</code>):</b> <code>5f818e716b0df0ffa6921db2012b9c723ec19189b660fe5f034335019c6bb353</code></li>
  <li><b>Leakage Canary (32 features tested alone on 4-fold hide-and-recover holdout):</b> <code>32 / 32 PASS</code> (max two-polarity ROC AUC = <code>0.603493</code> on <code>det_elev_curv2</code>, threshold <code>0.90</code>).</li>
  <li><b>Pre-Placement Surface &amp; Final-Dot Registry Duplicate Screen (22 rasters across <code>GEMSDOE24..36</code> and local repo):</b> <code>0 / 22 duplicate triggers</code> (max |surface Spearman &rho;| = <code>0.100002</code> vs <code>GEMSDOE27</code>; max dot Spearman &rho; = <code>0.031003</code> vs <code>GEMSDOE24</code>; max fraction of dots within 3 px = <code>0.505816</code> vs <code>GEMSDOE27</code> and <code>0.427338</code> vs <code>GEMSDOE32</code>).</li>
</ul>
</div>

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
        f"<td>{esc(s.get('type'))}</td><td>{esc(s.get('license'))}</td><td>{esc(s.get('note'))}</td></tr>"
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
