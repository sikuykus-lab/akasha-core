from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml


def _load_nav_raw(brain_path: Path) -> dict[str, Any]:
    nav_path = brain_path / "skills" / "NAV.yaml"
    if not nav_path.exists():
        return {"chunks": [], "sets": [], "skills": []}
    raw = yaml.safe_load(nav_path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        return {"chunks": [], "sets": [], "skills": []}
    raw.setdefault("chunks", [])
    raw.setdefault("sets", [])
    raw.setdefault("skills", [])
    return raw


def register_chunks(brain_path: Path, new_chunks: list[dict[str, Any]]) -> None:
    """Lego-карта (§7): chunks = атомарные skills; sets = наборы по проектам."""
    nav_path = brain_path / "skills" / "NAV.yaml"
    data = _load_nav_raw(brain_path)
    by_id = {c["id"]: c for c in data["chunks"] if isinstance(c, dict) and c.get("id")}

    for chunk in new_chunks:
        cid = chunk["id"]
        if cid in by_id:
            existing = by_id[cid]
            existing_tags = set(existing.get("tags") or [])
            existing_tags.update(chunk.get("tags") or [])
            existing["tags"] = sorted(existing_tags)
            paths = set(existing.get("paths") or [])
            paths.update(chunk.get("paths") or [])
            existing["paths"] = sorted(paths)
        else:
            by_id[cid] = chunk

    data["chunks"] = sorted(by_id.values(), key=lambda c: c.get("id", ""))
    _rebuild_sets(data)
    nav_path.parent.mkdir(parents=True, exist_ok=True)
    nav_path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    _append_links(brain_path, new_chunks)


def _rebuild_sets(data: dict[str, Any]) -> None:
    by_project: dict[str, list[str]] = {}
    for chunk in data["chunks"]:
        proj = chunk.get("project") or "misc"
        by_project.setdefault(proj, []).append(chunk["id"])
    data["sets"] = [
        {"id": f"set-{proj.lower().replace(' ', '-')[:32]}", "project": proj, "chunks": sorted(ids)}
        for proj, ids in sorted(by_project.items())
    ]


def _append_links(brain_path: Path, chunks: list[dict[str, Any]]) -> None:
    links_path = brain_path / "state" / "links.jsonl"
    links_path.parent.mkdir(parents=True, exist_ok=True)
    by_project: dict[str, list[str]] = {}
    for c in chunks:
        by_project.setdefault(c.get("project", "misc"), []).append(c["id"])
    with links_path.open("a", encoding="utf-8") as f:
        for project, ids in by_project.items():
            if len(ids) < 2:
                continue
            for i, a in enumerate(ids):
                for b in ids[i + 1 :]:
                    f.write(
                        json.dumps(
                            {"from": a, "to": b, "project": project, "kind": "same-project"},
                            ensure_ascii=False,
                        )
                        + "\n"
                    )


def merge_usage_scores(brain_path: Path) -> None:
    from .nav import SkillScore

    data = _load_nav_raw(brain_path)
    usage_path = brain_path / "state" / "usage.jsonl"
    scores: dict[str, SkillScore] = {}
    if usage_path.exists():
        for line in usage_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            skill = record.get("skill")
            if not skill:
                continue
            entry = scores.get(skill) or SkillScore(skill=skill, score=0.0, uses=0)
            delta = int(record.get("help_score", 1)) if record.get("outcome") == "success" else -1
            entry.score += delta
            entry.uses += 1
            scores[skill] = entry
    data["skills"] = [
        {"id": s.skill, "score": s.score, "uses": s.uses}
        for s in sorted(scores.values(), key=lambda x: x.score, reverse=True)
    ]
    nav_path = brain_path / "skills" / "NAV.yaml"
    nav_path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def fit_skills_for_task(brain_path: Path, task: str, limit: int = 5) -> list[str]:
    data = _load_nav_raw(brain_path)
    task_tokens = set(_tokenize(task))
    ranked: list[tuple[float, str]] = []
    usage = {s["id"]: float(s.get("score", 0)) for s in data.get("skills", []) if isinstance(s, dict)}

    for chunk in data.get("chunks", []):
        if not isinstance(chunk, dict) or not chunk.get("id"):
            continue
        cid = chunk["id"]
        tag_tokens: set[str] = set()
        for t in chunk.get("tags") or []:
            tag_tokens.update(_tokenize(str(t)))
        overlap = len(task_tokens & tag_tokens)
        score = overlap * 3.0 + usage.get(cid, 0.0) * 0.1
        if overlap > 0 or usage.get(cid, 0) > 0:
            ranked.append((score, cid))

    ranked.sort(key=lambda x: x[0], reverse=True)
    if ranked:
        return [cid for _, cid in ranked[:limit]]
    return [s["id"] for s in data.get("skills", [])[:limit] if isinstance(s, dict) and s.get("id")]


def _tokenize(text: str) -> list[str]:
    return [w.lower() for w in re.findall(r"[a-zA-Zа-яА-ЯёЁ0-9]+", text) if len(w) > 2]
