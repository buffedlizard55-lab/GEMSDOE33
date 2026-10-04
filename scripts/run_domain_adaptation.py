#!/usr/bin/env python3
"""Fail-closed Ben-David transfer preflight; not an automatic divergence estimator.

The former version silently substituted geographic well/spring-record density for named field
labels, used a random pixel split, and called an arbitrary discriminator error a formal
HΔH-divergence. That result is withdrawn (IR-33-DA-01). This replacement writes an auditable
BLOCKED report and does not fit a classifier, assign a divergence, or license transfer.

A future implementation must be designed against the official Theorem 2 assumptions before it is
run. See ``src/gemsdoe33/domain.py`` and the official paper linked there.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build_report() -> dict:
    return {
        "schema": 2,
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "BLOCKED_NOT_ESTIMATED",
        "source_candidate": "BRIDGE GDR submission 1682: Dixie Valley or Gabbs Valley LiDAR fault picks",
        "target_candidate": "DOE GEMS competition raster footprint; target-label completeness is not established",
        "reference": {
            "citation": "Ben-David, Blitzer, Crammer, Kulesza, Pereira & Vaughan (2010), A theory of learning from different domains, Machine Learning 79, 151-175.",
            "url": "https://link.springer.com/article/10.1007/s10994-009-5152-4",
            "theorem_2_form": "epsilon_T(h) <= epsilon_S(h) + 0.5*d_hat_HDeltaH(U_S,U_T) + finite-sample complexity + lambda",
            "required_terms": [
                "source error for the declared target hypothesis class",
                "empirical HΔH divergence estimated under an explicit shared class and sampling design",
                "finite-sample term with defensible effective sample size and class complexity",
                "lambda, the joint error of the best shared hypothesis"
            ]
        },
        "availability": {
            "official_gdr_page": "https://gdr.openei.org/submissions/1682",
            "official_page_and_license_checked": True,
            "archive_payload_staged_or_inspected": False,
            "direct_download_result": "TLS/HTTP 000 in this sandbox; no source vectors were used"
        },
        "blocking_gates": [
            "Obtain and inspect the official BRIDGE vector archive; verify coordinate reference system, field IDs, confidence/verification attributes, and license conditions.",
            "Define source and target as named, non-overlapping field polygons before examining target benchmark outcomes; do not substitute record-density quantiles.",
            "Declare identical target hypothesis class, label policy, feature schema, spatial resolution, mask, and physically interpretable covariate transformations in both fields.",
            "Use field/system-level spatial blocks for train, domain-discriminator validation, and evaluation; prevent neighboring pixels or duplicate site records crossing partitions.",
            "Specify how source risk, the HΔH class/divergence, effective independent sample size and confidence intervals will be estimated.",
            "Estimate or conservatively bound lambda with an independent shared-label audit; do not set lambda to zero by assumption.",
            "Obtain a target-relevant, spatially blocked holdout and compare transferred candidates at matched emission budget before any submission-slot decision."
        ],
        "decision": "No transfer is implemented, licensed, rejected, or slot-approved by this report."
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "evidence" / "domain_adaptation_preflight.json")
    args = parser.parse_args()
    report = build_report()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"{report['status']}: no classifier fit; report written to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
