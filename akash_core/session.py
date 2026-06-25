from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any


SESSION_FILE = Path.home() / ".akash" / "session.json"


@dataclass
class HotMemory:
    persona: str
    rapport: str
    actions: str


def load_hot_memory(brain_path: Path) -> HotMemory:
    """
    Загрузить три hot-файла (§6): persona, rapport, ACTIONS.
    """
    persona = (brain_path / "core" / "persona.md").read_text(encoding="utf-8") if (brain_path / "core" / "persona.md").exists() else ""
    rapport = (brain_path / "core" / "rapport.md").read_text(encoding="utf-8") if (brain_path / "core" / "rapport.md").exists() else ""
    actions = (brain_path / "memory" / "ACTIONS.md").read_text(encoding="utf-8") if (brain_path / "memory" / "ACTIONS.md").exists() else ""
    return HotMemory(persona=persona, rapport=rapport, actions=actions)


def compact_hot_memory(brain_path: Path) -> None:
    """
    Проверка и сжатие hot-файлов по лимитам §6 (простая реализация: обрезаем старые строки).
    """
    limits = {
        ("core", "persona.md"): 4 * 1024,
        ("core", "rapport.md"): 4 * 1024,
        ("memory", "ACTIONS.md"): 8 * 1024,
    }
    for (subdir, name), limit in limits.items():
        p = brain_path / subdir / name
        if not p.exists():
            continue
        content = p.read_text(encoding="utf-8")
        if len(content.encode("utf-8")) <= limit * 0.8:
            continue
        # Сжимаем: хвост по строкам, чтобы не резать UTF-8 посередине символа.
        lines = content.splitlines(keepends=True)
        while lines and len("".join(lines).encode("utf-8")) > limit:
            lines.pop(0)
        p.write_text("".join(lines), encoding="utf-8")


def cli_compact_check(brain_path: Path) -> None:
    """
    Утилитная команда `akash compact-check` (§11).
    """
    compact_hot_memory(brain_path)
    print("Hot memory compaction check executed.")


def cli_remember(fact: str) -> None:
    """
    Запись факта в буфер сессии (§4, §6, §14.3).
    """
    sessions_dir = Path.home() / ".akash" / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    # agent-id сюда может быть добавлен позже, сейчас пишем общий буфер.
    session_file = sessions_dir / f"session-{today}.jsonl"
    record: dict[str, Any] = {"fact": fact}
    with session_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def cli_record_outcome(skill_id: str, outcome: str, help_score: int) -> None:
    """
    `akash record-outcome` → state/usage.jsonl (§8).
    """
    # В реальной интеграции сюда нужно прокинуть agent_id; для v1 берём из SESSION_FILE, если есть.
    agent_id = None
    if SESSION_FILE.exists():
        try:
            session = json.loads(SESSION_FILE.read_text(encoding="utf-8"))
            agent_id = session.get("agent")
        except Exception:
            agent_id = None
    record: dict[str, Any] = {
        "skill": skill_id,
        "outcome": outcome,
        "help_score": help_score,
        "agent": agent_id,
    }
    root = Path.home() / ".akash"
    usage = root / "usage.jsonl"
    root.mkdir(parents=True, exist_ok=True)
    with usage.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

