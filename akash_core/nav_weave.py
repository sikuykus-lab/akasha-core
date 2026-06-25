from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .skill_laws import TRIGGER_HEADERS, _extract_after_header

MIN_CUBE_SCORE = 3.0
MAX_CUBES = 8
MARGINAL_RATIO = 0.35

PATH_HEADERS = ("## paths", "## пути")
ENTRY_HEADERS = ("## entrypoints", "## entrypoint", "## точки входа")


@dataclass
class CubeMeta:
    id: str
    score: float
    tags: list[str]
    project: str
    paths: list[str]
    triggers: list[str]
    entrypoints: list[str]
    role: str = "candidate"


def _tokenize(text: str) -> set[str]:
    return {w.lower() for w in re.findall(r"[a-zA-Zа-яА-ЯёЁ0-9]+", text) if len(w) > 2}


def _skill_md_path(brain_path: Path, skill_id: str) -> Path:
    return brain_path / "skills" / skill_id / "SKILL.md"


def skill_exists(brain_path: Path, skill_id: str) -> bool:
    return _skill_md_path(brain_path, skill_id).is_file()


def _load_ineffective(brain_path: Path) -> set[str]:
    path = brain_path / "skills" / "INEFFECTIVE.yaml"
    if not path.is_file():
        return set()
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    blocked: set[str] = set()
    for item in raw.get("skills") or []:
        if isinstance(item, str):
            blocked.add(item)
        elif isinstance(item, dict) and item.get("id"):
            blocked.add(str(item["id"]))
    return blocked


def _bullets_after(content: str, headers: tuple[str, ...]) -> list[str]:
    section = _extract_after_header(content, headers)
    items: list[str] = []
    for line in section.splitlines():
        line = line.strip()
        if not line:
            if items:
                break
            continue
        if line.startswith("#"):
            break
        m = re.match(r"^[-*]\s+`?([^`]+)`?", line)
        if m:
            items.append(m.group(1).strip().rstrip("()"))
        elif re.match(r"^\d+\.", line):
            items.append(re.sub(r"^\d+\.\s*", "", line).strip())
    return items[:12]


def parse_skill_md(content: str) -> dict[str, list[str]]:
    triggers = _bullets_after(content, TRIGGER_HEADERS)
    paths = _bullets_after(content, PATH_HEADERS)
    entrypoints: list[str] = []
    for item in _bullets_after(content, ENTRY_HEADERS):
        name = re.sub(r"\(\)$", "", item.strip("`"))
        if name:
            entrypoints.append(name)
    return {"triggers": triggers, "paths": paths, "entrypoints": entrypoints}


def _load_links(brain_path: Path) -> dict[str, set[str]]:
    links_path = brain_path / "state" / "links.jsonl"
    graph: dict[str, set[str]] = {}
    if not links_path.is_file():
        return graph
    for line in links_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        a, b = rec.get("from"), rec.get("to")
        if a and b:
            graph.setdefault(a, set()).add(b)
            graph.setdefault(b, set()).add(a)
    return graph


def score_cube_for_task(task: str, cube_id: str, meta: dict[str, list[str]], chunk: dict[str, Any]) -> float:
    task_tokens = _tokenize(task)
    if not task_tokens:
        return 0.0

    score = 0.0
    id_tokens = _tokenize(cube_id.replace("-", " "))
    score += len(task_tokens & id_tokens) * 5.0

    for t in meta.get("triggers") or []:
        score += len(task_tokens & _tokenize(str(t))) * 4.0

    for t in chunk.get("tags") or []:
        score += len(task_tokens & _tokenize(str(t))) * 3.0

    for ep in meta.get("entrypoints") or []:
        ep_tokens = _tokenize(ep.replace("_", " "))
        score += len(task_tokens & ep_tokens) * 4.5

    for p in (chunk.get("paths") or []) + (meta.get("paths") or []):
        stem = Path(str(p)).stem
        score += len(task_tokens & _tokenize(stem)) * 2.0

    proj = str(chunk.get("project") or "")
    score += len(task_tokens & _tokenize(proj)) * 2.0

    return score


def _load_chunks(brain_path: Path) -> list[dict[str, Any]]:
    nav_path = brain_path / "skills" / "NAV.yaml"
    if not nav_path.is_file():
        return []
    raw = yaml.safe_load(nav_path.read_text(encoding="utf-8")) or {}
    return [c for c in raw.get("chunks") or [] if isinstance(c, dict) and c.get("id")]


