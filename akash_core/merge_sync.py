from __future__ import annotations

import hashlib
import json
import re
import subprocess
import socket
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .backend import Backend

PENDING_USAGE = Path.home() / ".akash" / "usage_pending.jsonl"
SESSIONS_DIR = Path.home() / ".akash" / "sessions"
LOCAL_SESSION = Path.home() / ".akash" / "session_token.json"
ACTIVE_SESSIONS = Path("state") / "active_sessions.jsonl"
MAX_PUSH_ATTEMPTS = 5

SECTION_RE = re.compile(
    r"<!-- akasha:agent:([a-zA-Z0-9_-]+) -->\n?(.*?)<!-- /akasha:agent:\1 -->",
    re.DOTALL,
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _host() -> str:
    return socket.gethostname()


def register_pull(backend: Backend, agent_id: str) -> None:
    """Старт сессии: pull уже сделан, фиксируем локально (без блокировки)."""
    LOCAL_SESSION.parent.mkdir(parents=True, exist_ok=True)
    LOCAL_SESSION.write_text(
        json.dumps(
            {
                "agent_id": agent_id,
                "host": _host(),
                "pid": os.getpid(),
                "started_at": _utc_now(),
                "brain_path": str(backend.brain_path.resolve()),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def _line_key(line: str) -> str:
    line = line.strip()
    if not line:
        return ""
    try:
        return json.dumps(json.loads(line), sort_keys=True, ensure_ascii=False)
    except json.JSONDecodeError:
        return line


def merge_jsonl_append(target: Path, lines: list[str]) -> int:
    """Append-only merge с дедупликацией строк."""
    existing_keys: set[str] = set()
    if target.is_file():
        for line in target.read_text(encoding="utf-8").splitlines():
            key = _line_key(line)
            if key:
                existing_keys.add(key)
    added = 0
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as f:
        for line in lines:
            key = _line_key(line)
            if not key or key in existing_keys:
                continue
            existing_keys.add(key)
            f.write(line.rstrip() + "\n")
            added += 1
    return added


def _parse_sections(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    for agent_id, body in SECTION_RE.findall(text):
        sections[agent_id] = body.strip()
    legacy = SECTION_RE.sub("", text).strip()
    if legacy and "_legacy" not in sections:
        sections["_legacy"] = legacy
    return sections


def _render_sections(sections: dict[str, str]) -> str:
    parts: list[str] = []
    for agent_id in sorted(sections.keys()):
        body = sections[agent_id].strip()
        if not body:
            continue
        if agent_id == "_legacy":
            parts.append(body)
        else:
            parts.append(f"<!-- akasha:agent:{agent_id} -->\n{body}\n<!-- /akasha:agent:{agent_id} -->")
    return "\n\n".join(parts).strip() + ("\n" if sections else "")


def upsert_agent_section(path: Path, agent_id: str, new_lines: list[str]) -> None:
    """Prose merge: секция на агента, чужие секции не трогаем."""
    if not new_lines:
        return
    body = "\n".join(new_lines).strip()
    if not body:
        return
    current = path.read_text(encoding="utf-8") if path.is_file() else ""
    sections = _parse_sections(current)
    prev = sections.get(agent_id, "")
    sections[agent_id] = (prev + "\n" + body).strip() if prev else body
    sections.pop("_legacy", None)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_render_sections(sections), encoding="utf-8")


def _collect_remember_facts(agent_id: str) -> list[str]:
    facts: list[str] = []
    if not SESSIONS_DIR.is_dir():
        return facts
    for path in sorted(SESSIONS_DIR.glob("session-*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            fact = rec.get("fact")
            if fact:
                facts.append(str(fact))
    return facts


def _flush_pending_usage(brain_path: Path) -> int:
    legacy = Path.home() / ".akash" / "usage.jsonl"
    if legacy.is_file():
        pending = PENDING_USAGE
        pending.parent.mkdir(parents=True, exist_ok=True)
        with pending.open("a", encoding="utf-8") as out:
            out.write(legacy.read_text(encoding="utf-8"))
        legacy.unlink()
    if not PENDING_USAGE.is_file():
        return 0
    lines = [ln for ln in PENDING_USAGE.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if not lines:
        return 0
    added = merge_jsonl_append(brain_path / "state" / "usage.jsonl", lines)
    PENDING_USAGE.unlink(missing_ok=True)
    return added


def _flush_remember(brain_path: Path, agent_id: str) -> int:
    facts = _collect_remember_facts(agent_id)
    if not facts:
        return 0
    upsert_agent_section(brain_path / "memory" / "ACTIONS.md", agent_id, facts)
    for path in SESSIONS_DIR.glob("session-*.jsonl"):
        path.unlink(missing_ok=True)
    return len(facts)


def _record_active_session(brain_path: Path, agent_id: str, event: str) -> None:
    line = json.dumps(
        {"agent_id": agent_id, "host": _host(), "event": event, "ts": _utc_now()},
        ensure_ascii=False,
    )
    merge_jsonl_append(brain_path / ACTIVE_SESSIONS, [line])


def _merge_nav_chunks(brain_path: Path) -> None:
    """При git-конфликте NAV — union по chunk id (ours + theirs из маркеров)."""
    nav_path = brain_path / "skills" / "NAV.yaml"
    if not nav_path.is_file():
        return
    text = nav_path.read_text(encoding="utf-8")
    if "<<<<<<<" not in text:
        return
    parts = re.split(r"^<<<<<<<.*$|^=======\s*$|^>>>>>>>.*$", text, flags=re.MULTILINE)
    chunks: dict[str, dict[str, Any]] = {}
    for part in parts:
        part = part.strip()
        if not part or part.startswith("#"):
            continue
        try:
            data = yaml.safe_load(part) or {}
        except yaml.YAMLError:
            continue
        if not isinstance(data, dict):
            continue
        for chunk in data.get("chunks") or []:
            if isinstance(chunk, dict) and chunk.get("id"):
                cid = chunk["id"]
                if cid in chunks:
                    old = chunks[cid]
                    tags = set(old.get("tags") or []) | set(chunk.get("tags") or [])
                    paths = set(old.get("paths") or []) | set(chunk.get("paths") or [])
                    old["tags"] = sorted(tags)
                    old["paths"] = sorted(paths)
                else:
                    chunks[cid] = chunk
    merged = {
        "chunks": sorted(chunks.values(), key=lambda c: c.get("id", "")),
        "sets": [],
        "skills": [],
    }
    for part in parts:
        try:
            data = yaml.safe_load(part) or {}
        except yaml.YAMLError:
            continue
        if isinstance(data, dict):
            for skill in data.get("skills") or []:
                if isinstance(skill, dict) and skill.get("id"):
                    merged["skills"].append(skill)
    nav_path.write_text(yaml.safe_dump(merged, sort_keys=False, allow_unicode=True), encoding="utf-8")


def _resolve_git_conflicts(brain_path: Path, agent_id: str) -> None:
    """После неудачного rebase — мержим известные типы файлов."""
    status = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=U"],
        cwd=brain_path,
        capture_output=True,
        text=True,
        check=True,
    )
    for rel in status.stdout.splitlines():
        rel = rel.strip()
        if not rel:
            continue
        path = brain_path / rel
        if rel.endswith(".jsonl"):
            raw = path.read_text(encoding="utf-8", errors="replace")
            lines = [ln for ln in raw.splitlines() if ln.strip() and not ln.startswith("<")]
            path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
            merge_jsonl_append(path, [])  # normalize
            subprocess.run(["git", "add", rel], cwd=brain_path, check=True)
        elif rel == "skills/NAV.yaml":
            _merge_nav_chunks(brain_path)
            subprocess.run(["git", "add", rel], cwd=brain_path, check=True)
        elif rel in ("core/persona.md", "core/rapport.md", "memory/ACTIONS.md"):
            sections: dict[str, str] = {}
            raw = path.read_text(encoding="utf-8", errors="replace")
            for block in re.split(r"^<<<<<<<.*$|^=======\s*$|^>>>>>>>.*$", raw, flags=re.MULTILINE):
                sections.update(_parse_sections(block))
            path.write_text(_render_sections(sections), encoding="utf-8")
            subprocess.run(["git", "add", rel], cwd=brain_path, check=True)


def _remove_legacy_lock(brain_path: Path) -> None:
    legacy = brain_path / "state" / "session_lock.json"
    if legacy.is_file():
        legacy.unlink()


def apply_local_merges(brain_path: Path, agent_id: str) -> dict[str, int]:
    """Применить локальные буферы и cooperative merge перед commit."""
    _remove_legacy_lock(brain_path)
    stats = {
        "facts": _flush_remember(brain_path, agent_id),
        "usage": _flush_pending_usage(brain_path),
    }
    _record_active_session(brain_path, agent_id, "sync")
    return stats


def cooperative_push(backend: Backend, message: str = "AKASHA sync") -> None:
    """pull → commit → push с retry; при конфликте — merge, не блокировка."""
    brain_path = backend.brain_path
    for attempt in range(1, MAX_PUSH_ATTEMPTS + 1):
        backend.pull()
        _resolve_git_conflicts(brain_path, "")
        dirty = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=brain_path,
            capture_output=True,
            text=True,
            check=True,
        )
        if dirty.stdout.strip():
            subprocess.run(["git", "add", "-A"], cwd=brain_path, check=True)
            subprocess.run(["git", "commit", "-m", message], cwd=brain_path, check=True)
        push = subprocess.run(["git", "push"], cwd=brain_path, capture_output=True, text=True)
        if push.returncode == 0:
            return
        subprocess.run(["git", "pull", "--rebase", "--autostash"], cwd=brain_path, check=False)
        _resolve_git_conflicts(brain_path, "")
    raise SystemExit(
        f"AKASHA: не удалось опубликовать brain после {MAX_PUSH_ATTEMPTS} попыток merge. "
        "Повторите `akash sync` — данные в буфере не потеряны."
    )


def cooperative_sync(backend: Backend, agent_id: str) -> None:
    from . import session as session_mod
    from . import nav as nav_mod
    from . import brain as brain_mod

    backend.pull()
    apply_local_merges(backend.brain_path, agent_id)
    session_mod.compact_hot_memory(backend.brain_path)
    nav_mod.recompute_nav(backend.brain_path)
    brain_mod.bump_brain_version(backend.brain_path, agent_id)
    cooperative_push(backend)


def cli_session_status(backend: Backend, agent_id: str | None) -> None:
    backend.pull()
    path = backend.brain_path / ACTIVE_SESSIONS
    print("=== AKASHA sessions (cooperative) ===")
    print("Режим: параллельные агенты без блокировки, merge при sync.")
    if not path.is_file():
        print("Recent activity: (none)")
        return
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    for line in lines[-8:]:
        try:
            rec = json.loads(line)
            print(f"  {rec.get('ts', '?')[:19]}  {rec.get('agent_id')}@{rec.get('host')}  {rec.get('event')}")
        except json.JSONDecodeError:
            print(f"  {line[:80]}")
    if agent_id:
        print(f"Configured agent_id: {agent_id}")
