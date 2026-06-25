from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .session import SESSION_FILE


PACK_LIMIT_BYTES = 24 * 1024


@dataclass
class SkillScore:
    skill: str
    score: float
    uses: int


def recompute_nav(brain_path: Path) -> None:
    """Пересчитать NAV scores, сохранить chunks/sets (§7, §10)."""
    from .nav_map import merge_usage_scores

    merge_usage_scores(brain_path)


def _load_nav(brain_path: Path) -> list[SkillScore]:
    nav_path = brain_path / "skills" / "NAV.yaml"
    if not nav_path.exists():
        return []
    raw = yaml.safe_load(nav_path.read_text(encoding="utf-8")) or {}
    result: list[SkillScore] = []
    for item in raw.get("skills", []):
        result.append(
            SkillScore(
                skill=item.get("id"),
                score=float(item.get("score", 0.0)),
                uses=int(item.get("uses", 0)),
            )
        )
    return result


def cli_prepare(backend, task: str) -> None:
    """Weave pack ≤24KB: Fit×Track по NAV chunks + usage (§7)."""
    from .nav_map import fit_skills_for_task

    brain_path = backend.brain_path
    skill_ids = fit_skills_for_task(brain_path, task, limit=5)
    if not skill_ids:
        scores = _load_nav(brain_path)
        skill_ids = [s.skill for s in scores[:5] if s.skill]

    pack: dict[str, Any] = {
        "task": task,
        "skills": skill_ids,
        "prepared_at": datetime.now(timezone.utc).isoformat(),
    }
    SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    with SESSION_FILE.open("w", encoding="utf-8") as f:
        json.dump(pack, f, ensure_ascii=False)
    print(json.dumps(pack, ensure_ascii=False))


def cli_read_skill(backend, skill_id: str) -> None:
    """Вернуть SKILL.md только если он в текущем pack (§7)."""
    if not SESSION_FILE.exists():
        raise SystemExit("No active pack; run `akash prepare` first.")
    pack = json.loads(SESSION_FILE.read_text(encoding="utf-8"))
    skills: list[str] = pack.get("skills", [])
    if skill_id not in skills:
        raise SystemExit("Skill is not part of current pack.")
    skill_path = backend.brain_path / "skills" / skill_id / "SKILL.md"
    if not skill_path.exists():
        raise SystemExit(f"Skill file not found: {skill_path}")
    print(skill_path.read_text(encoding="utf-8"))
