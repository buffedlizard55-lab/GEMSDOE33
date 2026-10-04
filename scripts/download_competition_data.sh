#!/usr/bin/env bash
# GEMSDOE33 data placement: restore hash-pinned public mirrors, then verify.
# NEVER contacts DrivenData. Run on any machine with GitHub API access.
set -euo pipefail
cd "$(dirname "$0")/.."
export GEMS_DATA_DIR="${GEMS_DATA_DIR:-$PWD/.cache/gemsdata}"
PY="${PYTHON:-$( [ -x .venv/bin/python ] && echo .venv/bin/python || echo python3 )}"
"$PY" scripts/restore_data.py --data-dir "$GEMS_DATA_DIR" "$@"
"$PY" scripts/prepare_data.py
