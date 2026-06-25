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
    from akash_core.harvest import _expand_glob, _iter_harvest_files

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
