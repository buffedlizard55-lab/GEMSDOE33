#!/usr/bin/env python3
"""Build the static, evidence-led GitHub Pages site.

The public pages are generated from the download manifest, research registries and evidence files.
They intentionally make the D2.8 *reference* prominent while refusing to promote withdrawn
first-pass holdout, score-inversion or domain-transfer claims.
"""
from __future__ import annotations

import html
import json
import re
import time
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
.nav a{padding:6px 12px;border:1px solid var(--line);border-radius:999px;text-decoration:none;color:var(--fg)}
.nav a[aria-current=page]{border-color:var(--blue);color:var(--blue)}main{padding:22px 0 64px}
h2{font-size:1.45rem;margin:36px 0 12px;padding-bottom:8px;border-bottom:1px solid var(--line)}
h3{font-size:1.1rem;line-height:1.35}.panel{background:var(--panel);border:1px solid var(--line);
border-radius:var(--radius);padding:18px 20px;margin:16px 0}.panel.good{border-left:5px solid var(--green)}
.panel.warn{border-left:5px solid var(--amber)}.panel.bad{border-left:5px solid var(--red)}
.hero-download{background:linear-gradient(115deg,#173425,#142130 65%);border:1px solid #3e7850;
border-radius:18px;padding:22px;margin:18px 0}.hero-download h2{border:0;margin:0 0 8px;padding:0}
.btn{display:inline-block;margin:8px 9px 2px 0;padding:11px 16px;border-radius:9px;background:var(--green);
color:#09210f;text-decoration:none;font-weight:750}.btn.alt{background:var(--panel);color:var(--fg);
border:1px solid var(--line)}.badge{display:inline-block;padding:2px 9px;border-radius:999px;
border:1px solid var(--line);color:var(--dim);font-size:.78rem;white-space:nowrap}
.badge.good{color:var(--green);border-color:#397849}.badge.warn{color:var(--amber);border-color:#80632b}
.badge.bad{color:var(--red);border-color:#794545}code,pre{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}
code{background:#0a1017;border:1px solid var(--line);border-radius:5px;padding:2px 5px;overflow-wrap:anywhere}
pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#0a1017;border:1px solid var(--line);border-radius:9px;
padding:14px}table{width:100%;border-collapse:collapse;margin:14px 0;font-size:.93rem}
th,td{border:1px solid var(--line);padding:9px 10px;text-align:left;vertical-align:top}
th{background:#1b2634}ul,ol{padding-left:1.35rem}li{margin:.45rem 0}.muted,.small{color:var(--dim)}
.small{font-size:.86rem}.scroll{overflow-x:auto}footer{padding:18px 0 30px;border-top:1px solid var(--line);color:var(--dim);
font-size:.88rem}blockquote{margin:14px 0;padding:10px 15px;border-left:3px solid var(--blue);background:#111a25}
"""

NAV = [
    ("index.html", "Overview"),
    ("executive-summary.html", "How to submit"),
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
    built = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Auditable DOE GEMS fault-discovery research; the recommended download is a format-checked D2.8 reference, not a new model.">
<title>{esc(title)}</title><link rel="stylesheet" href="assets/site.css"></head>
<body><header><div class="wrap"><h1>GEMSDOE33 · DOE GEMS fault discovery</h1>
<p>DrivenData #306 · evidence-led research · as of 2026-10-04</p><nav class="nav" aria-label="Primary">{links}</nav></div></header>
<main class="wrap">{body}</main>
<footer><div class="wrap">Generated {built} by <code>scripts/build_site.py</code>. The featured TIFF is a
D2.8 reference emission, not a new model. No DrivenData upload was made from this workspace. Owner
mirror, measured, model-derived and official evidence are identified separately in the records.</div></footer>
</body></html>"""


def download_manifest() -> dict:
    return read_json(DOWNLOADS / "manifest.json")


def artifact_by_name(man: dict, filename: str | None):
    return next((a for a in man.get("artifacts", []) if a.get("file") == filename), None)


def validation_text(artifact: dict) -> str:
    v = artifact.get("validation", {})
    checks = v.get("checks", {})
    passed = sum(bool(x) for x in checks.values())
    total = len(checks) or v.get("n_checks", 0)
    return f"{passed}/{total} local file checks passed; portal acceptance not tested"


def download_card(man: dict, artifact: dict, recommended: bool) -> str:
    filename = artifact["file"]
    tag = '<span class="badge good">RECOMMENDED · NaN outside</span>' if recommended else \
          '<span class="badge warn">ALTERNATE · 0.0 outside</span>'
    note = man.get("note", "")
    name = man.get("name", "")
    warning = "" if recommended else f'<p class="small">{esc(man.get("alternate_warning", "Troubleshooting alternative."))}</p>'
    return f"""<section class="panel {'good' if recommended else ''}">
<h3>{tag} <code>{esc(filename)}</code></h3>
{warning}
<table><tbody>
<tr><th>File</th><td><a href="downloads/{esc(filename)}">{esc(filename)}</a> ·
<a href="downloads/{esc(artifact['zip'])}">single-member ZIP</a></td></tr>
<tr><th>Unique submission name</th><td><code>{esc(name)}</code></td></tr>
<tr><th>Outside footprint</th><td>{esc(artifact.get('outside'))}</td></tr>
<tr><th>Size / emitted pixels</th><td>{int(artifact.get('bytes', 0)):,} bytes ·
{int(man.get('emitted_pixels', 0)):,} non-zero in-footprint cells</td></tr>
<tr><th>SHA-256</th><td><code>{esc(artifact.get('sha256', ''))}</code></td></tr>
<tr><th>Local validation</th><td>{esc(validation_text(artifact))}</td></tr>
</tbody></table>
<p><b>Paste-ready note ({int(man.get('note_chars', 0))}/200 characters):</b></p><pre>{esc(note)}</pre>
</section>"""


def package_box() -> str:
    man = download_manifest()
    recommended = artifact_by_name(man, man.get("recommended"))
    alternate = artifact_by_name(man, man.get("alternate"))
    if not recommended:
        return '<div class="panel bad">No recommended artifact is recorded in the manifest.</div>'
    primary = download_card(man, recommended, True)
    alt = download_card(man, alternate, False) if alternate else ""
    return f"""<div class="hero-download" id="download"><h2>⬇ Download the format-checked reference TIFF</h2>
<p><b>D2.8 reference only.</b> This is not a new model and is not demonstrated to beat the official
leaderboard. Its reported 0.2600 association is owner-reported; exact score-to-file identity is not
confirmed. The top card is the recommended, NaN-outside file.</p>{primary}{alt}</div>"""


def build_index() -> str:
    review = reg("leaderboard_review.json")
    source_url = review.get(
        "source_url",
        "https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/",
    )
    body = f"""{package_box()}
<p class="small">Grid: single-band float32 · EPSG:32611 · 3730 × 3292 · 100 m · exact registered
owner-mirror template transform · in-footprint values in [0,1]. Recommended outside value is NaN. Hash and byte-level
checks are in <a href="downloads/manifest.json">the package manifest</a>.</p>
<p class="panel warn">Local checks are not organizer acceptance. No upload, portal response or
submission receipt exists in this workspace.</p>
<h2 id="leaderboard-review">Official leaderboard review — one-time, not a feed</h2>
<div class="panel warn"><p>The official public <a href="{esc(source_url)}">leaderboard page</a> was reviewed once on
2026-10-04 at the owner's request. At that observation, the brief's claim that <code>0.3195</code> was
the current highest score was not supported. No participant/rank/score rows are retained or republished
here after review of the site's <a href="https://www.drivendata.org/termsofuse/">Terms of Use</a>,
which prohibit automatic monitoring/copying and manual monitoring/copying without prior written consent.
This project does not poll or refresh the page; no permission for further review or reproduction is
recorded. A public row cannot establish which local TIFF or account produced a score.</p></div>
<div class="panel bad"><h3>H27-4 score attribution is not supported</h3>
<p>The owner's GEMSDOE28 page says <b>“NO GEMSDOE28 SCORE”</b> and labels artifacts unscored/research-only.
No organizer receipt or verified account/file record ties the brief's <code>0.2708</code> claim to
<code>h27-4-r1-solo-d2-8</code>. See <a href="irregularities.html">the provenance and score
irregularities</a>; detailed leaderboard rows are intentionally not reproduced.</p></div>
<h2>Decision status</h2>
<ul><li>No new candidate has passed a valid independent spatially blocked holdout against the current
best comparable emission.</li><li>Upstream C2 is archived as research-only: the earlier P1 pass was withdrawn; the corrected
conditional source-exclusion diagnostic is P1 mean ΔDTI −0.000722 (0/4 positive), P2 SGMC proxy
+0.000283, and not slot-cleared because H19-5 was not re-derived per fold and the diagnostic was not
an independent preregistered confirmation. See <a href="irregularities.html">IR-33-C2-01</a> and
<a href="https://github.com/buffedlizard55-lab/GEMSDOE33/blob/main/evidence/holdout33.json">the evidence</a>.</li>
<li>First-pass holdout, reconstruction, pruning and domain-transfer promotion claims were withdrawn after
review; archived results are preserved for audit but are not promotion evidence.</li><li>No weekly submission
slot is approved or spent. Only the D2.8 reference is packaged.</li></ul>
<p>For the exact upload procedure, open the <a href="executive-summary.html">executive summary</a>.
For the geological shortlist and blocked source checks, see <a href="research.html">research</a>.</p>"""
    return page("GEMSDOE33 · overview and reference TIFF", body, "index.html")


def build_exec() -> str:
    man = download_manifest()
    art = artifact_by_name(man, man.get("recommended"))
    if not art:
        return page("How to submit · GEMSDOE33", '<p>Download package unavailable.</p>', "executive-summary.html")
    fname = art["file"]
    note = man.get("note", "")
    body = f"""<h2>Executive summary — exact upload steps</h2>
<p>The competition problem page describes the GeoTIFF grid and submission format. Review the
<a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">official problem
page</a>, the <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/rules/">current rules page</a>,
and the <a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">user-provided rules PDF</a> before submitting.
The TIFF below is an owner-mirror D2.8 reference,
not a newly validated model. Its reported 0.2600 score has no organizer receipt linking it to these
exact file bytes.</p>
{package_box()}
<ol><li><b>Download the recommended NaN-outside TIFF</b> from the top card:
<code>{esc(fname)}</code>. Optionally verify its SHA-256 against the card. It is a single-band
float32 GeoTIFF, EPSG:32611, 3730 × 3292, 100 m, on the exact owner-mirror template grid. Values on the finite
footprint are within [0,1]; cells outside are NaN.</li>
<li><b>Open the <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/">DrivenData DOE GEMS #306 submission page</a></b> in your own authenticated browser session.
This workspace has no DrivenData login and cannot submit on your behalf.</li>
<li><b>Select the file</b> (or its single-member ZIP if the portal's TIFF parser reports an error).
Do not edit or resave the raster unless required; a GIS export could change its grid or dtype.</li>
<li><b>Enter the unique submission name</b> <code>{esc(man.get('name', ''))}</code> wherever the form
provides a submission name/title field. The TIFF filename itself also carries this unique identifier.</li>
<li><b>Paste the note</b> below into the optional note/comment field. It is {int(man.get('note_chars', 0))}
characters, under the 200-character limit.</li>
<li><b>Review the selected file and attribution, then submit.</b> Save the portal's receipt and score
if it provides one. No upload or score is asserted by this repository.</li></ol>
<div class="panel warn"><b>Note to paste ({int(man.get('note_chars', 0))}/200 characters):</b><pre>{esc(note)}</pre></div>
<h3>Why NaN outside is recommended</h3>
<p>The official problem wording says data outside the bounds should be null or NaN. The recommended
file follows that wording and passed all {len(art.get('validation', {}).get('checks', {}))} recorded
local byte/grid/value checks. The <code>-zeros.tif</code> alternative has 0.0 outside the footprint;
it is offered only as a troubleshooting option and is not as close to the literal null/NaN wording.
Neither local validation nor the ZIP container guarantees portal acceptance.</p>
<h3>Rebuild the local reference package</h3>
<pre>python scripts/restore_data.py --group all
python scripts/build_submission.py
python scripts/build_site.py
python -m pytest -q</pre>
<p class="small">Inputs are SHA-pinned owner mirrors, not organizer-authenticated downloads. See
<a href="{GITHUB}/data/README.md">data provenance notes</a> in the repository and the
<a href="downloads/manifest.json">package manifest</a>.</p>"""
    return page("How to submit · GEMSDOE33", body, "executive-summary.html")


def build_research() -> str:
    hyp = reg("hypotheses.json")
    rows = []
    for h in hyp.get("hypotheses", []):
        layers = "<ul>" + "".join(f"<li>{esc(layer)}</li>" for layer in h.get("layers", [])) + "</ul>"
        src_raw = h.get("specific_free_official_source", "")
        src = esc(src_raw)
        for url in re.findall(r"https?://[^\s;,]+", src_raw):
            safe_url = esc(url.rstrip(".,"))
            src = src.replace(esc(url), f'<a href="{safe_url}">{safe_url}</a>')
        check = esc(h.get("obtainability_check", ""))
        rows.append(f"""<tr><td>{int(h.get('rank', 0))} · <code>{esc(h.get('id', ''))}</code><br>
<b>{esc(h.get('title', ''))}</b><br><span class="badge warn">{esc(h.get('status', ''))}</span></td>
<td>{layers}</td><td>{esc(h.get('physical_signature', ''))}</td>
<td>{esc(h.get('why_it_targets_faults_absent_from_USGS_INGENIOUS', ''))}</td>
<td>{esc(h.get('difference_from_prior_art', ''))}</td>
<td>{esc(h.get('expected_DTI_improvement_rank', ''))}<br><b>Cost:</b> {esc(h.get('implementation_cost', ''))}</td>
<td>{src}<br><br><b>Availability check:</b> {check}</td></tr>""")
    htable = "".join(rows) or '<tr><td>No hypotheses registered.</td></tr>'
    da = read_json(ROOT / "evidence" / "domain_adaptation_preflight.json")
    blockers = da.get("blocking_gates", [])
    block_list = "<ol>" + "".join(f"<li>{esc(item)}</li>" for item in blockers) + "</ol>"
    status = esc(da.get("status", "BLOCKED_NOT_ESTIMATED"))
    current = esc(hyp.get("status", ""))
    body = f"""<h2>Research status</h2>
<div class="panel warn"><b>{current}</b><p>The hypothesis registry is retrospective: implementation began before
it was assembled, so none of these entries is claimed as preregistration. They are research leads,
not validated candidates or slot approvals. No new candidate has been demonstrated to beat the
current best.</p></div>
<h2>Ranked geological hypotheses</h2>
<div class="scroll"><table><thead><tr><th>Rank / status</th><th>Layers</th><th>Physical signature</th>
<th>Why it may find faults absent from USGS/INGENIOUS</th><th>Difference from prior art</th>
<th>Expected upside / cost</th><th>Official source and availability check</th></tr></thead>
<tbody>{htable}</tbody></table></div>
<h2>Ben-David domain adaptation — fail-closed</h2>
<div class="panel bad"><b>{status}</b><p>No source/target divergence was estimated and no transfer is licensed or refused.
The first-pass well/spring-density split, random pixel discriminator and its conclusion were withdrawn.
The official BRIDGE GIS archive payload could not be staged in this sandbox.</p>
<p>Ben-David et al. (2010), Theorem 2 requires source error plus one half of an empirical
<code>HΔH</code> divergence, a defensible finite-sample/class-complexity term, and the joint-label
error <code>lambda</code>. A generic two-sample AUC is not by itself that bound.
<a href="https://link.springer.com/article/10.1007/s10994-009-5152-4">Paper</a> ·
<a href="{GITHUB}/src/gemsdoe33/domain.py">implementation notes</a>.</p>
<h3>Blocking gates</h3>{block_list}</div>
<h2>Review and evidence boundary</h2>
<p>Initial promotion claims were withdrawn after discovering truth-conditioned prediction
reconstruction, tuning against owner-reported scores, reused seeds/budgets, a comparator structurally
biased against some artifact families, invalid domain definitions, and unverified arithmetic on
quantized radiometric bands. See <a href="{GITHUB}/evidence/first_pass_disposition.json">the disposition</a>
and <a href="irregularities.html">the irregularities register</a>. No archived score or metric is
used here to promote a candidate.</p>
<p>Upstream C2 is also <b>not slot-cleared</b>. Its legacy P1 pass was withdrawn; the corrected conditional
source-exclusion diagnostic is P1 mean ΔDTI <code>−0.000722</code> (0/4 folds positive), while P2 is
<code>+0.000283</code> on the separate SGMC proxy. Because the fixed H19-5 surface was not rebuilt per
fold and the correction was not an independent preregistered confirmation, these figures remain a
conditional local diagnostic—not score evidence. See <a href="{GITHUB}/evidence/holdout33.json">the
full diagnostic</a> and <a href="{GITHUB}/archive/legacy_candidates/README.md">the archive-only
artifact note</a>.</p>
<p>Source and licence observations are linked from the <a href="sources.html">source register</a>;
external file availability and footprint/schema checks remain explicitly incomplete where indicated.</p>"""
    return page("Research · GEMSDOE33", body, "research.html")


def build_sources() -> str:
    data = reg("sources.json")
    rows = "".join(
        f'<tr><td><code>{esc(item.get("id", ""))}</code><br>{esc(item.get("title", ""))}</td>'
        f'<td><a href="{esc(item.get("url", ""))}">{esc(item.get("url", ""))}</a></td>'
        f'<td>{esc(item.get("used_for", ""))}</td><td>{esc(item.get("evidence_class", ""))}</td></tr>'
        for item in data.get("sources", [])
    )
    body = f"""<h2>Source register</h2>
<p>Official and trusted source links for provenance checks. The competition input files restored in this
repository are owner-published mirrors; hashes do not authenticate organizer provenance. The rules
PDF is a user-provided link and was not re-downloaded on 2026-10-04. The leaderboard is not polled,
scraped, copied, or refreshed by this project; its Terms of Use require prior written consent for
manual monitoring/copying. The registry keeps only a dated status note, not leaderboard rows.</p>
<div class="scroll"><table><thead><tr><th>Source</th><th>Link</th><th>Use and observed facts</th><th>Evidence class</th></tr></thead>
<tbody>{rows}</tbody></table></div>
<p>Data hashes and provenance warnings: <a href="{GITHUB}/registry/owner_mirror_input_pins.json">17 audited input pins</a> ·
<a href="{GITHUB}/registry/data_manifest.json">upstream C0/C2 restore manifest</a> ·
<a href="{GITHUB}/data/README.md">data README</a>.</p>"""
    return page("Sources · GEMSDOE33", body, "sources.html")


def build_irregularities() -> str:
    data = reg("irregularities.json")
    rows = "".join(
        f'<tr><td><code>{esc(item.get("id", ""))}</code></td>'
        f'<td>{esc(item.get("severity", ""))}</td><td>{esc(item.get("status", ""))}</td>'
        f'<td>{esc(item.get("finding", ""))}<br><br><b>Evidence:</b> {esc(item.get("evidence", ""))}'
        f'<br><br><b>Consequence:</b> {esc(item.get("consequence", ""))}</td></tr>'
        for item in data.get("irregularities", [])
    )
    body = f"""<h2>Irregularities — record, do not conceal</h2>
<p>{esc(data.get('convention', ''))}</p><div class="scroll"><table><thead><tr>
<th>ID</th><th>Severity</th><th>Status</th><th>Finding, evidence and consequence</th></tr></thead>
<tbody>{rows}</tbody></table></div>"""
    return page("Irregularities · GEMSDOE33", body, "irregularities.html")


def build_prompt() -> str:
    prompt = ROOT / "standing_prompt.md"
    content = prompt.read_text(encoding="utf-8") if prompt.exists() else "Standing brief missing."
    body = f"<h2>Standing brief (full text)</h2><pre>{esc(content)}</pre>"
    return page("Standing brief · GEMSDOE33", body, "standing-prompt.html")


def legacy_redirect(title: str, target: str, note: str) -> str:
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="0; url={esc(target)}"><title>{esc(title)}</title></head>
<body><main><h1>{esc(title)}</h1><p>{esc(note)}</p>
<p>Continue to <a href="{esc(target)}">{esc(target)}</a>.</p></main></body></html>'''


def retired_score_feed() -> str:
    record = {
        "schema_version": 1,
        "status": "RETIRED_NO_LEADERBOARD_FEED",
        "policy": "This endpoint intentionally contains no participant, rank, or score rows. DrivenData Terms of Use prohibits automated monitoring/copying and manual monitoring/copying without prior written consent. This project does not poll or refresh the leaderboard.",
        "official_url": "https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/",
        "terms_url": "https://www.drivendata.org/termsofuse/",
        "review_record": "https://github.com/buffedlizard55-lab/GEMSDOE33/blob/main/registry/leaderboard_review.json",
    }
    return json.dumps(record, indent=2, ensure_ascii=False) + chr(10)


def main() -> int:
    (ASSETS / "site.css").write_text(CSS, encoding="utf-8")
    pages = {
        "index.html": build_index(),
        "executive-summary.html": build_exec(),
        "research.html": build_research(),
        "sources.html": build_sources(),
        "irregularities.html": build_irregularities(),
        "standing-prompt.html": build_prompt(),
        "how-to-submit.html": legacy_redirect("How to submit", "executive-summary.html", "This legacy page was replaced by the current executive summary."),
        "hypotheses.html": legacy_redirect("Hypotheses", "research.html", "This legacy page was replaced by the current research page."),
        "data-sources.html": legacy_redirect("Data sources", "sources.html", "This legacy page was replaced by the current source register."),
        "results.html": legacy_redirect("Results and leaderboard", "index.html#leaderboard-review", "This legacy results page and copied leaderboard feed have been retired."),
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
