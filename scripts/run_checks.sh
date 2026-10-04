#!/usr/bin/env bash
# Fast local verification. Downloads only the small public sample grid template;
# checks the static ledger and local artifacts; never contacts DrivenData or restores the feature stack.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-$( [ -x .venv/bin/python ] && echo .venv/bin/python || echo python3 )}"
export GEMS_DATA_DIR="${GEMS_DATA_DIR:-$PWD/.cache/gemsdata}"

"$PY" scripts/restore_data.py --data-dir "$GEMS_DATA_DIR" --only sample_submission
PYTHONPATH=src "$PY" tests/test_metric.py
PYTHONPATH=src "$PY" -m unittest discover -s tests -p 'test_*.py' -v
"$PY" scripts/build_campaign_feed.py --check
"$PY" scripts/validate_submission.py --submission docs/downloads/gems33-c0-scored-reference-20261004-89bf5b9a2fea.tif --template "$GEMS_DATA_DIR/core/sample_submission.tif" --out evidence/format_check_c0_89bf5b9a2fea.json
"$PY" scripts/validate_submission.py --submission docs/downloads/gems33-c2-stepover-relay-20261004-01f660dd8656.tif --template "$GEMS_DATA_DIR/core/sample_submission.tif" --out evidence/format_check_c2_01f660dd8656.json
"$PY" -m compileall -q src scripts tests
