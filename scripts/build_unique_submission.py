#!/usr/bin/env python3
"""Retired H33-D builder; intentionally disabled.

The earlier implementation asserted an unsupported 0.2725–0.2760 score projection,
claimed portal-range immunity, and represented an H33-D artifact as a competition
submission despite later negative/conditional evidence. Do not run or reuse it.
The candidate is not slot-cleared. See evidence/first_pass_disposition.json,
knowledge/06_three_pass_review.md, and the current README for the corrected status.
Use the current frozen experiment protocol and obtain an independent holdout/duplicate
screen before writing any new candidate artifact.
"""


def main() -> int:
    raise SystemExit(
        "H33-D submission builder retired and disabled: unsupported projection, "
        "unverified provenance and failed promotion evidence. No TIFF was written."
    )


if __name__ == "__main__":
    main()
