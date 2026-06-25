from __future__ import annotations

import json
import shutil
from pathlib import Path

from .cli_resolve import cli_command_string


def _read_template(brain_path: Path, agent_id: str, name: str) -> str | None:
    for platform in (agent_id, "_template"):
        path = brain_path / "adapters" / platform / name
        if path.exists():
            return path.read_text(encoding="utf-8")
    return None


def _install_hook_scripts(brain_path: Path, project_root: Path, agent_id: str) -> list[str]:
    """Скопировать hook-скрипты в .cursor/hooks/ и сделать исполняемыми."""
    hooks_dir = project_root / ".cursor" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    created: list[str] = []
    for platform in (agent_id, "_template"):
        src_dir = brain_path / "adapters" / platform
        if not src_dir.is_dir():
            continue
        for src in src_dir.glob("akash-*.py"):
            dest = hooks_dir / src.name
            shutil.copy2(src, dest)
            dest.chmod(0o755)
            created.append(str(dest))
    return created


def install_cursor_shell(*, brain_path: Path, project_root: Path, agent_id: str = "cursor") -> list[str]:
    """
    Собрать оболочку Cursor: rule + hooks (sessionStart, preToolUse gate, stop).
    """
    created: list[str] = []
    rules_dir = project_root / ".cursor" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)

    inject = _read_template(brain_path, agent_id, "inject.md")
    if inject:
        rule_path = rules_dir / "akasha-lifecycle.mdc"
        rule_path.write_text(inject, encoding="utf-8")
        created.append(str(rule_path))

    hook_scripts = _install_hook_scripts(brain_path, project_root, agent_id)
    created.extend(hook_scripts)

    session_hook = project_root / ".cursor" / "hooks" / "akash-session-start.py"
    gate_hook = project_root / ".cursor" / "hooks" / "akash-prepare-gate.py"

    hooks_path = project_root / ".cursor" / "hooks.json"
    hooks: dict = {
        "version": 1,
        "hooks": {
            "sessionStart": [
                {"command": cli_command_string("pull")},
            ],
            "stop": [{"command": cli_command_string("sync")}],
        },
    }

    if session_hook.is_file():
        hooks["hooks"]["sessionStart"] = [{"command": str(session_hook)}]
    if gate_hook.is_file():
        hooks["hooks"]["preToolUse"] = [
            {
                "command": str(gate_hook),
                "matcher": "Read|Write|Grep|Shell|StrReplace|Delete|EditNotebook|Task",
            }
        ]

    hooks_path.write_text(json.dumps(hooks, indent=2) + "\n", encoding="utf-8")
    created.append(str(hooks_path))
    return created


def detect_project_root(start: Path | None = None) -> Path:
    start = start or Path.cwd()
    return start.resolve()