def _rank_cubes(brain_path: Path, task: str) -> list[CubeMeta]:
    ineffective = _load_ineffective(brain_path)
    ranked: list[CubeMeta] = []

    for chunk in _load_chunks(brain_path):
        cid = str(chunk["id"])
        if cid in ineffective or not skill_exists(brain_path, cid):
            continue
        content = _skill_md_path(brain_path, cid).read_text(encoding="utf-8", errors="replace")
        meta = parse_skill_md(content)
        score = score_cube_for_task(task, cid, meta, chunk)
        if score < MIN_CUBE_SCORE:
            continue
        ranked.append(
            CubeMeta(
                id=cid,
                score=score,
                tags=list(chunk.get("tags") or []),
                project=str(chunk.get("project") or ""),
                paths=list(chunk.get("paths") or []) or meta.get("paths") or [],
                triggers=meta.get("triggers") or [],
                entrypoints=meta.get("entrypoints") or [],
            )
        )

    ranked.sort(key=lambda c: c.score, reverse=True)
    if not ranked:
        return []

    best = ranked[0].score
    selected: list[CubeMeta] = []
    for cube in ranked:
        if len(selected) >= MAX_CUBES:
            break
        if cube.score < best * MARGINAL_RATIO and selected:
            break
        selected.append(cube)
    return selected


def _assign_roles(cubes: list[CubeMeta], links: dict[str, set[str]]) -> None:
    if not cubes:
        return
    cubes[0].role = "anchor"
    anchor_id = cubes[0].id
    linked = links.get(anchor_id, set())
    for cube in cubes[1:]:
        if cube.id in linked:
            cube.role = "glue"
        elif cube.project and cube.project == cubes[0].project:
            cube.role = "related"
        else:
            cube.role = "support"


def _build_hint(task: str, cubes: list[CubeMeta]) -> str:
    if not cubes:
        return "Готовых кубиков под задачу нет — собери решение с нуля."
    anchor = cubes[0]
    parts = [f"Якорь: `{anchor.id}`"]
    if anchor.entrypoints:
        parts.append("функции: " + ", ".join(f"`{e}()`" for e in anchor.entrypoints[:4]))
    if len(cubes) > 1:
        glue = [c.id for c in cubes[1:] if c.role in ("glue", "related")]
        if glue:
            parts.append("склейка с: " + ", ".join(f"`{g}`" for g in glue[:3]))
    parts.append("не копируй целиком — возьми entrypoints и собери новое")
    return " · ".join(parts)


def _build_assembly(cubes: list[CubeMeta]) -> list[str]:
    if not cubes:
        return ["Задача без совпадений в паутине — исследуй проект и после успеха `create-skill`."]

    steps: list[str] = []
    anchor = cubes[0]
    steps.append(f"`read-skill {anchor.id}` — наводка и paths якорного кубика.")
    if anchor.entrypoints:
        steps.append(
            "Опирайся на entrypoints: "
            + ", ".join(f"`{e}()`" for e in anchor.entrypoints[:5])
            + " — не переписывай, вызывай/адаптируй."
        )
    for cube in cubes[1:]:
        if cube.role == "glue":
            line = f"Кубик `{cube.id}` — склейка"
            if cube.entrypoints:
                line += " через " + ", ".join(f"`{e}()`" for e in cube.entrypoints[:3])
            steps.append(line + ".")
    steps.append("Собери новую функцию/сценарий из кусков; лишние кубики не читай.")
    steps.append("После успеха — `create-skill` или `record-outcome` + `sync`.")
    return steps[:6]


def weave_solution_for_task(brain_path: Path, task: str) -> dict[str, Any]:
    """
    Собрать наводку на решение из lego-кубиков (функции, файлы), не «5 готовых ответов».
    """
    cubes = _rank_cubes(brain_path, task)
    links = _load_links(brain_path)
    _assign_roles(cubes, links)

    if not cubes:
        return {
            "confidence": "empty",
            "hint": _build_hint(task, cubes),
            "cubes": [],
            "assembly": _build_assembly(cubes),
        }

    best = cubes[0].score
    confidence = "high" if best >= 8.0 else "medium" if best >= MIN_CUBE_SCORE else "low"

    return {
        "confidence": confidence,
        "hint": _build_hint(task, cubes),
        "cubes": [
            {
                "id": c.id,
                "score": round(c.score, 1),
                "role": c.role,
                "project": c.project,
                "paths": c.paths[:5],
                "entrypoints": c.entrypoints[:8],
            }
            for c in cubes
        ],
        "assembly": _build_assembly(cubes),
    }


def reconcile_nav(brain_path: Path) -> int:
    """Убрать из NAV chunks/skills без SKILL.md. Возвращает число удалённых."""
    nav_path = brain_path / "skills" / "NAV.yaml"
    if not nav_path.is_file():
        return 0
    data = yaml.safe_load(nav_path.read_text(encoding="utf-8")) or {}
    removed = 0

    chunks = []
    for c in data.get("chunks") or []:
        if not isinstance(c, dict) or not c.get("id"):
            continue
        if skill_exists(brain_path, str(c["id"])):
            chunks.append(c)
        else:
            removed += 1
    data["chunks"] = chunks

    skills = []
    for s in data.get("skills") or []:
        if not isinstance(s, dict) or not s.get("id"):
            continue
        if skill_exists(brain_path, str(s["id"])):
            skills.append(s)
        else:
            removed += 1
    data["skills"] = skills

    if removed:
        nav_path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return removed
