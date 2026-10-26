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
.hero-download.bad{background:linear-gradient(115deg,#411919,#192334 70%);border-color:#a64f4f}
.hero-download.bad h2{color:#ffb0b0}.hero-download.bad .btn{background:var(--red);color:#2b0808}
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


def current_run_card() -> dict:
    return read_json(ROOT / "evidence" / "a33_l1_run_card.json")


def unique_submission_hero() -> str:
    card = current_run_card()
    sub = card["submission"]
    holdout = card["holdout_dti"]
    filename = sub["file"]
    zipname = filename.removesuffix(".tif") + ".zip"
    nan_twin = sub["nan_twin"]
    ci = holdout["candidate_95pct_ci"]["interval"]
    return f"""<div class="hero-download bad" id="unique-submission">
<h2>Unique GeoTIFF ready to download — DO NOT SUBMIT</h2>
<p>A33-L1 is genuinely different and saved-byte valid, but its preregistered holdout gate failed. It lost to the fold-safe regional comparator in all four folds. <b>It is not OK to submit and no weekly slot should be spent.</b></p>
<p><a class="btn" href="downloads/{esc(filename)}">Download unique research GeoTIFF</a>
<a class="btn alt" href="downloads/{esc(zipname)}">Download ZIP</a>
<a class="btn alt" href="downloads/{esc(nan_twin)}">NaN-outside twin</a></p>
<table><tbody>
<tr><th>Unique name</th><td><code>{esc(sub['name'])}</code></td></tr>
<tr><th>Note (≤140 characters)</th><td><pre>{esc(sub['note'])}</pre></td></tr>
<tr><th>Scientific status</th><td><span class="badge bad">NEGATIVE · NOT OK TO SUBMIT</span> HOLDOUT-DTI <b>{holdout['candidate']:.6f}</b>, 95% CI [{ci[0]:.6f}, {ci[1]:.6f}], {holdout['withheld_positives']:,} withheld positives; paired Δ vs best comparator {holdout['paired_delta']:+.6f}, 0/4 fold wins.</td></tr>
<tr><th>Automated format checks</th><td>One float32 band, EPSG:32611, exact 3730 × 3292 template grid/transform, values [0,1], no NaN inside footprint. Format validity is not portal acceptance.</td></tr>
<tr><th>SHA-256</th><td><code>{esc(card['raster_sha256'])}</code></td></tr>
</tbody></table>
<p>No DrivenData upload was made and no competition score is projected. Read the <a href="executive-summary.html">submission decision and procedure</a>, <a href="results.html">nine-site forensics</a>, and <a href="research.html">complete experiment record</a>.</p>
</div>"""


def build_index() -> str:
    body = f"""{unique_submission_hero()}
<h2>Direct answer: why GEMSDOE32 B2 may have done well</h2>
<div class="panel accent"><p><b>The strongest supported explanation is metric-aware subtraction, not a new detector.</b> Byte-level forensics show one exact nested family: GEMSDOE25/30 d2.8 (44,090 dots) ⊃ GEMSDOE31 solo (40,199) ⊃ GEMSDOE32 B2 (37,654). Solo removes 3,891 dots exactly 100 m from the mapped catalogue; B2 removes 2,545 more at 100–200 m. GEMSDOE36 then contains every B2 dot plus 1,200.</p>
<p>Because DTI penalizes low-credit predicted mass, masks mapped faults and rewards nonredundant placement within 300 m of hidden truth, pruning dots beside already mapped traces can improve denominator efficiency while preserving inherited off-catalogue lineaments. The reported progression 0.2600 → 0.2708 → 0.2778, followed by 0.2750 after adding dots, is directionally consistent—<b>if the owner reports are accurate and byte-linked</b>.</p></div>
<div class="panel warn"><b>Evidence boundary:</b> all historical values are OWNER/USER-REPORTED, NOT ORGANIZER-CONFIRMED. No authenticated portal receipt is retained here. The nested artifacts are dependent, so they are not independent replications and the explanation is not causal proof.</div>
<h2>Can a higher result be supported?</h2>
<p><b>Not by the present evidence.</b> A33-L1 improved over raw analog transfer but lost to the stronger regional visible-fault expert. It therefore cannot justify a slot or a score projection. At fixed mass, reaching 0.30 from the reported 0.2778 would require roughly 8% more useful hidden-fault credit; that is algebraic scale context, not a predicted score. See <a href="results.html">the complete nine-site table and HOLDOUT-DTI result</a>.</p>
<h2>What was completed</h2>
<ul><li>Five analog-transfer hypotheses ranked and hash-frozen before implementation.</li><li>One four-fold whole-component experiment with a 15-pixel buffer, fold-visible catalogue handling and matched emission budgets.</li><li>All 12 feature-alone leakage canaries passed.</li><li>Pre-placement and final uniqueness guards passed against nine SHA-pinned focus rasters.</li><li>One unique GeoTIFF plus ZIP/twin, strict saved-byte receipt, and one final JSON run card.</li><li>One experiment, zero competition slots, zero uploads.</li></ul>
<h2>Our operating values</h2>
<div class="grid-2"><div class="panel accent"><h3>Maximize P(Win)</h3><p>Prefer evidence that predicts useful hidden-fault detection over a hopeful upload. A unique file is necessary but not sufficient; no slot follows a negative holdout.</p></div><div class="panel accent"><h3>Own the Outcome</h3><p>Publish the negative result, preserve exact hashes and provenance, and distinguish owner reports, HOLDOUT-DTI, format validity and organizer acceptance.</p></div></div>
"""
    return page("GEMSDOE33 · Evidence-led fault discovery", body, "index.html")

def build_exec() -> str:
    card = current_run_card()
    sub = card["submission"]
    filename = sub["file"]
    zipname = filename.removesuffix(".tif") + ".zip"
    body = f"""<h2>Executive summary — submission decision and procedure</h2>
<div class="panel bad"><b>Current decision: NOT OK TO SUBMIT.</b> A33-L1 is unique and technically valid, but its scientific gate failed: paired HOLDOUT-DTI delta versus the best fold-safe comparator was {card['holdout_dti']['paired_delta']:+.6f}, 95% CI [{card['holdout_dti']['paired_delta_95pct_ci'][0]:+.6f}, {card['holdout_dti']['paired_delta_95pct_ci'][1]:+.6f}], with 0/4 fold wins. The separate weekly-slot selector was not run. Do not upload this file.</div>
<h3>One-click research package</h3>
<p><a class="btn alt" href="downloads/{esc(filename)}">Download unique zero-outside TIFF</a>
<a class="btn alt" href="downloads/{esc(zipname)}">Download ZIP</a></p>
<table><tbody><tr><th>Name</th><td><code>{esc(sub['name'])}</code></td></tr>
<tr><th>Note (≤140 characters)</th><td><code>{esc(sub['note'])}</code> ({sub['note_characters']} characters)</td></tr>
<tr><th>SHA-256</th><td><code>{esc(card['raster_sha256'])}</code></td></tr>
<tr><th>Status</th><td><span class="badge bad">RESEARCH ONLY · DO NOT UPLOAD</span></td></tr></tbody></table>
<h2>Automated checks completed</h2>
<ul><li>One band and float32 dtype.</li><li>EPSG:32611, 3730 × 3292, and affine transform exactly match the restored sample template.</li><li>Every footprint value is finite and in [0,1]; zero-outside primary is finite over the whole array.</li><li>Exactly 37,654 in-footprint positive pixels; saved bytes were reopened and hashed.</li><li>Final uniqueness: max Spearman 0.02221 and max within-3-pixel overlap 42.25% against nine pinned rasters.</li></ul>
<p>These checks establish local format and novelty only. They do not override a failed scientific gate or guarantee portal acceptance.</p>
<h2>Steps for a future promoted candidate</h2>
<ol><li>Open the current run card. Require both an explicit <b>promote</b> scientific verdict and a separate <b>slot-cleared</b> selector decision. A format pass alone is insufficient.</li><li>Review the live <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">official problem/format instructions</a> and <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/rules/">rules</a>; verify a weekly slot remains.</li><li>Download the exact named TIFF or single-file ZIP and verify its SHA-256. Do not rename/rewrite the raster after validation.</li><li>Rerun <code>python scripts/validate_submission.py --submission PATH --template data/sample_submission.tif</code> or the pinned shared writer validator; check dtype, grid, footprint finiteness and range.</li><li>Using the authorized DrivenData account, select the file, paste its unique name and ≤140-character note, and submit manually.</li><li>Save the organizer receipt. Only a receipt can establish portal acceptance and a score/file association; label HOLDOUT-DTI separately.</li></ol>
<div class="panel warn"><b>No account action occurred here.</b> This workspace has no DrivenData authentication, did not upload, did not retrieve a receipt and did not scrape the leaderboard. The previous “values must be in [0,1]” portal error has no preserved exact rejected file/diagnostic; the zero-outside variant defensively passes a strict whole-array finite [0,1] check, but acceptance remains untested.</div>
<h3>What a next candidate must add</h3><ul><li>Independent off-catalogue or expert truth, rather than another catalogue-derived subtraction.</li><li>A frozen fold-safe experiment that beats the regional comparator with paired 95% CI strictly above zero and at least 3/4 fold wins.</li><li>Feature-alone leakage canaries, matched emission, both uniqueness guards, exact writer validation, then a separate slot selector.</li></ul>
"""
    return page("Executive summary & submission guidance · GEMSDOE33", body, "executive-summary.html")

def build_results() -> str:
    registry = reg("focus_rasters_20261025.json")
    analysis = read_json(ROOT / "evidence" / "focus_registry_analysis_20261025.json")
    by_id = {row["id"]: row for row in analysis.get("artifacts", [])}
    rows = "".join(
        f"<tr><td><code>{esc(item['id'])}</code></td><td>{by_id.get(item['id'], {}).get('dots', 0):,}</td>"
        f"<td>{item['reported_dti']:.4f}</td><td>OWNER/USER-REPORTED<br><span class='small'>not organizer-confirmed</span></td></tr>"
        for item in registry.get("rasters", [])
    )
    card = current_run_card()
    h = card["holdout_dti"]
    ci = h["candidate_95pct_ci"]["interval"]
    bci = h["best_baseline_95pct_ci"]["interval"]
    body = f"""<h2>Nine-site results and score-provenance boundary</h2>
<div class="panel bad"><b>No historical organizer-confirmed result is retained here.</b> Every focus value is an owner/user report without an authenticated submission receipt in this checkout. Values are not training truth, not refreshed from a leaderboard, and not upgraded to official scores. A33-L1 numbers are explicitly HOLDOUT-DTI only.</div>
<div class="scroll"><table><thead><tr><th>Pinned artifact</th><th>Measured dots</th><th>Reported DTI claim</th><th>Evidence class</th></tr></thead><tbody>{rows}</tbody></table></div>
<h2>Forensic answer for the reported 0.2778</h2>
<p><b>Measured bytes:</b> GEMSDOE25 and GEMSDOE30 are identical. GEMSDOE31 solo is an exact subset of that 44,090-dot d2.8 raster after removing 3,891 dots exactly 1 pixel from the mapped catalogue. GEMSDOE32 B2 is an exact subset of solo after removing 2,545 dots at distances greater than 1 and at most 2 pixels. GEMSDOE36 Anderson contains every B2 dot plus 1,200. B2/Anderson binary Spearman is 0.9843; solo/B2 is 0.9676.</p>
<p><b>Scientific interpretation:</b> the inherited lineament field may carry useful fault geometry, while 2.8-pixel spacing reduces redundancy and B2 catalogue exclusion removes predictions likely to pay the DTI false-positive term without covering omitted truth. The reported score ordering is consistent with denominator thrift. It is not causal proof: artifacts are dependent, catalogue proximity is not hidden truth, owner reports are unauthenticated, and contacts/basin edges can mimic faults.</p>
<div class="panel warn">The exact B2 family itself fails this project's duplicate lane: correlations above 0.90 and near-total 3-pixel nesting are common. A new file cannot be justified by making B3 or another strict subset in the analog lane.</div>
<h2>A33-L1 result</h2>
<table><thead><tr><th>Method</th><th>HOLDOUT-DTI</th><th>95% CI</th></tr></thead><tbody>
<tr><td>Raw pooled analog B0</td><td>0.087750</td><td>[0.079569, 0.095940]</td></tr>
<tr><td>Regional visible-fault expert B1</td><td><b>{h['best_comparable_baseline']:.6f}</b></td><td>[{bci[0]:.6f}, {bci[1]:.6f}]</td></tr>
<tr><td>A33-L1 field-balanced transfer</td><td>{h['candidate']:.6f}</td><td>[{ci[0]:.6f}, {ci[1]:.6f}]</td></tr>
<tr><td>Matched random</td><td>0.071432</td><td>[0.068402, 0.074308]</td></tr></tbody></table>
<p>Label: <b>HOLDOUT-DTI</b> (<code>{esc(h['evaluator_version'])}</code>; {h['withheld_positives']:,} withheld positives; 95% spatial-block bootstrap CI). A33-L1 minus B1 = <b>{h['paired_delta']:+.6f}</b>, paired 95% CI [{h['paired_delta_95pct_ci'][0]:+.6f}, {h['paired_delta_95pct_ci'][1]:+.6f}], {h['fold_wins']}/4 fold wins. This is mapped-catalogue proxy evidence, not hidden truth or an organizer score.</p>
<div class="panel bad"><b>Can a higher result be supported?</b> No. A33-L1 failed the comparator gate, so no score projection or slot claim is defensible. Roughly 8% more useful credit would be needed to move 0.2778 to 0.30 at fixed mass/comparable denominator terms; that is algebraic context only.</div>
<p>Review the <a href="https://github.com/buffedlizard55-lab/GEMSDOE33/blob/main/knowledge/11_focus_forensics_and_a33_l1_result_20261025.md">full scientific report</a>, <a href="data/a33_l1_run_card.json">run card</a>, and pinned <a href="https://github.com/buffedlizard55-lab/GEMSDOE33/blob/main/evidence/focus_registry_analysis_20261025.json">pairwise evidence</a>.</p>
"""
    return page("Results & score provenance · GEMSDOE33", body, "results.html")

def build_hypotheses() -> str:
    body = """<h2>Preregistered analog-transfer hypothesis slate</h2>
<p>These five hypotheses were ranked and hash-frozen before A33-L1 implementation. Ranks are expected-improvement priors, not scores. Full layer lists, signatures, missing-fault rationales, prior-art distinctions, costs, falsifiers and source checks are in <a href="https://github.com/buffedlizard55-lab/GEMSDOE33/blob/main/knowledge/10_analog_lane_hypotheses_20261025.md">the frozen slate</a>.</p>
<table><thead><tr><th>Rank</th><th>Hypothesis / layers and signature</th><th>Missing-fault rationale / mimic</th><th>Prior-art distinction, cost, status</th></tr></thead><tbody>
<tr><td>1</td><td><b>A33-L1 target-aligned field-balanced structural transfer.</b> TMI/gravity horizontal gradients, slope, multiscale gradients/coherence, basement-depth and conductivity structure. Seek aligned cross-physics discontinuities portable across Dixie Valley, Brady and Desert Peak windows.</td><td>Concealed basin-bounding/relay faults can retain potential-field structure without mapped scarps. Lithologic contacts and basin-fill edges mimic it.</td><td>Per-field target CDF alignment + equal field loss + frozen 0.80/0.20 regional/analog fusion; unlike raw pooling. Medium cost. <b>Tested; negative.</b></td></tr>
<tr><td>2</td><td><b>A33-L2 leave-one-field-out consensus ensemble.</b> Same 12 channels; fit one target-aligned expert per field and use a lower trimmed mean requiring recurrence in at least two fields.</td><td>Recurrent signatures across structurally different fields may reject field-specific lithology. Contacts remain the mimic.</td><td>Per-field disagreement/two-of-three consensus instead of pooled fitting. Medium–high cost; runnable, untested.</td></tr>
<tr><td>3</td><td><b>A33-L3 matched local-contrast transfer.</b> Express features relative to a 2–5 km annular median/MAD and use same-field, same-relief matched negatives.</td><td>Local contrast may preserve a buried edge while cancelling basin-to-basin level shifts. Relief boundaries can mimic it.</td><td>Annular normalization and matched negatives were absent from H33-F/L1. Medium cost; runnable but requires a separate frozen matching audit.</td></tr>
<tr><td>4</td><td><b>A33-L4 CORAL covariance alignment with field holdout.</b> Whiten each source representation and recolor it to fold-training target covariance.</td><td>Joint covariance alignment may retain co-occurring gravity/magnetic/basement edges while reducing domain identity. Survey covariance can mimic transferability.</td><td>Second-moment alignment rather than raw or marginal-only transfer. Medium cost; runnable, but low domain discrimination cannot bound joint-label error.</td></tr>
<tr><td>5</td><td><b>A33-L5 field-verified BRIDGE/Gabbs supervision.</b> DOE GDR #1682 field picks or USGS Gabbs Valley 3D fault surfaces joined to shared structural layers.</td><td>Independent mapped traces could test geometry absent from the target catalogue and reduce circular validation.</td><td>No active experiment has obtained/audited the source geometry. Highest ceiling; blocked on official archive bytes, schema, CRS, overlap and label policy.</td></tr></tbody></table>
<div class="panel bad"><b>Promotion status:</b> no hypothesis is promoted. A33-L1 failed its frozen comparator gate. A33-L2–L4 remain untested concepts, not results; A33-L5 is blocked until official free payloads are retrieved and audited.</div>
"""
    return page("Ranked hypotheses · GEMSDOE33", body, "hypotheses.html")

def build_data_sources() -> str:
    body = """<h2>Analog data and transfer limits</h2>
<div class="panel bad"><b>No independent dense analog truth was found.</b> The reviewed GEMSDOE24 <code>labels.tif</code> and <code>existing_faults.tif</code> are byte-identical. Repository searches did not locate independent Dixie Valley, Brady or Desert Peak field-verified labels. A33-L1 therefore uses named-field windows and the visible mapped catalogue for a constrained transfer experiment; it is not true leave-one-field-out validation against independent truth.</div>
<p>The shared feature stack contains official-band-derived structural layers, restored from 17 SHA-256-pinned owner-mirror inputs. All 17 were restored and grid-audited, but an owner mirror is not proof of organizer provenance. The sample submission exactly reproduces catalogue values on its finite footprint and is used only for shape, transform, CRS and footprint.</p>
<h3>What A33-L1 did—and did not—test</h3><ul><li>Tested: whether target-CDF adaptation and equal field weighting make named-window structural appearance improve a fold-safe target regional expert.</li><li>Controlled: whole fault components, 15-pixel fold buffer, fold-visible catalogue sampling, pixel-exact masking, feature-alone canaries, matched dot budgets.</li><li>Did not establish: independent source error, dense source-label quality, a Ben-David target-error bound, or performance on private hidden faults.</li><li>Result: adapted fusion beat raw pooled analog transfer but lost to the regional expert; negative.</li></ul>
<h3>External hypotheses and availability</h3>
<div class="panel warn"><b>BRIDGE / DOE GDR context:</b> public metadata was reviewed in earlier work, but no independently verified dense named-field label payload was pinned here. Geometry, label policy and overlap must be audited before use.</div>
<div class="panel warn"><b>USGS seismicity and geothermal context:</b> official/free source concepts were identified, but this environment's outbound allowlist did not permit payload verification. They remain blocked, not “viable” inputs.</div>
<h3>Conditions for a valid transfer-bound claim</h3><ol><li>Independent, audited source labels and a target evaluation set not derived from the same catalogue.</li><li>Common feature support, spatial deduplication and explicit survey/acquisition confound controls.</li><li>Source error, a justified divergence estimator, finite-sample term and joint-label error assumptions—not a classifier AUC alone.</li><li>Predeclared field holdout and off-catalogue confirmation before any competition slot.</li></ol>
<p>See <a href="hypotheses.html">the frozen slate</a>, <a href="research.html">experiment evidence</a>, and <a href="sources.html">source registry and provenance caveats</a>.</p>
"""
    return page("Data sources & transfer limits · GEMSDOE33", body, "data-sources.html")

def build_research() -> str:
    card = current_run_card()
    h = card["holdout_dti"]
    report = read_json(ROOT / "evidence" / "a33_l1_experiment.json")
    canary = report.get("leakage_canary", {})
    worst = max(
        (max(max(row["auc"], 1 - row["auc"]) for row in item["folds"]) for item in canary.get("features", {}).values()),
        default=0.0,
    )
    body = f"""<h2>A33-L1 complete research record</h2>
<div class="panel bad"><b>Final verdict: NEGATIVE — NOT OK TO SUBMIT.</b> The experiment completed in {report.get('elapsed_seconds', 0):.2f} seconds, used one of the three allowed experiments and consumed zero submission slots. The output is retained because unique negative results are part of the scientific record.</div>
<h3>Frozen mechanism</h3><p>Use 12 structural channels; map each named source field's marginal feature distributions onto fold-training target distributions with 257-knot CDF maps; weight source fields equally; train raw analog, adapted analog and regional experts; fuse regional/adapted score ranks at a frozen 0.80/0.20. Named non-fault mimic: lithologic contact or basin-fill edge.</p>
<h3>Fold integrity</h3><p>Four quadrant folds withheld entire connected catalogue components with a 15-pixel buffer. Withheld positive pixels were NW 10,165; NE 12,511; SW 20,534; SE 17,778—60,988 pooled. Catalogue sampling and exclusion used visible faults only; hidden truth had zero overlap with visible faults; training and validation masks were disjoint.</p>
<h3>Leakage canary</h3><p>All 12 frozen features passed standalone tests. Worst fold-level two-sided AUC was <b>{worst:.4f}</b>; stop threshold was strictly above 0.90. This rejects obvious direct leakage but does not establish independent labels.</p>
<h3>HOLDOUT-DTI result</h3><p>A33-L1 = <b>{h['candidate']:.6f}</b> (95% CI [{h['candidate_95pct_ci']['interval'][0]:.6f}, {h['candidate_95pct_ci']['interval'][1]:.6f}]); best regional comparator = <b>{h['best_comparable_baseline']:.6f}</b> (95% CI [{h['best_baseline_95pct_ci']['interval'][0]:.6f}, {h['best_baseline_95pct_ci']['interval'][1]:.6f}]). Paired delta = <b>{h['paired_delta']:+.6f}</b>, 95% CI [{h['paired_delta_95pct_ci'][0]:+.6f}, {h['paired_delta_95pct_ci'][1]:+.6f}], 0/4 fold wins. Label: HOLDOUT-DTI (<code>{esc(h['evaluator_version'])}</code>; 60,988 withheld positives; spatial-block bootstrap 95% CI). Not a competition score.</p>
<h3>Uniqueness</h3><p>Before placement, max Spearman was {card['correlation_overlap_vs_registry']['surface']['max_spearman_rho']:.4f}. Final max Spearman was {card['correlation_overlap_vs_registry']['final_dots']['max_spearman_rho']:.5f}; max candidate-dot fraction within 3 px was {100*card['correlation_overlap_vs_registry']['final_dots']['max_candidate_fraction_within_3px']:.2f}%. All are below frozen stop thresholds.</p>
<h3>Artifacts and evidence</h3><ul><li><a href="downloads/{esc(card['submission']['file'])}">A33-L1 unique zero-outside TIFF</a> — research only</li><li><a href="downloads/receipt-gemsdoe33-a33-l1-analog-transfer-research-37654-20261025-85c94a805a34.json">shared-writer receipt</a></li><li><a href="data/a33_l1_run_card.json">final run card</a></li><li><a href="https://github.com/buffedlizard55-lab/GEMSDOE33/blob/main/evidence/a33_l1_experiment.json">complete experiment evidence</a></li><li><a href="https://github.com/buffedlizard55-lab/GEMSDOE33/blob/main/evidence/analog_lane_preregistration_20261025.json">hash-frozen preregistration</a></li><li><a href="https://github.com/buffedlizard55-lab/GEMSDOE33/blob/main/evidence/a33_l1_three_pass_review_20261025.md">three-pass release review</a></li></ul>
<h2>Historical negative controls</h2>
<p>H33-6 remains failed/duplicate and H33-F remains negative; neither is slot-approved. Their historical files remain for audit but do not supersede the current A33-L1 run card. No post-result experiment was used to tune A33-L1.</p>
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

<h3>Owner-mirror input pin registry</h3>
<p>The pin list records reproducible owner-mirror inputs. All 17 files were restored and hash-verified for A33-L1, and their grid audit passed. These hashes establish byte identity with the named GitHub mirrors; they do <b>not</b> authenticate the files as organizer downloads. Generated caches are intentionally untracked.</p>
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
<div class="panel bad"><h3>A33-L1 scientific stop</h3><p>The unique raster passed leakage, novelty and format guards but lost to the regional comparator (paired HOLDOUT-DTI delta −0.004870, 95% CI [−0.010900, +0.001226], 0/4 folds). It is not OK to submit. No selector, upload or score projection followed.</p></div>
<div class="panel warn"><h3>Analog truth is not independent</h3><p>No independent dense Dixie Valley, Brady or Desert Peak label archive was found. In the reviewed shared source, <code>labels.tif</code> and <code>existing_faults.tif</code> are byte-identical. A33-L1 is therefore a catalogue hide-and-recover proxy, not field-verified transfer validation.</p></div>
<div class="panel warn"><h3>Historical score evidence</h3><p>The nine focus DTI values are owner/user reports without authenticated organizer receipts retained here. Exact raster lineage is measured; portal score/file associations are not independently confirmed.</p></div>

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
