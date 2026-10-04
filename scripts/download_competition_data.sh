#!/usr/bin/env bash
# Restore the candidate-ready, hash-pinned public mirrors, then verify the core grid.
# NEVER contacts DrivenData. Run on any machine with GitHub API access.
set -euo pipefail
cd "$(dirname "$0")/.."
export GEMS_DATA_DIR="${GEMS_DATA_DIR:-$PWD/.cache/gemsdata}"
PY="${PYTHON:-$( [ -x .venv/bin/python ] && echo .venv/bin/python || echo python3 )}"

# This legacy research helper uses the upstream C0/C2 manifest and its own
# .cache/gemsdata layout. It does not restore the current D2.8 reference pins,
# and never contacts DrivenData. Avoid silently fetching the optional unpinned
# 408 MB research archive on the ordinary path.
if [[ "$#" -eq 0 ]]; then
  set -- --group candidate
fi
"$PY" scripts/restore_candidate_data.py --data-dir "$GEMS_DATA_DIR" "$@"
"$PY" scripts/prepare_campaign_data.py
