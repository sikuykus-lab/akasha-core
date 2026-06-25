from __future__ import annotations

import json
from dataclasses import dataclass
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
    """
    Пересчитать NAV по state/usage.jsonl (§7, §8, §10).
    """
    usage_path = brain_path / "state" / "usage.jsonl"
    scores: dict[str, SkillScore] = {}
    if usage_path.exists():
        for line in usage_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record: dict[str, Any] = json.loads(line)
            skill = record.get("skill")
            if not skill:
                continue
            outcome = record.get("outcome")
            help_score = int(record.get("help_score", 1))
            entry = scores.get(skill) or SkillScore(skill=skill, score=0.0, uses=0)
            delta = help_score if outcome == "success" else -help_score
            entry.score += delta
            entry.uses += 1
            scores[skill] = entry
    nav_data = {
        "skills": [
            {"id": s.skill, "score": s.score, "uses": s.uses}
            for s in sorted(scores.values(), key=lambda s: s.score, reverse=True)
        ]
    }
    nav_path = brain_path / "skills" / "NAV.yaml"
    nav_path.write_text(yaml.safe_dump(nav_data, sort_keys=False, allow_unicode=True), encoding="utf-8")


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
    """
    weаve pack ≤24KB по NAV + INEFFECTIVE (§7).
    Упрощённо: выбираем 3–5 skills с наибольшим score.
    """
    brain_path = backend.brain_path
    scores = _load_nav(brain_path)
    top = scores[:5]
    pack: dict[str, Any] = {
        "task": task,
        "skills": [s.skill for s in top],
    }
    SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    with SESSION_FILE.open("w", encoding="utf-8") as f:
        json.dump(pack, f, ensure_ascii=False)
    print(json.dumps(pack, ensure_ascii=False))


def cli_read_skill(backend, skill_id: str) -> None:
    """
    Вернуть SKILL.md только если он в текущем pack (§7).
    """
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

