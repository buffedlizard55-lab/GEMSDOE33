"""Retired unsupported candidate runners must fail closed without writing outputs."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_h33d_builder_is_disabled():
    result = subprocess.run(
        [sys.executable, "scripts/build_unique_submission.py"],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert result.returncode != 0
    assert "retired and disabled" in result.stderr
    assert "No TIFF was written" in result.stderr


def test_domain_adaptation_runner_is_disabled():
    result = subprocess.run(
        [sys.executable, "scripts/run_domain_adaptation.py"],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert result.returncode != 0
    assert "not a valid HΔH bound" in result.stderr
    assert "no independent analog labels" in result.stderr
