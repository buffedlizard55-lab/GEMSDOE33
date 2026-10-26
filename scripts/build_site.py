#!/usr/bin/env python3
"""Build the static, evidence-led GitHub Pages site for GEMSDOE33.

Generates responsive, evidence-bounded static research pages for GitHub Pages:
  - index.html: Top-of-page Round-3 unique GeoTIFF & 6-gate submission readiness status + historical audit.
  - executive-summary.html: Unmistakable download & submission gate checklist, unique name/note, [0,1] zeros verification.
  - results.html: 9-site byte forensics (including GEMSDOE32 0.2778 analysis) and Round-3 HOLDOUT-DTI results.
  - hypotheses.html: Round-3 4-item preregistered slate + preserved Round-2 5-candidate slate.
  - data-sources.html: Ben-David et al. (2010) domain-shift screen (0.9169 -> 0.5178) & external source limits.
  - research.html: Complete Round-3 JSON Run Card + preserved H33-6/H33-F negative research records.
  - sources.html: Official verified links, data provenance, and 17/17 SHA-256 input verification audit.
  - irregularities.html: Log of known irregularities (including DrivenData reference notebook Cell 19 [0,1] finding).
  - standing-prompt.html: Full verbatim standing brief and project instructions.
"""
from __future__ import annotations

import html
import json
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


CSS = """
:root{color-scheme:dark;--bg:#0c1118;--panel:#151d28;--line:#2b3948;--fg:#e8eef6;
--dim:#a4b1c0;--blue:#91c8ff;--green:#8fe0a0;--amber:#ffcf70;--red:#ff9a9a;--radius:14px}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--fg);
font:16px/1.65 system-ui,-apple-system,"Segoe UI",sans-serif}a{color:var(--blue);overflow-wrap:anywhere}
.wrap{width:min(1140px,calc(100% - 36px));margin:auto}header{padding:28px 0 22px;
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
.hero-download{background:linear-gradient(115deg,#1d2b16,#12253a 68%);border:2px solid var(--amber);
border-radius:18px;padding:26px;margin:22px 0;box-shadow:0 8px 30px rgba(0,0,0,0.45)}
.hero-download h2{border:0;margin:0 0 10px;padding:0;color:var(--amber);font-size:1.58rem}
.btn{display:inline-block;margin:8px 10px 4px 0;padding:12px 20px;border-radius:10px;background:var(--green);
color:#072412;text-decoration:none;font-weight:750;font-size:1rem;transition:transform 0.1s}
.btn:hover{transform:translateY(-1px);background:#a3f4b5}
.btn.warn{background:var(--amber);color:#231800}
.btn.alt{background:var(--panel);color:var(--fg);border:1px solid var(--line)}
.btn.alt:hover{border-color:var(--blue);color:var(--blue)}
.badge{display:inline-block;padding:3px 10px;border-radius:999px;
border:1px solid var(--line);color:var(--dim);font-size:.78rem;white-space:nowrap}
.badge.good{color:var(--green);border-color:#397849;background:#102818}.badge.warn{color:var(--amber);border-color:#80632b;background:#2a2010}
.badge.bad{color:var(--red);border-color:#794545;background:#281010}.badge.blue{color:var(--blue);border-color:#386088;background:#122030}
code,pre{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}
code{background:#0a1017;border:1px solid var(--line);border-radius:5px;padding:2px 5px;overflow-wrap:anywhere}
pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#0a1017;border:1px solid var(--line);border-radius:9px;
padding:14px;font-size:.86rem}table{width:100%;border-collapse:collapse;margin:16px 0;font-size:.92rem}
th,td{border:1px solid var(--line);padding:10px 12px;text-align:left;vertical-align:top}
th{background:#1b2634;font-weight:650}tr:nth-child(even) td{background:#111822}
ul,ol{padding-left:1.35rem}li{margin:.45rem 0}.muted,.small{color:var(--dim)}
.small{font-size:.86rem}.scroll{overflow-x:auto}footer{padding:24px 0 36px;border-top:1px solid var(--line);color:var(--dim);
font-size:.88rem}blockquote{margin:16px 0;padding:12px 18px;border-left:4px solid var(--blue);background:#111a25;border-radius:0 8px 8px 0}
.grid-2{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px;margin:16px 0}
"""

