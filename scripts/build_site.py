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
    filename = "GEMSDOE33-H33-6-edge-consensus-research-20261004-6c888d2ce0f7-nan.tif"
    note = "H33-6 edge-normal research artifact; holdout gate failed; not approved for competition upload. id 6c888d2ce0f7"
    return f"""<div class="hero-download" id="unique-submission">
<h2>Research GeoTIFF download — NOT approved for competition upload</h2>
<p>This is the existing H33-6 research artifact, not a newly generated submission. Its retained final dots trigger the duplicate guard; uniqueness is NOT certified. Its blocked catalogue-proxy gate failed and its upstream baseline is not fold-independent. Do not submit or spend a competition slot on it. No candidate is slot-cleared.</p>
<p><a class="btn alt" href="downloads/research/{filename}">Download research GeoTIFF — DO NOT SUBMIT</a></p>
<table><tbody>
<tr><th>Artifact name</th><td><code>GEMSDOE33-H33-6-edge-consensus-research-20261004</code></td></tr>
<tr><th>Suggested note (under 140 characters)</th><td><pre>{note}</pre></td></tr>
<tr><th>Scientific status</th><td><span class="badge bad">FAILED HOLDOUT · NOT FOR UPLOAD</span> P1 mean delta −0.002737 DTI; 2/4 spatial folds positive. Conditional proxy result only.</td></tr>
<tr><th>Local format audit</th><td>Single-band float32, EPSG:32611, 3730 × 3292, 100 m; finite in-footprint values in [0,1]; NaN outside footprint. Local format check only; portal acceptance not tested.</td></tr>
<tr><th>SHA-256</th><td><code>18604d71f11db269a3f70007433d1dd74e4f09eb195861dc2aeda4d98aa8efe7</code></td></tr>
</tbody></table>
<p><b>Current audit:</b> all 17 owner-mirror inputs restored; 121 feature channels prepared; 12 focus-site references compared. No new experiment or TIFF. <a href="latest-review.html">Read the byte-level findings and automatic gate failures</a> · <a href="research/current-run-card.json" download>Download current run card (JSON)</a>.</p>
<p>Historical score claims and leaderboard status are unverified here. See <a href="hypotheses.html">the ranked hypothesis slate</a>, <a href="research.html">holdout evidence</a>, and <a href="executive-summary.html">submission requirements and current gate status</a>.</p>
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
<p>The existing H33-6 TIFF is downloadable for inspection/reproducibility only. <b>It is not okay to upload.</b> The historical D2.8 mirror artifacts are educational references only and are not a new strategy or verified score-file pairing. Read <a href="executive-summary.html">the executive summary</a> before using any artifact.</p>
"""
    return page("GEMSDOE33 · Evidence-led fault discovery", body, "index.html")

