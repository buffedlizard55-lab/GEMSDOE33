"""GEMSDOE33 — auditable fault-discovery research stack for the DOE GEMS Prize (DrivenData #306).

Evidence-class convention used throughout this repository.  Every quantitative claim in the
README, the site and ``evidence/*.json`` carries exactly one of:

``[OFFICIAL]``   read from a DrivenData / USGS / DOE page or product (link recorded).
``[MEASURED]``   computed in this checkout from SHA-256-pinned bytes on disk (command recorded).
``[OWNER-REPORT]`` the owner's own page or brief; no organiser receipt exists.
``[MODEL]``      an estimate conditioned on an unverified anchor.  Never presented as a result.
"""

__version__ = "1.0.0"
