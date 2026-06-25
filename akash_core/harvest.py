from __future__ import annotations

from pathlib import Path
from typing import Iterable

import yaml


def _iter_sources(brain_path: Path, platform: str) -> Iterable[Path]:
    """
    Прочитать adapters/<platform>/harvest-sources.yaml и вернуть пути (§14.2).
    Упрощённо: ожидаем список glob-паттернов.
    """
    cfg = brain_path / "adapters" / platform / "harvest-sources.yaml"
    if not cfg.exists():
        return []
    data = yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}
    patterns = data.get("globs", [])
    for pattern in patterns:
        yield from brain_path.glob(pattern)


def cli_harvest(backend, preview: bool, merge: bool) -> None:
    """
    Заглушка harvest для v1: выводит количество найденных файлов по источникам.
    Подробный перенос в persona/rapport/ACTIONS/skills оставляем на следующие итерации.
    """
    brain_path = backend.brain_path
    # Платформа в первой итерации не определяем, поэтому используем _template.
    sources = list(_iter_sources(brain_path, "_template"))
    print(f"Harvest preview: {len(sources)} files from adapters/_template/harvest-sources.yaml")
    if preview:
        return
    # Здесь должна быть логика записи в brain (§14.3–§14.7).


def cli_import_legacy(backend) -> None:
    """
    Узкий режим harvest для SOUL/USER/MEMORY/AGENTS (§14.2, §14.3).
    Сейчас выступает как синоним harvest --merge без платформенных globs.
    """
    print("import-legacy is not fully implemented yet; use harvest instead.")