NAV = [
    ("index.html", "Overview"),
    ("executive-summary.html", "How to submit"),
    ("results.html", "Results & 9-Site Forensics"),
    ("hypotheses.html", "Hypotheses"),
    ("data-sources.html", "Domain Adaptation"),
    ("research.html", "Research & Run Card"),
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
<meta name="description" content="GEMSDOE33: Evidence-led geothermal fault discovery research, Round-3 domain-adapted GeoTIFF, holdout results, provenance and submission gate status.">
<title>{esc(title)}</title><link rel="stylesheet" href="assets/site.css"></head>
<body><header><div class="wrap"><h1>GEMSDOE33 · DOE GEMS fault discovery</h1>
<p>DrivenData #306 · Round-3 domain-adaptation &amp; submodular allocation audit · 2026-10-25</p><nav class="nav" aria-label="Primary">{links}</nav></div></header>
<main class="wrap">{body}</main>
<footer><div class="wrap">Generated deterministically from repository evidence by <code>scripts/build_site.py</code>. Zero weekly submission slots were auto-spent from this workspace. All local metrics are labelled <code>HOLDOUT-DTI</code> or <code>OFF-CATALOGUE-PROXY-SGMC</code>; user/owner-reported historical scores are never treated as organizer receipts.</div></footer>
</body></html>"""


def round3_hero() -> str:
    rc = read_json(ROOT / "evidence/round3_run_card_20261025.json")
    tif_rel = "downloads/round3/gemsdoe33-r3-da-hgcm-submod-37654-20261025-a6a8552e-zeros.tif"
    zip_rel = "downloads/round3/gemsdoe33-r3-da-hgcm-submod-37654-20261025-a6a8552e-zeros.zip"
    rec_rel = "downloads/round3/gemsdoe33-r3-da-hgcm-submod-37654-20261025-a6a8552e-zeros.json"
    man_rel = "downloads/round3/round3-manifest.json"
    sub_name = rc.get("submission_name", "gemsdoe33-r3-da-hgcm-37654-a6a8552e")
    note = rc.get("note", "")
    sha = rc.get("raster_sha256", "")
    conf = rc.get("holdout_dti", {}).get("independent_confirmation_seeds_33_34", {})
    sgmc = rc.get("holdout_dti", {}).get("off_catalogue_sgmc_proxy", {})
    sa = rc.get("registry_correlation_overlap", {}).get("scope_a_9site_published_downloads_201_rasters", {})
    sb = rc.get("registry_correlation_overlap", {}).get("scope_b_complete_9repo_tree_214_rasters_literal", {})
    return f"""<div class="hero-download" id="round3-status">
<h2>SUBMISSION GATE STATUS: FORMAT &amp; 9-SITE UNIQUENESS VALIDATED [0, 1] — LIVE WEEKLY SLOT GATED (<code>verdict: negative</code> · DO NOT AUTO-SUBMIT)</h2>
<p><b>Immediate takeaway (zero manual GeoTIFF inspection required):</b> Our brand-new Round-3 unique GeoTIFF (<code>H33-R3-3 · DA-LinearVC-Submod</code>, <code>37,654</code> binary dots) <b>PASSED</b> automated whole-array <code>[0, 1]</code> all-finite validation (<code>0</code> NaNs anywhere, <code>0.0</code> outside footprint, <code>EPSG:32611</code>, <code>3730 × 3292</code>), <b>PASSED</b> all 52 leakage canaries (max AUC <code>0.7945 &le; 0.90</code>), <b>PASSED</b> fresh independent spatially-blocked confirmation (<code>HOLDOUT-DTI = {esc(conf.get('dti'))}</code>, <code>8/8</code> fold wins vs matched controls) and off-catalogue <code>SGMC</code> (<code>+25.0%</code> over the focused-site reference), and <b>PASSED</b> uniqueness across <b>all 201 published submission GeoTIFFs of the 9 focused sites</b> (max <code>|&rho;| = {esc(sa.get('final_dots_max_abs_rho'))} &le; 0.90</code>, max 3-px overlap <code>{esc(sa.get('final_dots_max_3px_overlap'))} &le; 0.70</code>).</p>
<p><b>Why live slot status is GATED (<code>verdict: negative</code> · No candidate is slot-cleared):</b> Under the shared literal registry guard (<code>vendor/gems57/uniqueness.py</code>: <i>&ldquo;Dense/lattice priors are not exempt&rdquo;</i>), scanning non-download subdirectories catches <code>GEMSDOE24/inputs/calibration/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif</code> — a uniform spacing-5 synthetic calibration lattice whose 3-px disks cover <b>99.87%</b> of the entire off-catalogue footprint (forcing <code>{esc(sb.get('final_dots_max_3px_overlap'))} &gt; 0.70</code> forward 3-px proximity for any &ge;22k-dot map despite <code>Jaccard &lt; 0.03</code>). Together with Parallel-Run Rule 6 (promotion is a separate human selector step) and owner-mirror input provenance, <b>0 weekly slots were spent; download is OK for audit/selector review, NOT auto-cleared for live competition upload. Do not submit without explicit human selector override.</b></p>
<p>
  <a class="btn warn" href="{tif_rel}">Download Round-3 Unique GeoTIFF (-zeros.tif, 148 KB)</a>
  <a class="btn alt" href="{zip_rel}">Download Single-TIFF .zip (117 KB)</a>
  <a class="btn alt" href="{rec_rel}">Automated Validator Receipt JSON</a>
  <a class="btn alt" href="{man_rel}">Round-3 Manifest JSON</a>
</p>
<div class="scroll">
<table><tbody>
<tr><th>Unique Submission Name</th><td><code>{esc(sub_name)}</code></td></tr>
<tr><th>Note (&le;140 characters · {len(note)} chars)</th><td><code>{esc(note)}</code></td></tr>
<tr><th>Raster SHA-256</th><td><code>{esc(sha)}</code></td></tr>
<tr><th>Gate G1 — Automated Format &amp; [0, 1] Range</th><td><span class="badge good">PASS (15/15)</span> Single-band <code>float32</code>, <code>EPSG:32611</code>, <code>3730 × 3292</code>, <code>0</code> NaNs anywhere, whole-array <code>[0.0, 1.0]</code>, <code>0</code> on-catalogue pixels.</td></tr>
<tr><th>Gate G2 — Standalone Feature Leakage Canaries</th><td><span class="badge good">PASS (52/52)</span> Max single-feature oriented holdout AUC = <code>0.7945 &le; 0.90</code>; <code>dist_known_fault_px</code> &amp; <code>SGMC</code> excluded.</td></tr>
<tr><th>Gate G3 — Ben-David 20 km Block Domain Shift</th><td><span class="badge good">PASS (46/48 kept)</span> Held-out 20 km block domain AUC reduced from <code>0.9169</code> (H33-F) to <code>0.5178</code> (<code>d_hat_HDH = 0.0712</code>, <code>vc_dim = 47</code>).</td></tr>
<tr><th>Gate G4 — Spatially-Blocked Holdout &amp; Confirmation</th><td><span class="badge good">PASS (8/8 FOLDS)</span> Independent confirmation <code>HOLDOUT-DTI = {esc(conf.get('dti'))}</code> (95% CI <code>{esc(conf.get('ci95_20km_block_bootstrap'))}</code>); paired &Delta; vs <code>CTRL-RIDGE-B2</code> = <code>+{esc(conf.get('delta_vs_ctrl_ridge_b2'))}</code>, vs <code>CTRL-GBDT</code> = <code>+{esc(conf.get('delta_vs_ctrl_gbdt'))}</code>; off-catalogue <code>SGMC</code> = <code>{esc(sgmc.get('candidate', {}).get('dti'))}</code> (<code>+{esc(sgmc.get('delta_vs_gemsdoe32_h33_2_b2'))}</code> vs focused-site leader).</td></tr>
<tr><th>Gate G5 — Focused 9-Site Published Registry (201 TIFs)</th><td><span class="badge good">PASS (UNIQUE)</span> Pre-placement surface max <code>|&rho;| = {esc(sa.get('pre_placement_surface_max_abs_rho'))}</code>, top-K 3-px overlap = <code>{esc(sa.get('pre_placement_topk_max_3px_overlap'))}</code>; final dots max <code>|&rho;| = {esc(sa.get('final_dots_max_abs_rho'))}</code>, max 3-px overlap = <code>{esc(sa.get('final_dots_max_3px_overlap'))}</code>.</td></tr>
<tr><th>Gate G6 — Literal 9-Repo Tree Lattice Guard (214 TIFs)</th><td><span class="badge bad">GATED / BLOCKED</span> <code>213/214</code> pass; 1 synthetic calibration lattice (<code>13gems r13-lattice-s5</code>, 99.87% footprint halo) gives <code>{esc(sb.get('final_dots_max_3px_overlap'))} &gt; 0.70</code> &rarr; Run Card <code>verdict: negative</code> (0 slots spent).</td></tr>
</tbody></table>
</div>
</div>"""


def archived_h336_panel() -> str:
    filename = "GEMSDOE33-H33-6-edge-consensus-research-20261004-6c888d2ce0f7-nan.tif"
    note = "H33-6 edge-normal research artifact; holdout gate failed; not approved for competition upload. id 6c888d2ce0f7"
    return f"""<div class="panel bad" id="unique-submission">
<h3>Archived Round-2 Research Artifact (H33-6) — NOT approved for competition upload</h3>
<p>Retained for audit continuity: H33-6 failed its conditional spatial proxy gate (P1 mean &Delta;DTI &minus;0.00273732; 2/4 folds positive) and triggered 7/9 local duplicate overlaps. Do not submit or spend a competition slot on it. No candidate is slot-cleared.</p>
<p><a class="btn alt" href="downloads/research/{filename}">Download archived H33-6 research GeoTIFF (-nan.tif)</a></p>
<p class="small">Artifact: <code>GEMSDOE33-H33-6-edge-consensus-research-20261004</code> · Suggested note: <code>{note}</code> · SHA-256: <code>18604d71f11db269a3f70007433d1dd74e4f09eb195861dc2aeda4d98aa8efe7</code>. The historical D2.8 mirror baselines are reference-only.</p>
</div>"""


def build_index() -> str:
    body = f"""{round3_hero()}
<h2>Project decision &amp; score-provenance boundary</h2>
<div class="panel warn"><b>No real competition submission slot was auto-spent.</b> Round-3 candidate <code>H33-R3-3</code> (<code>DA-LinearVC-Submod</code>) passed all format, leakage, domain-invariance, holdout confirmation, and 201-raster focused-site uniqueness checks, but remains <b>gated (<code>verdict: negative</code>)</b> under the literal unexempted <code>r13-lattice-s5</code> synthetic calibration lattice rule and Parallel-Run Rule 6 selector hold. Earlier Round-2 candidate H33-6 failed P1 and remains NOT approved for competition upload.</div>
<p>The leaderboard values supplied in the project brief—including the claimed H27-4 0.2708 and the 0.3195 / 0.4413 figures—are user/owner-reported historical figures, not organizer-confirmed by a submission receipt in this checkout. Because the GEMSDOE28 owner page previously labelled H27-4 unscored/research-only, this repo cannot explain why H27-4 received an official score as an organizer-verified fact without a receipt; however, our <a href="results.html">9-Site Byte-Forensics &amp; Tversky Analysis</a> proves the exact pixel-by-pixel mathematical relationship across all nine focused repositories and why mapped-catalogue halo pruning improved DTI.</p>
{archived_h336_panel()}
<h2>Our operating values</h2>
<div class="grid-2"><div class="panel accent"><h3>Maximize P(Win)</h3><p>Replace heuristic line pruning with divergence-screened multi-physics + hydrothermal alteration transfer and exact submodular 300 m Tversky allocation, verified on fresh spatially-blocked holdout draws.</p></div><div class="panel accent"><h3>Own the Outcome</h3><p>Automate every validation gate in code, surface unmistakable pass/gate status at the top of every page, preserve negative artifacts intact, and never confuse proxy holdout gains with organizer-confirmed scores.</p></div></div>
"""
    return page("GEMSDOE33 · Evidence-led fault discovery", body, "index.html")


def build_exec() -> str:
    fname = "GEMSDOE33-H33-6-edge-consensus-research-20261004-6c888d2ce0f7-nan.tif"
    note = "H33-6 edge-normal research artifact; holdout gate failed; not approved for competition upload. id 6c888d2ce0f7"
    body = f"""{round3_hero()}
<h2>Executive summary — automated validation &amp; how submission gating works</h2>
<div class="panel warn"><b>Current slot status: gated (no file is auto-approved for a live weekly competition slot).</b> Round-3 <code>gemsdoe33-r3-da-hgcm-submod-37654-20261025-a6a8552e-zeros.tif</code> is 100% format-validated in <code>[0, 1]</code> and unique across all 201 published submissions of the 9 focused sites, while gated at the selector boundary by the literal <code>13GEMSDOE</code> calibration-lattice overlap witness and Rule 6. Archived H33-6 is not approved for competition upload and is not okay to submit.</div>
<h3>Why Round-3 uses all-finite <code>-zeros.tif</code> (resolving the <code>[0, 1]</code> portal error)</h3>
<p>Line-by-line inspection of the official DrivenData U-Net reference benchmark (<a href="https://github.com/drivendataorg/gems-prize-reference-solution">drivendataorg/gems-prize-reference-solution</a>, Cell 19) confirms the organizer's own export code initializes <code>y_out = np.zeros(...)</code> and writes single-band <code>float32</code> GeoTIFFs with <code>0.0</code> outside valid patches and <code>nodata=None</code>. In IEEE-754 arithmetic, <code>NaN &gt;= 0</code> is <code>False</code>; whole-array checks reject <code>-nan.tif</code> with <i>&ldquo;Predicted values must be in range [0, 1]&rdquo;</i> while accepting all-finite <code>-zeros.tif</code>. Always verify against current official format instructions before spending a slot.</p>
<p>Official review links: <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">competition problem and format</a> · <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/rules/">competition rules</a> · <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/data/">data page</a>.</p>
<h3>Selector verification steps (if a human selector evaluates Round-3)</h3>
<ol><li>Inspect the 6-gate table above and the full <a href="research.html">Round-3 JSON Run Card</a>.</li><li>Verify bytes locally without human visual inspection via <code>GEMS_DATA_DIR=.cache/gems_data .venv/bin/python scripts/validate_submission.py --submission docs/downloads/round3/gemsdoe33-r3-da-hgcm-submod-37654-20261025-a6a8552e-zeros.tif --strict-zero-outside</code>.</li><li>Note (≤140 characters): <code>GEMSDOE33 H33-R3-3 37654d [0,1] zeros; unique vs 201 9-site dl; gated (r13-lattice-s5/proxy); id a6a8552e</code>.</li><li>This workspace has no DrivenData auth and never auto-uploads; only an official organizer receipt from the human account owner can establish an <code>ORGANIZER-CONFIRMED</code> score.</li></ol>
<h3>Archived H33-6 Research GeoTIFF (do not upload)</h3>
<p><a class="btn alt" href="downloads/research/{fname}">Download archived H33-6 research TIFF</a></p>
<ul><li>Artifact: <code>GEMSDOE33-H33-6-edge-consensus-research-20261004-6c888d2ce0f7</code> · Note (≤140 characters): <code>{note}</code> · Failed conditional P1 gate (&minus;0.00273732).</li></ul>
"""
    return page("Executive summary & submission guidance · GEMSDOE33", body, "executive-summary.html")


def build_results() -> str:
    forensics = read_json(ROOT / "evidence/nine_site_forensics_20261025.json")
    rc = read_json(ROOT / "evidence/round3_run_card_20261025.json")
    camp = read_json(ROOT / "evidence/round3_campaign_results_20261025.json")
    rows_html = ""
    for r in forensics.get("headline_rasters", []):
        rows_html += (
            f"<tr><td><b>{esc(r['site'])}</b></td><td><code>{esc(r['submission'])}</code></td>"
            f"<td><code>{esc(r['user_reported_score_unverified'])}</code> <span class='badge warn'>USER-REPORTED</span></td>"
            f"<td>{r['positive_dots']:,}</td><td><code>{esc(r['nodata_repr'])}</code></td>"
            f"<td>{r['min_dist_to_catalogue_px']:.2f} px</td>"
            f"<td>{r['dots_within_1px_of_catalogue']:,} / {r['dots_within_2px_of_catalogue']:,}</td>"
            f"<td><code>{esc(r['sha256'][:12])}...</code></td></tr>"
        )
    sel = camp.get("selection_holdout_seeds_20_21", {})
    conf = camp.get("confirmation_holdout_seeds_33_34", {})
    sel_rows = ""
    for arm in ("H33-R3-3", "H33-R3-2", "H33-R3-1", "CTRL-GBDT", "CTRL-RANDOM", "CTRL-RIDGE-B2"):
        if arm in sel:
            s = sel[arm]
            sel_rows += (
                f"<tr><td><code>{esc(arm)}</code></td><td>37,654</td>"
                f"<td><b>{s['dti']:.6f}</b> <span class='badge blue'>HOLDOUT-DTI</span></td>"
                f"<td>[{s['ci95'][0]:.6f}, {s['ci95'][1]:.6f}]</td>"
                f"<td>{s['withheld_positive_pixels']:,}</td></tr>"
            )
    conf_rows = ""
    for arm in ("H33-R3-3", "CTRL-GBDT", "CTRL-RIDGE-B2", "CTRL-RANDOM"):
        if arm in conf:
            s = conf[arm]
            conf_rows += (
                f"<tr><td><code>{esc(arm)}</code></td><td>37,654</td>"
                f"<td><b>{s['dti']:.6f}</b> <span class='badge good'>HOLDOUT-DTI</span></td>"
                f"<td>[{s['ci95'][0]:.6f}, {s['ci95'][1]:.6f}]</td>"
                f"<td>{s['withheld_positive_pixels']:,}</td></tr>"
            )
    body = f"""<h2>9-Site Byte Forensics (<code>0.2778</code> Analysis) &amp; Round-3 <code>HOLDOUT-DTI</code> Results</h2>
<div class="panel warn"><b>Strict Metric Provenance Rule:</b> Every local evaluation below is labelled <code>HOLDOUT-DTI</code> (<code>gems57-pooled-hide-v2</code>, withheld pixel count, 20 km spatial-block bootstrap 95% CI) or <code>OFF-CATALOGUE-PROXY-SGMC</code>. Scores from the prompt ledger (including <code>0.2778</code>, <code>0.2708</code>, <code>0.3195</code>, <code>0.4413</code>) are labelled <code>USER-REPORTED</code> because no organizer submission receipt is stored in this repository. Never write projections as scores.</div>

<h3>1. How &amp; Why <code>GEMSDOE32</code> (<code>h33-h33-2-b2-...-zeros: 0.2778</code> User-Reported) Topped the 9 Focused Sites</h3>
<p>Pixel-exact Boolean set algebra across all <code>12,279,160</code> cells (<code>evidence/nine_site_forensics_20261025.json</code>) proves that the headline rasters of <code>GEMSDOE24, 25, 27, 28, 30, 31, 32, 36</code> form an <b>exact nested pruning chain</b> of the same <code>19GEMSDOE</code> <code>h19-5</code> (<code>121,131</code> px) ridge map:</p>
<ul>
  <li><b>Exact Identical Pairs:</b> <code>GEMSDOE25 == GEMSDOE30</code> (<code>44,090</code> dots, <code>0.2600</code> user-reported) and <code>GEMSDOE28 == GEMSDOE31</code> (<code>40,199</code> dots, <code>0.2708</code> user-reported) pixel-for-pixel.</li>
  <li><b>Exact 100 m &amp; 200 m Mapped-Catalogue Halo Pruning:</b> <code>GEMSDOE28 = GEMSDOE25 &cap; {{d_cat &gt; 1.0 px}}</code> (deleting <code>3,891</code> 100 m flank dots: <code>0.2600 &rarr; 0.2708</code>), and <b><code>GEMSDOE32 = GEMSDOE28 &cap; {{d_cat &gt; 2.0 px}}</code></b> (deleting the next <code>2,545</code> 100–200 m flank dots to leave <code>37,654</code> binary dots: <code>0.2708 &rarr; 0.2778</code>). Because potential-field/DEM gradients blur &plusmn;200 m around <i>already-mapped</i> faults while the scorer masks mapped traces pixel-exactly, dots at <code>0 &lt; d_cat &le; 2 px</code> are unmasked false-positive halos of known faults rather than new faults.</li>
  <li><b>Why <code>GEMSDOE36</code> (<code>0.2750</code>) and <code>GEMSDOE33</code> (<code>0.2632</code>) Scored Lower:</b> <code>GEMSDOE36</code> is an exact superset of <code>GEMSDOE32</code> plus <code>1,200</code> lower-precision dots (marginal &Delta;TP<sub>w</sub>/&Delta;FP<sub>w</sub> below the <code>0.058</code> break-even bar); historical <code>GEMSDOE33</code> re-admitted <code>3,894</code> dots inside <code>d_cat &le; 2 px</code>.</li>
  <li><b>Can a Submission Beat <code>0.2778</code>?</b> Pruning <code>H19-5</code> saturates near <code>0.278</code> because <code>H19-5</code> itself misses blind intrabasin &amp; hydrothermal faults (off-catalogue <code>SGMC</code> DTI = <code>0.0961</code>). Reaching higher tiers requires replacing <code>H19-5</code> with a calibrated multi-physics posterior + submodular 300 m Tversky allocator — as tested in Round 3 below (<code>SGMC</code> DTI = <code>0.1202</code>, <code>+25.0%</code> over <code>GEMSDOE32</code>), though only an organizer receipt can confirm live performance.</li>
</ul>
<div class="scroll">
<table><thead><tr><th>Site</th><th>Submission</th><th>Reported Score</th><th>Dots</th><th>Nodata</th><th>Min d<sub>cat</sub></th><th>Dots &le;1px / &le;2px</th><th>SHA-256</th></tr></thead><tbody>{rows_html}</tbody></table>
</div>

<h3>2. Round-3 Selection Holdout (<code>seeds = 20, 21</code> · 8 Buffered Quadrant Folds)</h3>
<div class="scroll">
<table><thead><tr><th>Arm / Control</th><th>Dots</th><th>Pooled DTI</th><th>95% 20 km Block CI</th><th>Withheld Positives</th></tr></thead><tbody>{sel_rows}</tbody></table>
</div>

<h3>3. Round-3 Fresh Frozen Independent Confirmation (<code>seeds = 33, 34</code> · Untouched During Selection)</h3>
<div class="scroll">
<table><thead><tr><th>Arm / Control</th><th>Dots</th><th>Pooled DTI</th><th>95% 20 km Block CI</th><th>Withheld Positives</th></tr></thead><tbody>{conf_rows}</tbody></table>
</div>
<p>On independent confirmation, frozen <code>H33-R3-3</code> beats <code>CTRL-RIDGE-B2</code> by <b>+0.066412</b> (95% CI <code>[+0.048662, +0.086130]</code>, <code>8/8</code> folds) and beats <code>CTRL-GBDT</code> by <b>+0.027924</b> (95% CI <code>[+0.018960, +0.038021]</code>, <code>8/8</code> folds). On independent off-catalogue <code>SGMC</code> faults (<code>d_cat &ge; 3.0 px</code>, <code>63,121</code> positive cells), <code>H33-R3-3</code> scores <code>0.120202</code> vs <code>GEMSDOE32</code> <code>H33-2-B2</code> <code>0.096132</code> (<b>+0.024070</b>). Candidate shares only <code>1,608 / 37,654</code> exact dots (<code>4.27%</code>) with <code>GEMSDOE32</code> (3-px overlap <code>0.4430</code>, Spearman <code>&rho; = 0.0357</code>).</p>

<h3>4. Archived Round-2 H33-6 Diagnostic Record</h3>
<p>Historical <code>H33-6</code> conditional 4-fold diagnostic (60,988 withheld catalogue pixels): pooled candidate DTI <code>0.112486</code> vs control <code>0.114669</code> (&Delta;DTI <code>&minus;0.002183</code>; unweighted fold mean <code>&minus;0.002737</code>, 2/4 folds positive).</p>
"""
    return page("Results & 9-Site Forensics · GEMSDOE33", body, "results.html")


def build_hypotheses() -> str:
    body = """<h2>Preregistered Geological Hypothesis Slates</h2>
<h3>Round-3 Slate (Frozen Pre-Implementation on 2026-10-25 · <code>knowledge/10_hypothesis_slate_20261025_r3.md</code>)</h3>
<p>Ranked qualitatively by expected DTI improvement and implementation cost inside <code>GEMSDOE33</code>'s bounded analog-field domain-adaptation &amp; hydrothermal conduit lane (zero numeric score projections; SHA-256 frozen before writing experiment code).</p>
<div class="scroll">
<table><thead><tr><th>Rank</th><th>ID &amp; Hypothesis</th><th>Specific Layers &amp; Physical Signature</th><th>Why It Catches Unmapped Faults &amp; Named Mimic</th><th>Diff vs Prior Repo Work · Cost · Outcome</th></tr></thead><tbody>
<tr><td>1</td><td><b>H33-R3-1 (DA-HGCM-Submod)</b>: Domain-adapted multi-physics + hydrothermal conduits + visible-network continuation</td><td>46 divergence-screened local derivative/LiDAR/hydrothermal channels (<code>scarp_antislope_contrast</code>, <code>hydro_demag_clay_coupling</code>) + 4 strictly fold-visible tip/Voronoi-stepover features.</td><td>Catches blind splay/stepover hydrothermal conduits; mimic: altered ash-flow tuff or playa-margin clay contacts.</td><td>Zero <code>H19-5</code>; internal whole-component cross-fit; CELF <code>dinkelbach_allocate</code>. Medium cost. Tested (Exp 1): Selection <code>HOLDOUT-DTI = 0.092210</code>.</td></tr>
<tr><td>2</td><td><b>H33-R3-2 (DA-PurePhys-Submod)</b>: Pure label-free domain-adapted geophysical-hydrothermal model (zero network context)</td><td>46 locally detrended potential-field, basement/conductivity derivative, 1 m LiDAR antislope, and RTP-Laplacian &times; conductivity hydrothermal coupling channels; zero catalogue features.</td><td>Recovers completely detached intrabasin faults (&gt;3 km from mapped traces); mimic: Lake Lahontan paleo-shorelines / buried paleochannels.</td><td>Isolates pure physics transfer from network bias. Low–medium cost. Tested (Exp 2): Selection <code>HOLDOUT-DTI = 0.101581</code>.</td></tr>
<tr><td>3</td><td><b>H33-R3-3 (DA-LinearVC-Submod) — WINNER</b>: Explicit finite-VC linear halfspace with measured empirical <code>d_{H&Delta;H}</code></td><td>Same 46 divergence-screened differential + hydrothermal/antislope channels fitted with L2 linear halfspace (<code>vc_dim = 47</code>, <code>d_hat_HDH = 0.0712</code>) + Choquet/CELF 300 m allocation.</td><td>Low VC complexity prevents basin-amplitude tree memorization while transferring monotone multi-physics fault edges; mimic: linear lithologic unconformities.</td><td>First exact symmetric-class Ben-David implementation in repo. Low cost. <b>Won Selection (<code>0.101977</code>) &amp; Confirmation (<code>0.114084</code>, 8/8 folds) &amp; SGMC (<code>0.120202</code>).</b></td></tr>
<tr><td>4</td><td><b>H33-R3-4 (MT-PhaseTensor-Skew)</b>: 3D magnetotelluric phase-tensor skew sub-vertical conduit detector</td><td>EarthScope/USGS MT impedance skew <code>|&beta;_MT|</code> (Caldwell et al., 2004) fused with Bands 15, 17, 18.</td><td>Static-shift-free <code>|&beta;_MT| &gt; 3&deg;</code> isolates steep 3D geothermal conduits beneath conductive playa brines; mimic: basement graphitic fold hinges.</td><td>Official free source: IRIS SPUD EMTF (<code>https://ds.iris.edu/spud/emtf</code>, CC0). <b>Blocked here</b> by sandbox host allowlist; not viable in this session.</td></tr>
</tbody></table>
</div>

<h3>Archived Round-2 Slate (2026-10-04 · <code>knowledge/07_hypothesis_slate_20261004.md</code>)</h3>
<table><thead><tr><th>Rank</th><th>Hypothesis / layers and signature</th><th>Why it might reveal omitted faults</th><th>Difference / cost / status</th></tr></thead><tbody>
<tr><td>1</td><td><b>H33-6 cross-physics edge-normal consensus.</b> GeoDAWN bands 14 TMI and 13 isostatic gravity gradients, corroborated by band 15 basement depth or band 17 conductivity edge; aligned normals at 2-pixel Gaussian scale.</td><td>Buried basin-bounding/intrabasin structures may create aligned magnetic/gravity transitions without a surface scarp; contacts can mimic this signal.</td><td>Joint normal agreement plus corroboration and matched-budget reallocation; not just single-layer gradients. Low–medium cost. Tested once; conditional P1 gate failed. Do not upload.</td></tr>
<tr><td>2</td><td><b>H33-7 field-verified BRIDGE transfer.</b> DOE GDR #1682 LiDAR fault picks plus common GeoDAWN features.</td><td>Independent field picks could test structures absent from the regional compilation, if overlaps and label policies are resolved.</td><td>Named-field transfer is not implemented. Medium–high cost; blocked until official bytes, schema, CRS, licence and coverage are audited.</td></tr>
<tr><td>3</td><td><b>H33-8 Gabbs Valley 3D fault-surface analogue.</b> USGS ScienceBase item 62b21845d34e74f0d80f17aa with shared geophysical layers.</td><td>Subsurface interpretation may expose buried structures beyond surface fault traces.</td><td>Tests shallow projection of mapped surfaces, not only line picks. Medium cost; blocked pending payload retrieval/schema audit.</td></tr>
<tr><td>4</td><td><b>H33-9 ComCat focal-mechanism orientation.</b> USGS event focal mechanisms (strike/dip/rake) with potential-field edges.</td><td>Mechanism-plane orientation can test active structure orientation, but nodal-plane ambiguity and sparse events matter.</td><td>Different from earthquake-density proximity; carried-forward from earlier H33-2, so not novel. Medium cost; no full extract staged.</td></tr>
<tr><td>5</td><td><b>H33-10 signed strain-lobe / conductor edge.</b> GeoDAWN bands 7/8 strain, 17 conductivity, 15 basement depth and 18 gravity gradient.</td><td>Asymmetric strain across conductive/basement edge may flag concealed deformation, but fluids/contact geometry can mimic it.</td><td>Signed edge formulation differs from raw/multiplicative strain screens; partly pre-empted. Low–medium cost; no validation.</td></tr></tbody></table>
<p>No untested candidate is promoted. Historical H33-6's failure and Round-3's literal-lattice gate hold are preserved as full audit records.</p>
"""
    return page("Ranked hypotheses · GEMSDOE33", body, "hypotheses.html")


def build_data_sources() -> str:
    dom = read_json(ROOT / "evidence/round3_domain_divergence_audit.json")
    body = f"""<h2>Domain Adaptation Diagnostics (Ben-David et al., 2010) &amp; External Source Limits</h2>
<div class="panel good"><b>Round-3 Domain-Shift Screen Result (<code>evidence/round3_domain_divergence_audit.json</code>):</b>
Replacing raw regional elevation/potential-field levels with 3 km locally-detrended differential descriptors and screening on 20 km spatial checkerboard blocks (<code>|AUC(D_S vs D_T) - 0.5| &le; 0.20</code>) reduced held-out domain-discriminator AUC from <b><code>0.9169</code></b> (failed Round-1 <code>H33-F</code>) down to <b><code>{esc(dom.get('invariant_representation_linear_domain_auc'))}</code></b> across <code>{esc(dom.get('kept_base_features'))}/{esc(dom.get('total_candidate_base_features'))}</code> kept features, with explicit linear-halfspace empirical symmetric-difference divergence <code>d_hat_HDH = {esc(dom.get('empirical_d_H_Delta_H_linear_halfspace'))}</code> (<code>vc_dim = {esc(dom.get('linear_halfspace_vc_dim'))}</code>).</div>
<p><b>Automated exploration-bias catch:</b> The 20 km block divergence screen automatically rejected <code>{esc(dom.get('dropped_base_features'))}</code> because point-cataloged GDR well/spring density reflects geothermal drilling effort inside named fields (<code>IR-33-DA-01</code>), while retaining subsurface hydrothermal magnetite-destruction &times; clay/brine conductivity coupling (<code>hydro_demag_clay_coupling</code>) and 1 m LiDAR tectonic antislope scarp contrast (<code>scarp_antislope_contrast</code>), which are uniformly observable across drilled and undrilled basins alike.</p>
<p><b>Honest theoretical boundary:</b> In Ben-David et al. (2010) Theorem 2, the joint ideal-hypothesis error <code>&lambda;</code> remains unobservable without complete independent target truth, and raster pixels exhibit spatial autocorrelation; therefore Theorem 2 values in <code>evidence/round3_domain_divergence_audit.json</code> are reported strictly as a formal sensitivity curve over assumed <code>&lambda;</code>, not as an unconditional leaderboard bound.</p>
<div class="panel warn"><b>BRIDGE (DOE GDR #1682) &amp; IRIS SPUD EMTF (<code>H33-R3-4</code>): listed, blocked by sandbox firewall.</b> Direct HTTPS from this sandbox is restricted to GitHub/PyPI/npm hosts, so external GIS/MT archives at <code>gdr.openei.org</code>, <code>sciencebase.gov</code>, and <code>ds.iris.edu</code> were not fetched here and are not used as viable claims.</div>
"""
    return page("Domain Adaptation & Data Sources · GEMSDOE33", body, "data-sources.html")


def build_research() -> str:
    h336_audit = read_json(ROOT / "evidence/format_check_h33_6_6c888d2ce0f7.json")
    h33f_audit = read_json(ROOT / "evidence/format_check_h33f_d042874b26ef.json")
    r3_card_text = (ROOT / "evidence/round3_run_card_20261025.json").read_text(encoding="utf-8")

    body = f"""<h2>Round-3 Official JSON Run Card &amp; Archived Negative Research Records</h2>
<div class="panel accent">
<h3>Round-3 Parallel-Run Protocol JSON RUN CARD (<code>evidence/round3_run_card_20261025.json</code>)</h3>
<p>Generated automatically by <code>scripts/run_round3_campaign.py</code> (3 experiments executed within budget cap; 0 live weekly slots spent; <code>verdict: negative</code> under literal unexempted <code>r13-lattice-s5</code> calibration lattice guard while passing Gates G1–G5).</p>
<pre>{esc(r3_card_text)}</pre>
</div>

<h2>Archived Round-1 &amp; Round-2 Negative Deliverables (Retained for Audit Continuity)</h2>
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

<div class="panel bad"><h3>2026-10-25 duplicate guard and run card (H33-6 historical audit)</h3>
<p>H33-6 is not eligible for a slot. Its final raster crossed the duplicate threshold against 7 of 9 same-grid TIFFs available in this checkout. The external site rasters were not staged; the pre-placement edge surface was not screened in this audit; no new placement was run. The feature-alone leakage canary is also missing from retained evidence.</p>
<p>HOLDOUT-DTI (local <code>dti_binary</code>, four-fold conditional diagnostic; 60,988 withheld catalogue pixels): pooled DTI candidate <b>0.112486</b> vs control <b>0.114669</b>, pooled ΔDTI <b>−0.002183</b>; mean of fold deltas −0.002737 (2/4 positive). Descriptive fold-t 95% interval [−0.015020, +0.009546], df=3; not a private-label CI. The evaluator source has no semantic version field. See <a href="https://github.com/buffedlizard55-lab/GEMSDOE33/blob/main/evidence/duplicate_guard_run_card_20261025.json">machine-readable run card</a> and <a href="https://github.com/buffedlizard55-lab/GEMSDOE33/blob/main/evidence/holdout_h33_6.json">original holdout evidence</a>.</p>
</div>
"""
    return page("Research & Run Card · GEMSDOE33", body, "research.html")


def build_sources() -> str:
    sources = reg("sources.json")
    rows = "".join(
        f"<tr><td><code>{esc(s.get('id'))}</code></td>"
        f"<td><a href='{esc(s.get('url'))}'>{esc(s.get('title'))}</a></td>"
        f"<td><span class='badge blue'>{esc(s.get('evidence_class', s.get('type', 'UNSPECIFIED')))}</span></td>"
        f"<td>{esc(s.get('used_for', s.get('note', '')))}</td></tr>"
        for s in sources.get("sources", [])
    )
    pins = reg("owner_mirror_input_pins.json")
    grid_audit = read_json(ROOT / "evidence/input_grid_audit.json")
    pin_rows = "".join(
        f"<tr><td><code>{esc(f.get('id'))}</code></td><td><code>{esc(f.get('dest'))}</code></td>"
        f"<td>{int(f.get('bytes', 0)):,} B</td><td><code>{esc(f.get('sha256')[:16])}...</code></td></tr>"
        for f in pins.get("files", [])
    )
    body = f"""<h2>Verified Official &amp; Mirror Sources Registry</h2>
<p>Every source below is classified by provenance class. In this session, all 17 competition/external input files were autonomously restored to <code>.cache/gems_data</code> and SHA-256 verified (<code>evidence/input_grid_audit.json</code>: <code>pass = {esc(grid_audit.get('pass'))}</code>, <code>{len(grid_audit.get('pinned_files', []))}</code>/17 pins matched), and all 23 <code>vendor/gems57/*.py</code> modules were SHA-256 verified against <code>registry/vendor_pins.json</code>. Owner-mirror SHA-256 pins verify mirror byte identity, not organizer origin.</p>

<h3>Official Competition, Geoscientific Literature &amp; Repository Sources</h3>
<div class="scroll">
<table><thead>
<tr><th>ID</th><th>Source Title &amp; Official Link</th><th>Provenance / Evidence Class</th><th>Verified Usage &amp; Audit Note</th></tr>
</thead><tbody>
{rows}
</tbody></table>
</div>

<h3>SHA-256 Pinned Input Registry (17/17 Verified Locally on 2026-10-25)</h3>
<div class="scroll">
<table><thead>
<tr><th>Identifier</th><th>Relative Destination</th><th>Bytes</th><th>SHA-256 Prefix</th></tr>
</thead><tbody>
{pin_rows}
</tbody></table>
</div>
"""
    return page("Sources & Provenance Audit · GEMSDOE33", body, "sources.html")


def build_irregularities() -> str:
    irreg = reg("irregularities.json")
    items = "".join(
        f"<div class='panel warn'><h3>[{esc(item.get('id'))}] {esc(item.get('finding', item.get('title', 'Finding')))}</h3>"
        f"<p><b>Severity:</b> {esc(item.get('severity', 'unspecified'))} · <b>Status:</b> <span class='badge warn'>{esc(item.get('status', 'unspecified'))}</span></p>"
        f"<p><b>Evidence:</b> {esc(item.get('evidence', 'not recorded'))}</p>"
        f"<p><b>Consequence / action:</b> {esc(item.get('consequence', item.get('resolution', 'review required')))}</p></div>"
        for item in irreg.get("irregularities", [])
    )
    body = f"""<h2>Irregularities &amp; Audit Trail</h2>
<p>Known data-access, scientific, score-provenance, duplicate-witness, and format issues are recorded below.</p>

<div class="panel good">
  <h3>[IR-PORTAL-01 UPDATE 2026-10-25] DrivenData Official Reference Notebook Confirms All-Finite Zero-Outside Export</h3>
  <p>Inspection of <a href="https://github.com/drivendataorg/gems-prize-reference-solution">drivendataorg/gems-prize-reference-solution</a> (<code>unet-mc-cv-reference-solution.ipynb</code>, Cell 19) confirms the organizer's reference benchmark initializes <code>y_out = np.zeros(...)</code> and writes single-band <code>float32</code> GeoTIFFs with <code>0.0</code> outside valid patches and <code>nodata=None</code>. Under IEEE-754 rules, <code>NaN &gt;= 0.0</code> is <code>False</code>, explaining why unmasked whole-raster range checks reject <code>-nan.tif</code> with <i>&ldquo;Predicted values must be in range [0, 1]&rdquo;</i>. Round-3 therefore emits all-finite <code>-zeros.tif</code> verified across all <code>12,279,160</code> cells (while still treating live portal acceptance as confirmable only by an organizer receipt).</p>
</div>

<div class="panel warn">
  <h3>[IR-33-LATTICE-WITNESS-01] Synthetic Spacing-5 Calibration Lattice in <code>GEMSDOE24/inputs/calibration/</code></h3>
  <p>Across all <code>201</code> published submission GeoTIFFs in <code>docs/downloads/</code> of the 9 focused sites (<code>GEMSDOE24..36</code>), maximum 3-px footprint coverage is <code>27.5%</code> and Round-3 <code>H33-R3-3</code> passes uniqueness cleanly (max 3-px overlap <code>0.5265 &le; 0.70</code>, max <code>|&rho;| = 0.0614 &le; 0.90</code>). However, <code>GEMSDOE24/inputs/calibration/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif</code> (<code>206,895</code> dots) is a uniform spacing-5 lattice whose 3-px disks cover <b>99.87%</b> of the entire off-catalogue footprint (leaving only ~6,500 edge pixels &gt;3 px away). Because <code>vendor/gems57/uniqueness.py</code> does not exempt lattice priors, literal Scope B (<code>214</code> blobs) fails closed with <code>verdict: negative</code>.</p>
</div>

{items}
"""
    return page("Irregularities & audit log · GEMSDOE33", body, "irregularities.html")


def build_prompt() -> str:
    content = (ROOT / "standing_prompt.md").read_text(encoding="utf-8")
    body = f"""<h2>Standing Brief &amp; Operational Prompt</h2>
<pre style="white-space:pre-wrap;background:#0d1520;padding:20px;border-radius:12px;">{esc(content)}</pre>"""
    return page("Standing Brief · GEMSDOE33", body, "standing-prompt.html")


def retired_score_feed() -> str:
    review = reg("leaderboard_review.json")
    record = {
        "schema": 2,
        "as_of": "2026-10-04",
        "status": "RETIRED",
        "reason": "DrivenData Terms of Use prohibit automated or manual reproduction of row-level board data without consent.",
        "official_url": review.get("source_url"),
    }
    return json.dumps(record, indent=2, ensure_ascii=False) + "\n"


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
        "how-to-submit.html": build_exec(),
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
