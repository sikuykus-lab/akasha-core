from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from .nav_map import register_chunks
from .skill_laws import validate_skill_md

_SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{1,47}$")
_TAG_LINE = re.compile(r"^tags:\s*(.+)$", re.MULTILINE | re.IGNORECASE)


def _normalize_id(skill_id: str) -> str:
    return skill_id.strip().lower().replace("_", "-")


def _tags_from_content(content: str) -> list[str]:
    m = _TAG_LINE.search(content)
    if not m:
        return []
    return [t.strip() for t in re.split(r"[,;]", m.group(1)) if t.strip()]


def cli_create_skill(
    backend,
    skill_id: str,
    *,
    content: str,
    tags: list[str] | None,
    built_from: list[str] | None,
    project: str,
    draft: bool,
) -> None:
    """Сохранить новый lego-кубик в brain после успешной задачи."""
    sid = _normalize_id(skill_id)
    if not _SLUG.match(sid):
        raise SystemExit(f"Invalid skill id: {skill_id!r} (use [a-z0-9-], 2–48 chars)")

    if not content.strip():
        raise SystemExit("Empty SKILL.md body (stdin or --file).")

    law = validate_skill_md(content)
    brain = backend.brain_path
    use_draft = draft or not law.ok

    if use_draft:
        dest = brain / "skills" / "_drafts" / sid / "SKILL.md"
        body = content
        if not law.ok:
            body += "\n## Law violations\n" + "\n".join(f"- {v}" for v in law.violations) + "\n"
    else:
        dest = brain / "skills" / sid / "SKILL.md"
        body = content

    if dest.exists():
        raise SystemExit(f"Skill already exists: {dest}")

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(body, encoding="utf-8")

    if built_from:
        meta = {"built_from": built_from}
        (dest.parent / "built_from.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    if not use_draft:
        tag_list = tags or _tags_from_content(content) or [project]
        register_chunks(
            brain,
            [{"id": sid, "tags": tag_list, "project": project, "paths": []}],
        )

    print(dest)
    if use_draft and not law.ok:
        print("Draft:", "; ".join(law.violations), file=sys.stderr)
