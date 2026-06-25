from pathlib import Path

from akash_core.project_harvest import discover_projects, synthesize_skill_md
from akash_core.skill_laws import validate_skill_md


def test_validate_skill_ok():
    md = """# test
tags: python

## Триггеры
- foo

## Шаги
1. Open file
2. Edit
"""
    r = validate_skill_md(md)
    assert r.ok


def test_validate_skill_too_big():
    body = "x" * 5000
    md = f"# big\n\n## Триггеры\n- a\n\n## Шаги\n1. a\n2. b\n\n{body}"
    r = validate_skill_md(md)
    assert not r.ok
    assert any("Law I" in v for v in r.violations)


def test_discover_projects_workspace():
    root = Path("/Users/user/Documents/Google Sheets")
    if not root.exists():
        return
    projects = discover_projects(root)
    names = {p.name for p in projects}
    assert "apps-script" in names or "streamlit-dashboard" in names


def test_synthesize_gas_skill(tmp_path):
    gas = tmp_path / "apps-script"
    gas.mkdir()
    script = gas / "Dispatch.gs"
    script.write_text("function sendMail() {}\nfunction onEdit() {}\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Test project\n", encoding="utf-8")
    projects = discover_projects(tmp_path)
    assert len(projects) == 1
    skill_id, content, tags = synthesize_skill_md(projects[0], script)
    assert "apps-script" in tags
    assert validate_skill_md(content).ok
    assert "sendMail" in content
