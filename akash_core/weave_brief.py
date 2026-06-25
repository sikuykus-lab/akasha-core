from __future__ import annotations

import json
from pathlib import Path
from typing import Any

WEAVE_BRIEF = Path.home() / ".akash" / "weave.brief.md"


def format_weave_brief(pack: dict[str, Any]) -> str:
    """Краткая наводка для агента — читать это, не весь JSON prepare."""
    task = pack.get("task") or ""
    weave = pack.get("weave") or {}
    conf = weave.get("confidence", "empty")
    lines = [
        "# AKASHA weave",
        "",
        f"**Задача:** {task}",
        f"**confidence:** {conf}",
        "",
        f"**hint:** {weave.get('hint', '—')}",
        "",
        "## assembly",
    ]
    for i, step in enumerate(weave.get("assembly") or [], 1):
        lines.append(f"{i}. {step}")
    cubes = weave.get("cubes") or []
    if cubes:
        lines.extend(["", "## кубики"])
        for c in cubes:
            eps = ", ".join(f"`{e}()`" for e in (c.get("entrypoints") or [])[:5])
            paths = ", ".join(f"`{p}`" for p in (c.get("paths") or [])[:3])
            line = f"- `{c.get('id')}` ({c.get('role')})"
            if eps:
                line += f" · {eps}"
            if paths:
                line += f" · {paths}"
            lines.append(line)
    lines.extend(
        [
            "",
            "Дальше: `read-skill <anchor>` → Read paths. Не листать skills/.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_weave_brief(pack: dict[str, Any]) -> Path:
    WEAVE_BRIEF.parent.mkdir(parents=True, exist_ok=True)
    WEAVE_BRIEF.write_text(format_weave_brief(pack), encoding="utf-8")
    return WEAVE_BRIEF


def cli_read_weave() -> None:
    if not WEAVE_BRIEF.is_file():
        raise SystemExit("No weave brief; run `akash prepare \"<задача>\"` first.")
    print(WEAVE_BRIEF.read_text(encoding="utf-8"))
