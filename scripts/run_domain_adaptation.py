#!/usr/bin/env python3
"""Retired exploratory domain-transfer runner; intentionally disabled.

The previous implementation interpreted a domain-classifier AUC as a transfer
bound and emitted an unsupported positive verdict. Its result has been withdrawn.
See evidence/domain_adaptation_results.json, evidence/holdout_analog.json and
knowledge/07_analog_transfer.md for the corrected limitations. No Ben-David
HΔH bound is established. Do not rerun or treat archived output as validation.
"""


def main() -> int:
    raise SystemExit(
        "Domain-transfer runner retired: prior discriminator is not a valid HΔH bound; "
        "no independent analog labels or transfer pass is established."
    )


if __name__ == "__main__":
    main()