def build_exec() -> str:
    fname = "GEMSDOE33-H33-6-edge-consensus-research-20261004-6c888d2ce0f7-nan.tif"
    note = "H33-6 edge-normal research artifact; holdout gate failed; not approved for competition upload. id 6c888d2ce0f7"
    body = f"""<h2>Executive summary — how a valid submission is made</h2>
<div class="panel bad"><b>Current status: no file in this project is approved for a competition slot.</b> The existing H33-6 TIFF is a research artifact with a failed conditional holdout gate. It is deliberately linked for reproducibility, but it is <b>not okay to submit</b>. Do not spend a weekly slot on it.</div>
<p>When a future candidate passes a predeclared, leakage-audited holdout gate, compare its package against the official competition instructions linked below and verify the complete saved GeoTIFF. No local audit guarantees portal acceptance or leaderboard performance.</p>
<p>Official review links: <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">competition problem and format</a> · <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/rules/">competition rules</a> · <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/data/">data page (login may be required)</a>.</p>
<h3>Research GeoTIFF (do not upload)</h3>
<p><a class="btn alt" href="downloads/research/{fname}">Download research TIFF — DO NOT SUBMIT</a></p>
<ul><li>Artifact: <code>GEMSDOE33-H33-6-edge-consensus-research-20261004-6c888d2ce0f7</code></li><li>SHA-256: <code>18604d71f11db269a3f70007433d1dd74e4f09eb195861dc2aeda4d98aa8efe7</code></li><li>Note (≤140 characters): <code>{note}</code></li><li>Reason: P1 mean delta DTI −0.00273732, 2/4 folds positive; conditional due to fixed H19-5 surface and proxy labels. Full evidence in <a href="research.html">research report</a>.</li></ul>
<h2>Steps for a future approved candidate</h2>
<ol><li>Require a passing automatic evidence gate <b>and</b> a separate selector decision within the verified weekly cap. A <b>promote</b> research verdict alone is not slot clearance; if either is missing, do not upload.</li><li>Download the exact named single-band GeoTIFF (or a ZIP with exactly one GeoTIFF) and keep it unchanged.</li><li>Run <code>python scripts/validate_submission.py --submission PATH --template PATH</code> against the official/sample template available in the local cache. Review CRS, shape, transform, dtype, footprint values, and outside-footprint handling against current official instructions.</li><li>In the authenticated DrivenData submission form, select the TIFF, enter a distinct name and concise note, and submit only if a competition slot is available and the submission rules permit it.</li><li>Save the organizer receipt. Only that receipt can confirm a score/file association; report the organizer score separately from holdout diagnostics.</li></ol>
<div class="panel warn"><b>Known validation limitation:</b> The archived H33-6 local report passed the then-current validator for finite [0,1] values on the footprint and NaNs outside. It is not all-finite over the whole raster and does not satisfy every possible portal-wide range check. The cause of the previously reported portal range error has not been confirmed. Follow the live official format instructions rather than assuming zero or NaN outside is accepted.</div>
<h3>What is required before the next competition submission</h3><ul><li>New spatially blocked holdout where every catalogue-derived feature, including baseline/pseudo-label surfaces, is rebuilt using fold-visible data only.</li><li>Feature-by-feature leakage canary; investigate AUC &gt; 0.90 before trusting a signal.</li><li>Predeclared experiment, matched budget/control, uncertainty interval, and uniqueness screen against accessible registry rasters.</li><li>Exact format check from source inputs plus saved-byte re-open; current validator requires installed rasterio/numpy.</li><li>All scientific/format inspections must be run automatically in-project. Only the final authorized account upload is outside this project; no human scientific inspector is required by the project gate. This workspace has no DrivenData auth and cannot upload or retrieve a receipt.</li></ul>
"""
    return page("Executive summary & submission guidance · GEMSDOE33", body, "executive-summary.html")

def build_results() -> str:
    body = """<h2>Results, score claims, and evidence boundaries</h2>
<p><a href="latest-review.html">New: twelve-raster byte-level forensic review, GEMSDOE32 pruning recipe and automatic gate status.</a></p>
<div class="panel bad"><b>No organizer-confirmed submission result is available in this checkout.</b> The leaderboard values in the user's research brief and owner-maintained GEMSDOE pages are historical reports, not organizer receipts linking scores to raster bytes. Do not infer or present projected scores.</div>
<h3>H27-4 claim (0.2708)</h3><p>The repo records that the linked GEMSDOE28 owner page labels H27-4 unscored/research-only. No authenticated organizer receipt proves the quoted 0.2708 or associates it with the raster. Therefore the question “why did it score 0.2708?” has no verified premise here. At most, the owner report suggests a dotted H19-5 baseline with d=2.8; its mechanism is not confirmed as the cause of any official score.</p>
<h3>H33-6 local holdout</h3><p>HOLDOUT-DTI (four spatial folds; 60,988 withheld catalogue pixels total): pooled candidate DTI 0.112486 versus pooled control DTI 0.114669, pooled ΔDTI −0.002183. The unweighted mean of four fold deltas is −0.002737 (2/4 positive). A descriptive Student-t 95% interval across those fold deltas is [−0.015020, +0.009546], df=3; it is imprecise with n=4, conditional, and does not estimate uncertainty against private expert truth. P2 SGMC proxy ΔDTI is +0.00015900. These are local proxy diagnostics, not competition scores. The upstream H19-5 baseline was not re-derived per fold, and no independent confirmation was run.</p>
<p>Evaluator source: <code>src/gemsdoe33/metric.py</code>, function <code>dti_binary</code>; evidence does not record a semantic evaluator version. Record SHA-256 in the run card, rather than inventing a version label. See <a href="research.html">full run and caveats</a>.</p>
<h3>Historical context and provenance</h3><p>Prior owner-reported results are retained as historical context in <code>registry/score_ledger.json</code>; they are not a live feed and are not organizer-confirmed. The user's listed scores are not independently reproduced here. Official leaderboard access is not refreshed automatically. No result above can establish a higher-than-0.2778 or higher-than-0.3195 submission.</p>
"""
    return page("Results & score provenance · GEMSDOE33", body, "results.html")

