#!/usr/bin/env bash
# Local deterministic checks; no network calls, DrivenData access, or data restoration.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python3}"

"$PY" scripts/build_site.py
"$PY" -m pytest -q
DATA_DIR="${GEMS_DATA_DIR:-$PWD/data}"
if [ -f "$DATA_DIR/sample_submission.tif" ]; then
  GEMS_DATA_DIR="$DATA_DIR" "$PY" scripts/audit_inputs.py
  GEMS_DATA_DIR="$DATA_DIR" "$PY" scripts/audit_sample_template_values.py
  GEMS_DATA_DIR="$DATA_DIR" "$PY" scripts/select_submission.py
else
  printf 'Input pins/template audit skipped: restore the git-ignored owner-mirror inputs first.\n'
fi
"$PY" -m compileall -q src scripts tests

git diff --check
printf 'Checks passed. All applicable local checks completed.\n'
