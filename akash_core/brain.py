from __future__ import annotations

import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .backend import Backend
from .config import Config


MANIFEST_NAME = "manifest.yaml"
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates" / "brain"


@dataclass
class Manifest:
    brain_version: int
    checksum: str | None
    supported_agents: list[str]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _copy_tree_if_missing(src: Path, dst: Path) -> None:
    """Копирует шаблоны brain только если целевого файла/каталога ещё нет."""
    if not src.exists():
        return
    if src.is_dir():
        for item in src.rglob("*"):
            rel = item.relative_to(src)
            target = dst / rel
            if item.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            elif not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target)
    elif not dst.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def init_brain(path: Path) -> None:
    """
    Scaffold brain-репозиторий в соответствии с §5 AKASHA-TZ.
    """
    path.mkdir(parents=True, exist_ok=True)

    (path / "core").mkdir(exist_ok=True)
    (path / "memory" / "daily").mkdir(parents=True, exist_ok=True)
    (path / "memory" / "archive").mkdir(parents=True, exist_ok=True)
    (path / "skills" / "_drafts").mkdir(parents=True, exist_ok=True)
    (path / "adapters").mkdir(exist_ok=True)
    (path / "state" / "sessions").mkdir(parents=True, exist_ok=True)

    readme = path / "README.md"
    if not readme.exists():
        readme.write_text(
            "AKASHA brain repository\n\n"
            "Скажи агрегатору что-то вроде:\n"
            "«Настрой себя по данному проекту GitHub: <URL ЭТОГО РЕПО>»\n",
            encoding="utf-8",
        )

    manifest_path = path / MANIFEST_NAME
    if not manifest_path.exists():
        manifest = Manifest(brain_version=1, checksum=None, supported_agents=[])
        _write_manifest(manifest_path, manifest)

    consciousness = path / "CONSCIOUSNESS.md"
    if not consciousness.exists():
        consciousness.write_text(
            "CONSCIOUSNESS\n\n"
            "Пока никто из агрегаторов не писал в мозг.\n",
            encoding="utf-8",
        )

    persona = path / "core" / "persona.md"
    if not persona.exists():
        persona.write_text("", encoding="utf-8")

    rapport = path / "core" / "rapport.md"
    if not rapport.exists():
        rapport.write_text("", encoding="utf-8")

    actions = path / "memory" / "ACTIONS.md"
    if not actions.exists():
        actions.write_text("", encoding="utf-8")

    nav = path / "skills" / "NAV.yaml"
    if not nav.exists():
        nav.write_text(
            yaml.safe_dump({"chunks": [], "sets": [], "skills": []}, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )

    ineffective = path / "skills" / "INEFFECTIVE.yaml"
    if not ineffective.exists():
        ineffective.write_text("# INEFFECTIVE patterns\n", encoding="utf-8")

    # Шаблоны skills/adapters из пакета (§3.2, §5, §9) — brain не бывает «пустой ссылкой».
    if TEMPLATES_DIR.exists():
        _copy_tree_if_missing(TEMPLATES_DIR / "skills", path / "skills")
        _copy_tree_if_missing(TEMPLATES_DIR / "adapters", path / "adapters")

    akasha_bootstrap = path / "skills" / "akasha-bootstrap" / "SKILL.md"
    if not akasha_bootstrap.exists():
        akasha_bootstrap.parent.mkdir(parents=True, exist_ok=True)
        akasha_bootstrap.write_text(
            "# akasha-bootstrap\n\n"
            "Первый skill при bootstrap. Полный чеклист:\n"
            "https://github.com/sikuykus-lab/akasha-core/blob/main/docs/AGENT-ONBOARDING.ru.md\n",
            encoding="utf-8",
        )

    for name in ("links.jsonl", "usage.jsonl"):
        state_file = path / "state" / name
        if not state_file.exists():
            state_file.write_text("", encoding="utf-8")


def migrate_brain(path: Path) -> None:
    """
    Минимальная миграция manifest/структуры до актуального вида (§3.2).
    """
    init_brain(path)
    manifest_path = path / MANIFEST_NAME
    manifest = _read_manifest(manifest_path)
    changed = False
    if manifest.brain_version < 1:
        manifest.brain_version = 1
        changed = True
    if manifest.supported_agents is None:
        manifest.supported_agents = []
        changed = True
    if changed:
        _write_manifest(manifest_path, manifest)


def _read_manifest(path: Path) -> Manifest:
    raw: dict[str, Any] = {}
    if path.exists():
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return Manifest(
        brain_version=int(raw.get("brain_version", 1)),
        checksum=raw.get("checksum"),
        supported_agents=list(raw.get("supported_agents") or []),
    )


def _write_manifest(path: Path, manifest: Manifest) -> None:
    data = {
        "brain_version": manifest.brain_version,
        "checksum": manifest.checksum,
        "supported_agents": manifest.supported_agents,
    }
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def pull_brain(backend: Backend) -> None:
    backend.pull()


def cli_sync(backend: Backend) -> None:
    """
    `akash sync` = pull → compact → NAV → push (§4.1, §6, §10).

    Здесь реализуем оболочку; compact и NAV заполнят другие модули.
    """
    from . import session as session_mod
    from . import nav as nav_mod

    backend.pull()
    session_mod.compact_hot_memory(backend.brain_path)
    nav_mod.recompute_nav(backend.brain_path)
    backend.push()


def cli_status(backend: Backend, cfg: Config) -> None:
    from . import harvest as harvest_mod

    manifest = _read_manifest(backend.brain_path / MANIFEST_NAME)
    skills = harvest_mod.count_skills(backend.brain_path)
    print("=== AKASHA status ===")
    print(f"Brain version: {manifest.brain_version}")
    print(f"Agent: {cfg.agent_id or '-'}")
    print(f"Backend: {cfg.backend or '-'}")
    print(f"Brain URL: {cfg.brain_url or '-'}")
    print(f"Scope: {cfg.scope or '-'}")
    print(f"Brain path: {backend.brain_path}")
    print(f"Skills: {skills}")
    print(f"Supported agents: {', '.join(manifest.supported_agents) or '-'}")


def bootstrap_brain(backend: Backend, agent_id: str) -> None:
    """
    Bootstrap-пайплайн для нового brain (§3.1–§3.2, упрощённая оболочка).
    """
    init_brain(backend.brain_path)
    manifest_path = backend.brain_path / MANIFEST_NAME
    manifest = _read_manifest(manifest_path)
    if agent_id not in manifest.supported_agents:
        manifest.supported_agents.append(agent_id)
        _write_manifest(manifest_path, manifest)

    _update_consciousness(backend.brain_path, agent_id)


def _update_consciousness(brain_path: Path, agent_id: str) -> None:
    path = brain_path / "CONSCIOUSNESS.md"
    ts = _now_iso()
    content = (
        f"Последний агрегатор: {agent_id}\n"
        f"Время (UTC): {ts}\n"
    )
    path.write_text(content, encoding="utf-8")

