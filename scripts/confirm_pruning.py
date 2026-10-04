#!/usr/bin/env python3
"""Retired first-pass confirmation runner.

The prior runner used a truth-conditioned pseudo-hidden reconstruction, radius tuning against
owner-reported scores, and reused exploratory seeds/budgets. It is archived and cannot be run as a
valid promotion test. See ``evidence/first_pass_disposition.json``. Do not spend a submission slot
on its archived results.
"""

raise SystemExit(
    "WITHDRAWN: invalid first-pass confirmation. See evidence/first_pass_disposition.json; "
    "the historical script is under archive/withdrawn_first_pass/scripts/confirm_pruning.py."
)
