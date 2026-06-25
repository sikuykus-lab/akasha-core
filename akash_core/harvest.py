from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Iterable

import yaml

from .config import load_config

SECRET_PATTERNS = [
    r"\.env$",
    r"credentials",
    r"secret",
    r"token",
    r"\.pem$",
    r"\.key$",
    r"id_rsa",
]

# Расширения, которые harvest никогда не трогает (бинарники, медиа).
BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".svg",
    ".pdf", ".zip", ".gz", ".tar", ".apk", ".dmg", ".exe", ".bin",
    ".pyc", ".woff", ".woff2", ".ttf", ".eot", ".mp3", ".mp4",
    ".docx", ".xlsx", ".pptx",
}


@dataclass
class HarvestReport:
    agent: str
    platform: str
    scanned: int = 0
    persona_bytes: int = 0
    rapport_bytes: int = 0
    actions_entries: int = 0
    skills_imported: int = 0
    skills_merged: int = 0
    skills_drafts: int = 0
    skills_skipped: int = 0
    secrets_skipped: int = 0
    binary_skipped: int = 0
    projects_scanned: int = 0
    chunks_synthesized: int = 0
    sources: list[str] = field(default_factory=list)


def count_skills(brain_path: Path) -> int:
    skills_dir = brain_path / "skills"
    if not skills_dir.exists():
        return 0
    return sum(
        1
        for p in skills_dir.iterdir()
        if p.is_dir() and p.name not in ("_drafts",) and (p / "SKILL.md").exists()
    )


def _is_secret_path(path: Path) -> bool:
    name = str(path).lower()
    return any(re.search(pat, name) for pat in SECRET_PATTERNS)


def _is_binary_path(path: Path) -> bool:
    if path.suffix.lower() in BINARY_EXTENSIONS:
        return True
    try:
        chunk = path.read_bytes()[:8192]
    except OSError:
        return True
    if not chunk:
        return False
    if b"\x00" in chunk:
        return True
    try:
        chunk.decode("utf-8")
        return False
    except UnicodeDecodeError:
        return True


def _read_text(path: Path) -> str | None:
    """UTF-8 текст; None если файл бинарный или не читается."""
    if _is_binary_path(path):
        return None
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def _read_text_lenient(path: Path) -> str:
    """Читает target brain-файл; битые байты заменяет (после сбойного harvest)."""
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _heal_brain_target(path: Path) -> None:
    """Перезаписать brain-файл в валидный UTF-8 после частично сбойного harvest."""
    if not path.exists():
        return
    text = _read_text_lenient(path).lstrip("\ufffd").strip()
    if text:
        path.write_text(text + "\n", encoding="utf-8")
    else:
        path.write_text("", encoding="utf-8")


def _expand_glob(pattern: str, project_root: Path) -> list[Path]:
    pattern = pattern.strip()
    expanded = Path(pattern).expanduser()

    # Абсолютный путь без wildcards — не glob (иначе NotImplementedError в pathlib).
    if expanded.is_absolute() and not any(ch in pattern for ch in "*?[]"):
        if expanded.is_file() and not _is_secret_path(expanded) and not _is_binary_path(expanded):
            return [expanded.resolve()]
        return []

    if pattern.startswith("~/"):
        root = Path.home()
        glob_part = pattern[2:]
    elif pattern.startswith("**"):
        root = project_root
        glob_part = pattern
    else:
        root = project_root
        glob_part = pattern
    found: list[Path] = []
    for p in root.glob(glob_part):
        if p.is_file() and not _is_secret_path(p) and not _is_binary_path(p):
            found.append(p.resolve())
    return found


def _iter_harvest_files(brain_path: Path, platform: str, project_root: Path) -> list[Path]:
    patterns: list[str] = []
    for plat in (platform, "_template"):
        cfg = brain_path / "adapters" / plat / "harvest-sources.yaml"
        if cfg.exists():
            data = yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}
            patterns.extend(data.get("globs", []))
    # Общие источники §14.2
    patterns.extend(
        [
            str(Path.home() / "SOUL.md"),
            str(Path.home() / "USER.md"),
            str(Path.home() / "MEMORY.md"),
            str(Path.home() / "AGENTS.md"),
            "SOUL.md",
            "USER.md",
            "MEMORY.md",
            "AGENTS.md",
        ]
    )
    seen: set[Path] = set()
    for pattern in patterns:
        if "/" not in pattern and not pattern.startswith("~") and not pattern.startswith("**"):
            for base in (project_root, Path.home(), project_root.parent):
                candidate = base / pattern
                if candidate.is_file() and not _is_secret_path(candidate) and not _is_binary_path(candidate):
                    seen.add(candidate.resolve())
            continue
        for p in _expand_glob(pattern, project_root):
            seen.add(p)
    return sorted(seen)


def _classify(path: Path) -> str:
    name = path.name.upper()
    if name == "SOUL.MD" or name == "AGENTS.MD":
        return "persona"
    if name == "USER.MD":
        return "rapport"
    if name == "MEMORY.MD" or "MEMORY" in str(path).upper():
        return "actions"
    if name == "SKILL.MD":
        return "skill"
    if "rules" in str(path).lower() or name.endswith(".MDC"):
        return "rapport"
    return "actions"


