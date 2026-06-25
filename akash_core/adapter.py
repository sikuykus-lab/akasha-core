from __future__ import annotations

import json
import re
from pathlib import Path

from .cli_resolve import cli_command_string


def _read_template(brain_path: Path, agent_id: str, name: str) -> str | None:
    for platform in (agent_id, "_template"):
        path = brain_path / "adapters" / platform / name
        if path.exists():
            return path.read_text(encoding="utf-8")
    return None


def install_cursor_shell(*, brain_path: Path, project_root: Path, agent_id: str = "cursor") -> list[str]:
    """
    Собрать оболочку Cursor: rule + hooks с CLI без зависимости от PATH.
    """
    created: list[str] = []
    rules_dir = project_root / ".cursor" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)

    inject = _read_template(brain_path, agent_id, "inject.md")
    if inject:
        rule_path = rules_dir / "akasha-lifecycle.mdc"
        rule_path.write_text(inject, encoding="utf-8")
        created.append(str(rule_path))

    hooks_path = project_root / ".cursor" / "hooks.json"
    hooks = {
        "version": 1,
        "hooks": {
            "sessionStart": [{"command": cli_command_string("pull")}],
            "stop": [{"command": cli_command_string("sync")}],
        },
    }
    hooks_path.write_text(json.dumps(hooks, indent=2) + "\n", encoding="utf-8")
    created.append(str(hooks_path))
    return created


def detect_project_root(start: Path | None = None) -> Path:
    start = start or Path.cwd()
    return start.resolve()
