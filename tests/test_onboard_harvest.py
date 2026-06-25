from pathlib import Path

from akash_core.cli_resolve import cli_invocation
from akash_core.harvest import _classify, count_skills


def test_cli_invocation_no_path_needed():
    inv = cli_invocation()
    assert inv[0]
    assert inv[-1] == "akash_core.cli"
    assert inv[-2] == "-m"


def test_classify_soul():
    assert _classify(Path("/home/user/SOUL.md")) == "persona"


def test_count_skills_empty(tmp_path):
    (tmp_path / "skills" / "_drafts").mkdir(parents=True)
    assert count_skills(tmp_path) == 0


def test_expand_glob_absolute_path(tmp_path):
    from akash_core.harvest import _expand_glob

    f = tmp_path / "SOUL.md"
    f.write_text("soul", encoding="utf-8")
    assert _expand_glob(str(f), tmp_path) == [f.resolve()]
    assert _expand_glob(str(tmp_path / "missing.md"), tmp_path) == []


def test_iter_harvest_no_glob_crash(tmp_path):
    from akash_core.harvest import _iter_harvest_files

    brain = tmp_path / "brain"
    (brain / "adapters" / "cursor").mkdir(parents=True)
    (brain / "adapters" / "cursor" / "harvest-sources.yaml").write_text("globs: []\n")
    files = _iter_harvest_files(brain, "cursor", tmp_path)
    assert isinstance(files, list)


def test_is_binary_path(tmp_path):
    from akash_core.harvest import _is_binary_path, _read_text

    binary = tmp_path / "x.bin"
    binary.write_bytes(b"\x00\x01\x02")
    assert _is_binary_path(binary)
    assert _read_text(binary) is None

    text = tmp_path / "ok.md"
    text.write_text("hello", encoding="utf-8")
    assert not _is_binary_path(text)
    assert _read_text(text) == "hello"


def test_heal_brain_target_bad_utf8(tmp_path):
    from akash_core.harvest import _heal_brain_target, _read_text_lenient

    bad = tmp_path / "rapport.md"
    bad.write_bytes(b"\xbd\xd1\x8e.\n# Rapport\nok")
    assert _read_text_lenient(bad).startswith("\ufffd")
    _heal_brain_target(bad)
    healed = bad.read_text(encoding="utf-8")
    assert "# Rapport" in healed
    assert "\ufffd" not in healed