def _append_section(target: Path, header: str, content: str, source: str) -> int:
    target.parent.mkdir(parents=True, exist_ok=True)
    block = f"\n\n## {header}\n[harvest:{source}]\n\n{content.strip()}\n"
    existing = _read_text_lenient(target)
    if source in existing:
        return 0
    target.write_text(existing + block, encoding="utf-8")
    return len(block.encode("utf-8"))


def _skill_id_from_path(path: Path) -> str:
    if path.name == "SKILL.md":
        return path.parent.name
    return hashlib.sha1(str(path).encode()).hexdigest()[:12]


def _import_skill(brain_path: Path, path: Path, merge: bool) -> str:
    fragment = _read_text(path)
    if fragment is None:
        return "skipped"
    skill_id = _skill_id_from_path(path)
    dest = brain_path / "skills" / skill_id / "SKILL.md"
    if dest.exists() and merge:
        existing = _read_text_lenient(dest)
        if fragment.strip() in existing:
            return "skipped"
        dest.write_text(existing + f"\n\n[harvest-merge:{path}]\n\n{fragment}", encoding="utf-8")
        return "merged"
    if dest.exists():
        return "skipped"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(fragment, encoding="utf-8")
    return "imported"


def run_harvest(
    backend,
    *,
    preview: bool,
    merge: bool,
    project_root: Path | None = None,
) -> HarvestReport:
    brain_path = backend.brain_path
    project_root = project_root or Path.cwd()
    cfg = load_config()
    platform = cfg.agent_id or "cursor"
    report = HarvestReport(agent=platform, platform=platform)

    persona_path = brain_path / "core" / "persona.md"
    rapport_path = brain_path / "core" / "rapport.md"
    actions_path = brain_path / "memory" / "ACTIONS.md"
    if not preview:
        for target in (persona_path, rapport_path, actions_path):
            _heal_brain_target(target)

    files = _iter_harvest_files(brain_path, platform, project_root)
    report.scanned = len(files)
    report.sources = [str(f) for f in files[:50]]

    for path in files:
        kind = _classify(path)
        rel = str(path)
        text = _read_text(path)
        if text is None:
            report.binary_skipped += 1
            continue
        if kind == "persona":
            if not preview:
                report.persona_bytes += _append_section(persona_path, path.name, text, rel)
        elif kind == "rapport":
            if not preview:
                report.rapport_bytes += _append_section(rapport_path, path.name, text, rel)
        elif kind == "skill":
            if preview:
                report.skills_imported += 1
            else:
                result = _import_skill(brain_path, path, merge=merge)
                if result == "imported":
                    report.skills_imported += 1
                elif result == "merged":
                    report.skills_merged += 1
                else:
                    report.skills_skipped += 1
        else:
            if not preview:
                report.actions_entries += 1
                _append_section(actions_path, path.name, text, rel)

    from .project_harvest import run_project_synthesis

    synth = run_project_synthesis(brain_path, project_root, preview=preview, merge=merge)
    report.projects_scanned = synth.projects
    report.chunks_synthesized = synth.chunks_found
    report.skills_imported += synth.imported
    report.skills_merged += synth.merged
    report.skills_drafts += synth.drafts
    report.skills_skipped += synth.skipped

    _print_report(report, preview=preview)

    if not preview:
        log_path = brain_path / "state" / f"harvest-{date.today().isoformat()}.jsonl"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "agent": report.agent,
                        "platform": report.platform,
                        "scanned": report.scanned,
                        "skills_imported": report.skills_imported,
                        "skills_merged": report.skills_merged,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

    return report


def _print_report(report: HarvestReport, preview: bool) -> None:
    title = "AKASHA Harvest Preview" if preview else "AKASHA Harvest Complete"
    print(title)
    print("─" * 22)
    print(f"Агрегатор:   {report.agent} (cli)")
    print(f"Сканировано: {report.scanned} файлов")
    print(f"Профиль:     persona +{report.persona_bytes} B, rapport +{report.rapport_bytes} B")
    print(f"Память:      ACTIONS +{report.actions_entries} записей")
    print(
        f"Skills:      {report.skills_imported} импортировано, "
        f"{report.skills_merged} merged, {report.skills_skipped} пропущено, "
        f"{report.skills_drafts} в _drafts"
    )
    print(f"Проекты:     {report.projects_scanned} каталогов, {report.chunks_synthesized} lego-кубиков")
    print(f"Секреты:     {report.secrets_skipped} файлов пропущено")
    print(f"Бинарники:   {report.binary_skipped} файлов пропущено")
    print("─" * 22)
    if preview:
        print("Записать в brain и sync? [да / нет / только skills / только профиль]")


def cli_harvest(backend, preview: bool, merge: bool) -> None:
    run_harvest(backend, preview=preview, merge=merge)


def cli_import_legacy(backend) -> None:
    run_harvest(backend, preview=False, merge=True)
