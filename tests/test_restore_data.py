"""Restoration must verify before replacing and clean only its own scratch files."""
import hashlib

import pytest

from scripts import restore_data


def entry(payload=b"verified", **extra):
    return dict(id="fixture", dest="nested/input.tif", repo="owner/repo", ref="pinned",
                path="input.tif", sha256=hashlib.sha256(payload).hexdigest(),
                bytes=len(payload), **extra)


def test_failed_fetch_preserves_existing_file(tmp_path, monkeypatch):
    target = tmp_path / "nested/input.tif"
    target.parent.mkdir()
    target.write_bytes(b"previous-unverified")

    def fail(*args):
        raise RuntimeError("offline")

    monkeypatch.setattr(restore_data, "fetch_to", fail)
    with pytest.raises(RuntimeError, match="offline"):
        restore_data.restore(entry(), tmp_path)
    assert target.read_bytes() == b"previous-unverified"
    assert not target.with_name("input.tif.assembling").exists()


def test_mismatched_download_preserves_existing_file(tmp_path, monkeypatch):
    target = tmp_path / "nested/input.tif"
    target.parent.mkdir()
    target.write_bytes(b"previous-unverified")
    monkeypatch.setattr(restore_data, "fetch_to",
                        lambda repo, ref, remote, dest: dest.write_bytes(b"wrong"))
    with pytest.raises(ValueError, match="pin mismatch"):
        restore_data.restore(entry(), tmp_path)
    assert target.read_bytes() == b"previous-unverified"


def test_parts_verify_replace_and_preserve_unrelated_raw(tmp_path, monkeypatch):
    raw = tmp_path / "raw"
    raw.mkdir()
    unrelated = raw / "unrelated.part"
    unrelated.write_bytes(b"keep")
    monkeypatch.setattr(restore_data, "fetch_to",
                        lambda repo, ref, remote, dest: dest.write_bytes(remote.encode()))
    result = restore_data.restore(entry(b"ab", parts=["a", "b"]), tmp_path)
    assert result["status"] == "restored-and-verified"
    assert (tmp_path / "nested/input.tif").read_bytes() == b"ab"
    assert list(raw.iterdir()) == [unrelated]


def test_verified_input_does_not_fetch(tmp_path, monkeypatch):
    target = tmp_path / "nested/input.tif"
    target.parent.mkdir()
    target.write_bytes(b"verified")
    monkeypatch.setattr(restore_data, "fetch_to", lambda *args: pytest.fail("unexpected fetch"))
    assert restore_data.restore(entry(), tmp_path)["status"] == "already-verified"
