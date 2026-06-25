from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .session import SESSION_FILE


@dataclass
class SkillScore:
    skill: str
    score: float
    uses: int


def recompute_nav(brain_path) -> None:
    """Пересчитать NAV scores (§7, §10)."""
    from .nav_map import merge_usage_scores
    from .nav_weave import reconcile_nav

    reconcile_nav(brain_path)
    merge_usage_scores(brain_path)


def cli_prepare(backend, task: str) -> None:
    """Собрать наводку на решение из lego-кубиков (функции, paths), не пачку готовых ответов."""
    from .nav_weave import reconcile_nav, weave_solution_for_task

    brain_path = backend.brain_path
    reconcile_nav(brain_path)
    weave = weave_solution_for_task(brain_path, task)
    skill_ids = [c["id"] for c in weave.get("cubes", [])]

    pack: dict[str, Any] = {
        "task": task,
        "weave": weave,
        "skills": skill_ids,
        "prepared_at": datetime.now(timezone.utc).isoformat(),
    }
    SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    with SESSION_FILE.open("w", encoding="utf-8") as f:
        json.dump(pack, f, ensure_ascii=False)
    print(json.dumps(pack, ensure_ascii=False, indent=2))

    conf = weave.get("confidence", "empty")
    print(f"[{conf}] {weave.get('hint', '')}", file=sys.stderr)
    for i, step in enumerate(weave.get("assembly") or [], 1):
        print(f"  {i}. {step}", file=sys.stderr)


def cli_read_skill(backend, skill_id: str) -> None:
    """Вернуть SKILL.md только если кубик в текущем weave/pack."""
    if not SESSION_FILE.exists():
        raise SystemExit("No active pack; run `akash prepare` first.")
    pack = json.loads(SESSION_FILE.read_text(encoding="utf-8"))
    skills: list[str] = list(pack.get("skills") or [])
    if not skills:
        weave = pack.get("weave") or {}
        skills = [c["id"] for c in weave.get("cubes", []) if c.get("id")]
    if skill_id not in skills:
        raise SystemExit("Skill is not part of current weave.")
    skill_path = backend.brain_path / "skills" / skill_id / "SKILL.md"
    if not skill_path.exists():
        raise SystemExit(f"Skill file not found: {skill_path}")
    print(skill_path.read_text(encoding="utf-8"))
