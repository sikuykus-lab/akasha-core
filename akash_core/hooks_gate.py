from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

CONFIG = Path.home() / ".akash" / "config.local"
SESSION = Path.home() / ".akash" / "session.json"
META = Path.home() / ".akash" / ".session_meta.json"

WORK_TOOLS = frozenset(
    {"Read", "Write", "Grep", "Delete", "StrReplace", "EditNotebook", "Shell", "Task"}
)
AKASHA_CLI_MARKERS = ("akash_core.cli", " akash ", "pip install")


def pack_ready(session_path: Path = SESSION) -> bool:
    if not session_path.is_file():
        return False
    try:
        data = json.loads(session_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return bool(data.get("task")) and bool(data.get("skills"))


def session_start(inp: dict) -> dict:
    session_id = inp.get("session_id", "")
    META.write_text(json.dumps({"session_id": session_id}), encoding="utf-8")
    SESSION.unlink(missing_ok=True)

    if not CONFIG.is_file():
        return {}

    subprocess.run(
        [sys.executable, "-m", "akash_core.cli", "pull"],
        capture_output=True,
        text=True,
    )

    import yaml

    raw = yaml.safe_load(CONFIG.read_text(encoding="utf-8")) or {}
    brain_url = raw.get("brain_url") or ""
    parts = brain_url.rstrip("/").split("/")
    brain_path = (
        Path.home() / ".akash" / "github" / parts[-2] / parts[-1] if len(parts) >= 2 else None
    )

    def _snippet(rel: str, limit: int = 400) -> str:
        if not brain_path:
            return ""
        p = brain_path / rel
        if not p.is_file():
            return ""
        t = p.read_text(encoding="utf-8", errors="replace").strip()
        return t[:limit] + ("…" if len(t) > limit else "")

    ctx = f"""# AKASHA — обязательный протокол (always)

Brain: `{brain_url}`

## На КАЖДУЮ задачу пользователя

1. `python3 -m akash_core.cli prepare "<задача>"`
2. `read-skill` только из pack
3. Потом код и файлы

До prepare **запрещено** Read/Write/Grep/Shell по проекту (hook заблокирует).

**persona:** {_snippet('core/persona.md') or '(пусто)'}
**rapport:** {_snippet('core/rapport.md') or '(пусто)'}
"""
    return {"additional_context": ctx}


def prepare_gate(inp: dict) -> dict:
    if not CONFIG.is_file():
        return {"permission": "allow"}

    tool = inp.get("tool_name") or ""
    tool_input = inp.get("tool_input") or {}

    if tool == "Shell":
        cmd = str(tool_input.get("command") or "")
        if any(m in cmd for m in AKASHA_CLI_MARKERS):
            return {"permission": "allow"}

    if pack_ready():
        return {"permission": "allow"}

    if tool in WORK_TOOLS:
        return {
            "permission": "deny",
            "agent_message": (
                "AKASHA: выполни prepare по задаче пользователя, затем read-skill из pack. "
                "python3 -m akash_core.cli prepare \"<задача>\""
            ),
            "user_message": "Сначала паутина AKASHA (prepare).",
        }
    return {"permission": "allow"}


def run_session_start_hook() -> None:
    inp = json.load(sys.stdin)
    print(json.dumps(session_start(inp), ensure_ascii=False))


def run_prepare_gate_hook() -> None:
    inp = json.load(sys.stdin)
    print(json.dumps(prepare_gate(inp), ensure_ascii=False))
