#!/usr/bin/env bash
# Local deterministic checks; no network calls, DrivenData access, or data restoration.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python3}"

"$PY" scripts/build_site.py
"$PY" -m pytest -q
"$PY" -m compileall -q src scripts tests

git diff --check
printf 'Checks passed. Input pin audit requires the optional local data/ files; run scripts/audit_inputs.py when available.\n'
