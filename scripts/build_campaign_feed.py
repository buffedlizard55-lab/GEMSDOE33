#!/usr/bin/env python3
"""Render the public campaign-score feed from the committed score ledger.

The script performs no network requests. The dated official leaderboard
snapshot and owner-reported historical campaign submissions are kept in
registry/score_ledger.json; the live official leaderboard link is always
shown so visitors can see changes after the snapshot date. GitHub Pages runs
this renderer at deploy time, and local/CI checks can use ``--check``.
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "registry" / "score_ledger.json"
RESULTS_HTML = ROOT / "docs" / "results.html"
FEED_JSON = ROOT / "docs" / "score-feed.json"
START = "<!-- BEGIN GENERATED CAMPAIGN SCORE FEED -->"
END = "<!-- END GENERATED CAMPAIGN SCORE FEED -->"


def load_ledger() -> dict[str, Any]:
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    rows = ledger.get("submissions")
    if not isinstance(rows, list):
        raise ValueError("score ledger must contain a submissions array")
    seen: set[tuple[str, str]] = set()
    for row in rows:
        if not isinstance(row, dict) or not row.get("site") or not row.get("name"):
            raise ValueError("every submission needs a non-empty site and name")
        key = (str(row["site"]), str(row["name"]))
        if key in seen:
            raise ValueError(f"duplicate submission row: {key[0]} / {key[1]}")
        seen.add(key)
        score = row.get("score")
        if score is not None and (not isinstance(score, (int, float)) or not 0 <= score <= 1):
            raise ValueError(f"score outside [0, 1] for {key[0]} / {key[1]}")
    snapshot = ledger.get("leaderboard_snapshot")
    if not isinstance(snapshot, dict) or not snapshot.get("checked_on_local"):
        raise ValueError("official leaderboard snapshot needs checked_on_local")
    snapshot_rows = snapshot.get("rows")
    if not isinstance(snapshot_rows, list) or not snapshot_rows:
        raise ValueError("official leaderboard snapshot needs at least one row")
    for row in snapshot_rows:
        if not isinstance(row, dict) or not 0 <= float(row.get("score", -1)) <= 1:
            raise ValueError("leaderboard snapshot contains an invalid score")
    return ledger


def _e(value: Any) -> str:
    return html.escape(str(value), quote=True)


def make_feed(ledger: dict[str, Any]) -> dict[str, Any]:
    site_urls = ledger.get("campaign_sites", {})
    rows = []
    for source_row in ledger["submissions"]:
        row = dict(source_row)
        row["source_url"] = site_urls.get(row["site"])
        row["status"] = "owner-reported" if row.get("score") is not None else "unscored / no score reported"
        rows.append(row)
    return {
        "schema_version": 1,
        "ledger_updated_utc": ledger.get("updated_utc"),
        "policy": (
            "Historical campaign scores are owner-reported unless an organizer receipt is linked. "
            "The leaderboard rows are a dated snapshot; this project does not scrape or poll DrivenData."
        ),
        "official_leaderboard_snapshot": ledger["leaderboard_snapshot"],
        "campaign_submissions": rows,
    }


def render_block(feed: dict[str, Any]) -> str:
    snapshot = feed["official_leaderboard_snapshot"]
    checked = _e(snapshot["checked_on_local"])
    source_url = _e(snapshot["source_url"])
    top_rows = snapshot["rows"]
    best = top_rows[0]
    top_table = "\n".join(
        "<tr><td>{}</td><td>{}</td><td><b>{:.4f}</b></td><td>{}</td></tr>".format(
            int(row["rank"]), _e(row["participant"]), float(row["score"]),
            _e(row.get("submissions", "—")),
        )
        for row in top_rows
    )

    rows = []
    for row in feed["campaign_submissions"]:
        site = _e(row["site"])
        source = row.get("source_url")
        site_cell = f'<a href="{_e(source)}" rel="noopener">{site}</a>' if source else site
        score = row.get("score")
        score_text = f"{float(score):.4f}" if score is not None else "—"
        status = "owner-reported" if score is not None else "unscored"
        note = row.get("note", "")
        search = " ".join(str(row.get(key, "")) for key in ("site", "name", "note"))
        rows.append(
            f'<tr data-search="{_e(search).lower()}">'
            f"<td>{site_cell}</td><td>{_e(row['name'])}</td>"
            f"<td>{_e(score_text)}</td><td>{status}</td><td>{_e(note)}</td></tr>"
        )

    return f'''{START}
<h2>Official public leaderboard snapshot — checked {checked}</h2>
<div class="card">
  <p>At the time checked, the public leader was <b>{_e(best['participant'])}: {float(best['score']):.4f}</b>.
  This is a dated snapshot, not an automatically polled value. Open the
  <a href="{source_url}" rel="noopener">official live leaderboard</a> for the current ranking.</p>
  <table>
    <thead><tr><th>Rank</th><th>Participant</th><th>Public score</th><th>Submissions shown</th></tr></thead>
    <tbody>{top_table}</tbody>
  </table>
  <p class="mut">Snapshot date: {checked} (America/Los_Angeles). This project does not scrape or poll DrivenData.
  The reported 0.3195 for DARD is now rank 3 in this snapshot, not the current top score.</p>
</div>

<h2>Campaign submission feed <span class="pill">owner-reported history</span></h2>
<div class="card">
  <p>Historical results below were provided in the project brief and copied into
  <code>registry/score_ledger.json</code>. They are not independently verified organizer receipts.
  The feed is regenerated from that ledger on each GitHub Pages deployment; no external polling occurs.
  Machine-readable copy: <a href="score-feed.json">score-feed.json</a>.</p>
  <label for="score-filter">Filter submissions</label>
  <input id="score-filter" type="search" placeholder="Search site, submission, or note" aria-label="Filter campaign submissions">
  <div class="table-scroll"><table id="campaign-results">
    <thead><tr><th>Campaign site</th><th>Submission</th><th>Score</th><th>Status</th><th>Note</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table></div>
  <p class="mut">No score is inferred for blank/unscored entries. A dash means the brief supplied no score.</p>
</div>
<script>
(() => {{
  const input = document.getElementById('score-filter');
  const table = document.getElementById('campaign-results');
  if (!input || !table) return;
  input.addEventListener('input', () => {{
    const query = input.value.trim().toLowerCase();
    for (const row of table.tBodies[0].rows) {{
      row.hidden = !row.dataset.search.includes(query);
    }}
  }});
}})();
</script>
{END}'''


def replace_block(document: str, replacement: str) -> str:
    start = document.find(START)
    end = document.find(END)
    if start < 0 or end < 0 or end < start:
        raise ValueError(f"{RESULTS_HTML} must contain the generated-feed markers")
    end += len(END)
    return document[:start] + replacement + document[end:]


def build(check: bool = False) -> bool:
    ledger = load_ledger()
    feed = make_feed(ledger)
    expected_json = json.dumps(feed, indent=2, ensure_ascii=False) + "\n"
    existing_html = RESULTS_HTML.read_text(encoding="utf-8")
    expected_html = replace_block(existing_html, render_block(feed))

    if check:
        mismatches = []
        if RESULTS_HTML.read_text(encoding="utf-8") != expected_html:
            mismatches.append(str(RESULTS_HTML.relative_to(ROOT)))
        if not FEED_JSON.exists() or FEED_JSON.read_text(encoding="utf-8") != expected_json:
            mismatches.append(str(FEED_JSON.relative_to(ROOT)))
        if mismatches:
            print("Stale generated campaign feed: " + ", ".join(mismatches), file=sys.stderr)
            return False
        print("Campaign score feed is current.")
        return True

    RESULTS_HTML.write_text(expected_html, encoding="utf-8")
    FEED_JSON.write_text(expected_json, encoding="utf-8")
    print(f"Rendered {len(feed['campaign_submissions'])} campaign rows to docs/results.html and docs/score-feed.json")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if generated files are stale")
    args = parser.parse_args()
    return 0 if build(check=args.check) else 1


if __name__ == "__main__":
    raise SystemExit(main())
