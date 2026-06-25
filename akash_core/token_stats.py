from __future__ import annotations

import json
from pathlib import Path

from .capabilities import format_map
from .nav_weave import skill_exists
from .weave_brief import WEAVE_BRIEF, format_weave_brief
from .session import SESSION_FILE

CHARS_PER_TOKEN = 4


def _est_tokens(text: str) -> int:
    return max(1, len(text.encode("utf-8")) // CHARS_PER_TOKEN)


def _all_skills_bytes(brain_path: Path) -> tuple[int, int]:
    total = 0
    count = 0
    skills_dir = brain_path / "skills"
    if not skills_dir.is_dir():
        return 0, 0
    for d in skills_dir.iterdir():
        if not d.is_dir() or d.name.startswith("_"):
            continue
        md = d / "SKILL.md"
        if md.is_file():
            total += len(md.read_text(encoding="utf-8", errors="replace").encode("utf-8"))
            count += 1
    return total, count


def cli_token_stats(backend) -> None:
    """Сравнение токенов: листинг всех skills vs карта + weave + якорь."""
    brain = backend.brain_path
    all_bytes, n_skills = _all_skills_bytes(brain)
    map_text = format_map(brain)
    map_tokens = _est_tokens(map_text)

    weave_tokens = 0
    anchor_tokens = 0
    anchor_id = ""
    if SESSION_FILE.exists():
        pack = json.loads(SESSION_FILE.read_text(encoding="utf-8"))
        brief = format_weave_brief(pack)
        weave_tokens = _est_tokens(brief)
        cubes = (pack.get("weave") or {}).get("cubes") or []
        if cubes:
            anchor_id = cubes[0].get("id") or ""
            md = brain / "skills" / anchor_id / "SKILL.md"
            if md.is_file():
                anchor_tokens = _est_tokens(md.read_text(encoding="utf-8", errors="replace"))

    naive_tokens = all_bytes // CHARS_PER_TOKEN if all_bytes else 0
    akasha_tokens = map_tokens + weave_tokens + anchor_tokens
    saved = max(0, naive_tokens - akasha_tokens)
    pct = round(100 * saved / naive_tokens, 1) if naive_tokens else 0.0

    report = {
        "skills_count": n_skills,
        "tokens_naive_all_skills": naive_tokens,
        "tokens_read_map": map_tokens,
        "tokens_read_weave": weave_tokens,
        "tokens_read_skill_anchor": anchor_tokens,
        "anchor_id": anchor_id,
        "tokens_akasha_path": akasha_tokens,
        "tokens_saved_vs_all_skills": saved,
        "savings_percent": pct,
        "note": "Оценка: bytes/4. naive = прочитать все SKILL.md; akasha = map+weave+1 якорь.",
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