def build_hypotheses() -> str:
    body = """<h2>Ranked geological hypothesis slate</h2>
<div class="panel warn"><b>Current planning slate:</b> four additional analog-transfer hypotheses are ranked in <a href="latest-review.html">the latest review</a>. All require independent official field labels and are blocked, not viable. The historical slate below is retained without rerunning failed arms.</div>
<p>The frozen 2026-10-04 slate in <a href="https://github.com/buffedlizard55-lab/GEMSDOE33/blob/main/knowledge/07_hypothesis_slate_20261004.md">knowledge/07_hypothesis_slate_20261004.md</a> contains five candidates ranked qualitatively by expected improvement and cost. It explicitly avoids numeric score projections. These ranks are prior beliefs, not scores.</p>
<table><thead><tr><th>Rank</th><th>Hypothesis / layers and signature</th><th>Why it might reveal omitted faults</th><th>Difference / cost / status</th></tr></thead><tbody>
<tr><td>1</td><td><b>H33-6 cross-physics edge-normal consensus.</b> GeoDAWN bands 14 TMI and 13 isostatic gravity gradients, corroborated by band 15 basement depth or band 17 conductivity edge; aligned normals at 2-pixel Gaussian scale.</td><td>Buried basin-bounding/intrabasin structures may create aligned magnetic/gravity transitions without a surface scarp; contacts can mimic this signal.</td><td>Joint normal agreement plus corroboration and matched-budget reallocation; not just single-layer gradients. Low–medium cost. Tested once; conditional P1 gate failed. Do not upload.</td></tr>
<tr><td>2</td><td><b>H33-7 field-verified BRIDGE transfer.</b> DOE GDR #1682 LiDAR fault picks plus common GeoDAWN features.</td><td>Independent field picks could test structures absent from the regional compilation, if overlaps and label policies are resolved.</td><td>Named-field transfer is not implemented. Medium–high cost; blocked until official bytes, schema, CRS, licence and coverage are audited.</td></tr>
<tr><td>3</td><td><b>H33-8 Gabbs Valley 3D fault-surface analogue.</b> USGS ScienceBase item 62b21845d34e74f0d80f17aa with shared geophysical layers.</td><td>Subsurface interpretation may expose buried structures beyond surface fault traces.</td><td>Tests shallow projection of mapped surfaces, not only line picks. Medium cost; blocked pending payload retrieval/schema audit.</td></tr>
<tr><td>4</td><td><b>H33-9 ComCat focal-mechanism orientation.</b> USGS event focal mechanisms (strike/dip/rake) with potential-field edges.</td><td>Mechanism-plane orientation can test active structure orientation, but nodal-plane ambiguity and sparse events matter.</td><td>Different from earthquake-density proximity; carried-forward from earlier H33-2, so not novel. Medium cost; no full extract staged.</td></tr>
<tr><td>5</td><td><b>H33-10 signed strain-lobe / conductor edge.</b> GeoDAWN bands 7/8 strain, 17 conductivity, 15 basement depth and 18 gravity gradient.</td><td>Asymmetric strain across conductive/basement edge may flag concealed deformation, but fluids/contact geometry can mimic it.</td><td>Signed edge formulation differs from raw/multiplicative strain screens; partly pre-empted. Low–medium cost; no validation.</td></tr></tbody></table>
<p>No untested candidate is promoted. H33-6's failure is a negative deliverable; remaining ideas require fresh preregistration and a valid holdout. Candidate details, official free-source availability checks and limitations are preserved in the linked slate.</p>
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
        ("run_card_focus_20261025.json", "current-run-card.json"),
        ("promotion_gate_20261025.json", "current-promotion-gate.json"),
        ("focus_raster_audit_20261025.json", "focus-raster-audit.json"),
    ):
        payload = read_json(ROOT / "evidence" / source)
        (research / name).write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
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
