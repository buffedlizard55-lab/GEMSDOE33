#!/usr/bin/env bash
# Restore the candidate-ready, hash-pinned public mirrors, then verify the core grid.
# NEVER contacts DrivenData. Run on any machine with GitHub API access.
set -euo pipefail
cd "$(dirname "$0")/.."
export GEMS_DATA_DIR="${GEMS_DATA_DIR:-$PWD/.cache/gemsdata}"
PY="${PYTHON:-$( [ -x .venv/bin/python ] && echo .venv/bin/python || echo python3 )}"

# Avoid silently fetching the optional 408 MB unpinned research archive on the
# ordinary path. Pass explicit restore_data.py arguments (e.g. --group core)
# to override the candidate-ready default.
if [[ "$#" -eq 0 ]]; then
  set -- --group candidate
fi
"$PY" scripts/restore_data.py --data-dir "$GEMS_DATA_DIR" "$@"
"$PY" scripts/prepare_data.py
