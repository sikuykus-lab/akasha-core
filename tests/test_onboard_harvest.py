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
