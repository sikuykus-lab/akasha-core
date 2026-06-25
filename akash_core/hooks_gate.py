from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

CONFIG = Path.home() / ".akash" / "config.local"
SESSION = Path.home() / ".akash" / "session.json"
META = Path.home() / ".akash" / ".session_meta.json"


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

    ctx = f"""# AKASHA — протокол (рекомендуемый)

Brain: `{brain_url}`

## На задачу

1. `python3 -m akash_core.cli prepare "<задача>"` — lego-кубики из паутины
2. `read-skill` из pack, если подходят
3. Работа (можно с нуля); после успеха — skill в brain + `sync`

Инструменты **не блокируются** — prepare желателен, не gate.

**persona:** {_snippet('core/persona.md') or '(пусто)'}
**rapport:** {_snippet('core/rapport.md') or '(пусто)'}
"""
    return {"additional_context": ctx}


def prepare_gate(inp: dict) -> dict:
    """Мягкий режим: инструменты не блокируются."""
    return {"permission": "allow"}


def run_session_start_hook() -> None:
    inp = json.load(sys.stdin)
    print(json.dumps(session_start(inp), ensure_ascii=False))


def run_prepare_gate_hook() -> None:
    inp = json.load(sys.stdin)
    print(json.dumps(prepare_gate(inp), ensure_ascii=False))
