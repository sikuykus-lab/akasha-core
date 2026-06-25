from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .skill_laws import _extract_after_header, extract_purpose

CAPABILITIES_FILE = "CAPABILITIES.yaml"


def capabilities_path(brain_path: Path) -> Path:
    return brain_path / "skills" / CAPABILITIES_FILE


def _load_raw(brain_path: Path) -> dict[str, Any]:
    path = capabilities_path(brain_path)
    if not path.is_file():
        return {"capabilities": []}
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        return {"capabilities": []}
    raw.setdefault("capabilities", [])
    return raw


def _save(brain_path: Path, data: dict[str, Any]) -> None:
    path = capabilities_path(brain_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def register_capability(
    brain_path: Path,
    skill_id: str,
    *,
    purpose: str,
    when: list[str] | None = None,
    entrypoints: list[str] | None = None,
    project: str = "",
    born_from: str = "",
) -> None:
    """Журнал возможностей — зачем существует нейрон-кубик."""
    purpose = purpose.strip()
    if not purpose:
        raise ValueError("purpose required")

    data = _load_raw(brain_path)
    by_id = {
        c["id"]: c
        for c in data["capabilities"]
        if isinstance(c, dict) and c.get("id")
    }
    entry = by_id.get(skill_id) or {"id": skill_id}
    entry["purpose"] = purpose
    entry["when"] = sorted(set(when or []) | _tokenize_purpose(purpose))
    if entrypoints:
        entry["entrypoints"] = entrypoints[:12]
    if project:
        entry["project"] = project
    if born_from:
        entry["born_from"] = born_from[:500]
    entry["updated_at"] = datetime.now(timezone.utc).isoformat()
    by_id[skill_id] = entry
    data["capabilities"] = sorted(by_id.values(), key=lambda c: c.get("id", ""))
    _save(brain_path, data)


def _tokenize_purpose(text: str) -> set[str]:
    return {w.lower() for w in re.findall(r"[a-zA-Zа-яА-ЯёЁ0-9]+", text) if len(w) > 2}


def purpose_for_skill(brain_path: Path, skill_id: str) -> str:
    data = _load_raw(brain_path)
    for c in data.get("capabilities") or []:
        if isinstance(c, dict) and c.get("id") == skill_id:
            return str(c.get("purpose") or "")
    return ""


def when_tags_for_skill(brain_path: Path, skill_id: str) -> list[str]:
    data = _load_raw(brain_path)
    for c in data.get("capabilities") or []:
        if isinstance(c, dict) and c.get("id") == skill_id:
            return list(c.get("when") or [])
    return []


def rebuild_from_skills(brain_path: Path) -> int:
    """Синхронизировать журнал из SKILL.md (## Назначение)."""
    from .nav_weave import parse_skill_md, skill_exists

    skills_dir = brain_path / "skills"
    if not skills_dir.is_dir():
        return 0
    count = 0
    for skill_dir in skills_dir.iterdir():
        if not skill_dir.is_dir() or skill_dir.name.startswith("_"):
            continue
        sid = skill_dir.name
        md = skill_dir / "SKILL.md"
        if not md.is_file():
            continue
        content = md.read_text(encoding="utf-8", errors="replace")
        purpose = extract_purpose(content)
        meta = parse_skill_md(content)
        if not purpose:
            triggers = meta.get("triggers") or []
            purpose = (
                f"Кубик `{sid}`"
                + (f" — {triggers[0]}" if triggers else "")
            )[:240]
        register_capability(
            brain_path,
            sid,
            purpose=purpose,
            when=meta.get("triggers") or [],
            entrypoints=meta.get("entrypoints") or [],
        )
        count += 1
    return count


def format_map(brain_path: Path, *, limit: int = 200) -> str:
    """Карта возможностей — журнал для точечного выбора, не перебор SKILL.md."""
    from .nav_weave import skill_exists

    data = _load_raw(brain_path)
    lines = ["# AKASHA — карта возможностей", ""]
    caps = [c for c in data.get("capabilities") or [] if isinstance(c, dict) and c.get("id")]
    caps = [c for c in caps if skill_exists(brain_path, str(c["id"]))][:limit]
    if not caps:
        lines.append("(пусто — после harvest/create-skill появятся записи)")
        return "\n".join(lines) + "\n"

    for c in caps:
        sid = c["id"]
        purpose = c.get("purpose") or "—"
        when = ", ".join((c.get("when") or [])[:6])
        eps = ", ".join(f"`{e}()`" for e in (c.get("entrypoints") or [])[:4])
        line = f"- **{sid}** — {purpose}"
        if when:
            line += f" · when: {when}"
        if eps:
            line += f" · {eps}"
        lines.append(line)
    lines.append("")
    lines.append(f"Всего: {len(caps)}. Тела skills — только `read-skill` из weave.")
    return "\n".join(lines) + "\n"


def cli_read_map(backend) -> None:
    print(format_map(backend.brain_path))
