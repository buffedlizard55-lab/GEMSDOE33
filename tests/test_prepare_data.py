"""Data preparation must fail clearly on the retired generic OOF detector path."""

import pytest

from scripts.prepare_data import stage_oof


def test_legacy_oof_detector_fails_closed_instead_of_attribute_error():
    with pytest.raises(SystemExit, match="No generic quadrant-OOF detector is implemented"):
        stage_oof()
